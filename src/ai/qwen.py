from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple

import httpx
from jinja2 import BaseLoader, Environment

from ..schemas import HRExtract, OKRAlignment, ReportIn
from ..utils.logger import get_logger

logger = get_logger(__name__)

TEXT_GENERATION_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
)
CHAT_COMPLETION_URL = (
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
)

SYSTEM_PROMPT = (
    "你是资深人力视角的解读助手。把技术日报/周报/月报翻译为非技术HR或小白能懂的语言，"
    "突出价值、风险、依赖和下一步动作。严格输出JSON。"
)

USER_PROMPT_TEMPLATE = """
【报告文本】
{{ report.raw_text }}

【人员】{{ report.user_name }} ({{ report.user_id }})
【周期】{{ report.period_type }} {{ report.period_start }}~{{ report.period_end }}

【该人员OKR（摘要）】
{{ okr_brief }}

请输出 JSON：
{
  "hr_summary": "不超过200字的通俗总结",
  "risks": [{"item":"", "likelihood":"low|medium|high", "mitigation":""}],
  "needs": [{"topic":"", "owner":""}],
  "okr_alignment": {
    "hit_objectives": ["O1","O2"],
    "hit_krs": ["KR1","KR2"],
    "gaps": ["未覆盖或落后KR的通俗描述"],
    "confidence": 0.0
  },
  "next_actions": ["可执行的下一步1","下一步2"],
  "risk_level": "low|medium|high"
}
约束：
1. 所有字段（包括 gaps、hit_objectives、hit_krs）都必须用HR能理解的通俗语言，避免专业术语（如TDD、BDD、API等）；
2. 对于 gaps 字段，不要输出 "O2KR1: xxx" 这样的格式，而要描述具体的业务目标，例如 "测试流程优化进展缓慢" 而不是 "TDD与BDD模式研究尚未完成"；
3. 如果必须保留技术词汇，请用括号补充通俗解释，例如 "自动化测试框架（让程序自动检测错误的工具）搭建延期"；
4. 如未提及OKR，也要基于文本给出最可能关联的O/KR并标注低置信度。
""".strip()


