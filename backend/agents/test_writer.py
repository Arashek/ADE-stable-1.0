from typing import Dict, List, Optional
import asyncio
import logging
from uuid import uuid4

from ..models.codebase import Codebase, File
from ..utils.llm import LLMClient
from ..utils.code_analysis import CodeAnalyzer
from ..utils.test_runner import TestRunner
from ..utils.telemetry import track_event

logger = logging.getLogger(__name__)

class TestWriterAgent:
    def __init__(self):
        self.llm_client = LLMClient()
        self.code_analyzer = CodeAnalyzer()
        self.test_runner = TestRunner()
        
    async def generate_tests(self, codebase: Codebase, requirements: Dict) -> List[File]:
        """
        Generate comprehensive test suite for the codebase
        """
        test_files = []
        
        # Analyze codebase for testable components
        components = await self._analyze_testable_components(codebase)
        
        # Generate test strategy
        test_strategy = await self._generate_test_strategy(
            components,
            requirements
        )
        
        # Generate test files for each component
        for component in components:
            test_file = await self._generate_component_tests(
                component,
                test_strategy,
                requirements
            )
            test_files.append(test_file)
            
        # Generate integration tests
        integration_tests = await self._generate_integration_tests(
            components,
            test_strategy
        )
        test_files.extend(integration_tests)
        
        # Generate end-to-end tests
        e2e_tests = await self._generate_e2e_tests(
            codebase,
            requirements
        )
        test_files.extend(e2e_tests)
        
        # Validate and optimize tests
        optimized_tests = await self._optimize_tests(test_files)
        
        return optimized_tests
        
    async def update_tests(self, codebase: Codebase, modifications: Dict) -> List[File]:
        """
        Update existing tests based on code changes
        """
        updated_tests = []
        
        # Analyze code changes
        changes = await self._analyze_code_changes(modifications)
        
        # Update affected tests
        for change in changes:
            updated_test = await self._update_test_file(
                change['test_file'],
                change['modifications']
            )
            updated_tests.append(updated_test)
            
        # Regenerate integration tests if needed
        if changes['requires_integration_update']:
            new_integration_tests = await self._update_integration_tests(
                codebase,
                changes
            )
            updated_tests.extend(new_integration_tests)
            
        return updated_tests
        
    async def _analyze_testable_components(self, codebase: Codebase) -> List[Dict]:
        """
        Analyze codebase to identify testable components
        """
        components = []
        
        for file in codebase.files:
            analysis = await self.code_analyzer.analyze_file(file)
            if analysis['testable']:
                components.append({
                    'file': file,
                    'functions': analysis['functions'],
                    'classes': analysis['classes'],
                    'complexity': analysis['complexity']
                })
                
        return components
        
    async def _generate_test_strategy(self, components: List[Dict], requirements: Dict) -> Dict:
        """
        Generate comprehensive test strategy
        """
        strategy_prompt = self._build_strategy_prompt(components, requirements)
        
        strategy = await self.llm_client.generate(
            strategy_prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        return self._parse_test_strategy(strategy)
        
    async def _generate_component_tests(self, component: Dict, strategy: Dict, requirements: Dict) -> File:
        """
        Generate tests for a specific component
        """
        test_prompt = self._build_test_prompt(component, strategy, requirements)
        
        test_code = await self.llm_client.generate(
            test_prompt,
            temperature=0.7,
            max_tokens=3000
        )
        
        test_file = File(
            path=f"tests/{component['file'].path}",
            content=test_code
        )
        
        # Validate test coverage
        coverage = await self._validate_test_coverage(test_file, component)
        if coverage < strategy['min_coverage']:
            test_file = await self._improve_test_coverage(
                test_file,
                component,
                coverage,
                strategy
            )
            
        return test_file
        
    async def _generate_integration_tests(self, components: List[Dict], strategy: Dict) -> List[File]:
        """
        Generate integration tests for component interactions
        """
        integration_tests = []
        
        # Identify component interactions
        interactions = await self._identify_interactions(components)
        
        for interaction in interactions:
            test_file = await self._generate_interaction_tests(
                interaction,
                strategy
            )
            integration_tests.append(test_file)
            
        return integration_tests
        
    async def _generate_e2e_tests(self, codebase: Codebase, requirements: Dict) -> List[File]:
        """
        Generate end-to-end tests based on requirements
        """
        e2e_tests = []
        
        # Extract user scenarios from requirements
        scenarios = await self._extract_test_scenarios(requirements)
        
        for scenario in scenarios:
            test_file = await self._generate_scenario_test(
                scenario,
                codebase
            )
            e2e_tests.append(test_file)
            
        return e2e_tests
        
    async def _optimize_tests(self, test_files: List[File]) -> List[File]:
        """
        Optimize test suite for performance and maintainability
        """
        optimized_files = []
        
        for test_file in test_files:
            # Analyze test performance
            performance = await self._analyze_test_performance(test_file)
            
            if performance['needs_optimization']:
                optimized_file = await self._optimize_test_file(
                    test_file,
                    performance['suggestions']
                )
                optimized_files.append(optimized_file)
            else:
                optimized_files.append(test_file)
                
        return optimized_files
