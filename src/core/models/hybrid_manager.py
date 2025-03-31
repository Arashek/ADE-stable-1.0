from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .model_router import ModelRouter
from .ast_parser import ASTParser
from ..config import ModelConfig

logger = logging.getLogger(__name__)

@dataclass
class HybridModelConfig:
    """Configuration for hybrid model components"""
    code_understanding_model: str = "codellama/CodeLlama-34b-Instruct-hf"
    tool_use_model: str = "anthropic/claude-3-sonnet-20240229"
    planning_model: str = "anthropic/claude-3-sonnet-20240229"
    code_generation_model: str = "bigcode/starcoder2-33b"
    reasoning_model: str = "gpt-4-turbo-preview"
    
    # Model-specific parameters
    temperature: float = 0.2
    max_tokens: int = 2000
    top_p: float = 0.9
    
    # Component-specific configurations
    code_understanding_config: Dict[str, Any] = None
    tool_use_config: Dict[str, Any] = None
    planning_config: Dict[str, Any] = None
    code_generation_config: Dict[str, Any] = None
    reasoning_config: Dict[str, Any] = None

class HybridModelManager:
    """Manages the hybrid model architecture for superior code awareness and tool use"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model_router = ModelRouter()
        self.hybrid_config = HybridModelConfig()
        self.ast_parser = ASTParser(config.ast_parser)
        self._initialize_components()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def _initialize_components(self):
        """Initialize all components of the hybrid architecture"""
        # Initialize code understanding component
        self.code_understanding = self._initialize_code_understanding()
        
        # Initialize tool use component
        self.tool_use = self._initialize_tool_use()
        
        # Initialize planning component
        self.planning = self._initialize_planning()
        
        # Initialize code generation component
        self.code_generation = self._initialize_code_generation()
        
        # Initialize reasoning component
        self.reasoning = self._initialize_reasoning()
        
    def _initialize_code_understanding(self):
        """Initialize code understanding component"""
        model_config = self.config.code_understanding
        try:
            models = {}
            for role, model_name in model_config["models"].items():
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
                if torch.cuda.is_available():
                    model = model.to("cuda")
                models[role] = {"tokenizer": tokenizer, "model": model}
            return models
        except Exception as e:
            logger.error(f"Failed to initialize code understanding component: {e}")
            return None
            
    def _initialize_tool_use(self):
        """Initialize tool use component"""
        return self.model_router.get_model_for_capability("tool_use")
        
    def _initialize_planning(self):
        """Initialize planning component"""
        return self.model_router.get_model_for_capability("planning")
        
    def _initialize_code_generation(self):
        """Initialize code generation component"""
        return self.model_router.get_model_for_capability("code_generation")
        
    def _initialize_reasoning(self):
        """Initialize reasoning component"""
        return self.model_router.get_model_for_capability("reasoning")
        
    async def process_code_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a code-related task using the hybrid architecture"""
        try:
            # 1. Code Understanding Phase
            code_understanding = await self._understand_code(task)
            
            # 2. Planning Phase
            plan = await self._create_plan(task, code_understanding)
            
            # 3. Tool Use Phase
            tools = await self._select_tools(plan)
            
            # 4. Code Generation Phase
            code = await self._generate_code(plan, tools)
            
            # 5. Reasoning Phase
            reasoning = await self._reason_about_code(code, plan)
            
            return {
                "code_understanding": code_understanding,
                "plan": plan,
                "tools": tools,
                "code": code,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logger.error(f"Error processing code task: {e}")
            return {"error": str(e)}
        
    async def _understand_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Understand the code context and requirements"""
        if not self.code_understanding:
            return {"error": "Code understanding component not initialized"}
            
        try:
            # Parse code using AST parser
            code = task.get("code", "")
            language = task.get("language", "python")
            ast_analysis = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.ast_parser.parse_code,
                code,
                language
            )
            
            # Use primary model for understanding
            primary_model = self.code_understanding["primary"]
            model_input = self._prepare_code_understanding_input(code, ast_analysis)
            
            # Generate understanding
            with torch.no_grad():
                inputs = primary_model["tokenizer"](model_input, return_tensors="pt")
                if torch.cuda.is_available():
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                outputs = primary_model["model"].generate(**inputs)
                understanding = primary_model["tokenizer"].decode(outputs[0], skip_special_tokens=True)
            
            return {
                "status": "success",
                "understanding": understanding,
                "ast_analysis": ast_analysis
            }
            
        except Exception as e:
            logger.error(f"Error in code understanding: {e}")
            return {"error": str(e)}
        
    async def _create_plan(self, task: Dict[str, Any], understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Create a plan for the task"""
        if not self.planning:
            return {"error": "Planning component not initialized"}
            
        try:
            # Use planning model to create task plan
            plan = await self.model_router.route_task({
                "task_type": "planning",
                "content": self._prepare_planning_input(task, understanding),
                "temperature": self.config.planning["temperature"]
            })
            
            return {
                "status": "success",
                "plan": plan.content,
                "metadata": plan.metadata
            }
            
        except Exception as e:
            logger.error(f"Error in planning: {e}")
            return {"error": str(e)}
        
    async def _select_tools(self, plan: Dict[str, Any]) -> List[str]:
        """Select appropriate tools for the plan"""
        if not self.tool_use:
            return ["error: Tool use component not initialized"]
            
        try:
            # Use tool use model to select appropriate tools
            tool_selection = await self.model_router.route_task({
                "task_type": "tool_use",
                "content": self._prepare_tool_selection_input(plan),
                "temperature": self.config.tool_use["temperature"]
            })
            
            return {
                "status": "success",
                "tools": self._parse_tool_selection(tool_selection.content),
                "metadata": tool_selection.metadata
            }
            
        except Exception as e:
            logger.error(f"Error in tool selection: {e}")
            return {"error": str(e)}
        
    async def _generate_code(self, plan: Dict[str, Any], tools: List[str]) -> str:
        """Generate code based on plan and tools"""
        if not self.code_generation:
            return "error: Code generation component not initialized"
            
        try:
            # Use code generation model to create code
            code = await self.model_router.route_task({
                "task_type": "code_generation",
                "content": self._prepare_code_generation_input(plan, tools),
                "temperature": self.config.code_generation["temperature"]
            })
            
            return {
                "status": "success",
                "code": code.content,
                "metadata": code.metadata
            }
            
        except Exception as e:
            logger.error(f"Error in code generation: {e}")
            return {"error": str(e)}
        
    async def _reason_about_code(self, code: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Reason about the generated code"""
        if not self.reasoning:
            return {"error": "Reasoning component not initialized"}
            
        try:
            # Use reasoning model to analyze code
            reasoning = await self.model_router.route_task({
                "task_type": "reasoning",
                "content": self._prepare_reasoning_input(code, plan),
                "temperature": self.config.reasoning["temperature"]
            })
            
            return {
                "status": "success",
                "reasoning": reasoning.content,
                "metadata": reasoning.metadata
            }
            
        except Exception as e:
            logger.error(f"Error in reasoning: {e}")
            return {"error": str(e)}
            
    def _prepare_code_understanding_input(self, code: str, ast_analysis: Dict[str, Any]) -> str:
        """Prepare input for code understanding model"""
        return f"""Analyze the following code and its AST analysis:
        
Code:
{code}

AST Analysis:
{ast_analysis}

Provide a comprehensive understanding of the code structure, dependencies, and functionality."""
        
    def _prepare_planning_input(self, task: Dict[str, Any], understanding: Dict[str, Any]) -> str:
        """Prepare input for planning model"""
        return f"""Based on the following task and code understanding, create a detailed plan:

Task:
{task}

Code Understanding:
{understanding}

Create a step-by-step plan for completing the task."""
        
    def _prepare_tool_selection_input(self, plan: Dict[str, Any]) -> str:
        """Prepare input for tool selection"""
        return f"""Based on the following plan, select appropriate tools:

Plan:
{plan}

Select the most suitable tools for implementing this plan."""
        
    def _prepare_code_generation_input(self, plan: Dict[str, Any], tools: List[str]) -> str:
        """Prepare input for code generation"""
        return f"""Generate code based on the following plan and selected tools:

Plan:
{plan}

Selected Tools:
{tools}

Generate high-quality code that implements the plan using the selected tools."""
        
    def _prepare_reasoning_input(self, code: str, plan: Dict[str, Any]) -> str:
        """Prepare input for reasoning"""
        return f"""Analyze the following generated code against the original plan:

Code:
{code}

Original Plan:
{plan}

Provide reasoning about the code's correctness, efficiency, and potential improvements."""
        
    def _parse_tool_selection(self, selection: str) -> List[str]:
        """Parse tool selection from model output"""
        # Implement tool selection parsing logic
        return selection.split("\n") 