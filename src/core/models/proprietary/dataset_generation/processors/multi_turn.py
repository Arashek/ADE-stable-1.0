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

class MultiTurnProcessor(BaseProcessor):
    """Processor for multi-turn interaction dataset generation"""
    
    def __init__(self, config: ProcessingConfig):
        """Initialize the processor"""
        super().__init__(config)
        self.github = GitHubIntegration()
        self.interaction_types = {
            "debugging": {
                "patterns": [
                    r"error|exception|bug|issue|problem|fail",
                    r"fix|solution|resolve|correct|repair",
                    r"debug|trace|log|diagnose|investigate"
                ],
                "max_turns": 5
            },
            "code_review": {
                "patterns": [
                    r"review|comment|suggest|improve|enhance",
                    r"style|format|convention|standard",
                    r"test|coverage|quality|performance"
                ],
                "max_turns": 3
            },
            "feature_implementation": {
                "patterns": [
                    r"implement|add|create|develop|build",
                    r"feature|functionality|capability|component",
                    r"design|architecture|structure|pattern"
                ],
                "max_turns": 4
            },
            "refactoring": {
                "patterns": [
                    r"refactor|restructure|reorganize|optimize",
                    r"clean|improve|enhance|modernize",
                    r"pattern|design|architecture|structure"
                ],
                "max_turns": 3
            }
        }
        
    def process_source(self, source_path: str) -> List[ProcessedExample]:
        """Process GitHub issues and discussions to create multi-turn interactions"""
        try:
            # Process GitHub issues
            issue_examples = self._process_github_issues(source_path)
            for example in issue_examples:
                self.add_example(example)
                
            # Process GitHub discussions
            discussion_examples = self._process_github_discussions(source_path)
            for example in discussion_examples:
                self.add_example(example)
                
            # Generate synthetic examples
            synthetic_examples = self._generate_synthetic_examples(source_path)
            for example in synthetic_examples:
                self.add_example(example)
                
            return self.examples
            
        except Exception as e:
            logger.error(f"Error processing source: {str(e)}")
            return []
            
    def _process_github_issues(self, source_path: str) -> List[ProcessedExample]:
        """Process GitHub issues to extract multi-turn interactions"""
        examples = []
        
        try:
            # Create issues directory
            issues_path = Path(source_path) / "issues"
            issues_path.mkdir(exist_ok=True)
            
            # Search for repositories with issues
            repos = self.github.search_repositories(
                language=self.config.language,
                min_stars=1000,
                min_activity=30
            )
            
            # Process each repository
            for repo in repos[:10]:  # Limit to top 10 repos
                try:
                    # Get issues
                    issues = self.github.get_repository_issues(repo)
                    
                    # Process each issue
                    for issue in issues:
                        try:
                            # Check if issue has enough interactions
                            if len(issue.comments) < 2:
                                continue
                                
                            # Determine interaction type
                            interaction_type = self._determine_interaction_type(issue)
                            if not interaction_type:
                                continue
                                
                            # Extract conversation
                            conversation = self._extract_conversation(issue)
                            if not conversation:
                                continue
                                
                            # Create example
                            example = ProcessedExample(
                                input_text=self._format_conversation(conversation),
                                output_text=self._generate_resolution(conversation),
                                metadata={
                                    "type": interaction_type,
                                    "source": "github_issue",
                                    "repo": repo.name,
                                    "issue_number": issue.number,
                                    "turns": len(conversation)
                                }
                            )
                            examples.append(example)
                            
                        except Exception as e:
                            logger.error(f"Error processing issue {issue.number}: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error processing repository {repo.name}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing GitHub issues: {str(e)}")
            
        return examples
        
    def _process_github_discussions(self, source_path: str) -> List[ProcessedExample]:
        """Process GitHub discussions to extract multi-turn interactions"""
        examples = []
        
        try:
            # Create discussions directory
            discussions_path = Path(source_path) / "discussions"
            discussions_path.mkdir(exist_ok=True)
            
            # Search for repositories with discussions
            repos = self.github.search_repositories(
                language=self.config.language,
                min_stars=1000,
                min_activity=30
            )
            
            # Process each repository
            for repo in repos[:10]:  # Limit to top 10 repos
                try:
                    # Get discussions
                    discussions = self.github.get_repository_discussions(repo)
                    
                    # Process each discussion
                    for discussion in discussions:
                        try:
                            # Check if discussion has enough interactions
                            if len(discussion.comments) < 2:
                                continue
                                
                            # Determine interaction type
                            interaction_type = self._determine_interaction_type(discussion)
                            if not interaction_type:
                                continue
                                
                            # Extract conversation
                            conversation = self._extract_conversation(discussion)
                            if not conversation:
                                continue
                                
                            # Create example
                            example = ProcessedExample(
                                input_text=self._format_conversation(conversation),
                                output_text=self._generate_resolution(conversation),
                                metadata={
                                    "type": interaction_type,
                                    "source": "github_discussion",
                                    "repo": repo.name,
                                    "discussion_number": discussion.number,
                                    "turns": len(conversation)
                                }
                            )
                            examples.append(example)
                            
                        except Exception as e:
                            logger.error(f"Error processing discussion {discussion.number}: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error processing repository {repo.name}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing GitHub discussions: {str(e)}")
            
        return examples
        
    def _generate_synthetic_examples(self, source_path: str) -> List[ProcessedExample]:
        """Generate synthetic multi-turn interactions"""
        examples = []
        
        try:
            # Create synthetic directory
            synthetic_path = Path(source_path) / "synthetic"
            synthetic_path.mkdir(exist_ok=True)
            
            # Generate examples for each interaction type
            for interaction_type, config in self.interaction_types.items():
                try:
                    # Generate multiple examples
                    for _ in range(10):  # Generate 10 examples per type
                        # Generate conversation
                        conversation = self._generate_conversation(interaction_type)
                        if not conversation:
                            continue
                            
                        # Create example
                        example = ProcessedExample(
                            input_text=self._format_conversation(conversation),
                            output_text=self._generate_resolution(conversation),
                            metadata={
                                "type": interaction_type,
                                "source": "synthetic",
                                "turns": len(conversation)
                            }
                        )
                        examples.append(example)
                        
                except Exception as e:
                    logger.error(f"Error generating synthetic examples for {interaction_type}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error generating synthetic examples: {str(e)}")
            
        return examples
        
    def _determine_interaction_type(self, content: Any) -> Optional[str]:
        """Determine the type of interaction from content"""
        text = content.title + " " + content.body
        
        for interaction_type, config in self.interaction_types.items():
            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    return interaction_type
                    
        return None
        
    def _extract_conversation(self, content: Any) -> List[Dict[str, str]]:
        """Extract conversation from content"""
        conversation = []
        
        # Add initial message
        conversation.append({
            "role": "user",
            "content": content.title + "\n\n" + content.body
        })
        
        # Add comments
        for comment in content.comments:
            conversation.append({
                "role": "assistant",
                "content": comment.body
            })
            
        return conversation
        
    def _generate_conversation(self, interaction_type: str) -> List[Dict[str, str]]:
        """Generate a synthetic conversation"""
        conversation = []
        
        # Generate initial message
        initial_message = self._generate_initial_message(interaction_type)
        conversation.append({
            "role": "user",
            "content": initial_message
        })
        
        # Generate turns
        max_turns = self.interaction_types[interaction_type]["max_turns"]
        for _ in range(random.randint(2, max_turns)):
            # Generate response
            response = self._generate_response(conversation, interaction_type)
            conversation.append({
                "role": "assistant",
                "content": response
            })
            
            # Generate follow-up
            follow_up = self._generate_follow_up(conversation, interaction_type)
            conversation.append({
                "role": "user",
                "content": follow_up
            })
            
        return conversation
        
    def _generate_initial_message(self, interaction_type: str) -> str:
        """Generate an initial message for the conversation"""
        if interaction_type == "debugging":
            return "I'm getting an error in my code. The error message says 'IndexError: list index out of range'. Can you help me debug this?"
        elif interaction_type == "code_review":
            return "Could you review this code and suggest improvements for better performance?"
        elif interaction_type == "feature_implementation":
            return "I want to implement a new feature that allows users to export data in different formats. How should I structure this?"
        elif interaction_type == "refactoring":
            return "This code is getting too complex. How can I refactor it to make it more maintainable?"
        else:
            return "I need help with my code."
            
    def _generate_response(self, conversation: List[Dict[str, str]], interaction_type: str) -> str:
        """Generate a response based on the conversation"""
        # Get the last message
        last_message = conversation[-1]["content"]
        
        if interaction_type == "debugging":
            return "I'll help you debug this. Could you share the relevant code section where the error occurs?"
        elif interaction_type == "code_review":
            return "I'll review your code. Please share the code you'd like me to look at."
        elif interaction_type == "feature_implementation":
            return "I can help you design this feature. What are the specific requirements and constraints?"
        elif interaction_type == "refactoring":
            return "I can help you refactor this code. Could you share the code you want to refactor?"
        else:
            return "I understand you need help. Could you provide more details?"
            
    def _generate_follow_up(self, conversation: List[Dict[str, str]], interaction_type: str) -> str:
        """Generate a follow-up message based on the conversation"""
        # Get the last response
        last_response = conversation[-1]["content"]
        
        if interaction_type == "debugging":
            return "Here's the code section. I've added some print statements to help track the issue."
        elif interaction_type == "code_review":
            return "Here's the code. I've also included some test cases."
        elif interaction_type == "feature_implementation":
            return "Here are the requirements. We need to support CSV, JSON, and Excel formats."
        elif interaction_type == "refactoring":
            return "Here's the code. It's a complex function with multiple responsibilities."
        else:
            return "Here's more information about what I need help with."
            
    def _format_conversation(self, conversation: List[Dict[str, str]]) -> str:
        """Format conversation for input"""
        formatted = []
        
        for message in conversation:
            role = message["role"]
            content = message["content"]
            formatted.append(f"{role}: {content}")
            
        return "\n\n".join(formatted)
        
    def _generate_resolution(self, conversation: List[Dict[str, str]]) -> str:
        """Generate a resolution for the conversation"""
        interaction_type = conversation[0]["metadata"]["type"]
        
        if interaction_type == "debugging":
            return "I've identified the issue. The error occurs because the list is empty when trying to access an index. Here's how to fix it: [solution]"
        elif interaction_type == "code_review":
            return "After reviewing your code, here are the suggested improvements: [improvements]"
        elif interaction_type == "feature_implementation":
            return "Based on your requirements, here's a proposed implementation: [implementation]"
        elif interaction_type == "refactoring":
            return "Here's how we can refactor the code to improve maintainability: [refactoring]"
        else:
            return "Here's the solution to your problem: [solution]"
            
    def validate_example(self, example: ProcessedExample) -> bool:
        """Validate a processed example"""
        # Check input/output lengths
        if len(example.input_text) < 50 or len(example.output_text) < 20:
            return False
            
        # Check conversation structure
        messages = example.input_text.split("\n\n")
        if len(messages) < 2:  # At least 2 messages
            return False
            
        # Check message roles
        roles = [msg.split(":")[0] for msg in messages]
        if not all(role in ["user", "assistant"] for role in roles):
            return False
            
        # Check interaction type
        interaction_type = example.metadata.get("type")
        if not interaction_type or interaction_type not in self.interaction_types:
            return False
            
        return True 