"""
LLM Translator MCP Server

Provides AI-powered content translation and analysis capabilities.
Translates technical reports into plain language suitable for non-technical audiences (HR, executives).
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.qwen import QwenClient
from src.schemas import HRExtract, OKRAlignment, ReportIn


class LLMTranslatorServer:
    """
    MCP Server for AI-powered content translation and analysis.

    This server wraps the Qwen LLM client to provide:
    - Technical → HR-friendly language translation
    - Risk extraction and assessment
    - OKR alignment inference
    - Next action generation

    Capabilities:
    - Tools: translate_to_hr_language, extract_risks, infer_okr_alignment, generate_next_actions
    - Resources: supported_models, prompt_templates
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "qwen-plus",
        api_mode: str = "text",
        timeout: float = 30.0,
    ):
        """
        Initialize LLM Translator Server.

        Args:
            api_key: DashScope API key (optional, can be set via env)
            model: Model name (qwen-plus, qwen-max, qwen-turbo)
            api_mode: API mode (text or compatible)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.api_mode = api_mode
        self.timeout = timeout
        self._client: Optional[QwenClient] = None

    def _get_client(self) -> QwenClient:
        """Lazy initialization of Qwen client."""
        if self._client is None:
            self._client = QwenClient(
                api_key=self.api_key,
                model=self.model,
                timeout=self.timeout,
                api_mode=self.api_mode,
                trust_env=False,
            )
        return self._client

    # ==================== MCP Tools ====================

    async def translate_to_hr_language(
        self,
        text: str,
        user_name: str = "Unknown User",
        period_type: str = "weekly",
        okr_context: Optional[str] = None,
        target_audience: str = "hr",
    ) -> Dict[str, Any]:
        """
        Translate technical report to HR-friendly language.

        This is the main MCP tool for content translation. It takes a technical
        report and transforms it into plain language suitable for non-technical readers.

        Args:
            text: Original technical report text
            user_name: Name of the person who wrote the report
            period_type: Report period (daily, weekly, monthly)
            okr_context: Optional OKR context/goals for the user
            target_audience: Target audience (hr, executive, board)

        Returns:
            {
                "summary": "Plain language summary (max 200 words)",
                "risks": [{"item": "...", "likelihood": "low|medium|high", "mitigation": "..."}],
                "needs": [{"topic": "...", "owner": "..."}],
                "okr_alignment": {
                    "hit_objectives": ["Objective 1", ...],
                    "hit_krs": ["Key Result 1", ...],
                    "gaps": ["Missing/behind area 1", ...],
                    "confidence": 0.0-1.0
                },
                "next_actions": ["Action 1", "Action 2", ...],
                "risk_level": "low|medium|high",
                "timestamp": "ISO timestamp"
            }

        Example:
            >>> result = await server.translate_to_hr_language(
            ...     text="本周完成了 API 重构和性能优化...",
            ...     user_name="张三",
            ...     period_type="weekly",
            ...     okr_context="提升系统性能和稳定性"
            ... )
            >>> print(result["summary"])
            "本周完成了后台接口优化，提升了系统响应速度..."
        """
        # Create ReportIn object
        report = ReportIn(
            user_id="mcp_user",
            user_name=user_name,
            raw_text=text,
            period_type=period_type,
            period_start="2025-01-01",  # Placeholder
            period_end="2025-01-07",
            message_ts=datetime.utcnow(),
        )

        # Generate HR extract
        client = self._get_client()
        hr_extract = await client.generate_hr_extract(
            report=report,
            okr_brief=okr_context or "暂无 OKR 信息",
        )

        # Format response
        return {
            "summary": hr_extract.hr_summary,
            "risks": [
                {
                    "item": risk.item,
                    "likelihood": risk.likelihood,
                    "mitigation": risk.mitigation or "",
                }
                for risk in hr_extract.risks
            ],
            "needs": [
                {
                    "topic": need.topic,
                    "owner": need.owner or "",
                }
                for need in hr_extract.needs
            ],
            "okr_alignment": {
                "hit_objectives": hr_extract.okr_alignment.hit_objectives,
                "hit_krs": hr_extract.okr_alignment.hit_krs,
                "gaps": hr_extract.okr_alignment.gaps,
                "confidence": hr_extract.okr_alignment.confidence,
            },
            "next_actions": hr_extract.next_actions,
            "risk_level": hr_extract.risk_level,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def extract_risks(
        self,
        text: str,
        context: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Extract risks from report text.

        Analyzes the report and identifies potential risks, blockers, or concerns.

        Args:
            text: Report text to analyze
            context: Optional context for risk assessment

        Returns:
            [
                {
                    "item": "Risk description",
                    "likelihood": "low|medium|high",
                    "mitigation": "Suggested mitigation strategy"
                },
                ...
            ]

        Example:
            >>> risks = await server.extract_risks(
            ...     text="项目进度延期，依赖的第三方 API 不稳定",
            ...     context="关键项目，需按时交付"
            ... )
            >>> for risk in risks:
            ...     print(f"{risk['likelihood']}: {risk['item']}")
        """
        result = await self.translate_to_hr_language(
            text=text,
            okr_context=context,
        )
        return result["risks"]

    async def infer_okr_alignment(
        self,
        text: str,
        okr_context: str,
    ) -> Dict[str, Any]:
        """
        Infer OKR alignment from report text.

        Analyzes the report against provided OKR context to determine:
        - Which objectives/KRs are being addressed
        - Which OKRs are falling behind or not covered
        - Confidence level of the alignment

        Args:
            text: Report text to analyze
            okr_context: User's OKR context/goals

        Returns:
            {
                "hit_objectives": ["Achieved objective 1", ...],
                "hit_krs": ["Achieved key result 1", ...],
                "gaps": ["Missing/behind area 1", ...],
                "confidence": 0.0-1.0
            }

        Example:
            >>> alignment = await server.infer_okr_alignment(
            ...     text="完成了用户登录功能开发",
            ...     okr_context="Q1 目标：完成用户认证系统 (KR: 登录、注册、密码重置)"
            ... )
            >>> print(f"已完成: {alignment['hit_krs']}")
            >>> print(f"待完成: {alignment['gaps']}")
        """
        result = await self.translate_to_hr_language(
            text=text,
            okr_context=okr_context,
        )
        return result["okr_alignment"]

    async def generate_next_actions(
        self,
        text: str,
        context: Optional[str] = None,
    ) -> List[str]:
        """
        Generate actionable next steps from report.

        Analyzes the report and suggests concrete, executable next actions.

        Args:
            text: Report text to analyze
            context: Optional context for action generation

        Returns:
            ["Action 1", "Action 2", ...]

        Example:
            >>> actions = await server.generate_next_actions(
            ...     text="已完成登录功能，但性能测试还未开始",
            ...     context="需要在月底前上线"
            ... )
            >>> for action in actions:
            ...     print(f"- {action}")
        """
        result = await self.translate_to_hr_language(
            text=text,
            okr_context=context,
        )
        return result["next_actions"]

    # ==================== MCP Resources ====================

    def get_supported_models(self) -> List[Dict[str, str]]:
        """
        Get list of supported LLM models.

        Returns:
            [
                {
                    "name": "qwen-max",
                    "provider": "dashscope",
                    "cost": "higher",
                    "description": "Most capable model"
                },
                ...
            ]
        """
        return [
            {
                "name": "qwen-max",
                "provider": "dashscope",
                "cost": "higher",
                "description": "Most capable Qwen model, best quality",
                "api_mode": "text",
            },
            {
                "name": "qwen-plus",
                "provider": "dashscope",
                "cost": "medium",
                "description": "Balanced performance and cost (recommended)",
                "api_mode": "compatible",
            },
            {
                "name": "qwen-turbo",
                "provider": "dashscope",
                "cost": "lower",
                "description": "Faster, lower cost, good for simple tasks",
                "api_mode": "compatible",
            },
            {
                "name": "qwen-long",
                "provider": "dashscope",
                "cost": "medium",
                "description": "Long context support (up to 10M tokens)",
                "api_mode": "compatible",
            },
        ]

    def get_prompt_templates(self) -> Dict[str, str]:
        """
        Get available prompt templates.

        Returns:
            {
                "system_prompt": "...",
                "user_prompt_template": "...",
                "constraints": "...",
            }
        """
        from src.ai.qwen import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

        return {
            "system_prompt": SYSTEM_PROMPT,
            "user_prompt_template": USER_PROMPT_TEMPLATE,
            "description": "Prompt templates used for HR-friendly translation",
            "language": "Chinese (Simplified)",
            "target_audience": "Non-technical HR/HRBP",
        }

    def get_translation_glossary(self) -> Dict[str, str]:
        """
        Get technical terms → plain language glossary.

        Returns:
            {"API": "系统接口/程序连接通道", ...}
        """
        return {
            "API": "系统接口 / 程序之间的连接通道",
            "SDK": "开发工具包 / 程序开发套件",
            "TDD/BDD": "测试驱动开发 / 先写测试再写代码的方法",
            "CI/CD": "自动化部署 / 代码自动上线流程",
            "重构": "代码优化 / 改进代码质量",
            "解耦": "模块分离 / 让各部分独立运行",
            "异步": "后台处理 / 不阻塞用户操作",
            "并发": "同时处理多个任务",
            "PR/MR": "代码合并请求 / 提交代码审查",
            "Bug": "程序错误 / 功能异常",
            "Debug": "排查问题 / 找出错误原因",
            "框架": "开发框架 / 开发工具集",
            "前端": "用户界面 / 网页显示部分",
            "后端": "服务器程序 / 数据处理部分",
            "数据库": "数据存储系统",
            "缓存": "临时数据存储 / 加快访问速度",
            "接口": "连接点 / 不同系统的对接方式",
        }


