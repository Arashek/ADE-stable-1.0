import requests
import json
import time
from typing import Dict, Any, Optional

class ADEPlatformTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def login(self, username: str, password: str) -> bool:
        """Login to the platform and get JWT token"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                return True
            return False
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False

    def create_project(self, name: str, description: str) -> Optional[Dict[str, Any]]:
        """Create a new project"""
        try:
            response = self.session.post(
                f"{self.base_url}/projects",
                json={"name": name, "description": description}
            )
            if response.status_code == 201:
                return response.json()
            print(f"Error creating project: {response.text}")
            return None
        except Exception as e:
            print(f"Error creating project: {str(e)}")
            return None

    def generate_code(self, project_id: str, prompt: str) -> Optional[Dict[str, Any]]:
        """Generate code based on a prompt"""
        try:
            response = self.session.post(
                f"{self.base_url}/projects/{project_id}/generate",
                json={"prompt": prompt}
            )
            if response.status_code == 200:
                return response.json()
            print(f"Error generating code: {response.text}")
            return None
        except Exception as e:
            print(f"Error generating code: {str(e)}")
            return None

    def edit_code(self, project_id: str, file_path: str, changes: str) -> Optional[Dict[str, Any]]:
        """Edit existing code"""
        try:
            response = self.session.put(
                f"{self.base_url}/projects/{project_id}/files/{file_path}",
                json={"content": changes}
            )
            if response.status_code == 200:
                return response.json()
            print(f"Error editing code: {response.text}")
            return None
        except Exception as e:
            print(f"Error editing code: {str(e)}")
            return None

    def style_interface(self, project_id: str, style_prompt: str) -> Optional[Dict[str, Any]]:
        """Apply styling to the interface"""
        try:
            response = self.session.post(
                f"{self.base_url}/projects/{project_id}/style",
                json={"prompt": style_prompt}
            )
            if response.status_code == 200:
                return response.json()
            print(f"Error styling interface: {response.text}")
            return None
        except Exception as e:
            print(f"Error styling interface: {str(e)}")
            return None

def test_platform():
    tester = ADEPlatformTester()
    
    # Login
    print("Logging in...")
    if not tester.login("admin", "admin"):
        print("Failed to login")
        return

    # Create a test project
    print("\nCreating a new project...")
    project = tester.create_project(
        "Test Project",
        "A test project for platform capabilities"
    )
    if not project:
        print("Failed to create project")
        return
    
    project_id = project["id"]
    print(f"Created project with ID: {project_id}")

    # Test code generation
    print("\nTesting code generation...")
    code_prompt = """
    Create a modern web application with:
    - A responsive dashboard layout
    - User authentication
    - Data visualization
    - Dark/light theme support
    Use React with TypeScript and Tailwind CSS.
    """
    
    generated_code = tester.generate_code(project_id, code_prompt)
    if generated_code:
        print("Code generation successful!")
        print("Generated files:", generated_code.get("files", []))

    # Test code editing
    print("\nTesting code editing...")
    edit_prompt = """
    Update the dashboard layout to include:
    - A sidebar navigation
    - A top header with user profile
    - A main content area with grid layout
    """
    
    edited_code = tester.edit_code(project_id, "src/components/Dashboard.tsx", edit_prompt)
    if edited_code:
        print("Code editing successful!")

    # Test interface styling
    print("\nTesting interface styling...")
    style_prompt = """
    Apply a modern design system with:
    - A clean, minimalist aesthetic
    - Consistent spacing and typography
    - Smooth transitions and animations
    - Accessible color contrast
    """
    
    styled_interface = tester.style_interface(project_id, style_prompt)
    if styled_interface:
        print("Interface styling successful!")

if __name__ == "__main__":
    print("Starting ADE Platform testing...")
    test_platform() 