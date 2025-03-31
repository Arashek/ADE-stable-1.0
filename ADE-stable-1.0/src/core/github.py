import os
from typing import Optional, Dict, List
import aiohttp
from fastapi import HTTPException
from github import Github, GithubException, Branch, PullRequest, Repository, Collaborator

class GitHubManager:
    def __init__(self, access_token: str):
        self.github = Github(access_token)
        self.user = self.github.get_user()

    async def create_repository(self, name: str, description: str = "", private: bool = True) -> Dict:
        """Create a new GitHub repository"""
        try:
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=True
            )
            return {
                "name": repo.name,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url
            }
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def push_code(self, repo_name: str, file_path: str, content: str, commit_message: str) -> Dict:
        """Push code to a GitHub repository"""
        try:
            repo = self.user.get_repo(repo_name)
            try:
                # Try to get the file first
                file = repo.get_contents(file_path)
                # Update existing file
                repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=file.sha
                )
            except GithubException:
                # File doesn't exist, create it
                repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content
                )
            return {"status": "success", "message": "Code pushed successfully"}
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_repository(self, repo_name: str) -> Dict:
        """Get repository details"""
        try:
            repo = self.user.get_repo(repo_name)
            return {
                "name": repo.name,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
                "description": repo.description,
                "private": repo.private
            }
        except GithubException as e:
            raise HTTPException(status_code=404, detail="Repository not found")

    async def list_repositories(self) -> List[Dict]:
        """List all repositories"""
        try:
            repos = self.user.get_repos()
            return [{
                "name": repo.name,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
                "description": repo.description,
                "private": repo.private
            } for repo in repos]
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_repository(self, repo_name: str) -> Dict:
        """Delete a repository"""
        try:
            repo = self.user.get_repo(repo_name)
            repo.delete()
            return {"status": "success", "message": "Repository deleted successfully"}
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def create_branch(self, repo_name: str, branch_name: str, base_branch: str = "main") -> Dict:
        """Create a new branch in a repository"""
        try:
            repo = self.user.get_repo(repo_name)
            base = repo.get_branch(base_branch)
            repo.create_git_ref(f"refs/heads/{branch_name}", base.commit.sha)
            return {
                "name": branch_name,
                "sha": base.commit.sha,
                "url": f"{repo.html_url}/tree/{branch_name}"
            }
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def create_pull_request(
        self,
        repo_name: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> Dict:
        """Create a pull request"""
        try:
            repo = self.user.get_repo(repo_name)
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            return {
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
                "state": pr.state
            }
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def create_from_template(
        self,
        template_repo: str,
        name: str,
        description: str = "",
        private: bool = True,
        include_all_branches: bool = False
    ) -> Dict:
        """Create a repository from a template"""
        try:
            template = self.github.get_repo(template_repo)
            repo = template.create_fork(
                name=name,
                description=description,
                private=private,
                include_all_branches=include_all_branches
            )
            return {
                "name": repo.name,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url
            }
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def create_webhook(
        self,
        repo_name: str,
        webhook_url: str,
        events: List[str] = ["push", "pull_request"],
        content_type: str = "json"
    ) -> Dict:
        """Create a webhook for a repository"""
        try:
            repo = self.user.get_repo(repo_name)
            webhook = repo.create_hook(
                name="web",
                config={
                    "url": webhook_url,
                    "content_type": content_type,
                    "insecure_ssl": "0"
                },
                events=events,
                active=True
            )
            return {
                "id": webhook.id,
                "url": webhook.url,
                "events": webhook.events,
                "active": webhook.active
            }
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def add_collaborator(
        self,
        repo_name: str,
        username: str,
        permission: str = "push"
    ) -> Dict:
        """Add a collaborator to a repository"""
        try:
            repo = self.user.get_repo(repo_name)
            collaborator = repo.add_to_collaborators(username, permission)
            return {
                "username": username,
                "permission": permission,
                "url": collaborator.url
            }
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def remove_collaborator(self, repo_name: str, username: str) -> Dict:
        """Remove a collaborator from a repository"""
        try:
            repo = self.user.get_repo(repo_name)
            repo.remove_from_collaborators(username)
            return {"status": "success", "message": f"Collaborator {username} removed"}
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def list_collaborators(self, repo_name: str) -> List[Dict]:
        """List all collaborators of a repository"""
        try:
            repo = self.user.get_repo(repo_name)
            collaborators = repo.get_collaborators()
            return [{
                "username": collab.login,
                "permission": collab.permissions,
                "url": collab.url
            } for collab in collaborators]
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def list_branches(self, repo_name: str) -> List[Dict]:
        """List all branches in a repository"""
        try:
            repo = self.user.get_repo(repo_name)
            branches = repo.get_branches()
            return [{
                "name": branch.name,
                "sha": branch.commit.sha,
                "protected": branch.protected,
                "url": f"{repo.html_url}/tree/{branch.name}"
            } for branch in branches]
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def list_pull_requests(
        self,
        repo_name: str,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc"
    ) -> List[Dict]:
        """List pull requests in a repository"""
        try:
            repo = self.user.get_repo(repo_name)
            pulls = repo.get_pulls(state=state, sort=sort, direction=direction)
            return [{
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "url": pr.html_url,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat()
            } for pr in pulls]
        except GithubException as e:
            raise HTTPException(status_code=400, detail=str(e))

async def get_github_client(access_token: str) -> GitHubManager:
    """Get a GitHub client instance"""
    return GitHubManager(access_token) 