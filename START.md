# How to Start SimpleGitHubAgent

## Quick Start

### Terminal 1: Start Webhook Service
```powershell
cd services/webhook
.\venv\Scripts\Activate.ps1
python main.py
```

### Terminal 2: Start ngrok
```powershell
ngrok http 8080
```

Then:
1. Copy the ngrok URL (e.g., `https://xxx.ngrok-free.dev`)
2. Go to https://github.com/settings/apps/simplegithubagent
3. Update Webhook URL to: `https://xxx.ngrok-free.dev/webhook`
4. Save

### Test It
1. Create an issue in your repo
2. Comment: `/agent help with this`
3. Watch the agent work! 🤖

## What's Running

- **Webhook Service** (port 8080): Receives GitHub webhooks
- **ngrok**: Exposes your local webhook to the internet
- **Agent Worker**: Runs automatically when webhook receives a command
- **MCP Server**: Starts automatically when agent needs GitHub access

## Stopping

Press `Ctrl+C` in each terminal to stop the services.

## Troubleshooting

**Webhook not receiving events?**
- Check ngrok is running
- Verify webhook URL in GitHub App settings
- Check webhook service logs

**Agent not responding?**
- Check `.env` has `GOOGLE_API_KEY`
- Check `.env` has GitHub credentials
- Look at webhook service terminal for errors

**Can't post comments?**
- Set `GITHUB_TOKEN` in `.env` (personal access token)
- Or the agent will try to use GitHub App auth
