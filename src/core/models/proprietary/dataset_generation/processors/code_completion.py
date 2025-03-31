import os
import logging
import random
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import ast
import re
from .base import BaseProcessor, ProcessingConfig, ProcessedExample
from ..github_integration import GitHubIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeCompletionProcessor(BaseProcessor):
    """Processor for code completion dataset generation"""
    
    def __init__(self, config: ProcessingConfig):
        """Initialize the processor"""
        super().__init__(config)
        self.github = GitHubIntegration()
        self.completion_types = [
            "function",
            "class",
            "loop",
            "condition",
            "variable"
        ]
        
    def process_source(self, source_path: str) -> List[ProcessedExample]:
        """Process high-quality repositories to create completion pairs"""
        try:
            # Search for repositories
            repos = self.github.search_repositories(
                language=self.config.language,
                min_stars=5000,  # Higher threshold for quality
                min_activity=30
            )
            
            # Process each repository
            for repo in repos[:10]:  # Limit to top 10 repos for testing
                try:
                    # Clone repository
                    repo_path = self.github.clone_repository(repo, source_path)
                    if not repo_path:
                        continue
                        
                    # Extract completion pairs
                    examples = self._extract_completion_pairs(repo_path)
                    
                    # Add examples to dataset
                    for example in examples:
                        self.add_example(example)
                        
                except Exception as e:
                    logger.error(f"Error processing repository {repo.name}: {str(e)}")
                    continue
                    
            return self.examples
            
        except Exception as e:
            logger.error(f"Error processing source: {str(e)}")
            return []
            
    def _extract_completion_pairs(self, repo_path: Path) -> List[ProcessedExample]:
        """Extract code completion pairs from repository"""
        examples = []
        
        try:
            # Find Python files
            for file_path in repo_path.rglob(f"*.{self.config.language}"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Parse the file
                    tree = ast.parse(content)
                    
                    # Extract completion pairs
                    for completion_type in self.completion_types:
                        if completion_type == "function":
                            examples.extend(self._extract_function_completions(content, tree))
                        elif completion_type == "class":
                            examples.extend(self._extract_class_completions(content, tree))
                        elif completion_type == "loop":
                            examples.extend(self._extract_loop_completions(content, tree))
                        elif completion_type == "condition":
                            examples.extend(self._extract_condition_completions(content, tree))
                        elif completion_type == "variable":
                            examples.extend(self._extract_variable_completions(content, tree))
                            
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting completion pairs: {str(e)}")
            
        return examples
        
    def _extract_function_completions(
        self,
        content: str,
        tree: ast.AST
    ) -> List[ProcessedExample]:
        """Extract function completion pairs"""
        examples = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function code
                start_line = node.lineno - 1
                end_line = node.end_lineno
                function_code = "\n".join(content.split("\n")[start_line:end_line])
                
                # Create completion pairs at different points
                lines = function_code.split("\n")
                for i in range(1, len(lines)):
                    prefix = "\n".join(lines[:i])
                    completion = "\n".join(lines[i:])
                    
                    # Get context
                    context_start = max(0, start_line - self.config.context_window)
                    context_end = min(len(content.split("\n")), end_line + self.config.context_window)
                    context = "\n".join(content.split("\n")[context_start:context_end])
                    
                    example = ProcessedExample(
                        input_text=f"Complete this function:\n\n{prefix}",
                        output_text=completion,
                        metadata={
                            "completion_type": "function",
                            "function_name": node.name,
                            "start_line": start_line,
                            "end_line": end_line,
                            "context_start": context_start,
                            "context_end": context_end,
                            "context": context
                        }
                    )
                    examples.append(example)
                    
        return examples
        
    def _extract_class_completions(
        self,
        content: str,
        tree: ast.AST
    ) -> List[ProcessedExample]:
        """Extract class completion pairs"""
        examples = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Get class code
                start_line = node.lineno - 1
                end_line = node.end_lineno
                class_code = "\n".join(content.split("\n")[start_line:end_line])
                
                # Create completion pairs
                lines = class_code.split("\n")
                for i in range(1, len(lines)):
                    prefix = "\n".join(lines[:i])
                    completion = "\n".join(lines[i:])
                    
                    # Get context
                    context_start = max(0, start_line - self.config.context_window)
                    context_end = min(len(content.split("\n")), end_line + self.config.context_window)
                    context = "\n".join(content.split("\n")[context_start:context_end])
                    
                    example = ProcessedExample(
                        input_text=f"Complete this class:\n\n{prefix}",
                        output_text=completion,
                        metadata={
                            "completion_type": "class",
                            "class_name": node.name,
                            "start_line": start_line,
                            "end_line": end_line,
                            "context_start": context_start,
                            "context_end": context_end,
                            "context": context
                        }
                    )
                    examples.append(example)
                    
        return examples
        
    def _extract_loop_completions(
        self,
        content: str,
        tree: ast.AST
    ) -> List[ProcessedExample]:
        """Extract loop completion pairs"""
        examples = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                # Get loop code
                start_line = node.lineno - 1
                end_line = node.end_lineno
                loop_code = "\n".join(content.split("\n")[start_line:end_line])
                
                # Create completion pairs
                lines = loop_code.split("\n")
                for i in range(1, len(lines)):
                    prefix = "\n".join(lines[:i])
                    completion = "\n".join(lines[i:])
                    
                    # Get context
                    context_start = max(0, start_line - self.config.context_window)
                    context_end = min(len(content.split("\n")), end_line + self.config.context_window)
                    context = "\n".join(content.split("\n")[context_start:context_end])
                    
                    example = ProcessedExample(
                        input_text=f"Complete this loop:\n\n{prefix}",
                        output_text=completion,
                        metadata={
                            "completion_type": "loop",
                            "loop_type": "for" if isinstance(node, ast.For) else "while",
                            "start_line": start_line,
                            "end_line": end_line,
                            "context_start": context_start,
                            "context_end": context_end,
                            "context": context
                        }
                    )
                    examples.append(example)
                    
        return examples
        
    def _extract_condition_completions(
        self,
        content: str,
        tree: ast.AST
    ) -> List[ProcessedExample]:
        """Extract condition completion pairs"""
        examples = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Get condition code
                start_line = node.lineno - 1
                end_line = node.end_lineno
                condition_code = "\n".join(content.split("\n")[start_line:end_line])
                
                # Create completion pairs
                lines = condition_code.split("\n")
                for i in range(1, len(lines)):
                    prefix = "\n".join(lines[:i])
                    completion = "\n".join(lines[i:])
                    
                    # Get context
                    context_start = max(0, start_line - self.config.context_window)
                    context_end = min(len(content.split("\n")), end_line + self.config.context_window)
                    context = "\n".join(content.split("\n")[context_start:context_end])
                    
                    example = ProcessedExample(
                        input_text=f"Complete this condition:\n\n{prefix}",
                        output_text=completion,
                        metadata={
                            "completion_type": "condition",
                            "start_line": start_line,
                            "end_line": end_line,
                            "context_start": context_start,
                            "context_end": context_end,
                            "context": context
                        }
                    )
                    examples.append(example)
                    
        return examples
        
    def _extract_variable_completions(
        self,
        content: str,
        tree: ast.AST
    ) -> List[ProcessedExample]:
        """Extract variable completion pairs"""
        examples = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Get assignment code
                start_line = node.lineno - 1
                end_line = node.end_lineno
                assignment_code = "\n".join(content.split("\n")[start_line:end_line])
                
                # Create completion pairs
                lines = assignment_code.split("\n")
                for i in range(1, len(lines)):
                    prefix = "\n".join(lines[:i])
                    completion = "\n".join(lines[i:])
                    
                    # Get context
                    context_start = max(0, start_line - self.config.context_window)
                    context_end = min(len(content.split("\n")), end_line + self.config.context_window)
                    context = "\n".join(content.split("\n")[context_start:context_end])
                    
                    example = ProcessedExample(
                        input_text=f"Complete this assignment:\n\n{prefix}",
                        output_text=completion,
                        metadata={
                            "completion_type": "variable",
                            "start_line": start_line,
                            "end_line": end_line,
                            "context_start": context_start,
                            "context_end": context_end,
                            "context": context
                        }
                    )
                    examples.append(example)
                    
        return examples
        
    def validate_example(self, example: ProcessedExample) -> bool:
        """Validate a processed example"""
        # Check input/output lengths
        if len(example.input_text) < 20 or len(example.output_text) < 10:
            return False
            
        # Check code quality
        try:
            # Parse the code part
            code_match = re.search(r"```\w*\n(.*?)\n```", example.input_text, re.DOTALL)
            if code_match:
                code = code_match.group(1)
                ast.parse(code)
        except:
            return False
            
        # Check completion quality
        if len(example.output_text.split("\n")) < 1:  # At least one line
            return False
            
        return True 