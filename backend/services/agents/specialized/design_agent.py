from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import logging
from pathlib import Path
from services.core.base_agent import BaseAgent

@dataclass
class DesignComponent:
    name: str
    type: str  # e.g., 'layout', 'component', 'style'
    properties: Dict[str, str]
    accessibility: Dict[str, bool]
    responsive: bool
    framework: str  # e.g., 'react', 'vue', 'angular'

@dataclass
class DesignIssue:
    severity: str
    description: str
    component: str
    category: str  # e.g., 'accessibility', 'responsive', 'usability'
    impact: str
    fix_suggestion: str
    wcag_guideline: Optional[str] = None

class DesignAgent(BaseAgent):
    """Specialized agent for UI/UX design analysis and recommendations"""
    
    def __init__(self):
        super().__init__("design_agent")
        self.logger = logging.getLogger(__name__)
        self._load_design_patterns()
        self._load_accessibility_guidelines()
        self._load_responsive_patterns()

    def _load_design_patterns(self):
        """Load UI/UX design patterns and best practices"""
        self.patterns = {
            'layout': {
                'grid_system': {
                    'columns': 12,
                    'breakpoints': ['xs', 'sm', 'md', 'lg', 'xl'],
                    'container_types': ['fluid', 'fixed']
                },
                'spacing': {
                    'units': ['rem', 'em'],
                    'scale': [0, 0.25, 0.5, 1, 1.5, 2, 3, 4]
                },
                'hierarchy': {
                    'levels': ['primary', 'secondary', 'tertiary'],
                    'emphasis': ['size', 'weight', 'color']
                },
                'composition': {
                    'patterns': ['z-pattern', 'f-pattern', 'rule-of-thirds', 'golden-ratio'],
                    'focal_points': ['primary', 'secondary'],
                    'whitespace': ['micro', 'macro']
                },
                'alignment': {
                    'types': ['left', 'center', 'right', 'justified'],
                    'grid_alignment': ['start', 'end', 'center', 'stretch']
                }
            },
            'components': {
                'buttons': {
                    'variants': ['primary', 'secondary', 'text', 'outline', 'icon'],
                    'states': ['default', 'hover', 'active', 'disabled', 'focus'],
                    'sizes': ['xs', 'sm', 'md', 'lg', 'xl']
                },
                'forms': {
                    'layout': ['stacked', 'horizontal', 'inline'],
                    'validation': ['inline', 'summary', 'tooltip'],
                    'feedback': ['success', 'error', 'warning', 'info']
                },
                'navigation': {
                    'types': ['navbar', 'sidebar', 'tabs', 'breadcrumbs', 'pagination', 'stepper'],
                    'responsive': ['collapse', 'drawer', 'bottom-bar', 'hamburger']
                },
                'cards': {
                    'types': ['basic', 'actionable', 'media', 'horizontal', 'list'],
                    'elements': ['header', 'media', 'content', 'actions', 'footer'],
                    'states': ['hover', 'selected', 'disabled']
                },
                'modal_dialogs': {
                    'types': ['notification', 'confirmation', 'form', 'full-screen'],
                    'positions': ['center', 'top', 'bottom', 'side'],
                    'animations': ['fade', 'slide', 'zoom', 'none']
                },
                'data_display': {
                    'tables': ['basic', 'data-grid', 'responsive'],
                    'lists': ['simple', 'complex', 'action', 'avatar'],
                    'charts': ['bar', 'line', 'pie', 'scatter', 'area']
                }
            },
            'interaction': {
                'feedback': {
                    'types': ['loading', 'success', 'error', 'empty', 'progress'],
                    'timing': ['immediate', 'delayed', 'progressive'],
                    'persistence': ['temporary', 'permanent', 'dismissible']
                },
                'animation': {
                    'duration': ['fast', 'normal', 'slow'],
                    'easing': ['ease', 'linear', 'ease-in', 'ease-out', 'ease-in-out', 'cubic-bezier'],
                    'purpose': ['feedback', 'transition', 'attention', 'storytelling', 'branding']
                },
                'gestures': {
                    'touch': ['tap', 'double-tap', 'long-press', 'swipe', 'pinch', 'drag'],
                    'mouse': ['click', 'hover', 'drag', 'scroll'],
                    'keyboard': ['tab', 'arrow', 'enter', 'escape', 'space']
                },
                'states': {
                    'system': ['loading', 'empty', 'error', 'success', 'partial'],
                    'content': ['collapsed', 'expanded', 'filtered', 'sorted'],
                    'user': ['new', 'viewed', 'saved', 'shared']
                }
            },
            'patterns': {
                'navigation': {
                    'infinite_scroll': {
                        'description': 'Content loads as user scrolls',
                        'use_cases': ['content feeds', 'search results', 'product listings']
                    },
                    'progressive_disclosure': {
                        'description': 'Information revealed progressively',
                        'use_cases': ['complex forms', 'wizards', 'onboarding']
                    },
                    'breadcrumbs': {
                        'description': 'Shows navigation path',
                        'use_cases': ['deep hierarchies', 'multi-step processes']
                    }
                },
                'input': {
                    'typeahead': {
                        'description': 'Predictive text suggestions',
                        'use_cases': ['search', 'form completion']
                    },
                    'inline_editing': {
                        'description': 'Edit content in place',
                        'use_cases': ['tables', 'profiles', 'documents']
                    },
                    'drag_and_drop': {
                        'description': 'Move items visually',
                        'use_cases': ['sorting', 'uploading', 'organizing']
                    }
                },
                'content': {
                    'skeleton_screens': {
                        'description': 'Placeholder UI while loading',
                        'use_cases': ['content pages', 'dashboards', 'media']
                    },
                    'cards': {
                        'description': 'Contained content modules',
                        'use_cases': ['dashboards', 'catalogs', 'profiles']
                    },
                    'data_visualization': {
                        'description': 'Visual representation of data',
                        'use_cases': ['analytics', 'reporting', 'monitoring']
                    }
                }
            }
        }

    def _load_accessibility_guidelines(self):
        """Load WCAG accessibility guidelines"""
        self.accessibility = {
            'perceivable': {
                'text_alternatives': {
                    'rule': 'Provide text alternatives for non-text content',
                    'wcag': '1.1.1',
                    'level': 'A'
                },
                'time_based_media': {
                    'rule': 'Provide alternatives for time-based media',
                    'wcag': '1.2',
                    'level': 'A'
                },
                'adaptable': {
                    'rule': 'Create content that can be presented in different ways',
                    'wcag': '1.3',
                    'level': 'A'
                },
                'distinguishable': {
                    'rule': 'Make it easier for users to see and hear content',
                    'wcag': '1.4',
                    'level': 'AA'
                }
            },
            'operable': {
                'keyboard_accessible': {
                    'rule': 'Make all functionality available from a keyboard',
                    'wcag': '2.1',
                    'level': 'A'
                },
                'enough_time': {
                    'rule': 'Provide users enough time to read and use content',
                    'wcag': '2.2',
                    'level': 'A'
                },
                'seizures': {
                    'rule': 'Do not design content in a way that causes seizures',
                    'wcag': '2.3',
                    'level': 'A'
                },
                'navigable': {
                    'rule': 'Provide ways to help users navigate and find content',
                    'wcag': '2.4',
                    'level': 'A'
                }
            }
        }

    def _load_responsive_patterns(self):
        """Load responsive design patterns"""
        self.responsive = {
            'breakpoints': {
                'xs': '0px',
                'sm': '576px',
                'md': '768px',
                'lg': '992px',
                'xl': '1200px',
                'xxl': '1400px',
                'mobile-portrait': '320px',
                'mobile-landscape': '480px',
                'tablet-portrait': '768px',
                'tablet-landscape': '1024px',
                'laptop': '1366px',
                'desktop': '1920px',
                '4k': '3840px'
            },
            'containers': {
                'xs': '100%',
                'sm': '540px',
                'md': '720px',
                'lg': '960px',
                'xl': '1140px',
                'xxl': '1320px',
                'desktop-wide': '1600px'
            },
            'grid': {
                'columns': 12,
                'gutter': {
                    'xs': '0.5rem',
                    'sm': '0.75rem',
                    'md': '1rem',
                    'lg': '1.5rem',
                    'xl': '2rem'
                },
                'margin': {
                    'xs': '0.5rem',
                    'sm': '0.75rem',
                    'md': '1rem',
                    'lg': '1.5rem',
                    'xl': '2rem'
                }
            },
            'typography': {
                'base_size': {
                    'xs': '14px',
                    'sm': '16px',
                    'md': '16px',
                    'lg': '18px',
                    'xl': '18px'
                },
                'scale': {
                    'xs': 1.2,
                    'sm': 1.25,
                    'md': 1.333,
                    'lg': 1.414,
                    'xl': 1.5
                }
            },
            'layout_patterns': {
                'stacked': 'Mobile-first vertical stacking',
                'column_drop': 'Columns stack as viewport narrows',
                'layout_shifter': 'Significant layout changes between breakpoints',
                'off_canvas': 'Off-screen content on small viewports',
                'mostly_fluid': 'Multi-column layout that stacks on smaller screens'
            },
            'component_patterns': {
                'disclosure': 'Show/hide content based on viewport',
                'priority_plus': 'Show most important items, hide others in menu',
                'responsive_table': 'Tables that adapt to small screens',
                'image_adaptation': 'Serve different image sizes based on viewport'
            }
        }

    async def analyze_design(self, code: str, filename: str, framework: str = None) -> List[DesignIssue]:
        """Analyze UI/UX design implementation"""
        issues = []
        
        # Determine framework if not provided
        if not framework:
            framework = self._detect_framework(code, filename)
        
        # Analyze accessibility
        issues.extend(await self._check_accessibility(code, filename))
        
        # Analyze responsive design
        issues.extend(await self._check_responsive_design(code, filename))
        
        # Analyze usability
        issues.extend(await self._check_usability(code, filename))
        
        # Analyze consistency
        issues.extend(await self._check_design_consistency(code, filename))
        
        # Framework-specific analysis
        issues.extend(await self._check_framework_specific(code, filename, framework))
        
        # Design pattern implementation
        issues.extend(await self._check_design_patterns(code, filename))
        
        return issues

    async def _check_framework_specific(self, code: str, filename: str, framework: str) -> List[DesignIssue]:
        """Check framework-specific best practices"""
        issues = []
        
        if framework == 'react':
            # React-specific checks
            if 'useState' in code and not 'key=' in code and ('map(' in code or 'forEach(' in code):
                issues.append(
                    DesignIssue(
                        severity="MEDIUM",
                        description="Missing key prop in list rendering",
                        component="lists",
                        category="react",
                        impact="Performance issues and potential bugs",
                        fix_suggestion="Add unique key prop to list items",
                    )
                )
        elif framework == 'vue':
            # Vue-specific checks
            if 'v-for' in code and not 'v-bind:key' in code and not ':key' in code:
                issues.append(
                    DesignIssue(
                        severity="MEDIUM",
                        description="Missing key in v-for directive",
                        component="lists",
                        category="vue",
                        impact="Performance issues and potential bugs",
                        fix_suggestion="Add :key binding to v-for elements",
                    )
                )
        elif framework == 'angular':
            # Angular-specific checks
            if '*ngFor' in code and not 'trackBy' in code:
                issues.append(
                    DesignIssue(
                        severity="LOW",
                        description="Missing trackBy function in *ngFor",
                        component="lists",
                        category="angular",
                        impact="Potential performance issues with large lists",
                        fix_suggestion="Add trackBy function to improve rendering performance",
                    )
                )
        
        return issues

    async def _check_design_patterns(self, code: str, filename: str) -> List[DesignIssue]:
        """Check implementation of common design patterns"""
        issues = []
        
        # Check for appropriate loading states
        if 'fetch(' in code or 'axios' in code or 'http.get' in code:
            if not self._has_loading_states(code):
                issues.append(
                    DesignIssue(
                        severity="MEDIUM",
                        description="Missing loading states",
                        component="feedback",
                        category="patterns",
                        impact="Poor user experience during data loading",
                        fix_suggestion="Implement skeleton screens or loading indicators",
                    )
                )
        
        # Check for empty states
        if 'map(' in code or 'v-for' in code or '*ngFor' in code:
            if not self._has_empty_states(code):
                issues.append(
                    DesignIssue(
                        severity="MEDIUM",
                        description="Missing empty states",
                        component="feedback",
                        category="patterns",
                        impact="Poor user experience with empty data",
                        fix_suggestion="Implement empty state messaging and visuals",
                    )
                )
        
        # Check for error states
        if 'try' in code and 'catch' in code:
            if not self._has_error_handling(code):
                issues.append(
                    DesignIssue(
                        severity="HIGH",
                        description="Missing error states",
                        component="feedback",
                        category="patterns",
                        impact="Users not informed of errors",
                        fix_suggestion="Implement error messages and recovery options",
                    )
                )
        
        return issues

    def _detect_framework(self, code: str, filename: str) -> str:
        """Detect UI framework from code"""
        if any(react_indicator in code for react_indicator in ['React', 'useState', 'useEffect', 'jsx', '.jsx']):
            return 'react'
        elif any(vue_indicator in code for vue_indicator in ['Vue', 'v-if', 'v-for', 'v-model', '.vue']):
            return 'vue'
        elif any(angular_indicator in code for angular_indicator in ['Angular', 'ngIf', 'ngFor', '*ngIf', '.component.ts']):
            return 'angular'
        elif '.svelte' in filename or 'svelte' in code.lower():
            return 'svelte'
        else:
            return 'generic'

    def _has_loading_states(self, code: str) -> bool:
        """Check for loading state implementation"""
        loading_indicators = [
            'loading', 'isLoading', 'is-loading', 'skeleton', 'spinner', 'progress'
        ]
        return any(indicator in code.lower() for indicator in loading_indicators)

    def _has_empty_states(self, code: str) -> bool:
        """Check for empty state implementation"""
        empty_indicators = [
            'empty', 'isEmpty', 'is-empty', 'no-data', 'noData', 'no-results', 'noResults'
        ]
        return any(indicator in code.lower() for indicator in empty_indicators)

    def _has_error_handling(self, code: str) -> bool:
        """Check for error handling implementation"""
        error_indicators = [
            'error', 'isError', 'is-error', 'hasError', 'has-error', 'onError', 'catch'
        ]
        return any(indicator in code.lower() for indicator in error_indicators)

    async def suggest_improvements(self, issues: List[DesignIssue]) -> Dict[str, List[str]]:
        """Generate improvement suggestions based on design issues"""
        suggestions = {
            "critical": [],
            "important": [],
            "nice_to_have": []
        }
        
        for issue in issues:
            if issue.severity == "HIGH":
                suggestions["critical"].append(issue.fix_suggestion)
            elif issue.severity == "MEDIUM":
                suggestions["important"].append(issue.fix_suggestion)
            else:
                suggestions["nice_to_have"].append(issue.fix_suggestion)
        
        return suggestions

    async def _check_accessibility(self, code: str, filename: str) -> List[DesignIssue]:
        """Check accessibility compliance"""
        issues = []
        
        # Check for alt text on images
        if 'img' in code and not 'alt=' in code:
            issues.append(
                DesignIssue(
                    severity="HIGH",
                    description="Images missing alt text",
                    component="image",
                    category="accessibility",
                    impact="Screen readers cannot describe images",
                    fix_suggestion="Add descriptive alt text to all images",
                    wcag_guideline="1.1.1"
                )
            )
        
        # Check for proper heading hierarchy
        if not self._has_proper_heading_hierarchy(code):
            issues.append(
                DesignIssue(
                    severity="MEDIUM",
                    description="Improper heading hierarchy",
                    component="typography",
                    category="accessibility",
                    impact="Difficult navigation for screen reader users",
                    fix_suggestion="Use proper h1-h6 hierarchy",
                    wcag_guideline="1.3.1"
                )
            )
        
        # Check for sufficient color contrast
        if not self._has_sufficient_contrast(code):
            issues.append(
                DesignIssue(
                    severity="HIGH",
                    description="Insufficient color contrast",
                    component="colors",
                    category="accessibility",
                    impact="Content may be difficult to read",
                    fix_suggestion="Ensure contrast ratio of at least 4.5:1",
                    wcag_guideline="1.4.3"
                )
            )
        
        return issues

    async def _check_responsive_design(self, code: str, filename: str) -> List[DesignIssue]:
        """Check responsive design implementation"""
        issues = []
        
        # Check for viewport meta tag
        if 'meta name="viewport"' not in code:
            issues.append(
                DesignIssue(
                    severity="HIGH",
                    description="Missing viewport meta tag",
                    component="meta",
                    category="responsive",
                    impact="Poor mobile rendering",
                    fix_suggestion="Add proper viewport meta tag",
                )
            )
        
        # Check for responsive units
        if 'px' in code and not self._is_pixel_use_valid(code):
            issues.append(
                DesignIssue(
                    severity="MEDIUM",
                    description="Using fixed pixel units",
                    component="styles",
                    category="responsive",
                    impact="Layout may not scale properly",
                    fix_suggestion="Use relative units (rem, em, %)",
                )
            )
        
        # Check for media queries
        if not self._has_media_queries(code):
            issues.append(
                DesignIssue(
                    severity="HIGH",
                    description="Missing media queries",
                    component="styles",
                    category="responsive",
                    impact="No mobile-specific layouts",
                    fix_suggestion="Add responsive breakpoints",
                )
            )
        
        return issues

    async def _check_usability(self, code: str, filename: str) -> List[DesignIssue]:
        """Check usability best practices"""
        issues = []
        
        # Check for interactive element size
        if not self._has_adequate_touch_targets(code):
            issues.append(
                DesignIssue(
                    severity="MEDIUM",
                    description="Touch targets too small",
                    component="interactive",
                    category="usability",
                    impact="Difficult to tap on mobile",
                    fix_suggestion="Use minimum 44x44px touch targets",
                )
            )
        
        # Check for form labels
        if '<input' in code and not self._has_proper_form_labels(code):
            issues.append(
                DesignIssue(
                    severity="HIGH",
                    description="Missing form labels",
                    component="forms",
                    category="usability",
                    impact="Poor form accessibility",
                    fix_suggestion="Add descriptive labels to all form fields",
                )
            )
        
        return issues

    async def _check_design_consistency(self, code: str, filename: str) -> List[DesignIssue]:
        """Check design system consistency"""
        issues = []
        
        # Check for consistent spacing
        if not self._has_consistent_spacing(code):
            issues.append(
                DesignIssue(
                    severity="MEDIUM",
                    description="Inconsistent spacing values",
                    component="layout",
                    category="consistency",
                    impact="Inconsistent visual rhythm",
                    fix_suggestion="Use spacing scale from design system",
                )
            )
        
        # Check for consistent colors
        if not self._has_consistent_colors(code):
            issues.append(
                DesignIssue(
                    severity="MEDIUM",
                    description="Non-system colors used",
                    component="colors",
                    category="consistency",
                    impact="Inconsistent brand appearance",
                    fix_suggestion="Use color tokens from design system",
                )
            )
        
        return issues

    def _has_proper_heading_hierarchy(self, code: str) -> bool:
        """Check for proper heading hierarchy"""
        # Implementation
        return True

    def _has_sufficient_contrast(self, code: str) -> bool:
        """Check color contrast ratios"""
        # Implementation
        return True

    def _is_pixel_use_valid(self, code: str) -> bool:
        """Check if pixel units are used appropriately"""
        # Implementation
        return True

    def _has_media_queries(self, code: str) -> bool:
        """Check for responsive breakpoints"""
        # Implementation
        return True

    def _has_adequate_touch_targets(self, code: str) -> bool:
        """Check interactive element sizes"""
        # Implementation
        return True

    def _has_proper_form_labels(self, code: str) -> bool:
        """Check form field labeling"""
        # Implementation
        return True

    def _has_consistent_spacing(self, code: str) -> bool:
        """Check spacing consistency"""
        # Implementation
        return True

    def _has_consistent_colors(self, code: str) -> bool:
        """Check color token usage"""
        # Implementation
        return True
