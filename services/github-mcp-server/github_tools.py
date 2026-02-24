"""GitHub API tool implementations."""
from typing import Optional, List, Dict, Any
from github import Github, GithubException
from github.Repository import Repository
from github.ContentFile import ContentFile
import base64
import logging

logger = logging.getLogger(__name__)


class GitHubTools:
    """GitHub API operations."""
    
    def __init__(self, github_client: Github):
        self.gh = github_client
    
    def _get_repo(self, repo_full_name: str) -> Repository:
        """Get a repository object."""
        try:
            return self.gh.get_repo(repo_full_name)
        except GithubException as e:
            raise ValueError(f"Repository '{repo_full_name}' not found or not accessible: {e}")
    
    def read_file(self, repo: str, path: str, ref: str = "main") -> str:
        """Read a file from a repository."""
        try:
            repository = self._get_repo(repo)
            content_file = repository.get_contents(path, ref=ref)
            
            if isinstance(content_file, list):
                raise ValueError(f"Path '{path}' is a directory, not a file")
            
            # Decode content
            content = base64.b64decode(content_file.content).decode('utf-8')
            return content
        except GithubException as e:
            raise ValueError(f"Failed to read file '{path}': {e}")
    
    def list_files(self, repo: str, path: str = "", ref: str = "main") -> List[Dict[str, Any]]:
        """List files in a directory."""
        try:
            repository = self._get_repo(repo)
            contents = repository.get_contents(path, ref=ref)
            
            if not isinstance(contents, list):
                contents = [contents]
            
            files = []
            for content in contents:
                files.append({
                    "name": content.name,
                    "path": content.path,
                    "type": content.type,
                    "size": content.size,
                    "sha": content.sha,
                })
            
            return files
        except GithubException as e:
            raise ValueError(f"Failed to list files in '{path}': {e}")
    
    def create_branch(self, repo: str, branch_name: str, from_ref: str = "main") -> str:
        """Create a new branch."""
        try:
            repository = self._get_repo(repo)
            
            # Get the source branch
            source_branch = repository.get_branch(from_ref)
            source_sha = source_branch.commit.sha
            
            # Create new branch
            ref = f"refs/heads/{branch_name}"
            repository.create_git_ref(ref, source_sha)
            
            logger.info(f"Created branch '{branch_name}' from '{from_ref}' in {repo}")
            return f"Successfully created branch '{branch_name}'"
        except GithubException as e:
            if e.status == 422:
                raise ValueError(f"Branch '{branch_name}' already exists")
            raise ValueError(f"Failed to create branch: {e}")
    
    def update_file(
        self,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str,
        sha: Optional[str] = None
    ) -> str:
        """Create or update a file in a repository."""
        try:
            repository = self._get_repo(repo)
            
            # Try to get existing file
            try:
                existing_file = repository.get_contents(path, ref=branch)
                if isinstance(existing_file, list):
                    raise ValueError(f"Path '{path}' is a directory")
                
                # Update existing file
                result = repository.update_file(
                    path=path,
                    message=message,
                    content=content,
                    sha=existing_file.sha,
                    branch=branch
                )
                action = "Updated"
            except GithubException as e:
                if e.status == 404:
                    # Create new file
                    result = repository.create_file(
                        path=path,
                        message=message,
                        content=content,
                        branch=branch
                    )
                    action = "Created"
                else:
                    raise
            
            logger.info(f"{action} file '{path}' in {repo} on branch '{branch}'")
            return f"{action} file '{path}' successfully"
        except GithubException as e:
            raise ValueError(f"Failed to update file '{path}': {e}")
    
    def create_pull_request(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        """Create a pull request."""
        try:
            repository = self._get_repo(repo)
            
            pr = repository.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )
            
            logger.info(f"Created PR #{pr.number} in {repo}")
            return {
                "number": pr.number,
                "url": pr.html_url,
                "title": pr.title,
                "state": pr.state,
            }
        except GithubException as e:
            raise ValueError(f"Failed to create pull request: {e}")
    
    def get_issue(self, repo: str, issue_number: int) -> Dict[str, Any]:
        """Get issue details."""
        try:
            repository = self._get_repo(repo)
            issue = repository.get_issue(issue_number)
            
            return {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "labels": [label.name for label in issue.labels],
                "user": issue.user.login,
                "created_at": issue.created_at.isoformat(),
                "url": issue.html_url,
            }
        except GithubException as e:
            raise ValueError(f"Failed to get issue #{issue_number}: {e}")
