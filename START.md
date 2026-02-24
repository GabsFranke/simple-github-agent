# How to Start SimpleGitHubAgent

## Quick Start with Docker Compose (Recommended)

### Prerequisites
- Docker & Docker Compose
- ngrok (for webhooks)
- GitHub App configured
- Google AI API Key

### Start Everything

```powershell
# 1. Configure .env
cp .env.example .env
# Edit .env with your credentials

# 2. Start all services
docker-compose up -d

# 3. Start ngrok (in another terminal)
ngrok http 8080

# 4. Update GitHub App webhook URL
# Go to https://github.com/settings/apps/your-app
# Set webhook URL to: https://your-ngrok-url.ngrok-free.dev/webhook
```

That's it! The agent is now running and will respond to `/agent` commands.

### View Logs
```powershell
docker-compose logs -f worker    # Agent worker logs
docker-compose logs -f webhook   # Webhook logs
docker-compose logs -f redis     # Redis logs
```

### Stop Everything
```powershell
docker-compose down
```

---

## Manual Start (Development)

### Terminal 1: Start Redis
```powershell
docker run -p 6379:6379 redis:7-alpine
```

### Terminal 2: Start Webhook Service
```powershell
cd services/webhook
.\venv\Scripts\Activate.ps1
python main.py
```

### Terminal 3: Start Worker
```powershell
cd services/agent-worker
.\venv\Scripts\Activate.ps1
python worker.py
```

### Terminal 4: Start ngrok
```powershell
ngrok http 8080
```

Then update GitHub App webhook URL as above.

---

## What's Running

- **Redis** (port 6379): Message queue
- **Webhook Service** (port 8080): Receives GitHub webhooks
- **Worker**: Processes agent requests from queue
- **ngrok**: Exposes webhook to internet
- **MCP Server**: Starts automatically when agent needs GitHub access

## Testing

1. Create an issue in your repo
2. Comment: `/agent help with this`
3. Watch the agent work! 🤖

Check logs to see what's happening:
- Webhook receives command → publishes to Redis
- Worker picks up from Redis → runs agent
- Agent uses MCP → creates branch/PR
- Worker posts result back to GitHub

## Troubleshooting

**Services won't start?**
- Check `.env` has all required values
- Ensure Redis is running
- Check Docker is running

**Webhook not receiving events?**
- Verify ngrok is running
- Check webhook URL in GitHub App settings
- Look at webhook service logs

**Agent not responding?**
- Check worker logs: `docker-compose logs -f worker`
- Verify `GOOGLE_API_KEY` is set
- Check Redis is accessible

**Can't post comments?**
- Verify GitHub App has correct permissions
- Check `GITHUB_APP_ID` and `GITHUB_INSTALLATION_ID` are correct
