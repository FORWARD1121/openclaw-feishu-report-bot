# TEST_EVIDENCE：开发环境已验证内容

本文件记录在开发环境（无外部飞书/大模型凭证、网络受限）中**真实跑通**的验证，
作为"不是纸面 Demo"的证据。凡是需要真实凭证的部分，明确标注为"待真机验证"，不伪造。

---

## 已真实验证 ✅

### 1. 周报生成主链路（A2）
命令：
```
python scripts/generate_report.py --input sample_data/sample_sales.csv
```
结果：退出码 0，生成 `output/weekly_report.json`（540 字节）与 `output/weekly_trend.png`（约 64 KB）。
生成的 stats：总营收 199400、总订单 1315、客单价 151.63、环比 +7.5%、最佳单日 2026-07-04。

### 2. 错误处理与退出码
命令：
```
python scripts/generate_report.py --input sample_data/does_not_exist.csv
```
结果：stderr 打印 `[错误] 找不到数据文件`，退出码 **1**（符合交付要求"失败返回非 0"）。

### 3. 递归降级 bug 已修复（评审 P0）
用测试脚本模拟"配置了 API Key 但 anthropic 接口异常"的场景，
统计 `anthropic` 被调用次数：**1 次**（修复前会重复调用）。
确认失败后仅一次性回退本地模板，不再递归调用 API。

### 4. 统一配置读取（评审 P0）
三个脚本（generate_report / feishu_webhook_push / feishu_ws_listener）
均改为 `from common_env import load_env`，import 全部成功，行为一致。

### 5. 健康检查（A1）
命令：
```
python scripts/health_check.py
```
结果：正确输出各项 PASS/WARN，并成功检出 "Docker 端口仅绑定 127.0.0.1"，退出码 0。

### 6. 飞书脚本逻辑（不含真实网络）
- `feishu_webhook_push`：签名函数 `gen_sign` 输出正常，卡片 `build_card` 构造正确。
- `feishu_ws_listener`：import 成功；命令路由 `handle_command` 对"详情/未知指令"返回正确内容。
  （用 lark_oapi stub 验证逻辑，未做真实连接。）

---

## 待真机验证 ⏳（需真实凭证，不能在开发环境完成）

| 项 | 依赖 | 验证方式 |
|---|---|---|
| A3 飞书卡片真实推送 | 真实 Webhook + 密钥 | 真机跑 feishu_webhook_push.py，飞书群截图 |
| A4 群内追问回复 | 真实企业应用 + 长连接 | 真机启动 listener，群里发"详情"，截图 |
| A5 OpenClaw 自动调度 | 安装 OpenClaw + workspace | 真机执行指令，日志记入 OPENCLAW_RUN_LOG.md |
| A6 Docker 一键启动 | 客户机 Docker | `docker compose up -d` + `docker ps` 截图 |
| 大模型真实总结 | 有效 ANTHROPIC_API_KEY | 配置后跑 generate_report，总结由 Claude 生成 |

---

## 环境说明
开发环境网络受限，`lark-oapi` 无法在线安装，因此 A3-A5 无法在此环境完成真实联调。
这些项已在代码层通过 stub/静态验证逻辑正确性，真实收发必须在装好飞书应用的机器上完成。
