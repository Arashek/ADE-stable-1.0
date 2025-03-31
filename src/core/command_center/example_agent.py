from typing import Dict, Any
import asyncio
import logging
from .agent import BaseAgent

logger = logging.getLogger(__name__)

class ExampleAgent(BaseAgent):
    def __init__(self, command_center_url: str):
        super().__init__(
            agent_type="example",
            capabilities=["text_processing", "data_analysis"],
            command_center_url=command_center_url
        )
        
    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """Execute the assigned task"""
        task_type = task.get("type")
        data = task.get("data", {})
        
        if task_type == "text_processing":
            return await self._process_text(data)
        elif task_type == "data_analysis":
            return await self._analyze_data(data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
            
    async def _process_text(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process text data"""
        text = data.get("text", "")
        operation = data.get("operation", "count_words")
        
        if operation == "count_words":
            word_count = len(text.split())
            return {"word_count": word_count}
        elif operation == "reverse":
            return {"reversed_text": text[::-1]}
        else:
            raise ValueError(f"Unknown text operation: {operation}")
            
    async def _analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze numerical data"""
        numbers = data.get("numbers", [])
        
        if not numbers:
            return {"error": "No numbers provided"}
            
        return {
            "sum": sum(numbers),
            "average": sum(numbers) / len(numbers),
            "min": min(numbers),
            "max": max(numbers)
        }
        
async def main():
    """Main entry point for the example agent"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start the agent
    agent = ExampleAgent("ws://localhost:8000")
    await agent.start()
    
if __name__ == "__main__":
    asyncio.run(main()) 