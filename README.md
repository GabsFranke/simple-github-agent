# SimpleGitHubAgent - GitHub Integration

AI-powered GitHub agent that creates pull requests from issues using Gemini and Model Context Protocol (MCP).

## Quick Start

### Prerequisites

- Python 3.11+
- GitHub App (create at https://github.com/settings/apps/new)
- Google AI API Key (get from https://aistudio.google.com/apikey)
- ngrok (for local testing) or cloud hosting

### Setup

1. **Install dependencies for each service:**

```powershell
# GitHub MCP Server
cd services/github-mcp-server
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ../..

# Agent Worker  
cd services/agent-worker
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ../..

# Webhook Service
cd services/webhook
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ../..
```

2. **Configure environment:**

```powershell
# Copy example config
cp .env.example .env

# Edit .env with your credentials:
# - GITHUB_APP_ID, GITHUB_CLIENT_ID, GITHUB_INSTALLATION_ID
# - GITHUB_PRIVATE_KEY (from your GitHub App)
# - GOOGLE_API_KEY (from Google AI Studio)
```

3. **Run locally:**

See [START.md](START.md) for detailed instructions.

## Architecture

```
GitHub Issue → Webhook → Pub/Sub → Agent Worker → Vertex AI Agent
                                                         ↓
                                                   GitHub MCP Server
                                                         ↓
                                                    GitHub API
```

## Components

### 1. GitHub MCP Server
Provides GitHub API access through Model Context Protocol with permission management.

**Tools:**
- `read_file` - Read files from repository
- `list_files` - List directory contents
- `create_branch` - Create new branches
- `update_file` - Create/update files
- `create_pull_request` - Create PRs
- `get_issue` - Get issue details

### 2. Agent Worker
Processes requests and runs the Vertex AI agent with GitHub tools.

### 3. Webhook Service
Receives GitHub webhooks and triggers agent processing.

## Usage

1. Create an issue in your GitHub repository
2. Comment on the issue: `/agent create a PR for this`
3. The agent will:
   - Analyze the issue
   - Create a branch
   - Make necessary changes
   - Create a pull request
   - Comment with the PR link

## Configuration

See `.env.example` for all configuration options.

### GitHub App Setup

1. Go to GitHub Settings → Developer settings → GitHub Apps
2. Create a new GitHub App with:
   - Webhook URL: `https://your-domain/webhook`
   - Permissions:
     - Repository contents: Read & Write
     - Issues: Read & Write
     - Pull requests: Read & Write
   - Subscribe to events:
     - Issue comments
3. Generate and download private key
4. Install the app on your repositories

## Development

### Project Structure
```
vertex-github-agent/
├── services/
│   ├── github-mcp-server/    # MCP server for GitHub API
│   ├── agent-worker/         # Vertex AI agent worker
│   └── webhook/              # Webhook receiver
├── ARCHITECTURE.md           # Complete system design
├── PROGRESS.md              # Development tracker
├── GETTING_STARTED.md       # Detailed setup guide
├── PROJECT_SUMMARY.md       # Project overview
└── test_local.py            # Local testing script
```

### Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Step-by-step setup guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete technical architecture
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview and status
- **[PROGRESS.md](PROGRESS.md)** - Development checklist

### Testing

```powershell
# Test webhook service
cd services/webhook
.\venv\Scripts\Activate.ps1
python main.py

# Test agent worker (requires TEST_REPO and TEST_ISSUE env vars)
cd services/agent-worker
.\venv\Scripts\Activate.ps1
$env:TEST_REPO="owner/repo"
$env:TEST_ISSUE="1"
python worker.py
```

Note: The MCP server starts automatically when the agent needs it - no need to run it separately.

## Deployment

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed deployment instructions.

## Progress

Track development progress in [PROGRESS.md](PROGRESS.md).

## License

MIT
