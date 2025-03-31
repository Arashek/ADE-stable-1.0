from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import logging
from datetime import datetime
from enum import Enum
import ast
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class InternationalizationType(Enum):
    """Types of internationalization analysis"""
    TRANSLATION = "translation"
    LOCALE = "locale"
    CULTURE = "culture"
    FORMATTING = "formatting"
    ENCODING = "encoding"
    RTL = "rtl"

class InternationalizationMetric(BaseModel):
    """Internationalization metric"""
    name: str
    value: float
    threshold: float
    status: str
    details: Dict[str, Any] = {}
    recommendations: List[str] = []

class InternationalizationResult(BaseModel):
    """Result of internationalization analysis"""
    internationalization_type: InternationalizationType
    metrics: Dict[str, InternationalizationMetric]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

@dataclass
class InternationalizationElement:
    """Information about an internationalization element"""
    element_type: str
    content: str
    locale: Optional[str]
    line_number: int
    column: int
    context: Optional[Dict[str, Any]] = None

class InternationalizationAnalyzer:
    """Analyzer for assessing code internationalization"""
    
    def __init__(self):
        self.analysis_history: List[InternationalizationResult] = []
        self.internationalization_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.analysis_metrics: Dict[str, Dict[str, float]] = {}
        self._initialize_patterns()
        self._initialize_internationalization_rules()
        
    def _initialize_patterns(self):
        """Initialize internationalization detection patterns"""
        # Translation patterns
        self.internationalization_patterns["translation"] = [
            {
                "pattern": r"gettext\(['\"]([^'\"]+)['\"]\)",
                "severity": "info",
                "description": "Translation function detected",
                "recommendation": "Review translation implementation"
            },
            {
                "pattern": r"_\(['\"]([^'\"]+)['\"]\)",
                "severity": "info",
                "description": "Translation shortcut detected",
                "recommendation": "Review translation implementation"
            }
        ]
        
        # Locale patterns
        self.internationalization_patterns["locale"] = [
            {
                "pattern": r"locale\.setlocale\([^)]+\)",
                "severity": "info",
                "description": "Locale setting detected",
                "recommendation": "Review locale handling"
            },
            {
                "pattern": r"babel\.Locale\([^)]+\)",
                "severity": "info",
                "description": "Babel locale detected",
                "recommendation": "Review locale handling"
            }
        ]
        
        # Culture patterns
        self.internationalization_patterns["culture"] = [
            {
                "pattern": r"datetime\.strftime\([^)]+\)",
                "severity": "info",
                "description": "Date formatting detected",
                "recommendation": "Review culture-specific formatting"
            },
            {
                "pattern": r"decimal\.Decimal\([^)]+\)",
                "severity": "info",
                "description": "Decimal handling detected",
                "recommendation": "Review number formatting"
            }
        ]
        
        # Formatting patterns
        self.internationalization_patterns["formatting"] = [
            {
                "pattern": r"format\([^)]+\)",
                "severity": "info",
                "description": "String formatting detected",
                "recommendation": "Review string formatting"
            },
            {
                "pattern": r"f\"[^\"]+\"",
                "severity": "info",
                "description": "F-string detected",
                "recommendation": "Review string formatting"
            }
        ]
        
        # Encoding patterns
        self.internationalization_patterns["encoding"] = [
            {
                "pattern": r"encode\(['\"]([^'\"]+)['\"]\)",
                "severity": "info",
                "description": "Encoding detected",
                "recommendation": "Review character encoding"
            },
            {
                "pattern": r"decode\(['\"]([^'\"]+)['\"]\)",
                "severity": "info",
                "description": "Decoding detected",
                "recommendation": "Review character encoding"
            }
        ]
        
        # RTL patterns
        self.internationalization_patterns["rtl"] = [
            {
                "pattern": r"dir=\"rtl\"",
                "severity": "info",
                "description": "RTL direction detected",
                "recommendation": "Review RTL support"
            },
            {
                "pattern": r"text-align:\s*right",
                "severity": "info",
                "description": "Right alignment detected",
                "recommendation": "Review text alignment"
            }
        ]
        
    def _initialize_internationalization_rules(self):
        """Initialize internationalization rules"""
        self.internationalization_rules = {
            InternationalizationType.TRANSLATION: [
                {
                    "name": "translation_coverage",
                    "threshold": 0.8,
                    "description": "Translation coverage score"
                },
                {
                    "name": "translation_quality",
                    "threshold": 0.8,
                    "description": "Translation quality score"
                },
                {
                    "name": "translation_consistency",
                    "threshold": 0.8,
                    "description": "Translation consistency score"
                }
            ],
            InternationalizationType.LOCALE: [
                {
                    "name": "locale_handling",
                    "threshold": 0.8,
                    "description": "Locale handling score"
                },
                {
                    "name": "locale_validation",
                    "threshold": 0.8,
                    "description": "Locale validation score"
                },
                {
                    "name": "locale_fallback",
                    "threshold": 0.8,
                    "description": "Locale fallback score"
                }
            ],
            InternationalizationType.CULTURE: [
                {
                    "name": "date_formatting",
                    "threshold": 0.8,
                    "description": "Date formatting score"
                },
                {
                    "name": "number_formatting",
                    "threshold": 0.8,
                    "description": "Number formatting score"
                },
                {
                    "name": "currency_formatting",
                    "threshold": 0.8,
                    "description": "Currency formatting score"
                }
            ],
            InternationalizationType.FORMATTING: [
                {
                    "name": "string_formatting",
                    "threshold": 0.8,
                    "description": "String formatting score"
                },
                {
                    "name": "plural_handling",
                    "threshold": 0.8,
                    "description": "Plural handling score"
                },
                {
                    "name": "gender_handling",
                    "threshold": 0.8,
                    "description": "Gender handling score"
                }
            ],
            InternationalizationType.ENCODING: [
                {
                    "name": "character_encoding",
                    "threshold": 0.8,
                    "description": "Character encoding score"
                },
                {
                    "name": "unicode_handling",
                    "threshold": 0.8,
                    "description": "Unicode handling score"
                },
                {
                    "name": "encoding_consistency",
                    "threshold": 0.8,
                    "description": "Encoding consistency score"
                }
            ],
            InternationalizationType.RTL: [
                {
                    "name": "rtl_support",
                    "threshold": 0.8,
                    "description": "RTL support score"
                },
                {
                    "name": "bidirectional_text",
                    "threshold": 0.8,
                    "description": "Bidirectional text score"
                },
                {
                    "name": "layout_adaptation",
                    "threshold": 0.8,
                    "description": "Layout adaptation score"
                }
            ]
        }
        
    def analyze_internationalization(
        self,
        code: str,
        file_path: str,
        internationalization_type: InternationalizationType,
        context: Optional[Dict[str, Any]] = None
    ) -> InternationalizationResult:
        """Analyze internationalization based on specified type"""
        try:
            # Initialize result
            result = InternationalizationResult(
                internationalization_type=internationalization_type,
                metrics={},
                issues=[],
                recommendations=[],
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "file_path": file_path,
                    "context": context or {}
                }
            )
            
            # Get internationalization rules for type
            rules = self.internationalization_rules.get(internationalization_type, [])
            
            # Parse code
            tree = ast.parse(code)
            
            # Perform analysis
            for rule in rules:
                metric = self._analyze_internationalization_metric(
                    rule["name"],
                    code,
                    tree,
                    rule["threshold"],
                    context
                )
                result.metrics[rule["name"]] = metric
                
                # Check for issues
                if metric.status != "good":
                    result.issues.append({
                        "metric": rule["name"],
                        "value": metric.value,
                        "threshold": rule["threshold"],
                        "status": metric.status,
                        "description": rule["description"]
                    })
                    
                # Add recommendations
                result.recommendations.extend(metric.recommendations)
                
            # Generate cross-metric recommendations
            result.recommendations.extend(
                self._generate_cross_metric_recommendations(result.metrics)
            )
            
            # Store in history
            self.analysis_history.append(result)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to analyze internationalization: {str(e)}")
            
    def _analyze_internationalization_metric(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        threshold: float,
        context: Optional[Dict[str, Any]] = None
    ) -> InternationalizationMetric:
        """Analyze specific internationalization metric"""
        try:
            # Calculate metric value
            value = self._calculate_metric_value(
                metric_name,
                code,
                tree,
                context
            )
            
            # Determine status
            status = self._determine_metric_status(value, threshold)
            
            # Generate recommendations
            recommendations = self._generate_metric_recommendations(
                metric_name,
                value,
                threshold,
                status
            )
            
            return InternationalizationMetric(
                name=metric_name,
                value=value,
                threshold=threshold,
                status=status,
                details={
                    "code": code,
                    "context": context
                },
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze internationalization metric {metric_name}: {str(e)}")
            return InternationalizationMetric(
                name=metric_name,
                value=0.0,
                threshold=threshold,
                status="error",
                details={"error": str(e)},
                recommendations=["Fix internationalization analysis error"]
            )
            
    def _calculate_metric_value(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate metric value"""
        if metric_name == "translation_coverage":
            return self._calculate_translation_coverage(code, tree)
        elif metric_name == "translation_quality":
            return self._calculate_translation_quality(code, tree)
        elif metric_name == "translation_consistency":
            return self._calculate_translation_consistency(code, tree)
        elif metric_name == "locale_handling":
            return self._calculate_locale_handling(code, tree)
        elif metric_name == "locale_validation":
            return self._calculate_locale_validation(code, tree)
        elif metric_name == "locale_fallback":
            return self._calculate_locale_fallback(code, tree)
        elif metric_name == "date_formatting":
            return self._calculate_date_formatting(code, tree)
        elif metric_name == "number_formatting":
            return self._calculate_number_formatting(code, tree)
        elif metric_name == "currency_formatting":
            return self._calculate_currency_formatting(code, tree)
        elif metric_name == "string_formatting":
            return self._calculate_string_formatting(code, tree)
        elif metric_name == "plural_handling":
            return self._calculate_plural_handling(code, tree)
        elif metric_name == "gender_handling":
            return self._calculate_gender_handling(code, tree)
        elif metric_name == "character_encoding":
            return self._calculate_character_encoding(code, tree)
        elif metric_name == "unicode_handling":
            return self._calculate_unicode_handling(code, tree)
        elif metric_name == "encoding_consistency":
            return self._calculate_encoding_consistency(code, tree)
        elif metric_name == "rtl_support":
            return self._calculate_rtl_support(code, tree)
        elif metric_name == "bidirectional_text":
            return self._calculate_bidirectional_text(code, tree)
        elif metric_name == "layout_adaptation":
            return self._calculate_layout_adaptation(code, tree)
        else:
            raise ValueError(f"Unknown metric: {metric_name}")
            
    def _determine_metric_status(self, value: float, threshold: float) -> str:
        """Determine metric status based on value and threshold"""
        if value >= threshold:
            return "good"
        elif value >= threshold * 0.8:
            return "warning"
        else:
            return "critical"
            
    def _generate_metric_recommendations(
        self,
        metric_name: str,
        value: float,
        threshold: float,
        status: str
    ) -> List[str]:
        """Generate recommendations for metric"""
        recommendations = []
        
        if status == "warning":
            recommendations.append(
                f"{metric_name} is slightly below threshold. Consider improving "
                f"internationalization implementation."
            )
        elif status == "critical":
            recommendations.append(
                f"{metric_name} is significantly below threshold. Immediate "
                f"internationalization improvements are recommended."
            )
            
        # Add specific recommendations based on metric
        if "translation" in metric_name and value < threshold:
            recommendations.append(
                "Translation issues detected. Review and improve translation "
                "implementation."
            )
        elif "locale" in metric_name and value < threshold:
            recommendations.append(
                "Locale issues detected. Review and improve locale handling."
            )
        elif "formatting" in metric_name and value < threshold:
            recommendations.append(
                "Formatting issues detected. Review and improve formatting "
                "implementation."
            )
        elif "encoding" in metric_name and value < threshold:
            recommendations.append(
                "Encoding issues detected. Review and improve character encoding "
                "handling."
            )
        elif "rtl" in metric_name and value < threshold:
            recommendations.append(
                "RTL issues detected. Review and improve RTL support."
            )
            
        return recommendations
        
    def _generate_cross_metric_recommendations(
        self,
        metrics: Dict[str, InternationalizationMetric]
    ) -> List[str]:
        """Generate recommendations based on multiple metrics"""
        recommendations = []
        
        # Check for multiple translation issues
        translation_metrics = [
            m for n, m in metrics.items()
            if any(p in n for p in ["translation"])
        ]
        if len(translation_metrics) > 1 and all(m.status == "critical" for m in translation_metrics):
            recommendations.append(
                "Multiple critical translation issues detected. Consider comprehensive "
                "translation improvements."
            )
            
        # Check for locale and formatting issues
        if ("locale_handling" in metrics and "date_formatting" in metrics and
            metrics["locale_handling"].status == "critical" and
            metrics["date_formatting"].status == "critical"):
            recommendations.append(
                "Critical locale and formatting issues detected. Consider improving "
                "both locale handling and date formatting."
            )
            
        # Check for encoding and RTL issues
        if ("character_encoding" in metrics and "rtl_support" in metrics and
            metrics["character_encoding"].status == "critical" and
            metrics["rtl_support"].status == "critical"):
            recommendations.append(
                "Critical encoding and RTL issues detected. Review both character "
                "encoding and RTL support."
            )
            
        return recommendations
        
    def get_analysis_history(self) -> List[InternationalizationResult]:
        """Get analysis history"""
        return self.analysis_history
        
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        if not self.analysis_history:
            return {}
            
        latest = self.analysis_history[-1]
        return {
            "internationalization_type": latest.internationalization_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.metrics.items()
            },
            "issue_count": len(latest.issues),
            "recommendation_count": len(latest.recommendations)
        }
        
    def get_internationalization_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get registered internationalization patterns"""
        return self.internationalization_patterns
        
    def get_analysis_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get internationalization analysis metrics"""
        return self.analysis_metrics
        
    def register_internationalization_pattern(
        self,
        issue_type: str,
        pattern: str,
        severity: str,
        description: str,
        recommendation: str
    ):
        """Register a new internationalization pattern"""
        if issue_type not in self.internationalization_patterns:
            self.internationalization_patterns[issue_type] = []
            
        self.internationalization_patterns[issue_type].append({
            "pattern": pattern,
            "severity": severity,
            "description": description,
            "recommendation": recommendation
        })
        
    # Metric calculation methods
    def _calculate_translation_coverage(self, code: str, tree: ast.AST) -> float:
        """Calculate translation coverage score"""
        try:
            # Find all string literals
            string_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Str):
                    string_nodes.append(node)
                    
            if not string_nodes:
                return 1.0  # No strings to translate
                
            # Count translated strings
            translated_count = 0
            for node in string_nodes:
                # Check if string is wrapped in translation function
                if isinstance(node.parent, ast.Call):
                    if isinstance(node.parent.func, ast.Name):
                        if node.parent.func.id in ['gettext', '_', 'translate']:
                            translated_count += 1
                            
            return translated_count / len(string_nodes) if string_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating translation coverage: {str(e)}")
            return 0.0
            
    def _calculate_translation_quality(self, code: str, tree: ast.AST) -> float:
        """Calculate translation quality score"""
        try:
            # Find all translation function calls
            translation_calls = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['gettext', '_', 'translate']:
                            translation_calls.append(node)
                            
            if not translation_calls:
                return 1.0  # No translations to check
                
            # Check translation quality
            quality_score = 0.0
            for call in translation_calls:
                # Check if string is properly formatted
                if isinstance(call.args[0], ast.Str):
                    string = call.args[0].s
                    # Check for proper string formatting
                    if '%' in string or '{' in string:
                        quality_score += 1.0
                    # Check for proper escaping
                    elif '\\' in string:
                        quality_score += 0.5
                    else:
                        quality_score += 1.0
                        
            return quality_score / len(translation_calls) if translation_calls else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating translation quality: {str(e)}")
            return 0.0
            
    def _calculate_translation_consistency(self, code: str, tree: ast.AST) -> float:
        """Calculate translation consistency score"""
        try:
            # Find all translation function calls
            translation_calls = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['gettext', '_', 'translate']:
                            translation_calls.append(node)
                            
            if not translation_calls:
                return 1.0  # No translations to check
                
            # Check translation consistency
            consistency_score = 0.0
            for call in translation_calls:
                # Check if translation function is used consistently
                if isinstance(call.func, ast.Name):
                    if call.func.id == 'gettext':  # Preferred method
                        consistency_score += 1.0
                    elif call.func.id == '_':  # Acceptable shortcut
                        consistency_score += 0.8
                    elif call.func.id == 'translate':  # Alternative method
                        consistency_score += 0.6
                        
            return consistency_score / len(translation_calls) if translation_calls else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating translation consistency: {str(e)}")
            return 0.0
            
    def _calculate_locale_handling(self, code: str, tree: ast.AST) -> float:
        """Calculate locale handling score"""
        try:
            # Find locale-related code
            locale_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['setlocale', 'getlocale', 'getdefaultlocale']:
                            locale_nodes.append(node)
                            
            if not locale_nodes:
                return 1.0  # No locale handling to check
                
            # Check locale handling quality
            handling_score = 0.0
            for node in locale_nodes:
                # Check for proper error handling
                if isinstance(node.parent, ast.Try):
                    handling_score += 1.0
                # Check for proper locale validation
                elif len(node.args) >= 2:  # Has locale category and locale name
                    handling_score += 0.8
                else:
                    handling_score += 0.5
                    
            return handling_score / len(locale_nodes) if locale_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating locale handling: {str(e)}")
            return 0.0
            
    def _calculate_locale_validation(self, code: str, tree: ast.AST) -> float:
        """Calculate locale validation score"""
        try:
            # Find locale validation code
            validation_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['getlocale', 'getdefaultlocale']:
                            validation_nodes.append(node)
                            
            if not validation_nodes:
                return 1.0  # No locale validation to check
                
            # Check locale validation quality
            validation_score = 0.0
            for node in validation_nodes:
                # Check for proper validation
                if isinstance(node.parent, ast.If):
                    validation_score += 1.0
                # Check for fallback handling
                elif isinstance(node.parent, ast.Try):
                    validation_score += 0.8
                else:
                    validation_score += 0.5
                    
            return validation_score / len(validation_nodes) if validation_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating locale validation: {str(e)}")
            return 0.0
            
    def _calculate_locale_fallback(self, code: str, tree: ast.AST) -> float:
        """Calculate locale fallback score"""
        try:
            # Find locale fallback code
            fallback_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['getlocale', 'getdefaultlocale']:
                            fallback_nodes.append(node)
                            
            if not fallback_nodes:
                return 1.0  # No locale fallback to check
                
            # Check locale fallback quality
            fallback_score = 0.0
            for node in fallback_nodes:
                # Check for proper fallback chain
                if isinstance(node.parent, ast.If):
                    fallback_score += 1.0
                # Check for default locale handling
                elif isinstance(node.parent, ast.Try):
                    fallback_score += 0.8
                else:
                    fallback_score += 0.5
                    
            return fallback_score / len(fallback_nodes) if fallback_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating locale fallback: {str(e)}")
            return 0.0
            
    def _calculate_date_formatting(self, code: str, tree: ast.AST) -> float:
        """Calculate date formatting score"""
        try:
            # Find date formatting code
            date_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['strftime', 'strptime']:
                            date_nodes.append(node)
                            
            if not date_nodes:
                return 1.0  # No date formatting to check
                
            # Check date formatting quality
            formatting_score = 0.0
            for node in date_nodes:
                # Check for proper format string
                if isinstance(node.args[0], ast.Str):
                    format_str = node.args[0].s
                    # Check for locale-aware formatting
                    if '%' in format_str:
                        formatting_score += 1.0
                    # Check for basic formatting
                    elif '{' in format_str:
                        formatting_score += 0.8
                    else:
                        formatting_score += 0.5
                        
            return formatting_score / len(date_nodes) if date_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating date formatting: {str(e)}")
            return 0.0
            
    def _calculate_number_formatting(self, code: str, tree: ast.AST) -> float:
        """Calculate number formatting score"""
        try:
            # Find number formatting code
            number_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['format', 'format_number']:
                            number_nodes.append(node)
                            
            if not number_nodes:
                return 1.0  # No number formatting to check
                
            # Check number formatting quality
            formatting_score = 0.0
            for node in number_nodes:
                # Check for proper format string
                if isinstance(node.args[0], ast.Str):
                    format_str = node.args[0].s
                    # Check for locale-aware formatting
                    if '%' in format_str:
                        formatting_score += 1.0
                    # Check for basic formatting
                    elif '{' in format_str:
                        formatting_score += 0.8
                    else:
                        formatting_score += 0.5
                        
            return formatting_score / len(number_nodes) if number_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating number formatting: {str(e)}")
            return 0.0
            
    def _calculate_currency_formatting(self, code: str, tree: ast.AST) -> float:
        """Calculate currency formatting score"""
        try:
            # Find currency formatting code
            currency_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['format_currency', 'format_money']:
                            currency_nodes.append(node)
                            
            if not currency_nodes:
                return 1.0  # No currency formatting to check
                
            # Check currency formatting quality
            formatting_score = 0.0
            for node in currency_nodes:
                # Check for proper format string
                if isinstance(node.args[0], ast.Str):
                    format_str = node.args[0].s
                    # Check for locale-aware formatting
                    if '%' in format_str:
                        formatting_score += 1.0
                    # Check for basic formatting
                    elif '{' in format_str:
                        formatting_score += 0.8
                    else:
                        formatting_score += 0.5
                        
            return formatting_score / len(currency_nodes) if currency_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating currency formatting: {str(e)}")
            return 0.0
            
    def _calculate_string_formatting(self, code: str, tree: ast.AST) -> float:
        """Calculate string formatting score"""
        try:
            # Find string formatting code
            string_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['format', 'format_string']:
                            string_nodes.append(node)
                            
            if not string_nodes:
                return 1.0  # No string formatting to check
                
            # Check string formatting quality
            formatting_score = 0.0
            for node in string_nodes:
                # Check for proper format string
                if isinstance(node.args[0], ast.Str):
                    format_str = node.args[0].s
                    # Check for locale-aware formatting
                    if '%' in format_str:
                        formatting_score += 1.0
                    # Check for basic formatting
                    elif '{' in format_str:
                        formatting_score += 0.8
                    else:
                        formatting_score += 0.5
                        
            return formatting_score / len(string_nodes) if string_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating string formatting: {str(e)}")
            return 0.0
            
    def _calculate_plural_handling(self, code: str, tree: ast.AST) -> float:
        """Calculate plural handling score"""
        try:
            # Find plural handling code
            plural_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['ngettext', 'pluralize']:
                            plural_nodes.append(node)
                            
            if not plural_nodes:
                return 1.0  # No plural handling to check
                
            # Check plural handling quality
            handling_score = 0.0
            for node in plural_nodes:
                # Check for proper plural forms
                if len(node.args) >= 3:  # Has singular, plural, and count
                    handling_score += 1.0
                # Check for basic plural handling
                elif len(node.args) >= 2:
                    handling_score += 0.8
                else:
                    handling_score += 0.5
                    
            return handling_score / len(plural_nodes) if plural_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating plural handling: {str(e)}")
            return 0.0
            
    def _calculate_gender_handling(self, code: str, tree: ast.AST) -> float:
        """Calculate gender handling score"""
        try:
            # Find gender handling code
            gender_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['pgettext', 'genderize']:
                            gender_nodes.append(node)
                            
            if not gender_nodes:
                return 1.0  # No gender handling to check
                
            # Check gender handling quality
            handling_score = 0.0
            for node in gender_nodes:
                # Check for proper gender forms
                if len(node.args) >= 3:  # Has context, singular, and plural
                    handling_score += 1.0
                # Check for basic gender handling
                elif len(node.args) >= 2:
                    handling_score += 0.8
                else:
                    handling_score += 0.5
                    
            return handling_score / len(gender_nodes) if gender_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating gender handling: {str(e)}")
            return 0.0
            
    def _calculate_character_encoding(self, code: str, tree: ast.AST) -> float:
        """Calculate character encoding score"""
        try:
            # Find character encoding code
            encoding_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['encode', 'decode']:
                            encoding_nodes.append(node)
                            
            if not encoding_nodes:
                return 1.0  # No character encoding to check
                
            # Check character encoding quality
            encoding_score = 0.0
            for node in encoding_nodes:
                # Check for proper encoding specification
                if isinstance(node.args[0], ast.Str):
                    encoding = node.args[0].s
                    # Check for UTF-8 encoding
                    if encoding.lower() in ['utf-8', 'utf8']:
                        encoding_score += 1.0
                    # Check for other Unicode encodings
                    elif encoding.lower().startswith('utf'):
                        encoding_score += 0.8
                    else:
                        encoding_score += 0.5
                        
            return encoding_score / len(encoding_nodes) if encoding_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating character encoding: {str(e)}")
            return 0.0
            
    def _calculate_unicode_handling(self, code: str, tree: ast.AST) -> float:
        """Calculate Unicode handling score"""
        try:
            # Find Unicode handling code
            unicode_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['encode', 'decode', 'normalize']:
                            unicode_nodes.append(node)
                            
            if not unicode_nodes:
                return 1.0  # No Unicode handling to check
                
            # Check Unicode handling quality
            handling_score = 0.0
            for node in unicode_nodes:
                # Check for proper Unicode handling
                if isinstance(node.args[0], ast.Str):
                    arg = node.args[0].s
                    # Check for Unicode normalization
                    if node.func.attr == 'normalize':
                        handling_score += 1.0
                    # Check for proper encoding/decoding
                    elif node.func.attr in ['encode', 'decode']:
                        handling_score += 0.8
                    else:
                        handling_score += 0.5
                        
            return handling_score / len(unicode_nodes) if unicode_nodes else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating Unicode handling: {str(e)}")
            return 0.0
            
    def _calculate_encoding_consistency(self, code: str, tree: ast.AST) -> float:
        """Calculate encoding consistency score"""
        try:
            # Find encoding-related code
            encoding_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['encode', 'decode']:
                            encoding_nodes.append(node)
                            
            if not encoding_nodes:
                return 1.0  # No encoding to check
                
            # Check encoding consistency
            consistency_score = 0.0
            encodings = set()
            for node in encoding_nodes:
                if isinstance(node.args[0], ast.Str):
                    encoding = node.args[0].s.lower()
                    encodings.add(encoding)
                    
            # Calculate consistency based on number of different encodings
            if len(encodings) == 0:
                consistency_score = 1.0
            elif len(encodings) == 1:
                consistency_score = 1.0
            elif len(encodings) == 2:
                consistency_score = 0.8
            else:
                consistency_score = 0.5
                
            return consistency_score
            
        except Exception as e:
            logger.error(f"Error calculating encoding consistency: {str(e)}")
            return 0.0
        
    def _calculate_rtl_support(self, code: str, tree: ast.AST) -> float:
        """Calculate RTL support score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_bidirectional_text(self, code: str, tree: ast.AST) -> float:
        """Calculate bidirectional text score"""
        # Implementation depends on the specific requirements
        return 0.8
        
    def _calculate_layout_adaptation(self, code: str, tree: ast.AST) -> float:
        """Calculate layout adaptation score"""
        # Implementation depends on the specific requirements
        return 0.8 