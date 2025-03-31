from typing import Dict, List, Optional, Set, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
import threading
from pathlib import Path
import yaml
from collections import defaultdict
import re
import hashlib
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationRuleType(Enum):
    """Types of validation rules."""
    REQUIRED = "required"
    FORMAT = "format"
    RANGE = "range"
    ENUM = "enum"
    REGEX = "regex"
    CUSTOM = "custom"

@dataclass
class ValidationRule:
    """Validation rule for permissions."""
    rule_type: ValidationRuleType
    parameters: Dict[str, Any]
    error_message: str
    severity: str  # "error" or "warning"

class PermissionLevel(Enum):
    """Permission levels for technical roles."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    EMERGENCY = "emergency"

class AccessRequestStatus(Enum):
    """Status of access requests."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"

@dataclass
class PermissionTemplate:
    """Template for role-based permissions."""
    name: str
    description: str
    permissions: Dict[str, Set[PermissionLevel]]
    required_approvals: int
    validity_period: int  # in days
    metadata: Dict[str, Any] = None

@dataclass
class AccessRequest:
    """Access request with approval workflow."""
    id: str
    requester_id: str
    template_name: str
    status: AccessRequestStatus
    created_at: datetime
    expires_at: datetime
    approvals: List[Dict[str, Any]]
    reason: str
    metadata: Dict[str, Any] = None

@dataclass
class ElevatedAccess:
    """Temporary elevated access grant."""
    id: str
    user_id: str
    permissions: Dict[str, Set[PermissionLevel]]
    granted_by: str
    granted_at: datetime
    expires_at: datetime
    reason: str
    metadata: Dict[str, Any] = None

@dataclass
class EmergencyAccess:
    """Emergency access protocol."""
    id: str
    user_id: str
    permissions: Dict[str, Set[PermissionLevel]]
    approved_by: List[str]
    activated_at: datetime
    expires_at: datetime
    reason: str
    metadata: Dict[str, Any] = None

@dataclass
class PermissionInheritance:
    """Permission inheritance configuration."""
    parent_template: str
    override_rules: Dict[str, Set[PermissionLevel]]
    metadata: Dict[str, Any] = None

class TeamPermissionError(Exception):
    """Base class for team permission errors."""
    pass

