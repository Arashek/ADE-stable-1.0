from typing import Dict, Any, Optional
from .registry import ModelRegistry

class ModelManager:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        
    async def load_model(self, name: str, device: str = "cuda") -> Optional[Any]:
        model_data = self.registry.get_model(name)
        if not model_data:
            raise ValueError(f"Model {name} not found")
            
        # Load model to specified device
        model = model_data["model"].to(device)
        return model
        
    async def unload_model(self, name: str) -> bool:
        if name in self.registry.models:
            del self.registry.models[name]
            return True
        return False
        
    async def get_model_info(self, name: str) -> Optional[Dict[str, Any]]:
        model_data = self.registry.get_model(name)
        if not model_data:
            return None
            
        return {
            "config": model_data["config"],
            "type": type(model_data["model"]).__name__,
            "device": getattr(model_data["model"], "device", None)
        } 