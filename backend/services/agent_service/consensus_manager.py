from typing import Dict, List, Any, Optional, Set
import asyncio
import time
import random
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class ConsensusType(Enum):
    PAXOS = "paxos"
    RAFT = "raft"
    PBFT = "pbft"  # Practical Byzantine Fault Tolerance
    WEIGHTED_VOTING = "weighted_voting"
    MULTI_PAXOS = "multi_paxos"
    HYBRID = "hybrid"

@dataclass
class ConsensusState:
    proposal_id: str
    value: Any
    phase: str
    proposer: str
    acceptors: Set[str]
    promises: Dict[str, Any]
    accepts: Dict[str, Any]
    quorum_size: int
    timestamp: datetime
    view_number: int = 0
    leader: Optional[str] = None
    term: int = 0

class ConsensusManager:
    def __init__(self, fault_tolerance: int = 1):
        self.states: Dict[str, ConsensusState] = {}
        self.fault_tolerance = fault_tolerance
        self.view_changes: Dict[str, Dict[str, Any]] = {}
        self.term_votes: Dict[str, Dict[str, int]] = {}
        self.agent_weights: Dict[str, float] = {}
        self.historical_reliability: Dict[str, float] = {}
        
    async def start_consensus(self,
                            consensus_id: str,
                            participants: List[str],
                            initial_value: Any,
                            consensus_type: ConsensusType = ConsensusType.HYBRID) -> Any:
        """Start a new consensus round"""
        if consensus_type == ConsensusType.HYBRID:
            # Use PBFT for critical decisions, weighted voting for others
            if self._is_critical_decision(initial_value):
                return await self._run_pbft(consensus_id, participants, initial_value)
            else:
                return await self._run_weighted_voting(consensus_id, participants, initial_value)
        elif consensus_type == ConsensusType.PBFT:
            return await self._run_pbft(consensus_id, participants, initial_value)
        elif consensus_type == ConsensusType.WEIGHTED_VOTING:
            return await self._run_weighted_voting(consensus_id, participants, initial_value)
        else:
            return await self._run_multi_paxos(consensus_id, participants, initial_value)
            
    async def _run_pbft(self, consensus_id: str, participants: List[str], value: Any) -> Any:
        """Run Practical Byzantine Fault Tolerance consensus"""
        state = self._initialize_state(consensus_id, participants, value)
        f = self.fault_tolerance
        
        # Require 3f + 1 replicas for Byzantine fault tolerance
        min_replicas = 3 * f + 1
        if len(participants) < min_replicas:
            raise ValueError(f"Need at least {min_replicas} participants for PBFT")
            
        # Phase 1: Pre-prepare
        pre_prepare_msg = {
            'type': 'pre-prepare',
            'view': state.view_number,
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        responses = await self._broadcast(participants, pre_prepare_msg)
        
        # Phase 2: Prepare
        if len(responses) >= 2 * f + 1:
            prepare_msg = {
                'type': 'prepare',
                'view': state.view_number,
                'value_hash': hash(str(value)),
                'timestamp': datetime.now().isoformat()
            }
            prepare_responses = await self._broadcast(participants, prepare_msg)
            
            # Phase 3: Commit
            if len(prepare_responses) >= 2 * f + 1:
                commit_msg = {
                    'type': 'commit',
                    'view': state.view_number,
                    'value_hash': hash(str(value)),
                    'timestamp': datetime.now().isoformat()
                }
                commit_responses = await self._broadcast(participants, commit_msg)
                
                if len(commit_responses) >= 2 * f + 1:
                    return value
                    
        # If consensus fails, initiate view change
        await self._initiate_view_change(state)
        return None
        
    async def _run_weighted_voting(self, 
                                 consensus_id: str, 
                                 participants: List[str], 
                                 value: Any) -> Any:
        """Run weighted voting consensus"""
        votes: Dict[str, float] = {}
        required_weight = sum(self.agent_weights.get(p, 1.0) for p in participants) * 0.67
        
        for participant in participants:
            weight = self.agent_weights.get(participant, 1.0)
            reliability = self.historical_reliability.get(participant, 0.5)
            
            # Apply dynamic weight adjustment
            adjusted_weight = weight * (0.5 + 0.5 * reliability)
            
            # Simulate participant voting
            vote_value = await self._get_participant_vote(participant, value)
            if vote_value in votes:
                votes[vote_value] += adjusted_weight
            else:
                votes[vote_value] = adjusted_weight
                
        # Find value with highest weighted votes
        winner = max(votes.items(), key=lambda x: x[1])
        if winner[1] >= required_weight:
            return winner[0]
            
        return None
        
    async def _run_multi_paxos(self, 
                              consensus_id: str, 
                              participants: List[str], 
                              value: Any) -> Any:
        """Run Multi-Paxos consensus"""
        state = self._initialize_state(consensus_id, participants, value)
        
        # Phase 1: Leader election
        if not state.leader:
            leader = await self._elect_leader(participants)
            state.leader = leader
            
        if state.leader:
            # Phase 2: Propose
            proposal = {
                'term': state.term,
                'value': value,
                'leader': state.leader
            }
            
            accept_count = 0
            for participant in participants:
                response = await self._send_proposal(participant, proposal)
                if response.get('accepted'):
                    accept_count += 1
                    
            # Need majority for consensus
            if accept_count > len(participants) / 2:
                return value
                
        return None
        
    def _initialize_state(self, 
                         consensus_id: str, 
                         participants: List[str], 
                         value: Any) -> ConsensusState:
        """Initialize consensus state"""
        if consensus_id not in self.states:
            self.states[consensus_id] = ConsensusState(
                proposal_id=f"prop_{int(time.time())}",
                value=value,
                phase="init",
                proposer=participants[0],
                acceptors=set(participants),
                promises={},
                accepts={},
                quorum_size=len(participants) // 2 + 1,
                timestamp=datetime.now()
            )
        return self.states[consensus_id]
        
    async def _initiate_view_change(self, state: ConsensusState):
        """Initiate view change protocol"""
        state.view_number += 1
        view_change_msg = {
            'type': 'view-change',
            'new_view': state.view_number,
            'last_value': state.value,
            'timestamp': datetime.now().isoformat()
        }
        
        responses = await self._broadcast(state.acceptors, view_change_msg)
        if len(responses) >= 2 * self.fault_tolerance + 1:
            # Start new view
            state.leader = self._select_new_leader(state.acceptors)
            state.phase = "init"
            
    def _is_critical_decision(self, value: Any) -> bool:
        """Determine if a decision is critical enough for PBFT"""
        if isinstance(value, dict):
            # Check for critical operations
            critical_keywords = {'security', 'payment', 'authentication', 'authorization'}
            value_str = str(value).lower()
            return any(keyword in value_str for keyword in critical_keywords)
        return False
        
    async def _broadcast(self, participants: List[str], message: Dict) -> List[Dict]:
        """Broadcast message to all participants"""
        # Simulate network communication
        responses = []
        for participant in participants:
            if random.random() > 0.2:  # 80% success rate
                responses.append({'from': participant, 'status': 'accepted'})
        return responses
        
    async def _get_participant_vote(self, participant: str, value: Any) -> Any:
        """Get vote from a participant"""
        # Simulate participant voting
        return value
        
    async def _elect_leader(self, participants: List[str]) -> Optional[str]:
        """Elect a leader using a weighted random selection"""
        weights = []
        for p in participants:
            base_weight = self.agent_weights.get(p, 1.0)
            reliability = self.historical_reliability.get(p, 0.5)
            weights.append(base_weight * reliability)
            
        total = sum(weights)
        if total == 0:
            return random.choice(participants)
            
        r = random.uniform(0, total)
        upto = 0
        for i, w in enumerate(weights):
            upto += w
            if upto >= r:
                return participants[i]
        return participants[-1]
        
    async def _send_proposal(self, participant: str, proposal: Dict) -> Dict:
        """Send proposal to a participant"""
        # Simulate proposal sending
        return {'accepted': random.random() > 0.2}
        
    def _select_new_leader(self, participants: Set[str]) -> str:
        """Select new leader based on reliability and weights"""
        return max(
            participants,
            key=lambda p: self.agent_weights.get(p, 1.0) * 
                        self.historical_reliability.get(p, 0.5)
        )
        
    def update_agent_weight(self, agent: str, performance: float):
        """Update agent's voting weight based on performance"""
        current_weight = self.agent_weights.get(agent, 1.0)
        # Exponential moving average with 0.1 learning rate
        self.agent_weights[agent] = 0.9 * current_weight + 0.1 * performance
        
    def update_reliability(self, agent: str, success: bool):
        """Update agent's reliability score"""
        current = self.historical_reliability.get(agent, 0.5)
        # Exponential moving average with 0.05 learning rate
        self.historical_reliability[agent] = (
            0.95 * current + 0.05 * (1.0 if success else 0.0)
        )
