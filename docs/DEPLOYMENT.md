# DEPLOYMENT：正式部署步骤

面向：上门给客户部署的实施工程师。目标：从零到飞书全链路可用。

---

## 阶段 0：环境准备（客户设备）

设备可能是 Mac Mini / Linux 服务器 / 树莓派，统一按下面装：

```bash
# Node.js v22+（nvm 管理版本）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install 22 && nvm use 22

# Python 3.x
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12
```

## 阶段 1：拉取项目并安装依赖

```bash
git clone <你的仓库地址> openclaw-feishu-report
cd openclaw-feishu-report
pip install -r requirements.txt
```

## 阶段 2：配置密钥

```bash
cp config/.env.example config/.env
chmod 600 config/.env      # 限制权限，安全要求
vim config/.env            # 填入下列各项
```

需要填：

| 变量 | 从哪拿 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic 控制台 |
| `FEISHU_APP_ID` / `FEISHU_APP_SECRET` | 飞书开放平台 → 企业自建应用 → 凭证与基础信息 |
| `FEISHU_WEBHOOK_URL` | 目标群 → 设置 → 群机器人 → 自定义机器人 |
| `FEISHU_WEBHOOK_SECRET` | 上面自定义机器人的"签名校验"密钥 |

## 阶段 3：飞书开放平台配置

1. 创建"企业自建应用"，记录 App ID / App Secret。
2. **权限**（最小化原则，只勾必要的）：
   - `im:message`（发送消息）
   - `im:message:send_as_bot`
   - `im:resource`（上传图片，用于发趋势图）
3. **事件订阅**：接收方式选 **"使用长连接接收事件"**（不需要公网 IP），
   订阅 `im.message.receive_v1`。
4. 群里添加：群设置 → 群机器人 → 添加"自定义机器人"（拿 Webhook），
   同时把上面的企业应用也添加进群（用于长连接接收）。
5. 发布应用版本并等待审核通过。

## 阶段 4：内网穿透（Tailscale）

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

登录同一 tailnet 后，运维可用手机/笔记本通过内网 IP 访问设备，**不需要开放公网端口**。

## 阶段 5：部署 OpenClaw

```bash
# 方式 A：Docker（推荐，一键、隔离）
cd docker
docker compose up -d
docker compose logs -f openclaw

# 方式 B：直接跑（调试用）
npm install -g openclaw
openclaw onboard
cp -r skills/weekly-report ~/.openclaw/workspace/skills/
```

## 阶段 6：自检 + 联调验证

```bash
python scripts/health_check.py     # 期望：无 FAIL

# 出站：飞书群应收到周报卡片
python scripts/generate_report.py --input sample_data/sample_sales.csv
python scripts/feishu_webhook_push.py --report output/weekly_report.json

# 入站：启动长连接，群里 @机器人 发"详情"应收到回复
python scripts/feishu_ws_listener.py
```

全部通过后，按 `docs/ACCEPTANCE.md` 逐项验收，并把执行结果记录到
`docs/OPENCLAW_RUN_LOG.md`（模板已给出）。

## 常见问题

见 `docs/TROUBLESHOOTING.md`。
