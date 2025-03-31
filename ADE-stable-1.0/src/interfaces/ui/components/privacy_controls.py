from typing import Dict, List, Optional, Set
from datetime import datetime
import streamlit as st
from pydantic import BaseModel

from ...core.learning.models.privacy_settings import (
    PrivacySettings,
    PrivacyLevel,
    AttributionType,
    PatternType
)
from ...core.orchestrator import Orchestrator

class PrivacyControls:
    """UI component for privacy settings"""
    
    def __init__(self, orchestrator: Orchestrator):
        """
        Initialize privacy controls.
        
        Args:
            orchestrator: ADE orchestrator instance
        """
        self.orchestrator = orchestrator
    
    def render(self) -> None:
        """Render privacy controls"""
        st.header("Privacy Settings")
        
        # Get current settings
        settings = self.orchestrator.learning_manager.get_privacy_settings()
        
        # Enable/disable learning
        enabled = st.checkbox(
            "Enable Pattern Collection",
            value=settings.enabled,
            help="Enable or disable pattern collection for learning"
        )
        
        if enabled:
            # Privacy level selection
            privacy_level = st.selectbox(
                "Privacy Level",
                options=list(PrivacyLevel),
                index=list(PrivacyLevel).index(settings.privacy_level),
                help="Set the level of privacy protection"
            )
            
            # Attribution type selection
            attribution_type = st.selectbox(
                "Attribution Type",
                options=list(AttributionType),
                index=list(AttributionType).index(settings.attribution_type),
                help="Set how patterns are attributed"
            )
            
            # Pattern type selection
            st.subheader("Shared Pattern Types")
            pattern_types = {}
            for pt in PatternType:
                pattern_types[pt] = st.checkbox(
                    pt.value,
                    value=pt in settings.shared_pattern_types,
                    help=f"Enable or disable sharing of {pt.value} patterns"
                )
            
            # Project exclusions
            st.subheader("Excluded Projects")
            excluded_projects = st.text_area(
                "Project IDs (one per line)",
                value="\n".join(settings.excluded_projects),
                help="Enter project IDs to exclude from pattern collection"
            ).split("\n")
            
            # Language exclusions
            st.subheader("Excluded Languages")
            excluded_languages = st.text_area(
                "Languages (one per line)",
                value="\n".join(settings.excluded_languages),
                help="Enter programming languages to exclude from pattern collection"
            ).split("\n")
            
            # Custom parameters
            st.subheader("Custom Privacy Parameters")
            custom_params = {}
            for name, value in settings.custom_parameters.items():
                custom_params[name] = st.number_input(
                    name,
                    value=float(value),
                    help=f"Set custom privacy parameter {name}"
                )
            
            # Save button
            if st.button("Save Settings"):
                try:
                    # Create updated settings
                    new_settings = PrivacySettings(
                        enabled=enabled,
                        privacy_level=privacy_level,
                        attribution_type=attribution_type,
                        shared_pattern_types={
                            pt for pt, enabled in pattern_types.items() if enabled
                        },
                        excluded_projects=set(excluded_projects),
                        excluded_languages=set(excluded_languages),
                        custom_parameters=custom_params
                    )
                    
                    # Update settings
                    self.orchestrator.learning_manager.update_privacy_settings(
                        new_settings,
                        modified_by="ui"
                    )
                    
                    # Update user preferences
                    self.orchestrator.user_preferences.update_privacy_settings(
                        new_settings
                    )
                    
                    st.success("Privacy settings updated successfully")
                    
                except Exception as e:
                    st.error(f"Error updating privacy settings: {str(e)}")
            
            # Reset button
            if st.button("Reset to Defaults"):
                try:
                    self.orchestrator.learning_manager.privacy_manager.reset_to_defaults(
                        modified_by="ui"
                    )
                    st.success("Privacy settings reset to defaults")
                    
                except Exception as e:
                    st.error(f"Error resetting privacy settings: {str(e)}")
        
        # Display statistics
        st.subheader("Learning Statistics")
        stats = self.orchestrator.learning_manager.get_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Patterns",
                stats["total_patterns"]
            )
            st.metric(
                "Activities Processed",
                stats["total_activities_processed"]
            )
        
        with col2:
            st.metric(
                "Patterns Shared",
                stats["total_patterns_shared"]
            )
            st.metric(
                "Patterns Filtered",
                stats["total_patterns_filtered"]
            )
        
        with col3:
            st.metric(
                "Collection Errors",
                stats["collection_errors"]
            )
            st.metric(
                "Processing Errors",
                stats["processing_errors"]
            )
        
        # Display pattern type distribution
        st.subheader("Pattern Distribution")
        for pt, count in stats["patterns_by_type"].items():
            st.progress(
                count / max(stats["patterns_by_type"].values()) if stats["patterns_by_type"] else 0,
                text=f"{pt.value}: {count}"
            ) 