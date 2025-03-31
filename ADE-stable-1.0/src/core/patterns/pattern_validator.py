from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import yaml
from pathlib import Path
import ast
import re
import sys
from radon.complexity import cc_visit
from radon.metrics import mi_visit

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of pattern validation"""
    is_valid: bool
    score: float
    issues: List[str]
    suggestions: List[str]
    timestamp: datetime

class PatternValidator:
    """System for validating and verifying design patterns"""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.validation_history: Dict[str, List[ValidationResult]] = {}
        self.validation_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.load_validation_rules()
        
    def load_validation_rules(self) -> None:
        """Load validation rules from configuration"""
        try:
            rules_path = Path("src/core/patterns/config/validation_rules.yaml")
            if rules_path.exists():
                with open(rules_path, "r") as f:
                    self.validation_rules = yaml.safe_load(f)
            else:
                logger.warning("Validation rules file not found")
                
        except Exception as e:
            logger.error(f"Error loading validation rules: {str(e)}")
            
    async def validate_pattern(
        self,
        pattern_id: str,
        code: str,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate a pattern implementation"""
        try:
            # Parse code
            tree = ast.parse(code)
            
            # Apply validation rules
            issues = []
            suggestions = []
            total_score = 0.0
            rule_count = 0
            
            # Apply general rules first
            for rule in self.validation_rules.get("general", []):
                rule_result = await self._apply_validation_rule(
                    rule,
                    tree,
                    code,
                    context
                )
                
                if not rule_result["is_valid"]:
                    issues.extend(rule_result["issues"])
                suggestions.extend(rule_result["suggestions"])
                total_score += rule_result["score"]
                rule_count += 1
                
            # Apply pattern-specific rules
            pattern_rules = self.validation_rules.get(pattern_id, [])
            for rule in pattern_rules:
                rule_result = await self._apply_validation_rule(
                    rule,
                    tree,
                    code,
                    context
                )
                
                if not rule_result["is_valid"]:
                    issues.extend(rule_result["issues"])
                suggestions.extend(rule_result["suggestions"])
                total_score += rule_result["score"]
                rule_count += 1
                
            # Calculate final score
            final_score = total_score / rule_count if rule_count > 0 else 0.0
            
            # Create validation result
            result = ValidationResult(
                is_valid=len(issues) == 0,
                score=final_score,
                issues=issues,
                suggestions=suggestions,
                timestamp=datetime.now()
            )
            
            # Update validation history
            if pattern_id not in self.validation_history:
                self.validation_history[pattern_id] = []
            self.validation_history[pattern_id].append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating pattern: {str(e)}")
            return ValidationResult(
                is_valid=False,
                score=0.0,
                issues=[str(e)],
                suggestions=[],
                timestamp=datetime.now()
            )
            
    async def _apply_validation_rule(
        self,
        rule: Dict[str, Any],
        tree: ast.AST,
        code: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply a single validation rule"""
        try:
            rule_type = rule.get("type")
            rule_params = rule.get("parameters", {})
            
            if rule_type == "syntax":
                return await self._validate_syntax(rule_params, code)
            elif rule_type == "structure":
                return await self._validate_structure(rule_params, tree)
            elif rule_type == "semantics":
                return await self._validate_semantics(rule_params, tree, context)
            elif rule_type == "performance":
                return await self._validate_performance(rule_params, code)
            elif rule_type == "security":
                return await self._validate_security(rule_params, code)
            else:
                return {
                    "is_valid": True,
                    "score": 1.0,
                    "issues": [],
                    "suggestions": []
                }
                
        except Exception as e:
            logger.error(f"Error applying validation rule: {str(e)}")
            return {
                "is_valid": False,
                "score": 0.0,
                "issues": [str(e)],
                "suggestions": []
            }
            
    async def _validate_syntax(
        self,
        params: Dict[str, Any],
        code: str
    ) -> Dict[str, Any]:
        """Validate code syntax"""
        try:
            issues = []
            suggestions = []
            score = 1.0
            
            # Check Python version
            required_version = params.get("python_version", ">=3.8")
            current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            if not self._version_meets_requirement(current_version, required_version):
                issues.append(f"Python version {current_version} does not meet requirement {required_version}")
                suggestions.append(f"Upgrade Python to version {required_version}")
                score *= 0.8
                
            # Check line length
            max_line_length = params.get("max_line_length", 100)
            for i, line in enumerate(code.splitlines(), 1):
                if len(line) > max_line_length:
                    issues.append(f"Line {i} exceeds maximum length of {max_line_length}")
                    suggestions.append("Split long line into multiple lines")
                    score *= 0.9
                    
            # Check complexity
            max_complexity = params.get("max_complexity", 10)
            complexity_results = cc_visit(code)
            for item in complexity_results:
                if item.complexity > max_complexity:
                    issues.append(f"Function {item.name} has complexity {item.complexity}")
                    suggestions.append("Refactor to reduce complexity")
                    score *= 0.8
                    
            return {
                "is_valid": len(issues) == 0,
                "score": score,
                "issues": issues,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error validating syntax: {str(e)}")
            return {
                "is_valid": False,
                "score": 0.0,
                "issues": [str(e)],
                "suggestions": []
            }
            
    async def _validate_structure(
        self,
        params: Dict[str, Any],
        tree: ast.AST
    ) -> Dict[str, Any]:
        """Validate code structure"""
        try:
            issues = []
            suggestions = []
            score = 1.0
            
            # Check required components
            required_components = params.get("required_components", [])
            for component in required_components:
                if not self._has_component(tree, component):
                    issues.append(f"Missing required component: {component}")
                    suggestions.append(f"Add {component} component")
                    score *= 0.8
                    
            # Check component relationships
            relationships = params.get("relationships", [])
            for relationship in relationships:
                if not self._has_relationship(tree, relationship):
                    issues.append(f"Missing required relationship: {relationship}")
                    suggestions.append(f"Add {relationship} relationship")
                    score *= 0.8
                    
            return {
                "is_valid": len(issues) == 0,
                "score": score,
                "issues": issues,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error validating structure: {str(e)}")
            return {
                "is_valid": False,
                "score": 0.0,
                "issues": [str(e)],
                "suggestions": []
            }
            
    async def _validate_semantics(
        self,
        params: Dict[str, Any],
        tree: ast.AST,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate code semantics"""
        try:
            # Use LLM to validate semantics
            prompt = f"""
            Analyze the following code for semantic correctness:
            
            {ast.unparse(tree)}
            
            Context:
            {json.dumps(context, indent=2)}
            
            Check for:
            1. Logical correctness
            2. Design pattern adherence
            3. Best practices
            4. Potential issues
            """
            
            response = await self.llm_manager.generate(
                prompt=prompt,
                task_type="semantic_validation"
            )
            
            # Parse LLM response
            issues = self._extract_issues(response)
            suggestions = self._extract_suggestions(response)
            
            # Calculate score
            score = 1.0 - (len(issues) * 0.2)
            score = max(0.0, min(1.0, score))
            
            return {
                "is_valid": len(issues) == 0,
                "score": score,
                "issues": issues,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error validating semantics: {str(e)}")
            return {
                "is_valid": False,
                "score": 0.0,
                "issues": [str(e)],
                "suggestions": []
            }
            
    async def _validate_performance(
        self,
        params: Dict[str, Any],
        code: str
    ) -> Dict[str, Any]:
        """Validate code performance"""
        try:
            issues = []
            suggestions = []
            score = 1.0
            
            # Check for performance anti-patterns
            anti_patterns = params.get("anti_patterns", [])
            for pattern in anti_patterns:
                if re.search(pattern["regex"], code):
                    issues.append(pattern["description"])
                    suggestions.append(pattern["suggestion"])
                    score *= 0.8
                    
            return {
                "is_valid": len(issues) == 0,
                "score": score,
                "issues": issues,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error validating performance: {str(e)}")
            return {
                "is_valid": False,
                "score": 0.0,
                "issues": [str(e)],
                "suggestions": []
            }
            
    async def _validate_security(
        self,
        params: Dict[str, Any],
        code: str
    ) -> Dict[str, Any]:
        """Validate code security"""
        try:
            issues = []
            suggestions = []
            score = 1.0
            
            # Check for security vulnerabilities
            vulnerabilities = params.get("vulnerabilities", [])
            for vulnerability in vulnerabilities:
                if re.search(vulnerability["regex"], code):
                    issues.append(vulnerability["description"])
                    suggestions.append(vulnerability["suggestion"])
                    score *= 0.8
                    
            return {
                "is_valid": len(issues) == 0,
                "score": score,
                "issues": issues,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error validating security: {str(e)}")
            return {
                "is_valid": False,
                "score": 0.0,
                "issues": [str(e)],
                "suggestions": []
            }
            
    def _has_component(self, tree: ast.AST, component: str) -> bool:
        """Check if code has a specific component"""
        try:
            if component == "private_constructor":
                return self._has_private_constructor(tree)
            elif component == "instance_variable":
                return self._has_instance_variable(tree)
            elif component == "get_instance_method":
                return self._has_get_instance_method(tree)
            elif component == "try_block":
                return self._has_try_block(tree)
            elif component == "except_block":
                return self._has_except_block(tree)
            elif component == "finally_block":
                return self._has_finally_block(tree)
            elif component == "resource_acquisition":
                return self._has_resource_acquisition(tree)
            elif component == "resource_release":
                return self._has_resource_release(tree)
            elif component == "cache_storage":
                return self._has_cache_storage(tree)
            elif component == "cache_lookup":
                return self._has_cache_lookup(tree)
            elif component == "cache_update":
                return self._has_cache_update(tree)
            elif component == "batch_collection":
                return self._has_batch_collection(tree)
            elif component == "batch_processing":
                return self._has_batch_processing(tree)
            elif component == "result_aggregation":
                return self._has_result_aggregation(tree)
            elif component == "credential_validation":
                return self._has_credential_validation(tree)
            elif component == "session_management":
                return self._has_session_management(tree)
            elif component == "access_control":
                return self._has_access_control(tree)
            elif component == "key_management":
                return self._has_key_management(tree)
            elif component == "encryption_operation":
                return self._has_encryption_operation(tree)
            elif component == "decryption_operation":
                return self._has_decryption_operation(tree)
            elif component == "model":
                return self._has_model(tree)
            elif component == "view":
                return self._has_view(tree)
            elif component == "controller":
                return self._has_controller(tree)
            elif component == "data_source":
                return self._has_data_source(tree)
            elif component == "repository_interface":
                return self._has_repository_interface(tree)
            elif component == "repository_implementation":
                return self._has_repository_implementation(tree)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking component: {str(e)}")
            return False
            
    def _has_relationship(self, tree: ast.AST, relationship: str) -> bool:
        """Check if code has a specific relationship"""
        try:
            if relationship == "constructor_private":
                return self._has_private_constructor(tree)
            elif relationship == "instance_lazy_initialization":
                return self._has_lazy_initialization(tree)
            elif relationship == "product_inheritance":
                return self._has_product_inheritance(tree)
            elif relationship == "creator_dependency":
                return self._has_creator_dependency(tree)
            elif relationship == "subject_observer_registration":
                return self._has_subject_observer_registration(tree)
            elif relationship == "observer_notification":
                return self._has_observer_notification(tree)
            elif relationship == "exception_hierarchy":
                return self._has_exception_hierarchy(tree)
            elif relationship == "resource_cleanup":
                return self._has_resource_cleanup(tree)
            elif relationship == "context_manager":
                return self._has_context_manager(tree)
            elif relationship == "cleanup_guarantee":
                return self._has_cleanup_guarantee(tree)
            elif relationship == "cache_invalidation":
                return self._has_cache_invalidation(tree)
            elif relationship == "cache_eviction":
                return self._has_cache_eviction(tree)
            elif relationship == "batch_size_control":
                return self._has_batch_size_control(tree)
            elif relationship == "processing_efficiency":
                return self._has_processing_efficiency(tree)
            elif relationship == "secure_storage":
                return self._has_secure_storage(tree)
            elif relationship == "token_validation":
                return self._has_token_validation(tree)
            elif relationship == "model_view_separation":
                return self._has_model_view_separation(tree)
            elif relationship == "controller_mediation":
                return self._has_controller_mediation(tree)
            elif relationship == "data_abstraction":
                return self._has_data_abstraction(tree)
            elif relationship == "query_encapsulation":
                return self._has_query_encapsulation(tree)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking relationship: {str(e)}")
            return False
            
    def _version_meets_requirement(self, current: str, required: str) -> bool:
        """Check if current version meets requirement"""
        try:
            current_parts = list(map(int, current.split(".")))
            required_parts = required.replace(">=", "").split(".")
            required_parts = list(map(int, required_parts))
            
            for i in range(min(len(current_parts), len(required_parts))):
                if current_parts[i] > required_parts[i]:
                    return True
                elif current_parts[i] < required_parts[i]:
                    return False
                    
            return len(current_parts) >= len(required_parts)
            
        except Exception as e:
            logger.error(f"Error checking version requirement: {str(e)}")
            return False
            
    def _extract_issues(self, response: str) -> List[str]:
        """Extract issues from LLM response"""
        try:
            # TODO: Implement issue extraction from LLM response
            return []
            
        except Exception as e:
            logger.error(f"Error extracting issues: {str(e)}")
            return []
            
    def _extract_suggestions(self, response: str) -> List[str]:
        """Extract suggestions from LLM response"""
        try:
            # TODO: Implement suggestion extraction from LLM response
            return []
            
        except Exception as e:
            logger.error(f"Error extracting suggestions: {str(e)}")
            return []
            
    def get_validation_history(self, pattern_id: str) -> List[ValidationResult]:
        """Get validation history for a pattern"""
        return self.validation_history.get(pattern_id, [])
        
    # Component checking methods
    def _has_private_constructor(self, tree: ast.AST) -> bool:
        """Check for private constructor"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for __init__ method
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                            # Check if constructor is private (starts with underscore)
                            if not item.name.startswith("_"):
                                return False
                            # Check if constructor is properly defined
                            if not item.args.args or not item.args.args[0].arg == "self":
                                return False
                            return True
            return False
        except Exception as e:
            logger.error(f"Error checking private constructor: {str(e)}")
            return False

    def _has_instance_variable(self, tree: ast.AST) -> bool:
        """Check for instance variable"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Look for class variables
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    # Check if variable is properly named (e.g., _instance)
                                    if not target.id.startswith("_"):
                                        return False
                                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking instance variable: {str(e)}")
            return False

    def _has_get_instance_method(self, tree: ast.AST) -> bool:
        """Check for get_instance method"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Look for get_instance method
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name == "get_instance":
                                # Check if method is static or class method
                                if not any(isinstance(decorator, ast.Name) and 
                                         decorator.id in ["staticmethod", "classmethod"] 
                                         for decorator in item.decorator_list):
                                    return False
                                # Check if method returns instance
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Return):
                                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking get_instance method: {str(e)}")
            return False

    def _has_try_block(self, tree: ast.AST) -> bool:
        """Check for try block"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking try block: {str(e)}")
            return False
        
    def _has_except_block(self, tree: ast.AST) -> bool:
        """Check for except block"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    for handler in node.handlers:
                        if isinstance(handler, ast.ExceptHandler):
                            return True
            return False
        except Exception as e:
            logger.error(f"Error checking except block: {str(e)}")
            return False
        
    def _has_finally_block(self, tree: ast.AST) -> bool:
        """Check for finally block"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    if node.finalbody:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking finally block: {str(e)}")
            return False
        
    def _has_resource_acquisition(self, tree: ast.AST) -> bool:
        """Check for resource acquisition"""
        # TODO: Implement resource acquisition check
        return True
        
    def _has_resource_release(self, tree: ast.AST) -> bool:
        """Check for resource release"""
        # TODO: Implement resource release check
        return True
        
    def _has_cache_storage(self, tree: ast.AST) -> bool:
        """Check for cache storage"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for cache storage
                    has_cache_dict = False
                    has_cache_methods = False
                    
                    for item in node.body:
                        # Check for cache dictionary
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if target.id.endswith("_cache"):
                                        has_cache_dict = True
                        
                        # Check for cache methods
                        elif isinstance(item, ast.FunctionDef):
                            if item.name.startswith("cache_"):
                                has_cache_methods = True
                    
                    if has_cache_dict and has_cache_methods:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking cache storage: {str(e)}")
            return False
        
    def _has_cache_lookup(self, tree: ast.AST) -> bool:
        """Check for cache lookup"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for cache lookup methods
                    has_lookup_method = False
                    has_key_validation = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith("get_") or item.name.startswith("lookup_"):
                                has_lookup_method = True
                                # Check for key validation
                                for child in ast.walk(item):
                                    if isinstance(child, ast.If):
                                        for subchild in ast.walk(child):
                                            if isinstance(subchild, ast.Compare):
                                                has_key_validation = True
                    
                    if has_lookup_method and has_key_validation:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking cache lookup: {str(e)}")
            return False
        
    def _has_cache_update(self, tree: ast.AST) -> bool:
        """Check for cache update"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for cache update methods
                    has_update_method = False
                    has_invalidation = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith("update_") or item.name.startswith("set_"):
                                has_update_method = True
                                # Check for cache invalidation
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Call):
                                        if isinstance(child.func, ast.Attribute):
                                            if child.func.attr == "invalidate":
                                                has_invalidation = True
                    
                    if has_update_method and has_invalidation:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking cache update: {str(e)}")
            return False
        
    def _has_batch_collection(self, tree: ast.AST) -> bool:
        """Check for batch collection"""
        # TODO: Implement batch collection check
        return True
        
    def _has_batch_processing(self, tree: ast.AST) -> bool:
        """Check for batch processing"""
        # TODO: Implement batch processing check
        return True
        
    def _has_result_aggregation(self, tree: ast.AST) -> bool:
        """Check for result aggregation"""
        # TODO: Implement result aggregation check
        return True
        
    def _has_credential_validation(self, tree: ast.AST) -> bool:
        """Check for credential validation"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for credential validation methods
                    has_validation_method = False
                    has_secure_storage = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith("validate_"):
                                has_validation_method = True
                                # Check for secure storage
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Call):
                                        if isinstance(child.func, ast.Attribute):
                                            if child.func.attr in ["hash", "encrypt", "verify"]:
                                                has_secure_storage = True
                    
                    if has_validation_method and has_secure_storage:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking credential validation: {str(e)}")
            return False
        
    def _has_session_management(self, tree: ast.AST) -> bool:
        """Check for session management"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for session management methods
                    has_session_methods = False
                    has_timeout = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith("session_"):
                                has_session_methods = True
                                # Check for timeout handling
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Call):
                                        if isinstance(child.func, ast.Attribute):
                                            if child.func.attr in ["expire", "timeout", "invalidate"]:
                                                has_timeout = True
                    
                    if has_session_methods and has_timeout:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking session management: {str(e)}")
            return False
        
    def _has_access_control(self, tree: ast.AST) -> bool:
        """Check for access control"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for access control methods
                    has_auth_methods = False
                    has_permission_check = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith("check_"):
                                has_auth_methods = True
                                # Check for permission validation
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Call):
                                        if isinstance(child.func, ast.Attribute):
                                            if child.func.attr in ["has_permission", "is_authorized", "can_access"]:
                                                has_permission_check = True
                    
                    if has_auth_methods and has_permission_check:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking access control: {str(e)}")
            return False
        
    def _has_key_management(self, tree: ast.AST) -> bool:
        """Check for key management"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for key management methods
                    has_key_methods = False
                    has_secure_storage = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith("key_"):
                                has_key_methods = True
                                # Check for secure storage
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Call):
                                        if isinstance(child.func, ast.Attribute):
                                            if child.func.attr in ["encrypt", "decrypt", "store"]:
                                                has_secure_storage = True
                    
                    if has_key_methods and has_secure_storage:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking key management: {str(e)}")
            return False
        
    def _has_encryption_operation(self, tree: ast.AST) -> bool:
        """Check for encryption operation"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for encryption methods
                    has_encryption_method = False
                    has_algorithm = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith("encrypt_"):
                                has_encryption_method = True
                                # Check for algorithm specification
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Call):
                                        if isinstance(child.func, ast.Attribute):
                                            if child.func.attr in ["encrypt", "cipher"]:
                                                has_algorithm = True
                    
                    if has_encryption_method and has_algorithm:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking encryption operation: {str(e)}")
            return False
        
    def _has_decryption_operation(self, tree: ast.AST) -> bool:
        """Check for decryption operation"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for decryption methods
                    has_decryption_method = False
                    has_algorithm = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith("decrypt_"):
                                has_decryption_method = True
                                # Check for algorithm specification
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Call):
                                        if isinstance(child.func, ast.Attribute):
                                            if child.func.attr in ["decrypt", "cipher"]:
                                                has_algorithm = True
                    
                    if has_decryption_method and has_algorithm:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking decryption operation: {str(e)}")
            return False
        
    def _has_model(self, tree: ast.AST) -> bool:
        """Check for model component"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for data attributes
                    has_data_attributes = False
                    has_validation_methods = False
                    
                    for item in node.body:
                        # Check for data attributes
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    has_data_attributes = True
                        
                        # Check for validation methods
                        elif isinstance(item, ast.FunctionDef):
                            if item.name.startswith("validate_"):
                                has_validation_methods = True
                    
                    if has_data_attributes and has_validation_methods:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking model component: {str(e)}")
            return False
        
    def _has_view(self, tree: ast.AST) -> bool:
        """Check for view component"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for display/rendering methods
                    has_display_methods = False
                    has_update_methods = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Check for display/rendering methods
                            if item.name in ["render", "display", "show"]:
                                has_display_methods = True
                            # Check for update methods
                            elif item.name.startswith("update_"):
                                has_update_methods = True
                    
                    if has_display_methods and has_update_methods:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking view component: {str(e)}")
            return False
        
    def _has_controller(self, tree: ast.AST) -> bool:
        """Check for controller component"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for model and view dependencies
                    has_model_dependency = False
                    has_view_dependency = False
                    has_action_methods = False
                    
                    for item in node.body:
                        # Check for model and view attributes
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if target.id.endswith("_model"):
                                        has_model_dependency = True
                                    elif target.id.endswith("_view"):
                                        has_view_dependency = True
                        
                        # Check for action methods
                        elif isinstance(item, ast.FunctionDef):
                            if item.name.startswith("handle_") or item.name.startswith("process_"):
                                has_action_methods = True
                    
                    if has_model_dependency and has_view_dependency and has_action_methods:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking controller component: {str(e)}")
            return False
        
    def _has_data_source(self, tree: ast.AST) -> bool:
        """Check for data source"""
        # TODO: Implement data source check
        return True
        
    def _has_repository_interface(self, tree: ast.AST) -> bool:
        """Check for repository interface"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for abstract base class
                    has_abstract_methods = False
                    has_crud_methods = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Check for abstract methods
                            if any(isinstance(decorator, ast.Name) and 
                                 decorator.id == "abstractmethod" 
                                 for decorator in item.decorator_list):
                                has_abstract_methods = True
                                # Check for CRUD operations
                                if item.name in ["create", "read", "update", "delete"]:
                                    has_crud_methods = True
                    
                    if has_abstract_methods and has_crud_methods:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking repository interface: {str(e)}")
            return False
        
    def _has_repository_implementation(self, tree: ast.AST) -> bool:
        """Check for repository implementation"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for concrete implementation
                    has_data_source = False
                    has_crud_implementation = False
                    
                    for item in node.body:
                        # Check for data source
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if target.id.endswith("_db") or target.id.endswith("_connection"):
                                        has_data_source = True
                        
                        # Check for CRUD implementation
                        elif isinstance(item, ast.FunctionDef):
                            if item.name in ["create", "read", "update", "delete"]:
                                has_crud_implementation = True
                    
                    if has_data_source and has_crud_implementation:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking repository implementation: {str(e)}")
            return False
        
    def _has_data_abstraction(self, tree: ast.AST) -> bool:
        """Check for data abstraction"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for data access abstraction
                    has_abstraction_methods = False
                    has_data_encapsulation = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Check for data access methods
                            if item.name.startswith("get_") or item.name.startswith("set_"):
                                has_abstraction_methods = True
                                # Check for data encapsulation
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Assign):
                                        for target in child.targets:
                                            if isinstance(target, ast.Name):
                                                if target.id.startswith("_"):
                                                    has_data_encapsulation = True
                    
                    if has_abstraction_methods and has_data_encapsulation:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking data abstraction: {str(e)}")
            return False
        
    def _has_query_encapsulation(self, tree: ast.AST) -> bool:
        """Check for query encapsulation"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for query methods
                    has_query_methods = False
                    has_query_builder = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Check for query methods
                            if item.name.startswith("query_") or item.name.startswith("find_"):
                                has_query_methods = True
                                # Check for query builder pattern
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Call):
                                        if isinstance(child.func, ast.Attribute):
                                            if child.func.attr in ["filter", "where", "order_by"]:
                                                has_query_builder = True
                    
                    if has_query_methods and has_query_builder:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking query encapsulation: {str(e)}")
            return False
        
    def _has_lazy_initialization(self, tree: ast.AST) -> bool:
        """Check for lazy initialization"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Look for get_instance method
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "get_instance":
                            # Check for instance variable initialization
                            instance_var = None
                            for child in ast.walk(item):
                                if isinstance(child, ast.Assign):
                                    for target in child.targets:
                                        if isinstance(target, ast.Name) and target.id.startswith("_"):
                                            instance_var = target.id
                                            # Check if initialization is conditional
                                            if isinstance(child.value, ast.If):
                                                return True
                            # Check if instance is initialized only when needed
                            if instance_var:
                                for child in ast.walk(item):
                                    if isinstance(child, ast.If):
                                        for subchild in ast.walk(child):
                                            if isinstance(subchild, ast.Assign):
                                                for target in subchild.targets:
                                                    if isinstance(target, ast.Name) and target.id == instance_var:
                                                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking lazy initialization: {str(e)}")
            return False

    def _has_product_inheritance(self, tree: ast.AST) -> bool:
        """Check for product inheritance"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for abstract base class
                    has_abstract_methods = False
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if any(isinstance(decorator, ast.Name) and 
                                 decorator.id == "abstractmethod" 
                                 for decorator in item.decorator_list):
                                has_abstract_methods = True
                                break
                    
                    if has_abstract_methods:
                        # Check for concrete implementations
                        for child in ast.walk(tree):
                            if isinstance(child, ast.ClassDef):
                                for base in child.bases:
                                    if isinstance(base, ast.Name) and base.id == node.name:
                                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking product inheritance: {str(e)}")
            return False

    def _has_creator_dependency(self, tree: ast.AST) -> bool:
        """Check for creator dependency"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Look for factory method
                    has_factory_method = False
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if any(isinstance(decorator, ast.Name) and 
                                 decorator.id == "abstractmethod" 
                                 for decorator in item.decorator_list):
                                has_factory_method = True
                                break
                    
                    if has_factory_method:
                        # Check for concrete creator implementations
                        for child in ast.walk(tree):
                            if isinstance(child, ast.ClassDef):
                                for base in child.bases:
                                    if isinstance(base, ast.Name) and base.id == node.name:
                                        # Check if concrete creator implements factory method
                                        for concrete_item in child.body:
                                            if isinstance(concrete_item, ast.FunctionDef):
                                                if concrete_item.name == item.name:
                                                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking creator dependency: {str(e)}")
            return False

    def _has_subject_observer_registration(self, tree: ast.AST) -> bool:
        """Check for subject-observer registration"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Look for observer list and registration methods
                    has_observer_list = False
                    has_attach_method = False
                    has_detach_method = False
                    
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name) and target.id == "_observers":
                                    has_observer_list = True
                        elif isinstance(item, ast.FunctionDef):
                            if item.name == "attach":
                                has_attach_method = True
                            elif item.name == "detach":
                                has_detach_method = True
                    
                    if has_observer_list and has_attach_method and has_detach_method:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking subject-observer registration: {str(e)}")
            return False

    def _has_observer_notification(self, tree: ast.AST) -> bool:
        """Check for observer notification"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Look for notify method
                    has_notify_method = False
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "notify":
                            # Check if method iterates over observers
                            for child in ast.walk(item):
                                if isinstance(child, ast.For):
                                    if isinstance(child.target, ast.Name) and child.target.id == "observer":
                                        # Check if observer.update is called
                                        for subchild in ast.walk(child):
                                            if isinstance(subchild, ast.Call):
                                                if isinstance(subchild.func, ast.Attribute):
                                                    if subchild.func.attr == "update":
                                                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking observer notification: {str(e)}")
            return False

    def _has_exception_hierarchy(self, tree: ast.AST) -> bool:
        """Check for exception hierarchy"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for custom exception classes
                    if any(isinstance(base, ast.Name) and 
                          base.id in ["Exception", "BaseException"] 
                          for base in node.bases):
                        # Check for proper exception attributes
                        has_message = False
                        has_code = False
                        
                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        if target.id == "message":
                                            has_message = True
                                        elif target.id == "code":
                                            has_code = True
                        
                        if has_message and has_code:
                            return True
            return False
        except Exception as e:
            logger.error(f"Error checking exception hierarchy: {str(e)}")
            return False
        
    def _has_resource_cleanup(self, tree: ast.AST) -> bool:
        """Check for resource cleanup"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for cleanup method
                    has_cleanup = False
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name in ["cleanup", "close", "dispose"]:
                                # Check if method properly releases resources
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Assign):
                                        for target in child.targets:
                                            if isinstance(target, ast.Name):
                                                if target.id.endswith("_handle") or target.id.endswith("_resource"):
                                                    return True
                    # Check for context manager implementation
                    if self._has_context_manager(node):
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking resource cleanup: {str(e)}")
            return False

    def _has_context_manager(self, tree: ast.AST) -> bool:
        """Check for context manager"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for __enter__ and __exit__ methods
                    has_enter = False
                    has_exit = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name == "__enter__":
                                has_enter = True
                            elif item.name == "__exit__":
                                has_exit = True
                    
                    if has_enter and has_exit:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking context manager: {str(e)}")
            return False

    def _has_cleanup_guarantee(self, tree: ast.AST) -> bool:
        """Check for cleanup guarantee"""
        # TODO: Implement cleanup guarantee check
        return True
        
    def _has_cache_invalidation(self, tree: ast.AST) -> bool:
        """Check for cache invalidation"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for cache invalidation methods
                    has_invalidation_method = False
                    has_cleanup = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith("invalidate_"):
                                has_invalidation_method = True
                                # Check for cleanup
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Call):
                                        if isinstance(child.func, ast.Attribute):
                                            if child.func.attr in ["clear", "pop", "remove"]:
                                                has_cleanup = True
                    
                    if has_invalidation_method and has_cleanup:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking cache invalidation: {str(e)}")
            return False
        
    def _has_cache_eviction(self, tree: ast.AST) -> bool:
        """Check for cache eviction"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for cache eviction methods
                    has_eviction_method = False
                    has_size_check = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith("evict_"):
                                has_eviction_method = True
                                # Check for size check
                                for child in ast.walk(item):
                                    if isinstance(child, ast.If):
                                        for subchild in ast.walk(child):
                                            if isinstance(subchild, ast.Compare):
                                                if isinstance(subchild.left, ast.Attribute):
                                                    if subchild.left.attr == "size":
                                                        has_size_check = True
                    
                    if has_eviction_method and has_size_check:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking cache eviction: {str(e)}")
            return False
        
    def _has_batch_size_control(self, tree: ast.AST) -> bool:
        """Check for batch size control"""
        # TODO: Implement batch size control check
        return True
        
    def _has_processing_efficiency(self, tree: ast.AST) -> bool:
        """Check for processing efficiency"""
        # TODO: Implement processing efficiency check
        return True
        
    def _has_secure_storage(self, tree: ast.AST) -> bool:
        """Check for secure storage"""
        # TODO: Implement secure storage check
        return True
        
    def _has_token_validation(self, tree: ast.AST) -> bool:
        """Check for token validation"""
        # TODO: Implement token validation check
        return True
        
    def _has_model_view_separation(self, tree: ast.AST) -> bool:
        """Check for model-view separation"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for direct model-view communication
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            for child in ast.walk(item):
                                if isinstance(child, ast.Call):
                                    if isinstance(child.func, ast.Attribute):
                                        # Check if view directly modifies model
                                        if child.func.attr.startswith("set_") or child.func.attr.startswith("update_"):
                                            return False
            return True
        except Exception as e:
            logger.error(f"Error checking model-view separation: {str(e)}")
            return False
        
    def _has_controller_mediation(self, tree: ast.AST) -> bool:
        """Check for controller mediation"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for controller mediating model-view communication
                    has_controller_methods = False
                    has_mediated_calls = False
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith("handle_") or item.name.startswith("process_"):
                                has_controller_methods = True
                                # Check if method mediates model-view communication
                                for child in ast.walk(item):
                                    if isinstance(child, ast.Call):
                                        if isinstance(child.func, ast.Attribute):
                                            if child.func.attr.startswith("set_") or child.func.attr.startswith("update_"):
                                                has_mediated_calls = True
                    
                    if has_controller_methods and has_mediated_calls:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking controller mediation: {str(e)}")
            return False 