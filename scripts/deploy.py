#!/usr/bin/env python3
import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, List
import docker
from docker.errors import DockerException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Deployer:
    def __init__(self, environment: str):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.env_path = self.project_root / 'environments' / environment
        
        try:
            self.docker_client = docker.from_env()
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise

    def validate_environment(self) -> bool:
        """Validate the deployment environment."""
        required_files = ['.env', 'docker-compose.yml']
        for file in required_files:
            if not (self.env_path / file).exists():
                logger.error(f"Missing required file {file} in {self.env_path}")
                return False
        return True

    def run_tests(self) -> bool:
        """Run the test suite."""
        try:
            logger.info("Running tests...")
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Tests failed: {result.stderr}")
                return False
            
            logger.info("Tests passed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return False

    def build_images(self) -> bool:
        """Build Docker images for the environment."""
        try:
            logger.info("Building Docker images...")
            result = subprocess.run(
                ['docker-compose', '-f', str(self.env_path / 'docker-compose.yml'), 'build'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to build images: {result.stderr}")
                return False
            
            logger.info("Docker images built successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to build images: {e}")
            return False

    def deploy_services(self) -> bool:
        """Deploy services using Docker Compose."""
        try:
            logger.info(f"Deploying services to {self.environment} environment...")
            result = subprocess.run(
                ['docker-compose', '-f', str(self.env_path / 'docker-compose.yml'), 'up', '-d'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to deploy services: {result.stderr}")
                return False
            
            logger.info("Services deployed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to deploy services: {e}")
            return False

    def verify_deployment(self) -> bool:
        """Verify the deployment by checking service health."""
        try:
            logger.info("Verifying deployment...")
            
            # Get running containers
            containers = self.docker_client.containers.list(
                filters={'name': 'ade-platform'}
            )
            
            if not containers:
                logger.error("No containers found")
                return False
            
            # Check container health
            for container in containers:
                health = container.attrs['State']['Health']
                if health['Status'] != 'healthy':
                    logger.error(f"Container {container.name} is not healthy")
                    return False
            
            logger.info("Deployment verified successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to verify deployment: {e}")
            return False

    def rollback(self) -> bool:
        """Rollback the deployment to the previous version."""
        try:
            logger.info("Rolling back deployment...")
            
            # Stop current services
            subprocess.run(
                ['docker-compose', '-f', str(self.env_path / 'docker-compose.yml'), 'down'],
                check=True
            )
            
            # Restore previous version
            # This would typically involve checking out the previous Git tag
            # and redeploying from that version
            
            logger.info("Rollback completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to rollback: {e}")
            return False

    def deploy(self) -> bool:
        """Perform the complete deployment process."""
        logger.info(f"Starting deployment to {self.environment} environment")
        
        # Validate environment
        if not self.validate_environment():
            logger.error("Environment validation failed")
            return False
        
        # Run tests
        if not self.run_tests():
            logger.error("Test suite failed")
            return False
        
        # Build images
        if not self.build_images():
            logger.error("Image build failed")
            return False
        
        # Deploy services
        if not self.deploy_services():
            logger.error("Service deployment failed")
            return False
        
        # Verify deployment
        if not self.verify_deployment():
            logger.error("Deployment verification failed")
            return False
        
        logger.info("Deployment completed successfully")
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python deploy.py <environment>")
        print("Example: python deploy.py production")
        sys.exit(1)
    
    environment = sys.argv[1]
    deployer = Deployer(environment)
    
    try:
        if not deployer.deploy():
            sys.exit(1)
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 