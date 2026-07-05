# Contributing

Thanks for considering a contribution. This project is a small, practical workflow demo, so contributions should keep the code easy to run and easy to audit.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/health_check.py
python scripts/generate_report.py --input sample_data/sample_sales.csv
```

## Contribution scope

Good contributions include:

- More robust data loaders for CSV/XLSX business reports.
- Additional report templates.
- Safer Feishu/Lark message handling.
- Better OpenClaw skill prompts.
- Tests, documentation, and deployment fixes.

Avoid committing:

- Real `.env` files.
- API keys, webhook URLs, tenant tokens, app secrets, or screenshots containing credentials.
- Customer business data.
- Generated outputs such as `weekly_report.json` or chart images.

## Pull request checklist

Before opening a PR, run:

```bash
python -m compileall scripts
python scripts/health_check.py
python scripts/generate_report.py --input sample_data/sample_sales.csv
```

Then describe:

1. What changed.
2. Why it changed.
3. How you verified it.
4. Whether real Feishu/OpenClaw validation is required.
