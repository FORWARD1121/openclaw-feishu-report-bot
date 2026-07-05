# OpenClaw sandbox image for the Feishu weekly report workflow.
# Secrets are injected at runtime through env_file; never bake them into the image.

FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

RUN npm install -g openclaw

RUN useradd -m -s /bin/bash openclaw
USER openclaw
WORKDIR /home/openclaw/workspace

VOLUME ["/home/openclaw/workspace"]

ENV OPENCLAW_BIND_HOST=127.0.0.1
ENV OPENCLAW_BIND_PORT=18789

EXPOSE 18789

CMD ["openclaw", "gateway"]
