# CHANGELOG

## [0.2.0] - 2026-07-05 · 交付化改造

按工程交付评审意见，从"能演示"改造为"能交付"。

### 修复 (P0)
- 修复 `generate_report.py` 中 Claude API 失败后的**递归降级 bug**：
  拆出独立的 `build_local_summary()`，失败后一次性回退本地模板，不再重复调用 API。
  （已通过测试验证：模拟接口异常时 anthropic 仅被调用 1 次。）
- **统一配置读取**：新增 `scripts/common_env.py`，三个脚本统一 `load_env()`，
  修复此前 `generate_report.py` 读不到 `config/.env` 的问题。
- 所有脚本增加**明确退出码**：成功 0，失败非 0，并统一 logging 到 stderr。

### 新增 (P1)
- `scripts/health_check.py`：一键自检依赖 / 配置 / 目录 / Docker 端口绑定。
- `requirements.txt`：固定 Python 依赖版本。
- `.gitignore`：禁止提交 `.env`、`output/`、日志、密钥。
- `output/.gitkeep`：保留空目录。
- 文档拆分：`QUICKSTART.md` / `docs/DEPLOYMENT.md` / `docs/ACCEPTANCE.md` /
  `docs/TROUBLESHOOTING.md` / `docs/TEST_EVIDENCE.md` / `docs/OPENCLAW_RUN_LOG.md`。

### 变更
- `docker/Dockerfile`：工作目录改为 `/home/openclaw/workspace`，
  增加 `pip install -r requirements.txt`，用户无需进容器手动装依赖。
- `docker/docker-compose.yml`：build context 指向项目根（使 COPY 生效），
  修正 `env_file` 路径。

### 待办（需真机验证，未在开发环境完成）
- 飞书 Webhook 真实推送（A3）
- 飞书长连接群内追问（A4）
- OpenClaw 自动调度闭环（A5）
- Docker 一键启动（A6）
以上依赖真实飞书凭证 / OpenClaw 环境，见 `docs/TEST_EVIDENCE.md` 的"待真机验证"。

## [0.1.0] - 2026-07-04 · 初始版本
- OpenClaw + 飞书自动化周报的可演示版本（README、SKILL、三个脚本、Docker、示例数据）。
