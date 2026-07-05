# ACCEPTANCE：验收标准

交付方与客户共同逐条勾选。每项都要有可见证据（终端输出 / 飞书群截图 / 日志）。

## 验收清单

| 编号 | 验收项 | 操作 | 通过标准 | 证据 | 状态 |
|---|---|---|---|---|---|
| A1 | 环境自检 | `python scripts/health_check.py` | 无 FAIL 项 | 终端输出 | ☐ |
| A2 | 周报生成 | `python scripts/generate_report.py --input sample_data/sample_sales.csv` | 退出码 0，生成 `weekly_report.json` + `weekly_trend.png` | 终端输出 + 文件 | ☐ |
| A3 | 飞书卡片推送 | `python scripts/feishu_webhook_push.py --report output/weekly_report.json` | 飞书群收到含关键指标的卡片 | 飞书群截图 | ☐ |
| A4 | 群内追问（详情） | 启动 `feishu_ws_listener.py` 后，群里 @机器人 发"详情" | 机器人返回最佳单日、最弱单日、客单价 | 飞书群截图 | ☐ |
| A5 | OpenClaw 自动调度 | OpenClaw 中输入"生成本周销售周报并发到飞书群" | Skill 自动依次调用生成与推送，群里收到卡片 | `OPENCLAW_RUN_LOG.md` + 截图 | ☐ |
| A6 | Docker 一键启动 | `cd docker && docker compose up -d` | 容器 Up，端口仅 `127.0.0.1:18789` | `docker ps` 输出 | ☐ |
| A7 | 安全核查 | 见下方安全清单 | 全部满足 | 命令输出 | ☐ |

## 安全验收清单（A7 明细）

| 检查 | 命令 / 方法 | 通过标准 |
|---|---|---|
| .env 权限 | `stat -c '%a' config/.env` | 输出 `600` |
| .env 不入库 | `git check-ignore config/.env` | 输出该路径（表示已被忽略） |
| 端口不公网 | `grep 18789 docker/docker-compose.yml` | 仅见 `127.0.0.1:18789` |
| 无硬编码密钥 | `grep -rn "sk-" scripts/ ; grep -rn "cli_" scripts/` | 无真实密钥（示例占位除外） |
| 飞书权限最小 | 人工核对开放平台权限列表 | 仅勾选必要权限 |

## 已验证 vs 待客户环境验证

**离线可验证（交付前已完成，见 `docs/TEST_EVIDENCE.md`）：**
- A1 健康检查逻辑
- A2 周报生成主链路（含 API 失败降级、错误退出码）
- 三个脚本的 import、签名、卡片构造、命令路由逻辑

**必须在客户真实环境验证（需真实飞书凭证 / OpenClaw）：**
- A3 / A4 / A5 —— 依赖真实飞书应用与群
- A6 —— 依赖客户机器上的 Docker

> 交付诚信说明：本项目在开发环境已完成所有不依赖外部凭证的验证；
> A3-A5 需在装好飞书应用的真机上跑通并截图，不能用伪造日志代替。
