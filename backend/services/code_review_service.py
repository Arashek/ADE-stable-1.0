from typing import Dict, List, Optional
from datetime import datetime
from ..models.code_review import PullRequest, ReviewComment, ReviewStatus
from ..core.config import settings
import json
from pathlib import Path

class CodeReviewService:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self._initialize_storage()

    def _initialize_storage(self):
        """Initialize storage for pull requests and reviews."""
        self.pulls_path = self.storage_path / "pull_requests"
        self.pulls_path.mkdir(parents=True, exist_ok=True)

    def create_pull_request(self, title: str, description: str, source_branch: str, 
                          target_branch: str, author: str) -> Dict:
        """Create a new pull request."""
        try:
            pr_id = f"PR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            pr = PullRequest(
                id=pr_id,
                title=title,
                description=description,
                source_branch=source_branch,
                target_branch=target_branch,
                author=author,
                status=ReviewStatus.OPEN,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            pr_path = self.pulls_path / f"{pr_id}.json"
            with open(pr_path, 'w') as f:
                json.dump(pr.dict(), f, default=str)
            
            return {"status": "success", "data": pr.dict()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def add_review_comment(self, pr_id: str, file_path: str, line_number: int,
                         comment: str, reviewer: str) -> Dict:
        """Add a review comment to a pull request."""
        try:
            pr_path = self.pulls_path / f"{pr_id}.json"
            if not pr_path.exists():
                return {"status": "error", "message": "Pull request not found"}

            with open(pr_path, 'r') as f:
                pr_data = json.load(f)
                pr = PullRequest(**pr_data)

            review_comment = ReviewComment(
                file_path=file_path,
                line_number=line_number,
                comment=comment,
                reviewer=reviewer,
                created_at=datetime.now()
            )

            if 'comments' not in pr_data:
                pr_data['comments'] = []
            pr_data['comments'].append(review_comment.dict())

            with open(pr_path, 'w') as f:
                json.dump(pr_data, f, default=str)

            return {"status": "success", "data": review_comment.dict()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def update_pr_status(self, pr_id: str, status: ReviewStatus) -> Dict:
        """Update the status of a pull request."""
        try:
            pr_path = self.pulls_path / f"{pr_id}.json"
            if not pr_path.exists():
                return {"status": "error", "message": "Pull request not found"}

            with open(pr_path, 'r') as f:
                pr_data = json.load(f)
                pr = PullRequest(**pr_data)

            pr_data['status'] = status
            pr_data['updated_at'] = datetime.now()

            with open(pr_path, 'w') as f:
                json.dump(pr_data, f, default=str)

            return {"status": "success", "data": pr_data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_pull_request(self, pr_id: str) -> Dict:
        """Get a pull request by ID."""
        try:
            pr_path = self.pulls_path / f"{pr_id}.json"
            if not pr_path.exists():
                return {"status": "error", "message": "Pull request not found"}

            with open(pr_path, 'r') as f:
                pr_data = json.load(f)
                pr = PullRequest(**pr_data)

            return {"status": "success", "data": pr.dict()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_pull_requests(self, status: Optional[ReviewStatus] = None) -> Dict:
        """List all pull requests, optionally filtered by status."""
        try:
            prs = []
            for pr_file in self.pulls_path.glob("*.json"):
                with open(pr_file, 'r') as f:
                    pr_data = json.load(f)
                    pr = PullRequest(**pr_data)
                    if status is None or pr.status == status:
                        prs.append(pr.dict())

            return {"status": "success", "data": prs}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def integrate_with_external_service(self, service_type: str, 
                                     credentials: Dict) -> Dict:
        """Integrate with external Git hosting services (GitHub, GitLab, Bitbucket)."""
        try:
            # Implementation would depend on the specific service
            # This is a placeholder for the integration logic
            if service_type not in ["github", "gitlab", "bitbucket"]:
                return {"status": "error", "message": "Unsupported service type"}

            # Here you would implement the specific integration logic
            # using the appropriate API client for each service

            return {"status": "success", "message": f"Successfully integrated with {service_type}"}
        except Exception as e:
            return {"status": "error", "message": str(e)} 