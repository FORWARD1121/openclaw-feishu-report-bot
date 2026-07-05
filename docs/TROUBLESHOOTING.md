# TROUBLESHOOTING：常见错误与解决

## 周报生成

**Q: `找不到数据文件: xxx.csv`**
检查 `--input` 路径。相对路径是相对于当前工作目录，建议在项目根目录执行。

**Q: `数据文件缺少必要列`**
输入文件必须含 `date, revenue, orders` 三列。参考 `sample_data/sample_sales.csv` 的格式。

**Q: 总结文字是模板生成的，不是大模型写的**
说明未配置 `ANTHROPIC_API_KEY`，或 API 调用失败已降级。查看 stderr 里的 WARNING 日志确认原因。
这是设计内的降级行为，保证离线也能出结果。

**Q: 趋势图中文乱码**
服务器缺中文字体。图表标题默认已用英文；如需中文，安装字体（如 `fonts-noto-cjk`）
并在 `generate_report.py` 里设置 `matplotlib.rcParams["font.sans-serif"]`。

## 飞书 Webhook 推送

**Q: `sign match fail`（19021）**
签名密钥错误或本机时间不准。核对 `FEISHU_WEBHOOK_SECRET`，并同步系统时间（`ntpdate`）。
飞书要求签名时间戳在当前时间 1 小时内。

**Q: `Key Words Not Found`（19024）**
群机器人设置了关键词校验，但推送内容不含关键词。要么去掉关键词校验，要么在卡片里包含它。

**Q: `incoming webhook access token invalid`（19001）**
`FEISHU_WEBHOOK_URL` 填错。重新从群机器人设置里复制完整地址。

**Q: 卡片里没有趋势图**
自定义 webhook 机器人不能直接发本地图片，需要企业应用凭证上传拿 image_key。
确认 `.env` 里配了 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`，且应用有 `im:resource` 权限。

## 飞书长连接（WebSocket）

**Q: 保存"使用长连接接收事件"时报错**
必须先本地启动 `feishu_ws_listener.py`，让长连接在线，飞书后台才能保存成功。

**Q: 群里 @机器人 没反应**
- 确认应用已发布且加入了该群
- 确认订阅了 `im.message.receive_v1` 事件
- 长连接是集群模式：同一应用起多个 client 时，只有随机一个收到消息，排查时只起一个
- 消息需在 3 秒内处理完，否则飞书会超时重推

**Q: 卡片按钮点击没回调**
已知限制：`card.action.trigger` 不支持长连接，只能走 Webhook。
本项目为避免公网暴露，采用纯文本指令方案，不依赖按钮回调。

## Docker

**Q: `COPY requirements.txt` 失败**
build context 必须是项目根。用 `docker compose`（已配置 `context: ..`），
不要在 `docker/` 目录里直接 `docker build .`。

**Q: 容器起来了但端口访问不到**
端口只绑定 `127.0.0.1`，是有意为之。远程访问走 Tailscale 内网，不要改成 `0.0.0.0`。

## OpenClaw

**Q: Skill 没被触发**
- 确认 `weekly-report/` 已复制到 workspace 的 `skills/` 目录
- 检查 `SKILL.md` 的 `description` 是否覆盖了你说的指令措辞
- 新建 session 后 Skill 才会重新加载

**Q: Skill 执行脚本时路径找不到**
OpenClaw 的工作目录要与脚本里的相对路径一致。Docker 部署时工作目录为
`/home/openclaw/workspace`，脚本、数据、output 都挂在这个目录下。
