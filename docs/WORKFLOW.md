# Workflow：业务流程与智能体工作流

本项目展示的是一个自动化办公 Agent 工作流，而不是单个脚本工具。核心目标是把“数据处理、LLM 总结、企业 IM 推送、群内追问、安全部署”串成可演示、可验收的闭环。

## 1. 业务主线

```text
业务人员提供销售/运营数据
→ 系统读取 CSV/XLSX
→ 自动计算经营指标
→ 生成自然语言周报总结
→ 生成趋势图
→ 推送飞书群
→ 群成员继续追问详情
```

当前示例数据字段：

| 字段 | 含义 |
|---|---|
| `date` | 日期 |
| `revenue` | 当日营收 |
| `orders` | 当日订单数 |

当前统计指标：

| 指标 | 说明 |
|---|---|
| 总营收 | 周期内 revenue 求和 |
| 总订单数 | 周期内 orders 求和 |
| 客单价 | 总营收 / 总订单数 |
| 最佳单日 | revenue 最高的一天 |
| 最弱单日 | revenue 最低的一天 |
| 环比增长 | 最近 7 天营收 vs 前 7 天营收 |

## 2. Agent 调度逻辑

OpenClaw 负责调度，不直接负责业务计算。业务计算仍由 Python 脚本完成。

```text
用户自然语言指令
→ OpenClaw 识别意图
→ 匹配 skills/weekly-report/SKILL.md
→ 执行前置检查
→ 调用 generate_report.py
→ 检查 output/weekly_report.json
→ 调用 feishu_webhook_push.py
→ 返回执行结果
```

## 3. 出站消息链路

```text
weekly_report.json
→ feishu_webhook_push.py
→ 读取 summary_text / stats / chart_path
→ 可选上传趋势图获取 image_key
→ 构造飞书交互卡片
→ Webhook 签名
→ 推送到飞书群
```

## 4. 入站追问链路

```text
飞书群 @机器人
→ Feishu/Lark WebSocket 长连接接收 im.message.receive_v1
→ 解析文本
→ handle_command 路由
→ 读取 output/weekly_report.json
→ 回复关键指标
```

当前支持的文本指令：

| 指令 | 行为 |
|---|---|
| `详情` | 返回最佳单日、最弱单日、客单价 |
| `生成周报` | 重新生成示例周报 |
| `推送` | 推送最新周报到飞书群 |

## 5. 降级策略

| 场景 | 处理 |
|---|---|
| 未配置 `ANTHROPIC_API_KEY` | 使用本地模板生成总结 |
| Claude API 调用失败 | 捕获异常后一次性回退本地模板 |
| 数据文件不存在 | 返回非 0 退出码并打印错误 |
| 飞书推送失败 | 抛出原始错误，不伪造成功 |
| 还没有生成周报就问详情 | 提示先生成周报 |

## 6. 安全边界

- 密钥只放在 `config/.env`，不提交到仓库。
- Docker 只绑定 `127.0.0.1:18789`。
- 飞书事件接收使用 WebSocket 长连接，避免公网回调 URL。
- 公开仓库只保留示例数据，不放客户数据。

## 7. 验收闭环

交付时必须验证：

```text
A1 health_check 通过
A2 周报文件和趋势图生成成功
A3 飞书群收到卡片
A4 群内 @机器人 能回复详情
A5 OpenClaw 能自动调度 Skill
A6 Docker 能一键启动
A7 安全检查通过
```

详细标准见 `docs/ACCEPTANCE.md`。
