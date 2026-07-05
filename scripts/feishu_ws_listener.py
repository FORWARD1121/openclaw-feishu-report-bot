#!/usr/bin/env python3
"""
feishu_ws_listener.py
用飞书官方 SDK（lark-oapi）以 WebSocket 长连接方式接收群消息事件。
优势：本地直接跑，不需要公网 IP、不需要内网穿透工具、不需要开放任何端口，
这正是"绝不越权开放公网端口"这条安全要求下最合适的接入方式。

依赖:
    uv pip install lark-oapi

需要在飞书开放平台后台，把"事件订阅"的接收方式改为"使用长连接接收事件"，
并订阅 im.message.receive_v1 事件。

用法:
    python feishu_ws_listener.py
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import lark_oapi as lark
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1

from common_env import load_env

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("feishu_ws_listener")


def extract_text(data: P2ImMessageReceiveV1) -> str:
    """飞书文本消息的 content 是一段 JSON 字符串，如 {"text":"@_user_1 详情"}。
    群里 @机器人 时会插入 @_user_1 这样的内部标记，这里简单去掉。"""
    try:
        content = json.loads(data.event.message.content)
        text = content.get("text", "")
        return text.replace("@_user_1", "").strip()
    except Exception:
        return ""


def reply_text(message_id: str, text: str):
    """用 requests 直接调用回复消息接口，避免在示例里引入过多 SDK 细节。"""
    import requests

    app_id = os.environ["FEISHU_APP_ID"]
    app_secret = os.environ["FEISHU_APP_SECRET"]

    token_resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=10,
    ).json()
    token = token_resp.get("tenant_access_token")
    if not token:
        print(f"[警告] 获取 token 失败: {token_resp}", file=sys.stderr)
        return

    requests.post(
        f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply",
        headers={"Authorization": f"Bearer {token}"},
        json={"msg_type": "text", "content": json.dumps({"text": text}, ensure_ascii=False)},
        timeout=10,
    )


def handle_command(text: str) -> str:
    """极简命令路由：目前只处理"详情"和"生成周报"两个指令，
    实际项目里可以在这里调用 OpenClaw 的 CLI/API 把消息转发给 Agent 处理。"""
    if "详情" in text:
        report_path = Path("output/weekly_report.json")
        if not report_path.exists():
            return "还没有生成过周报，请先说「生成周报」。"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        stats = report["stats"]
        return (
            f"最佳单日：{stats['best_day']['date']}（{stats['best_day']['revenue']:.0f} 元）\n"
            f"最弱单日：{stats['worst_day']['date']}（{stats['worst_day']['revenue']:.0f} 元）\n"
            f"客单价：{stats['avg_order_value']:.0f} 元"
        )
    if "生成周报" in text:
        subprocess.run(
            [sys.executable, "scripts/generate_report.py", "--input", "sample_data/sample_sales.csv"],
            check=False,
        )
        return "周报已重新生成，回复「推送」可发到群里。"
    if "推送" in text:
        subprocess.run(
            [sys.executable, "scripts/feishu_webhook_push.py", "--report", "output/weekly_report.json"],
            check=False,
        )
        return "已推送最新周报到群里。"
    return "支持的指令：生成周报 / 推送 / 详情"


def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    text = extract_text(data)
    if not text:
        return
    print(f"[收到消息] {text}")
    reply = handle_command(text)
    reply_text(data.event.message.message_id, reply)


def main():
    load_env()
    app_id = os.environ["FEISHU_APP_ID"]
    app_secret = os.environ["FEISHU_APP_SECRET"]

    event_handler = (
        lark.EventDispatcherHandler.builder("", "")
        .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1)
        .build()
    )

    client = lark.ws.Client(
        app_id,
        app_secret,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO,
    )
    logger.info("飞书 WebSocket 长连接客户端启动，等待群消息...")
    print("[启动] 飞书 WebSocket 长连接客户端，等待群消息...")
    client.start()  # 阻塞运行


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("收到中断信号，退出。")
        sys.exit(0)
    except Exception as e:
        logger.error("长连接客户端异常退出: %s", e)
        print(f"[错误] {e}", file=sys.stderr)
        sys.exit(1)