class QwenClient:
    def __init__(
        self,
        api_key: Optional[str],
        model: str,
        timeout: float = 10.0,
        http_client: Optional[httpx.AsyncClient] = None,
        max_retries: int = 2,
        api_mode: str = "text",
        trust_env: bool = False,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._client = http_client
        self.max_retries = max(1, max_retries)
        self.api_mode = api_mode
        self._jinja_env = Environment(loader=BaseLoader(), autoescape=False)
        self.trust_env = trust_env

    async def generate_hr_extract(self, report: ReportIn, okr_brief: str) -> HRExtract:
        if not self.api_key and not self._client:
            raise RuntimeError("DashScope API key is required for Qwen integration.")
        system_prompt, user_prompt = self._render_prompts(report, okr_brief)
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                timeout = self._timeout_for_attempt(attempt)
                raw_text = await self._invoke_completion(
                    system_prompt, user_prompt, attempt, timeout=timeout
                )
                return self._parse_extract(raw_text)
            except Exception as exc:
                last_error = exc
                logger.error(
                    "qwen_invoke_error",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": self.max_retries,
                        "error": str(exc) or repr(exc),
                        "error_type": type(exc).__name__,
                    },
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    user_prompt = self._append_retry_hint(user_prompt, str(exc))
                    continue

        logger.error(
            "qwen_fallback",
            extra={
                "error": str(last_error),
                "attempts": self.max_retries,
                "user_id": report.user_id,
            },
        )
        return self._fallback_extract(report)

    def _append_retry_hint(self, prompt: str, error: str) -> str:
        hint = "\n\n注意：上一轮输出未通过JSON校验，必须输出有效JSON对象。错误:" + error
        return prompt + hint

    async def _invoke_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        attempt: int,
        *,
        timeout: float,
    ) -> str:
        timeout_config = httpx.Timeout(
            timeout,
            connect=min(timeout, 10.0),
            read=timeout,
            write=min(timeout, 10.0),
            pool=timeout,
        )
        client = self._client or httpx.AsyncClient(
            timeout=timeout_config, trust_env=self.trust_env
        )
        should_close = self._client is None
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            if self.api_mode == "compatible":
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "response_format": {"type": "json_object"},
                }
                response = await client.post(
                    CHAT_COMPLETION_URL, json=payload, headers=headers
                )
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise RuntimeError(
                        f"DashScope temporary error: {response.status_code}"
                    )
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    try:
                        detail = response.json()
                    except Exception:
                        detail = response.text
                    logger.error(
                        "qwen_http_error",
                        extra={
                            "status_code": response.status_code,
                            "detail": detail,
                        },
                    )
                    raise exc
                text = self._extract_chat_text(response)
            else:
                combined_prompt = self._combine_prompts(system_prompt, user_prompt)
                payload = {
                    "model": self.model,
                    "input": {
                        "messages": [
                            {"role": "user", "content": combined_prompt},
                        ]
                    },
                }
                response = await client.post(
                    TEXT_GENERATION_URL, json=payload, headers=headers
                )
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise RuntimeError(
                        f"DashScope temporary error: {response.status_code}"
                    )
                response.raise_for_status()
                text = self._extract_text(response)

            json.loads(text)  # validate before returning
            return text
        finally:
            if should_close:
                await client.aclose()

    def _timeout_for_attempt(self, attempt: int) -> float:
        base = max(20.0, self.timeout)
        factor = 2.0**attempt
        return min(base * factor, 120.0)

    def _parse_extract(self, raw_text: str) -> HRExtract:
        data = json.loads(raw_text)
        sanitized = self._sanitize_extract_payload(data)
        return HRExtract.model_validate(sanitized)

    def _render_prompts(self, report: ReportIn, okr_brief: str) -> Tuple[str, str]:
        template = self._jinja_env.from_string(USER_PROMPT_TEMPLATE)
        user_prompt = template.render(report=report.model_dump(), okr_brief=okr_brief)
        return SYSTEM_PROMPT, user_prompt

    def _combine_prompts(self, system_prompt: str, user_prompt: str) -> str:
        return f"system\n\n{system_prompt}\n\nuser\n{user_prompt}"

    def _extract_text(self, response: httpx.Response) -> str:
        payload = response.json()
        output = payload.get("output") or {}
        if "text" in output:
            return output["text"]
        choices = output.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message") or {}
            if "content" in message:
                return message["content"]
        raise ValueError("DashScope response missing text content.")

    def _extract_chat_text(self, response: httpx.Response) -> str:
        payload = response.json()
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message") or {}
            content = message.get("content")
            if content:
                return content
        raise ValueError("DashScope compatible response missing content.")

    def _fallback_extract(self, report: ReportIn) -> HRExtract:
        raw = (report.raw_text or "").strip()
        if raw:
            summary = raw[:180]
            if len(raw) > 180:
                summary += "..."
        else:
            summary = "AI 暂未返回内容。"

        next_actions = []
        if report.period_type == "weekly":
            next_actions.append("请在下次周会上同步关键进展。")
        elif report.period_type == "monthly":
            next_actions.append("整理本月成果，准备月度复盘资料。")
        else:
            next_actions.append("保持日报节奏，补充风险与需求。")

        return HRExtract(
            hr_summary=f"(离线模式) {summary}",
            risks=[],
            needs=[],
            okr_alignment=OKRAlignment(
                hit_objectives=[],
                hit_krs=[],
                gaps=["AI 未能解析，需人工确认进展。"],
                confidence=0.1,
            ),
            next_actions=next_actions,
            risk_level="medium" if "风险" in raw else "low",
        )

    def _sanitize_extract_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        result["hr_summary"] = self._ensure_string(data.get("hr_summary", ""))
        result["risks"] = self._normalize_risks(data.get("risks"))
        result["needs"] = self._normalize_needs(data.get("needs"))
        result["okr_alignment"] = self._normalize_okr_alignment(
            data.get("okr_alignment") or {}
        )
        result["next_actions"] = self._normalize_str_list(data.get("next_actions"))
        result["risk_level"] = self._normalize_level(
            data.get("risk_level"), default="medium"
        )
        return result

    def _normalize_str_list(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [self._ensure_string(item) for item in value if item]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    def _normalize_risks(self, value: Any) -> List[Dict[str, Any]]:
        risks: List[Dict[str, Any]] = []
        if isinstance(value, list):
            iterable = value
        elif value:
            iterable = [value]
        else:
            iterable = []
        for item in iterable:
            if isinstance(item, dict):
                risk_item = {
                    "item": self._ensure_string(item.get("item", "")),
                    "likelihood": self._normalize_level(
                        item.get("likelihood"), default="medium"
                    ),
                    "mitigation": self._ensure_string(item.get("mitigation", "")),
                }
            else:
                text = self._ensure_string(item)
                risk_item = {
                    "item": text,
                    "likelihood": "medium",
                    "mitigation": "",
                }
            if risk_item["item"]:
                risks.append(risk_item)
        return risks

    def _normalize_needs(self, value: Any) -> List[Dict[str, Any]]:
        needs: List[Dict[str, Any]] = []
        if isinstance(value, list):
            iterable = value
        elif value:
            iterable = [value]
        else:
            iterable = []
        for item in iterable:
            if isinstance(item, dict):
                topic = self._ensure_string(item.get("topic", ""))
                owner_val = item.get("owner")
                owner = (
                    self._ensure_string(owner_val) if owner_val not in (None, "") else None
                )
            else:
                topic = self._ensure_string(item)
                owner = None
            if topic:
                needs.append({"topic": topic, "owner": owner})
        return needs

    def _normalize_okr_alignment(self, value: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(value, dict):
            value = {}
        return {
            "hit_objectives": self._normalize_str_list(value.get("hit_objectives")),
            "hit_krs": self._normalize_str_list(value.get("hit_krs")),
            "gaps": self._normalize_str_list(value.get("gaps")),
            "confidence": self._normalize_confidence(value.get("confidence")),
        }

    def _normalize_confidence(self, value: Any) -> float:
        if isinstance(value, (int, float)):
            return max(0.0, min(1.0, float(value)))
        if isinstance(value, str):
            try:
                parsed = float(value.strip().rstrip("%")) / (
                    100.0 if "%" in value else 1.0
                )
                return max(0.0, min(1.0, parsed))
            except ValueError:
                return 0.5
        return 0.5

    def _normalize_level(self, value: Any, default: str = "medium") -> str:
        mapping = {
            "low": "low",
            "l": "low",
            "较低": "low",
            "偏低": "low",
            "低": "low",
            "medium": "medium",
            "mid": "medium",
            "m": "medium",
            "中": "medium",
            "中等": "medium",
            "适中": "medium",
            "moderate": "medium",
            "medium-low": "medium",
            "medium-high": "medium",
            "high": "high",
            "h": "high",
            "较高": "high",
            "高": "high",
            "偏高": "high",
        }
        if isinstance(value, str):
            key = value.strip().lower()
            return mapping.get(key, mapping.get(value.strip(), default))
        return mapping.get(value, default)

    def _ensure_string(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()


class DummyQwenClient(QwenClient):
    def __init__(self, response: HRExtract) -> None:
        super().__init__(api_key=None, model="dummy", trust_env=False, api_mode="text")
        self._response = response

    async def generate_hr_extract(self, report: ReportIn, okr_brief: str) -> HRExtract:
        return self._response

    def _fallback_extract(self, report: ReportIn) -> HRExtract:
        return self._response

    async def _invoke_completion(
        self, system_prompt: str, user_prompt: str, attempt: int
    ) -> str:
        raise RuntimeError("Dummy client should not invoke completion.")
