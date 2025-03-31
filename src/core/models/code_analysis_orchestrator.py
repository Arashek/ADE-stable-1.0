from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import logging
from datetime import datetime
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
from .code_quality_analyzer import CodeQualityAnalyzer, CodeQualityResult
from .code_metrics_manager import CodeMetricsManager, CodeMetricsResult, MetricType
from .code_review_manager import CodeReviewManager, ReviewResult, ReviewCategory
from .refactoring_manager import CodeRefactoringManager, RefactoringResult, RefactoringType
from .dependency_analyzer import DependencyAnalyzer, DependencyResult, DependencyType
from .model_validator import ModelValidator, ValidationResult, ValidationType
from .deployment_optimizer import DeploymentOptimizer, OptimizationResult, DeploymentType
from .resource_optimizer import ResourceOptimizer, ResourceResult, ResourceType
from .security_analyzer import SecurityAnalyzer, SecurityResult, SecurityType
from .performance_analyzer import PerformanceAnalyzer, PerformanceResult, PerformanceType
from .architecture_analyzer import ArchitectureAnalyzer, ArchitectureResult, ArchitectureType
from .api_analyzer import APIAnalyzer, APIResult, APIType
from .database_analyzer import DatabaseAnalyzer, DatabaseResult, DatabaseType
from .model_architecture_analyzer import ModelArchitectureAnalyzer, ModelArchitectureResult, ModelArchitectureType
from .test_analyzer import TestAnalyzer, TestResult, TestType
from .documentation_analyzer import DocumentationAnalyzer, DocumentationResult, DocumentationType
from .routing_analyzer import RoutingAnalyzer, RoutingResult, RoutingType
from .accessibility_analyzer import AccessibilityAnalyzer, AccessibilityResult, AccessibilityType
from .internationalization_analyzer import InternationalizationAnalyzer, InternationalizationType

logger = logging.getLogger(__name__)