# ==================== MCP Server Integration ====================

def create_mcp_server() -> LLMTranslatorServer:
    """
    Factory function to create MCP server instance.

    This function is called by the MCP framework to instantiate the server.
    Configuration is read from environment variables or MCP config.
    """
    import os

    return LLMTranslatorServer(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model=os.getenv("QWEN_MODEL", "qwen-plus"),
        api_mode=os.getenv("QWEN_API_MODE", "text"),
        timeout=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30.0")),
    )


# ==================== CLI for testing ====================

async def _test_translation():
    """Test the translation functionality."""
    server = create_mcp_server()

    test_text = """
    本周完成了 WebApp 的 TDD/BDD 测试框架搭建，重构了 API 层的异步调用逻辑，
    修复了 O2KR1 相关的 bug_num=t100755 问题。下周计划进行性能优化。
    """

    print("🔄 测试 LLM Translator Server...")
    print(f"输入文本: {test_text.strip()}\n")

    result = await server.translate_to_hr_language(
        text=test_text,
        user_name="测试用户",
        period_type="weekly",
        okr_context="提升测试效率和质量，优化系统性能",
    )

    print("✅ 翻译结果:")
    print(f"📝 HR 总结: {result['summary']}\n")

    if result['risks']:
        print("⚠️ 风险项:")
        for risk in result['risks']:
            print(f"  - [{risk['likelihood']}] {risk['item']}")
            if risk['mitigation']:
                print(f"    缓解措施: {risk['mitigation']}")
        print()

    if result['okr_alignment']['hit_krs']:
        print("🎯 已完成的关键成果:")
        for kr in result['okr_alignment']['hit_krs']:
            print(f"  - {kr}")
        print()

    if result['okr_alignment']['gaps']:
        print("📌 待推进的目标:")
        for gap in result['okr_alignment']['gaps']:
            print(f"  - {gap}")
        print()

    if result['next_actions']:
        print("➡️ 下一步行动:")
        for action in result['next_actions']:
            print(f"  - {action}")
        print()

    print(f"📊 风险等级: {result['risk_level']}")
    print(f"🔍 OKR 对齐置信度: {result['okr_alignment']['confidence']:.0%}")


if __name__ == "__main__":
    # Run test
    asyncio.run(_test_translation())
