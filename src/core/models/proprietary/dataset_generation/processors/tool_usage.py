import os
import logging
import random
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re
import json
from .base import BaseProcessor, ProcessingConfig, ProcessedExample
from ..github_integration import GitHubIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolUsageProcessor(BaseProcessor):
    """Processor for tool usage dataset generation"""
    
    def __init__(self, config: ProcessingConfig):
        """Initialize the processor"""
        super().__init__(config)
        self.github = GitHubIntegration()
        self.tool_categories = {
            "version_control": ["git", "svn", "hg"],
            "build_tools": ["make", "cmake", "gradle", "maven", "npm"],
            "testing": ["pytest", "junit", "jest", "mocha"],
            "deployment": ["docker", "kubernetes", "terraform", "ansible"],
            "package_management": ["pip", "npm", "yarn", "cargo", "maven"],
            "documentation": ["sphinx", "doxygen", "javadoc"],
            "linting": ["pylint", "eslint", "clang-tidy"],
            "profiling": ["cProfile", "valgrind", "perf"]
        }
        
    def process_source(self, source_path: str) -> List[ProcessedExample]:
        """Process API documentation and tutorials to create tool usage examples"""
        try:
            # Process API documentation
            api_examples = self._process_api_documentation(source_path)
            for example in api_examples:
                self.add_example(example)
                
            # Process tutorials
            tutorial_examples = self._process_tutorials(source_path)
            for example in tutorial_examples:
                self.add_example(example)
                
            # Process GitHub examples
            github_examples = self._process_github_examples(source_path)
            for example in github_examples:
                self.add_example(example)
                
            return self.examples
            
        except Exception as e:
            logger.error(f"Error processing source: {str(e)}")
            return []
            
    def _process_api_documentation(self, source_path: str) -> List[ProcessedExample]:
        """Process API documentation to extract tool usage examples"""
        examples = []
        
        try:
            # Create documentation directory
            docs_path = Path(source_path) / "api_docs"
            docs_path.mkdir(exist_ok=True)
            
            # Process each tool category
            for category, tools in self.tool_categories.items():
                for tool in tools:
                    try:
                        # Search for documentation
                        repos = self.github.search_repositories(
                            query=f"{tool} documentation",
                            language="markdown",
                            min_stars=100
                        )
                        
                        # Process each repository
                        for repo in repos[:5]:  # Limit to top 5 docs
                            try:
                                # Clone repository
                                repo_path = self.github.clone_repository(repo, str(docs_path))
                                if not repo_path:
                                    continue
                                    
                                # Extract examples
                                tool_examples = self._extract_api_examples(repo_path, tool)
                                examples.extend(tool_examples)
                                
                            except Exception as e:
                                logger.error(f"Error processing documentation repo {repo.name}: {str(e)}")
                                continue
                                
                    except Exception as e:
                        logger.error(f"Error processing tool {tool}: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error processing API documentation: {str(e)}")
            
        return examples
        
    def _process_tutorials(self, source_path: str) -> List[ProcessedExample]:
        """Process tutorials to extract tool usage examples"""
        examples = []
        
        try:
            # Create tutorials directory
            tutorials_path = Path(source_path) / "tutorials"
            tutorials_path.mkdir(exist_ok=True)
            
            # Process each tool category
            for category, tools in self.tool_categories.items():
                for tool in tools:
                    try:
                        # Search for tutorials
                        repos = self.github.search_repositories(
                            query=f"{tool} tutorial",
                            language="markdown",
                            min_stars=100
                        )
                        
                        # Process each repository
                        for repo in repos[:5]:  # Limit to top 5 tutorials
                            try:
                                # Clone repository
                                repo_path = self.github.clone_repository(repo, str(tutorials_path))
                                if not repo_path:
                                    continue
                                    
                                # Extract examples
                                tool_examples = self._extract_tutorial_examples(repo_path, tool)
                                examples.extend(tool_examples)
                                
                            except Exception as e:
                                logger.error(f"Error processing tutorial repo {repo.name}: {str(e)}")
                                continue
                                
                    except Exception as e:
                        logger.error(f"Error processing tool {tool}: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error processing tutorials: {str(e)}")
            
        return examples
        
    def _process_github_examples(self, source_path: str) -> List[ProcessedExample]:
        """Process GitHub repositories for real-world tool usage examples"""
        examples = []
        
        try:
            # Create examples directory
            examples_path = Path(source_path) / "github_examples"
            examples_path.mkdir(exist_ok=True)
            
            # Process each tool category
            for category, tools in self.tool_categories.items():
                for tool in tools:
                    try:
                        # Search for repositories using the tool
                        repos = self.github.search_repositories(
                            query=f"filename:{tool}",
                            language=self.config.language,
                            min_stars=100
                        )
                        
                        # Process each repository
                        for repo in repos[:5]:  # Limit to top 5 examples
                            try:
                                # Clone repository
                                repo_path = self.github.clone_repository(repo, str(examples_path))
                                if not repo_path:
                                    continue
                                    
                                # Extract examples
                                tool_examples = self._extract_github_examples(repo_path, tool)
                                examples.extend(tool_examples)
                                
                            except Exception as e:
                                logger.error(f"Error processing example repo {repo.name}: {str(e)}")
                                continue
                                
                    except Exception as e:
                        logger.error(f"Error processing tool {tool}: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error processing GitHub examples: {str(e)}")
            
        return examples
        
    def _extract_api_examples(
        self,
        repo_path: Path,
        tool: str
    ) -> List[ProcessedExample]:
        """Extract examples from API documentation"""
        examples = []
        
        try:
            # Find markdown files
            for file_path in repo_path.rglob("*.md"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Find code blocks
                    code_blocks = re.finditer(r"```\w*\n(.*?)\n```", content, re.DOTALL)
                    
                    for block in code_blocks:
                        code = block.group(1)
                        
                        # Find tool usage patterns
                        if self._is_tool_usage(code, tool):
                            # Get context
                            context_start = max(0, block.start() - 200)
                            context_end = min(len(content), block.end() + 200)
                            context = content[context_start:context_end]
                            
                            # Create example
                            example = ProcessedExample(
                                input_text=f"Use {tool} to:\n{self._extract_task(context)}",
                                output_text=code,
                                metadata={
                                    "tool": tool,
                                    "source": "api_doc",
                                    "file": str(file_path),
                                    "context": context
                                }
                            )
                            examples.append(example)
                            
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting API examples: {str(e)}")
            
        return examples
        
    def _extract_tutorial_examples(
        self,
        repo_path: Path,
        tool: str
    ) -> List[ProcessedExample]:
        """Extract examples from tutorials"""
        examples = []
        
        try:
            # Find markdown files
            for file_path in repo_path.rglob("*.md"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Find code blocks
                    code_blocks = re.finditer(r"```\w*\n(.*?)\n```", content, re.DOTALL)
                    
                    for block in code_blocks:
                        code = block.group(1)
                        
                        # Find tool usage patterns
                        if self._is_tool_usage(code, tool):
                            # Get context
                            context_start = max(0, block.start() - 200)
                            context_end = min(len(content), block.end() + 200)
                            context = content[context_start:context_end]
                            
                            # Create example
                            example = ProcessedExample(
                                input_text=f"Use {tool} to:\n{self._extract_task(context)}",
                                output_text=code,
                                metadata={
                                    "tool": tool,
                                    "source": "tutorial",
                                    "file": str(file_path),
                                    "context": context
                                }
                            )
                            examples.append(example)
                            
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting tutorial examples: {str(e)}")
            
        return examples
        
    def _extract_github_examples(
        self,
        repo_path: Path,
        tool: str
    ) -> List[ProcessedExample]:
        """Extract examples from GitHub repositories"""
        examples = []
        
        try:
            # Find tool-specific files
            tool_files = list(repo_path.rglob(f"*{tool}*"))
            
            for file_path in tool_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Find tool usage patterns
                    if self._is_tool_usage(content, tool):
                        # Get context
                        context_start = max(0, 0)
                        context_end = min(len(content), 400)
                        context = content[context_start:context_end]
                        
                        # Create example
                        example = ProcessedExample(
                            input_text=f"Use {tool} to:\n{self._extract_task(context)}",
                            output_text=content,
                            metadata={
                                "tool": tool,
                                "source": "github",
                                "file": str(file_path),
                                "context": context
                            }
                        )
                        examples.append(example)
                        
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting GitHub examples: {str(e)}")
            
        return examples
        
    def _is_tool_usage(self, code: str, tool: str) -> bool:
        """Check if code contains tool usage patterns"""
        # Check for tool commands
        if tool in ["git", "docker", "npm", "pip"]:
            return bool(re.search(rf"^{tool}\s+", code, re.MULTILINE))
            
        # Check for tool configuration files
        if tool in ["make", "cmake", "gradle", "maven"]:
            return bool(re.search(rf"\.{tool}$", code))
            
        # Check for tool imports/requires
        if tool in ["pytest", "junit", "jest", "mocha"]:
            return bool(re.search(rf"import\s+{tool}|require\s*\(\s*['\"]{tool}['\"]", code))
            
        # Check for tool-specific patterns
        if tool == "docker":
            return bool(re.search(r"FROM|RUN|CMD|ENTRYPOINT", code))
        elif tool == "terraform":
            return bool(re.search(r"resource|provider|variable|output", code))
        elif tool == "ansible":
            return bool(re.search(r"hosts|tasks|handlers|vars", code))
            
        return False
        
    def _extract_task(self, context: str) -> str:
        """Extract task description from context"""
        # Find task description in markdown
        task_match = re.search(r"^#\s+(.*?)$|^##\s+(.*?)$|^###\s+(.*?)$", context, re.MULTILINE)
        if task_match:
            return task_match.group(1) or task_match.group(2) or task_match.group(3)
            
        # Find task description in comments
        comment_match = re.search(r"#\s+(.*?)$|//\s+(.*?)$|/\*\s*(.*?)\s*\*/", context, re.MULTILINE)
        if comment_match:
            return comment_match.group(1) or comment_match.group(2) or comment_match.group(3)
            
        # Default task description
        return "Perform the specified operation"
        
    def validate_example(self, example: ProcessedExample) -> bool:
        """Validate a processed example"""
        # Check input/output lengths
        if len(example.input_text) < 20 or len(example.output_text) < 10:
            return False
            
        # Check tool usage
        tool = example.metadata.get("tool")
        if not tool or not self._is_tool_usage(example.output_text, tool):
            return False
            
        # Check task description
        if not example.input_text.startswith(f"Use {tool} to:"):
            return False
            
        return True 