class TeamPermissionManager:
    """Manages team permissions and access controls."""
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self._lock = threading.Lock()
        self._templates: Dict[str, PermissionTemplate] = {}
        self._requests: Dict[str, AccessRequest] = {}
        self._elevated_access: Dict[str, ElevatedAccess] = {}
        self._emergency_access: Dict[str, EmergencyAccess] = {}
        self._user_permissions: Dict[str, Dict[str, Set[PermissionLevel]]] = {}
        self._validation_rules: Dict[str, List[ValidationRule]] = {}
        self._inheritance_rules: Dict[str, PermissionInheritance] = {}
        self._access_tokens: Dict[str, Dict[str, Any]] = {}
        
        self._load_templates()
        self._load_requests()
        self._load_elevated_access()
        self._load_emergency_access()
        self._load_validation_rules()
        self._load_inheritance_rules()
        
    def _load_templates(self) -> None:
        """Load permission templates from file."""
        templates_file = self.config_dir / "permission_templates.yaml"
        if not templates_file.exists():
            return
            
        try:
            with open(templates_file) as f:
                data = yaml.safe_load(f)
                for template_data in data:
                    template = PermissionTemplate(
                        name=template_data["name"],
                        description=template_data.get("description", ""),
                        permissions={
                            component: {PermissionLevel(level) for level in levels}
                            for component, levels in template_data["permissions"].items()
                        },
                        required_approvals=template_data["required_approvals"],
                        validity_period=template_data["validity_period"],
                        metadata=template_data.get("metadata", {})
                    )
                    self._templates[template.name] = template
        except Exception as e:
            logger.error(f"Failed to load permission templates: {str(e)}")
            
    def _save_templates(self) -> None:
        """Save permission templates to file."""
        templates_file = self.config_dir / "permission_templates.yaml"
        with open(templates_file, "w") as f:
            yaml.dump([
                {
                    "name": template.name,
                    "description": template.description,
                    "permissions": {
                        component: [level.value for level in levels]
                        for component, levels in template.permissions.items()
                    },
                    "required_approvals": template.required_approvals,
                    "validity_period": template.validity_period,
                    "metadata": template.metadata
                }
                for template in self._templates.values()
            ], f)
            
    def create_template(self, template_data: Dict[str, Any]) -> PermissionTemplate:
        """Create new permission template."""
        with self._lock:
            template = PermissionTemplate(
                name=template_data["name"],
                description=template_data.get("description", ""),
                permissions={
                    component: {PermissionLevel(level) for level in levels}
                    for component, levels in template_data["permissions"].items()
                },
                required_approvals=template_data["required_approvals"],
                validity_period=template_data["validity_period"],
                metadata=template_data.get("metadata", {})
            )
            
            if template.name in self._templates:
                raise TeamPermissionError(f"Template already exists: {template.name}")
                
            self._templates[template.name] = template
            self._save_templates()
            return template
            
    def request_access(self, requester_id: str, template_name: str, reason: str) -> AccessRequest:
        """Create new access request."""
        with self._lock:
            template = self._templates.get(template_name)
            if not template:
                raise TeamPermissionError(f"Template not found: {template_name}")
                
            request = AccessRequest(
                id=f"req_{len(self._requests) + 1}",
                requester_id=requester_id,
                template_name=template_name,
                status=AccessRequestStatus.PENDING,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7),
                approvals=[],
                reason=reason
            )
            
            self._requests[request.id] = request
            self._save_requests()
            return request
            
    def approve_request(self, request_id: str, approver_id: str, comment: str = "") -> None:
        """Approve access request."""
        with self._lock:
            request = self._requests.get(request_id)
            if not request:
                raise TeamPermissionError(f"Request not found: {request_id}")
                
            if request.status != AccessRequestStatus.PENDING:
                raise TeamPermissionError(f"Request is not pending: {request_id}")
                
            template = self._templates[request.template_name]
            
            # Add approval
            request.approvals.append({
                "approver_id": approver_id,
                "timestamp": datetime.now(),
                "comment": comment
            })
            
            # Check if enough approvals
            if len(request.approvals) >= template.required_approvals:
                request.status = AccessRequestStatus.APPROVED
                # Grant permissions
                self._grant_permissions(
                    request.requester_id,
                    template.permissions,
                    template.validity_period
                )
                
            self._save_requests()
            
    def reject_request(self, request_id: str, approver_id: str, reason: str) -> None:
        """Reject access request."""
        with self._lock:
            request = self._requests.get(request_id)
            if not request:
                raise TeamPermissionError(f"Request not found: {request_id}")
                
            if request.status != AccessRequestStatus.PENDING:
                raise TeamPermissionError(f"Request is not pending: {request_id}")
                
            request.status = AccessRequestStatus.REJECTED
            request.approvals.append({
                "approver_id": approver_id,
                "timestamp": datetime.now(),
                "comment": f"Rejected: {reason}"
            })
            
            self._save_requests()
            
    def request_elevated_access(
        self,
        user_id: str,
        permissions: Dict[str, Set[PermissionLevel]],
        reason: str,
        duration_hours: int = 24
    ) -> ElevatedAccess:
        """Request temporary elevated access."""
        with self._lock:
            access = ElevatedAccess(
                id=f"elev_{len(self._elevated_access) + 1}",
                user_id=user_id,
                permissions=permissions,
                granted_by="system",  # TODO: Get from context
                granted_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=duration_hours),
                reason=reason
            )
            
            self._elevated_access[access.id] = access
            self._save_elevated_access()
            return access
            
    def request_emergency_access(
        self,
        user_id: str,
        permissions: Dict[str, Set[PermissionLevel]],
        reason: str,
        approvers: List[str]
    ) -> EmergencyAccess:
        """Request emergency access."""
        with self._lock:
            access = EmergencyAccess(
                id=f"emerg_{len(self._emergency_access) + 1}",
                user_id=user_id,
                permissions=permissions,
                approved_by=approvers,
                activated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=4),
                reason=reason
            )
            
            self._emergency_access[access.id] = access
            self._save_emergency_access()
            return access
            
    def _grant_permissions(
        self,
        user_id: str,
        permissions: Dict[str, Set[PermissionLevel]],
        validity_days: int
    ) -> None:
        """Grant permissions to user."""
        if user_id not in self._user_permissions:
            self._user_permissions[user_id] = {}
            
        for component, levels in permissions.items():
            if component not in self._user_permissions[user_id]:
                self._user_permissions[user_id][component] = set()
            self._user_permissions[user_id][component].update(levels)
            
    def check_permission(
        self,
        user_id: str,
        component: str,
        required_level: PermissionLevel
    ) -> bool:
        """Check if user has required permission level."""
        # Check base permissions
        if user_id in self._user_permissions:
            user_levels = self._user_permissions[user_id].get(component, set())
            if required_level in user_levels:
                return True
                
        # Check elevated access
        for access in self._elevated_access.values():
            if access.user_id == user_id and access.expires_at > datetime.now():
                if component in access.permissions and required_level in access.permissions[component]:
                    return True
                    
        # Check emergency access
        for access in self._emergency_access.values():
            if access.user_id == user_id and access.expires_at > datetime.now():
                if component in access.permissions and required_level in access.permissions[component]:
                    return True
                    
        return False
        
    def revoke_access(self, user_id: str, component: str) -> None:
        """Revoke user's access to component."""
        with self._lock:
            if user_id in self._user_permissions:
                if component in self._user_permissions[user_id]:
                    del self._user_permissions[user_id][component]
                    
            # Revoke elevated access
            for access_id, access in list(self._elevated_access.items()):
                if access.user_id == user_id:
                    del self._elevated_access[access_id]
                    
            # Revoke emergency access
            for access_id, access in list(self._emergency_access.items()):
                if access.user_id == user_id:
                    del self._emergency_access[access_id]
                    
    def get_user_permissions(self, user_id: str) -> Dict[str, Set[PermissionLevel]]:
        """Get all permissions for user."""
        return self._user_permissions.get(user_id, {}).copy()
        
    def get_pending_requests(self) -> List[AccessRequest]:
        """Get all pending access requests."""
        return [
            request for request in self._requests.values()
            if request.status == AccessRequestStatus.PENDING
        ]
        
    def get_active_elevated_access(self, user_id: str) -> List[ElevatedAccess]:
        """Get active elevated access for user."""
        return [
            access for access in self._elevated_access.values()
            if access.user_id == user_id and access.expires_at > datetime.now()
        ]
        
    def get_active_emergency_access(self, user_id: str) -> List[EmergencyAccess]:
        """Get active emergency access for user."""
        return [
            access for access in self._emergency_access.values()
            if access.user_id == user_id and access.expires_at > datetime.now()
        ]
        
    def _load_requests(self) -> None:
        """Load access requests from file."""
        requests_file = self.config_dir / "access_requests.yaml"
        if not requests_file.exists():
            return
            
        try:
            with open(requests_file) as f:
                data = yaml.safe_load(f)
                for request_data in data:
                    request = AccessRequest(
                        id=request_data["id"],
                        requester_id=request_data["requester_id"],
                        template_name=request_data["template_name"],
                        status=AccessRequestStatus(request_data["status"]),
                        created_at=datetime.fromisoformat(request_data["created_at"]),
                        expires_at=datetime.fromisoformat(request_data["expires_at"]),
                        approvals=request_data["approvals"],
                        reason=request_data["reason"],
                        metadata=request_data.get("metadata", {})
                    )
                    self._requests[request.id] = request
        except Exception as e:
            logger.error(f"Failed to load access requests: {str(e)}")
            
    def _save_requests(self) -> None:
        """Save access requests to file."""
        requests_file = self.config_dir / "access_requests.yaml"
        with open(requests_file, "w") as f:
            yaml.dump([
                {
                    "id": request.id,
                    "requester_id": request.requester_id,
                    "template_name": request.template_name,
                    "status": request.status.value,
                    "created_at": request.created_at.isoformat(),
                    "expires_at": request.expires_at.isoformat(),
                    "approvals": request.approvals,
                    "reason": request.reason,
                    "metadata": request.metadata
                }
                for request in self._requests.values()
            ], f)
            
    def _load_elevated_access(self) -> None:
        """Load elevated access from file."""
        access_file = self.config_dir / "elevated_access.yaml"
        if not access_file.exists():
            return
            
        try:
            with open(access_file) as f:
                data = yaml.safe_load(f)
                for access_data in data:
                    access = ElevatedAccess(
                        id=access_data["id"],
                        user_id=access_data["user_id"],
                        permissions={
                            component: {PermissionLevel(level) for level in levels}
                            for component, levels in access_data["permissions"].items()
                        },
                        granted_by=access_data["granted_by"],
                        granted_at=datetime.fromisoformat(access_data["granted_at"]),
                        expires_at=datetime.fromisoformat(access_data["expires_at"]),
                        reason=access_data["reason"],
                        metadata=access_data.get("metadata", {})
                    )
                    self._elevated_access[access.id] = access
        except Exception as e:
            logger.error(f"Failed to load elevated access: {str(e)}")
            
    def _save_elevated_access(self) -> None:
        """Save elevated access to file."""
        access_file = self.config_dir / "elevated_access.yaml"
        with open(access_file, "w") as f:
            yaml.dump([
                {
                    "id": access.id,
                    "user_id": access.user_id,
                    "permissions": {
                        component: [level.value for level in levels]
                        for component, levels in access.permissions.items()
                    },
                    "granted_by": access.granted_by,
                    "granted_at": access.granted_at.isoformat(),
                    "expires_at": access.expires_at.isoformat(),
                    "reason": access.reason,
                    "metadata": access.metadata
                }
                for access in self._elevated_access.values()
            ], f)
            
    def _load_emergency_access(self) -> None:
        """Load emergency access from file."""
        access_file = self.config_dir / "emergency_access.yaml"
        if not access_file.exists():
            return
            
        try:
            with open(access_file) as f:
                data = yaml.safe_load(f)
                for access_data in data:
                    access = EmergencyAccess(
                        id=access_data["id"],
                        user_id=access_data["user_id"],
                        permissions={
                            component: {PermissionLevel(level) for level in levels}
                            for component, levels in access_data["permissions"].items()
                        },
                        approved_by=access_data["approved_by"],
                        activated_at=datetime.fromisoformat(access_data["activated_at"]),
                        expires_at=datetime.fromisoformat(access_data["expires_at"]),
                        reason=access_data["reason"],
                        metadata=access_data.get("metadata", {})
                    )
                    self._emergency_access[access.id] = access
        except Exception as e:
            logger.error(f"Failed to load emergency access: {str(e)}")
            
    def _save_emergency_access(self) -> None:
        """Save emergency access to file."""
        access_file = self.config_dir / "emergency_access.yaml"
        with open(access_file, "w") as f:
            yaml.dump([
                {
                    "id": access.id,
                    "user_id": access.user_id,
                    "permissions": {
                        component: [level.value for level in levels]
                        for component, levels in access.permissions.items()
                    },
                    "approved_by": access.approved_by,
                    "activated_at": access.activated_at.isoformat(),
                    "expires_at": access.expires_at.isoformat(),
                    "reason": access.reason,
                    "metadata": access.metadata
                }
                for access in self._emergency_access.values()
            ], f)
            
    def add_validation_rule(
        self,
        template_name: str,
        rule: ValidationRule
    ) -> None:
        """Add validation rule to template."""
        with self._lock:
            if template_name not in self._templates:
                raise TeamPermissionError(f"Template not found: {template_name}")
                
            if template_name not in self._validation_rules:
                self._validation_rules[template_name] = []
                
            self._validation_rules[template_name].append(rule)
            self._save_validation_rules()
            
    def validate_template(self, template_name: str) -> List[str]:
        """Validate template against rules."""
        errors = []
        template = self._templates.get(template_name)
        if not template:
            raise TeamPermissionError(f"Template not found: {template_name}")
            
        rules = self._validation_rules.get(template_name, [])
        for rule in rules:
            if rule.rule_type == ValidationRuleType.REQUIRED:
                for field in rule.parameters["fields"]:
                    if not getattr(template, field):
                        errors.append(f"{rule.error_message}: {field} is required")
                        
            elif rule.rule_type == ValidationRuleType.FORMAT:
                for field, pattern in rule.parameters["patterns"].items():
                    value = getattr(template, field)
                    if not re.match(pattern, value):
                        errors.append(f"{rule.error_message}: {field} format invalid")
                        
            elif rule.rule_type == ValidationRuleType.RANGE:
                for field, (min_val, max_val) in rule.parameters["ranges"].items():
                    value = getattr(template, field)
                    if not (min_val <= value <= max_val):
                        errors.append(f"{rule.error_message}: {field} out of range")
                        
            elif rule.rule_type == ValidationRuleType.ENUM:
                for field, allowed_values in rule.parameters["enums"].items():
                    value = getattr(template, field)
                    if value not in allowed_values:
                        errors.append(f"{rule.error_message}: {field} invalid value")
                        
            elif rule.rule_type == ValidationRuleType.REGEX:
                for field, pattern in rule.parameters["patterns"].items():
                    value = getattr(template, field)
                    if not re.match(pattern, value):
                        errors.append(f"{rule.error_message}: {field} invalid format")
                        
            elif rule.rule_type == ValidationRuleType.CUSTOM:
                if not rule.parameters["validator"](template):
                    errors.append(rule.error_message)
                    
        return errors
        
    def set_inheritance(
        self,
        template_name: str,
        parent_template: str,
        override_rules: Dict[str, Set[PermissionLevel]] = None
    ) -> None:
        """Set inheritance relationship between templates."""
        with self._lock:
            if template_name not in self._templates or parent_template not in self._templates:
                raise TeamPermissionError("Template not found")
                
            # Check for circular inheritance
            if self._has_circular_inheritance(template_name, parent_template):
                raise TeamPermissionError("Circular inheritance detected")
                
            inheritance = PermissionInheritance(
                parent_template=parent_template,
                override_rules=override_rules or {},
                metadata={"created_at": datetime.now().isoformat()}
            )
            
            self._inheritance_rules[template_name] = inheritance
            self._save_inheritance_rules()
            
    def _has_circular_inheritance(self, template_name: str, parent_template: str) -> bool:
        """Check for circular inheritance."""
        visited = set()
        
        def check_cycle(current: str) -> bool:
            if current in visited:
                return True
            visited.add(current)
            
            inheritance = self._inheritance_rules.get(current)
            if inheritance:
                return check_cycle(inheritance.parent_template)
            return False
            
        return check_cycle(parent_template)
            
    def get_inherited_permissions(self, template_name: str) -> Dict[str, Set[PermissionLevel]]:
        """Get permissions including inherited ones."""
        permissions = {}
        template = self._templates.get(template_name)
        if not template:
            raise TeamPermissionError(f"Template not found: {template_name}")
            
        # Start with template's own permissions
        permissions.update(template.permissions)
        
        # Add inherited permissions
        inheritance = self._inheritance_rules.get(template_name)
        if inheritance:
            parent_permissions = self.get_inherited_permissions(inheritance.parent_template)
            
            # Apply inheritance with overrides
            for component, levels in parent_permissions.items():
                if component in inheritance.override_rules:
                    permissions[component] = inheritance.override_rules[component]
                elif component not in permissions:
                    permissions[component] = levels
                    
        return permissions
        
    def generate_access_token(
        self,
        user_id: str,
        permissions: Dict[str, Set[PermissionLevel]],
        expires_in: int = 3600  # 1 hour
    ) -> str:
        """Generate secure access token."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        self._access_tokens[token] = {
            "user_id": user_id,
            "permissions": permissions,
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "last_used": datetime.now()
        }
        
        return token
        
    def validate_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate access token and return permissions if valid."""
        token_data = self._access_tokens.get(token)
        if not token_data:
            return None
            
        if token_data["expires_at"] < datetime.now():
            del self._access_tokens[token]
            return None
            
        token_data["last_used"] = datetime.now()
        return token_data["permissions"]
        
    def revoke_access_token(self, token: str) -> None:
        """Revoke access token."""
        if token in self._access_tokens:
            del self._access_tokens[token]
            
    def _load_validation_rules(self) -> None:
        """Load validation rules from file."""
        rules_file = self.config_dir / "validation_rules.yaml"
        if not rules_file.exists():
            return
            
        try:
            with open(rules_file) as f:
                data = yaml.safe_load(f)
                for template_name, rules_data in data.items():
                    rules = []
                    for rule_data in rules_data:
                        rule = ValidationRule(
                            rule_type=ValidationRuleType(rule_data["type"]),
                            parameters=rule_data["parameters"],
                            error_message=rule_data["error_message"],
                            severity=rule_data["severity"]
                        )
                        rules.append(rule)
                    self._validation_rules[template_name] = rules
        except Exception as e:
            logger.error(f"Failed to load validation rules: {str(e)}")
            
    def _save_validation_rules(self) -> None:
        """Save validation rules to file."""
        rules_file = self.config_dir / "validation_rules.yaml"
        with open(rules_file, "w") as f:
            yaml.dump(
                {
                    template_name: [
                        {
                            "type": rule.rule_type.value,
                            "parameters": rule.parameters,
                            "error_message": rule.error_message,
                            "severity": rule.severity
                        }
                        for rule in rules
                    ]
                    for template_name, rules in self._validation_rules.items()
                },
                f
            )
            
    def _load_inheritance_rules(self) -> None:
        """Load inheritance rules from file."""
        rules_file = self.config_dir / "inheritance_rules.yaml"
        if not rules_file.exists():
            return
            
        try:
            with open(rules_file) as f:
                data = yaml.safe_load(f)
                for template_name, rule_data in data.items():
                    inheritance = PermissionInheritance(
                        parent_template=rule_data["parent_template"],
                        override_rules={
                            component: {PermissionLevel(level) for level in levels}
                            for component, levels in rule_data["override_rules"].items()
                        },
                        metadata=rule_data.get("metadata", {})
                    )
                    self._inheritance_rules[template_name] = inheritance
        except Exception as e:
            logger.error(f"Failed to load inheritance rules: {str(e)}")
            
    def _save_inheritance_rules(self) -> None:
        """Save inheritance rules to file."""
        rules_file = self.config_dir / "inheritance_rules.yaml"
        with open(rules_file, "w") as f:
            yaml.dump(
                {
                    template_name: {
                        "parent_template": rule.parent_template,
                        "override_rules": {
                            component: [level.value for level in levels]
                            for component, levels in rule.override_rules.items()
                        },
                        "metadata": rule.metadata
                    }
                    for template_name, rule in self._inheritance_rules.items()
                },
                f
            ) 