class AnalysisPriority(Enum):
    """Priority levels for analysis tasks"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AnalysisTask(BaseModel):
    """Analysis task configuration"""
    task_id: str
    priority: AnalysisPriority
    components: List[str]
    metrics: List[MetricType]
    review_categories: List[ReviewCategory]
    refactoring_types: List[RefactoringType]
    dependency_types: List[DependencyType] = []
    validation_types: List[ValidationType] = []
    deployment_types: List[DeploymentType] = []
    resource_types: List[ResourceType] = []
    security_types: List[SecurityType] = []
    performance_types: List[PerformanceType] = []
    architecture_types: List[ArchitectureType] = []
    api_types: List[APIType] = []
    database_types: List[DatabaseType] = []
    model_architecture_types: List[ModelArchitectureType] = []
    test_types: List[TestType] = []
    documentation_types: List[DocumentationType] = []
    routing_types: List[RoutingType] = []
    accessibility_types: List[AccessibilityType] = []
    context: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class UnifiedAnalysisResult(BaseModel):
    """Unified result of code analysis"""
    analysis_type: AnalysisType
    model_architecture_analysis: Optional[ModelArchitectureResult] = None
    test_analysis: Optional[TestResult] = None
    dependency_analysis: Optional[DependencyResult] = None
    documentation_analysis: Optional[DocumentationResult] = None
    routing_analysis: Optional[RoutingResult] = None
    accessibility_analysis: Optional[AccessibilityResult] = None
    internationalization_analysis: Optional[InternationalizationResult] = None
    metadata: Dict[str, Any] = {}

class CacheConfig(BaseModel):
    """Configuration for analysis cache"""
    enabled: bool = True
    max_size: int = 1000  # Maximum number of cached results
    ttl: int = 3600  # Time-to-live in seconds
    storage_path: Optional[str] = None  # Path for persistent cache storage
    compression_enabled: bool = True  # Enable compression for cached results
    compression_level: int = 6  # Compression level (1-9)
    cache_validation: bool = True  # Enable cache validation
    cache_metrics: bool = True  # Enable cache metrics collection
    cache_compression: bool = True  # Enable cache compression
    cache_encryption: bool = False  # Enable cache encryption
    cache_backup: bool = True  # Enable cache backup
    cache_backup_interval: int = 3600  # Backup interval in seconds
    cache_cleanup: bool = True  # Enable cache cleanup
    cache_cleanup_interval: int = 86400  # Cleanup interval in seconds
    cache_distributed: bool = False  # Enable distributed caching
    cache_replication: bool = False  # Enable cache replication
    cache_sharding: bool = False  # Enable cache sharding
    cache_consistency: str = "eventual"  # Cache consistency model
    cache_fallback: bool = True  # Enable cache fallback mechanisms

class CodeAnalysisOrchestrator:
    """Orchestrator for coordinating code analysis components"""
    
    def __init__(self, cache_config: Optional[CacheConfig] = None):
        self.quality_analyzer = CodeQualityAnalyzer()
        self.metrics_manager = CodeMetricsManager()
        self.review_manager = CodeReviewManager()
        self.refactoring_manager = CodeRefactoringManager()
        self.dependency_analyzer = DependencyAnalyzer()
        self.model_validator = ModelValidator()
        self.deployment_optimizer = DeploymentOptimizer()
        self.resource_optimizer = ResourceOptimizer()
        self.security_analyzer = SecurityAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.architecture_analyzer = ArchitectureAnalyzer()
        self.api_analyzer = APIAnalyzer()
        self.database_analyzer = DatabaseAnalyzer()
        self.model_architecture_analyzer = ModelArchitectureAnalyzer()
        self.test_analyzer = TestAnalyzer()
        self.documentation_analyzer = DocumentationAnalyzer()
        self.routing_analyzer = RoutingAnalyzer()
        self.accessibility_analyzer = AccessibilityAnalyzer()
        self.internationalization_analyzer = InternationalizationAnalyzer()
        self.analysis_history: List[UnifiedAnalysisResult] = []
        self.component_metrics: Dict[str, Dict[str, float]] = {}
        self.cache_config = cache_config or CacheConfig()
        self.analysis_cache: Dict[str, UnifiedAnalysisResult] = {}
        self.cache_metrics: Dict[str, Dict[str, Any]] = {}
        self._initialize_cache()
        self.analysis_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.analysis_rules: Dict[str, List[Dict[str, Any]]] = {}
        self._initialize_patterns()
        self._initialize_analysis_rules()
        
    def _initialize_cache(self):
        """Initialize analysis cache"""
        if self.cache_config.storage_path:
            cache_dir = Path(self.cache_config.storage_path)
            cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_persistent_cache()
            if self.cache_config.cache_backup:
                self._schedule_cache_backup()
            if self.cache_config.cache_cleanup:
                self._schedule_cache_cleanup()
            if self.cache_config.cache_distributed:
                self._initialize_distributed_cache()
            if self.cache_config.cache_replication:
                self._initialize_cache_replication()
            if self.cache_config.cache_sharding:
                self._initialize_cache_sharding()
                
    def _initialize_distributed_cache(self):
        """Initialize distributed cache"""
        # Implementation for distributed cache initialization
        pass
        
    def _initialize_cache_replication(self):
        """Initialize cache replication"""
        # Implementation for cache replication initialization
        pass
        
    def _initialize_cache_sharding(self):
        """Initialize cache sharding"""
        # Implementation for cache sharding initialization
        pass
        
    def _schedule_cache_backup(self):
        """Schedule cache backup"""
        # Implementation for scheduling cache backup
        pass
        
    def _schedule_cache_cleanup(self):
        """Schedule cache cleanup"""
        # Implementation for scheduling cache cleanup
        pass
        
    def _load_persistent_cache(self):
        """Load cache from persistent storage"""
        cache_dir = Path(self.cache_config.storage_path)
        for cache_file in cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    cache_data = json.load(f)
                    if self._is_cache_valid(cache_data):
                        if self.cache_config.cache_compression:
                            # Decompress cache data
                            pass
                        if self.cache_config.cache_encryption:
                            # Decrypt cache data
                            pass
                        self.analysis_cache[cache_data["key"]] = UnifiedAnalysisResult(**cache_data["result"])
                        if self.cache_config.cache_metrics:
                            self._update_cache_metrics("load", cache_data["key"], True)
            except Exception as e:
                logger.error(f"Failed to load cache file {cache_file}: {str(e)}")
                if self.cache_config.cache_metrics:
                    self._update_cache_metrics("load", cache_data["key"], False, str(e))
                    
    def _save_persistent_cache(self):
        """Save cache to persistent storage"""
        if not self.cache_config.storage_path:
            return
            
        cache_dir = Path(self.cache_config.storage_path)
        for key, result in self.analysis_cache.items():
            try:
                cache_file = cache_dir / f"{key}.json"
                cache_data = {
                    "key": key,
                    "result": result.dict(),
                    "timestamp": datetime.now().isoformat()
                }
                
                if self.cache_config.cache_encryption:
                    # Encrypt cache data
                    pass
                if self.cache_config.cache_compression:
                    # Compress cache data
                    pass
                    
                with open(cache_file, "w") as f:
                    json.dump(cache_data, f)
                if self.cache_config.cache_metrics:
                    self._update_cache_metrics("save", key, True)
            except Exception as e:
                logger.error(f"Failed to save cache file {cache_file}: {str(e)}")
                if self.cache_config.cache_metrics:
                    self._update_cache_metrics("save", key, False, str(e))
                    
    def _backup_cache(self):
        """Backup cache to a separate location"""
        if not self.cache_config.storage_path:
            return
            
        try:
            backup_dir = Path(self.cache_config.storage_path) / "backup"
            backup_dir.mkdir(exist_ok=True)
            backup_file = backup_dir / f"cache_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_file, "w") as f:
                json.dump(self.analysis_cache, f)
                
            if self.cache_config.cache_metrics:
                self._update_cache_metrics("backup", "cache", True)
        except Exception as e:
            logger.error(f"Failed to backup cache: {str(e)}")
            if self.cache_config.cache_metrics:
                self._update_cache_metrics("backup", "cache", False, str(e))
                
    def _cleanup_cache(self):
        """Clean up old cache entries"""
        try:
            current_time = datetime.now()
            expired_keys = []
            
            for key, result in self.analysis_cache.items():
                analyzed_at = datetime.fromisoformat(result.metadata.get("analyzed_at", ""))
                age = (current_time - analyzed_at).total_seconds()
                if age > self.cache_config.ttl:
                    expired_keys.append(key)
                    
            for key in expired_keys:
                del self.analysis_cache[key]
                if self.cache_config.cache_metrics:
                    self._update_cache_metrics("cleanup", key, True)
                    
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {str(e)}")
            if self.cache_config.cache_metrics:
                self._update_cache_metrics("cleanup", "cache", False, str(e))
                
    def _is_cache_valid(self, cache_data: Dict[str, Any]) -> bool:
        """Check if cache entry is valid"""
        if not cache_data.get("timestamp"):
            return False
            
        cache_time = datetime.fromisoformat(cache_data["timestamp"])
        age = (datetime.now() - cache_time).total_seconds()
        return age < self.cache_config.ttl
        
    def _generate_cache_key(self, code: str, file_path: str, task: AnalysisTask) -> str:
        """Generate cache key for analysis result"""
        # Create a hash of the code and task configuration
        content = f"{code}:{file_path}:{json.dumps(task.dict(), sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()
        
    def _update_cache_metrics(self, operation: str, key: str, success: bool, error: Optional[str] = None):
        """Update cache operation metrics"""
        if operation not in self.cache_metrics:
            self.cache_metrics[operation] = {
                "total": 0,
                "success": 0,
                "failed": 0,
                "errors": []
            }
            
        metrics = self.cache_metrics[operation]
        metrics["total"] += 1
        if success:
            metrics["success"] += 1
        else:
            metrics["failed"] += 1
            if error:
                metrics["errors"].append(error)
                
    async def analyze_code(
        self,
        code: str,
        file_path: str,
        task: AnalysisTask,
        context: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> UnifiedAnalysisResult:
        """Perform unified code analysis"""
        try:
            # Check cache if enabled
            if use_cache and self.cache_config.enabled:
                cache_key = self._generate_cache_key(code, file_path, task)
                if cache_key in self.analysis_cache:
                    cached_result = self.analysis_cache[cache_key]
                    if self._is_cache_valid({"timestamp": cached_result.metadata.get("analyzed_at")}):
                        if self.cache_config.cache_metrics:
                            self._update_cache_metrics("hit", cache_key, True)
                        return cached_result
                    if self.cache_config.cache_metrics:
                        self._update_cache_metrics("invalid", cache_key, True)
                        
            # Initialize result
            result = UnifiedAnalysisResult(
                task_id=task.task_id,
                file_path=file_path,
                integrated_metrics={},
                recommendations=[],
                issues=[],
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "task": task.dict(),
                    "context": context or {}
                }
            )
            
            # Perform quality analysis
            if "quality" in task.components:
                try:
                    result.quality_analysis = self.quality_analyzer.analyze_code(code)
                    self._update_component_metrics("quality", result.quality_analysis.overall_score)
                except Exception as e:
                    logger.error(f"Quality analysis failed: {str(e)}")
                    
            # Perform metrics analysis
            if "metrics" in task.components:
                try:
                    result.metrics_analysis = await self.metrics_manager.analyze_code(
                        code=code,
                        file_path=file_path,
                        metric_types=task.metrics,
                        context=context
                    )
                    self._update_component_metrics("metrics", self._calculate_metrics_score(result.metrics_analysis))
                except Exception as e:
                    logger.error(f"Metrics analysis failed: {str(e)}")
                    
            # Perform review analysis
            if "review" in task.components:
                try:
                    result.review_analysis = await self.review_manager.review_code(
                        code=code,
                        file_path=file_path,
                        categories=task.review_categories,
                        context=context
                    )
                    self._update_component_metrics("review", self._calculate_review_score(result.review_analysis))
                except Exception as e:
                    logger.error(f"Review analysis failed: {str(e)}")
                    
            # Perform refactoring analysis
            if "refactoring" in task.components:
                try:
                    result.refactoring_analysis = await self.refactoring_manager.refactor_code(
                        code=code,
                        refactoring_types=task.refactoring_types,
                        context=context
                    )
                    self._update_component_metrics("refactoring", self._calculate_refactoring_score(result.refactoring_analysis))
                except Exception as e:
                    logger.error(f"Refactoring analysis failed: {str(e)}")
                    
            # Perform dependency analysis
            if task.dependency_types:
                try:
                    result.dependency_analysis = self.dependency_analyzer.analyze_dependencies(
                        code=code,
                        file_path=file_path,
                        dependency_type=task.dependency_types[0],
                        context=context
                    )
                    self._update_component_metrics("dependency", self._calculate_dependency_score(result.dependency_analysis))
                except Exception as e:
                    logger.error(f"Dependency analysis failed: {str(e)}")
                    
            # Perform model validation
            if task.validation_types:
                try:
                    result.validation_analysis = self.model_validator.validate_model(
                        model_config=context.get("model_config", {}),
                        training_data=context.get("training_data", {}),
                        validation_type=task.validation_types[0],
                        context=context
                    )
                    self._update_component_metrics("validation", self._calculate_validation_score(result.validation_analysis))
                except Exception as e:
                    logger.error(f"Model validation failed: {str(e)}")
                    
            # Perform deployment optimization
            if task.deployment_types:
                try:
                    result.deployment_analysis = self.deployment_optimizer.optimize_deployment(
                        deployment_config=context.get("deployment_config", {}),
                        current_metrics=context.get("current_metrics", {}),
                        optimization_type=task.deployment_types[0],
                        context=context
                    )
                    self._update_component_metrics("deployment", self._calculate_deployment_score(result.deployment_analysis))
                except Exception as e:
                    logger.error(f"Deployment optimization failed: {str(e)}")
                    
            # Perform resource optimization
            if task.resource_types:
                try:
                    result.resource_analysis = self.resource_optimizer.optimize_resources(
                        resource_config=context.get("resource_config", {}),
                        current_metrics=context.get("current_metrics", {}),
                        resource_type=task.resource_types[0],
                        context=context
                    )
                    self._update_component_metrics("resource", self._calculate_resource_score(result.resource_analysis))
                except Exception as e:
                    logger.error(f"Resource optimization failed: {str(e)}")
                    
            # Perform security analysis
            if task.security_types:
                try:
                    result.security_analysis = self.security_analyzer.analyze_security(
                        code=code,
                        file_path=file_path,
                        security_type=task.security_types[0],
                        context=context
                    )
                    self._update_component_metrics("security", self._calculate_security_score(result.security_analysis))
                except Exception as e:
                    logger.error(f"Security analysis failed: {str(e)}")
                    
            # Perform performance analysis
            if task.performance_types:
                try:
                    result.performance_analysis = self.performance_analyzer.analyze_performance(
                        code=code,
                        file_path=file_path,
                        performance_type=task.performance_types[0],
                        context=context
                    )
                    self._update_component_metrics("performance", self._calculate_performance_score(result.performance_analysis))
                except Exception as e:
                    logger.error(f"Performance analysis failed: {str(e)}")
                    
            # Perform architecture analysis
            if task.architecture_types:
                try:
                    result.architecture_analysis = self.architecture_analyzer.analyze_architecture(
                        code=code,
                        file_path=file_path,
                        architecture_type=task.architecture_types[0],
                        context=context
                    )
                    self._update_component_metrics("architecture", self._calculate_architecture_score(result.architecture_analysis))
                except Exception as e:
                    logger.error(f"Architecture analysis failed: {str(e)}")
                    
            # Perform API analysis
            if task.api_types:
                try:
                    result.api_analysis = self.api_analyzer.analyze_api(
                        code=code,
                        file_path=file_path,
                        api_type=task.api_types[0],
                        context=context
                    )
                    self._update_component_metrics("api", self._calculate_api_score(result.api_analysis))
                except Exception as e:
                    logger.error(f"API analysis failed: {str(e)}")
                    
            # Perform database analysis
            if task.database_types:
                try:
                    result.database_analysis = self.database_analyzer.analyze_database(
                        code=code,
                        file_path=file_path,
                        database_type=task.database_types[0],
                        context=context
                    )
                    self._update_component_metrics("database", self._calculate_database_score(result.database_analysis))
                except Exception as e:
                    logger.error(f"Database analysis failed: {str(e)}")
                    
            # Perform model architecture analysis
            if task.model_architecture_types:
                try:
                    result.model_architecture_analysis = self.model_architecture_analyzer.analyze_architecture(
                        code=code,
                        file_path=file_path,
                        architecture_type=task.model_architecture_types[0],
                        context=context
                    )
                    self._update_component_metrics("model_architecture", self._calculate_model_architecture_score(result.model_architecture_analysis))
                except Exception as e:
                    logger.error(f"Model architecture analysis failed: {str(e)}")
                    
            # Perform test analysis
            if task.test_types:
                try:
                    result.test_analysis = self.test_analyzer.analyze_tests(
                        code=code,
                        file_path=file_path,
                        test_type=task.test_types[0],
                        context=context
                    )
                    self._update_component_metrics("test", self._calculate_test_score(result.test_analysis))
                except Exception as e:
                    logger.error(f"Test analysis failed: {str(e)}")
                    
            # Perform documentation analysis
            if task.documentation_types:
                try:
                    result.documentation_analysis = self.documentation_analyzer.analyze_documentation(
                        code=code,
                        file_path=file_path,
                        documentation_type=task.documentation_types[0],
                        context=context
                    )
                    self._update_component_metrics("documentation", self._calculate_documentation_score(result.documentation_analysis))
                except Exception as e:
                    logger.error(f"Documentation analysis failed: {str(e)}")
                    
            # Perform routing analysis
            if task.routing_types:
                try:
                    result.routing_analysis = self.routing_analyzer.analyze_routing(
                        code=code,
                        file_path=file_path,
                        routing_type=task.routing_types[0],
                        context=context
                    )
                    self._update_component_metrics("routing", self._calculate_routing_score(result.routing_analysis))
                except Exception as e:
                    logger.error(f"Routing analysis failed: {str(e)}")
                    
            # Perform accessibility analysis
            if task.accessibility_types:
                try:
                    result.accessibility_analysis = self.accessibility_analyzer.analyze_accessibility(
                        code=code,
                        file_path=file_path,
                        accessibility_type=task.accessibility_types[0],
                        context=context
                    )
                    self._update_component_metrics("accessibility", self._calculate_accessibility_score(result.accessibility_analysis))
                except Exception as e:
                    logger.error(f"Accessibility analysis failed: {str(e)}")
                    
            # Calculate integrated metrics
            result.integrated_metrics = self._calculate_integrated_metrics(result)
            
            # Generate recommendations
            result.recommendations = self._generate_integrated_recommendations(result)
            
            # Collect issues
            result.issues = self._collect_integrated_issues(result)
            
            # Store in history and cache
            self.analysis_history.append(result)
            if use_cache and self.cache_config.enabled:
                cache_key = self._generate_cache_key(code, file_path, task)
                self.analysis_cache[cache_key] = result
                if len(self.analysis_cache) > self.cache_config.max_size:
                    self._prune_cache()
                self._save_persistent_cache()
                if self.cache_config.cache_metrics:
                    self._update_cache_metrics("store", cache_key, True)
                    
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to perform unified analysis: {str(e)}")
            
    def _prune_cache(self):
        """Prune cache to maintain size limit"""
        # Sort by timestamp and remove oldest entries
        sorted_entries = sorted(
            self.analysis_cache.items(),
            key=lambda x: x[1].metadata.get("analyzed_at", ""),
            reverse=True
        )
        removed_entries = dict(sorted_entries[self.cache_config.max_size:])
        self.analysis_cache = dict(sorted_entries[:self.cache_config.max_size])
        
        # Update cache metrics
        if self.cache_config.cache_metrics:
            for key in removed_entries:
                self._update_cache_metrics("prune", key, True)
                
    def _calculate_database_score(self, database_result: Optional[DatabaseResult]) -> float:
        """Calculate overall database score"""
        if not database_result:
            return 0.0
            
        scores = []
        for metric in database_result.metrics.values():
            if metric.status == "good":
                scores.append(1.0)
            elif metric.status == "warning":
                scores.append(0.7)
            elif metric.status == "critical":
                scores.append(0.3)
            else:
                scores.append(0.0)
                
        return sum(scores) / len(scores) if scores else 0.0
        
    def _calculate_model_architecture_score(self, model_architecture_result: Optional[ModelArchitectureResult]) -> float:
        """Calculate overall model architecture score"""
        if not model_architecture_result:
            return 0.0
            
        scores = []
        for metric in model_architecture_result.metrics.values():
            if metric.status == "good":
                scores.append(1.0)
            elif metric.status == "warning":
                scores.append(0.7)
            elif metric.status == "critical":
                scores.append(0.3)
            else:
                scores.append(0.0)
                
        return sum(scores) / len(scores) if scores else 0.0
        
    def _calculate_integrated_metrics(self, result: UnifiedAnalysisResult) -> Dict[str, float]:
        """Calculate integrated metrics from all analyses"""
        metrics = {}
        
        # Quality metrics
        if result.quality_analysis:
            metrics["quality_score"] = result.quality_analysis.overall_score
            
        # Metrics analysis
        if result.metrics_analysis:
            for metric_type, metric_result in result.metrics_analysis.metrics.items():
                metrics[f"metric_{metric_type.value}"] = metric_result.value
                
        # Review metrics
        if result.review_analysis:
            metrics["review_score"] = self._calculate_review_score(result.review_analysis)
            metrics["issue_count"] = len(result.review_analysis.comments)
            
        # Refactoring metrics
        if result.refactoring_analysis:
            metrics["refactoring_score"] = self._calculate_refactoring_score(result.refactoring_analysis)
            metrics["improvement_count"] = len(result.refactoring_analysis.changes)
            
        # Dependency metrics
        if result.dependency_analysis:
            metrics["dependency_score"] = self._calculate_dependency_score(result.dependency_analysis)
            for metric_name, metric in result.dependency_analysis.metrics.items():
                metrics[f"dependency_{metric_name}"] = metric.value
            
        # Validation metrics
        if result.validation_analysis:
            metrics["validation_score"] = self._calculate_validation_score(result.validation_analysis)
            for metric_name, metric in result.validation_analysis.metrics.items():
                metrics[f"validation_{metric_name}"] = metric.value
                
        # Deployment metrics
        if result.deployment_analysis:
            metrics["deployment_score"] = self._calculate_deployment_score(result.deployment_analysis)
            for metric_name, metric in result.deployment_analysis.metrics.items():
                metrics[f"deployment_{metric_name}"] = metric.value
                
        # Resource metrics
        if result.resource_analysis:
            metrics["resource_score"] = self._calculate_resource_score(result.resource_analysis)
            for metric_name, metric in result.resource_analysis.metrics.items():
                metrics[f"resource_{metric_name}"] = metric.value
                
        # Security metrics
        if result.security_analysis:
            metrics["security_score"] = self._calculate_security_score(result.security_analysis)
            for metric_name, metric in result.security_analysis.metrics.items():
                metrics[f"security_{metric_name}"] = metric.value
                
        # Performance metrics
        if result.performance_analysis:
            metrics["performance_score"] = self._calculate_performance_score(result.performance_analysis)
            for metric_name, metric in result.performance_analysis.metrics.items():
                metrics[f"performance_{metric_name}"] = metric.value
                
        # Architecture metrics
        if result.architecture_analysis:
            metrics["architecture_score"] = self._calculate_architecture_score(result.architecture_analysis)
            for metric_name, metric in result.architecture_analysis.metrics.items():
                metrics[f"architecture_{metric_name}"] = metric.value
                
        # API metrics
        if result.api_analysis:
            metrics["api_score"] = self._calculate_api_score(result.api_analysis)
            for metric_name, metric in result.api_analysis.metrics.items():
                metrics[f"api_{metric_name}"] = metric.value
                
        # Database metrics
        if result.database_analysis:
            metrics["database_score"] = self._calculate_database_score(result.database_analysis)
            for metric_name, metric in result.database_analysis.metrics.items():
                metrics[f"database_{metric_name}"] = metric.value
            
        # Model architecture metrics
        if result.model_architecture_analysis:
            metrics["model_architecture_score"] = self._calculate_model_architecture_score(result.model_architecture_analysis)
            for metric_name, metric in result.model_architecture_analysis.metrics.items():
                metrics[f"model_architecture_{metric_name}"] = metric.value
            
        # Test metrics
        if result.test_analysis:
            metrics["test_score"] = self._calculate_test_score(result.test_analysis)
            for metric_name, metric in result.test_analysis.metrics.items():
                metrics[f"test_{metric_name}"] = metric.value
            
        # Documentation metrics
        if result.documentation_analysis:
            metrics["documentation_score"] = self._calculate_documentation_score(result.documentation_analysis)
            for metric_name, metric in result.documentation_analysis.metrics.items():
                metrics[f"documentation_{metric_name}"] = metric.value
            
        # Routing metrics
        if result.routing_analysis:
            metrics["routing_score"] = self._calculate_routing_score(result.routing_analysis)
            for metric_name, metric in result.routing_analysis.metrics.items():
                metrics[f"routing_{metric_name}"] = metric.value
            
        # Accessibility metrics
        if result.accessibility_analysis:
            metrics["accessibility_score"] = self._calculate_accessibility_score(result.accessibility_analysis)
            for metric_name, metric in result.accessibility_analysis.metrics.items():
                metrics[f"accessibility_{metric_name}"] = metric.value
            
        # Calculate overall score with weights
        weights = {
            "quality": 0.15,
            "metrics": 0.1,
            "review": 0.1,
            "refactoring": 0.1,
            "dependency": 0.1,
            "validation": 0.1,
            "deployment": 0.1,
            "resource": 0.1,
            "security": 0.15,
            "performance": 0.1,
            "architecture": 0.1,
            "api": 0.1,
            "database": 0.1,
            "model_architecture": 0.1,
            "test": 0.1,
            "documentation": 0.1,
            "routing": 0.1,
            "accessibility": 0.1
        }
        
        scores = []
        if "quality" in result.metadata.get("task", {}).get("components", []):
            scores.append((metrics.get("quality_score", 0.0), weights["quality"]))
        if "metrics" in result.metadata.get("task", {}).get("components", []):
            scores.append((self._calculate_metrics_score(result.metrics_analysis), weights["metrics"]))
        if "review" in result.metadata.get("task", {}).get("components", []):
            scores.append((metrics.get("review_score", 0.0), weights["review"]))
        if "refactoring" in result.metadata.get("task", {}).get("components", []):
            scores.append((metrics.get("refactoring_score", 0.0), weights["refactoring"]))
        if "dependency" in result.metadata.get("task", {}).get("components", []):
            scores.append((metrics.get("dependency_score", 0.0), weights["dependency"]))
        if result.validation_analysis:
            scores.append((metrics.get("validation_score", 0.0), weights["validation"]))
        if result.deployment_analysis:
            scores.append((metrics.get("deployment_score", 0.0), weights["deployment"]))
        if result.resource_analysis:
            scores.append((metrics.get("resource_score", 0.0), weights["resource"]))
        if result.security_analysis:
            scores.append((metrics.get("security_score", 0.0), weights["security"]))
        if result.performance_analysis:
            scores.append((metrics.get("performance_score", 0.0), weights["performance"]))
        if result.architecture_analysis:
            scores.append((metrics.get("architecture_score", 0.0), weights["architecture"]))
        if result.api_analysis:
            scores.append((metrics.get("api_score", 0.0), weights["api"]))
        if result.database_analysis:
            scores.append((metrics.get("database_score", 0.0), weights["database"]))
        if result.model_architecture_analysis:
            scores.append((metrics.get("model_architecture_score", 0.0), weights["model_architecture"]))
        if result.test_analysis:
            scores.append((metrics.get("test_score", 0.0), weights["test"]))
        if result.documentation_analysis:
            scores.append((metrics.get("documentation_score", 0.0), weights["documentation"]))
        if result.routing_analysis:
            scores.append((metrics.get("routing_score", 0.0), weights["routing"]))
        if result.accessibility_analysis:
            scores.append((metrics.get("accessibility_score", 0.0), weights["accessibility"]))
            
        if scores:
            metrics["overall_score"] = sum(score * weight for score, weight in scores)
        else:
            metrics["overall_score"] = 0.0
            
        return metrics
        
    def _generate_integrated_recommendations(self, result: UnifiedAnalysisResult) -> List[str]:
        """Generate integrated recommendations from all analyses"""
        recommendations = []
        
        # Quality recommendations
        if result.quality_analysis:
            recommendations.extend(result.quality_analysis.suggestions)
            
        # Metrics recommendations
        if result.metrics_analysis:
            for metric in result.metrics_analysis.metrics.values():
                recommendations.extend(metric.recommendations)
                
        # Review recommendations
        if result.review_analysis:
            for comment in result.review_analysis.comments:
                if comment.suggestion:
                    recommendations.append(comment.suggestion)
                    
        # Refactoring recommendations
        if result.refactoring_analysis:
            for change in result.refactoring_analysis.changes:
                recommendations.append(f"Apply {change['type']} refactoring: {change['description']}")
                
        # Dependency recommendations
        if result.dependency_analysis:
            recommendations.extend(result.dependency_analysis.recommendations)
            
        # Validation recommendations
        if result.validation_analysis:
            recommendations.extend(result.validation_analysis.recommendations)
            
        # Deployment recommendations
        if result.deployment_analysis:
            recommendations.extend(result.deployment_analysis.recommendations)
            
        # Resource recommendations
        if result.resource_analysis:
            recommendations.extend(result.resource_analysis.recommendations)
            
        # Security recommendations
        if result.security_analysis:
            recommendations.extend(result.security_analysis.recommendations)
            
        # Performance recommendations
        if result.performance_analysis:
            recommendations.extend(result.performance_analysis.recommendations)
            
        # Architecture recommendations
        if result.architecture_analysis:
            recommendations.extend(result.architecture_analysis.recommendations)
            
        # API recommendations
        if result.api_analysis:
            recommendations.extend(result.api_analysis.recommendations)
            
        # Database recommendations
        if result.database_analysis:
            recommendations.extend(result.database_analysis.recommendations)
            
        # Model architecture recommendations
        if result.model_architecture_analysis:
            recommendations.extend(result.model_architecture_analysis.recommendations)
            
        # Test recommendations
        if result.test_analysis:
            recommendations.extend(result.test_analysis.recommendations)
            
        # Documentation recommendations
        if result.documentation_analysis:
            recommendations.extend(result.documentation_analysis.recommendations)
            
        # Routing recommendations
        if result.routing_analysis:
            recommendations.extend(result.routing_analysis.recommendations)
            
        # Accessibility recommendations
        if result.accessibility_analysis:
            recommendations.extend(result.accessibility_analysis.recommendations)
            
        # Generate cross-component recommendations
        recommendations.extend(self._generate_cross_component_recommendations(result))
                
        return list(set(recommendations))  # Remove duplicates
        
    def _generate_cross_component_recommendations(self, result: UnifiedAnalysisResult) -> List[str]:
        """Generate recommendations based on cross-component analysis"""
        recommendations = []
        
        # Check for high complexity and low maintainability
        if (result.quality_analysis and result.metrics_analysis and
            result.quality_analysis.overall_score < 0.6 and
            result.metrics_analysis.metrics.get(MetricType.MAINTAINABILITY).value < 0.7):
            recommendations.append(
                "High complexity and low maintainability detected. Consider breaking down "
                "complex components and improving code organization."
            )
            
        # Check for security issues and refactoring needs
        if (result.review_analysis and result.refactoring_analysis and
            any(comment.severity.value in ["critical", "high"] for comment in result.review_analysis.comments)):
            recommendations.append(
                "Security issues detected. Prioritize security-related refactoring "
                "suggestions to address vulnerabilities."
            )
            
        # Check for dependency issues and code quality
        if (result.dependency_analysis and result.quality_analysis and
            result.dependency_analysis.metrics.coupling_score > 0.7 and
            result.quality_analysis.overall_score < 0.7):
            recommendations.append(
                "High coupling and low code quality detected. Consider improving "
                "code organization and reducing external dependencies."
            )
            
        # Check for model validation and deployment issues
        if (result.validation_analysis and result.deployment_analysis and
            result.validation_analysis.metrics.get("model_complexity", None) and
            result.deployment_analysis.metrics.get("inference_latency", None) and
            result.validation_analysis.metrics["model_complexity"].status == "critical" and
            result.deployment_analysis.metrics["inference_latency"].status == "critical"):
            recommendations.append(
                "Model complexity and deployment performance issues detected. Consider "
                "model optimization and deployment improvements."
            )
            
        # Check for resource constraints
        if (result.resource_analysis and result.deployment_analysis and
            result.resource_analysis.metrics.get("cpu_utilization", None) and
            result.deployment_analysis.metrics.get("resource_utilization", None) and
            result.resource_analysis.metrics["cpu_utilization"].status == "critical" and
            result.deployment_analysis.metrics["resource_utilization"].status == "critical"):
            recommendations.append(
                "Resource utilization issues detected. Consider optimizing resource "
                "allocation and implementing better resource management."
            )
            
        # Check for security vulnerabilities
        if (result.security_analysis and result.review_analysis and
            result.security_analysis.metrics.get("sql_injection", None) and
            result.security_analysis.metrics["sql_injection"].status == "critical"):
            recommendations.append(
                "Critical security vulnerabilities detected. Prioritize security "
                "fixes and implement proper input validation."
            )
            
        # Check for compliance issues
        if (result.security_analysis and result.validation_analysis and
            any(metric.status == "critical" for metric in result.security_analysis.metrics.values()
                if "compliance" in metric.name)):
            recommendations.append(
                "Compliance issues detected. Review and implement necessary security "
                "controls to meet requirements."
            )
            
        # Check for performance issues
        if (result.performance_analysis and result.deployment_analysis and
            result.performance_analysis.metrics.get("cpu_usage", None) and
            result.deployment_analysis.metrics.get("resource_utilization", None) and
            result.performance_analysis.metrics["cpu_usage"].status == "critical" and
            result.deployment_analysis.metrics["resource_utilization"].status == "critical"):
            recommendations.append(
                "Critical performance issues detected. Consider optimizing algorithms "
                "and improving resource utilization."
            )
            
        # Check for memory issues
        if (result.performance_analysis and result.resource_analysis and
            result.performance_analysis.metrics.get("memory_usage", None) and
            result.resource_analysis.metrics.get("memory_efficiency", None) and
            result.performance_analysis.metrics["memory_usage"].status == "critical" and
            result.resource_analysis.metrics["memory_efficiency"].status == "critical"):
            recommendations.append(
                "Critical memory issues detected. Consider implementing memory "
                "optimizations and better resource management."
            )
            
        # Check for API issues
        if (result.api_analysis and result.performance_analysis and
            result.api_analysis.metrics.get("response_time", None) and
            result.performance_analysis.metrics.get("response_time", None) and
            result.api_analysis.metrics["response_time"].status == "critical" and
            result.performance_analysis.metrics["response_time"].status == "critical"):
            recommendations.append(
                "Critical API performance issues detected. Consider implementing "
                "caching and optimizing API endpoints."
            )
            
        # Check for API security issues
        if (result.api_analysis and result.security_analysis and
            result.api_analysis.metrics.get("authentication", None) and
            result.security_analysis.metrics.get("api_security", None) and
            result.api_analysis.metrics["authentication"].status == "critical" and
            result.security_analysis.metrics["api_security"].status == "critical"):
            recommendations.append(
                "Critical API security issues detected. Implement proper authentication, "
                "authorization, and rate limiting."
            )
            
        # Check for database issues
        if (result.database_analysis and result.performance_analysis and
            result.database_analysis.metrics.get("query_performance", None) and
            result.performance_analysis.metrics.get("database_performance", None) and
            result.database_analysis.metrics["query_performance"].status == "critical" and
            result.performance_analysis.metrics["database_performance"].status == "critical"):
            recommendations.append(
                "Critical database performance issues detected. Consider optimizing "
                "queries and implementing better caching strategies."
            )
            
        # Check for database security issues
        if (result.database_analysis and result.security_analysis and
            result.database_analysis.metrics.get("sql_injection", None) and
            result.security_analysis.metrics.get("database_security", None) and
            result.database_analysis.metrics["sql_injection"].status == "critical" and
            result.security_analysis.metrics["database_security"].status == "critical"):
            recommendations.append(
                "Critical database security issues detected. Implement proper SQL "
                "injection prevention and access controls."
            )
            
        # Check for documentation and code quality issues
        if (result.documentation_analysis and result.quality_analysis and
            result.documentation_analysis.metrics.get("docstring_coverage", None) and
            result.quality_analysis.overall_score < 0.7 and
            result.documentation_analysis.metrics["docstring_coverage"].status == "critical"):
            recommendations.append(
                "Critical documentation and code quality issues detected. Consider "
                "improving both code quality and documentation."
            )
            
        # Check for documentation and test coverage issues
        if (result.documentation_analysis and result.test_analysis and
            result.documentation_analysis.metrics.get("overall_coverage", None) and
            result.test_analysis.metrics.get("test_coverage", None) and
            result.documentation_analysis.metrics["overall_coverage"].status == "critical" and
            result.test_analysis.metrics["test_coverage"].status == "critical"):
            recommendations.append(
                "Critical documentation and test coverage issues detected. Consider "
                "improving both documentation and test coverage."
            )
            
        # Check for accessibility and documentation issues
        if (result.accessibility_analysis and result.documentation_analysis and
            result.accessibility_analysis.metrics.get("aria_compliance", None) and
            result.documentation_analysis.metrics.get("docstring_coverage", None) and
            result.accessibility_analysis.metrics["aria_compliance"].status == "critical" and
            result.documentation_analysis.metrics["docstring_coverage"].status == "critical"):
            recommendations.append(
                "Critical accessibility and documentation issues detected. Consider "
                "improving both accessibility implementation and documentation."
            )
            
        # Check for accessibility and test coverage issues
        if (result.accessibility_analysis and result.test_analysis and
            result.accessibility_analysis.metrics.get("screen_reader_compatibility", None) and
            result.test_analysis.metrics.get("test_coverage", None) and
            result.accessibility_analysis.metrics["screen_reader_compatibility"].status == "critical" and
            result.test_analysis.metrics["test_coverage"].status == "critical"):
            recommendations.append(
                "Critical accessibility and test coverage issues detected. Consider "
                "improving both accessibility testing and overall test coverage."
            )
            
        return recommendations
        
    def _collect_integrated_issues(self, result: UnifiedAnalysisResult) -> List[Dict[str, Any]]:
        """Collect issues from all analyses"""
        issues = []
        
        # Quality issues
        if result.quality_analysis:
            for issue in result.quality_analysis.issues:
                issues.append({
                    "source": "quality",
                    "type": issue["type"],
                    "line": issue["line"],
                    "column": issue["column"],
                    "message": issue["message"],
                    "severity": "high" if issue["type"] == "complexity" else "medium"
                })
                
        # Metrics issues
        if result.metrics_analysis:
            for metric_type, metric in result.metrics_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "metrics",
                        "type": metric_type.value,
                        "value": metric.value,
                        "threshold": metric.thresholds.get("warning"),
                        "message": f"{metric_type.value} metric is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Review issues
        if result.review_analysis:
            for comment in result.review_analysis.comments:
                issues.append({
                    "source": "review",
                    "type": comment.category.value,
                    "line": comment.line_number,
                    "column": comment.column,
                    "message": comment.description,
                    "severity": comment.severity.value
                })
                
        # Refactoring issues
        if result.refactoring_analysis:
            for change in result.refactoring_analysis.changes:
                issues.append({
                    "source": "refactoring",
                    "type": change["type"].value,
                    "description": change["description"],
                    "message": f"Suggested refactoring: {change['description']}",
                    "severity": "medium"
                })
                
        # Dependency issues
        if result.dependency_analysis:
            for metric_name, metric in result.dependency_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "dependency",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Dependency issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Validation issues
        if result.validation_analysis:
            for metric_name, metric in result.validation_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "validation",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Validation issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Deployment issues
        if result.deployment_analysis:
            for metric_name, metric in result.deployment_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "deployment",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Deployment issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Resource issues
        if result.resource_analysis:
            for metric_name, metric in result.resource_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "resource",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Resource issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Security issues
        if result.security_analysis:
            for metric_name, metric in result.security_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "security",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Security issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Performance issues
        if result.performance_analysis:
            for metric_name, metric in result.performance_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "performance",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Performance issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Architecture issues
        if result.architecture_analysis:
            for metric_name, metric in result.architecture_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "architecture",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Architecture issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # API issues
        if result.api_analysis:
            for metric_name, metric in result.api_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "api",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"API issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Database issues
        if result.database_analysis:
            for metric_name, metric in result.database_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "database",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Database issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Model architecture issues
        if result.model_architecture_analysis:
            for metric_name, metric in result.model_architecture_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "model_architecture",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Model architecture issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Test issues
        if result.test_analysis:
            for metric_name, metric in result.test_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "test",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Test issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Documentation issues
        if result.documentation_analysis:
            for metric_name, metric in result.documentation_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "documentation",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Documentation issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Routing issues
        if result.routing_analysis:
            for metric_name, metric in result.routing_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "routing",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Routing issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        # Accessibility issues
        if result.accessibility_analysis:
            for metric_name, metric in result.accessibility_analysis.metrics.items():
                if metric.status != "good":
                    issues.append({
                        "source": "accessibility",
                        "type": metric_name,
                        "value": metric.value,
                        "target": metric.target,
                        "message": f"Accessibility issue: {metric_name} is {metric.status}",
                        "severity": metric.status
                    })
                    
        return issues
        
    def clear_cache(self):
        """Clear the analysis cache"""
        self.analysis_cache.clear()
        if self.cache_config.storage_path:
            cache_dir = Path(self.cache_config.storage_path)
            for cache_file in cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.error(f"Failed to delete cache file {cache_file}: {str(e)}")
                    
    def get_cached_analysis(self, file_path: str, task_id: str) -> Optional[UnifiedAnalysisResult]:
        """Get cached analysis result"""
        cache_key = self._generate_cache_key(file_path, task_id)
        return self.analysis_cache.get(cache_key)
        
    def get_analysis_history(self) -> List[UnifiedAnalysisResult]:
        """Get analysis history"""
        return self.analysis_history
        
    def get_component_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get component performance metrics"""
        return self.component_metrics
        
    def get_cache_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get cache operation metrics"""
        return self.cache_metrics
        
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        if not self.analysis_history:
            return {}
            
        latest = self.analysis_history[-1]
        summary = {
            "analysis_type": latest.analysis_type.value,
            "metadata": latest.metadata
        }
        
        # Add model architecture metrics
        if latest.model_architecture_analysis:
            summary["model_architecture"] = {
                "metrics": {
                    name: {
                        "value": metric.value,
                        "status": metric.status
                    }
                    for name, metric in latest.model_architecture_analysis.metrics.items()
                },
                "issue_count": len(latest.model_architecture_analysis.issues),
                "recommendation_count": len(latest.model_architecture_analysis.recommendations)
            }
            
        # Add test metrics
        if latest.test_analysis:
            summary["test"] = {
                "metrics": {
                    name: {
                        "value": metric.value,
                        "status": metric.status
                    }
                    for name, metric in latest.test_analysis.metrics.items()
                },
                "issue_count": len(latest.test_analysis.issues),
                "recommendation_count": len(latest.test_analysis.recommendations)
            }
            
        # Add dependency metrics
        if latest.dependency_analysis:
            summary["dependency"] = {
                "metrics": {
                    name: {
                        "value": metric.value,
                        "status": metric.status
                    }
                    for name, metric in latest.dependency_analysis.metrics.items()
                },
                "issue_count": len(latest.dependency_analysis.issues),
                "recommendation_count": len(latest.dependency_analysis.recommendations)
            }
            
        # Add documentation metrics
        if latest.documentation_analysis:
            summary["documentation"] = {
                "metrics": {
                    name: {
                        "value": metric.value,
                        "status": metric.status
                    }
                    for name, metric in latest.documentation_analysis.metrics.items()
                },
                "issue_count": len(latest.documentation_analysis.issues),
                "recommendation_count": len(latest.documentation_analysis.recommendations)
            }
            
        # Add routing metrics
        if latest.routing_analysis:
            summary["routing"] = {
                "metrics": {
                    name: {
                        "value": metric.value,
                        "status": metric.status
                    }
                    for name, metric in latest.routing_analysis.metrics.items()
                },
                "issue_count": len(latest.routing_analysis.issues),
                "recommendation_count": len(latest.routing_analysis.recommendations)
            }
            
        # Add accessibility metrics
        if latest.accessibility_analysis:
            summary["accessibility"] = {
                "metrics": {
                    name: {
                        "value": metric.value,
                        "status": metric.status
                    }
                    for name, metric in latest.accessibility_analysis.metrics.items()
                },
                "issue_count": len(latest.accessibility_analysis.issues),
                "recommendation_count": len(latest.accessibility_analysis.recommendations)
            }
            
        # Add internationalization metrics
        if latest.internationalization_analysis:
            summary["internationalization"] = {
                "metrics": {
                    name: {
                        "value": metric.value,
                        "status": metric.status
                    }
                    for name, metric in latest.internationalization_analysis.metrics.items()
                },
                "issue_count": len(latest.internationalization_analysis.issues),
                "recommendation_count": len(latest.internationalization_analysis.recommendations)
            }
            
        return summary
        
    def _update_component_metrics(self, component: str, score: float):
        """Update component performance metrics"""
        if component not in self.component_metrics:
            self.component_metrics[component] = {
                "total_analyses": 0,
                "avg_score": 0.0,
                "success_rate": 0.0
            }
            
        metrics = self.component_metrics[component]
        metrics["total_analyses"] += 1
        metrics["avg_score"] = 0.9 * metrics["avg_score"] + 0.1 * score
        metrics["success_rate"] = 0.9 * metrics["success_rate"] + 0.1 * float(score > 0.5)
        
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security analysis summary"""
        security_results = [
            result for result in self.analysis_history
            if result.security_analysis
        ]
        
        if not security_results:
            return {}
            
        latest = security_results[-1]
        return {
            "security_type": latest.security_analysis.security_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.security_analysis.metrics.items()
            },
            "issue_count": len(latest.security_analysis.issues),
            "recommendation_count": len(latest.security_analysis.recommendations)
        }
        
    def get_deployment_summary(self) -> Dict[str, Any]:
        """Get deployment analysis summary"""
        deployment_results = [
            result for result in self.analysis_history
            if result.deployment_analysis
        ]
        
        if not deployment_results:
            return {}
            
        latest = deployment_results[-1]
        return {
            "deployment_type": latest.deployment_analysis.deployment_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.deployment_analysis.metrics.items()
            },
            "issue_count": len(latest.deployment_analysis.issues),
            "recommendation_count": len(latest.deployment_analysis.recommendations)
        }
        
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get resource analysis summary"""
        resource_results = [
            result for result in self.analysis_history
            if result.resource_analysis
        ]
        
        if not resource_results:
            return {}
            
        latest = resource_results[-1]
        return {
            "resource_type": latest.resource_analysis.resource_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.resource_analysis.metrics.items()
            },
            "issue_count": len(latest.resource_analysis.issues),
            "recommendation_count": len(latest.resource_analysis.recommendations)
        }
        
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation analysis summary"""
        validation_results = [
            result for result in self.analysis_history
            if result.validation_analysis
        ]
        
        if not validation_results:
            return {}
            
        latest = validation_results[-1]
        return {
            "validation_type": latest.validation_analysis.validation_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.validation_analysis.metrics.items()
            },
            "issue_count": len(latest.validation_analysis.issues),
            "recommendation_count": len(latest.validation_analysis.recommendations)
        }
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance analysis summary"""
        performance_results = [
            result for result in self.analysis_history
            if result.performance_analysis
        ]
        
        if not performance_results:
            return {}
            
        latest = performance_results[-1]
        return {
            "performance_type": latest.performance_analysis.performance_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.performance_analysis.metrics.items()
            },
            "issue_count": len(latest.performance_analysis.issues),
            "recommendation_count": len(latest.performance_analysis.recommendations)
        }
        
    def get_architecture_summary(self) -> Dict[str, Any]:
        """Get architecture analysis summary"""
        architecture_results = [
            result for result in self.analysis_history
            if result.architecture_analysis
        ]
        
        if not architecture_results:
            return {}
            
        latest = architecture_results[-1]
        return {
            "architecture_type": latest.architecture_analysis.architecture_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.architecture_analysis.metrics.items()
            },
            "issue_count": len(latest.architecture_analysis.issues),
            "recommendation_count": len(latest.architecture_analysis.recommendations)
        }
        
    def get_api_summary(self) -> Dict[str, Any]:
        """Get API analysis summary"""
        api_results = [
            result for result in self.analysis_history
            if result.api_analysis
        ]
        
        if not api_results:
            return {}
            
        latest = api_results[-1]
        return {
            "api_type": latest.api_analysis.api_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.api_analysis.metrics.items()
            },
            "issue_count": len(latest.api_analysis.issues),
            "recommendation_count": len(latest.api_analysis.recommendations)
        }
        
    def get_database_summary(self) -> Dict[str, Any]:
        """Get database analysis summary"""
        database_results = [
            result for result in self.analysis_history
            if result.database_analysis
        ]
        
        if not database_results:
            return {}
            
        latest = database_results[-1]
        return {
            "database_type": latest.database_analysis.database_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.database_analysis.metrics.items()
            },
            "issue_count": len(latest.database_analysis.issues),
            "recommendation_count": len(latest.database_analysis.recommendations)
        }
        
    def get_model_architecture_summary(self) -> Dict[str, Any]:
        """Get model architecture analysis summary"""
        model_architecture_results = [
            result for result in self.analysis_history
            if result.model_architecture_analysis
        ]
        
        if not model_architecture_results:
            return {}
            
        latest = model_architecture_results[-1]
        return {
            "architecture_type": latest.model_architecture_analysis.architecture_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.model_architecture_analysis.metrics.items()
            },
            "issue_count": len(latest.model_architecture_analysis.issues),
            "recommendation_count": len(latest.model_architecture_analysis.recommendations)
        }
        
    def get_test_summary(self) -> Dict[str, Any]:
        """Get test analysis summary"""
        test_results = [
            result for result in self.analysis_history
            if result.test_analysis
        ]
        
        if not test_results:
            return {}
            
        latest = test_results[-1]
        return {
            "test_type": latest.test_analysis.test_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.test_analysis.metrics.items()
            },
            "issue_count": len(latest.test_analysis.issues),
            "recommendation_count": len(latest.test_analysis.recommendations)
        }
        
    def _calculate_test_score(self, test_result: Optional[TestResult]) -> float:
        """Calculate overall test score"""
        if not test_result:
            return 0.0
            
        scores = []
        for metric in test_result.metrics.values():
            if metric.status == "good":
                scores.append(1.0)
            elif metric.status == "warning":
                scores.append(0.7)
            elif metric.status == "critical":
                scores.append(0.3)
            else:
                scores.append(0.0)
                
        return sum(scores) / len(scores) if scores else 0.0
        
    def _calculate_dependency_score(self, dependency_result: Optional[DependencyResult]) -> float:
        """Calculate overall dependency score"""
        if not dependency_result:
            return 0.0
            
        scores = []
        for metric in dependency_result.metrics.values():
            if metric.status == "good":
                scores.append(1.0)
            elif metric.status == "warning":
                scores.append(0.7)
            elif metric.status == "critical":
                scores.append(0.3)
            else:
                scores.append(0.0)
                
        return sum(scores) / len(scores) if scores else 0.0
        
    def get_dependency_summary(self) -> Dict[str, Any]:
        """Get dependency analysis summary"""
        dependency_results = [
            result for result in self.analysis_history
            if result.dependency_analysis
        ]
        
        if not dependency_results:
            return {}
            
        latest = dependency_results[-1]
        return {
            "dependency_type": latest.dependency_analysis.dependency_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.dependency_analysis.metrics.items()
            },
            "issue_count": len(latest.dependency_analysis.issues),
            "recommendation_count": len(latest.dependency_analysis.recommendations)
        }
        
    def get_documentation_summary(self) -> Dict[str, Any]:
        """Get documentation analysis summary"""
        documentation_results = [
            result for result in self.analysis_history
            if result.documentation_analysis
        ]
        
        if not documentation_results:
            return {}
            
        latest = documentation_results[-1]
        return {
            "documentation_type": latest.documentation_analysis.documentation_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.documentation_analysis.metrics.items()
            },
            "issue_count": len(latest.documentation_analysis.issues),
            "recommendation_count": len(latest.documentation_analysis.recommendations)
        }
        
    def _calculate_documentation_score(self, documentation_result: Optional[DocumentationResult]) -> float:
        """Calculate overall documentation score"""
        if not documentation_result:
            return 0.0
            
        scores = []
        for metric in documentation_result.metrics.values():
            if metric.status == "good":
                scores.append(1.0)
            elif metric.status == "warning":
                scores.append(0.7)
            elif metric.status == "critical":
                scores.append(0.3)
            else:
                scores.append(0.0)
                
        return sum(scores) / len(scores) if scores else 0.0
        
    def _calculate_accessibility_score(self, accessibility_result: Optional[AccessibilityResult]) -> float:
        """Calculate overall accessibility score"""
        if not accessibility_result:
            return 0.0
            
        scores = []
        for metric in accessibility_result.metrics.values():
            if metric.status == "good":
                scores.append(1.0)
            elif metric.status == "warning":
                scores.append(0.7)
            elif metric.status == "critical":
                scores.append(0.3)
            else:
                scores.append(0.0)
                
        return sum(scores) / len(scores) if scores else 0.0
        
    def get_accessibility_summary(self) -> Dict[str, Any]:
        """Get accessibility analysis summary"""
        accessibility_results = [
            result for result in self.analysis_history
            if result.accessibility_analysis
        ]
        
        if not accessibility_results:
            return {}
            
        latest = accessibility_results[-1]
        return {
            "accessibility_type": latest.accessibility_analysis.accessibility_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.accessibility_analysis.metrics.items()
            },
            "issue_count": len(latest.accessibility_analysis.issues),
            "recommendation_count": len(latest.accessibility_analysis.recommendations)
        }
        
    def analyze_internationalization(
        self,
        code: str,
        file_path: str,
        internationalization_type: InternationalizationType,
        context: Optional[Dict[str, Any]] = None
    ) -> UnifiedAnalysisResult:
        """Analyze internationalization"""
        try:
            result = self.internationalization_analyzer.analyze_internationalization(
                code,
                file_path,
                internationalization_type,
                context
            )
            
            # Store in history
            self.analysis_history.append(result)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to analyze internationalization: {str(e)}")
        
    def _initialize_patterns(self):
        """Initialize analysis detection patterns"""
        # Model architecture patterns
        self.analysis_patterns["model_architecture"] = [
            {
                "pattern": r"class\s+\w+\([^)]*\):",
                "severity": "info",
                "description": "Class definition detected",
                "recommendation": "Review class architecture"
            },
            {
                "pattern": r"def\s+\w+\([^)]*\):",
                "severity": "info",
                "description": "Method definition detected",
                "recommendation": "Review method implementation"
            }
        ]
        
        # Test patterns
        self.analysis_patterns["test"] = [
            {
                "pattern": r"def\s+test_\w+\([^)]*\):",
                "severity": "info",
                "description": "Test method detected",
                "recommendation": "Review test implementation"
            },
            {
                "pattern": r"assert\s+[^:]+:",
                "severity": "info",
                "description": "Assertion detected",
                "recommendation": "Review test assertions"
            }
        ]
        
        # Dependency patterns
        self.analysis_patterns["dependency"] = [
            {
                "pattern": r"import\s+[^:]+:",
                "severity": "info",
                "description": "Import statement detected",
                "recommendation": "Review dependencies"
            },
            {
                "pattern": r"from\s+[^:]+:",
                "severity": "info",
                "description": "From import detected",
                "recommendation": "Review dependencies"
            }
        ]
        
        # Documentation patterns
        self.analysis_patterns["documentation"] = [
            {
                "pattern": r'"""[^"]*"""',
                "severity": "info",
                "description": "Docstring detected",
                "recommendation": "Review documentation"
            },
            {
                "pattern": r"#\s+[^:]+:",
                "severity": "info",
                "description": "Comment detected",
                "recommendation": "Review documentation"
            }
        ]
        
        # Routing patterns
        self.analysis_patterns["routing"] = [
            {
                "pattern": r"@app\.route\([^)]+\)",
                "severity": "info",
                "description": "Route decorator detected",
                "recommendation": "Review routing"
            },
            {
                "pattern": r"@router\.get\([^)]+\)",
                "severity": "info",
                "description": "Router method detected",
                "recommendation": "Review routing"
            }
        ]
        
        # Accessibility patterns
        self.analysis_patterns["accessibility"] = [
            {
                "pattern": r"aria-[^=]+=[^>]+",
                "severity": "info",
                "description": "ARIA attribute detected",
                "recommendation": "Review accessibility"
            },
            {
                "pattern": r"role=[^>]+",
                "severity": "info",
                "description": "Role attribute detected",
                "recommendation": "Review accessibility"
            }
        ]
        
        # Internationalization patterns
        self.analysis_patterns["internationalization"] = [
            {
                "pattern": r"gettext\(['\"]([^'\"]+)['\"]\)",
                "severity": "info",
                "description": "Translation function detected",
                "recommendation": "Review translation implementation"
            },
            {
                "pattern": r"locale\.setlocale\([^)]+\)",
                "severity": "info",
                "description": "Locale setting detected",
                "recommendation": "Review locale handling"
            }
        ]
        
    def _initialize_analysis_rules(self):
        """Initialize analysis rules"""
        self.analysis_rules = {
            AnalysisType.MODEL_ARCHITECTURE: [
                {
                    "name": "model_complexity",
                    "threshold": 0.8,
                    "description": "Model complexity score"
                },
                {
                    "name": "model_cohesion",
                    "threshold": 0.8,
                    "description": "Model cohesion score"
                },
                {
                    "name": "model_coupling",
                    "threshold": 0.8,
                    "description": "Model coupling score"
                }
            ],
            AnalysisType.TEST: [
                {
                    "name": "test_coverage",
                    "threshold": 0.8,
                    "description": "Test coverage score"
                },
                {
                    "name": "test_quality",
                    "threshold": 0.8,
                    "description": "Test quality score"
                },
                {
                    "name": "test_maintainability",
                    "threshold": 0.8,
                    "description": "Test maintainability score"
                }
            ],
            AnalysisType.DEPENDENCY: [
                {
                    "name": "dependency_management",
                    "threshold": 0.8,
                    "description": "Dependency management score"
                },
                {
                    "name": "dependency_security",
                    "threshold": 0.8,
                    "description": "Dependency security score"
                },
                {
                    "name": "dependency_optimization",
                    "threshold": 0.8,
                    "description": "Dependency optimization score"
                }
            ],
            AnalysisType.DOCUMENTATION: [
                {
                    "name": "documentation_coverage",
                    "threshold": 0.8,
                    "description": "Documentation coverage score"
                },
                {
                    "name": "documentation_quality",
                    "threshold": 0.8,
                    "description": "Documentation quality score"
                },
                {
                    "name": "documentation_maintainability",
                    "threshold": 0.8,
                    "description": "Documentation maintainability score"
                }
            ],
            AnalysisType.ROUTING: [
                {
                    "name": "routing_coverage",
                    "threshold": 0.8,
                    "description": "Routing coverage score"
                },
                {
                    "name": "routing_quality",
                    "threshold": 0.8,
                    "description": "Routing quality score"
                },
                {
                    "name": "routing_security",
                    "threshold": 0.8,
                    "description": "Routing security score"
                }
            ],
            AnalysisType.ACCESSIBILITY: [
                {
                    "name": "accessibility_coverage",
                    "threshold": 0.8,
                    "description": "Accessibility coverage score"
                },
                {
                    "name": "accessibility_quality",
                    "threshold": 0.8,
                    "description": "Accessibility quality score"
                },
                {
                    "name": "accessibility_compliance",
                    "threshold": 0.8,
                    "description": "Accessibility compliance score"
                }
            ],
            AnalysisType.INTERNATIONALIZATION: [
                {
                    "name": "internationalization_coverage",
                    "threshold": 0.8,
                    "description": "Internationalization coverage score"
                },
                {
                    "name": "internationalization_quality",
                    "threshold": 0.8,
                    "description": "Internationalization quality score"
                },
                {
                    "name": "internationalization_compliance",
                    "threshold": 0.8,
                    "description": "Internationalization compliance score"
                }
            ]
        } 