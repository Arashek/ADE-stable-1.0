"""
Container Registry

This module provides functionality for managing container images in a registry.
It handles image storage, versioning, and access control.
"""

import os
import logging
import asyncio
import json
import base64
import hashlib
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import aiohttp

# Configure logging
logger = logging.getLogger(__name__)

class ImageVisibility(str, Enum):
    """Visibility levels for container images."""
    PUBLIC = "public"  # Accessible to all users
    PRIVATE = "private"  # Accessible only to the owner
    ORGANIZATION = "organization"  # Accessible to members of the organization

class ImageTag(BaseModel):
    """Tag for a container image."""
    name: str
    digest: str
    created_at: datetime
    size: int
    labels: Dict[str, str] = Field(default_factory=dict)

class ContainerImage(BaseModel):
    """Container image model."""
    id: str
    name: str
    repository: str
    owner_id: str
    visibility: ImageVisibility
    created_at: datetime
    updated_at: datetime
    tags: Dict[str, ImageTag] = Field(default_factory=dict)
    description: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)

class RegistryCredentials(BaseModel):
    """Credentials for accessing a container registry."""
    registry_url: str
    username: str
    password: str
    email: Optional[str] = None

class ContainerRegistry:
    """
    Container Registry
    
    Manages container images, including:
    - Storing and retrieving images
    - Versioning images
    - Managing access to images
    """
    
    def __init__(self, registry_url: str = None, credentials: RegistryCredentials = None):
        """
        Initialize the Container Registry.
        
        Args:
            registry_url: URL of the container registry
            credentials: Credentials for accessing the registry
        """
        self.registry_url = registry_url or os.environ.get("CONTAINER_REGISTRY_URL", "localhost:5000")
        self.credentials = credentials
        self.images: Dict[str, ContainerImage] = {}
        
        # For development/testing, we'll use a mock registry
        self._initialize_mock_registry()
        
        logger.info(f"Container Registry initialized with URL: {self.registry_url}")
    
    def _initialize_mock_registry(self):
        """Initialize a mock registry with sample images."""
        # User base image
        user_base = ContainerImage(
            id="sha256:1234567890abcdef",
            name="user-base",
            repository="ade",
            owner_id="system",
            visibility=ImageVisibility.PUBLIC,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags={
                "latest": ImageTag(
                    name="latest",
                    digest="sha256:1234567890abcdef",
                    created_at=datetime.now(),
                    size=100000000,
                    labels={
                        "type": "user",
                        "version": "1.0.0"
                    }
                ),
                "1.0.0": ImageTag(
                    name="1.0.0",
                    digest="sha256:1234567890abcdef",
                    created_at=datetime.now(),
                    size=100000000,
                    labels={
                        "type": "user",
                        "version": "1.0.0"
                    }
                )
            },
            description="Base image for user containers",
            labels={
                "type": "user",
                "version": "1.0.0"
            }
        )
        self.images[user_base.id] = user_base
        
        # Project base image
        project_base = ContainerImage(
            id="sha256:abcdef1234567890",
            name="project-base",
            repository="ade",
            owner_id="system",
            visibility=ImageVisibility.PUBLIC,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags={
                "latest": ImageTag(
                    name="latest",
                    digest="sha256:abcdef1234567890",
                    created_at=datetime.now(),
                    size=50000000,
                    labels={
                        "type": "project",
                        "version": "1.0.0"
                    }
                ),
                "1.0.0": ImageTag(
                    name="1.0.0",
                    digest="sha256:abcdef1234567890",
                    created_at=datetime.now(),
                    size=50000000,
                    labels={
                        "type": "project",
                        "version": "1.0.0"
                    }
                )
            },
            description="Base image for project containers",
            labels={
                "type": "project",
                "version": "1.0.0"
            }
        )
        self.images[project_base.id] = project_base
        
        # Web frontend application image
        web_frontend = ContainerImage(
            id="sha256:9876543210fedcba",
            name="app-web-frontend",
            repository="ade",
            owner_id="system",
            visibility=ImageVisibility.PUBLIC,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags={
                "latest": ImageTag(
                    name="latest",
                    digest="sha256:9876543210fedcba",
                    created_at=datetime.now(),
                    size=200000000,
                    labels={
                        "type": "application",
                        "app_type": "web_frontend",
                        "version": "1.0.0"
                    }
                ),
                "1.0.0": ImageTag(
                    name="1.0.0",
                    digest="sha256:9876543210fedcba",
                    created_at=datetime.now(),
                    size=200000000,
                    labels={
                        "type": "application",
                        "app_type": "web_frontend",
                        "version": "1.0.0"
                    }
                )
            },
            description="Base image for web frontend applications",
            labels={
                "type": "application",
                "app_type": "web_frontend",
                "version": "1.0.0"
            }
        )
        self.images[web_frontend.id] = web_frontend
        
        # Web backend application image
        web_backend = ContainerImage(
            id="sha256:fedcba9876543210",
            name="app-web-backend",
            repository="ade",
            owner_id="system",
            visibility=ImageVisibility.PUBLIC,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags={
                "latest": ImageTag(
                    name="latest",
                    digest="sha256:fedcba9876543210",
                    created_at=datetime.now(),
                    size=150000000,
                    labels={
                        "type": "application",
                        "app_type": "web_backend",
                        "version": "1.0.0"
                    }
                ),
                "1.0.0": ImageTag(
                    name="1.0.0",
                    digest="sha256:fedcba9876543210",
                    created_at=datetime.now(),
                    size=150000000,
                    labels={
                        "type": "application",
                        "app_type": "web_backend",
                        "version": "1.0.0"
                    }
                )
            },
            description="Base image for web backend applications",
            labels={
                "type": "application",
                "app_type": "web_backend",
                "version": "1.0.0"
            }
        )
        self.images[web_backend.id] = web_backend
    
    async def get_image(self, image_id: str) -> ContainerImage:
        """
        Get an image by ID.
        
        Args:
            image_id: ID of the image to get
            
        Returns:
            The image
        """
        if image_id not in self.images:
            raise ValueError(f"Image not found: {image_id}")
        
        return self.images[image_id]
    
    async def get_image_by_name_tag(self, repository: str, name: str, tag: str = "latest") -> ContainerImage:
        """
        Get an image by name and tag.
        
        Args:
            repository: Repository name
            name: Image name
            tag: Image tag
            
        Returns:
            The image
        """
        for image in self.images.values():
            if image.repository == repository and image.name == name and tag in image.tags:
                return image
        
        raise ValueError(f"Image not found: {repository}/{name}:{tag}")
    
    async def list_images(
        self, 
        owner_id: Optional[str] = None,
        repository: Optional[str] = None,
        visibility: Optional[ImageVisibility] = None,
        label_selector: Optional[Dict[str, str]] = None
    ) -> List[ContainerImage]:
        """
        List images with optional filtering.
        
        Args:
            owner_id: Filter by owner ID
            repository: Filter by repository
            visibility: Filter by visibility
            label_selector: Filter by labels
            
        Returns:
            List of images matching the filters
        """
        images = list(self.images.values())
        
        if owner_id:
            images = [img for img in images if img.owner_id == owner_id]
        
        if repository:
            images = [img for img in images if img.repository == repository]
        
        if visibility:
            images = [img for img in images if img.visibility == visibility]
        
        if label_selector:
            filtered_images = []
            for img in images:
                match = True
                for key, value in label_selector.items():
                    if key not in img.labels or img.labels[key] != value:
                        match = False
                        break
                if match:
                    filtered_images.append(img)
            images = filtered_images
        
        return images
    
    async def create_image(
        self, 
        name: str,
        repository: str,
        owner_id: str,
        visibility: ImageVisibility,
        description: Optional[str] = None,
        labels: Dict[str, str] = None,
        tag: str = "latest"
    ) -> ContainerImage:
        """
        Create a new image entry.
        
        Args:
            name: Image name
            repository: Repository name
            owner_id: Owner ID
            visibility: Image visibility
            description: Image description
            labels: Image labels
            tag: Initial tag
            
        Returns:
            The created image
        """
        # Generate a unique ID for the image
        digest = f"sha256:{hashlib.sha256(f'{repository}/{name}:{tag}'.encode()).hexdigest()}"
        
        # Create the image
        image = ContainerImage(
            id=digest,
            name=name,
            repository=repository,
            owner_id=owner_id,
            visibility=visibility,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            description=description,
            labels=labels or {},
            tags={
                tag: ImageTag(
                    name=tag,
                    digest=digest,
                    created_at=datetime.now(),
                    size=0,
                    labels=labels or {}
                )
            }
        )
        
        # Store the image
        self.images[digest] = image
        
        logger.info(f"Image created: {repository}/{name}:{tag}")
        return image
    
    async def add_image_tag(self, image_id: str, tag: str) -> ContainerImage:
        """
        Add a tag to an existing image.
        
        Args:
            image_id: ID of the image
            tag: Tag to add
            
        Returns:
            The updated image
        """
        if image_id not in self.images:
            raise ValueError(f"Image not found: {image_id}")
        
        image = self.images[image_id]
        
        # Add the tag
        image.tags[tag] = ImageTag(
            name=tag,
            digest=image_id,
            created_at=datetime.now(),
            size=next(iter(image.tags.values())).size,
            labels=image.labels
        )
        
        # Update the image
        image.updated_at = datetime.now()
        
        logger.info(f"Tag added to image: {image.repository}/{image.name}:{tag}")
        return image
    
    async def delete_image_tag(self, image_id: str, tag: str) -> ContainerImage:
        """
        Delete a tag from an image.
        
        Args:
            image_id: ID of the image
            tag: Tag to delete
            
        Returns:
            The updated image
        """
        if image_id not in self.images:
            raise ValueError(f"Image not found: {image_id}")
        
        image = self.images[image_id]
        
        if tag not in image.tags:
            raise ValueError(f"Tag not found: {tag}")
        
        # Delete the tag
        del image.tags[tag]
        
        # Update the image
        image.updated_at = datetime.now()
        
        logger.info(f"Tag deleted from image: {image.repository}/{image.name}:{tag}")
        return image
    
    async def delete_image(self, image_id: str) -> None:
        """
        Delete an image.
        
        Args:
            image_id: ID of the image to delete
        """
        if image_id not in self.images:
            raise ValueError(f"Image not found: {image_id}")
        
        # Delete the image
        del self.images[image_id]
        
        logger.info(f"Image deleted: {image_id}")
    
    async def get_image_manifest(self, repository: str, name: str, tag: str = "latest") -> Dict[str, Any]:
        """
        Get the manifest for an image.
        
        Args:
            repository: Repository name
            name: Image name
            tag: Image tag
            
        Returns:
            Image manifest
        """
        # This is a mock implementation
        image = await self.get_image_by_name_tag(repository, name, tag)
        
        return {
            "schemaVersion": 2,
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "config": {
                "mediaType": "application/vnd.docker.container.image.v1+json",
                "size": 1000,
                "digest": image.tags[tag].digest
            },
            "layers": [
                {
                    "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                    "size": image.tags[tag].size,
                    "digest": f"sha256:{hashlib.sha256(f'layer-{image.name}-{tag}'.encode()).hexdigest()}"
                }
            ]
        }
    
    async def get_registry_auth_token(self) -> str:
        """
        Get an authentication token for the registry.
        
        Returns:
            Authentication token
        """
        if not self.credentials:
            return ""
        
        # Create a basic auth token
        auth_string = f"{self.credentials.username}:{self.credentials.password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        return f"Basic {encoded_auth}"
    
    async def push_image(self, local_image: str, repository: str, name: str, tag: str = "latest") -> ContainerImage:
        """
        Push an image to the registry.
        
        Args:
            local_image: Local image name
            repository: Repository name
            name: Image name
            tag: Image tag
            
        Returns:
            The pushed image
        """
        # This is a mock implementation
        logger.info(f"Pushing image {local_image} to {repository}/{name}:{tag}")
        
        # Check if the image already exists
        try:
            image = await self.get_image_by_name_tag(repository, name, tag)
        except ValueError:
            # Create a new image
            image = await self.create_image(
                name=name,
                repository=repository,
                owner_id="system",  # This would be the actual user ID in a real implementation
                visibility=ImageVisibility.PRIVATE,
                description=f"Image pushed from {local_image}",
                labels={
                    "source": local_image
                },
                tag=tag
            )
        
        # Update the image tag
        image.tags[tag] = ImageTag(
            name=tag,
            digest=image.id,
            created_at=datetime.now(),
            size=100000000,  # Mock size
            labels=image.labels
        )
        
        # Update the image
        image.updated_at = datetime.now()
        
        logger.info(f"Image pushed: {repository}/{name}:{tag}")
        return image
    
    async def pull_image(self, repository: str, name: str, tag: str = "latest") -> str:
        """
        Pull an image from the registry.
        
        Args:
            repository: Repository name
            name: Image name
            tag: Image tag
            
        Returns:
            Local image name
        """
        # This is a mock implementation
        logger.info(f"Pulling image {repository}/{name}:{tag}")
        
        # Check if the image exists
        image = await self.get_image_by_name_tag(repository, name, tag)
        
        local_image = f"{repository}/{name}:{tag}"
        
        logger.info(f"Image pulled: {local_image}")
        return local_image

# Singleton instance
container_registry = ContainerRegistry()
