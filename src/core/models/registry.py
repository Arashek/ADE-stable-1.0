from typing import Dict, Any, Optional

class ModelRegistry:
    def __init__(self):
        self.models: Dict[str, Any] = {}
        
    def register_model(self, name: str, model: Any, config: Dict[str, Any]):
        self.models[name] = {
            "model": model,
            "config": config
        }
        
    def get_model(self, name: str) -> Optional[Any]:
        return self.models.get(name)
        
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "config": data["config"],
                "type": type(data["model"]).__name__
            }
            for name, data in self.models.items()
        } 