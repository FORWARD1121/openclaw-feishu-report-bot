# QUICKSTART：5 分钟跑通最小 Demo

这份文档只保证一件事：**在不配置任何飞书/大模型凭证的情况下，本地跑通周报生成**，
验证环境没问题。真实飞书联调见 `docs/DEPLOYMENT.md`。

## 前置

- Python 3.10+
- pip

## 步骤

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 自检（不需要任何密钥，全绿或仅 WARN 即可）
python scripts/health_check.py

# 3. 生成周报（用内置示例数据；未配置 API Key 时自动用本地模板生成总结）
python scripts/generate_report.py --input sample_data/sample_sales.csv
```

## 预期结果

- 终端打印 `[完成] 周报已生成: output/weekly_report.json`
- `output/weekly_report.json` 生成，包含 stats / summary_text / chart_path
- `output/weekly_trend.png` 生成（营收趋势图）
- 退出码为 0

跑到这一步，说明数据处理、总结生成、出图这条主链路完全 OK。
接下来配置飞书凭证即可打通推送与群内交互，详见 `docs/DEPLOYMENT.md`。
