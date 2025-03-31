from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class DecisionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VOTING = "voting"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"

class ImpactLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class DecisionOption:
    id: str
    title: str
    description: str
    pros: List[str]
    cons: List[str]
    impact_analysis: Dict[str, float]
    votes: Dict[str, int]
    created_at: datetime
    updated_at: datetime

@dataclass
class DecisionPoint:
    id: str
    title: str
    description: str
    category: str
    status: DecisionStatus
    options: List[DecisionOption]
    impact_level: ImpactLevel
    created_at: datetime
    updated_at: datetime
    deadline: Optional[datetime]
    rationale: Optional[str]

class DecisionEngine:
    def __init__(self, project_store):
        self.project_store = project_store

    async def create_decision_point(self, decision_data: Dict[str, Any]) -> DecisionPoint:
        """Create a new decision point."""
        decision = DecisionPoint(
            id=decision_data['id'],
            title=decision_data['title'],
            description=decision_data['description'],
            category=decision_data['category'],
            status=DecisionStatus.PENDING,
            options=[],
            impact_level=decision_data.get('impact_level', ImpactLevel.MEDIUM),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deadline=decision_data.get('deadline'),
            rationale=None
        )
        await self.project_store.save_decision_point(decision)
        return decision

    async def get_decision_point(self, decision_id: str) -> Optional[DecisionPoint]:
        """Retrieve a decision point by ID."""
        return await self.project_store.get_decision_point(decision_id)

    async def update_decision_point(self, decision_id: str, decision_data: Dict[str, Any]) -> Optional[DecisionPoint]:
        """Update an existing decision point."""
        decision = await self.get_decision_point(decision_id)
        if not decision:
            return None

        for key, value in decision_data.items():
            if hasattr(decision, key):
                setattr(decision, key, value)
        
        decision.updated_at = datetime.now()
        await self.project_store.save_decision_point(decision)
        return decision

    async def add_decision_option(self, decision_id: str, option_data: Dict[str, Any]) -> Optional[DecisionOption]:
        """Add a new option to a decision point."""
        decision = await self.get_decision_point(decision_id)
        if not decision:
            return None

        option = DecisionOption(
            id=option_data['id'],
            title=option_data['title'],
            description=option_data['description'],
            pros=option_data['pros'],
            cons=option_data['cons'],
            impact_analysis=option_data.get('impact_analysis', {}),
            votes={'up': 0, 'down': 0},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        decision.options.append(option)
        decision.updated_at = datetime.now()
        await self.project_store.save_decision_point(decision)
        return option

    async def update_decision_option(self, decision_id: str, option_id: str, option_data: Dict[str, Any]) -> Optional[DecisionOption]:
        """Update an existing decision option."""
        decision = await self.get_decision_point(decision_id)
        if not decision:
            return None

        option = next((o for o in decision.options if o.id == option_id), None)
        if not option:
            return None

        for key, value in option_data.items():
            if hasattr(option, key):
                setattr(option, key, value)
        
        option.updated_at = datetime.now()
        decision.updated_at = datetime.now()
        await self.project_store.save_decision_point(decision)
        return option

    async def vote_on_option(self, decision_id: str, option_id: str, vote_type: str) -> bool:
        """Record a vote on a decision option."""
        decision = await self.get_decision_point(decision_id)
        if not decision:
            return False

        option = next((o for o in decision.options if o.id == option_id), None)
        if not option:
            return False

        if vote_type == 'up':
            option.votes['up'] += 1
        elif vote_type == 'down':
            option.votes['down'] += 1

        option.updated_at = datetime.now()
        decision.updated_at = datetime.now()
        await self.project_store.save_decision_point(decision)
        return True

    async def update_decision_status(self, decision_id: str, status: DecisionStatus) -> Optional[DecisionPoint]:
        """Update the status of a decision point."""
        decision = await self.get_decision_point(decision_id)
        if not decision:
            return None

        decision.status = status
        decision.updated_at = datetime.now()
        await self.project_store.save_decision_point(decision)
        return decision

    async def get_decision_impact(self, decision_id: str) -> Dict[str, Any]:
        """Calculate the impact analysis for a decision point."""
        decision = await self.get_decision_point(decision_id)
        if not decision:
            return {}

        impact_metrics = {
            'performance': 0,
            'scalability': 0,
            'maintainability': 0,
            'cost': 0
        }

        for option in decision.options:
            for metric, value in option.impact_analysis.items():
                if metric in impact_metrics:
                    impact_metrics[metric] += value

        # Average the impact metrics
        option_count = len(decision.options)
        if option_count > 0:
            for metric in impact_metrics:
                impact_metrics[metric] /= option_count

        return impact_metrics

    async def get_decision_history(self, project_id: str) -> List[Dict[str, Any]]:
        """Get the decision history for a project."""
        decisions = await self.project_store.get_project_decisions(project_id)
        return [
            {
                'id': d.id,
                'title': d.title,
                'status': d.status.value,
                'category': d.category,
                'created_at': d.created_at,
                'updated_at': d.updated_at,
                'rationale': d.rationale
            }
            for d in decisions
        ]

    async def get_pending_decisions(self, project_id: str) -> List[DecisionPoint]:
        """Get all pending decisions for a project."""
        decisions = await self.project_store.get_project_decisions(project_id)
        return [d for d in decisions if d.status in [DecisionStatus.PENDING, DecisionStatus.IN_PROGRESS]]

    async def get_decision_templates(self) -> List[Dict[str, Any]]:
        """Get predefined decision templates for common scenarios."""
        return [
            {
                'id': 'architecture_selection',
                'title': 'Architecture Selection',
                'description': 'Choose the system architecture approach',
                'category': 'architecture',
                'impact_level': ImpactLevel.HIGH,
                'options_template': [
                    {
                        'title': 'Monolithic',
                        'description': 'Traditional monolithic architecture',
                        'pros': ['Simple to develop', 'Easy to deploy'],
                        'cons': ['Limited scalability', 'Tight coupling']
                    },
                    {
                        'title': 'Microservices',
                        'description': 'Distributed microservices architecture',
                        'pros': ['Scalable', 'Independent deployment'],
                        'cons': ['Complex to manage', 'Network overhead']
                    }
                ]
            },
            {
                'id': 'tech_stack',
                'title': 'Technology Stack Selection',
                'description': 'Choose the technology stack for implementation',
                'category': 'technology',
                'impact_level': ImpactLevel.HIGH,
                'options_template': [
                    {
                        'title': 'Traditional Stack',
                        'description': 'Proven and stable technology stack',
                        'pros': ['Mature ecosystem', 'Well-documented'],
                        'cons': ['Less modern features', 'Limited innovation']
                    },
                    {
                        'title': 'Modern Stack',
                        'description': 'Latest technology stack with modern features',
                        'pros': ['Latest features', 'Better performance'],
                        'cons': ['Less stable', 'Limited community support']
                    }
                ]
            }
        ]

    async def apply_decision_template(self, decision_id: str, template_id: str) -> Optional[DecisionPoint]:
        """Apply a decision template to an existing decision point."""
        decision = await self.get_decision_point(decision_id)
        if not decision:
            return None

        templates = await self.get_decision_templates()
        template = next((t for t in templates if t['id'] == template_id), None)
        if not template:
            return None

        # Update decision with template data
        decision.title = template['title']
        decision.description = template['description']
        decision.category = template['category']
        decision.impact_level = template['impact_level']

        # Add template options
        for option_data in template['options_template']:
            await self.add_decision_option(decision_id, {
                'id': f"{decision_id}-{len(decision.options)}",
                **option_data
            })

        decision.updated_at = datetime.now()
        await self.project_store.save_decision_point(decision)
        return decision 