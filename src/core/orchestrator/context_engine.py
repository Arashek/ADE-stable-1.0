from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from dataclasses import dataclass
from enum import Enum

from ..api.context_management import (
    ContextManagementAPI,
    ContextReference,
    ContextType,
    ContextSource,
    ContextInfluence
)

class ContextProcessingMode(Enum):
    PASSIVE = "passive"  # Only use context when explicitly referenced
    ACTIVE = "active"    # Actively incorporate relevant context
    AGGRESSIVE = "aggressive"  # Maximize context usage

@dataclass
class ContextProcessingResult:
    original_text: str
    processed_text: str
    applied_contexts: List[ContextReference]
    influence_scores: Dict[str, float]
    processing_time: float

class ContextEngine:
    def __init__(
        self,
        context_api: ContextManagementAPI,
        processing_mode: ContextProcessingMode = ContextProcessingMode.ACTIVE
    ):
        self.context_api = context_api
        self.processing_mode = processing_mode

    async def process_text(
        self,
        text: str,
        current_context: Optional[str] = None
    ) -> ContextProcessingResult:
        """Process text by incorporating relevant context."""
        start_time = datetime.now()
        
        # Get relevant contexts based on processing mode
        contexts = await self._get_relevant_contexts(text, current_context)
        
        # Process text with contexts
        processed_text = await self._apply_contexts(text, contexts)
        
        # Calculate influence scores
        influence_scores = await self._calculate_influence_scores(text, contexts)
        
        # Record context usage
        await self._record_context_usage(contexts, influence_scores)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ContextProcessingResult(
            original_text=text,
            processed_text=processed_text,
            applied_contexts=contexts,
            influence_scores=influence_scores,
            processing_time=processing_time
        )

    async def _get_relevant_contexts(
        self,
        text: str,
        current_context: Optional[str] = None
    ) -> List[ContextReference]:
        """Get relevant contexts based on processing mode."""
        if self.processing_mode == ContextProcessingMode.PASSIVE:
            # Only get explicitly referenced contexts
            return await self._get_explicit_references(text)
        
        # Get active contexts
        active_contexts = await self.context_api.get_active_contexts()
        
        if self.processing_mode == ContextProcessingMode.ACTIVE:
            # Get contexts with high relevance
            return await self._filter_by_relevance(active_contexts, text)
        
        # Aggressive mode: use all active contexts
        return active_contexts

    async def _get_explicit_references(self, text: str) -> List[ContextReference]:
        """Extract explicit context references from text."""
        # Implementation would parse text for explicit references
        # For example: @context_id, #context_tag, etc.
        return []

    async def _filter_by_relevance(
        self,
        contexts: List[ContextReference],
        text: str,
        threshold: float = 0.7
    ) -> List[ContextReference]:
        """Filter contexts by relevance score."""
        relevant_contexts = []
        for context in contexts:
            relevance = await self.context_api.analyze_context_relevance(
                context.id,
                text
            )
            if relevance["semantic_similarity"] >= threshold:
                relevant_contexts.append(context)
        return relevant_contexts

    async def _apply_contexts(
        self,
        text: str,
        contexts: List[ContextReference]
    ) -> str:
        """Apply contexts to text."""
        processed_text = text
        
        for context in contexts:
            # Apply context based on type
            if context.type == ContextType.CODE:
                processed_text = await self._apply_code_context(
                    processed_text,
                    context
                )
            elif context.type == ContextType.DOCUMENTATION:
                processed_text = await self._apply_doc_context(
                    processed_text,
                    context
                )
            # Add handling for other context types
        
        return processed_text

    async def _apply_code_context(
        self,
        text: str,
        context: ContextReference
    ) -> str:
        """Apply code context to text."""
        # Implementation would:
        # 1. Parse code context
        # 2. Identify relevant code sections
        # 3. Insert code references or snippets
        return text

    async def _apply_doc_context(
        self,
        text: str,
        context: ContextReference
    ) -> str:
        """Apply documentation context to text."""
        # Implementation would:
        # 1. Parse documentation
        # 2. Identify relevant sections
        # 3. Insert documentation references
        return text

    async def _calculate_influence_scores(
        self,
        text: str,
        contexts: List[ContextReference]
    ) -> Dict[str, float]:
        """Calculate influence scores for applied contexts."""
        scores = {}
        for context in contexts:
            relevance = await self.context_api.analyze_context_relevance(
                context.id,
                text
            )
            scores[context.id] = relevance["semantic_similarity"]
        return scores

    async def _record_context_usage(
        self,
        contexts: List[ContextReference],
        influence_scores: Dict[str, float]
    ):
        """Record usage of contexts."""
        for context in contexts:
            await self.context_api.record_context_usage(
                context.id,
                influence_scores.get(context.id, 0.0)
            )

    async def get_context_attribution(
        self,
        text: str,
        contexts: List[ContextReference]
    ) -> List[Dict[str, Any]]:
        """Generate attribution information for used contexts."""
        attributions = []
        for context in contexts:
            influence = await self.context_api.get_context_influence(context.id)
            if influence:
                attributions.append({
                    "context_id": context.id,
                    "title": context.title,
                    "type": context.type,
                    "influence_score": influence.influence_score,
                    "usage_count": influence.usage_count
                })
        return attributions

    async def analyze_context_effectiveness(
        self,
        context_id: str,
        time_range: Optional[Dict[str, datetime]] = None
    ) -> Dict[str, Any]:
        """Analyze the effectiveness of a context reference."""
        history = await self.context_api.get_context_history(
            context_id,
            limit=100  # Adjust based on needs
        )
        
        if time_range:
            history = [
                h for h in history
                if time_range["start"] <= h["timestamp"] <= time_range["end"]
            ]
        
        # Calculate effectiveness metrics
        total_uses = len(history)
        avg_influence = sum(h["influence_score"] for h in history) / total_uses if total_uses > 0 else 0
        
        return {
            "total_uses": total_uses,
            "average_influence": avg_influence,
            "usage_trend": self._calculate_usage_trend(history),
            "effectiveness_score": self._calculate_effectiveness_score(history)
        }

    def _calculate_usage_trend(
        self,
        history: List[Dict[str, Any]]
    ) -> float:
        """Calculate the trend in context usage over time."""
        if len(history) < 2:
            return 0.0
        
        # Simple linear regression for usage trend
        x = range(len(history))
        y = [h["influence_score"] for h in history]
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_xx = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        return slope

    def _calculate_effectiveness_score(
        self,
        history: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall effectiveness score for context."""
        if not history:
            return 0.0
        
        # Weight recent usage more heavily
        weights = [1.0 / (i + 1) for i in range(len(history))]
        total_weight = sum(weights)
        
        weighted_scores = [
            h["influence_score"] * w
            for h, w in zip(history, weights)
        ]
        
        return sum(weighted_scores) / total_weight 