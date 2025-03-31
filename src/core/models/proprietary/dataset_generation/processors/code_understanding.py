import os
import logging
import random
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from .base import BaseProcessor, ProcessingConfig, ProcessedExample
from ..github_integration import GitHubIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeUnderstandingProcessor(BaseProcessor):
    """Processor for code understanding dataset generation"""
    
    def __init__(self, config: ProcessingConfig):
        """Initialize the processor"""
        super().__init__(config)
        self.github = GitHubIntegration()
        self.question_templates = [
            "What does this function do?",
            "How does this function work?",
            "Explain the purpose of this code:",
            "Describe the functionality of this function:",
            "What is the main purpose of this code snippet?"
        ]
        
    def process_source(self, source_path: str) -> List[ProcessedExample]:
        """Process GitHub repositories to extract function definitions and documentation"""
        try:
            # Search for repositories
            repos = self.github.search_repositories(
                language=self.config.language,
                min_stars=1000,
                min_activity=30
            )
            
            # Process each repository
            for repo in repos[:10]:  # Limit to top 10 repos for testing
                try:
                    # Clone repository
                    repo_path = self.github.clone_repository(repo, source_path)
                    if not repo_path:
                        continue
                        
                    # Extract functions and their documentation
                    examples = self._extract_functions(repo_path)
                    
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
            
    def _extract_functions(self, repo_path: Path) -> List[ProcessedExample]:
        """Extract functions and their documentation from repository"""
        examples = []
        
        try:
            # Find Python files
            for file_path in repo_path.rglob(f"*.{self.config.language}"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Parse the file
                    tree = ast.parse(content)
                    
                    # Extract functions
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Get function documentation
                            docstring = ast.get_docstring(node)
                            if not docstring:
                                continue
                                
                            # Get function code
                            start_line = node.lineno - 1
                            end_line = node.end_lineno
                            function_code = "\n".join(content.split("\n")[start_line:end_line])
                            
                            # Generate questions
                            for template in self.question_templates:
                                example = ProcessedExample(
                                    input_text=f"{template}\n\n{function_code}",
                                    output_text=docstring,
                                    metadata={
                                        "file_path": str(file_path),
                                        "function_name": node.name,
                                        "start_line": start_line,
                                        "end_line": end_line,
                                        "question_template": template
                                    }
                                )
                                examples.append(example)
                                
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting functions: {str(e)}")
            
        return examples
        
    def validate_example(self, example: ProcessedExample) -> bool:
        """Validate a processed example"""
        # Check input/output lengths
        if len(example.input_text) < 50 or len(example.output_text) < 20:
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
            
        # Check documentation quality
        if len(example.output_text.split()) < 5:  # At least 5 words
            return False
            
        return True
        
    def augment_examples(self, examples: List[ProcessedExample]) -> List[ProcessedExample]:
        """Augment examples with additional questions"""
        augmented = []
        
        for example in examples:
            # Add original example
            augmented.append(example)
            
            # Extract code from input
            code_match = re.search(r"```\w*\n(.*?)\n```", example.input_text, re.DOTALL)
            if not code_match:
                continue
                
            code = code_match.group(1)
            
            # Generate additional questions
            additional_questions = [
                f"What are the parameters of this function?",
                f"What is the return value of this function?",
                f"Are there any side effects in this function?",
                f"What are the edge cases this function handles?",
                f"How would you test this function?"
            ]
            
            for question in additional_questions:
                augmented.append(ProcessedExample(
                    input_text=f"{question}\n\n{code}",
                    output_text=example.output_text,  # Use same documentation
                    metadata={
                        **example.metadata,
                        "question_template": question,
                        "is_augmented": True
                    }
                ))
                
        return augmented 