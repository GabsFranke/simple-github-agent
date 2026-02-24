# SimpleGitHubAgent - GitHub Integration Architecture

## Overview

Enterprise-grade GitHub App integrated with Vertex AI agents, enabling automated PR creation from GitHub issues using slash commands.

## System Architecture

```
GitHub Issue (/agent command)
    ↓
GitHub Webhook
    ↓
Cloud Run (Webhook Service)
    ↓
Pub/Sub Topic
    ↓
Cloud Run (Agent Worker)
    ↓
Vertex AI Agent ←→ GitHub MCP Server ←→ GitHub API
    ↓
Response posted back to GitHub
```

## Components

### 1. GitHub MCP Server
**Purpose**: Centralized GitHub API access with permission control

**Responsibilities**:
- Implements GitHub tools as MCP tools
- Enforces permission-based access control (RBAC)
- Manages GitHub App authentication
- Provides audit logging
- Handles rate limiting

**Tools Exposed**:
- `create_branch` - Creates a new branch
- `read_file` - Reads file content from repository
- `update_file` - Creates or updates files
- `create_pull_request` - Creates PRs
- `list_files` - Lists repository files
- `get_issue` - Retrieves issue details

**Technology**: Python, MCP SDK, PyGithub

### 2. Webhook Service
**Purpose**: Receives and validates GitHub webhooks

**Responsibilities**:
- Validates webhook signatures
- Parses slash commands (`/agent`)
- Extracts context (issue, repo, user)
- Publishes to Pub/Sub
- Returns 200 OK quickly (< 10s)

**Endpoints**:
- `POST /webhook` - GitHub webhook receiver
- `GET /health` - Health check

**Technology**: FastAPI, Cloud Run

### 3. Agent Worker
**Purpose**: Processes agent requests asynchronously

**Responsibilities**:
- Subscribes to Pub/Sub messages
- Connects to GitHub MCP Server
- Wraps MCP tools as Vertex AI tools
- Executes Vertex AI agent
- Posts responses back to GitHub
- Handles errors and retries

**Technology**: Python, Google ADK, MCP Client, Cloud Run

### 4. Vertex AI Agent
**Purpose**: AI logic and decision making

**Responsibilities**:
- Analyzes GitHub issues
- Plans implementation approach
- Calls GitHub tools to create branches, files, PRs
- Generates code and commit messages
- Provides status updates

**Configuration**:
- Model: Gemini 2.5 Flash
- Sub-agents: Google Search, URL Context
- Tools: GitHub MCP tools

## Project Structure

```
vertex-github-agent/
├── services/
│   ├── webhook/
│   │   ├── main.py                # FastAPI webhook receiver
│   │   ├── github_auth.py         # GitHub App JWT authentication
│   │   ├── models.py              # Request/response models
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── agent-worker/
│   │   ├── agent.py              # Vertex AI agent definition
│   │   ├── worker.py             # Pub/Sub subscriber
│   │   ├── mcp_tools.py          # MCP tool wrappers
│   │   ├── github_poster.py      # Posts responses to GitHub
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── github-mcp-server/
│       ├── server.py             # MCP server implementation
│       ├── github_tools.py       # GitHub API tool implementations
│       ├── permissions.py        # RBAC permission definitions
│       ├── auth.py               # GitHub App token management
│       ├── requirements.txt
│       └── Dockerfile
│
├── shared/
│   ├── models.py                 # Shared Pydantic models
│   ├── config.py                 # Configuration management
│   └── mcp_client.py            # MCP client wrapper
│
├── infrastructure/
│   ├── pubsub.tf                # Pub/Sub topic and subscriptions
│   ├── cloud_run.tf             # Cloud Run services
│   ├── iam.tf                   # IAM roles and permissions
│   └── secrets.tf               # Secret Manager configuration
│
├── tests/
│   ├── test_webhook.py
│   ├── test_agent.py
│   └── test_mcp_server.py
│
├── .env.example
├── docker-compose.yml           # Local development
├── README.md
└── PROGRESS.md
```

## Data Flow

### Issue to PR Flow

1. **User Action**
   - Creates GitHub issue: "Add login button to homepage"
   - Comments: `/agent create a PR for this`

2. **Webhook Reception**
   - GitHub sends webhook to Cloud Run
   - Webhook service validates signature
   - Extracts: repo, issue number, command, user

3. **Message Publishing**
   - Publishes to Pub/Sub topic: `agent-requests`
   - Message includes: issue context, repository info, command

4. **Agent Processing**
   - Worker receives message from Pub/Sub
   - Initializes Vertex AI agent
   - Connects to GitHub MCP Server

5. **Agent Execution**
   - Agent analyzes issue content
   - Plans implementation
   - Calls MCP tools:
     - `create_branch("feature/login-button")`
     - `read_file("index.html")`
     - `update_file("index.html", new_content)`
     - `create_pull_request("Add login button", "Fixes #123")`

