from typing import Dict, List, Optional
from datetime import datetime
import yaml
import json
from pathlib import Path
import subprocess
import os
from ..core.config import settings

class CICDService:
    def __init__(self, pipeline_config_path: str):
        self.pipeline_config_path = Path(pipeline_config_path)
        self._initialize_pipeline_config()

    def _initialize_pipeline_config(self):
        """Initialize the pipeline configuration directory."""
        self.pipeline_config_path.mkdir(parents=True, exist_ok=True)

    def create_pipeline_config(self, project_name: str, config: Dict) -> Dict:
        """Create a new pipeline configuration."""
        try:
            config_path = self.pipeline_config_path / f"{project_name}.yaml"
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
            return {"status": "success", "message": "Pipeline configuration created successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute_pipeline(self, project_name: str, environment: str) -> Dict:
        """Execute the CI/CD pipeline for a project."""
        try:
            config_path = self.pipeline_config_path / f"{project_name}.yaml"
            if not config_path.exists():
                return {"status": "error", "message": "Pipeline configuration not found"}

            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Execute build stage
            build_result = self._execute_build_stage(config, environment)
            if build_result["status"] != "success":
                return build_result

            # Execute test stage
            test_result = self._execute_test_stage(config, environment)
            if test_result["status"] != "success":
                return test_result

            # Execute deployment stage
            deploy_result = self._execute_deployment_stage(config, environment)
            if deploy_result["status"] != "success":
                return deploy_result

            return {"status": "success", "message": "Pipeline executed successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _execute_build_stage(self, config: Dict, environment: str) -> Dict:
        """Execute the build stage of the pipeline."""
        try:
            build_commands = config.get("build", {}).get("commands", [])
            for cmd in build_commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return {
                        "status": "error",
                        "message": f"Build failed: {result.stderr}"
                    }
            return {"status": "success", "message": "Build completed successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _execute_test_stage(self, config: Dict, environment: str) -> Dict:
        """Execute the test stage of the pipeline."""
        try:
            test_commands = config.get("test", {}).get("commands", [])
            for cmd in test_commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return {
                        "status": "error",
                        "message": f"Tests failed: {result.stderr}"
                    }
            return {"status": "success", "message": "Tests completed successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _execute_deployment_stage(self, config: Dict, environment: str) -> Dict:
        """Execute the deployment stage of the pipeline."""
        try:
            deploy_config = config.get("deploy", {}).get(environment, {})
            deploy_commands = deploy_config.get("commands", [])
            
            for cmd in deploy_commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return {
                        "status": "error",
                        "message": f"Deployment failed: {result.stderr}"
                    }
            return {"status": "success", "message": "Deployment completed successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_pipeline_status(self, project_name: str) -> Dict:
        """Get the current status of a pipeline."""
        try:
            status_path = self.pipeline_config_path / f"{project_name}_status.json"
            if not status_path.exists():
                return {"status": "error", "message": "Pipeline status not found"}

            with open(status_path, 'r') as f:
                status_data = json.load(f)

            return {"status": "success", "data": status_data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def update_environment_config(self, project_name: str, environment: str, 
                               config: Dict) -> Dict:
        """Update the configuration for a specific environment."""
        try:
            config_path = self.pipeline_config_path / f"{project_name}.yaml"
            if not config_path.exists():
                return {"status": "error", "message": "Pipeline configuration not found"}

            with open(config_path, 'r') as f:
                pipeline_config = yaml.safe_load(f)

            if "deploy" not in pipeline_config:
                pipeline_config["deploy"] = {}
            pipeline_config["deploy"][environment] = config

            with open(config_path, 'w') as f:
                yaml.dump(pipeline_config, f)

            return {"status": "success", "message": "Environment configuration updated successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_pipeline_report(self, project_name: str) -> Dict:
        """Generate a detailed report of pipeline execution."""
        try:
            report_path = self.pipeline_config_path / f"{project_name}_report.json"
            if not report_path.exists():
                return {"status": "error", "message": "Pipeline report not found"}

            with open(report_path, 'r') as f:
                report_data = json.load(f)

            return {"status": "success", "data": report_data}
        except Exception as e:
            return {"status": "error", "message": str(e)} 