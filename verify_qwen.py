#!/usr/bin/env python
"""
Minimal connectivity check for DashScope Qwen APIs.

Usage:
  python verify_qwen.py
"""
from __future__ import annotations

import asyncio
import json
import os
from typing import Dict, Tuple

import httpx
from dotenv import load_dotenv

TEXT_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
)
CHAT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a helpful assistant. Reply in JSON with a short HR summary. "
    "Use simplified Chinese."
)
USER_PROMPT = (
    "【报告】本周完成支付接口灰度，正在观察线上表现，暂无风险。\n"
    "请用 JSON 返回：{'hr_summary': '...'}"
)


def load_settings() -> Tuple[str, str, bool]:
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("请先设置 DASHSCOPE_API_KEY 环境变量")

    model = os.getenv("QWEN_MODEL", "qwen-max")
    trust_env = os.getenv("HTTP_TRUST_ENV", "false").lower() == "true"
    return api_key, model, trust_env


def choose_endpoint(model: str) -> Tuple[str, Dict]:
    compatible_models = {"qwen-plus", "qwen-long", "qwen-turbo"}
    if model.lower() in compatible_models:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT},
            ],
            # optional: enforce JSON
            # "response_format": {"type": "json_object"},
        }
        return CHAT_URL, payload

    prompt = f"system\n\n{SYSTEM_PROMPT}\n\nuser\n{USER_PROMPT}"
    payload = {
        "model": model,
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        },
    }
    return TEXT_URL, payload


async def main() -> None:
    api_key, model, trust_env = load_settings()
    url, payload = choose_endpoint(model)

    async with httpx.AsyncClient(timeout=15.0, trust_env=trust_env) as client:
        response = await client.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print("请求失败：")
        print("status:", exc.response.status_code)
        print("headers:", exc.response.headers)
        print("body:", exc.response.text)
        raise

    data = response.json()
    print("DashScope response:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    if "choices" in data:
        content = data["choices"][0]["message"]["content"]
        print("\nExtracted message content:")
        print(content)


if __name__ == "__main__":
    asyncio.run(main())
