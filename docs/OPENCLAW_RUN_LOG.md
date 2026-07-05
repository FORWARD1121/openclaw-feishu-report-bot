# OPENCLAW_RUN_LOG：OpenClaw 调度闭环运行日志

> ⚠️ 本文件是**模板**。以下方括号内容需在装好 OpenClaw + 飞书应用的**真实环境**跑通后，
> 用真实终端输出 / 飞书截图替换。**请勿伪造**——评审明确要求这里放真实执行日志。

---

## 期望闭环

```
用户指令
→ OpenClaw 识别 weekly-report Skill
→ 调用 generate_report.py
→ 检查 weekly_report.json
→ 调用 feishu_webhook_push.py
→ 返回执行结果
```

## 真实运行记录（待填）

```text
[时间] __________
[用户输入] 生成本周销售周报并发到飞书群
[Skill 匹配] weekly-report
[执行] python scripts/generate_report.py --input sample_data/sample_sales.csv --output output/weekly_report.json
[结果] __________（贴真实退出码/输出）
[执行] python scripts/feishu_webhook_push.py --report output/weekly_report.json
[结果] __________（贴真实退出码/输出）
[飞书消息] __________（贴群消息 ID 或截图路径）
```

## 群内追问记录（待填）

```text
[时间] __________
[群内消息] @机器人 详情
[长连接收到] im.message.receive_v1
[机器人回复] __________（贴真实回复内容/截图）
```

## 截图清单（待补）

- [ ] OpenClaw 终端：指令识别 + Skill 匹配
- [ ] 飞书群：收到周报卡片
- [ ] 飞书群：@机器人 发"详情"
- [ ] 飞书群：机器人回复详情

---

填完后，把本文件与 `docs/ACCEPTANCE.md` 一并作为验收材料交付。
