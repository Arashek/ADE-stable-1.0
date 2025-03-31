from typing import Dict, Any, List, Optional, Tuple
import os
import json
import random
from pathlib import Path
import ast
from dataclasses import dataclass
import logging
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer

logger = logging.getLogger(__name__)

@dataclass
class CodeExample:
    """Represents a code completion example"""
    context: str
    completion: str
    language: str
    file_path: str
    line_number: int
    metadata: Dict[str, Any] = None

class TrainingDataCollector:
    """Collects training examples from a codebase"""
    
    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)
        self.examples: List[CodeExample] = []
    
    def collect_examples(self, num_examples: int) -> List[CodeExample]:
        """Collect training examples from the codebase"""
        try:
            # Walk through codebase
            for root, _, files in os.walk(self.codebase_path):
                for file in files:
                    if not file.endswith('.py'):
                        continue
                        
                    file_path = Path(root) / file
                    self._process_file(file_path)
                    
                    # Stop if we have enough examples
                    if len(self.examples) >= num_examples:
                        return self.examples[:num_examples]
            
            # If we don't have enough examples, return what we have
            return self.examples
            
        except Exception as e:
            logger.error(f"Failed to collect examples: {str(e)}")
            return self.examples
    
    def _process_file(self, file_path: Path) -> None:
        """Process a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse the file
            tree = ast.parse(content)
            
            # Extract functions and classes
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._extract_function_example(node, content, file_path)
                elif isinstance(node, ast.ClassDef):
                    self._extract_class_example(node, content, file_path)
                    
        except Exception as e:
            logger.warning(f"Failed to process file {file_path}: {str(e)}")
    
    def _extract_function_example(self, node: ast.FunctionDef, content: str, file_path: Path) -> None:
        """Extract a function example"""
        try:
            # Get function body
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            
            # Get context (previous lines)
            context_start = max(0, start_line - 5)
            context = '\n'.join(content.split('\n')[context_start:start_line])
            
            # Get function body
            body = '\n'.join(content.split('\n')[start_line:end_line])
            
            # Create example
            example = CodeExample(
                context=context,
                completion=body,
                language="python",
                file_path=str(file_path),
                line_number=start_line,
                metadata={
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'returns': ast.unparse(node.returns) if node.returns else None
                }
            )
            
            self.examples.append(example)
            
        except Exception as e:
            logger.warning(f"Failed to extract function example: {str(e)}")
    
    def _extract_class_example(self, node: ast.ClassDef, content: str, file_path: Path) -> None:
        """Extract a class example"""
        try:
            # Get class body
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            
            # Get context (previous lines)
            context_start = max(0, start_line - 5)
            context = '\n'.join(content.split('\n')[context_start:start_line])
            
            # Get class body
            body = '\n'.join(content.split('\n')[start_line:end_line])
            
            # Create example
            example = CodeExample(
                context=context,
                completion=body,
                language="python",
                file_path=str(file_path),
                line_number=start_line,
                metadata={
                    'name': node.name,
                    'bases': [ast.unparse(base) for base in node.bases],
                    'methods': [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                }
            )
            
            self.examples.append(example)
            
        except Exception as e:
            logger.warning(f"Failed to extract class example: {str(e)}")

class SyntheticDataGenerator:
    """Generates synthetic training examples"""
    
    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizer
    ):
        self.model = model
        self.tokenizer = tokenizer
    
    async def generate_examples(
        self,
        num_examples: int,
        example_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Generate synthetic training examples"""
        if example_types is None:
            example_types = ['function', 'class']
            
        examples = []
        
        try:
            for _ in range(num_examples):
                # Randomly select example type
                example_type = random.choice(example_types)
                
                if example_type == 'function':
                    example = await self._generate_function_example()
                else:
                    example = await self._generate_class_example()
                    
                if example:
                    examples.append(example)
                    
            return examples
            
        except Exception as e:
            logger.error(f"Failed to generate synthetic examples: {str(e)}")
            return examples
    
    async def _generate_function_example(self) -> Optional[Dict[str, Any]]:
        """Generate a synthetic function example"""
        try:
            # Generate function signature
            prompt = "def "
            completion = await self._generate_completion(prompt)
            
            if not completion:
                return None
                
            # Parse completion to extract metadata
            try:
                tree = ast.parse(completion)
                node = tree.body[0]
                
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return None
                    
                example = {
                    'type': 'function',
                    'context': '',
                    'completion': completion,
                    'metadata': {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'returns': ast.unparse(node.returns) if node.returns else None
                    }
                }
                
                return example
                
            except Exception as e:
                logger.warning(f"Failed to parse function completion: {str(e)}")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to generate function example: {str(e)}")
            return None
    
    async def _generate_class_example(self) -> Optional[Dict[str, Any]]:
        """Generate a synthetic class example"""
        try:
            # Generate class definition
            prompt = "class "
            completion = await self._generate_completion(prompt)
            
            if not completion:
                return None
                
            # Parse completion to extract metadata
            try:
                tree = ast.parse(completion)
                node = tree.body[0]
                
                if not isinstance(node, ast.ClassDef):
                    return None
                    
                example = {
                    'type': 'class',
                    'context': '',
                    'completion': completion,
                    'metadata': {
                        'name': node.name,
                        'bases': [ast.unparse(base) for base in node.bases],
                        'methods': [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    }
                }
                
                return example
                
            except Exception as e:
                logger.warning(f"Failed to parse class completion: {str(e)}")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to generate class example: {str(e)}")
            return None
    
    async def _generate_completion(self, prompt: str) -> Optional[str]:
        """Generate completion for a prompt"""
        try:
            # Get device from model
            device = next(self.model.parameters()).device
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            
            # Move inputs to device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.7,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode and return
            completion = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            
            return completion if completion.strip() else None
            
        except Exception as e:
            logger.warning(f"Failed to generate completion: {str(e)}")
            return None 