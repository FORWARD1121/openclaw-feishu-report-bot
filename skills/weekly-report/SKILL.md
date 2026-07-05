---
name: weekly-report
description: >
  自动生成销售/业务周报并推送到飞书群。
  Use when: 用户说"生成周报"、"本周数据总结"、"发周报到飞书"，或每周五定时触发。
  NOT for: 需要人工审批的正式财报、涉及未公开财务数据的敏感汇报。
tools: ["Bash", "Read", "Write"]
---

# Weekly Report Skill

## 触发条件
用户说出以下任一意图时触发：
- "生成本周(销售/业务)周报"
- "把周报发到飞书"
- 每周五 17:00 定时触发（heartbeat）

## 前置检查
1. 确认 `sample_data/` 或用户指定路径下存在本周数据文件（csv/xlsx）。
2. 确认 `config/.env` 中已配置 `ANTHROPIC_API_KEY`、`FEISHU_WEBHOOK_URL`、`FEISHU_WEBHOOK_SECRET`。
   若缺失，提示用户先完成配置，不要继续执行。

## 执行步骤
1. 调用数据汇总与总结脚本：
   ```bash
   python scripts/generate_report.py --input <数据文件路径> --output output/weekly_report.json
   ```
2. 检查 `output/weekly_report.json` 是否生成成功，读取其中的 `summary_text` 和 `chart_path`。
3. 调用飞书推送脚本：
   ```bash
   python scripts/feishu_webhook_push.py --report output/weekly_report.json
   ```
4. 推送成功后，向用户确认："周报已生成并推送到飞书群，共 N 条关键指标。"
5. 若飞书推送返回非 0 状态码，把原始错误信息完整展示给用户，不要自行编造成功结果。

## 输出格式
向用户汇报时使用：
```
✅ 周报已生成并推送
📊 关键指标：{summary_text 的前 100 字}
🖼 趋势图：{chart_path}
📮 飞书群：已推送（消息 ID: {message_id}）
```

## 安全规则
- 不得在对话中回显 `.env` 里的任何密钥内容。
- 不得跳过"前置检查"直接执行推送。
- 若用户要求把周报发到未在白名单内的飞书群，先向用户确认群名称/ID 是否正确。
