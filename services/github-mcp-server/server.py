"""GitHub MCP Server implementation."""
import asyncio
import logging
import os
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import AnyUrl

from auth import GitHubAppAuth
from github_tools import GitHubTools
from permissions import PermissionManager, Permission

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize server
app = Server("github-mcp-server")

# Global state
github_auth: GitHubAppAuth = None
permission_manager = PermissionManager()
default_installation_id: int = None


def get_github_tools(agent_id: str = "SimpleGitHubAgent") -> GitHubTools:
    """Get GitHub tools instance for an agent."""
    gh_client = github_auth.get_github_client(default_installation_id)
    return GitHubTools(gh_client)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available GitHub tools."""
    return [
        Tool(
            name="read_file",
            description="Read a file from a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "ref": {
                        "type": "string",
                        "description": "Branch, tag, or commit SHA (default: main)",
                        "default": "main"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent identifier for permission checking",
                        "default": "SimpleGitHubAgent"
                    }
                },
                "required": ["repo", "path"]
            }
        ),
        Tool(
            name="list_files",
            description="List files in a directory of a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory path (empty for root)",
                        "default": ""
                    },
                    "ref": {
                        "type": "string",
                        "description": "Branch, tag, or commit SHA (default: main)",
                        "default": "main"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent identifier for permission checking",
                        "default": "SimpleGitHubAgent"
                    }
                },
                "required": ["repo"]
            }
        ),
        Tool(
            name="create_branch",
            description="Create a new branch in a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Name for the new branch"
                    },
                    "from_ref": {
                        "type": "string",
                        "description": "Source branch/ref (default: main)",
                        "default": "main"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent identifier for permission checking",
                        "default": "SimpleGitHubAgent"
                    }
                },
                "required": ["repo", "branch_name"]
            }
        ),
        Tool(
            name="update_file",
            description="Create or update a file in a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "File content"
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch to commit to"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent identifier for permission checking",
                        "default": "SimpleGitHubAgent"
                    }
                },
                "required": ["repo", "path", "content", "message", "branch"]
            }
        ),
        Tool(
            name="create_pull_request",
            description="Create a pull request in a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "title": {
                        "type": "string",
                        "description": "PR title"
                    },
                    "body": {
                        "type": "string",
                        "description": "PR description"
                    },
                    "head": {
                        "type": "string",
                        "description": "Branch containing changes"
                    },
                    "base": {
                        "type": "string",
                        "description": "Base branch (default: main)",
                        "default": "main"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent identifier for permission checking",
                        "default": "SimpleGitHubAgent"
                    }
                },
                "required": ["repo", "title", "body", "head"]
            }
        ),
        Tool(
            name="get_issue",
            description="Get details of a GitHub issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "issue_number": {
                        "type": "integer",
                        "description": "Issue number"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent identifier for permission checking",
                        "default": "SimpleGitHubAgent"
                    }
                },
                "required": ["repo", "issue_number"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls."""
    agent_id = arguments.get("agent_id", "SimpleGitHubAgent")
    
    try:
        tools = get_github_tools(agent_id)
        
        if name == "read_file":
            permission_manager.check_permission(agent_id, Permission.READ_FILE)
            result = tools.read_file(
                repo=arguments["repo"],
                path=arguments["path"],
                ref=arguments.get("ref", "main")
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "list_files":
            permission_manager.check_permission(agent_id, Permission.LIST_FILES)
            result = tools.list_files(
                repo=arguments["repo"],
                path=arguments.get("path", ""),
                ref=arguments.get("ref", "main")
            )
            return [TextContent(type="text", text=str(result))]
        
        elif name == "create_branch":
            permission_manager.check_permission(agent_id, Permission.CREATE_BRANCH)
            result = tools.create_branch(
                repo=arguments["repo"],
                branch_name=arguments["branch_name"],
                from_ref=arguments.get("from_ref", "main")
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "update_file":
            permission_manager.check_permission(agent_id, Permission.UPDATE_FILE)
            result = tools.update_file(
                repo=arguments["repo"],
                path=arguments["path"],
                content=arguments["content"],
                message=arguments["message"],
                branch=arguments["branch"]
            )
            return [TextContent(type="text", text=result)]
        
        elif name == "create_pull_request":
            permission_manager.check_permission(agent_id, Permission.CREATE_PR)
            result = tools.create_pull_request(
                repo=arguments["repo"],
                title=arguments["title"],
                body=arguments["body"],
                head=arguments["head"],
                base=arguments.get("base", "main")
            )
            return [TextContent(type="text", text=str(result))]
        
        elif name == "get_issue":
            permission_manager.check_permission(agent_id, Permission.GET_ISSUE)
            result = tools.get_issue(
                repo=arguments["repo"],
                issue_number=arguments["issue_number"]
            )
            return [TextContent(type="text", text=str(result))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        return [TextContent(type="text", text=f"Permission denied: {e}")]
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]


async def main():
    """Run the MCP server."""
    global github_auth, default_installation_id
    
    # Load configuration
    app_id = os.getenv("GITHUB_APP_ID")
    private_key = os.getenv("GITHUB_PRIVATE_KEY")
    default_installation_id = int(os.getenv("GITHUB_INSTALLATION_ID"))
    
    if not app_id or not private_key:
        raise ValueError("GITHUB_APP_ID and GITHUB_PRIVATE_KEY must be set")
    
    # Initialize GitHub auth
    github_auth = GitHubAppAuth(app_id, private_key)
    
    logger.info("Starting GitHub MCP Server...")
    logger.info(f"App ID: {app_id}")
    logger.info(f"Installation ID: {default_installation_id}")
    
    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
