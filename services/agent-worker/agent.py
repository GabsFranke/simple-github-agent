import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Load environment variables
load_dotenv()

# Get the absolute path to the MCP server
_current_dir = os.path.dirname(os.path.abspath(__file__))
_mcp_server_path = os.path.join(_current_dir, '..', 'github-mcp-server', 'server.py')

# Sub-agent for web search
google_search_agent = LlmAgent(
    name='google_search_agent',
    model='gemini-2.5-flash',
    description='Agent specialized in performing Google searches.',
    sub_agents=[],
    instruction='Use the GoogleSearchTool to find information on the web.',
    tools=[GoogleSearchTool()],
)

# Sub-agent for URL content fetching
url_context_agent = LlmAgent(
    name='url_context_agent',
    model='gemini-2.5-flash',
    description='Agent specialized in fetching content from URLs.',
    sub_agents=[],
    instruction='Use the UrlContextTool to retrieve content from provided URLs.',
    tools=[url_context],
)

# Main agent with GitHub capabilities via MCP
root_agent = LlmAgent(
    name='SimpleGitHubAgent',
    model='gemini-2.5-flash',
    description='AI agent that helps with GitHub tasks by creating branches, modifying files, and creating pull requests.',
    sub_agents=[],
    instruction="""You are SimpleGitHubAgent, an AI assistant that helps developers with GitHub tasks.

When a user asks you to work on an issue, follow these steps:
1. Use get_issue to understand the issue details
2. Use list_files and read_file to explore the repository
3. Create a new branch using create_branch with a descriptive name (e.g., "feature/add-login-button")
4. Make necessary file changes using update_file
5. Create a pull request using create_pull_request

IMPORTANT: If the user just wants a simple response (like "ping/pong"), just respond with text - don't create branches or PRs.

Always:
- Use clear, descriptive branch names
- Write meaningful commit messages
- Include "Fixes #<issue_number>" in PR descriptions
- Explain what you're doing at each step

You have access to web search and URL fetching for research when needed.""",
    tools=[
        # GitHub MCP Toolset
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='python',
                    args=[_mcp_server_path],
                    env={
                        'GITHUB_APP_ID': os.getenv('GITHUB_APP_ID'),
                        'GITHUB_PRIVATE_KEY': os.getenv('GITHUB_PRIVATE_KEY'),
                        'GITHUB_INSTALLATION_ID': os.getenv('GITHUB_INSTALLATION_ID'),
                    }
                ),
                timeout=30,
            ),
            tool_filter=[
                'read_file',
                'list_files',
                'create_branch',
                'update_file',
                'create_pull_request',
                'get_issue',
            ],
        ),
        # Sub-agents for web research
        agent_tool.AgentTool(agent=google_search_agent),
        agent_tool.AgentTool(agent=url_context_agent),
    ],
)
