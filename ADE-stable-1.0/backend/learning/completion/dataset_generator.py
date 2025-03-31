from typing import Dict, List, Any, Optional, Tuple
import ast
import re
from pathlib import Path
import json
from dataclasses import dataclass
from datetime import datetime
import logging
from ...config.logging_config import logger

@dataclass
class CompletionExample:
    """Represents a single code completion example"""
    context: str
    completion: str
    cursor_position: int
    completion_type: str  # 'line', 'function', 'import', 'type'
    metadata: Dict[str, Any]

class CompletionDatasetGenerator:
    """Generates training data for code completion"""
    
    def __init__(self, output_dir: str = "data/completion"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize tokenizers and parsers
        self.completion_types = {
            'line': self._generate_line_completions,
            'function': self._generate_function_completions,
            'import': self._generate_import_completions,
            'type': self._generate_type_completions
        }
        
    def generate_dataset(self, 
                        code_files: List[str],
                        num_examples: int = 1000) -> List[CompletionExample]:
        """Generate a dataset of completion examples"""
        try:
            examples = []
            
            for file_path in code_files:
                with open(file_path, 'r') as f:
                    code = f.read()
                    
                # Generate examples for each completion type
                for comp_type, generator in self.completion_types.items():
                    type_examples = generator(code, num_examples // len(self.completion_types))
                    examples.extend(type_examples)
                    
            # Save dataset
            self._save_dataset(examples)
            
            return examples
            
        except Exception as e:
            logger.error(f"Error generating dataset: {str(e)}")
            return []
            
    def _generate_line_completions(self, code: str, num_examples: int) -> List[CompletionExample]:
        """Generate line-level completion examples"""
        examples = []
        lines = code.split('\n')
        
        for i in range(len(lines)):
            if i >= num_examples:
                break
                
            # Get context (previous lines)
            context = '\n'.join(lines[max(0, i-5):i])
            
            # Get completion (current line)
            completion = lines[i]
            
            # Generate example
            example = CompletionExample(
                context=context,
                completion=completion,
                cursor_position=len(context),
                completion_type='line',
                metadata={
                    'line_number': i,
                    'indentation_level': len(re.match(r'^\s*', completion).group(0)) // 4
                }
            )
            
            examples.append(example)
            
        return examples
        
    def _generate_function_completions(self, code: str, num_examples: int) -> List[CompletionExample]:
        """Generate function-level completion examples"""
        examples = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(examples) >= num_examples:
                        break
                        
                    # Get function context
                    context = code[:node.col_offset]
                    
                    # Get function body
                    completion = code[node.col_offset:node.end_col_offset]
                    
                    # Generate example
                    example = CompletionExample(
                        context=context,
                        completion=completion,
                        cursor_position=len(context),
                        completion_type='function',
                        metadata={
                            'function_name': node.name,
                            'num_args': len(node.args.args),
                            'has_return': any(isinstance(n, ast.Return) for n in ast.walk(node))
                        }
                    )
                    
                    examples.append(example)
                    
        except Exception as e:
            logger.error(f"Error parsing code for function completions: {str(e)}")
            
        return examples
        
    def _generate_import_completions(self, code: str, num_examples: int) -> List[CompletionExample]:
        """Generate import completion examples"""
        examples = []
        
        try:
            tree = ast.parse(code)
            
            # Find import statements
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            for imp in imports:
                if len(examples) >= num_examples:
                    break
                    
                # Get context before import
                context = code[:imp.col_offset]
                
                # Get import statement
                completion = code[imp.col_offset:imp.end_col_offset]
                
                # Generate example
                example = CompletionExample(
                    context=context,
                    completion=completion,
                    cursor_position=len(context),
                    completion_type='import',
                    metadata={
                        'import_type': 'from' if isinstance(imp, ast.ImportFrom) else 'import',
                        'module_name': imp.names[0].name if isinstance(imp, ast.Import) else imp.module
                    }
                )
                
                examples.append(example)
                
        except Exception as e:
            logger.error(f"Error parsing code for import completions: {str(e)}")
            
        return examples
        
    def _generate_type_completions(self, code: str, num_examples: int) -> List[CompletionExample]:
        """Generate type annotation completion examples"""
        examples = []
        
        try:
            tree = ast.parse(code)
            
            # Find function arguments and return annotations
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(examples) >= num_examples:
                        break
                        
                    # Generate examples for arguments
                    for arg in node.args.args:
                        if arg.annotation is None:
                            # Get context before argument
                            context = code[:arg.col_offset]
                            
                            # Generate type annotation
                            completion = f": {self._infer_type(arg.arg)}"
                            
                            # Generate example
                            example = CompletionExample(
                                context=context,
                                completion=completion,
                                cursor_position=len(context),
                                completion_type='type',
                                metadata={
                                    'function_name': node.name,
                                    'arg_name': arg.arg,
                                    'annotation_type': 'argument'
                                }
                            )
                            
                            examples.append(example)
                            
                    # Generate example for return type
                    if node.returns is None:
                        # Get context before return annotation
                        context = code[:node.col_offset + len(node.name) + 1]
                        
                        # Generate return type annotation
                        completion = f" -> {self._infer_return_type(node)}"
                        
                        # Generate example
                        example = CompletionExample(
                            context=context,
                            completion=completion,
                            cursor_position=len(context),
                            completion_type='type',
                            metadata={
                                'function_name': node.name,
                                'annotation_type': 'return'
                            }
                        )
                        
                        examples.append(example)
                        
        except Exception as e:
            logger.error(f"Error parsing code for type completions: {str(e)}")
            
        return examples
        
    def _infer_type(self, arg_name: str) -> str:
        """Infer type for a function argument"""
        # Simple type inference based on argument name
        type_hints = {
            'self': 'Any',
            'cls': 'Type[Any]',
            'data': 'Dict[str, Any]',
            'items': 'List[Any]',
            'count': 'int',
            'name': 'str',
            'value': 'Any',
            'key': 'Any',
            'default': 'Any',
            'args': 'List[Any]',
            'kwargs': 'Dict[str, Any]'
        }
        
        return type_hints.get(arg_name, 'Any')
        
    def _infer_return_type(self, node: ast.FunctionDef) -> str:
        """Infer return type for a function"""
        # Simple return type inference based on function name and body
        if any(isinstance(n, ast.Return) for n in ast.walk(node)):
            return 'Any'
        return 'None'
        
    def _save_dataset(self, examples: List[CompletionExample]):
        """Save the generated dataset"""
        try:
            # Convert examples to dict format
            dataset = []
            for example in examples:
                dataset.append({
                    'context': example.context,
                    'completion': example.completion,
                    'cursor_position': example.cursor_position,
                    'completion_type': example.completion_type,
                    'metadata': example.metadata,
                    'timestamp': datetime.now().isoformat()
                })
                
            # Save to file
            output_file = self.output_dir / f"completion_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(dataset, f, indent=2)
                
            logger.info(f"Saved dataset to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving dataset: {str(e)}")
            
    def generate_from_cursor_position(self, 
                                    code: str,
                                    cursor_position: int,
                                    completion_type: str) -> List[CompletionExample]:
        """Generate completion examples for a specific cursor position"""
        try:
            if completion_type not in self.completion_types:
                raise ValueError(f"Unknown completion type: {completion_type}")
                
            # Get context before cursor
            context = code[:cursor_position]
            
            # Generate examples using appropriate generator
            generator = self.completion_types[completion_type]
            examples = generator(context, 1)
            
            return examples
            
        except Exception as e:
            logger.error(f"Error generating examples from cursor position: {str(e)}")
            return [] 