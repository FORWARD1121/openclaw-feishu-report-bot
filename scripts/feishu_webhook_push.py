#!/usr/bin/env python3
"""
feishu_webhook_push.py
把 generate_report.py 产出的 weekly_report.json 推送到飞书自定义机器人。

需要在 config/.env 中配置：
    FEISHU_WEBHOOK_URL       # 群机器人 webhook 地址
    FEISHU_WEBHOOK_SECRET    # 群机器人签名密钥（群机器人设置里的"签名校验"）
可选（用于把趋势图作为图片一并发送，需要企业自建应用凭证）：
    FEISHU_APP_ID
    FEISHU_APP_SECRET

用法:
    python feishu_webhook_push.py --report output/weekly_report.json
"""

import argparse
import base64
import hashlib
import hmac
import json
import logging
import os
import sys
import time
from pathlib import Path

import requests

from common_env import load_env

TENANT_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
IMAGE_UPLOAD_URL = "https://open.feishu.cn/open-apis/im/v1/images"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("feishu_webhook_push")


def gen_sign(timestamp: str, secret: str) -> str:
    """飞书自定义机器人签名算法：见开放平台文档"自定义机器人的安全设置"。"""
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def get_tenant_access_token(app_id: str, app_secret: str) -> str | None:
    try:
        resp = requests.post(
            TENANT_TOKEN_URL,
            json={"app_id": app_id, "app_secret": app_secret},
            timeout=10,
        )
        data = resp.json()
        if data.get("code") == 0:
            return data["tenant_access_token"]
        print(f"[警告] 获取 tenant_access_token 失败: {data}")
    except Exception as e:
        print(f"[警告] 获取 tenant_access_token 异常: {e}")
    return None


def upload_image(token: str, image_path: str) -> str | None:
    """上传图片到飞书，返回 image_key。自定义 webhook 机器人本身不能直接发本地图片，
    必须先用企业自建应用的 API 上传拿到 image_key 再引用。"""
    try:
        with open(image_path, "rb") as f:
            resp = requests.post(
                IMAGE_UPLOAD_URL,
                headers={"Authorization": f"Bearer {token}"},
                data={"image_type": "message"},
                files={"image": f},
                timeout=15,
            )
        data = resp.json()
        if data.get("code") == 0:
            return data["data"]["image_key"]
        print(f"[警告] 上传图片失败: {data}")
    except Exception as e:
        print(f"[警告] 上传图片异常: {e}")
    return None


def build_card(stats: dict, summary_text: str, image_key: str | None) -> dict:
    elements = [
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**本周总结**\n{summary_text}"}},
        {"tag": "hr"},
        {
            "tag": "div",
            "fields": [
                {"is_short": True, "text": {"tag": "lark_md", "content": f"**总营收**\n{stats['total_revenue']:.0f} 元"}},
                {"is_short": True, "text": {"tag": "lark_md", "content": f"**总订单数**\n{stats['total_orders']}"}},
                {"is_short": True, "text": {"tag": "lark_md", "content": f"**客单价**\n{stats['avg_order_value']:.0f} 元"}},
                {"is_short": True, "text": {"tag": "lark_md", "content": f"**环比**\n{stats.get('wow_growth_pct', '暂无')}%"}},
            ],
        },
    ]
    if image_key:
        elements.append({"tag": "img", "img_key": image_key, "alt": {"tag": "plain_text", "content": "趋势图"}})

    return {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": "📊 自动化周报"}, "template": "blue"},
        "elements": elements,
    }


def push_to_feishu(card: dict):
    webhook_url = os.environ["FEISHU_WEBHOOK_URL"]
    secret = os.environ.get("FEISHU_WEBHOOK_SECRET", "")

    timestamp = str(int(time.time()))
    payload = {
        "timestamp": timestamp,
        "msg_type": "interactive",
        "card": card,
    }
    if secret:
        payload["sign"] = gen_sign(timestamp, secret)

    resp = requests.post(webhook_url, json=payload, timeout=10)
    result = resp.json()
    if result.get("code", result.get("StatusCode")) not in (0, None):
        raise RuntimeError(f"飞书推送失败: {result}")
    return result


def main():
    parser = argparse.ArgumentParser(description="把周报推送到飞书群")
    parser.add_argument("--report", required=True, help="generate_report.py 产出的 json 文件路径")
    args = parser.parse_args()

    load_env()

    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    stats = report["stats"]
    summary_text = report["summary_text"]
    chart_path = report.get("chart_path")

    image_key = None
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    if app_id and app_secret and chart_path and Path(chart_path).exists():
        token = get_tenant_access_token(app_id, app_secret)
        if token:
            image_key = upload_image(token, chart_path)

    card = build_card(stats, summary_text, image_key)
    result = push_to_feishu(card)

    logger.info("已推送到飞书群")
    print("[完成] 已推送到飞书群")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("飞书推送失败: %s", e)
        print(f"[错误] {e}", file=sys.stderr)
        sys.exit(1)
