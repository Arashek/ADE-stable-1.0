from typing import Dict, Any, List, Optional
import inspect
import re
from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from .base import BaseDocumentationGenerator
from ...config.logging_config import logger

class APIDocumentationGenerator(BaseDocumentationGenerator):
    """Generator for API documentation using OpenAPI/Swagger"""
    
    def __init__(self, output_dir: str = "docs"):
        super().__init__(output_dir)
        self.openapi_version = "3.0.0"
        self.swagger_ui_version = "4.11.1"
        self.redoc_version = "2.0.0"
        
    def generate_api_docs(self, app: FastAPI, version: str = "1.0.0"):
        """Generate API documentation from FastAPI application"""
        try:
            self.version = version
            self.create_output_dirs()
            
            # Generate OpenAPI schema
            openapi_schema = self._generate_openapi_schema(app)
            
            # Generate Swagger UI documentation
            swagger_html = self._generate_swagger_ui(openapi_schema)
            
            # Generate ReDoc documentation
            redoc_html = self._generate_redoc(openapi_schema)
            
            # Generate markdown documentation
            markdown_docs = self._generate_markdown_docs(app)
            
            # Save documentation files
            self.save_file(
                json.dumps(openapi_schema, indent=2),
                "api/openapi.json"
            )
            self.save_file(swagger_html, "api/swagger.html")
            self.save_file(redoc_html, "api/redoc.html")
            self.save_file(markdown_docs, "api/api_docs.md")
            
            # Generate API version history
            self._generate_api_version_history(app)
            
            logger.info("API documentation generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating API documentation: {str(e)}")
            raise
            
    def _generate_openapi_schema(self, app: FastAPI) -> Dict[str, Any]:
        """Generate OpenAPI schema from FastAPI application"""
        try:
            return get_openapi(
                title=app.title,
                version=app.version,
                description=app.description,
                routes=app.routes,
                openapi_version=self.openapi_version
            )
        except Exception as e:
            logger.error(f"Error generating OpenAPI schema: {str(e)}")
            raise
            
    def _generate_swagger_ui(self, openapi_schema: Dict[str, Any]) -> str:
        """Generate Swagger UI HTML"""
        try:
            template = self.load_template("swagger.html")
            return template.render(
                openapi_schema=json.dumps(openapi_schema),
                swagger_ui_version=self.swagger_ui_version
            )
        except Exception as e:
            logger.error(f"Error generating Swagger UI: {str(e)}")
            raise
            
    def _generate_redoc(self, openapi_schema: Dict[str, Any]) -> str:
        """Generate ReDoc HTML"""
        try:
            template = self.load_template("redoc.html")
            return template.render(
                openapi_schema=json.dumps(openapi_schema),
                redoc_version=self.redoc_version
            )
        except Exception as e:
            logger.error(f"Error generating ReDoc: {str(e)}")
            raise
            
    def _generate_markdown_docs(self, app: FastAPI) -> str:
        """Generate markdown documentation"""
        try:
            template = self.load_template("api_markdown.md")
            endpoints = self._extract_endpoints(app)
            
            return template.render(
                title=app.title,
                version=app.version,
                description=app.description,
                endpoints=endpoints,
                version_info=self.generate_version_info()
            )
        except Exception as e:
            logger.error(f"Error generating markdown documentation: {str(e)}")
            raise
            
    def _extract_endpoints(self, app: FastAPI) -> List[Dict[str, Any]]:
        """Extract endpoint information from FastAPI application"""
        try:
            endpoints = []
            for route in app.routes:
                if isinstance(route, APIRouter):
                    endpoints.extend(self._extract_router_endpoints(route))
                else:
                    endpoints.append(self._extract_endpoint_info(route))
            return endpoints
        except Exception as e:
            logger.error(f"Error extracting endpoints: {str(e)}")
            return []
            
    def _extract_router_endpoints(self, router: APIRouter) -> List[Dict[str, Any]]:
        """Extract endpoints from APIRouter"""
        try:
            endpoints = []
            for route in router.routes:
                endpoints.append(self._extract_endpoint_info(route))
            return endpoints
        except Exception as e:
            logger.error(f"Error extracting router endpoints: {str(e)}")
            return []
            
    def _extract_endpoint_info(self, route: Any) -> Dict[str, Any]:
        """Extract information from a single endpoint"""
        try:
            endpoint_info = {
                "path": route.path,
                "methods": route.methods,
                "summary": route.summary,
                "description": route.description,
                "parameters": [],
                "request_body": None,
                "responses": []
            }
            
            # Extract parameters
            if hasattr(route, "parameters"):
                endpoint_info["parameters"] = [
                    {
                        "name": param.name,
                        "type": param.type,
                        "required": param.required,
                        "description": param.description
                    }
                    for param in route.parameters
                ]
                
            # Extract request body
            if hasattr(route, "request_body"):
                endpoint_info["request_body"] = {
                    "type": route.request_body.type,
                    "description": route.request_body.description
                }
                
            # Extract responses
            if hasattr(route, "responses"):
                endpoint_info["responses"] = [
                    {
                        "status_code": response.status_code,
                        "description": response.description,
                        "content": response.content
                    }
                    for response in route.responses
                ]
                
            return endpoint_info
        except Exception as e:
            logger.error(f"Error extracting endpoint info: {str(e)}")
            return {}
            
    def _generate_api_version_history(self, app: FastAPI):
        """Generate API version history"""
        try:
            version_history = {
                "versions": [
                    {
                        "version": app.version,
                        "timestamp": self.last_updated,
                        "endpoints": len(app.routes),
                        "changes": self._extract_api_changes(app)
                    }
                ]
            }
            
            self.save_file(
                json.dumps(version_history, indent=2),
                "api/version_history.json"
            )
        except Exception as e:
            logger.error(f"Error generating API version history: {str(e)}")
            raise
            
    def _extract_api_changes(self, app: FastAPI) -> List[Dict[str, Any]]:
        """Extract API changes from version history"""
        try:
            changes = []
            history_file = self.output_dir / "api_version_history.json"
            
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    
                if history:
                    last_version = history[-1]
                    current_endpoints = set(route.path for route in app.routes)
                    previous_endpoints = set(last_version.get("endpoints", []))
                    
                    # Find added endpoints
                    added = current_endpoints - previous_endpoints
                    if added:
                        changes.append({
                            "type": "added",
                            "endpoints": list(added)
                        })
                        
                    # Find removed endpoints
                    removed = previous_endpoints - current_endpoints
                    if removed:
                        changes.append({
                            "type": "removed",
                            "endpoints": list(removed)
                        })
                        
            return changes
        except Exception as e:
            logger.error(f"Error extracting API changes: {str(e)}")
            return []
            
    def generate_endpoint_examples(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate example requests and responses for an endpoint"""
        try:
            examples = {
                "request": self._generate_request_example(endpoint),
                "response": self._generate_response_example(endpoint)
            }
            return examples
        except Exception as e:
            logger.error(f"Error generating endpoint examples: {str(e)}")
            return {}
            
    def _generate_request_example(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate example request for an endpoint"""
        try:
            if not endpoint.get("request_body"):
                return {}
                
            example = {}
            if endpoint["request_body"]["type"] == "application/json":
                # Generate example JSON based on Pydantic model
                model = self._get_request_model(endpoint)
                if model:
                    example = self._generate_model_example(model)
                    
            return {
                "content_type": endpoint["request_body"]["type"],
                "example": example
            }
        except Exception as e:
            logger.error(f"Error generating request example: {str(e)}")
            return {}
            
    def _generate_response_example(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate example response for an endpoint"""
        try:
            examples = {}
            for response in endpoint.get("responses", []):
                if response["content"]:
                    content_type = list(response["content"].keys())[0]
                    model = self._get_response_model(response)
                    if model:
                        examples[response["status_code"]] = {
                            "content_type": content_type,
                            "example": self._generate_model_example(model)
                        }
            return examples
        except Exception as e:
            logger.error(f"Error generating response example: {str(e)}")
            return {}
            
    def _get_request_model(self, endpoint: Dict[str, Any]) -> Optional[BaseModel]:
        """Get Pydantic model for request body"""
        try:
            if hasattr(endpoint, "request_body"):
                return endpoint.request_body.model
            return None
        except Exception as e:
            logger.error(f"Error getting request model: {str(e)}")
            return None
            
    def _get_response_model(self, response: Dict[str, Any]) -> Optional[BaseModel]:
        """Get Pydantic model for response"""
        try:
            if response.get("content"):
                content_type = list(response["content"].keys())[0]
                if content_type == "application/json":
                    return response["content"][content_type]["schema"].get("model")
            return None
        except Exception as e:
            logger.error(f"Error getting response model: {str(e)}")
            return None
            
    def _generate_model_example(self, model: BaseModel) -> Dict[str, Any]:
        """Generate example data for a Pydantic model"""
        try:
            example = {}
            for field_name, field in model.__fields__.items():
                example[field_name] = self._generate_field_example(field)
            return example
        except Exception as e:
            logger.error(f"Error generating model example: {str(e)}")
            return {}
            
    def _generate_field_example(self, field: Any) -> Any:
        """Generate example value for a field"""
        try:
            field_type = field.type_
            if field_type == str:
                return "example_string"
            elif field_type == int:
                return 0
            elif field_type == float:
                return 0.0
            elif field_type == bool:
                return True
            elif field_type == list:
                return []
            elif field_type == dict:
                return {}
            else:
                return None
        except Exception as e:
            logger.error(f"Error generating field example: {str(e)}")
            return None 