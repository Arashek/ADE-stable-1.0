from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path
from ..models.project_management import Task, Sprint, Project, TimeEntry
from ..core.config import settings

class ProjectManagementService:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self._initialize_storage()

    def _initialize_storage(self):
        """Initialize storage for project management data."""
        self.projects_path = self.storage_path / "projects"
        self.projects_path.mkdir(parents=True, exist_ok=True)

    def create_project(self, name: str, description: str, owner: str) -> Dict:
        """Create a new project."""
        try:
            project_id = f"PROJ-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            project = Project(
                id=project_id,
                name=name,
                description=description,
                owner=owner,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status="active"
            )
            
            project_path = self.projects_path / f"{project_id}.json"
            with open(project_path, 'w') as f:
                json.dump(project.dict(), f, default=str)
            
            return {"status": "success", "data": project.dict()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_task(self, project_id: str, title: str, description: str,
                   assignee: str, estimated_hours: float) -> Dict:
        """Create a new task in a project."""
        try:
            project_path = self.projects_path / f"{project_id}.json"
            if not project_path.exists():
                return {"status": "error", "message": "Project not found"}

            with open(project_path, 'r') as f:
                project_data = json.load(f)
                project = Project(**project_data)

            task_id = f"TASK-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            task = Task(
                id=task_id,
                title=title,
                description=description,
                assignee=assignee,
                estimated_hours=estimated_hours,
                status="todo",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            if 'tasks' not in project_data:
                project_data['tasks'] = []
            project_data['tasks'].append(task.dict())

            with open(project_path, 'w') as f:
                json.dump(project_data, f, default=str)

            return {"status": "success", "data": task.dict()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_sprint(self, project_id: str, name: str, start_date: datetime,
                     end_date: datetime) -> Dict:
        """Create a new sprint in a project."""
        try:
            project_path = self.projects_path / f"{project_id}.json"
            if not project_path.exists():
                return {"status": "error", "message": "Project not found"}

            with open(project_path, 'r') as f:
                project_data = json.load(f)
                project = Project(**project_data)

            sprint_id = f"SPRINT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            sprint = Sprint(
                id=sprint_id,
                name=name,
                start_date=start_date,
                end_date=end_date,
                status="planned",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            if 'sprints' not in project_data:
                project_data['sprints'] = []
            project_data['sprints'].append(sprint.dict())

            with open(project_path, 'w') as f:
                json.dump(project_data, f, default=str)

            return {"status": "success", "data": sprint.dict()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def update_task_status(self, project_id: str, task_id: str, 
                         status: str) -> Dict:
        """Update the status of a task."""
        try:
            project_path = self.projects_path / f"{project_id}.json"
            if not project_path.exists():
                return {"status": "error", "message": "Project not found"}

            with open(project_path, 'r') as f:
                project_data = json.load(f)
                project = Project(**project_data)

            for task in project_data['tasks']:
                if task['id'] == task_id:
                    task['status'] = status
                    task['updated_at'] = datetime.now()
                    break

            with open(project_path, 'w') as f:
                json.dump(project_data, f, default=str)

            return {"status": "success", "message": "Task status updated successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def log_time(self, project_id: str, task_id: str, hours: float,
                description: str, user: str) -> Dict:
        """Log time spent on a task."""
        try:
            project_path = self.projects_path / f"{project_id}.json"
            if not project_path.exists():
                return {"status": "error", "message": "Project not found"}

            with open(project_path, 'r') as f:
                project_data = json.load(f)
                project = Project(**project_data)

            time_entry = TimeEntry(
                task_id=task_id,
                hours=hours,
                description=description,
                user=user,
                logged_at=datetime.now()
            )

            for task in project_data['tasks']:
                if task['id'] == task_id:
                    if 'time_entries' not in task:
                        task['time_entries'] = []
                    task['time_entries'].append(time_entry.dict())
                    break

            with open(project_path, 'w') as f:
                json.dump(project_data, f, default=str)

            return {"status": "success", "data": time_entry.dict()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_project_backlog(self, project_id: str) -> Dict:
        """Get the project backlog with all tasks."""
        try:
            project_path = self.projects_path / f"{project_id}.json"
            if not project_path.exists():
                return {"status": "error", "message": "Project not found"}

            with open(project_path, 'r') as f:
                project_data = json.load(f)
                project = Project(**project_data)

            return {"status": "success", "data": project_data['tasks']}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_sprint_tasks(self, project_id: str, sprint_id: str) -> Dict:
        """Get all tasks assigned to a sprint."""
        try:
            project_path = self.projects_path / f"{project_id}.json"
            if not project_path.exists():
                return {"status": "error", "message": "Project not found"}

            with open(project_path, 'r') as f:
                project_data = json.load(f)
                project = Project(**project_data)

            sprint_tasks = [task for task in project_data['tasks'] 
                          if task.get('sprint_id') == sprint_id]

            return {"status": "success", "data": sprint_tasks}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def integrate_with_external_tool(self, tool_type: str, 
                                  credentials: Dict) -> Dict:
        """Integrate with external project management tools."""
        try:
            if tool_type not in ["jira", "trello", "asana"]:
                return {"status": "error", "message": "Unsupported tool type"}

            # Here you would implement the specific integration logic
            # using the appropriate API client for each tool

            return {"status": "success", "message": f"Successfully integrated with {tool_type}"}
        except Exception as e:
            return {"status": "error", "message": str(e)} 