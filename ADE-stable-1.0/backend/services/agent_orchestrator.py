import asyncio
from typing import Dict, List, Any, Optional
from .llm_service import llm_service
import logging
from prometheus_client import Counter, Histogram, Gauge

# Metrics
AGENT_REQUESTS = Counter('agent_requests_total', 'Total number of agent requests', ['agent'])
AGENT_LATENCY = Histogram('agent_latency_seconds', 'Agent request latency', ['agent'])
AGENT_ACTIVE = Gauge('agent_active_total', 'Number of active agents', ['type'])

class AgentOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents = {
            'llama2_agent': {
                'model': 'llama2',
                'role': 'Problem solver with focus on code generation and architecture',
                'temperature': 0.7
            },
            'mistral_agent': {
                'model': 'mistral',
                'role': 'Problem solver with focus on analysis and optimization',
                'temperature': 0.8
            },
            'coordinator_agent': {
                'model': 'llama2',  # Using Llama 2 for coordination due to its strong reasoning
                'role': 'Senior coordinator that evaluates and combines solutions',
                'temperature': 0.4  # Lower temperature for more focused responses
            }
        }
        
        # Workflow agents to prevent stalls
        self.workflow_agents = {
            'initiative_agent': {
                'model': 'mistral',
                'role': 'Proactively identifies next steps and initiates actions',
                'temperature': 0.6
            },
            'progress_agent': {
                'model': 'llama2',
                'role': 'Monitors progress and suggests unblocking actions',
                'temperature': 0.6
            }
        }

        AGENT_ACTIVE.labels(type='solver').set(len(self.agents) - 1)  # Excluding coordinator
        AGENT_ACTIVE.labels(type='workflow').set(len(self.workflow_agents))

    async def _generate_agent_response(
        self,
        agent_name: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a response from a specific agent."""
        agent = self.agents.get(agent_name) or self.workflow_agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")

        AGENT_REQUESTS.labels(agent=agent_name).inc()
        
        # Construct agent-specific prompt
        agent_prompt = f"""Role: {agent['role']}
Context: {context.get('task_description', '')}
Previous Solutions: {context.get('previous_solutions', [])}
Current Task: {prompt}

Generate a solution based on your expertise and role."""

        try:
            response = await llm_service.generate_completion(
                prompt=agent_prompt,
                model=agent['model'],
                temperature=agent['temperature'],
                max_tokens=2000
            )
            
            return {
                'agent': agent_name,
                'response': response['text'],
                'model': agent['model'],
                'metrics': {
                    'latency': response['latency'],
                    'tokens': response['usage']['totalTokens']
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating response from {agent_name}: {str(e)}")
            raise

    async def _coordinate_solutions(
        self,
        solutions: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Have the coordinator agent evaluate and combine solutions."""
        solutions_text = "\n\n".join([
            f"Solution from {s['agent']} ({s['model']}):\n{s['response']}"
            for s in solutions
        ])

        coordinator_prompt = f"""As a senior coordinator, evaluate the following solutions:

{solutions_text}

Context: {context.get('task_description', '')}

1. Analyze each solution's strengths and weaknesses
2. Identify the best elements from each solution
3. Provide a final recommended solution that combines the best approaches
4. Explain your reasoning

Provide your response in a structured format."""

        response = await llm_service.generate_completion(
            prompt=coordinator_prompt,
            model=self.agents['coordinator_agent']['model'],
            temperature=self.agents['coordinator_agent']['temperature'],
            max_tokens=2000
        )

        return {
            'coordinator_analysis': response['text'],
            'solutions': solutions
        }

    async def _get_workflow_guidance(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get guidance from workflow agents to prevent stalls."""
        tasks = []
        
        # Get initiative agent's suggestion
        initiative_prompt = f"""Based on the current context:
{context.get('task_description', '')}
Current Progress: {context.get('progress_status', 'Not started')}

What should be the next immediate actions? Identify any potential blockers and suggest proactive steps."""

        tasks.append(self._generate_agent_response('initiative_agent', initiative_prompt, context))

        # Get progress agent's assessment
        progress_prompt = f"""Review the current progress:
{context.get('progress_status', 'Not started')}
Blockers: {context.get('blockers', [])}

Suggest specific actions to maintain momentum and overcome any obstacles."""

        tasks.append(self._generate_agent_response('progress_agent', progress_prompt, context))

        workflow_responses = await asyncio.gather(*tasks)
        
        return {
            'initiative_guidance': workflow_responses[0]['response'],
            'progress_assessment': workflow_responses[1]['response']
        }

    async def process_request(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a request using multiple agents and coordinate their responses."""
        # Get workflow guidance first
        workflow_guidance = await self._get_workflow_guidance(context)
        
        # Update context with workflow guidance
        context.update({
            'workflow_guidance': workflow_guidance
        })

        # Generate solutions from all agents in parallel
        tasks = [
            self._generate_agent_response(agent_name, prompt, context)
            for agent_name in self.agents
            if agent_name != 'coordinator_agent'
        ]

        solutions = await asyncio.gather(*tasks)
        
        # Have coordinator evaluate and combine solutions
        final_result = await self._coordinate_solutions(solutions, context)
        
        return {
            'workflow_guidance': workflow_guidance,
            'agent_solutions': solutions,
            'coordinator_result': final_result['coordinator_analysis']
        }

# Create singleton instance
agent_orchestrator = AgentOrchestrator() 