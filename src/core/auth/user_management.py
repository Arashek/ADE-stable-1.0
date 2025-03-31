from typing import Dict, List, Optional, Set
from datetime import datetime
import bcrypt
import uuid
from dataclasses import dataclass
import logging
from enum import Enum
import json
from cryptography.fernet import Fernet
from .auth_service import User, UserRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccountStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    PENDING = "pending"

@dataclass
class Organization:
    id: str
    name: str
    created_at: datetime
    owner_id: str
    metadata: Dict[str, Any]
    subscription_tier: str
    max_users: int
    features: Set[str]

@dataclass
class Team:
    id: str
    name: str
    organization_id: str
    created_at: datetime
    leader_id: str
    members: Set[str]
    permissions: Set[str]

class UserRepository:
    def __init__(self, encryption_key: str):
        self._encryption_key = encryption_key
        self._fernet = Fernet(encryption_key.encode())
        self._users: Dict[str, User] = {}
        self._organizations: Dict[str, Organization] = {}
        self._teams: Dict[str, Team] = {}
        
    def _encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive user data."""
        return self._fernet.encrypt(data.encode()).decode()
        
    def _decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive user data."""
        return self._fernet.decrypt(encrypted_data.encode()).decode()
        
    def create_user(self, email: str, password: str, role: UserRole,
                   organization_id: str, metadata: Dict[str, Any] = None) -> User:
        """Create a new user with encrypted sensitive data."""
        user_id = str(uuid.uuid4())
        hashed_password = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()
        
        user = User(
            id=user_id,
            email=email,
            role=role,
            organization_id=organization_id,
            is_active=True,
            created_at=datetime.utcnow(),
            last_login=None,
            metadata=metadata or {}
        )
        
        # Store user with encrypted password
        user_dict = user.__dict__.copy()
        user_dict["password"] = self._encrypt_sensitive_data(hashed_password)
        self._users[user_id] = user_dict
        
        return user
        
    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID."""
        user_dict = self._users.get(user_id)
        if not user_dict:
            return None
            
        # Create User object from stored data
        user_data = user_dict.copy()
        user_data.pop("password", None)  # Remove password from returned data
        return User(**user_data)
        
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update user data."""
        user_dict = self._users.get(user_id)
        if not user_dict:
            return None
            
        # Handle password updates
        if "password" in updates:
            hashed_password = bcrypt.hashpw(
                updates["password"].encode(),
                bcrypt.gensalt()
            ).decode()
            updates["password"] = self._encrypt_sensitive_data(hashed_password)
            
        # Update user data
        user_dict.update(updates)
        self._users[user_id] = user_dict
        
        return self.get_user(user_id)
        
    def delete_user(self, user_id: str) -> bool:
        """Soft delete user account."""
        user_dict = self._users.get(user_id)
        if not user_dict:
            return False
            
        user_dict["is_active"] = False
        user_dict["deleted_at"] = datetime.utcnow()
        self._users[user_id] = user_dict
        
        return True
        
    def verify_password(self, user_id: str, password: str) -> bool:
        """Verify user password."""
        user_dict = self._users.get(user_id)
        if not user_dict:
            return False
            
        stored_password = self._decrypt_sensitive_data(user_dict["password"])
        return bcrypt.checkpw(password.encode(), stored_password.encode())

