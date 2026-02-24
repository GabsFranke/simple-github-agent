FROM python:3.11-slim

WORKDIR /app

# Copy shared module
COPY shared/ ./shared/

# Copy github-mcp-server (needed for auth)
COPY services/github-mcp-server/*.py ./services/github-mcp-server/

# Copy agent-worker
COPY services/agent-worker/requirements.txt ./services/agent-worker/
RUN pip install --no-cache-dir -r services/agent-worker/requirements.txt

COPY services/agent-worker/*.py ./services/agent-worker/

WORKDIR /app/services/agent-worker

CMD ["python", "worker.py"]
