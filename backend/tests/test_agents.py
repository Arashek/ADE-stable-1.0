import os
from openai import OpenAI
from agents import Agent, Runner

def test_code_agent():
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create a code-focused agent
    code_agent = Agent(
        name="CodeAssistant",
        instructions="""You are an expert code assistant. Your role is to:
        1. Write clean, efficient, and well-documented code
        2. Review and improve existing code
        3. Debug and fix issues
        4. Provide explanations for code concepts
        5. Suggest best practices and optimizations
        
        Always include:
        - Type hints
        - Docstrings
        - Error handling
        - Unit tests
        - Performance considerations""",
        model="gpt-4-turbo-preview"
    )
    
    try:
        # Test the agent with a coding task
        result = Runner.run_sync(
            code_agent,
            "Write a Python function to implement a binary search algorithm with proper error handling and type hints."
        )
        assert result.final_output is not None
        print("✅ Code Agent test successful")
        return True
    except Exception as e:
        print(f"❌ Code Agent test failed: {str(e)}")
        return False

def test_reasoning_agent():
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create a reasoning-focused agent
    reasoning_agent = Agent(
        name="ReasoningAssistant",
        instructions="""You are an expert reasoning assistant. Your role is to:
        1. Break down complex problems into steps
        2. Provide detailed explanations
        3. Consider edge cases and alternatives
        4. Make logical connections
        5. Validate assumptions
        
        Always include:
        - Step-by-step reasoning
        - Assumptions and constraints
        - Alternative approaches
        - Validation steps""",
        model="gpt-4-turbo-preview"
    )
    
    try:
        # Test the agent with a reasoning task
        result = Runner.run_sync(
            reasoning_agent,
            "Explain how to design a scalable microservices architecture, considering factors like service discovery, load balancing, and data consistency."
        )
        assert result.final_output is not None
        print("✅ Reasoning Agent test successful")
        return True
    except Exception as e:
        print(f"❌ Reasoning Agent test failed: {str(e)}")
        return False

def test_agent_handoff():
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create two specialized agents
    code_agent = Agent(
        name="CodeAssistant",
        instructions="You are an expert code assistant focused on writing and reviewing code.",
        model="gpt-4-turbo-preview"
    )
    
    reasoning_agent = Agent(
        name="ReasoningAssistant",
        instructions="You are an expert reasoning assistant focused on problem-solving and architecture.",
        model="gpt-4-turbo-preview"
    )
    
    try:
        # Test handoff between agents
        initial_result = Runner.run_sync(
            reasoning_agent,
            "Design a system for handling real-time data processing with multiple data sources."
        )
        
        # Handoff to code agent for implementation
        final_result = Runner.run_sync(
            code_agent,
            f"Implement the system design provided: {initial_result.final_output}"
        )
        
        assert final_result.final_output is not None
        print("✅ Agent Handoff test successful")
        return True
    except Exception as e:
        print(f"❌ Agent Handoff test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("\nTesting OpenAI Agents SDK Integration...\n")
    
    results = {
        "Code Agent": test_code_agent(),
        "Reasoning Agent": test_reasoning_agent(),
        "Agent Handoff": test_agent_handoff()
    }
    
    print("\nTest Results Summary:")
    print("-" * 30)
    for test, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {test}") 