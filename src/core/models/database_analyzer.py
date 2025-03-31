from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import logging
from datetime import datetime
from enum import Enum
import ast
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Types of database analysis"""
    QUERY = "query"
    SCHEMA = "schema"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MIGRATION = "migration"
    CONNECTION = "connection"

class DatabaseMetric(BaseModel):
    """Database metric"""
    name: str
    value: float
    threshold: float
    status: str
    details: Dict[str, Any] = {}
    recommendations: List[str] = []

class DatabaseResult(BaseModel):
    """Result of database analysis"""
    database_type: DatabaseType
    metrics: Dict[str, DatabaseMetric]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

@dataclass
class DatabaseQuery:
    """Information about a database query"""
    query_type: str
    table: str
    complexity: float
    performance_impact: float
    security_risk: float
    line_number: int
    column: int
    context: Optional[Dict[str, Any]] = None

class DatabaseAnalyzer:
    """Analyzer for assessing and improving database-related code"""
    
    def __init__(self):
        self.analysis_history: List[DatabaseResult] = []
        self.db_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.analysis_metrics: Dict[str, Dict[str, float]] = {}
        self._initialize_patterns()
        self._initialize_database_rules()
        
    def _initialize_patterns(self):
        """Initialize database detection patterns"""
        # Query patterns
        self.db_patterns["query"] = [
            {
                "pattern": r"SELECT\s+\*\s+FROM",
                "severity": "warning",
                "description": "SELECT * query detected",
                "recommendation": "Specify required columns instead of using SELECT *"
            },
            {
                "pattern": r"WHERE\s+1\s*=\s*1",
                "severity": "warning",
                "description": "Always true WHERE clause detected",
                "recommendation": "Remove unnecessary WHERE clause"
            }
        ]
        
        # Schema patterns
        self.db_patterns["schema"] = [
            {
                "pattern": r"CREATE\s+TABLE",
                "severity": "info",
                "description": "Table creation detected",
                "recommendation": "Consider adding appropriate indexes"
            },
            {
                "pattern": r"ALTER\s+TABLE",
                "severity": "info",
                "description": "Table modification detected",
                "recommendation": "Review impact on existing data"
            }
        ]
        
        # Performance patterns
        self.db_patterns["performance"] = [
            {
                "pattern": r"JOIN\s+.*\s+JOIN",
                "severity": "warning",
                "description": "Multiple JOINs detected",
                "recommendation": "Consider optimizing query with better JOIN strategy"
            },
            {
                "pattern": r"ORDER\s+BY\s+.*\s+DESC",
                "severity": "warning",
                "description": "DESC ordering detected",
                "recommendation": "Consider using appropriate index for DESC ordering"
            }
        ]
        
        # Security patterns
        self.db_patterns["security"] = [
            {
                "pattern": r"exec\s*\(",
                "severity": "critical",
                "description": "SQL execution detected",
                "recommendation": "Use parameterized queries to prevent SQL injection"
            },
            {
                "pattern": r"password\s*=\s*['\"].*['\"]",
                "severity": "critical",
                "description": "Hardcoded password detected",
                "recommendation": "Use environment variables or secure configuration"
            }
        ]
        
        # Migration patterns
        self.db_patterns["migration"] = [
            {
                "pattern": r"DROP\s+TABLE",
                "severity": "warning",
                "description": "Table drop detected",
                "recommendation": "Consider using soft delete instead"
            },
            {
                "pattern": r"TRUNCATE\s+TABLE",
                "severity": "warning",
                "description": "Table truncate detected",
                "recommendation": "Ensure data backup before truncate"
            }
        ]
        
        # Connection patterns
        self.db_patterns["connection"] = [
            {
                "pattern": r"connection\.close\s*\(",
                "severity": "warning",
                "description": "Manual connection close detected",
                "recommendation": "Use context managers for connection handling"
            },
            {
                "pattern": r"pool\.acquire\s*\(",
                "severity": "info",
                "description": "Connection pool usage detected",
                "recommendation": "Review pool size configuration"
            }
        ]
        
    def _initialize_database_rules(self):
        """Initialize database rules"""
        self.database_rules = {
            DatabaseType.QUERY: [
                {
                    "name": "query_complexity",
                    "threshold": 0.8,
                    "description": "Query complexity score"
                },
                {
                    "name": "query_efficiency",
                    "threshold": 0.8,
                    "description": "Query efficiency score"
                },
                {
                    "name": "query_optimization",
                    "threshold": 0.7,
                    "description": "Query optimization score"
                }
            ],
            DatabaseType.SCHEMA: [
                {
                    "name": "schema_design",
                    "threshold": 0.8,
                    "description": "Schema design score"
                },
                {
                    "name": "index_usage",
                    "threshold": 0.8,
                    "description": "Index usage score"
                },
                {
                    "name": "normalization",
                    "threshold": 0.7,
                    "description": "Schema normalization score"
                }
            ],
            DatabaseType.PERFORMANCE: [
                {
                    "name": "query_performance",
                    "threshold": 0.8,
                    "description": "Query performance score"
                },
                {
                    "name": "connection_pooling",
                    "threshold": 0.8,
                    "description": "Connection pooling score"
                },
                {
                    "name": "resource_usage",
                    "threshold": 0.7,
                    "description": "Resource usage efficiency score"
                }
            ],
            DatabaseType.SECURITY: [
                {
                    "name": "sql_injection",
                    "threshold": 0.8,
                    "description": "SQL injection prevention score"
                },
                {
                    "name": "access_control",
                    "threshold": 0.8,
                    "description": "Access control implementation score"
                },
                {
                    "name": "data_encryption",
                    "threshold": 0.7,
                    "description": "Data encryption score"
                }
            ],
            DatabaseType.MIGRATION: [
                {
                    "name": "migration_safety",
                    "threshold": 0.8,
                    "description": "Migration safety score"
                },
                {
                    "name": "backup_strategy",
                    "threshold": 0.8,
                    "description": "Backup strategy score"
                },
                {
                    "name": "rollback_plan",
                    "threshold": 0.7,
                    "description": "Rollback plan score"
                }
            ],
            DatabaseType.CONNECTION: [
                {
                    "name": "connection_management",
                    "threshold": 0.8,
                    "description": "Connection management score"
                },
                {
                    "name": "error_handling",
                    "threshold": 0.8,
                    "description": "Connection error handling score"
                },
                {
                    "name": "connection_pooling",
                    "threshold": 0.7,
                    "description": "Connection pooling implementation score"
                }
            ]
        }
        
    def analyze_database(
        self,
        code: str,
        file_path: str,
        database_type: DatabaseType,
        context: Optional[Dict[str, Any]] = None
    ) -> DatabaseResult:
        """Analyze database code based on specified type"""
        try:
            # Initialize result
            result = DatabaseResult(
                database_type=database_type,
                metrics={},
                issues=[],
                recommendations=[],
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "file_path": file_path,
                    "context": context or {}
                }
            )
            
            # Get database rules for type
            rules = self.database_rules.get(database_type, [])
            
            # Parse code
            tree = ast.parse(code)
            
            # Perform analysis
            for rule in rules:
                metric = self._analyze_database_metric(
                    rule["name"],
                    code,
                    tree,
                    rule["threshold"],
                    context
                )
                result.metrics[rule["name"]] = metric
                
                # Check for issues
                if metric.status != "good":
                    result.issues.append({
                        "metric": rule["name"],
                        "value": metric.value,
                        "threshold": rule["threshold"],
                        "status": metric.status,
                        "description": rule["description"]
                    })
                    
                # Add recommendations
                result.recommendations.extend(metric.recommendations)
                
            # Generate cross-metric recommendations
            result.recommendations.extend(
                self._generate_cross_metric_recommendations(result.metrics)
            )
            
            # Store in history
            self.analysis_history.append(result)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to analyze database code: {str(e)}")
            
    def _analyze_database_metric(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        threshold: float,
        context: Optional[Dict[str, Any]] = None
    ) -> DatabaseMetric:
        """Analyze specific database metric"""
        try:
            # Calculate metric value
            value = self._calculate_metric_value(
                metric_name,
                code,
                tree,
                context
            )
            
            # Determine status
            status = self._determine_metric_status(value, threshold)
            
            # Generate recommendations
            recommendations = self._generate_metric_recommendations(
                metric_name,
                value,
                threshold,
                status
            )
            
            return DatabaseMetric(
                name=metric_name,
                value=value,
                threshold=threshold,
                status=status,
                details={
                    "code": code,
                    "context": context
                },
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze database metric {metric_name}: {str(e)}")
            return DatabaseMetric(
                name=metric_name,
                value=0.0,
                threshold=threshold,
                status="error",
                details={"error": str(e)},
                recommendations=["Fix database analysis error"]
            )
            
    def _calculate_metric_value(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate metric value"""
        if metric_name == "query_complexity":
            return self._calculate_query_complexity(code, tree)
        elif metric_name == "query_efficiency":
            return self._calculate_query_efficiency(code, tree)
        elif metric_name == "query_optimization":
            return self._calculate_query_optimization(code, tree)
        elif metric_name == "schema_design":
            return self._calculate_schema_design(code, tree)
        elif metric_name == "index_usage":
            return self._calculate_index_usage(code, tree)
        elif metric_name == "normalization":
            return self._calculate_normalization(code, tree)
        elif metric_name == "query_performance":
            return self._calculate_query_performance(code, tree)
        elif metric_name == "connection_pooling":
            return self._calculate_connection_pooling(code, tree)
        elif metric_name == "resource_usage":
            return self._calculate_resource_usage(code, tree)
        elif metric_name == "sql_injection":
            return self._calculate_sql_injection(code, tree)
        elif metric_name == "access_control":
            return self._calculate_access_control(code, tree)
        elif metric_name == "data_encryption":
            return self._calculate_data_encryption(code, tree)
        elif metric_name == "migration_safety":
            return self._calculate_migration_safety(code, tree)
        elif metric_name == "backup_strategy":
            return self._calculate_backup_strategy(code, tree)
        elif metric_name == "rollback_plan":
            return self._calculate_rollback_plan(code, tree)
        elif metric_name == "connection_management":
            return self._calculate_connection_management(code, tree)
        elif metric_name == "error_handling":
            return self._calculate_error_handling(code, tree)
        else:
            raise ValueError(f"Unknown metric: {metric_name}")
            
    def _determine_metric_status(self, value: float, threshold: float) -> str:
        """Determine metric status based on value and threshold"""
        if value >= threshold:
            return "good"
        elif value >= threshold * 0.8:
            return "warning"
        else:
            return "critical"
            
    def _generate_metric_recommendations(
        self,
        metric_name: str,
        value: float,
        threshold: float,
        status: str
    ) -> List[str]:
        """Generate recommendations for metric"""
        recommendations = []
        
        if status == "warning":
            recommendations.append(
                f"{metric_name} is slightly below threshold. Consider improving "
                f"database implementation."
            )
        elif status == "critical":
            recommendations.append(
                f"{metric_name} is significantly below threshold. Immediate "
                f"database improvements are recommended."
            )
            
        # Add specific recommendations based on metric
        if "query" in metric_name and value < threshold:
            recommendations.append(
                "Query issues detected. Consider optimizing queries and improving "
                "query patterns."
            )
        elif "schema" in metric_name and value < threshold:
            recommendations.append(
                "Schema issues detected. Review database schema design and "
                "normalization."
            )
        elif "performance" in metric_name and value < threshold:
            recommendations.append(
                "Performance issues detected. Consider implementing better "
                "performance optimizations."
            )
        elif "security" in metric_name and value < threshold:
            recommendations.append(
                "Security issues detected. Implement proper security controls "
                "and best practices."
            )
        elif "migration" in metric_name and value < threshold:
            recommendations.append(
                "Migration issues detected. Review migration strategy and "
                "backup procedures."
            )
        elif "connection" in metric_name and value < threshold:
            recommendations.append(
                "Connection issues detected. Improve connection management "
                "and error handling."
            )
            
        return recommendations
        
    def _generate_cross_metric_recommendations(
        self,
        metrics: Dict[str, DatabaseMetric]
    ) -> List[str]:
        """Generate recommendations based on multiple metrics"""
        recommendations = []
        
        # Check for multiple database issues
        db_metrics = [
            m for n, m in metrics.items()
            if any(p in n for p in ["query", "schema", "performance"])
        ]
        if len(db_metrics) > 1 and all(m.status == "critical" for m in db_metrics):
            recommendations.append(
                "Multiple critical database issues detected. Consider comprehensive "
                "database improvements."
            )
            
        # Check for security and performance issues
        if ("sql_injection" in metrics and "query_performance" in metrics and
            metrics["sql_injection"].status == "critical" and
            metrics["query_performance"].status == "critical"):
            recommendations.append(
                "Critical security and performance issues detected. Consider "
                "implementing better security controls and performance optimizations."
            )
            
        # Check for schema and migration issues
        if ("schema_design" in metrics and "migration_safety" in metrics and
            metrics["schema_design"].status == "critical" and
            metrics["migration_safety"].status == "critical"):
            recommendations.append(
                "Critical schema and migration issues detected. Review database "
                "schema design and migration strategy."
            )
            
        return recommendations
        
    def get_analysis_history(self) -> List[DatabaseResult]:
        """Get analysis history"""
        return self.analysis_history
        
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        if not self.analysis_history:
            return {}
            
        latest = self.analysis_history[-1]
        return {
            "database_type": latest.database_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.metrics.items()
            },
            "issue_count": len(latest.issues),
            "recommendation_count": len(latest.recommendations)
        }
        
    def get_database_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get registered database patterns"""
        return self.db_patterns
        
    def get_analysis_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get database analysis metrics"""
        return self.analysis_metrics
        
    def register_database_pattern(
        self,
        issue_type: str,
        pattern: str,
        severity: str,
        description: str,
        recommendation: str
    ):
        """Register a new database pattern"""
        if issue_type not in self.db_patterns:
            self.db_patterns[issue_type] = []
            
        self.db_patterns[issue_type].append({
            "pattern": pattern,
            "severity": severity,
            "description": description,
            "recommendation": recommendation
        })
        
    # Metric calculation methods
    def _calculate_query_complexity(self, code: str, tree: ast.AST) -> float:
        """Calculate query complexity score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_query_efficiency(self, code: str, tree: ast.AST) -> float:
        """Calculate query efficiency score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_query_optimization(self, code: str, tree: ast.AST) -> float:
        """Calculate query optimization score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_schema_design(self, code: str, tree: ast.AST) -> float:
        """Calculate schema design score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_index_usage(self, code: str, tree: ast.AST) -> float:
        """Calculate index usage score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_normalization(self, code: str, tree: ast.AST) -> float:
        """Calculate normalization score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_query_performance(self, code: str, tree: ast.AST) -> float:
        """Calculate query performance score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_connection_pooling(self, code: str, tree: ast.AST) -> float:
        """Calculate connection pooling score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_resource_usage(self, code: str, tree: ast.AST) -> float:
        """Calculate resource usage efficiency score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_sql_injection(self, code: str, tree: ast.AST) -> float:
        """Calculate SQL injection prevention score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_access_control(self, code: str, tree: ast.AST) -> float:
        """Calculate access control implementation score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_data_encryption(self, code: str, tree: ast.AST) -> float:
        """Calculate data encryption score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_migration_safety(self, code: str, tree: ast.AST) -> float:
        """Calculate migration safety score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_backup_strategy(self, code: str, tree: ast.AST) -> float:
        """Calculate backup strategy score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_rollback_plan(self, code: str, tree: ast.AST) -> float:
        """Calculate rollback plan score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_connection_management(self, code: str, tree: ast.AST) -> float:
        """Calculate connection management score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_error_handling(self, code: str, tree: ast.AST) -> float:
        """Calculate error handling score"""
        # Implementation depends on the specific requirements
        return 0.8 