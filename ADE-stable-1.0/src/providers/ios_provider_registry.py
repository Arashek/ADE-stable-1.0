from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from .base import BaseProviderRegistry
from ..services.apple.app_store_connect import AppStoreConnect
from ..services.apple.provisioning import ProvisioningManager
from ..build.ios_build_system import IOSBuildSystem
from ..build.xcode_integration import XcodeIntegration
from ..dependencies.swift_package_manager import SwiftPackageManager
from ..dependencies.cocoa_pods import CocoaPodsManager
from ..ci.ios_ci_system import IOSCISystem
from ..ci.test_runner import IOSTestRunner
from ..review.ios_code_reviewer import IOSCodeReviewer
from ..review.swift_linter import SwiftLinter
from ..monitoring.ios_analytics import IOSAnalytics
from ..monitoring.crash_reporting import CrashReporting
from ..knowledge.ios_knowledge_manager import IOSKnowledgeManager
from ..knowledge.pattern_matcher import PatternMatcher
from ..resources.ios_resource_manager import IOSResourceManager
from ..resources.asset_catalog import AssetCatalogManager

logger = logging.getLogger(__name__)

class IOSProviderRegistry(BaseProviderRegistry):
    """Specialized provider registry for iOS development"""
    
    def __init__(self, metadata: Optional[Dict[str, Any]] = None):
        super().__init__(metadata)
        
        # Initialize iOS-specific providers
        self.app_store = AppStoreConnect(self)
        self.provisioning = ProvisioningManager(self)
        self.build_system = IOSBuildSystem(self)
        self.xcode = XcodeIntegration(self)
        self.package_manager = SwiftPackageManager(self)
        self.cocoa_pods = CocoaPodsManager(self)
        self.ci_system = IOSCISystem(self)
        self.test_runner = IOSTestRunner(self)
        self.code_reviewer = IOSCodeReviewer(self)
        self.linter = SwiftLinter(self)
        self.analytics = IOSAnalytics(self)
        self.crash_reporting = CrashReporting(self)
        self.knowledge_manager = IOSKnowledgeManager(self)
        self.pattern_matcher = PatternMatcher(self)
        self.resource_manager = IOSResourceManager(self)
        self.asset_catalog = AssetCatalogManager(self)
    
    async def initialize(self) -> None:
        """Initialize all iOS providers"""
        try:
            # Initialize base registry
            await super().initialize()
            
            # Initialize Apple services
            await self.app_store.initialize()
            await self.provisioning.initialize()
            
            # Initialize build tools
            await self.build_system.initialize()
            await self.xcode.initialize()
            
            # Initialize dependency management
            await self.package_manager.initialize()
            await self.cocoa_pods.initialize()
            
            # Initialize CI/CD
            await self.ci_system.initialize()
            await self.test_runner.initialize()
            
            # Initialize code quality tools
            await self.code_reviewer.initialize()
            await self.linter.initialize()
            
            # Initialize monitoring
            await self.analytics.initialize()
            await self.crash_reporting.initialize()
            
            # Initialize knowledge management
            await self.knowledge_manager.initialize()
            await self.pattern_matcher.initialize()
            
            # Initialize resource management
            await self.resource_manager.initialize()
            await self.asset_catalog.initialize()
            
            logger.info("iOS provider registry initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize iOS provider registry: {str(e)}")
            raise
    
    def get_provider(self, provider_type: str) -> Any:
        """Get a provider by type"""
        providers = {
            "app_store": self.app_store,
            "provisioning": self.provisioning,
            "build_system": self.build_system,
            "xcode": self.xcode,
            "package_manager": self.package_manager,
            "cocoa_pods": self.cocoa_pods,
            "ci_system": self.ci_system,
            "test_runner": self.test_runner,
            "code_reviewer": self.code_reviewer,
            "linter": self.linter,
            "analytics": self.analytics,
            "crash_reporting": self.crash_reporting,
            "knowledge_manager": self.knowledge_manager,
            "pattern_matcher": self.pattern_matcher,
            "resource_manager": self.resource_manager,
            "asset_catalog": self.asset_catalog
        }
        
        if provider_type not in providers:
            raise ValueError(f"Unknown provider type: {provider_type}")
            
        return providers[provider_type]
    
    async def validate_providers(self) -> Dict[str, bool]:
        """Validate all providers are properly configured"""
        validation_results = {}
        
        try:
            # Validate Apple services
            validation_results["app_store"] = await self.app_store.validate()
            validation_results["provisioning"] = await self.provisioning.validate()
            
            # Validate build tools
            validation_results["build_system"] = await self.build_system.validate()
            validation_results["xcode"] = await self.xcode.validate()
            
            # Validate dependency management
            validation_results["package_manager"] = await self.package_manager.validate()
            validation_results["cocoa_pods"] = await self.cocoa_pods.validate()
            
            # Validate CI/CD
            validation_results["ci_system"] = await self.ci_system.validate()
            validation_results["test_runner"] = await self.test_runner.validate()
            
            # Validate code quality tools
            validation_results["code_reviewer"] = await self.code_reviewer.validate()
            validation_results["linter"] = await self.linter.validate()
            
            # Validate monitoring
            validation_results["analytics"] = await self.analytics.validate()
            validation_results["crash_reporting"] = await self.crash_reporting.validate()
            
            # Validate knowledge management
            validation_results["knowledge_manager"] = await self.knowledge_manager.validate()
            validation_results["pattern_matcher"] = await self.pattern_matcher.validate()
            
            # Validate resource management
            validation_results["resource_manager"] = await self.resource_manager.validate()
            validation_results["asset_catalog"] = await self.asset_catalog.validate()
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Provider validation failed: {str(e)}")
            raise
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        
        try:
            # Get Apple services status
            status["app_store"] = await self.app_store.get_status()
            status["provisioning"] = await self.provisioning.get_status()
            
            # Get build tools status
            status["build_system"] = await self.build_system.get_status()
            status["xcode"] = await self.xcode.get_status()
            
            # Get dependency management status
            status["package_manager"] = await self.package_manager.get_status()
            status["cocoa_pods"] = await self.cocoa_pods.get_status()
            
            # Get CI/CD status
            status["ci_system"] = await self.ci_system.get_status()
            status["test_runner"] = await self.test_runner.get_status()
            
            # Get code quality tools status
            status["code_reviewer"] = await self.code_reviewer.get_status()
            status["linter"] = await self.linter.get_status()
            
            # Get monitoring status
            status["analytics"] = await self.analytics.get_status()
            status["crash_reporting"] = await self.crash_reporting.get_status()
            
            # Get knowledge management status
            status["knowledge_manager"] = await self.knowledge_manager.get_status()
            status["pattern_matcher"] = await self.pattern_matcher.get_status()
            
            # Get resource management status
            status["resource_manager"] = await self.resource_manager.get_status()
            status["asset_catalog"] = await self.asset_catalog.get_status()
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get provider status: {str(e)}")
            raise 