from typing import List, Dict, Any, Optional
import ast
import json
from pathlib import Path
import logging
from datetime import datetime
from ...config.logging_config import logger
from .completion_provider import CompletionProvider
from .code_analysis import CodeAnalyzer

class TrainingDataGenerator:
    """Generates training data for code completion"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.provider = CompletionProvider()
        self.analyzer = CodeAnalyzer()
        
    def generate_training_data(self, code_files: List[str], num_examples: int = 1000) -> Dict[str, Any]:
        """Generate training data from code files"""
        try:
            examples = []
            
            for file_path in code_files:
                # Analyze file
                analysis = self.analyzer.analyze_file(file_path)
                
                # Generate examples
                file_examples = self._generate_file_examples(file_path, analysis, num_examples)
                examples.extend(file_examples)
                
            # Save training data
            training_data = {
                'examples': examples,
                'metadata': {
                    'total_examples': len(examples),
                    'generated_at': datetime.now().isoformat(),
                    'source_files': code_files
                }
            }
            
            self._save_training_data(training_data)
            return training_data
            
        except Exception as e:
            logger.error(f"Error generating training data: {str(e)}")
            return {}
            
    def _generate_file_examples(self, file_path: str, analysis: Dict[str, Any], num_examples: int) -> List[Dict[str, Any]]:
        """Generate examples from a single file"""
        examples = []
        
        try:
            with open(file_path, 'r') as f:
                code = f.read()
                
            # Parse code
            tree = ast.parse(code)
            
            # Get all positions where we can generate examples
            positions = self._get_example_positions(tree)
            
            # Generate examples at each position
            for pos in positions[:num_examples]:
                example = self._generate_example(code, pos, analysis)
                if example:
                    examples.append(example)
                    
        except Exception as e:
            logger.error(f"Error generating examples for {file_path}: {str(e)}")
            
        return examples
        
    def _get_example_positions(self, tree: ast.AST) -> List[int]:
        """Get positions where we can generate examples"""
        positions = []
        
        for node in ast.walk(tree):
            if hasattr(node, 'col_offset'):
                positions.append(node.col_offset)
                
        return sorted(list(set(positions)))
        
    def _generate_example(self, code: str, position: int, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a single training example"""
        try:
            # Get context before position
            context = code[:position]
            
            # Get completions at position
            completions = self.provider.get_completions(context, position)
            
            if not completions:
                return None
                
            # Get actual completion from code
            actual_completion = self._get_actual_completion(code, position)
            
            if not actual_completion:
                return None
                
            # Create example
            example = {
                'context': context,
                'position': position,
                'completions': completions,
                'actual_completion': actual_completion,
                'metadata': {
                    'imports': analysis['imports'],
                    'types': analysis['types'],
                    'references': analysis['references']
                }
            }
            
            return example
            
        except Exception as e:
            logger.error(f"Error generating example at position {position}: {str(e)}")
            return None
            
    def _get_actual_completion(self, code: str, position: int) -> Optional[str]:
        """Get the actual completion from the code"""
        try:
            # Get the line containing the position
            lines = code[:position].split('\n')
            current_line = lines[-1] if lines else ''
            
            # Get the word at position
            words = current_line.split()
            if not words:
                return None
                
            # Find the word containing the position
            current_word = None
            current_pos = 0
            
            for word in words:
                word_end = current_pos + len(word)
                if current_pos <= position <= word_end:
                    current_word = word
                    break
                current_pos = word_end + 1
                
            return current_word
            
        except Exception as e:
            logger.error(f"Error getting actual completion: {str(e)}")
            return None
            
    def _save_training_data(self, training_data: Dict[str, Any]):
        """Save training data to file"""
        try:
            # Create output directory if it doesn't exist
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'training_data_{timestamp}.json'
            
            # Save to file
            output_path = self.output_dir / filename
            with open(output_path, 'w') as f:
                json.dump(training_data, f, indent=2)
                
            logger.info(f"Saved training data to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving training data: {str(e)}")
            
    def generate_evaluation_data(self, training_data: Dict[str, Any], split_ratio: float = 0.8) -> Dict[str, Any]:
        """Generate evaluation data from training data"""
        try:
            # Shuffle examples
            examples = training_data['examples']
            import random
            random.shuffle(examples)
            
            # Split into train and test
            split_idx = int(len(examples) * split_ratio)
            train_examples = examples[:split_idx]
            test_examples = examples[split_idx:]
            
            # Create evaluation data
            evaluation_data = {
                'train': {
                    'examples': train_examples,
                    'metadata': {
                        'num_examples': len(train_examples),
                        'split_ratio': split_ratio
                    }
                },
                'test': {
                    'examples': test_examples,
                    'metadata': {
                        'num_examples': len(test_examples),
                        'split_ratio': 1 - split_ratio
                    }
                }
            }
            
            # Save evaluation data
            self._save_evaluation_data(evaluation_data)
            return evaluation_data
            
        except Exception as e:
            logger.error(f"Error generating evaluation data: {str(e)}")
            return {}
            
    def _save_evaluation_data(self, evaluation_data: Dict[str, Any]):
        """Save evaluation data to file"""
        try:
            # Create output directory if it doesn't exist
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'evaluation_data_{timestamp}.json'
            
            # Save to file
            output_path = self.output_dir / filename
            with open(output_path, 'w') as f:
                json.dump(evaluation_data, f, indent=2)
                
            logger.info(f"Saved evaluation data to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving evaluation data: {str(e)}")
            
    def analyze_training_data(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the generated training data"""
        try:
            examples = training_data['examples']
            
            # Calculate statistics
            stats = {
                'total_examples': len(examples),
                'completion_types': {},
                'context_lengths': [],
                'completion_lengths': []
            }
            
            for example in examples:
                # Count completion types
                for completion in example['completions']:
                    comp_type = completion['type']
                    stats['completion_types'][comp_type] = stats['completion_types'].get(comp_type, 0) + 1
                    
                # Record lengths
                stats['context_lengths'].append(len(example['context']))
                stats['completion_lengths'].append(len(example['actual_completion']))
                
            # Calculate averages
            stats['avg_context_length'] = sum(stats['context_lengths']) / len(stats['context_lengths'])
            stats['avg_completion_length'] = sum(stats['completion_lengths']) / len(stats['completion_lengths'])
            
            # Save analysis
            self._save_analysis(stats)
            return stats
            
        except Exception as e:
            logger.error(f"Error analyzing training data: {str(e)}")
            return {}
            
    def _save_analysis(self, analysis: Dict[str, Any]):
        """Save analysis results to file"""
        try:
            # Create output directory if it doesn't exist
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'analysis_{timestamp}.json'
            
            # Save to file
            output_path = self.output_dir / filename
            with open(output_path, 'w') as f:
                json.dump(analysis, f, indent=2)
                
            logger.info(f"Saved analysis to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}") 