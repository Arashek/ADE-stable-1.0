from typing import Dict, Any, Optional
import logging
from datetime import datetime

from ..build.ios_build_system import IOSBuildSystem
from ..dependencies.swift_package_manager import SwiftPackageManager
from ..ci.ios_ci_system import IOSCISystem
from ..review.ios_code_reviewer import IOSCodeReviewer
from ..knowledge.ios_knowledge_manager import IOSKnowledgeManager
from ..resources.ios_resource_manager import IOSResourceManager
from ..resources.asset_catalog import AssetCatalogManager

logger = logging.getLogger(__name__)

class IOSIntegrationLayer:
    """Handles all iOS-specific integrations"""
    
    def __init__(self):
        # Build and dependency management
        self.build_system = IOSBuildSystem()
        self.package_manager = SwiftPackageManager()
        
        # CI/CD and code review
        self.ci_system = IOSCISystem()
        self.code_reviewer = IOSCodeReviewer()
        
        # Knowledge and resource management
        self.knowledge_manager = IOSKnowledgeManager()
        self.resource_manager = IOSResourceManager()
        self.asset_catalog = AssetCatalogManager()
        
        # Integration metrics
        self.metrics = {
            "initialized": False,
            "last_initialization": None,
            "build_count": 0,
            "package_updates": 0,
            "ci_runs": 0,
            "reviews_completed": 0,
            "resources_managed": 0,
            "assets_processed": 0
        }
    
    async def initialize(self) -> None:
        """Initialize all integrations"""
        try:
            # Initialize build system
            await self.build_system.initialize()
            
            # Initialize package manager
            await self.package_manager.initialize()
            
            # Initialize CI system
            await self.ci_system.initialize()
            
            # Initialize code reviewer
            await self.code_reviewer.initialize()
            
            # Initialize knowledge manager
            await self.knowledge_manager.initialize()
            
            # Initialize resource manager
            await self.resource_manager.initialize()
            
            # Initialize asset catalog
            await self.asset_catalog.initialize()
            
            # Update metrics
            self.metrics["initialized"] = True
            self.metrics["last_initialization"] = datetime.now()
            
            logger.info("iOS Integration Layer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize iOS Integration Layer: {str(e)}")
            raise
    
    async def setup_project(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup a new iOS project"""
        try:
            # Create project structure
            project_structure = await self.build_system.create_project(project_config)
            
            # Initialize dependencies
            dependencies = await self.package_manager.initialize_dependencies(
                project_config.get("dependencies", {})
            )
            
            # Setup CI/CD
            ci_config = await self.ci_system.setup_project(project_config)
            
            # Initialize resource management
            resources = await self.resource_manager.initialize_project_resources(
                project_config.get("resources", {})
            )
            
            # Setup asset catalog
            assets = await self.asset_catalog.initialize_catalog(
                project_config.get("assets", {})
            )
            
            return {
                "success": True,
                "project_structure": project_structure,
                "dependencies": dependencies,
                "ci_config": ci_config,
                "resources": resources,
                "assets": assets
            }
            
        except Exception as e:
            logger.error(f"Project setup failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def manage_resources(self, resource_config: Dict[str, Any]) -> Dict[str, Any]:
        """Manage project resources"""
        try:
            # Update metrics
            self.metrics["resources_managed"] += 1
            
            # Manage resources
            resource_result = await self.resource_manager.manage_resources(resource_config)
            
            # Update asset catalog if needed
            if resource_config.get("update_assets", False):
                asset_result = await self.asset_catalog.update_catalog(
                    resource_config.get("assets", {})
                )
                resource_result["assets"] = asset_result
            
            return resource_result
            
        except Exception as e:
            logger.error(f"Resource management failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_assets(self, asset_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process project assets"""
        try:
            # Update metrics
            self.metrics["assets_processed"] += 1
            
            # Process assets
            result = await self.asset_catalog.process_assets(asset_config)
            
            return result
            
        except Exception as e:
            logger.error(f"Asset processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of all integrations"""
        return {
            "metrics": self.metrics,
            "build_system": await self.build_system.get_status(),
            "package_manager": await self.package_manager.get_status(),
            "ci_system": await self.ci_system.get_status(),
            "code_reviewer": await self.code_reviewer.get_status(),
            "knowledge_manager": await self.knowledge_manager.get_status(),
            "resource_manager": await self.resource_manager.get_status(),
            "asset_catalog": await self.asset_catalog.get_status(),
            "timestamp": datetime.now()
        } 