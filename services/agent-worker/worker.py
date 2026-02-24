"""Agent worker that processes GitHub requests from message queue."""
import os
import json
import logging
import asyncio
import sys
from typing import Dict, Any
from github import Github
from google.adk.runners import InMemoryRunner
from google.genai import types

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'github-mcp-server'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from auth import GitHubAppAuth
from shared.queue import get_queue

from agent import root_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentWorker:
    """Processes agent requests and posts responses to GitHub."""
    
    def __init__(self):
        self.agent = root_agent
        self.runner = InMemoryRunner(agent=self.agent, app_name="simplegithubagent")
        
        # Initialize GitHub App auth
        self.github_auth = GitHubAppAuth(
            os.getenv("GITHUB_APP_ID"),
            os.getenv("GITHUB_PRIVATE_KEY")
        )
    
    def _get_github_client(self, installation_id: int = None) -> Github:
        """Get authenticated GitHub client using App auth."""
        if not installation_id:
            installation_id = int(os.getenv("GITHUB_INSTALLATION_ID"))
        
        token = self.github_auth.get_installation_token(installation_id)
        return Github(token)
    
    async def process_request_async(self, request_data: Dict[str, Any]) -> None:
        """Process an agent request asynchronously."""
        try:
            repo_name = request_data["repository"]
            issue_number = request_data["issue_number"]
            command = request_data["command"]
            user = request_data.get("user", "unknown")
            installation_id = request_data.get("installation_id")
            
            logger.info(f"Processing request for {repo_name} issue #{issue_number}")
            logger.info(f"Command: {command}")
            
            # Build prompt for agent
            prompt = f"""A user @{user} has requested help with issue #{issue_number} in repository {repo_name}.

Command: {command}

Please help by:
1. Getting the issue details to understand what's needed
2. Analyzing the repository structure
3. Creating a branch for the work
4. Making the necessary changes
5. Creating a pull request
6. Summarizing what you did

Repository: {repo_name}
Issue: #{issue_number}
"""
            
            # Create session
            session_id = f"{repo_name.replace('/', '_')}_{issue_number}"
            await self.runner.session_service.create_session(
                app_name="simplegithubagent",
                user_id=user,
                session_id=session_id
            )
            
            # Run agent
            logger.info("Running agent...")
            response_text = ""
            
            async for event in self.runner.run_async(
                user_id=user,
                session_id=session_id,
                new_message=types.Content(role="user", parts=[types.Part(text=prompt)])
            ):
                if event.is_final_response():
                    response_text = event.content.parts[0].text.strip()
            
            logger.info(f"Agent response: {response_text[:200]}...")
            
            # Post response to GitHub using App auth
            self._post_comment(repo_name, issue_number, f"🤖 **SimpleGitHubAgent Response**\n\n{response_text}", installation_id)
            
            logger.info("Request processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            # Try to post error to GitHub
            try:
                error_msg = f"❌ Error processing request: {str(e)}"
                self._post_comment(
                    request_data["repository"],
                    request_data["issue_number"],
                    error_msg,
                    request_data.get("installation_id")
                )
            except:
                pass
    
    def process_request(self, request_data: Dict[str, Any]) -> None:
        """Process an agent request (sync wrapper)."""
        asyncio.run(self.process_request_async(request_data))
    
    def _post_comment(self, repo_name: str, issue_number: int, comment: str, installation_id: int = None) -> None:
        """Post a comment to a GitHub issue using GitHub App auth."""
        try:
            gh = self._get_github_client(installation_id)
            repo = gh.get_repo(repo_name)
            issue = repo.get_issue(issue_number)
            issue.create_comment(comment)
            logger.info(f"Posted comment to issue #{issue_number} as SimpleGitHubAgent[bot]")
        except Exception as e:
            logger.error(f"Failed to post comment: {e}")


def main():
    """Main entry point - subscribe to queue and process messages."""
    logger.info("Starting agent worker (queue mode)")
    
    worker = AgentWorker()
    queue = get_queue()
    
    async def process_message(message: Dict[str, Any]):
        """Process a message from the queue."""
        await worker.process_request_async(message)
    
    async def run():
        try:
            await queue.subscribe(process_message)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            await queue.close()
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
