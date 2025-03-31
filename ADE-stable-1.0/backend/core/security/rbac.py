from typing import List, Dict, Optional, Set
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
import jwt
from pydantic import BaseModel

class Permission(BaseModel):
    resource: str
    action: str
    conditions: Optional[Dict] = None

class Role(BaseModel):
    name: str
    permissions: List[Permission]
    description: Optional[str] = None

class RBACManager:
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = {}
        
    def create_role(self, role: Role):
        """Create a new role"""
        self.roles[role.name] = role
        
    def assign_role(self, user_id: str, role_name: str):
        """Assign a role to a user"""
        if role_name not in self.roles:
            raise ValueError(f"Role {role_name} does not exist")
            
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        self.user_roles[user_id].add(role_name)
        
    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has permission to perform action on resource"""
        if user_id not in self.user_roles:
            return False
            
        user_role_names = self.user_roles[user_id]
        for role_name in user_role_names:
            role = self.roles[role_name]
            for permission in role.permissions:
                if permission.resource == resource and permission.action == action:
                    return True
        return False

class AuditLogger:
    def __init__(self, log_file: str = "audit.log"):
        self.log_file = log_file
        
    async def log_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        status: str,
        details: Optional[Dict] = None
    ):
        """Log an audited action"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details or {}
        }
        
        # In production, you might want to use a proper logging system
        # or database for audit logs
        with open(self.log_file, "a") as f:
            f.write(f"{str(log_entry)}\n")

# Initialize managers
rbac_manager = RBACManager()
audit_logger = AuditLogger()

# Define common roles
admin_role = Role(
    name="admin",
    permissions=[
        Permission(resource="*", action="*")
    ],
    description="Full system access"
)

developer_role = Role(
    name="developer",
    permissions=[
        Permission(resource="code", action="read"),
        Permission(resource="code", action="write"),
        Permission(resource="project", action="read"),
        Permission(resource="project", action="write")
    ],
    description="Developer access"
)

viewer_role = Role(
    name="viewer",
    permissions=[
        Permission(resource="*", action="read")
    ],
    description="Read-only access"
)

# Register roles
for role in [admin_role, developer_role, viewer_role]:
    rbac_manager.create_role(role)

def require_permission(resource: str, action: str):
    """Decorator to require specific permissions"""
    def decorator(func):
        async def wrapper(*args, user_id: str = Depends(get_current_user), **kwargs):
            if not rbac_manager.check_permission(user_id, resource, action):
                raise HTTPException(status_code=403, detail="Permission denied")
            
            result = await func(*args, user_id=user_id, **kwargs)
            
            # Log the action
            await audit_logger.log_action(
                user_id=user_id,
                action=action,
                resource=resource,
                status="success"
            )
            
            return result
        return wrapper
    return decorator
