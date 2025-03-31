import logging
from typing import Dict, Any, Optional, List
import aiohttp
from ..models.language_models import AIModel
from ..config import settings

logger = logging.getLogger(__name__)

class AIProviderRegistry:
    def __init__(self):
        self.models: Dict[str, AIModel] = {}
        self._load_ai_models()

    def _load_ai_models(self):
        """Load AI model configurations from settings."""
        try:
            model_configs = settings.AI_MODELS
            for task, config in model_configs.items():
                self.models[task] = AIModel(
                    name=config["name"],
                    provider=config["provider"],
                    endpoint=config["endpoint"],
                    api_key=config.get("api_key"),
                    capabilities=config.get("capabilities", {}),
                    parameters=config.get("parameters", {})
                )
        except Exception as e:
            logger.error(f"Error loading AI models: {str(e)}")
            raise

    def get_model(self, task: str) -> Optional[AIModel]:
        """Get the AI model for a specific task."""
        return self.models.get(task)

    async def analyze_code(
        self,
        code: str,
        language: str,
        task: str,
        cursor_position: Optional[Dict[str, int]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze code using the appropriate AI model."""
        model = self.get_model(task)
        if not model:
            raise RuntimeError(f"No AI model available for task: {task}")

        try:
            # Prepare the analysis request
            request_data = {
                "code": code,
                "language": language,
                "task": task,
                "cursor_position": cursor_position,
                "context": context
            }

            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    model.endpoint,
                    json=request_data,
                    headers=self._get_headers(model)
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f"AI model request failed: {await response.text()}")
                    
                    result = await response.json()
                    return self._process_result(result, task)

        except Exception as e:
            logger.error(f"Error in analyze_code: {str(e)}")
            raise

    def _get_headers(self, model: AIModel) -> Dict[str, str]:
        """Get headers for the AI model request."""
        headers = {
            "Content-Type": "application/json"
        }
        if model.api_key:
            headers["Authorization"] = f"Bearer {model.api_key}"
        return headers

    def _process_result(self, result: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Process and format the AI model result based on the task."""
        if task == "linting":
            return {
                "diagnostics": result.get("diagnostics", []),
                "style_issues": result.get("style_issues", [])
            }
        elif task == "formatting":
            return {
                "formatted_code": result.get("formatted_code", ""),
                "changes": result.get("changes", [])
            }
        elif task == "completion":
            return {
                "suggestions": result.get("suggestions", []),
                "trigger_character": result.get("trigger_character")
            }
        elif task == "hover":
            return {
                "contents": result.get("contents", []),
                "range": result.get("range")
            }
        elif task == "definition":
            return {
                "locations": result.get("locations", []),
                "symbol": result.get("symbol")
            }
        elif task == "analysis":
            return {
                "insights": result.get("insights", []),
                "suggestions": result.get("suggestions", []),
                "warnings": result.get("warnings", []),
                "metrics": result.get("metrics", {})
            }
        else:
            return result

    async def generate_documentation(
        self,
        code: str,
        language: str,
        style: str = "standard"
    ) -> Dict[str, Any]:
        """Generate documentation for code using AI."""
        return await self.analyze_code(
            code=code,
            language=language,
            task="documentation",
            context={"style": style}
        )

    async def detect_bugs(
        self,
        code: str,
        language: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Detect potential bugs in code using AI."""
        return await self.analyze_code(
            code=code,
            language=language,
            task="bug_detection",
            context=context
        )

    async def generate_tests(
        self,
        code: str,
        language: str,
        framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate tests for code using AI."""
        return await self.analyze_code(
            code=code,
            language=language,
            task="test_generation",
            context={"framework": framework}
        )

    async def translate_code(
        self,
        code: str,
        source_language: str,
        target_language: str
    ) -> Dict[str, Any]:
        """Translate code between languages using AI."""
        return await self.analyze_code(
            code=code,
            language=source_language,
            task="translation",
            context={"target_language": target_language}
        )

    async def optimize_code(
        self,
        code: str,
        language: str,
        optimization_type: str = "performance"
    ) -> Dict[str, Any]:
        """Optimize code using AI."""
        return await self.analyze_code(
            code=code,
            language=language,
            task="optimization",
            context={"type": optimization_type}
        ) 