from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime
from .model_service.model_selector import ModelSelector
from .agent_service.evaluation_manager import EvaluationManager, EvaluationCriteria
from .agent_service.consensus_manager import ConsensusManager, ConsensusType
from ..core.models.agent_communication import AgentCommunicationSystem, CoordinationPattern

class AgentOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_selector = ModelSelector('config/model_config.yaml')
        self.communication_system = AgentCommunicationSystem()
        self.evaluation_manager = EvaluationManager()
        self.consensus_manager = ConsensusManager(fault_tolerance=1)
        
        # Agent configurations with expertise levels
        self.agents = {
            'llama2_agent': {
                'model': 'llama2',
                'role': 'Problem solver with focus on code generation and architecture',
                'temperature': 0.7,
                'expertise': {
                    'code_quality': 0.8,
                    'architecture': 0.9,
                    'performance': 0.7,
                    'security': 0.6
                }
            },
            'mistral_agent': {
                'model': 'mistral',
                'role': 'Problem solver with focus on analysis and optimization',
                'temperature': 0.8,
                'expertise': {
                    'code_quality': 0.7,
                    'architecture': 0.6,
                    'performance': 0.9,
                    'security': 0.8
                }
            },
            'coordinator_agent': {
                'model': 'llama2',
                'role': 'Senior coordinator that evaluates and combines solutions',
                'temperature': 0.4,
                'expertise': {
                    'code_quality': 0.9,
                    'architecture': 0.8,
                    'performance': 0.8,
                    'security': 0.9
                }
            }
        }
        
        # Initialize agent weights based on expertise
        for agent_name, config in self.agents.items():
            avg_expertise = sum(config['expertise'].values()) / len(config['expertise'])
            self.consensus_manager.update_agent_weight(agent_name, avg_expertise)
            
    async def process_request(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request using multiple agents with enhanced consensus"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        participants = list(self.agents.keys())
        
        # Start consensus process for task planning with PBFT
        planning_result = await self.consensus_manager.start_consensus(
            consensus_id=f"{task_id}_planning",
            participants=participants,
            initial_value={
                'prompt': prompt,
                'context': context,
                'proposed_approach': None
            },
            consensus_type=ConsensusType.PBFT
        )
        
        if not planning_result:
            self.logger.error("Failed to reach consensus on task planning")
            return {'error': 'Consensus failure in task planning'}
            
        # Generate and evaluate responses from each agent
        responses = {}
        evaluations = {}
        for agent_name in participants:
            response = await self._generate_agent_response(agent_name, prompt, context)
            responses[agent_name] = response
            
            # Evaluate response using enhanced criteria
            evaluation = self.evaluation_manager.evaluate_solution(
                solution=response,
                agent_expertise=self.agents[agent_name]['expertise'],
                context=context
            )
            evaluations[agent_name] = evaluation
            
            # Update agent's reliability based on evaluation
            self.consensus_manager.update_reliability(
                agent_name,
                evaluation['overall_score'] > 0.7
            )
            
        # Use weighted voting for solution selection
        solution_consensus = await self.consensus_manager.start_consensus(
            consensus_id=f"{task_id}_solution",
            participants=participants,
            initial_value={
                'responses': responses,
                'evaluations': evaluations
            },
            consensus_type=ConsensusType.WEIGHTED_VOTING
        )
        
        if not solution_consensus:
            self.logger.error("Failed to reach consensus on solution selection")
            return {'error': 'Consensus failure in solution selection'}
            
        # Get final solution through PBFT for critical decisions
        final_solution = await self._reach_consensus(task_id, responses, evaluations)
        
        # Start coordination for implementation
        await self.communication_system.start_coordination(
            task_id=f"{task_id}_impl",
            coordinator_id='coordinator_agent',
            participants=participants,
            task_type=CoordinationPattern.WORK_DISTRIBUTION,
            parameters={
                'solution': final_solution,
                'context': context,
                'evaluations': evaluations
            }
        )
        
        return final_solution
        
    async def _reach_consensus(self, 
                             task_id: str, 
                             responses: Dict[str, Any],
                             evaluations: Dict[str, Any]) -> Dict[str, Any]:
        """Reach consensus on the best solution using enhanced mechanisms"""
        # Use PBFT for critical decisions
        consensus_result = await self.consensus_manager.start_consensus(
            consensus_id=f"{task_id}_final",
            participants=list(self.agents.keys()),
            initial_value={
                'responses': responses,
                'evaluations': evaluations,
                'evaluation_criteria': [c.value for c in EvaluationCriteria]
            },
            consensus_type=ConsensusType.PBFT
        )
        
        if not consensus_result:
            # Fallback to weighted voting if PBFT fails
            consensus_result = await self.consensus_manager.start_consensus(
                consensus_id=f"{task_id}_final_fallback",
                participants=list(self.agents.keys()),
                initial_value={
                    'responses': responses,
                    'evaluations': evaluations
                },
                consensus_type=ConsensusType.WEIGHTED_VOTING
            )
            
        if not consensus_result:
            raise ValueError("Failed to reach consensus after multiple attempts")
            
        # Select best solution based on consensus and evaluations
        best_solution = max(
            responses.items(),
            key=lambda x: evaluations[x[0]]['overall_score']
        )[1]
        
        # Get review and enhancements
        review_feedback = await self._generate_agent_response(
            'coordinator_agent',
            f"Review and enhance solution: {best_solution['response']}",
            {'original_responses': responses, 'evaluations': evaluations}
        )
        
        return {
            'solution': best_solution['response'],
            'enhancements': review_feedback['response'],
            'consensus_score': evaluations[best_solution['agent']]['overall_score'],
            'contributing_agents': list(responses.keys()),
            'evaluation_details': evaluations[best_solution['agent']],
            'consensus_type': 'pbft' if consensus_result else 'weighted_voting'
        }
        
    async def _generate_agent_response(
        self,
        agent_name: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a response from a specific agent"""
        agent_config = self.agents[agent_name]
        
        # Select appropriate model
        model_config = await self.model_selector.select_model(
            task=context.get('task_type', 'general'),
            agent_type=agent_name
        )
        
        # Generate response using selected model
        response = await self._execute_with_model(
            model_config['model'],
            prompt,
            agent_config['temperature'],
            context
        )
        
        return {
            'agent': agent_name,
            'model': model_config['model'],
            'response': response,
            'expertise': agent_config['expertise'],
            'confidence': self._calculate_confidence(response)
        }
        
    def _calculate_confidence(self, response: str) -> float:
        """Calculate confidence score for a response"""
        # Implement confidence calculation based on response characteristics
        return 0.8
        
    async def _execute_with_model(
        self,
        model: str,
        prompt: str,
        temperature: float,
        context: Dict[str, Any]
    ) -> str:
        """Execute prompt with selected model"""
        # Implement model execution
        return "Model response placeholder"