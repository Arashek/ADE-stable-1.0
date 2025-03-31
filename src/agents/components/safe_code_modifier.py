from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import difflib

logger = logging.getLogger(__name__)

class SafeCodeModifier:
    """Component for safely modifying code with validation and rollback"""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.modification_history: Dict[str, List[Dict[str, Any]]] = {}
        self.backup_cache: Dict[str, str] = {}
        self.modification_metrics: Dict[str, Dict[str, Any]] = {}
    
    async def modify_code(
        self,
        code: str,
        changes: List[Dict[str, Any]],
        validation_rules: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Safely modify code with validation and rollback support
        
        Args:
            code: Original code to modify
            changes: List of changes to apply
            validation_rules: Optional validation rules
            
        Returns:
            Modified code
        """
        try:
            # Create backup
            backup = await self._create_backup(code)
            
            # Apply changes
            modified_code = await self._apply_changes(code, changes)
            
            # Validate changes
            validation = await self._validate_changes(
                original_code=code,
                modified_code=modified_code,
                changes=changes,
                validation_rules=validation_rules
            )
            
            if not validation["success"]:
                # Rollback on validation failure
                modified_code = await self._rollback(code, backup)
                logger.warning(f"Changes rolled back due to validation failure: {validation['errors']}")
            
            # Record modification
            self._record_modification(code, modified_code, changes, validation)
            
            # Update metrics
            self._update_metrics(changes, validation)
            
            return modified_code
            
        except Exception as e:
            logger.error(f"Code modification failed: {str(e)}")
            # Attempt rollback on exception
            try:
                return await self._rollback(code, backup)
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {str(rollback_error)}")
                raise
    
    async def _create_backup(self, code: str) -> str:
        """Create a backup of the code"""
        backup_key = self._generate_backup_key(code)
        self.backup_cache[backup_key] = code
        return backup_key
    
    async def _apply_changes(
        self,
        code: str,
        changes: List[Dict[str, Any]]
    ) -> str:
        """Apply changes to code"""
        modified_code = code
        
        for change in changes:
            change_type = change.get("type")
            if change_type == "insert":
                modified_code = self._apply_insert(modified_code, change)
            elif change_type == "replace":
                modified_code = self._apply_replace(modified_code, change)
            elif change_type == "delete":
                modified_code = self._apply_delete(modified_code, change)
            elif change_type == "refactor":
                modified_code = self._apply_refactor(modified_code, change)
        
        return modified_code
    
    async def _validate_changes(
        self,
        original_code: str,
        modified_code: str,
        changes: List[Dict[str, Any]],
        validation_rules: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Validate applied changes"""
        validation_result = {
            "success": True,
            "errors": [],
            "warnings": [],
            "timestamp": datetime.now()
        }
        
        # Apply default validation rules
        validation_result.update(await self._apply_default_validation(
            original_code=original_code,
            modified_code=modified_code,
            changes=changes
        ))
        
        # Apply custom validation rules
        if validation_rules:
            validation_result.update(await self._apply_custom_validation(
                original_code=original_code,
                modified_code=modified_code,
                changes=changes,
                validation_rules=validation_rules
            ))
        
        # Update success status
        validation_result["success"] = len(validation_result["errors"]) == 0
        
        return validation_result
    
    async def _rollback(self, code: str, backup_key: str) -> str:
        """Rollback code to backup"""
        if backup_key not in self.backup_cache:
            raise ValueError(f"Backup not found: {backup_key}")
        
        return self.backup_cache[backup_key]
    
    def _record_modification(
        self,
        original_code: str,
        modified_code: str,
        changes: List[Dict[str, Any]],
        validation: Dict[str, Any]
    ) -> None:
        """Record code modification in history"""
        modification_key = self._generate_modification_key(original_code, changes)
        
        if modification_key not in self.modification_history:
            self.modification_history[modification_key] = []
        
        self.modification_history[modification_key].append({
            "original_code": original_code,
            "modified_code": modified_code,
            "changes": changes,
            "validation": validation,
            "diff": self._generate_diff(original_code, modified_code),
            "timestamp": datetime.now()
        })
    
    def _update_metrics(
        self,
        changes: List[Dict[str, Any]],
        validation: Dict[str, Any]
    ) -> None:
        """Update modification metrics"""
        change_type = changes[0]["type"] if changes else "unknown"
        
        if change_type not in self.modification_metrics:
            self.modification_metrics[change_type] = {
                "total_modifications": 0,
                "successful_modifications": 0,
                "failed_modifications": 0,
                "total_changes": 0,
                "avg_validation_time": 0.0
            }
        
        metrics = self.modification_metrics[change_type]
        metrics["total_modifications"] += 1
        metrics["total_changes"] += len(changes)
        
        if validation["success"]:
            metrics["successful_modifications"] += 1
        else:
            metrics["failed_modifications"] += 1
        
        metrics["avg_validation_time"] = (
            (metrics["avg_validation_time"] * (metrics["total_modifications"] - 1) +
             (datetime.now() - validation["timestamp"]).total_seconds()) /
            metrics["total_modifications"]
        )
    
    def _generate_backup_key(self, code: str) -> str:
        """Generate a unique key for code backup"""
        # Implementation would generate a hash of the code
        return "backup_key"
    
    def _generate_modification_key(self, code: str, changes: List[Dict[str, Any]]) -> str:
        """Generate a unique key for code modification"""
        # Implementation would generate a hash of code and changes
        return "modification_key"
    
    def _generate_diff(self, original_code: str, modified_code: str) -> str:
        """Generate a diff between original and modified code"""
        diff = difflib.unified_diff(
            original_code.splitlines(keepends=True),
            modified_code.splitlines(keepends=True),
            fromfile="original",
            tofile="modified"
        )
        return "".join(diff)
    
    def _apply_insert(self, code: str, change: Dict[str, Any]) -> str:
        """Apply insert change to code"""
        # Implementation would insert code at specified position
        return code
    
    def _apply_replace(self, code: str, change: Dict[str, Any]) -> str:
        """Apply replace change to code"""
        # Implementation would replace code at specified position
        return code
    
    def _apply_delete(self, code: str, change: Dict[str, Any]) -> str:
        """Apply delete change to code"""
        # Implementation would delete code at specified position
        return code
    
    def _apply_refactor(self, code: str, change: Dict[str, Any]) -> str:
        """Apply refactor change to code"""
        # Implementation would apply refactoring changes
        return code
    
    async def _apply_default_validation(
        self,
        original_code: str,
        modified_code: str,
        changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply default validation rules"""
        return {
            "success": True,
            "errors": [],
            "warnings": []
        }
    
    async def _apply_custom_validation(
        self,
        original_code: str,
        modified_code: str,
        changes: List[Dict[str, Any]],
        validation_rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply custom validation rules"""
        return {
            "success": True,
            "errors": [],
            "warnings": []
        } 