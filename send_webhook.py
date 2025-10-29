import json

import httpx


def main() -> None:
    payload = {
        "user_id": "ou_1303116204be60d4c20823499c14937d",
        "user_name": "airbang",
        "text": """[daily] 生产问题跟踪验证：t100721、t100722、t100714；协助售前同事对接锡山区用户问题；理解锡山区二期需求，及编写测试用例；"BOSS·AI 智能打分" 插件开发，及《简易操作手册》编写：BOSS·AI 智能打分 — 简易操作手册；飞书日周报与OKR智能流程方案调研：Feishu AI Report Analyzer方案""",
    }
    with httpx.Client(timeout=10.0, trust_env=False) as client:
        resp = client.post(
            "http://127.0.0.1:8080/webhook/feishu",
            json=payload,
        )
    print(resp.status_code)
    try:
        print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
    except Exception:
        print(resp.text)


if __name__ == "__main__":
    main()
