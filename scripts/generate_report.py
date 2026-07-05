#!/usr/bin/env python3
"""
generate_report.py
读取销售/业务数据（csv 或 xlsx），用 pandas 做周汇总，
调用 Claude API 生成中文总结文字，用 matplotlib 画趋势图，
最终把结果写成 output/weekly_report.json 供飞书推送脚本使用。

用法:
    python generate_report.py --input sample_data/sample_sales.csv
    python generate_report.py --input sample_data/sample_sales.csv --output output/weekly_report.json

退出码:
    0  成功
    1  失败（数据文件缺失、格式错误等，详见 stderr）
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # 服务器无显示环境下也能出图
import matplotlib.pyplot as plt

from common_env import load_env

matplotlib.rcParams["axes.unicode_minus"] = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("generate_report")


def load_data(input_path: str) -> pd.DataFrame:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"找不到数据文件: {input_path}")

    if path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    required_cols = {"date", "revenue", "orders"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"数据文件缺少必要列: {missing}，需要包含 date, revenue, orders")

    df["date"] = pd.to_datetime(df["date"])
    logger.info("已加载数据 %d 行，日期范围 %s ~ %s",
                len(df), df["date"].min().date(), df["date"].max().date())
    return df.sort_values("date")


def summarize(df: pd.DataFrame) -> dict:
    total_revenue = float(df["revenue"].sum())
    total_orders = int(df["orders"].sum())
    avg_order_value = total_revenue / total_orders if total_orders else 0
    best_day = df.loc[df["revenue"].idxmax()]
    worst_day = df.loc[df["revenue"].idxmin()]

    wow_growth = None
    if len(df) >= 14:
        last7 = df.tail(7)["revenue"].sum()
        prev7 = df.iloc[-14:-7]["revenue"].sum()
        if prev7 > 0:
            wow_growth = (last7 - prev7) / prev7 * 100

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "avg_order_value": round(avg_order_value, 2),
        "best_day": {"date": str(best_day["date"].date()), "revenue": float(best_day["revenue"])},
        "worst_day": {"date": str(worst_day["date"].date()), "revenue": float(worst_day["revenue"])},
        "wow_growth_pct": round(wow_growth, 1) if wow_growth is not None else None,
    }


def build_local_summary(stats: dict) -> str:
    """本地模板生成总结，不依赖任何外部 API，保证离线环境也能跑通演示。"""
    growth_desc = (
        f"环比增长 {stats['wow_growth_pct']}%" if stats.get("wow_growth_pct") is not None
        else "数据周期不足，暂无环比"
    )
    return (
        f"本周总营收 {stats['total_revenue']:.0f} 元，共 {stats['total_orders']} 笔订单，"
        f"客单价约 {stats['avg_order_value']:.0f} 元，{growth_desc}。"
        f"最佳单日为 {stats['best_day']['date']}（{stats['best_day']['revenue']:.0f} 元），"
        f"建议关注 {stats['worst_day']['date']} 前后的转化情况。"
    )


def call_claude_for_summary(stats: dict) -> str:
    """调用 Claude API 把统计数字转成一段自然语言周报总结。
    - 未配置 API Key 或强制本地时，直接走本地模板（不会递归）。
    - 有 Key 但接口异常时，捕获后一次性回退到本地模板（不再重新调用 API）。
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    # 关键修复：无 Key 或强制本地时，直接返回本地模板，避免递归调用 API
    if stats.get("_force_local") or not api_key:
        if not api_key:
            logger.info("未配置 ANTHROPIC_API_KEY，使用本地模板生成总结（仅供离线演示）。")
        return build_local_summary(stats)

    prompt = (
        "你是一个企业运营分析助手，请根据以下本周经营数据，写一段不超过150字的中文周报总结，"
        "语气专业、简洁，指出亮点和需要关注的地方：\n"
        f"{json.dumps(stats, ensure_ascii=False)}"
    )

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in message.content if block.type == "text").strip()
        logger.info("已通过 Claude API 生成总结。")
        return text
    except Exception as e:
        # 一次性回退到本地模板，不再走 API，杜绝递归
        logger.warning("调用 Claude API 失败（%s），改用本地模板生成总结。", e)
        return build_local_summary(stats)


def make_chart(df: pd.DataFrame, output_dir: Path) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    chart_path = output_dir / "weekly_trend.png"

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["date"], df["revenue"], marker="o", linewidth=2)
    ax.set_title("Revenue Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)

    logger.info("趋势图已保存: %s", chart_path)
    return str(chart_path)


def run(input_path: str, output_path: str) -> dict:
    df = load_data(input_path)
    stats = summarize(df)
    summary_text = call_claude_for_summary(stats)
    chart_path = make_chart(df, Path("output"))

    result = {
        "stats": stats,
        "summary_text": summary_text,
        "chart_path": chart_path,
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("周报已生成: %s", out)
    return result


def main():
    parser = argparse.ArgumentParser(description="生成自动化周报（数据汇总 + 大模型总结 + 趋势图）")
    parser.add_argument("--input", required=True, help="输入数据文件路径 (csv 或 xlsx)")
    parser.add_argument("--output", default="output/weekly_report.json", help="输出 JSON 路径")
    args = parser.parse_args()

    load_env()
    result = run(args.input, args.output)

    # 面向用户的简洁输出（stdout），便于 OpenClaw 抓取结果
    print(f"[完成] 周报已生成: {args.output}")
    print(f"总结: {result['summary_text']}")
    print(f"趋势图: {result['chart_path']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("生成周报失败: %s", e)
        print(f"[错误] {e}", file=sys.stderr)
        sys.exit(1)
