from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from .ast_parser import ASTParser, ASTAnalysisResult
from .security_analyzer import SecurityAnalyzer, SecurityAnalysisResult
from .code_generation_model import CodeGenerationModel, CodeGenerationResult

class OptimizationResult(BaseModel):
    """Result of code optimization"""
    original_code: str
    optimized_code: str
    improvements: List[str]
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    optimization_level: str
    metadata: Dict[str, Any] = {}

class OptimizationManager:
    """Manager for coordinating code optimization across components"""
    
    def __init__(self):
        self.ast_parser = ASTParser()
        self.security_analyzer = SecurityAnalyzer()
        self.code_generator = CodeGenerationModel(None)  # Model router not needed for optimization
        self.optimization_history: List[OptimizationResult] = []
        
    async def optimize_code(
        self,
        code: str,
        optimization_level: str = "balanced",
        context: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """Optimize code using multiple components"""
        try:
            # Initialize result
            result = OptimizationResult(
                original_code=code,
                optimized_code=code,
                improvements=[],
                metrics_before={},
                metrics_after={},
                optimization_level=optimization_level,
                metadata={
                    "optimized_at": datetime.now().isoformat(),
                    "context": context or {}
                }
            )
            
            # Analyze original code
            ast_analysis = self.ast_parser.parse_code(code)
            security_analysis = self.security_analyzer.analyze_code(code)
            
            # Calculate initial metrics
            result.metrics_before = self._calculate_metrics(
                code, ast_analysis, security_analysis
            )
            
            # Apply optimizations based on level
            optimized_code = code
            improvements = []
            
            if optimization_level in ["balanced", "aggressive"]:
                # Apply AST-based optimizations
                ast_optimizations = self._apply_ast_optimizations(code, ast_analysis)
                if ast_optimizations["improved"]:
                    optimized_code = ast_optimizations["code"]
                    improvements.extend(ast_optimizations["improvements"])
                    
                # Apply security optimizations
                security_optimizations = self._apply_security_optimizations(
                    optimized_code, security_analysis
                )
                if security_optimizations["improved"]:
                    optimized_code = security_optimizations["code"]
                    improvements.extend(security_optimizations["improvements"])
                    
            if optimization_level == "aggressive":
                # Apply additional aggressive optimizations
                aggressive_optimizations = self._apply_aggressive_optimizations(
                    optimized_code, ast_analysis
                )
                if aggressive_optimizations["improved"]:
                    optimized_code = aggressive_optimizations["code"]
                    improvements.extend(aggressive_optimizations["improvements"])
                    
            # Analyze optimized code
            optimized_ast_analysis = self.ast_parser.parse_code(optimized_code)
            optimized_security_analysis = self.security_analyzer.analyze_code(optimized_code)
            
            # Calculate final metrics
            result.metrics_after = self._calculate_metrics(
                optimized_code,
                optimized_ast_analysis,
                optimized_security_analysis
            )
            
            # Update result
            result.optimized_code = optimized_code
            result.improvements = improvements
            
            # Store in history
            self.optimization_history.append(result)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to optimize code: {str(e)}")
            
    def _calculate_metrics(
        self,
        code: str,
        ast_analysis: ASTAnalysisResult,
        security_analysis: SecurityAnalysisResult
    ) -> Dict[str, float]:
        """Calculate comprehensive code metrics"""
        return {
            "complexity": ast_analysis.metrics.get("complexity", 0),
            "maintainability": ast_analysis.metrics.get("maintainability", 0),
            "security_risk": security_analysis.risk_score,
            "code_size": len(code),
            "line_count": code.count("\n") + 1,
            "quality_score": ast_analysis.metrics.get("quality_score", 0)
        }
        
    def _apply_ast_optimizations(
        self,
        code: str,
        ast_analysis: ASTAnalysisResult
    ) -> Dict[str, Any]:
        """Apply AST-based optimizations"""
        improvements = []
        optimized_code = code
        
        # Remove unused imports
        if ast_analysis.imports:
            optimized_code = self.ast_parser.optimize_code(
                optimized_code,
                rules=["remove_unused_imports"]
            )
            improvements.append("Removed unused imports")
            
        # Optimize loops
        if ast_analysis.metrics.get("loop_count", 0) > 0:
            optimized_code = self.ast_parser.optimize_code(
                optimized_code,
                rules=["optimize_loops"]
            )
            improvements.append("Optimized loop structures")
            
        # Optimize function calls
        if ast_analysis.metrics.get("function_call_count", 0) > 0:
            optimized_code = self.ast_parser.optimize_code(
                optimized_code,
                rules=["optimize_function_calls"]
            )
            improvements.append("Optimized function calls")
            
        return {
            "improved": len(improvements) > 0,
            "code": optimized_code,
            "improvements": improvements
        }
        
    def _apply_security_optimizations(
        self,
        code: str,
        security_analysis: SecurityAnalysisResult
    ) -> Dict[str, Any]:
        """Apply security-based optimizations"""
        improvements = []
        optimized_code = code
        
        # Fix critical vulnerabilities
        for vuln in security_analysis.vulnerabilities:
            if vuln.severity == "CRITICAL":
                optimized_code = self.security_analyzer.fix_vulnerability(
                    optimized_code,
                    vuln
                )
                improvements.append(f"Fixed critical vulnerability: {vuln.description}")
                
        # Fix high severity vulnerabilities
        for vuln in security_analysis.vulnerabilities:
            if vuln.severity == "HIGH":
                optimized_code = self.security_analyzer.fix_vulnerability(
                    optimized_code,
                    vuln
                )
                improvements.append(f"Fixed high severity vulnerability: {vuln.description}")
                
        return {
            "improved": len(improvements) > 0,
            "code": optimized_code,
            "improvements": improvements
        }
        
    def _apply_aggressive_optimizations(
        self,
        code: str,
        ast_analysis: ASTAnalysisResult
    ) -> Dict[str, Any]:
        """Apply aggressive optimizations"""
        improvements = []
        optimized_code = code
        
        # Optimize memory usage
        if ast_analysis.metrics.get("memory_usage", 0) > 1000:
            optimized_code = self.ast_parser.optimize_code(
                optimized_code,
                rules=["optimize_memory_usage"]
            )
            improvements.append("Optimized memory usage")
            
        # Optimize CPU usage
        if ast_analysis.metrics.get("cpu_usage", 0) > 80:
            optimized_code = self.ast_parser.optimize_code(
                optimized_code,
                rules=["optimize_cpu_usage"]
            )
            improvements.append("Optimized CPU usage")
            
        # Optimize I/O operations
        if ast_analysis.metrics.get("io_operation_count", 0) > 10:
            optimized_code = self.ast_parser.optimize_code(
                optimized_code,
                rules=["optimize_io_operations"]
            )
            improvements.append("Optimized I/O operations")
            
        return {
            "improved": len(improvements) > 0,
            "code": optimized_code,
            "improvements": improvements
        }
        
    def get_optimization_history(self) -> List[OptimizationResult]:
        """Get optimization history"""
        return self.optimization_history
        
    def get_optimization_stats(self) -> Dict[str, float]:
        """Get optimization statistics"""
        if not self.optimization_history:
            return {}
            
        total_improvements = sum(len(r.improvements) for r in self.optimization_history)
        avg_complexity_reduction = sum(
            r.metrics_before["complexity"] - r.metrics_after["complexity"]
            for r in self.optimization_history
        ) / len(self.optimization_history)
        
        avg_security_improvement = sum(
            r.metrics_before["security_risk"] - r.metrics_after["security_risk"]
            for r in self.optimization_history
        ) / len(self.optimization_history)
        
        return {
            "total_optimizations": len(self.optimization_history),
            "total_improvements": total_improvements,
            "avg_complexity_reduction": avg_complexity_reduction,
            "avg_security_improvement": avg_security_improvement
        } 