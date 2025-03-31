from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import os

from ...core.base_agent import BaseAgent
from ...core.provider_registry import ProviderRegistry
from ...core.version_control import VersionControlManager
from ...core.solution_generator import MultiSolutionGenerator
from ...core.fix_system import ContextAwareFixSystem
from ...core.code_modifier import SafeCodeModifier
from ...services.voice.voice_processor import VoiceProcessor
from ...services.voice.ios_voice_processor import IOSVoiceProcessor
from ..knowledge.ios_knowledge_manager import IOSKnowledgeManager
from ..knowledge.pattern_matcher import PatternMatcher
from .ios_developer_collaboration import IOSDeveloperCollaboration
from .ios_external_services import IOSExternalServices
from .ios_integration_layer import IOSIntegrationLayer

logger = logging.getLogger(__name__)

class IOSDeveloperAgent(BaseAgent):
    """iOS Developer Agent for handling iOS development tasks"""
    
    def __init__(self, project_dir: str):
        super().__init__()
        self.project_dir = project_dir
        self.provider_registry = ProviderRegistry()
        self.version_control = VersionControlManager(project_dir)
        self.solution_generator = MultiSolutionGenerator()
        self.fix_system = ContextAwareFixSystem()
        self.code_modifier = SafeCodeModifier()
        self.voice_processor = IOSVoiceProcessor()
        self.collaboration = IOSDeveloperCollaboration(self)
        self.external_services = IOSExternalServices()
        self.knowledge_manager = IOSKnowledgeManager()
        self.pattern_matcher = PatternMatcher()
        self.integration_layer = IOSIntegrationLayer()
        
        # Initialize metrics
        self.metrics = {
            "tasks_processed": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_processing_time": 0.0,
            "last_task": None,
            "documentation_coverage": 0.0,
            "test_coverage": 0.0,
            "code_quality_score": 0.0,
            "knowledge_base": {
                "patterns_loaded": 0,
                "patterns_matched": 0,
                "knowledge_queries": 0,
                "knowledge_hits": 0
            },
            "external_services": {
                "app_store": {"submissions": 0, "success": 0},
                "provisioning": {"profiles": 0, "success": 0},
                "analytics": {"events": 0, "success": 0},
                "crash_reporting": {"reports": 0, "success": 0}
            },
            "integration": {
                "initialized": False,
                "last_initialization": None,
                "build_count": 0,
                "package_updates": 0,
                "ci_runs": 0,
                "reviews_completed": 0,
                "resources_managed": 0,
                "assets_processed": 0
            }
        }
        
        # Initialize task history
        self.task_history = []
    
    async def initialize(self) -> None:
        """Initialize the agent and its components"""
        try:
            # Initialize core components
            await self.provider_registry.initialize()
            await self.version_control.initialize()
            await self.solution_generator.initialize()
            await self.fix_system.initialize()
            await self.code_modifier.initialize()
            await self.voice_processor.initialize()
            
            # Initialize collaboration system
            await self.collaboration.initialize()
            
            # Initialize external services
            await self.external_services.initialize()
            
            # Initialize knowledge base
            await self.knowledge_manager.initialize()
            await self.pattern_matcher.initialize()
            
            # Initialize integration layer
            await self.integration_layer.initialize()
            
            # Load iOS-specific patterns
            await self._load_ios_patterns()
            
            # Update integration metrics
            self.metrics["integration"]["initialized"] = True
            self.metrics["integration"]["last_initialization"] = datetime.now()
            
            logger.info("iOS Developer Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize iOS Developer Agent: {str(e)}")
            raise
    
    async def _load_ios_patterns(self) -> None:
        """Load iOS-specific patterns into the pattern matcher"""
        try:
            # Load SwiftUI patterns
            await self.pattern_matcher.load_patterns(
                pattern_type="swiftui",
                patterns=await self.knowledge_manager.get_swiftui_patterns()
            )
            
            # Load UIKit patterns
            await self.pattern_matcher.load_patterns(
                pattern_type="uikit",
                patterns=await self.knowledge_manager.get_uikit_patterns()
            )
            
            # Load architecture patterns
            await self.pattern_matcher.load_patterns(
                pattern_type="architecture",
                patterns=await self.knowledge_manager.get_architecture_patterns()
            )
            
            # Update metrics
            self.metrics["knowledge_base"]["patterns_loaded"] = (
                len(await self.pattern_matcher.get_patterns("swiftui")) +
                len(await self.pattern_matcher.get_patterns("uikit")) +
                len(await self.pattern_matcher.get_patterns("architecture"))
            )
            
        except Exception as e:
            logger.error(f"Failed to load iOS patterns: {str(e)}")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a development task"""
        try:
            # Record task start
            self._record_task_start(task)
            
            # Update metrics
            self.metrics["tasks_processed"] += 1
            start_time = datetime.now()
            
            # Validate required providers
            required_providers = self._get_required_providers(task)
            if not await self._validate_providers(required_providers):
                raise ValueError("Required providers not available")
            
            # Process task based on type
            result = await self._process_task_by_type(task)
            
            # Update metrics
            self.metrics["last_task"] = datetime.now()
            processing_time = (self.metrics["last_task"] - start_time).total_seconds()
            self.metrics["average_processing_time"] = (
                (self.metrics["average_processing_time"] * (self.metrics["tasks_processed"] - 1) +
                 processing_time) / self.metrics["tasks_processed"]
            )
            
            if result.get("success", False):
                self.metrics["successful_tasks"] += 1
                self._record_task_completion(task, result)
            else:
                self.metrics["failed_tasks"] += 1
                self._record_task_failure(task, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Task processing failed: {str(e)}")
            self.metrics["failed_tasks"] += 1
            self._record_task_failure(task, {"error": str(e)})
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def collaborate(self, other_agent: BaseAgent, task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with another agent on a task"""
        return await self.collaboration.collaborate(other_agent, task)
    
    async def submit_to_app_store(self, build_config: Dict[str, Any]) -> Dict[str, Any]:
        """Submit app to App Store"""
        try:
            # Update metrics
            self.metrics["external_services"]["app_store"]["submissions"] += 1
            
            # Submit to App Store
            result = await self.external_services.submit_to_app_store(build_config)
            
            # Update metrics
            if result.get("success", False):
                self.metrics["external_services"]["app_store"]["success"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"App Store submission failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def manage_provisioning(self, profile_config: Dict[str, Any]) -> Dict[str, Any]:
        """Manage provisioning profiles and certificates"""
        try:
            # Update metrics
            self.metrics["external_services"]["provisioning"]["profiles"] += 1
            
            # Manage provisioning
            result = await self.external_services.manage_provisioning(profile_config)
            
            # Update metrics
            if result.get("success", False):
                self.metrics["external_services"]["provisioning"]["success"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Provisioning management failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def track_analytics(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track analytics events"""
        try:
            # Update metrics
            self.metrics["external_services"]["analytics"]["events"] += 1
            
            # Track analytics
            result = await self.external_services.track_analytics(event_data)
            
            # Update metrics
            if result.get("success", False):
                self.metrics["external_services"]["analytics"]["success"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Analytics tracking failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def report_crash(self, crash_data: Dict[str, Any]) -> Dict[str, Any]:
        """Report app crash"""
        try:
            # Update metrics
            self.metrics["external_services"]["crash_reporting"]["reports"] += 1
            
            # Report crash
            result = await self.external_services.report_crash(crash_data)
            
            # Update metrics
            if result.get("success", False):
                self.metrics["external_services"]["crash_reporting"]["success"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Crash reporting failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def get_knowledge_status(self) -> Dict[str, Any]:
        """Get the current status of the knowledge base"""
        return {
            "patterns_loaded": self.metrics["knowledge_base"]["patterns_loaded"],
            "patterns_matched": self.metrics["knowledge_base"]["patterns_matched"],
            "knowledge_queries": self.metrics["knowledge_base"]["knowledge_queries"],
            "knowledge_hits": self.metrics["knowledge_base"]["knowledge_hits"],
            "pattern_types": await self.pattern_matcher.get_pattern_types(),
            "knowledge_categories": await self.knowledge_manager.get_categories(),
            "timestamp": datetime.now()
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent"""
        return {
            "metrics": self.metrics,
            "task_history": self.task_history,
            "collaboration_metrics": await self.collaboration.get_collaboration_metrics(),
            "external_services_metrics": await self.external_services.get_metrics(),
            "knowledge_status": await self.get_knowledge_status(),
            "integration_status": await self.integration_layer.get_status(),
            "timestamp": datetime.now()
        }
    
    def _get_required_providers(self, task: Dict[str, Any]) -> List[str]:
        """Get the list of required providers for a task"""
        task_type = task.get("type", "")
        provider_map = {
            "create_project": ["project_creator", "dependency_manager"],
            "generate_code": ["code_generator", "linter"],
            "implement_swiftui": ["swiftui_generator", "ui_validator"],
            "setup_architecture": ["architecture_designer", "code_generator"],
            "write_tests": ["test_generator", "test_runner"],
            "prepare_release": ["release_manager", "build_system"],
            "manage_resources": ["resource_manager", "asset_optimizer"],
            "generate_documentation": ["documentation_generator", "documentation_validator"],
            "review_code": ["code_reviewer", "linter"],
            "optimize_performance": ["performance_analyzer", "optimizer"]
        }
        return provider_map.get(task_type, [])
    
    async def _validate_providers(self, required_providers: List[str]) -> bool:
        """Validate that all required providers are available"""
        for provider in required_providers:
            if not await self.provider_registry.is_provider_available(provider):
                return False
        return True
    
    async def _process_task_by_type(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task based on its type"""
        try:
            # Update knowledge metrics
            self.metrics["knowledge_base"]["knowledge_queries"] += 1
            
            # Get relevant knowledge for the task
            task_type = task.get("type", "")
            knowledge = await self.knowledge_manager.get_task_knowledge(task_type)
            
            if knowledge:
                self.metrics["knowledge_base"]["knowledge_hits"] += 1
            
            # Get matching patterns
            patterns = await self.pattern_matcher.find_matching_patterns(
                task_type=task_type,
                context=task.get("context", {})
            )
            
            if patterns:
                self.metrics["knowledge_base"]["patterns_matched"] += 1
            
            # Process task with knowledge and patterns
            handlers = {
                "create_project": self._create_project,
                "generate_code": self._generate_code,
                "implement_swiftui": self._implement_swiftui,
                "setup_architecture": self._setup_architecture,
                "write_tests": self._write_tests,
                "prepare_release": self._prepare_release,
                "manage_resources": self._manage_resources,
                "generate_documentation": self._generate_documentation,
                "review_code": self._review_code,
                "optimize_performance": self._optimize_performance
            }
            
            handler = handlers.get(task_type)
            if not handler:
                raise ValueError(f"Unsupported task type: {task_type}")
            
            # Add knowledge and patterns to task context
            task["knowledge"] = knowledge
            task["patterns"] = patterns
            
            return await handler(task)
            
        except Exception as e:
            logger.error(f"Task processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def _record_task_start(self, task: Dict[str, Any]) -> None:
        """Record the start of a task"""
        self.task_history.append({
            "type": task.get("type", "unknown"),
            "start_time": datetime.now(),
            "status": "started",
            "details": task
        })
    
    def _record_task_completion(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Record the completion of a task"""
        for task_record in reversed(self.task_history):
            if task_record["type"] == task.get("type") and task_record["status"] == "started":
                task_record.update({
                    "end_time": datetime.now(),
                    "status": "completed",
                    "result": result
                })
                break
    
    def _record_task_failure(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Record the failure of a task"""
        for task_record in reversed(self.task_history):
            if task_record["type"] == task.get("type") and task_record["status"] == "started":
                task_record.update({
                    "end_time": datetime.now(),
                    "status": "failed",
                    "error": result.get("error", "Unknown error")
                })
                break
    
    async def _create_project(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new iOS project"""
        try:
            # Get project requirements
            requirements = task.get("requirements", {})
            
            # Use integration layer for project setup
            setup_result = await self.integration_layer.setup_project(requirements)
            
            if not setup_result["success"]:
                raise ValueError(f"Project setup failed: {setup_result.get('error')}")
            
            # Generate project structure
            solution = await self.solution_generator.generate_solution(
                requirements=requirements,
                language="swift",
                framework="ios",
                architecture=requirements.get("architecture", "mvvm"),
                style=requirements.get("style", "modern")
            )
            
            # Apply solution
            await self.code_modifier.modify_code(
                code="",
                changes=solution["changes"]
            )
            
            # Commit changes
            await self.version_control.commit_changes(
                files=solution["files"],
                message="Initial project setup"
            )
            
            return {
                "status": "success",
                "project_structure": solution["structure"],
                "files_created": solution["files"],
                "setup_result": setup_result
            }
            
        except Exception as e:
            logger.error(f"Project creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def _generate_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Swift code"""
        # Get code requirements
        requirements = task.get("requirements", {})
        
        # Generate code solution
        solution = await self.solution_generator.generate_solution(
            requirements=requirements,
            language="swift",
            framework=requirements.get("framework", "swiftui"),
            architecture=requirements.get("architecture", "mvvm"),
            style=requirements.get("style", "modern")
        )
        
        # Apply solution
        await self.code_modifier.modify_code(
            code=requirements.get("existing_code", ""),
            changes=solution["changes"]
        )
        
        # Commit changes
        await self.version_control.commit_changes(
            files=solution["files"],
            message=f"Generated {requirements.get('component_type', 'code')}"
        )
        
        return {
            "status": "success",
            "generated_code": solution["code"],
            "files_modified": solution["files"]
        }
    
    async def _implement_swiftui(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Implement SwiftUI components"""
        # Get component requirements
        requirements = task.get("requirements", {})
        
        # Generate SwiftUI solution
        solution = await self.solution_generator.generate_solution(
            requirements=requirements,
            language="swift",
            framework="swiftui",
            architecture=requirements.get("architecture", "mvvm"),
            style=requirements.get("style", "modern")
        )
        
        # Apply solution
        await self.code_modifier.modify_code(
            code=requirements.get("existing_code", ""),
            changes=solution["changes"]
        )
        
        # Commit changes
        await self.version_control.commit_changes(
            files=solution["files"],
            message=f"Implemented {requirements.get('component_type', 'SwiftUI component')}"
        )
        
        return {
            "status": "success",
            "component_code": solution["code"],
            "files_modified": solution["files"]
        }
    
    async def _setup_architecture(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Setup project architecture"""
        # Get architecture requirements
        requirements = task.get("requirements", {})
        
        # Get architecture knowledge
        architecture_knowledge = await self.provider_registry.get_provider(
            "knowledge_manager"
        ).get_architecture_knowledge()
        
        # Generate architecture solution
        solution = await self.solution_generator.generate_solution(
            requirements=requirements,
            language="swift",
            framework="ios",
            architecture=requirements.get("architecture", "mvvm"),
            style=requirements.get("style", "modern"),
            knowledge=architecture_knowledge
        )
        
        # Apply solution
        await self.code_modifier.modify_code(
            code="",
            changes=solution["changes"]
        )
        
        # Commit changes
        await self.version_control.commit_changes(
            files=solution["files"],
            message="Project architecture setup"
        )
        
        return {
            "status": "success",
            "architecture": solution["architecture"],
            "files_created": solution["files"]
        }
    
    async def _write_tests(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Write iOS tests"""
        # Get test requirements
        requirements = task.get("requirements", {})
        
        # Generate test solution
        solution = await self.solution_generator.generate_solution(
            requirements=requirements,
            language="swift",
            framework="ios",
            architecture=requirements.get("architecture", "mvvm"),
            style=requirements.get("style", "modern"),
            test_type=requirements.get("test_type", "unit")
        )
        
        # Apply solution
        await self.code_modifier.modify_code(
            code=requirements.get("existing_code", ""),
            changes=solution["changes"]
        )
        
        # Run tests
        test_results = await self.provider_registry.get_provider(
            "test_runner"
        ).run_tests(solution["files"])
        
        # Commit changes
        await self.version_control.commit_changes(
            files=solution["files"],
            message=f"Added {requirements.get('test_type', 'unit')} tests"
        )
        
        return {
            "status": "success",
            "test_results": test_results,
            "files_created": solution["files"]
        }
    
    async def _prepare_release(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare app for release"""
        # Get release requirements
        requirements = task.get("requirements", {})
        
        # Create release branch
        await self.version_control.create_branch(
            branch_name=f"release/{requirements.get('version', '1.0.0')}"
        )
        
        # Update version info
        version_info = await self.provider_registry.get_provider(
            "build_system"
        ).update_version_info(requirements)
        
        # Build release
        build_result = await self.provider_registry.get_provider(
            "build_system"
        ).build_release(requirements)
        
        # Run tests
        test_results = await self.provider_registry.get_provider(
            "test_runner"
        ).run_tests()
        
        # Commit changes
        await self.version_control.commit_changes(
            files=build_result["files"],
            message=f"Release {requirements.get('version', '1.0.0')} preparation"
        )
        
        return {
            "status": "success",
            "version_info": version_info,
            "build_result": build_result,
            "test_results": test_results
        }
    
    async def _manage_resources(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Manage app resources"""
        try:
            # Get resource requirements
            requirements = task.get("requirements", {})
            
            # Use integration layer for resource management
            resource_result = await self.integration_layer.manage_resources(requirements)
            
            if not resource_result["success"]:
                raise ValueError(f"Resource management failed: {resource_result.get('error')}")
            
            # Commit changes
            await self.version_control.commit_changes(
                files=resource_result["files"],
                message="Resource management"
            )
            
            return {
                "status": "success",
                "resource_result": resource_result
            }
            
        except Exception as e:
            logger.error(f"Resource management failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def _generate_documentation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation for code"""
        # Get documentation requirements
        requirements = task.get("requirements", {})
        
        # Get code to document
        code = requirements.get("code", "")
        
        # Generate documentation
        doc_solution = await self.solution_generator.generate_solution(
            requirements=requirements,
            language="markdown",
            framework="documentation",
            style=requirements.get("style", "standard")
        )
        
        # Apply documentation
        await self._update_documentation_coverage()
        
        # Commit changes
        await self.version_control.commit_changes(
            files=doc_solution["files"],
            message="Documentation update"
        )
        
        return {
            "status": "success",
            "documentation": doc_solution["code"],
            "files_modified": doc_solution["files"],
            "coverage": self.metrics["documentation_coverage"]
        }
    
    async def _review_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review code for quality and best practices"""
        # Get review requirements
        requirements = task.get("requirements", {})
        
        # Get code to review
        code = requirements.get("code", "")
        
        # Get code reviewer
        code_reviewer = self.provider_registry.get_provider("code_reviewer")
        
        # Perform code review
        review_result = await code_reviewer.review_code(
            code=code,
            requirements=requirements
        )
        
        # Apply fixes if needed
        if review_result["issues"]:
            fixed_code = await self.fix_system.apply_fix(
                code=code,
                issue=review_result["issues"][0]["description"],
                context=review_result["context"]
            )
            
            # Commit changes
            await self.version_control.commit_changes(
                files=review_result["files"],
                message="Code review fixes"
            )
        else:
            fixed_code = code
        
        # Update code quality score
        await self._update_code_quality_score(review_result)
        
        return {
            "status": "success",
            "review_result": review_result,
            "fixed_code": fixed_code if review_result["issues"] else None,
            "quality_score": self.metrics["code_quality_score"]
        }
    
    async def _optimize_performance(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize code performance"""
        # Get optimization requirements
        requirements = task.get("requirements", {})
        
        # Get code to optimize
        code = requirements.get("code", "")
        
        # Get performance analyzer
        performance_analyzer = self.provider_registry.get_provider("performance_analyzer")
        
        # Analyze performance
        analysis_result = await performance_analyzer.analyze_performance(
            code=code,
            requirements=requirements
        )
        
        # Generate optimization solution
        optimization_solution = await self.solution_generator.generate_solution(
            requirements=analysis_result["optimization_opportunities"],
            language="swift",
            framework=requirements.get("framework", "swiftui"),
            style="performance"
        )
        
        # Apply optimizations
        optimized_code = await self.code_modifier.modify_code(
            code=code,
            changes=optimization_solution["changes"]
        )
        
        # Validate optimizations
        validation_result = await performance_analyzer.validate_optimizations(
            original_code=code,
            optimized_code=optimized_code,
            analysis_result=analysis_result
        )
        
        # Commit changes if validation passed
        if validation_result["success"]:
            await self.version_control.commit_changes(
                files=optimization_solution["files"],
                message="Performance optimization"
            )
        
        return {
            "status": "success",
            "analysis_result": analysis_result,
            "optimization_result": optimization_solution,
            "validation_result": validation_result,
            "performance_improvement": validation_result.get("improvement", 0.0)
        }
    
    async def _update_documentation_coverage(self) -> None:
        """Update documentation coverage metrics"""
        try:
            # Get documentation analyzer
            doc_analyzer = self.provider_registry.get_provider("documentation_analyzer")
            
            # Calculate coverage
            coverage = await doc_analyzer.calculate_coverage()
            
            # Update metrics
            self.metrics["documentation_coverage"] = coverage
            
        except Exception as e:
            logger.error(f"Documentation coverage update failed: {str(e)}")
    
    async def _update_code_quality_score(self, review_result: Dict[str, Any]) -> None:
        """Update code quality score"""
        try:
            # Calculate quality score from review result
            issues = review_result.get("issues", [])
            total_issues = len(issues)
            
            if total_issues == 0:
                quality_score = 1.0
            else:
                # Weight issues by severity
                weighted_score = sum(
                    1.0 - (0.2 * i["severity"]) for i in issues
                )
                quality_score = max(0.0, weighted_score / total_issues)
            
            # Update metrics
            self.metrics["code_quality_score"] = quality_score
            
        except Exception as e:
            logger.error(f"Code quality score update failed: {str(e)}") 