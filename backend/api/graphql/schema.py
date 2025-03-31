import strawberry
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass
from ..models.core_components import UserProfile, Project, Component

@strawberry.type
class User:
    id: str
    username: str
    email: str
    profile: Optional['UserProfile']
    projects: List['Project']

@strawberry.type
class Project:
    id: str
    name: str
    description: Optional[str]
    owner: User
    components: List['Component']
    created_at: datetime
    updated_at: datetime

@strawberry.type
class Component:
    id: str
    name: str
    type: str
    config: dict
    project: Project
    metrics: Optional['ComponentMetrics']

@strawberry.type
class ComponentMetrics:
    complexity: float
    performance: float
    reliability: float
    last_updated: datetime

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, info, id: str) -> Optional[User]:
        return await info.context["user_service"].get_user(id)

    @strawberry.field
    async def project(self, info, id: str) -> Optional[Project]:
        return await info.context["project_service"].get_project(id)

    @strawberry.field
    async def projects(
        self,
        info,
        owner_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Project]:
        return await info.context["project_service"].get_projects(
            owner_id=owner_id,
            limit=limit,
            offset=offset
        )

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_project(
        self,
        info,
        name: str,
        description: Optional[str] = None
    ) -> Project:
        return await info.context["project_service"].create_project(
            name=name,
            description=description,
            owner_id=info.context["user_id"]
        )

    @strawberry.mutation
    async def update_component(
        self,
        info,
        id: str,
        config: dict
    ) -> Component:
        return await info.context["component_service"].update_component(
            id=id,
            config=config
        )

schema = strawberry.Schema(query=Query, mutation=Mutation)

# Example of efficient data loading with DataLoader
from strawberry.dataloader import DataLoader

async def load_user_by_id(ids: List[str]) -> List[Optional[User]]:
    # Batch load users
    users = await User.objects.filter(id__in=ids)
    user_map = {str(user.id): user for user in users}
    return [user_map.get(id) for id in ids]

async def load_projects_by_user_id(ids: List[str]) -> List[List[Project]]:
    # Batch load projects
    projects = await Project.objects.filter(owner_id__in=ids)
    project_map = {}
    for project in projects:
        if project.owner_id not in project_map:
            project_map[project.owner_id] = []
        project_map[project.owner_id].append(project)
    return [project_map.get(id, []) for id in ids]

# Create DataLoaders
user_loader = DataLoader(load_fn=load_user_by_id)
projects_loader = DataLoader(load_fn=load_projects_by_user_id)
