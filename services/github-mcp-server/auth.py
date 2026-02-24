"""GitHub App authentication management."""
import time
import jwt
from typing import Dict
from github import Github, Auth
import os


class GitHubAppAuth:
    """Manages GitHub App authentication and token generation."""
    
    def __init__(self, app_id: str, private_key: str):
        self.app_id = app_id
        self.private_key = private_key
        self._installation_tokens: Dict[int, tuple[str, float]] = {}
    
    def generate_jwt(self) -> str:
        """Generate a JWT for GitHub App authentication."""
        now = int(time.time())
        payload = {
            'iat': now - 60,  # Issued at time (60 seconds in the past to account for clock drift)
            'exp': now + (10 * 60),  # Expiration time (10 minutes)
            'iss': self.app_id
        }
        
        token = jwt.encode(payload, self.private_key, algorithm='RS256')
        return token
    
    def get_installation_token(self, installation_id: int) -> str:
        """Get an installation access token, using cache if valid."""
        # Check cache
        if installation_id in self._installation_tokens:
            token, expires_at = self._installation_tokens[installation_id]
            # If token expires in more than 5 minutes, use it
            if expires_at - time.time() > 300:
                return token
        
        # Generate new token using PyGithub's App authentication
        from github import GithubIntegration
        
        integration = GithubIntegration(self.app_id, self.private_key)
        auth = integration.get_access_token(installation_id)
        
        # Cache token (expires in 1 hour, cache for 55 minutes)
        expires_at = time.time() + (55 * 60)
        self._installation_tokens[installation_id] = (auth.token, expires_at)
        
        return auth.token
    
    def get_github_client(self, installation_id: int) -> Github:
        """Get an authenticated GitHub client for an installation."""
        token = self.get_installation_token(installation_id)
        return Github(token)
