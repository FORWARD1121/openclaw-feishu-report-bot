"""
common_env.py
统一的 .env 读取模块，供 generate_report / feishu_webhook_push / feishu_ws_listener 共用，
避免三个脚本各写一份、行为不一致。
"""

import os
from pathlib import Path


def load_env() -> None:
    """从 config/.env 加载环境变量（若文件存在）。
    使用 setdefault，不会覆盖已经通过 docker env_file / export 注入的值。"""
    env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())
