# SimpleGitHubAgent - GitHub Integration

AI-powered GitHub agent that creates pull requests from issues using Gemini and Model Context Protocol (MCP).

## Quick Start

### Prerequisites

- Docker & Docker Compose (recommended) OR Python 3.11+
- GitHub App (create at https://github.com/settings/apps/new)
- Google AI API Key (get from https://aistudio.google.com/apikey)
- ngrok (for local testing) or cloud hosting

### Setup

1. **Configure environment:**

```bash
# Copy example config
cp .env.example .env

# Edit .env with your credentials:
# - GITHUB_APP_ID, GITHUB_CLIENT_ID, GITHUB_INSTALLATION_ID
# - GITHUB_PRIVATE_KEY_PATH (path to your .pem file)
# - GOOGLE_API_KEY (from Google AI Studio)
# - QUEUE_TYPE=redis (for Docker) or pubsub (for cloud)
```

2. **Run with Docker (recommended):**

```bash
# Start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

3. **Expose webhook with ngrok:**

```bash
ngrok http 8080
```

Update your GitHub App webhook URL with the ngrok URL.

4. **Manual setup (without Docker):**

See [START.md](START.md) for detailed instructions.

## Architecture

```
GitHub Issue → Webhook → Message Queue → Agent Worker → Gemini Agent
                            (Redis)                           ↓
                                                        GitHub MCP Server
                                                              ↓
                                                         GitHub API
```

The system uses a message queue architecture that works for both self-hosted (Redis) and cloud (Google Pub/Sub) deployments.

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
Subscribes to message queue and runs the Gemini agent with GitHub tools.

### 3. Webhook Service
Receives GitHub webhooks and publishes to message queue.

### 4. Message Queue
- Redis for self-hosted/development
- Google Pub/Sub for cloud production

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

### Environment Variables

- `QUEUE_TYPE`: `redis` (self-hosted) or `pubsub` (cloud)
- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)
- `PUBSUB_PROJECT_ID`: Google Cloud project ID (for cloud deployment)
- `PUBSUB_TOPIC`: Pub/Sub topic name (for cloud deployment)
- `PUBSUB_SUBSCRIPTION`: Pub/Sub subscription name (for cloud deployment)

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
SimpleGitHubAgent/
├── services/
│   ├── github-mcp-server/    # MCP server for GitHub API
│   ├── agent-worker/         # Gemini agent worker
│   └── webhook/              # Webhook receiver
├── shared/
│   └── queue.py             # Message queue abstraction
├── docker-compose.yml       # Docker Compose config
├── ARCHITECTURE.md          # Complete system design
├── PROGRESS.md             # Development tracker
└── START.md                # Detailed setup guide
```

### Documentation

- **[START.md](START.md)** - Step-by-step setup guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete technical architecture
- **[PROGRESS.md](PROGRESS.md)** - Development checklist

### Testing

With Docker:
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f webhook
docker-compose logs -f worker
```

Without Docker (manual):
```bash
# Test webhook service
cd services/webhook
python main.py

# Test agent worker
cd services/agent-worker
python worker.py
```

Note: The MCP server starts automatically when the agent needs it - no need to run it separately.

## Deployment

### Self-Hosted (Development)
Uses Docker Compose with Redis:
```bash
docker-compose up -d
```

### Cloud (Production)
Deploy to Google Cloud Run with Pub/Sub. See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed instructions.

## Progress

Track development progress in [PROGRESS.md](PROGRESS.md).

## License

MIT
