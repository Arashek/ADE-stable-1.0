import os
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from src.core.error.root_cause_analyzer import RootCause

@dataclass
class Fix:
    """Represents a code fix with safety checks"""
    cause_type: str
    description: str
    confidence: float
    changes: List[Dict[str, Any]]
    safety_checks: List[Dict[str, Any]]
    rollback_plan: Optional[Dict[str, Any]] = None

class FixManager:
    """Manages code fixes with safety checks and rollback capabilities"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("fix_manager")
        self.fixes: Dict[str, List[Fix]] = {}
        self.backup_dir = "fix_backups"
        self._setup_backup_dir()
    
    def _setup_backup_dir(self):
        """Set up directory for fix backups"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def register_fix(self, fix: Fix):
        """Register a new fix"""
        if fix.cause_type not in self.fixes:
            self.fixes[fix.cause_type] = []
        self.fixes[fix.cause_type].append(fix)
    
    def can_fix(self, cause: RootCause) -> bool:
        """Check if a fix is available for the given cause"""
        return cause.cause_type in self.fixes and len(self.fixes[cause.cause_type]) > 0
    
    def get_available_fixes(self, cause: RootCause) -> List[Fix]:
        """Get available fixes for a cause"""
        return self.fixes.get(cause.cause_type, [])
    
    def apply_fix(self, cause: RootCause, file_path: str) -> bool:
        """
        Apply a fix to the given file
        
        Args:
            cause: The root cause to fix
            file_path: Path to the file to fix
            
        Returns:
            True if fix was applied successfully
        """
        if not self.can_fix(cause):
            self.logger.warning(f"No fixes available for cause type: {cause.cause_type}")
            return False
        
        # Get available fixes
        fixes = self.get_available_fixes(cause)
        if not fixes:
            return False
        
        # Sort fixes by confidence
        fixes.sort(key=lambda x: x.confidence, reverse=True)
        
        # Try each fix until one succeeds
        for fix in fixes:
            try:
                # Create backup
                backup_path = self._create_backup(file_path)
                
                # Run safety checks
                if not self._run_safety_checks(fix, file_path):
                    self.logger.warning(f"Safety checks failed for fix: {fix.description}")
                    continue
                
                # Apply changes
                self._apply_changes(fix, file_path)
                
                # Verify changes
                if not self._verify_changes(fix, file_path):
                    self.logger.warning(f"Change verification failed for fix: {fix.description}")
                    self._restore_backup(file_path, backup_path)
                    continue
                
                self.logger.info(f"Successfully applied fix: {fix.description}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to apply fix: {str(e)}")
                if backup_path and os.path.exists(backup_path):
                    self._restore_backup(file_path, backup_path)
                continue
        
        return False
    
    def _create_backup(self, file_path: str) -> str:
        """Create a backup of the file"""
        import shutil
        from datetime import datetime
        
        backup_name = f"{os.path.basename(file_path)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _restore_backup(self, file_path: str, backup_path: str):
        """Restore file from backup"""
        import shutil
        shutil.copy2(backup_path, file_path)
    
    def _run_safety_checks(self, fix: Fix, file_path: str) -> bool:
        """Run safety checks before applying fix"""
        for check in fix.safety_checks:
            try:
                if not self._execute_safety_check(check, file_path):
                    return False
            except Exception as e:
                self.logger.error(f"Safety check failed: {str(e)}")
                return False
        return True
    
    def _execute_safety_check(self, check: Dict[str, Any], file_path: str) -> bool:
        """Execute a single safety check"""
        check_type = check.get("type")
        
        if check_type == "file_exists":
            return os.path.exists(file_path)
        
        elif check_type == "file_permissions":
            return os.access(file_path, os.W_OK)
        
        elif check_type == "syntax_check":
            return self._check_syntax(file_path)
        
        elif check_type == "dependency_check":
            return self._check_dependencies(check.get("dependencies", []))
        
        elif check_type == "custom":
            return self._execute_custom_check(check.get("function"), file_path)
        
        return False
    
    def _check_syntax(self, file_path: str) -> bool:
        """Check Python syntax of the file"""
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            return True
        except SyntaxError:
            return False
    
    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Check if required dependencies are installed"""
        import importlib
        for dep in dependencies:
            try:
                importlib.import_module(dep)
            except ImportError:
                return False
        return True
    
    def _execute_custom_check(self, check_func: callable, file_path: str) -> bool:
        """Execute a custom safety check function"""
        try:
            return check_func(file_path)
        except Exception:
            return False
    
    def _apply_changes(self, fix: Fix, file_path: str):
        """Apply changes to the file"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        for change in fix.changes:
            change_type = change.get("type")
            
            if change_type == "replace":
                content = content.replace(
                    change["old"],
                    change["new"]
                )
            
            elif change_type == "insert":
                content = self._insert_text(
                    content,
                    change["position"],
                    change["text"]
                )
            
            elif change_type == "delete":
                content = self._delete_text(
                    content,
                    change["start"],
                    change["end"]
                )
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    def _insert_text(self, content: str, position: int, text: str) -> str:
        """Insert text at the specified position"""
        return content[:position] + text + content[position:]
    
    def _delete_text(self, content: str, start: int, end: int) -> str:
        """Delete text between start and end positions"""
        return content[:start] + content[end:]
    
    def _verify_changes(self, fix: Fix, file_path: str) -> bool:
        """Verify that changes were applied correctly"""
        # Basic verification: check if file exists and is readable
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check syntax
            if not self._check_syntax(file_path):
                return False
            
            # Run any custom verification
            if fix.rollback_plan and "verification" in fix.rollback_plan:
                return self._execute_custom_check(
                    fix.rollback_plan["verification"],
                    file_path
                )
            
            return True
            
        except Exception:
            return False 