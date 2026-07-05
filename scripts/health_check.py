#!/usr/bin/env python3
"""
health_check.py
交付前/部署后一键自检：检查依赖、配置、目录、端口绑定是否符合要求。
把 README 里的"安全检查清单"从人工核对变成可执行验证。

用法:
    python health_check.py

退出码:
    0  全部通过
    1  存在必须修复的问题（FAIL）
    仅有 WARN 时仍返回 0（不阻塞离线演示）
"""

import importlib
import os
import subprocess
import sys
from pathlib import Path

from common_env import load_env

ROOT = Path(__file__).resolve().parent.parent

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
results = []


def record(level: str, item: str, detail: str = ""):
    results.append((level, item, detail))


def check_env_file():
    env_path = ROOT / "config" / ".env"
    if env_path.exists():
        record(PASS, "config/.env 存在")
        # 顺带检查文件权限（Unix）
        try:
            mode = oct(env_path.stat().st_mode)[-3:]
            if mode != "600":
                record(WARN, ".env 文件权限非 600", f"当前 {mode}，建议 chmod 600 config/.env")
            else:
                record(PASS, ".env 权限为 600")
        except Exception:
            pass
    else:
        record(WARN, "config/.env 不存在", "离线演示可跳过；真实联调前需从 .env.example 复制并填写")


def check_secret(name: str, required: bool):
    val = os.environ.get(name)
    if val:
        record(PASS, f"{name} 已配置")
    elif required:
        record(FAIL, f"{name} 未配置", "真实飞书/大模型联调必需")
    else:
        record(WARN, f"{name} 未配置", "缺失时对应功能不可用（离线演示可忽略）")


def check_dependencies():
    deps = {
        "pandas": True,
        "matplotlib": True,
        "requests": True,
        "anthropic": False,   # 缺失时可降级本地模板
        "lark_oapi": False,   # 缺失时长连接不可用，但周报生成不受影响
    }
    for mod, required in deps.items():
        try:
            importlib.import_module(mod)
            record(PASS, f"依赖 {mod} 已安装")
        except ImportError:
            level = FAIL if required else WARN
            record(level, f"依赖 {mod} 缺失", "pip install -r requirements.txt")


def check_paths():
    output_dir = ROOT / "output"
    if output_dir.exists() and os.access(output_dir, os.W_OK):
        record(PASS, "output/ 可写")
    else:
        record(FAIL, "output/ 不可写或不存在", "mkdir -p output")

    sample = ROOT / "sample_data" / "sample_sales.csv"
    if sample.exists():
        record(PASS, "示例数据存在")
    else:
        record(WARN, "示例数据缺失", "sample_data/sample_sales.csv")


def check_docker_binding():
    """检查 docker-compose.yml 端口是否只绑定 127.0.0.1，避免误开公网。"""
    compose = ROOT / "docker" / "docker-compose.yml"
    if not compose.exists():
        record(WARN, "docker-compose.yml 不存在")
        return
    text = compose.read_text(encoding="utf-8")
    if "0.0.0.0:18789" in text:
        record(FAIL, "Docker 端口绑定到 0.0.0.0", "存在公网暴露风险，改为 127.0.0.1")
    elif "127.0.0.1:18789" in text:
        record(PASS, "Docker 端口仅绑定 127.0.0.1")
    else:
        record(WARN, "未能确认 Docker 端口绑定方式")


def main():
    load_env()
    check_env_file()
    check_secret("ANTHROPIC_API_KEY", required=False)
    check_secret("FEISHU_WEBHOOK_URL", required=False)
    check_secret("FEISHU_APP_ID", required=False)
    check_secret("FEISHU_APP_SECRET", required=False)
    check_dependencies()
    check_paths()
    check_docker_binding()

    print("=" * 60)
    print("OpenClaw 飞书周报助手 · 健康检查")
    print("=" * 60)
    n_fail = 0
    for level, item, detail in results:
        mark = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}[level]
        line = f"{mark} [{level}] {item}"
        if detail:
            line += f"  → {detail}"
        print(line)
        if level == FAIL:
            n_fail += 1
    print("=" * 60)

    if n_fail:
        print(f"存在 {n_fail} 项 FAIL，请先修复后再部署。")
        sys.exit(1)
    print("无致命问题，可继续部署（WARN 项按需处理）。")
    sys.exit(0)


if __name__ == "__main__":
    main()
