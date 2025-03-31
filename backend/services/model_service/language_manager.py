from typing import Dict, Optional, List
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LanguageManager:
    def __init__(self, config: Dict):
        self.config = config
        self.language_patterns = {
            'python': [r'\.py$', r'requirements\.txt$', r'setup\.py$'],
            'javascript': [r'\.js$', r'\.jsx$', r'\.ts$', r'\.tsx$', r'package\.json$'],
            'rust': [r'\.rs$', r'Cargo\.toml$'],
            'go': [r'\.go$', r'go\.mod$'],
            'java': [r'\.java$', r'pom\.xml$', r'build\.gradle$']
        }
        self.framework_patterns = {
            'django': [r'manage\.py$', r'wsgi\.py$', r'asgi\.py$'],
            'fastapi': [r'fastapi', r'pydantic'],
            'flask': [r'flask'],
            'react': [r'react', r'jsx', r'tsx'],
            'vue': [r'vue'],
            'next': [r'next\.config\.js$'],
            'spring': [r'@SpringBootApplication', r'@Controller'],
            'quarkus': [r'quarkus'],
            'actix': [r'actix_web'],
            'tokio': [r'tokio'],
            'gin': [r'gin-gonic/gin'],
            'fiber': [r'gofiber/fiber']
        }
        
    def detect_language(self, file_path: str, file_content: str = None) -> Optional[str]:
        """Detect programming language from file path and optionally content"""
        path = Path(file_path)
        
        # Check file extension patterns
        for lang, patterns in self.language_patterns.items():
            if any(re.search(pattern, str(path), re.IGNORECASE) for pattern in patterns):
                return lang
                
        # If content is provided, do deeper analysis
        if file_content:
            return self._detect_from_content(file_content)
                
        return None
        
    def detect_framework(self, file_path: str, file_content: str) -> Optional[str]:
        """Detect framework from file content and path"""
        for framework, patterns in self.framework_patterns.items():
            # Check file patterns
            if any(re.search(pattern, file_path, re.IGNORECASE) for pattern in patterns):
                return framework
                
            # Check content patterns
            if any(re.search(pattern, file_content, re.IGNORECASE) for pattern in patterns):
                return framework
                
        return None
        
    def get_language_model(self, language: str, framework: Optional[str] = None) -> Dict:
        """Get appropriate model for language and framework"""
        lang_config = self.config.get('language_specific', {}).get(language, {})
        if not lang_config:
            return self._get_default_model()
            
        # If framework is specified and exists in config, use it
        if framework and framework in lang_config.get('frameworks', {}):
            return {
                'model': lang_config['frameworks'][framework],
                'reason': f'Specialized model for {framework} framework'
            }
            
        # Use language-specific primary model
        return {
            'model': lang_config['primary'],
            'fallback': lang_config.get('fallback'),
            'reason': f'Primary model for {language}'
        }
        
    def _detect_from_content(self, content: str) -> Optional[str]:
        """Detect language from file content"""
        # Common language-specific patterns
        patterns = {
            'python': [r'import \w+', r'from \w+ import', r'def \w+\('],
            'javascript': [r'const \w+', r'let \w+', r'function \w+\(', r'=>'],
            'rust': [r'fn \w+\(', r'use \w+::', r'impl \w+'],
            'go': [r'package \w+', r'func \w+\(', r'import \('],
            'java': [r'public class', r'private \w+', r'package \w+']
        }
        
        scores = {lang: 0 for lang in patterns.keys()}
        
        for lang, lang_patterns in patterns.items():
            for pattern in lang_patterns:
                matches = re.findall(pattern, content)
                scores[lang] += len(matches)
                
        if not scores:
            return None
            
        # Return language with highest score
        return max(scores.items(), key=lambda x: x[1])[0]
        
    def _get_default_model(self) -> Dict:
        """Get default model when language/framework specific one isn't available"""
        return {
            'model': 'codellama-13b',
            'fallback': 'deepseek-coder-6.7b',
            'reason': 'Default code generation model'
        }
        
    def get_language_specific_prompts(self, language: str, framework: Optional[str] = None) -> Dict:
        """Get language and framework specific prompt templates"""
        prompts = {
            'python': {
                'code_style': 'Follow PEP 8 guidelines\nUse type hints\nInclude docstrings',
                'best_practices': ['Use context managers for files', 'Handle exceptions properly'],
                'testing': 'Use pytest for testing\nInclude test fixtures'
            },
            'javascript': {
                'code_style': 'Use ES6+ features\nFollow Airbnb style guide',
                'best_practices': ['Use async/await', 'Implement proper error handling'],
                'testing': 'Use Jest for testing\nImplement component tests'
            },
            'rust': {
                'code_style': 'Follow Rust style guidelines\nUse proper error handling',
                'best_practices': ['Implement proper traits', 'Use Option and Result types'],
                'testing': 'Include unit tests\nUse test modules'
            }
        }
        
        framework_prompts = {
            'django': {
                'code_style': 'Follow Django coding style\nUse class-based views',
                'best_practices': ['Implement proper models', 'Use Django REST framework'],
                'testing': 'Use Django test client\nImplement model tests'
            },
            'react': {
                'code_style': 'Use functional components\nImplement proper prop types',
                'best_practices': ['Use React hooks', 'Implement proper state management'],
                'testing': 'Use React Testing Library\nTest component behavior'
            }
        }
        
        result = prompts.get(language, {})
        if framework:
            result.update(framework_prompts.get(framework, {}))
            
        return result
