"""Permission management for GitHub MCP tools."""
from typing import List, Dict
from enum import Enum


class Permission(str, Enum):
    """Available permissions for GitHub operations."""
    READ_FILE = "read_file"
    LIST_FILES = "list_files"
    GET_ISSUE = "get_issue"
    CREATE_BRANCH = "create_branch"
    UPDATE_FILE = "update_file"
    CREATE_PR = "create_pull_request"
    MERGE_PR = "merge_pull_request"
    CREATE_ISSUE = "create_issue"
    ADD_LABEL = "add_label"


class AgentRole(str, Enum):
    """Predefined agent roles."""
    READER = "reader"
    CONTRIBUTOR = "contributor"
    MAINTAINER = "maintainer"
    ADMIN = "admin"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[AgentRole, List[Permission]] = {
    AgentRole.READER: [
        Permission.READ_FILE,
        Permission.LIST_FILES,
        Permission.GET_ISSUE,
    ],
    AgentRole.CONTRIBUTOR: [
        Permission.READ_FILE,
        Permission.LIST_FILES,
        Permission.GET_ISSUE,
        Permission.CREATE_BRANCH,
        Permission.UPDATE_FILE,
        Permission.CREATE_PR,
    ],
    AgentRole.MAINTAINER: [
        Permission.READ_FILE,
        Permission.LIST_FILES,
        Permission.GET_ISSUE,
        Permission.CREATE_BRANCH,
        Permission.UPDATE_FILE,
        Permission.CREATE_PR,
        Permission.MERGE_PR,
        Permission.CREATE_ISSUE,
        Permission.ADD_LABEL,
    ],
    AgentRole.ADMIN: list(Permission),  # All permissions
}


class PermissionManager:
    """Manages agent permissions."""
    
    def __init__(self):
        # Agent ID to role mapping (can be loaded from config/database)
        self.agent_roles: Dict[str, AgentRole] = {
            "SimpleGitHubAgent": AgentRole.CONTRIBUTOR,  # Default agent
        }
    
    def has_permission(self, agent_id: str, permission: Permission) -> bool:
        """Check if an agent has a specific permission."""
        role = self.agent_roles.get(agent_id, AgentRole.READER)
        allowed_permissions = ROLE_PERMISSIONS.get(role, [])
        return permission in allowed_permissions
    
    def check_permission(self, agent_id: str, permission: Permission) -> None:
        """Check permission and raise error if not allowed."""
        if not self.has_permission(agent_id, permission):
            role = self.agent_roles.get(agent_id, AgentRole.READER)
            raise PermissionError(
                f"Agent '{agent_id}' with role '{role}' does not have permission '{permission}'"
            )
    
    def set_agent_role(self, agent_id: str, role: AgentRole) -> None:
        """Set an agent's role."""
        self.agent_roles[agent_id] = role
    
    def get_agent_permissions(self, agent_id: str) -> List[Permission]:
        """Get all permissions for an agent."""
        role = self.agent_roles.get(agent_id, AgentRole.READER)
        return ROLE_PERMISSIONS.get(role, [])
