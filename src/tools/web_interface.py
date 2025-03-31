import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
import json
import shutil
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from .auth import get_current_user, User, create_access_token, Token
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import WebSocket
import io

class WebInterface:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.app = FastAPI(title="ADE Platform Web Interface")
        self.setup_middleware()
        self.setup_routes()
        self.setup_static_files()

    def setup_middleware(self):
        """Setup CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_static_files(self):
        """Setup static files serving"""
        static_dir = self.project_dir / "static"
        static_dir.mkdir(exist_ok=True)
        
        # Copy visualizations to static directory
        visualization_dir = self.project_dir / "visualizations"
        if visualization_dir.exists():
            for file in visualization_dir.glob("*.png"):
                shutil.copy2(file, static_dir / file.name)
        
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    def setup_routes(self):
        """Setup API routes"""
        @self.app.get("/")
        async def root():
            """Serve the main dashboard page"""
            return FileResponse(str(self.project_dir / "static" / "index.html"))

        @self.app.get("/workspace")
        async def workspace():
            """Serve the workspace view page"""
            return FileResponse(str(self.project_dir / "static" / "workspace.html"))

        @self.app.post("/token", response_model=Token)
        async def login(form_data: OAuth2PasswordRequestForm = Depends()):
            """Login endpoint"""
            user = get_user(form_data.username)
            if not user or not verify_password(form_data.password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token = create_access_token(data={"sub": user.username})
            return {"access_token": access_token, "token_type": "bearer"}

        @self.app.get("/api/projects")
        async def list_projects(current_user: User = Depends(get_current_user)):
            """List all projects"""
            projects = []
            for file in self.project_dir.glob("*.json"):
                with open(file) as f:
                    projects.append(json.load(f))
            return projects

        @self.app.get("/api/projects/{project_name}")
        async def get_project(project_name: str, current_user: User = Depends(get_current_user)):
            """Get project details"""
            project_file = self.project_dir / f"{project_name}.json"
            if not project_file.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            with open(project_file) as f:
                return json.load(f)

        @self.app.post("/api/projects/{project_name}")
        async def update_project(
            project_name: str,
            project_data: Dict[str, Any],
            current_user: User = Depends(get_current_user)
        ):
            """Update project details"""
            project_file = self.project_dir / f"{project_name}.json"
            if not project_file.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2)
            return {"status": "success"}

        @self.app.get("/api/projects/{project_name}/visualizations")
        async def get_visualizations(project_name: str, current_user: User = Depends(get_current_user)):
            """Get project visualizations"""
            visualization_dir = self.project_dir / "visualizations"
            if not visualization_dir.exists():
                return []
            
            visualizations = []
            for file in visualization_dir.glob("*.png"):
                visualizations.append({
                    "name": file.stem,
                    "url": f"/static/{file.name}"
                })
            return visualizations

        @self.app.get("/api/projects/{project_name}/metrics")
        async def get_metrics(project_name: str, current_user: User = Depends(get_current_user)):
            """Get project metrics"""
            project_file = self.project_dir / f"{project_name}.json"
            if not project_file.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            
            with open(project_file) as f:
                project_data = json.load(f)
                return project_data.get("metrics", {})

        @self.app.get("/api/projects/{project_name}/components")
        async def get_components(project_name: str, current_user: User = Depends(get_current_user)):
            """Get project components"""
            project_file = self.project_dir / f"{project_name}.json"
            if not project_file.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            
            with open(project_file) as f:
                project_data = json.load(f)
                return project_data.get("components", [])

        @self.app.get("/api/projects/{project_name}/dependencies")
        async def get_dependencies(project_name: str, current_user: User = Depends(get_current_user)):
            """Get project dependencies graph"""
            project_file = self.project_dir / f"{project_name}.json"
            if not project_file.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            
            with open(project_file) as f:
                project_data = json.load(f)
                return self._generate_dependency_graph(project_data)

        @self.app.get("/api/projects/{project_name}/code-structure")
        async def get_code_structure(project_name: str, current_user: User = Depends(get_current_user)):
            """Get project code structure"""
            project_file = self.project_dir / f"{project_name}.json"
            if not project_file.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            
            with open(project_file) as f:
                project_data = json.load(f)
                return self._generate_code_structure(project_data)

        @self.app.get("/api/projects/{project_name}/agent-activities")
        async def get_agent_activities(project_name: str, current_user: User = Depends(get_current_user)):
            """Get agent activities"""
            project_file = self.project_dir / f"{project_name}.json"
            if not project_file.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            
            with open(project_file) as f:
                project_data = json.load(f)
                return project_data.get("agent_activities", [])

        @self.app.websocket("/ws/{project_name}")
        async def websocket_endpoint(websocket: WebSocket, project_name: str):
            """WebSocket endpoint for real-time collaboration"""
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_json()
                    # Broadcast changes to all connected clients
                    await broadcast_message(project_name, data)
            except WebSocketDisconnect:
                await disconnect_client(project_name, websocket)

        @self.app.get("/api/projects/{project_name}/chat")
        async def get_chat_history(project_name: str, current_user: User = Depends(get_current_user)):
            """Get project chat history"""
            project_file = self.project_dir / f"{project_name}.json"
            if not project_file.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            
            with open(project_file) as f:
                project_data = json.load(f)
                return project_data.get("chat_history", [])

        @self.app.get("/api/projects/{project_name}/tasks")
        async def get_tasks(project_name: str, current_user: User = Depends(get_current_user)):
            """Get project tasks"""
            project_file = self.project_dir / f"{project_name}.json"
            if not project_file.exists():
                raise HTTPException(status_code=404, detail="Project not found")
            
            with open(project_file) as f:
                project_data = json.load(f)
                return project_data.get("tasks", [])

        @self.app.get("/api/tutorials")
        async def get_tutorials(current_user: User = Depends(get_current_user)):
            """Get available tutorials"""
            return {
                "tutorials": [
                    {
                        "id": "getting-started",
                        "title": "Getting Started",
                        "description": "Learn the basics of using the ADE Platform",
                        "sections": [
                            {
                                "title": "Interface Overview",
                                "content": """
                                The ADE Platform workspace is divided into several panels:
                                
                                1. **File Explorer** (Left Panel)
                                   - Browse project files and directories
                                   - Click on files to open them in the editor
                                   - Use the refresh button to update the file list
                                
                                2. **Code Editor** (Center Panel)
                                   - Edit code with syntax highlighting
                                   - Use the toolbar for common actions:
                                     - 💾 Save: Save current file
                                     - 📝 Format: Format code
                                     - ▶️ Run: Execute code
                                     - 🐛 Debug: Start debugging
                                
                                3. **Right Panel**
                                   - **Agent Activities**: View AI agent actions and updates
                                   - **Chat**: Communicate with AI agents
                                   - **Tasks**: Manage project tasks
                                
                                4. **Terminal** (Bottom Panel)
                                   - Execute commands
                                   - View command output
                                """
                            },
                            {
                                "title": "Working with Files",
                                "content": """
                                To work with files:
                                
                                1. Navigate to your file in the File Explorer
                                2. Click on the file to open it in the editor
                                3. Make your changes
                                4. Use the Save button or Ctrl+S to save
                                5. Use the Format button to format your code
                                """
                            },
                            {
                                "title": "Using the Chat",
                                "content": """
                                The chat panel allows you to:
                                
                                1. Ask questions about your code
                                2. Request code explanations
                                3. Get help with debugging
                                4. Discuss project requirements
                                
                                Type your message and press Enter or click Send.
                                """
                            }
                        ]
                    },
                    {
                        "id": "advanced-features",
                        "title": "Advanced Features",
                        "description": "Learn about advanced features and capabilities",
                        "sections": [
                            {
                                "title": "Real-time Collaboration",
                                "content": """
                                The platform supports real-time collaboration:
                                
                                1. Multiple users can edit the same file
                                2. See other users' cursors
                                3. Chat with team members
                                4. Share tasks and updates
                                """
                            },
                            {
                                "title": "Code Analysis",
                                "content": """
                                Use the built-in code analysis features:
                                
                                1. View code structure and dependencies
                                2. Get code quality metrics
                                3. Track changes and history
                                4. Generate documentation
                                """
                            }
                        ]
                    }
                ]
            }

    def _generate_dependency_graph(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dependency graph data for visualization"""
        components = project_data.get("components", [])
        dependencies = []
        
        for component in components:
            for dep in component.get("dependencies", []):
                dependencies.append({
                    "source": component["name"],
                    "target": dep,
                    "type": "depends_on"
                })
        
        return {
            "nodes": [{"id": comp["name"], "type": comp.get("type", "component")} for comp in components],
            "links": dependencies
        }

    def _generate_code_structure(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code structure data"""
        return {
            "files": project_data.get("files", []),
            "directories": project_data.get("directories", []),
            "dependencies": project_data.get("dependencies", {}),
            "components": project_data.get("components", [])
        }

    def create_dashboard(self):
        """Create the dashboard HTML file"""
        dashboard_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ADE Platform Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
        </head>
        <body class="bg-gray-100">
            <!-- Login Form -->
            <div id="login-form" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
                <div class="bg-white p-8 rounded-lg shadow-lg w-96">
                    <h2 class="text-2xl font-bold mb-6">Login</h2>
                    <form id="login" class="space-y-4">
                        <div>
                            <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
                                Username
                            </label>
                            <input type="text" id="username" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <div>
                            <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                                Password
                            </label>
                            <input type="password" id="password" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        </div>
                        <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full">
                            Login
                        </button>
                    </form>
                </div>
            </div>

            <!-- Main Dashboard -->
            <div id="dashboard" class="container mx-auto px-4 py-8 hidden">
                <div class="flex justify-between items-center mb-8">
                    <h1 class="text-3xl font-bold">ADE Platform Dashboard</h1>
                    <div class="flex items-center space-x-4">
                        <span id="user-info" class="text-gray-600"></span>
                        <button id="logout" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                            Logout
                        </button>
                    </div>
                </div>
                
                <!-- Project Selection -->
                <div class="mb-8">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="project-select">
                        Select Project
                    </label>
                    <select id="project-select" class="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                        <option value="">Loading projects...</option>
                    </select>
                </div>

                <!-- Project Info -->
                <div id="project-info" class="bg-white shadow rounded-lg p-6 mb-8 hidden">
                    <div class="flex justify-between items-start mb-4">
                        <h2 class="text-xl font-semibold">Project Information</h2>
                        <button id="edit-project" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                            Edit Project
                        </button>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <p class="text-gray-600">Name</p>
                            <p id="project-name" class="font-medium"></p>
                        </div>
                        <div>
                            <p class="text-gray-600">Description</p>
                            <p id="project-description" class="font-medium"></p>
                        </div>
                        <div>
                            <p class="text-gray-600">Created At</p>
                            <p id="project-created" class="font-medium"></p>
                        </div>
                        <div>
                            <p class="text-gray-600">Last Modified</p>
                            <p id="project-modified" class="font-medium"></p>
                        </div>
                    </div>
                </div>

                <!-- Visualizations -->
                <div id="visualizations" class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    <!-- Architecture Diagram -->
                    <div class="bg-white shadow rounded-lg p-6">
                        <h2 class="text-xl font-semibold mb-4">Architecture Diagram</h2>
                        <div id="architecture-diagram" class="w-full h-96"></div>
                    </div>

                    <!-- Component Relationships -->
                    <div class="bg-white shadow rounded-lg p-6">
                        <h2 class="text-xl font-semibold mb-4">Component Relationships</h2>
                        <div id="component-relationships" class="w-full h-96"></div>
                    </div>

                    <!-- Metrics Chart -->
                    <div class="bg-white shadow rounded-lg p-6 md:col-span-2">
                        <h2 class="text-xl font-semibold mb-4">Project Metrics</h2>
                        <canvas id="metrics-chart"></canvas>
                    </div>

                    <!-- Dependencies Graph -->
                    <div class="bg-white shadow rounded-lg p-6 md:col-span-2">
                        <h2 class="text-xl font-semibold mb-4">Dependencies Graph</h2>
                        <div id="dependencies-graph" class="w-full h-96"></div>
                    </div>
                </div>

                <!-- Components List -->
                <div class="bg-white shadow rounded-lg p-6 mb-8">
                    <h2 class="text-xl font-semibold mb-4">Components</h2>
                    <div id="components-list" class="space-y-4"></div>
                </div>
            </div>

            <script>
                // Authentication
                let token = localStorage.getItem('token');
                const loginForm = document.getElementById('login-form');
                const dashboard = document.getElementById('dashboard');
                const userInfo = document.getElementById('user-info');
                const logoutBtn = document.getElementById('logout');

                // Login form submission
                document.getElementById('login').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;

                    try {
                        const response = await fetch('/token', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                            },
                            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
                        });

                        if (response.ok) {
                            const data = await response.json();
                            token = data.access_token;
                            localStorage.setItem('token', token);
                            loginForm.classList.add('hidden');
                            dashboard.classList.remove('hidden');
                            userInfo.textContent = `Logged in as ${username}`;
                            loadProjects();
                        } else {
                            alert('Login failed');
                        }
                    } catch (error) {
                        console.error('Login error:', error);
                        alert('Login failed');
                    }
                });

                // Logout
                logoutBtn.addEventListener('click', () => {
                    localStorage.removeItem('token');
                    token = null;
                    loginForm.classList.remove('hidden');
                    dashboard.classList.add('hidden');
                });

                // Project selection
                const projectSelect = document.getElementById('project-select');
                const projectInfo = document.getElementById('project-info');
                let metricsChart = null;

                // Load projects
                async function loadProjects() {
                    try {
                        const response = await fetch('/api/projects', {
                            headers: {
                                'Authorization': `Bearer ${token}`
                            }
                        });
                        const projects = await response.json();
                        
                        projectSelect.innerHTML = projects.map(project => 
                            `<option value="${project.name}">${project.name}</option>`
                        ).join('');
                    } catch (error) {
                        console.error('Error loading projects:', error);
                    }
                }

                // Load project details
                async function loadProjectDetails(projectName) {
                    try {
                        const response = await fetch(`/api/projects/${projectName}`, {
                            headers: {
                                'Authorization': `Bearer ${token}`
                            }
                        });
                        const project = await response.json();
                        
                        // Update project info
                        document.getElementById('project-name').textContent = project.name;
                        document.getElementById('project-description').textContent = project.description;
                        document.getElementById('project-created').textContent = new Date(project.created_at).toLocaleString();
                        document.getElementById('project-modified').textContent = project.last_modified || 'Never';
                        
                        projectInfo.classList.remove('hidden');
                        
                        // Load visualizations
                        loadVisualizations(projectName);
                        
                        // Load metrics
                        loadMetrics(projectName);
                        
                        // Load components
                        loadComponents(projectName);
                        
                        // Load dependencies
                        loadDependencies(projectName);
                    } catch (error) {
                        console.error('Error loading project details:', error);
                    }
                }

                // Load visualizations
                async function loadVisualizations(projectName) {
                    try {
                        const response = await fetch(`/api/projects/${projectName}/visualizations`, {
                            headers: {
                                'Authorization': `Bearer ${token}`
                            }
                        });
                        const visualizations = await response.json();
                        
                        visualizations.forEach(viz => {
                            if (viz.name === 'architecture') {
                                document.getElementById('architecture-diagram').src = viz.url;
                            } else if (viz.name === 'component_relationships') {
                                document.getElementById('component-relationships').src = viz.url;
                            }
                        });
                    } catch (error) {
                        console.error('Error loading visualizations:', error);
                    }
                }

                // Load metrics
                async function loadMetrics(projectName) {
                    try {
                        const response = await fetch(`/api/projects/${projectName}/metrics`, {
                            headers: {
                                'Authorization': `Bearer ${token}`
                            }
                        });
                        const metrics = await response.json();
                        
                        // Destroy existing chart if it exists
                        if (metricsChart) {
                            metricsChart.destroy();
                        }
                        
                        // Create new chart
                        const ctx = document.getElementById('metrics-chart').getContext('2d');
                        metricsChart = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: Array.from({length: Math.max(...Object.values(metrics).map(m => m.length))}, (_, i) => i + 1),
                                datasets: Object.entries(metrics).map(([key, values]) => ({
                                    label: key.charAt(0).toUpperCase() + key.slice(1),
                                    data: values,
                                    borderColor: getRandomColor(),
                                    tension: 0.1
                                }))
                            },
                            options: {
                                responsive: true,
                                scales: {
                                    y: {
                                        beginAtZero: true
                                    }
                                }
                            }
                        });
                    } catch (error) {
                        console.error('Error loading metrics:', error);
                    }
                }

                // Load components
                async function loadComponents(projectName) {
                    try {
                        const response = await fetch(`/api/projects/${projectName}/components`, {
                            headers: {
                                'Authorization': `Bearer ${token}`
                            }
                        });
                        const components = await response.json();
                        
                        const componentsList = document.getElementById('components-list');
                        componentsList.innerHTML = components.map(component => `
                            <div class="border rounded p-4">
                                <h3 class="font-semibold">${component.name}</h3>
                                <p class="text-gray-600">${component.description || 'No description'}</p>
                                <div class="mt-2">
                                    <span class="text-sm text-gray-500">Type: ${component.type}</span>
                                </div>
                            </div>
                        `).join('');
                    } catch (error) {
                        console.error('Error loading components:', error);
                    }
                }

                // Load dependencies
                async function loadDependencies(projectName) {
                    try {
                        const response = await fetch(`/api/projects/${project_name}/dependencies`, {
                            headers: {
                                'Authorization': `Bearer ${token}`
                            }
                        });
                        const data = await response.json();
                        
                        // Create dependency graph using D3
                        const width = document.getElementById('dependencies-graph').clientWidth;
                        const height = 400;
                        
                        const svg = d3.select('#dependencies-graph')
                            .append('svg')
                            .attr('width', width)
                            .attr('height', height);
                        
                        // Create force simulation
                        const simulation = d3.forceSimulation(data.nodes)
                            .force('link', d3.forceLink(data.links).id(d => d.id))
                            .force('charge', d3.forceManyBody().strength(-100))
                            .force('center', d3.forceCenter(width / 2, height / 2));
                        
                        // Create links
                        const link = svg.append('g')
                            .selectAll('line')
                            .data(data.links)
                            .enter()
                            .append('line')
                            .attr('stroke', '#999')
                            .attr('stroke-opacity', 0.6);
                        
                        // Create nodes
                        const node = svg.append('g')
                            .selectAll('circle')
                            .data(data.nodes)
                            .enter()
                            .append('circle')
                            .attr('r', 5)
                            .attr('fill', d => getNodeColor(d.type))
                            .call(d3.drag()
                                .on('start', dragstarted)
                                .on('drag', dragged)
                                .on('end', dragended));
                        
                        // Add labels
                        const label = svg.append('g')
                            .selectAll('text')
                            .data(data.nodes)
                            .enter()
                            .append('text')
                            .text(d => d.id)
                            .attr('font-size', '12px')
                            .attr('dx', 8)
                            .attr('dy', 3);
                        
                        // Update positions on each tick
                        simulation.on('tick', () => {
                            link
                                .attr('x1', d => d.source.x)
                                .attr('y1', d => d.source.y)
                                .attr('x2', d => d.target.x)
                                .attr('y2', d => d.target.y);
                            
                            node
                                .attr('cx', d => d.x)
                                .attr('cy', d => d.y);
                            
                            label
                                .attr('x', d => d.x)
                                .attr('y', d => d.y);
                        });
                        
                        // Drag functions
                        function dragstarted(event) {
                            if (!event.active) simulation.alphaTarget(0.3).restart();
                            event.subject.fx = event.subject.x;
                            event.subject.fy = event.subject.y;
                        }
                        
                        function dragged(event) {
                            event.subject.fx = event.x;
                            event.subject.fy = event.y;
                        }
                        
                        function dragended(event) {
                            if (!event.active) simulation.alphaTarget(0);
                            event.subject.fx = null;
                            event.subject.fy = null;
                        }
                        
                        // Helper function for node colors
                        function getNodeColor(type) {
                            const colors = {
                                'component': '#4299e1',
                                'service': '#48bb78',
                                'database': '#ed8936',
                                'default': '#718096'
                            };
                            return colors[type] || colors.default;
                        }
                    } catch (error) {
                        console.error('Error loading dependencies:', error);
                    }
                }

                // Helper function to generate random colors
                function getRandomColor() {
                    const letters = '0123456789ABCDEF';
                    let color = '#';
                    for (let i = 0; i < 6; i++) {
                        color += letters[Math.floor(Math.random() * 16)];
                    }
                    return color;
                }

                // Event listeners
                projectSelect.addEventListener('change', (e) => {
                    if (e.target.value) {
                        loadProjectDetails(e.target.value);
                    }
                });

                // Edit project button
                document.getElementById('edit-project').addEventListener('click', () => {
                    // Implement project editing functionality
                    alert('Project editing functionality coming soon!');
                });

                // Check authentication on page load
                if (token) {
                    loginForm.classList.add('hidden');
                    dashboard.classList.remove('hidden');
                    userInfo.textContent = 'Logged in as demo';
                    loadProjects();
                }
            </script>
        </body>
        </html>
        """
        
        # Save the dashboard HTML
        dashboard_file = self.project_dir / "static" / "index.html"
        with open(dashboard_file, 'w') as f:
            f.write(dashboard_html)

    def create_workspace_view(self):
        """Create the workspace view HTML file"""
        workspace_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ADE Platform Workspace</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.33.0/min/vs/loader.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.33.0/min/vs/editor/editor.main.js"></script>
            <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
            <style>
                .workspace-container {
                    display: grid;
                    grid-template-columns: 250px 1fr 300px;
                    grid-template-rows: 1fr 300px;
                    height: 100vh;
                    gap: 4px;
                    padding: 4px;
                    background-color: #1e1e1e;
                }
                .panel {
                    background-color: #252526;
                    border-radius: 4px;
                    overflow: hidden;
                }
                .panel-header {
                    background-color: #333333;
                    padding: 8px;
                    color: #cccccc;
                    font-weight: 500;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .panel-content {
                    height: calc(100% - 40px);
                    overflow: auto;
                }
                .editor-container {
                    grid-column: 2;
                    grid-row: 1 / span 2;
                }
                .file-explorer {
                    grid-column: 1;
                    grid-row: 1 / span 2;
                }
                .right-panel {
                    grid-column: 3;
                    grid-row: 1 / span 2;
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }
                .agent-panel {
                    flex: 1;
                }
                .chat-panel {
                    flex: 1;
                }
                .tasks-panel {
                    flex: 1;
                }
                .terminal {
                    grid-column: 3;
                    grid-row: 2;
                }
                .file-tree {
                    padding: 8px;
                }
                .file-tree-item {
                    padding: 4px 8px;
                    cursor: pointer;
                    color: #cccccc;
                }
                .file-tree-item:hover {
                    background-color: #2a2d2e;
                }
                .agent-activity {
                    padding: 8px;
                    border-bottom: 1px solid #333333;
                    color: #cccccc;
                }
                .agent-activity:hover {
                    background-color: #2a2d2e;
                }
                .terminal-content {
                    padding: 8px;
                    font-family: monospace;
                    color: #cccccc;
                }
                .chat-message {
                    padding: 8px;
                    margin: 4px 0;
                    border-radius: 4px;
                    background-color: #2a2d2e;
                }
                .chat-message.user {
                    background-color: #1a4b8c;
                }
                .chat-message.agent {
                    background-color: #2a2d2e;
                }
                .task-item {
                    padding: 8px;
                    margin: 4px 0;
                    border-radius: 4px;
                    background-color: #2a2d2e;
                    cursor: pointer;
                }
                .task-item:hover {
                    background-color: #333333;
                }
                .task-item.completed {
                    opacity: 0.6;
                }
                .editor-toolbar {
                    padding: 4px;
                    background-color: #333333;
                    display: flex;
                    gap: 4px;
                }
                .editor-toolbar button {
                    padding: 4px 8px;
                    background-color: #2a2d2e;
                    border: none;
                    border-radius: 4px;
                    color: #cccccc;
                    cursor: pointer;
                }
                .editor-toolbar button:hover {
                    background-color: #3a3d3e;
                }
                .cursor {
                    position: absolute;
                    width: 3px;
                    height: 16px;
                    background-color: #00ff00;
                }
                .cursor-label {
                    position: absolute;
                    background-color: #00ff00;
                    color: #000000;
                    padding: 2px 4px;
                    border-radius: 2px;
                    font-size: 12px;
                }
                
                .tutorial-panel {
                    position: fixed;
                    top: 0;
                    right: 0;
                    width: 400px;
                    height: 100vh;
                    background-color: #252526;
                    border-left: 1px solid #333333;
                    z-index: 1000;
                    display: none;
                }
                
                .tutorial-panel.active {
                    display: block;
                }
                
                .tutorial-header {
                    padding: 16px;
                    background-color: #333333;
                    color: #cccccc;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .tutorial-content {
                    padding: 16px;
                    color: #cccccc;
                    overflow-y: auto;
                    height: calc(100vh - 60px);
                }
                
                .tutorial-section {
                    margin-bottom: 24px;
                }
                
                .tutorial-section h3 {
                    color: #ffffff;
                    margin-bottom: 12px;
                }
                
                .tutorial-section pre {
                    background-color: #1e1e1e;
                    padding: 12px;
                    border-radius: 4px;
                    overflow-x: auto;
                }
                
                .tutorial-section code {
                    font-family: monospace;
                    background-color: #1e1e1e;
                    padding: 2px 4px;
                    border-radius: 2px;
                }
                
                .tutorial-nav {
                    display: flex;
                    gap: 8px;
                    margin-top: 16px;
                }
                
                .tutorial-nav button {
                    padding: 8px 16px;
                    background-color: #2a2d2e;
                    border: none;
                    border-radius: 4px;
                    color: #cccccc;
                    cursor: pointer;
                }
                
                .tutorial-nav button:hover {
                    background-color: #3a3d3e;
                }
                
                .help-button {
                    position: fixed;
                    bottom: 16px;
                    right: 16px;
                    width: 48px;
                    height: 48px;
                    background-color: #007acc;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    z-index: 1000;
                }
                
                .help-button:hover {
                    background-color: #0098ff;
                }
            </style>
        </head>
        <body class="bg-gray-900">
            <div class="workspace-container">
                <!-- File Explorer -->
                <div class="panel file-explorer">
                    <div class="panel-header">
                        <span>File Explorer</span>
                        <button id="refresh-files" class="text-sm">🔄</button>
                    </div>
                    <div class="panel-content">
                        <div id="file-tree" class="file-tree"></div>
                    </div>
                </div>

                <!-- Code Editor -->
                <div class="panel editor-container">
                    <div class="panel-header">
                        <span>Code Editor</span>
                        <div class="editor-toolbar">
                            <button id="save-file">💾 Save</button>
                            <button id="format-code">📝 Format</button>
                            <button id="run-code">▶️ Run</button>
                            <button id="debug-code">🐛 Debug</button>
                        </div>
                    </div>
                    <div id="editor" class="panel-content"></div>
                </div>

                <!-- Right Panel -->
                <div class="right-panel">
                    <!-- Agent Panel -->
                    <div class="panel agent-panel">
                        <div class="panel-header">
                            <span>Agent Activities</span>
                            <button id="clear-activities" class="text-sm">🗑️</button>
                        </div>
                        <div class="panel-content">
                            <div id="agent-activities"></div>
                        </div>
                    </div>

                    <!-- Chat Panel -->
                    <div class="panel chat-panel">
                        <div class="panel-header">
                            <span>Chat</span>
                        </div>
                        <div class="panel-content">
                            <div id="chat-messages" class="flex-1 overflow-auto"></div>
                            <div class="chat-input p-4">
                                <div class="flex gap-2">
                                    <input type="text" id="chat-input" class="flex-1 bg-gray-700 text-white rounded px-2 py-1" placeholder="Type a message...">
                                    <button id="send-message" class="bg-blue-500 text-white px-4 py-1 rounded">Send</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Tasks Panel -->
                    <div class="panel tasks-panel">
                        <div class="panel-header">
                            <span>Tasks</span>
                            <button id="add-task" class="text-sm">➕</button>
                        </div>
                        <div class="panel-content">
                            <div id="tasks-list"></div>
                        </div>
                    </div>
                </div>

                <!-- Terminal -->
                <div class="panel terminal">
                    <div class="panel-header">
                        <span>Terminal</span>
                        <button id="clear-terminal" class="text-sm">🗑️</button>
                    </div>
                    <div class="panel-content">
                        <div id="terminal-content" class="terminal-content"></div>
                        <div class="terminal-input p-4">
                            <div class="flex gap-2">
                                <input type="text" id="terminal-input" class="flex-1 bg-gray-700 text-white rounded px-2 py-1" placeholder="Enter command...">
                                <button id="execute-command" class="bg-green-500 text-white px-4 py-1 rounded">Execute</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tutorial Panel -->
            <div class="tutorial-panel" id="tutorial-panel">
                <div class="tutorial-header">
                    <h2 id="tutorial-title">User Tutorial</h2>
                    <button onclick="closeTutorial()">✕</button>
                </div>
                <div class="tutorial-content">
                    <div id="tutorial-sections"></div>
                    <div class="tutorial-nav">
                        <button onclick="prevSection()">Previous</button>
                        <button onclick="nextSection()">Next</button>
                    </div>
                </div>
            </div>
            
            <!-- Help Button -->
            <div class="help-button" onclick="toggleTutorial()">?</div>
            
            <script>
                // Initialize Monaco Editor with collaboration features
                require.config({ paths: { 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.33.0/min/vs' }});
                require(['vs/editor/editor.main'], function() {
                    window.editor = monaco.editor.create(document.getElementById('editor'), {
                        value: '// Select a file to view its contents',
                        language: 'python',
                        theme: 'vs-dark',
                        automaticLayout: true,
                        minimap: { enabled: true },
                        scrollBeyondLastLine: false,
                        fontSize: 14,
                        lineNumbers: 'on',
                        roundedSelection: false,
                        scrollbar: {
                            vertical: 'visible',
                            horizontal: 'visible'
                        }
                    });

                    // Add cursor decorations for collaboration
                    window.cursors = new Map();
                    window.decorations = new Map();
                });

                // WebSocket connection for real-time collaboration
                let socket;
                const projectName = new URLSearchParams(window.location.search).get('project');
                if (projectName) {
                    socket = io(`/ws/${projectName}`);
                    
                    socket.on('connect', () => {
                        console.log('Connected to WebSocket server');
                    });

                    socket.on('editor_change', (data) => {
                        // Apply remote changes to editor
                        const model = window.editor.getModel();
                        model.pushEditOperations(
                            [],
                            [{
                                range: data.range,
                                text: data.text
                            }],
                            []
                        );
                    });

                    socket.on('cursor_move', (data) => {
                        // Update remote cursor
                        updateRemoteCursor(data.userId, data.position);
                    });

                    socket.on('chat_message', (data) => {
                        // Add new chat message
                        addChatMessage(data.message, data.userId);
                    });

                    socket.on('task_update', (data) => {
                        // Update task list
                        updateTaskList(data.tasks);
                    });
                }

                // Editor event handlers
                window.editor.onDidChangeModelContent(() => {
                    // Send changes to server
                    const model = window.editor.getModel();
                    const changes = model.getLastEditOperation();
                    if (changes) {
                        socket.emit('editor_change', {
                            range: changes.range,
                            text: changes.text
                        });
                    }
                });

                window.editor.onDidChangeCursorPosition((e) => {
                    // Send cursor position to server
                    socket.emit('cursor_move', {
                        position: e.position
                    });
                });

                // Chat functionality
                const chatInput = document.getElementById('chat-input');
                const sendMessage = document.getElementById('send-message');
                const chatMessages = document.getElementById('chat-messages');

                sendMessage.addEventListener('click', () => {
                    const message = chatInput.value.trim();
                    if (message) {
                        socket.emit('chat_message', {
                            message: message,
                            userId: getCurrentUserId()
                        });
                        chatInput.value = '';
                    }
                });

                chatInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        sendMessage.click();
                    }
                });

                // Task management
                const addTask = document.getElementById('add-task');
                const tasksList = document.getElementById('tasks-list');

                addTask.addEventListener('click', () => {
                    const taskName = prompt('Enter task name:');
                    if (taskName) {
                        socket.emit('task_update', {
                            action: 'add',
                            task: {
                                id: Date.now(),
                                name: taskName,
                                completed: false
                            }
                        });
                    }
                });

                // Terminal functionality
                const terminalInput = document.getElementById('terminal-input');
                const executeCommand = document.getElementById('execute-command');
                const terminalContent = document.getElementById('terminal-content');

                executeCommand.addEventListener('click', () => {
                    const command = terminalInput.value.trim();
                    if (command) {
                        socket.emit('execute_command', {
                            command: command
                        });
                        terminalInput.value = '';
                    }
                });

                terminalInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        executeCommand.click();
                    }
                });

                // Helper functions
                function updateRemoteCursor(userId, position) {
                    const cursor = window.cursors.get(userId);
                    if (cursor) {
                        window.editor.deltaDecorations(cursor, []);
                    }
                    
                    const newCursor = window.editor.deltaDecorations([], [{
                        range: new monaco.Range(
                            position.lineNumber,
                            position.column,
                            position.lineNumber,
                            position.column + 1
                        ),
                        options: {
                            className: 'cursor',
                            hoverMessage: { value: `User ${userId}` }
                        }
                    }]);
                    
                    window.cursors.set(userId, newCursor);
                }

                function addChatMessage(message, userId) {
                    const messageElement = document.createElement('div');
                    messageElement.className = `chat-message ${userId === getCurrentUserId() ? 'user' : 'agent'}`;
                    messageElement.textContent = message;
                    chatMessages.appendChild(messageElement);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }

                function updateTaskList(tasks) {
                    tasksList.innerHTML = tasks.map(task => `
                        <div class="task-item ${task.completed ? 'completed' : ''}" data-id="${task.id}">
                            <div class="flex items-center">
                                <input type="checkbox" ${task.completed ? 'checked' : ''} class="mr-2">
                                <span>${task.name}</span>
                            </div>
                        </div>
                    `).join('');
                }

                function getCurrentUserId() {
                    return localStorage.getItem('userId') || 'anonymous';
                }

                // Initial load
                if (projectName) {
                    loadCodeStructure(projectName);
                    loadAgentActivities(projectName);
                    loadChatHistory(projectName);
                    loadTasks(projectName);
                } else {
                    window.location.href = '/';
                }

                // Tutorial functionality
                let currentTutorial = null;
                let currentSection = 0;
                
                async function loadTutorials() {
                    try {
                        const response = await fetch('/api/tutorials', {
                            headers: {
                                'Authorization': `Bearer ${localStorage.getItem('token')}`
                            }
                        });
                        const data = await response.json();
                        return data.tutorials;
                    } catch (error) {
                        console.error('Error loading tutorials:', error);
                        return [];
                    }
                }
                
                function toggleTutorial() {
                    const panel = document.getElementById('tutorial-panel');
                    if (panel.classList.contains('active')) {
                        closeTutorial();
                    } else {
                        openTutorial();
                    }
                }
                
                async function openTutorial() {
                    const tutorials = await loadTutorials();
                    if (tutorials.length > 0) {
                        currentTutorial = tutorials[0];
                        currentSection = 0;
                        renderTutorial();
                        document.getElementById('tutorial-panel').classList.add('active');
                    }
                }
                
                function closeTutorial() {
                    document.getElementById('tutorial-panel').classList.remove('active');
                    currentTutorial = null;
                    currentSection = 0;
                }
                
                function renderTutorial() {
                    if (!currentTutorial) return;
                    
                    document.getElementById('tutorial-title').textContent = currentTutorial.title;
                    const sections = document.getElementById('tutorial-sections');
                    sections.innerHTML = currentTutorial.sections.map((section, index) => `
                        <div class="tutorial-section" style="display: ${index === currentSection ? 'block' : 'none'}">
                            <h3>${section.title}</h3>
                            <div>${section.content}</div>
                        </div>
                    `).join('');
                }
                
                function nextSection() {
                    if (currentTutorial && currentSection < currentTutorial.sections.length - 1) {
                        currentSection++;
                        renderTutorial();
                    }
                }
                
                function prevSection() {
                    if (currentTutorial && currentSection > 0) {
                        currentSection--;
                        renderTutorial();
                    }
                }
                
                // Add keyboard shortcuts
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape') {
                        closeTutorial();
                    }
                    if (e.key === 'ArrowRight') {
                        nextSection();
                    }
                    if (e.key === 'ArrowLeft') {
                        prevSection();
                    }
                });
            </script>
        </body>
        </html>
        """
        
        # Save the workspace view HTML
        workspace_file = self.project_dir / "static" / "workspace.html"
        with open(workspace_file, 'w') as f:
            f.write(workspace_html)

    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """Run the web interface"""
        self.create_dashboard()
        self.create_workspace_view()
        import uvicorn
        uvicorn.run(self.app, host=host, port=port) 