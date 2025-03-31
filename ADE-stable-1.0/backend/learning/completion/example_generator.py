from typing import Dict, List, Any, Optional
import ast
import re
from pathlib import Path
import json
from dataclasses import dataclass
from datetime import datetime
import logging
from ...config.logging_config import logger

@dataclass
class CompletionVariation:
    """Represents a variation of a completion example"""
    context: str
    completion: str
    cursor_position: int
    metadata: Dict[str, Any]

class CompletionExampleGenerator:
    """Generates variations of completion examples"""
    
    def __init__(self):
        self.variation_types = {
            'import': self._generate_import_variations,
            'type': self._generate_type_variations,
            'function': self._generate_function_variations,
            'line': self._generate_line_variations
        }
        
    def generate_variations(self,
                          code: str,
                          cursor_position: int,
                          completion_type: str,
                          num_variations: int = 5) -> List[CompletionVariation]:
        """Generate variations of completion examples"""
        try:
            if completion_type not in self.variation_types:
                raise ValueError(f"Unknown completion type: {completion_type}")
                
            # Get context before cursor
            context = code[:cursor_position]
            
            # Generate variations using appropriate generator
            generator = self.variation_types[completion_type]
            variations = generator(context, num_variations)
            
            return variations
            
        except Exception as e:
            logger.error(f"Error generating variations: {str(e)}")
            return []
            
    def _generate_import_variations(self, context: str, num_variations: int) -> List[CompletionVariation]:
        """Generate variations of import statements"""
        variations = []
        
        # Common import patterns
        import_patterns = [
            "from {module} import {name}",
            "import {module}",
            "from {module} import {name} as {alias}",
            "import {module} as {alias}"
        ]
        
        # Common module names
        common_modules = [
            "typing", "pathlib", "json", "datetime", "logging",
            "numpy", "pandas", "torch", "transformers"
        ]
        
        # Generate variations
        for _ in range(num_variations):
            pattern = import_patterns[_ % len(import_patterns)]
            module = common_modules[_ % len(common_modules)]
            
            if "as" in pattern:
                completion = pattern.format(
                    module=module,
                    name=module.split('.')[-1],
                    alias=f"{module.split('.')[-1]}_alias"
                )
            else:
                completion = pattern.format(
                    module=module,
                    name=module.split('.')[-1]
                )
                
            variation = CompletionVariation(
                context=context,
                completion=completion,
                cursor_position=len(context),
                metadata={
                    'pattern': pattern,
                    'module': module,
                    'variation_type': 'import'
                }
            )
            
            variations.append(variation)
            
        return variations
        
    def _generate_type_variations(self, context: str, num_variations: int) -> List[CompletionVariation]:
        """Generate variations of type annotations"""
        variations = []
        
        # Common type patterns
        type_patterns = [
            ": {type}",
            " -> {type}",
            ": Optional[{type}]",
            ": List[{type}]",
            ": Dict[str, {type}]"
        ]
        
        # Common types
        common_types = [
            "str", "int", "float", "bool", "Any",
            "List", "Dict", "Optional", "Union"
        ]
        
        # Generate variations
        for _ in range(num_variations):
            pattern = type_patterns[_ % len(type_patterns)]
            type_name = common_types[_ % len(common_types)]
            
            completion = pattern.format(type=type_name)
            
            variation = CompletionVariation(
                context=context,
                completion=completion,
                cursor_position=len(context),
                metadata={
                    'pattern': pattern,
                    'type': type_name,
                    'variation_type': 'type'
                }
            )
            
            variations.append(variation)
            
        return variations
        
    def _generate_function_variations(self, context: str, num_variations: int) -> List[CompletionVariation]:
        """Generate variations of function completions"""
        variations = []
        
        # Common function patterns
        function_patterns = [
            "def {name}({args}):\n    {body}",
            "async def {name}({args}):\n    {body}",
            "def {name}({args}) -> {return_type}:\n    {body}"
        ]
        
        # Common function names
        common_names = [
            "process", "handle", "validate", "transform",
            "calculate", "generate", "update", "create"
        ]
        
        # Common argument patterns
        arg_patterns = [
            "self",
            "self, data: Dict[str, Any]",
            "self, items: List[Any]",
            "self, value: Any",
            "self, *args, **kwargs"
        ]
        
        # Common body patterns
        body_patterns = [
            "pass",
            "return None",
            "return True",
            "return False",
            "raise NotImplementedError()"
        ]
        
        # Generate variations
        for _ in range(num_variations):
            pattern = function_patterns[_ % len(function_patterns)]
            name = common_names[_ % len(common_names)]
            args = arg_patterns[_ % len(arg_patterns)]
            body = body_patterns[_ % len(body_patterns)]
            
            if "->" in pattern:
                completion = pattern.format(
                    name=name,
                    args=args,
                    return_type="Any",
                    body=body
                )
            else:
                completion = pattern.format(
                    name=name,
                    args=args,
                    body=body
                )
                
            variation = CompletionVariation(
                context=context,
                completion=completion,
                cursor_position=len(context),
                metadata={
                    'pattern': pattern,
                    'name': name,
                    'args': args,
                    'body': body,
                    'variation_type': 'function'
                }
            )
            
            variations.append(variation)
            
        return variations
        
    def _generate_line_variations(self, context: str, num_variations: int) -> List[CompletionVariation]:
        """Generate variations of line completions"""
        variations = []
        
        # Common line patterns
        line_patterns = [
            "{var} = {value}",
            "{var}.{method}()",
            "if {condition}:",
            "for {var} in {iterable}:",
            "while {condition}:",
            "return {value}",
            "raise {exception}",
            "assert {condition}"
        ]
        
        # Common variables
        common_vars = [
            "result", "data", "value", "item",
            "count", "index", "key", "name"
        ]
        
        # Common values
        common_values = [
            "None", "True", "False", "0",
            "''", "[]", "{}", "set()"
        ]
        
        # Common methods
        common_methods = [
            "append", "extend", "update",
            "pop", "remove", "clear"
        ]
        
        # Generate variations
        for _ in range(num_variations):
            pattern = line_patterns[_ % len(line_patterns)]
            var = common_vars[_ % len(common_vars)]
            
            if "=" in pattern:
                completion = pattern.format(
                    var=var,
                    value=common_values[_ % len(common_values)]
                )
            elif "." in pattern:
                completion = pattern.format(
                    var=var,
                    method=common_methods[_ % len(common_methods)]
                )
            elif "in" in pattern:
                completion = pattern.format(
                    var=var,
                    iterable="range(10)"
                )
            else:
                completion = pattern.format(
                    condition="True",
                    value="None",
                    exception="ValueError"
                )
                
            variation = CompletionVariation(
                context=context,
                completion=completion,
                cursor_position=len(context),
                metadata={
                    'pattern': pattern,
                    'var': var,
                    'variation_type': 'line'
                }
            )
            
            variations.append(variation)
            
        return variations
        
    def save_variations(self, variations: List[CompletionVariation], output_file: str):
        """Save generated variations to file"""
        try:
            # Convert variations to dict format
            data = []
            for variation in variations:
                data.append({
                    'context': variation.context,
                    'completion': variation.completion,
                    'cursor_position': variation.cursor_position,
                    'metadata': variation.metadata,
                    'timestamp': datetime.now().isoformat()
                })
                
            # Save to file
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved variations to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving variations: {str(e)}") 