6. **Response**
   - Worker posts comment to issue
   - "✅ Created PR #124 with login button implementation"
   - Links to the new PR

## Authentication & Security

### GitHub App Authentication
- **App ID**: From GitHub App settings
- **Client ID**: From GitHub App settings
- **Installation ID**: From app installation URL
- **Private Key**: Stored in Secret Manager

### Token Flow
1. Generate JWT using App private key
2. Exchange JWT for installation access token
3. Use installation token for GitHub API calls
4. Tokens expire after 1 hour (auto-refresh)

### Webhook Security
- Validate webhook signature using webhook secret
- Verify payload authenticity
- Rate limiting per installation

### MCP Server Security
- Agent identity verification
- Permission-based tool access
- Audit logging of all operations

## Scalability Considerations

### Horizontal Scaling
- All services are stateless
- Cloud Run auto-scales based on load
- Pub/Sub handles message buffering

### Rate Limiting
- GitHub API: 5,000 requests/hour per installation
- MCP server implements token bucket algorithm
- Queue requests during rate limit periods

### Cost Optimization
- Cloud Run scales to zero when idle
- Pub/Sub pay-per-message
- Vertex AI pay-per-token

### Performance Targets
- Webhook response: < 1s
- Agent processing: < 30s for simple tasks
- End-to-end: < 60s for PR creation

## Monitoring & Observability

### Metrics
- Webhook latency
- Agent execution time
- GitHub API rate limit usage
- Error rates by component
- Pub/Sub message age

### Logging
- Structured JSON logs
- Request tracing with correlation IDs
- Agent decision logging
- GitHub API call logging

### Alerting
- Webhook failures
- Agent errors
- Rate limit approaching
- Pub/Sub message backlog

## Development Phases

### Phase 1: Local Development (Current)
- [ ] Set up local development environment
- [ ] Build GitHub MCP Server
- [ ] Create basic Vertex AI agent
- [ ] Test locally with mock webhooks
- [ ] Verify end-to-end flow

### Phase 2: Cloud Deployment
- [ ] Deploy GitHub MCP Server to Cloud Run
- [ ] Deploy Webhook Service
- [ ] Deploy Agent Worker
- [ ] Configure Pub/Sub
- [ ] Set up Secret Manager
- [ ] Configure GitHub App webhook URL

### Phase 3: Production Hardening
- [ ] Add comprehensive error handling
- [ ] Implement retry logic
- [ ] Add monitoring and alerting
- [ ] Set up CI/CD pipeline
- [ ] Load testing
- [ ] Security audit

### Phase 4: Feature Expansion
- [ ] Add multi-agent support
- [ ] Implement more GitHub tools
- [ ] Add code review capabilities
- [ ] Support multiple repositories
- [ ] Add user preferences

## Technology Stack

### Core Technologies
- **Language**: Python 3.11+
- **Agent Framework**: Google ADK (Agent Development Kit)
- **AI Model**: Gemini 2.5 Flash
- **Protocol**: Model Context Protocol (MCP)

### Infrastructure
- **Cloud Platform**: Google Cloud Platform
- **Compute**: Cloud Run (serverless containers)
- **Messaging**: Pub/Sub
- **Secrets**: Secret Manager
- **IaC**: Terraform

### Libraries & Frameworks
- **Web Framework**: FastAPI
- **GitHub API**: PyGithub
- **MCP**: mcp Python SDK
- **Validation**: Pydantic
- **Testing**: pytest
- **Async**: asyncio

## Configuration

### Environment Variables

**Webhook Service**:
```
GITHUB_APP_ID=<your_app_id>
GITHUB_CLIENT_ID=<your_client_id>
GITHUB_WEBHOOK_SECRET=<secret>
GITHUB_PRIVATE_KEY=<secret>
PUBSUB_TOPIC=agent-requests
GCP_PROJECT_ID=<project>
```

**Agent Worker**:
```
PUBSUB_SUBSCRIPTION=agent-requests-sub
MCP_SERVER_URL=<mcp-server-url>
GITHUB_APP_ID=<your_app_id>
GITHUB_PRIVATE_KEY=<secret>
GCP_PROJECT_ID=<project>
VERTEX_AI_LOCATION=us-central1
```

**GitHub MCP Server**:
```
GITHUB_APP_ID=<your_app_id>
GITHUB_PRIVATE_KEY=<secret>
MCP_TRANSPORT=stdio
LOG_LEVEL=INFO
```

## Future Enhancements

### Multi-Agent Architecture
- Specialized agents for different tasks
- Agent orchestration layer
- Per-agent permission management

### Advanced Features
- Code review automation
- Test generation
- Documentation updates
- Issue triage and labeling
- Release automation

### Integration Expansion
- Slack notifications
- Jira integration
- CI/CD pipeline integration
- Analytics dashboard

## References

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/agent-builder)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