class UserManagementService:
    def __init__(self, encryption_key: str):
        self.repository = UserRepository(encryption_key)
        
    def create_organization(self, name: str, owner_id: str,
                          subscription_tier: str = "basic",
                          max_users: int = 10) -> Organization:
        """Create a new organization."""
        org_id = str(uuid.uuid4())
        organization = Organization(
            id=org_id,
            name=name,
            created_at=datetime.utcnow(),
            owner_id=owner_id,
            metadata={},
            subscription_tier=subscription_tier,
            max_users=max_users,
            features=self._get_tier_features(subscription_tier)
        )
        
        self.repository._organizations[org_id] = organization
        return organization
        
    def create_team(self, name: str, organization_id: str,
                   leader_id: str, permissions: Set[str]) -> Team:
        """Create a new team within an organization."""
        team_id = str(uuid.uuid4())
        team = Team(
            id=team_id,
            name=name,
            organization_id=organization_id,
            created_at=datetime.utcnow(),
            leader_id=leader_id,
            members={leader_id},
            permissions=permissions
        )
        
        self.repository._teams[team_id] = team
        return team
        
    def add_user_to_team(self, team_id: str, user_id: str) -> bool:
        """Add user to team."""
        team = self.repository._teams.get(team_id)
        if not team:
            return False
            
        team.members.add(user_id)
        return True
        
    def remove_user_from_team(self, team_id: str, user_id: str) -> bool:
        """Remove user from team."""
        team = self.repository._teams.get(team_id)
        if not team:
            return False
            
        team.members.discard(user_id)
        return True
        
    def get_team_permissions(self, team_id: str) -> Set[str]:
        """Get team permissions."""
        team = self.repository._teams.get(team_id)
        return team.permissions if team else set()
        
    def update_team_permissions(self, team_id: str,
                              permissions: Set[str]) -> bool:
        """Update team permissions."""
        team = self.repository._teams.get(team_id)
        if not team:
            return False
            
        team.permissions = permissions
        return True
        
    def get_organization_users(self, organization_id: str) -> List[User]:
        """Get all users in an organization."""
        return [
            self.repository.get_user(user_id)
            for user_id, user_dict in self.repository._users.items()
            if user_dict["organization_id"] == organization_id
        ]
        
    def get_team_members(self, team_id: str) -> List[User]:
        """Get all members of a team."""
        team = self.repository._teams.get(team_id)
        if not team:
            return []
            
        return [
            self.repository.get_user(user_id)
            for user_id in team.members
        ]
        
    def suspend_user(self, user_id: str, reason: str) -> bool:
        """Suspend user account."""
        user_dict = self.repository._users.get(user_id)
        if not user_dict:
            return False
            
        user_dict["status"] = AccountStatus.SUSPENDED
        user_dict["suspension_reason"] = reason
        user_dict["suspended_at"] = datetime.utcnow()
        self.repository._users[user_id] = user_dict
        
        return True
        
    def activate_user(self, user_id: str) -> bool:
        """Activate suspended user account."""
        user_dict = self.repository._users.get(user_id)
        if not user_dict:
            return False
            
        user_dict["status"] = AccountStatus.ACTIVE
        user_dict.pop("suspension_reason", None)
        user_dict.pop("suspended_at", None)
        self.repository._users[user_id] = user_dict
        
        return True
        
    def update_user_preferences(self, user_id: str,
                              preferences: Dict[str, Any]) -> bool:
        """Update user preferences."""
        user_dict = self.repository._users.get(user_id)
        if not user_dict:
            return False
            
        user_dict["preferences"] = preferences
        self.repository._users[user_id] = user_dict
        
        return True
        
    def _get_tier_features(self, tier: str) -> Set[str]:
        """Get features available in subscription tier."""
        tier_features = {
            "basic": {
                "max_users": 10,
                "features": {
                    "basic_analytics": True,
                    "email_support": True
                }
            },
            "pro": {
                "max_users": 50,
                "features": {
                    "advanced_analytics": True,
                    "priority_support": True,
                    "custom_domains": True
                }
            },
            "enterprise": {
                "max_users": float("inf"),
                "features": {
                    "advanced_analytics": True,
                    "24_7_support": True,
                    "custom_domains": True,
                    "sso": True,
                    "audit_logs": True
                }
            }
        }
        
        tier_data = tier_features.get(tier, tier_features["basic"])
        return set(tier_data["features"].keys())
        
    def validate_organization_capacity(self, organization_id: str) -> bool:
        """Check if organization has reached user capacity."""
        organization = self.repository._organizations.get(organization_id)
        if not organization:
            return False
            
        current_users = len(self.get_organization_users(organization_id))
        return current_users < organization.max_users 