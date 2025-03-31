"""Sample Python file for testing code understanding capabilities."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import logging
from pathlib import Path

@dataclass
class User:
    """Represents a user in the system."""
    name: str
    email: str
    age: Optional[int] = None
    preferences: Dict[str, Any] = None

class UserManager:
    """Manages user operations and data."""
    
    def __init__(self, data_file: str):
        """Initialize the user manager.
        
        Args:
            data_file: Path to the JSON file storing user data
        """
        self.data_file = Path(data_file)
        self.users: Dict[str, User] = {}
        self.logger = logging.getLogger(__name__)
        self._load_users()
        
    def _load_users(self) -> None:
        """Load users from the data file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for user_data in data:
                        user = User(**user_data)
                        self.users[user.email] = user
        except Exception as e:
            self.logger.error(f"Error loading users: {e}")
            raise
            
    def add_user(self, user: User) -> bool:
        """Add a new user to the system.
        
        Args:
            user: User object to add
            
        Returns:
            bool: True if user was added successfully
        """
        try:
            if user.email in self.users:
                return False
            self.users[user.email] = user
            self._save_users()
            return True
        except Exception as e:
            self.logger.error(f"Error adding user: {e}")
            return False
            
    def get_user(self, email: str) -> Optional[User]:
        """Get a user by email.
        
        Args:
            email: Email address of the user
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        return self.users.get(email)
        
    def update_user(self, email: str, **kwargs) -> bool:
        """Update user information.
        
        Args:
            email: Email address of the user to update
            **kwargs: Fields to update
            
        Returns:
            bool: True if update was successful
        """
        try:
            if email not in self.users:
                return False
            user = self.users[email]
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self._save_users()
            return True
        except Exception as e:
            self.logger.error(f"Error updating user: {e}")
            return False
            
    def delete_user(self, email: str) -> bool:
        """Delete a user from the system.
        
        Args:
            email: Email address of the user to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            if email not in self.users:
                return False
            del self.users[email]
            self._save_users()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting user: {e}")
            return False
            
    def list_users(self) -> List[User]:
        """Get a list of all users.
        
        Returns:
            List[User]: List of all users
        """
        return list(self.users.values())
        
    def _save_users(self) -> None:
        """Save users to the data file."""
        try:
            data = [
                {
                    'name': user.name,
                    'email': user.email,
                    'age': user.age,
                    'preferences': user.preferences
                }
                for user in self.users.values()
            ]
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving users: {e}")
            raise
            
    def search_users(self, query: str) -> List[User]:
        """Search users by name or email.
        
        Args:
            query: Search query string
            
        Returns:
            List[User]: List of matching users
        """
        query = query.lower()
        return [
            user for user in self.users.values()
            if query in user.name.lower() or query in user.email.lower()
        ]
        
    def get_user_stats(self) -> Dict[str, Any]:
        """Get statistics about users.
        
        Returns:
            Dict[str, Any]: Dictionary containing user statistics
        """
        return {
            'total_users': len(self.users),
            'users_with_age': sum(1 for user in self.users.values() if user.age is not None),
            'users_with_preferences': sum(1 for user in self.users.values() if user.preferences)
        } 