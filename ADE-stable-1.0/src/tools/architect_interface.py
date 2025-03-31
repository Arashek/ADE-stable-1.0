import os
import sys
from pathlib import Path
import json
from typing import List, Dict, Any
import time
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

class ArchitectInterface:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.current_project = None
        self.architect_agent = None
        self.project_history = []
        self.current_state = {
            'project_name': None,
            'description': None,
            'architecture': None,
            'components': [],
            'current_phase': None,
            'last_modified': None
        }
        self.console = Console()
        self.visualization_dir = self.project_dir / "visualizations"
        self.visualization_dir.mkdir(exist_ok=True)

    def start_new_project(self) -> None:
        """Start a new project with the architect agent"""
        self.console.print(Panel.fit(
            "[bold blue]Starting New Project with ADE Architect[/bold blue]",
            title="Project Initialization"
        ))
        
        # Get project details with rich interface
        project_name = self.console.input("[bold]Enter project name: [/bold]")
        description = self.console.input("[bold]Enter project description: [/bold]")
        
        # Initialize project structure
        self.current_project = {
            'name': project_name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'components': [],
            'architecture': None,
            'development_history': [],
            'metrics': {
                'complexity': [],
                'performance': [],
                'documentation': []
            }
        }
        
        self.console.print(f"\n[green]Project '{project_name}' initialized successfully![/green]")
        self.show_project_menu()

    def show_project_menu(self) -> None:
        """Show the main project menu with rich interface"""
        menu = Table(title="Project Menu")
        menu.add_column("Option", style="cyan")
        menu.add_column("Description", style="white")
        
        menu.add_row("design", "Request architectural design")
        menu.add_row("implement", "Request implementation of components")
        menu.add_row("improve", "Request improvements to existing components")
        menu.add_row("review", "Review current project state")
        menu.add_row("status", "Check project status")
        menu.add_row("visualize", "Generate visualizations")
        menu.add_row("metrics", "View project metrics")
        menu.add_row("help", "Show available commands")
        menu.add_row("exit", "Exit project")
        
        self.console.print(menu)

    def interact_with_architect(self) -> None:
        """Main interaction loop with the architect agent"""
        if not self.current_project:
            self.console.print("[red]No active project. Please start a new project first.[/red]")
            return
        
        self.console.print(Panel.fit(
            "[bold blue]Architect Agent: Hello! I'm your ADE architect agent. How can I help you today?[/bold blue]"
        ))
        
        while True:
            command = self.console.input("\n[bold]Your command: [/bold]").lower().strip()
            
            if command == 'exit':
                if self.console.input("\n[yellow]Would you like to save the project before exiting? (y/n): [/yellow]").lower() == 'y':
                    self.save_project()
                self.console.print("\n[green]Exiting project...[/green]")
                break
            
            elif command == 'help':
                self.show_project_menu()
            
            elif command == 'design':
                self.request_design()
            
            elif command == 'implement':
                self.request_implementation()
            
            elif command == 'improve':
                self.request_improvements()
            
            elif command == 'review':
                self.review_project()
            
            elif command == 'status':
                self.check_status()
            
            elif command == 'visualize':
                self.generate_visualizations()
            
            elif command == 'metrics':
                self.view_metrics()
            
            else:
                self.console.print("[red]I'm not sure how to help with that. Type 'help' to see available commands.[/red]")

    def request_design(self) -> None:
        """Request architectural design from the architect agent"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Designing architecture...", total=None)
            
            self.console.print("\n[bold]Please describe your requirements in detail:[/bold]")
            requirements = self.console.input("> ")
            
            # Simulate design process
            time.sleep(2)
            
            self.console.print("\n[bold]Architect Agent: Based on your requirements, I suggest the following architecture:[/bold]")
            architecture_table = Table(title="Proposed Architecture")
            architecture_table.add_column("Component", style="cyan")
            architecture_table.add_column("Technology", style="green")
            
            architecture_table.add_row("Frontend", "React with TypeScript")
            architecture_table.add_row("Backend", "FastAPI with Python")
            architecture_table.add_row("Database", "PostgreSQL")
            architecture_table.add_row("Authentication", "JWT")
            
            self.console.print(architecture_table)
            
            if self.console.input("\n[yellow]Would you like me to proceed with this architecture? (y/n): [/yellow]").lower() == 'y':
                self.current_project['architecture'] = {
                    'frontend': 'React with TypeScript',
                    'backend': 'FastAPI with Python',
                    'database': 'PostgreSQL',
                    'auth': 'JWT'
                }
                self.console.print("\n[green]Architecture saved successfully![/green]")
                
                if self.console.input("\n[yellow]Would you like to start implementing components? (y/n): [/yellow]").lower() == 'y':
                    self.request_implementation()

    def request_implementation(self) -> None:
        """Request implementation of components"""
        if not self.current_project.get('architecture'):
            print("\nArchitect Agent: We need to design the architecture first. Would you like to do that now?")
            if input().lower() == 'y':
                self.request_design()
            return
        
        print("\nArchitect Agent: I'll help you implement the components. Which component would you like to start with?")
        print("1. Frontend setup")
        print("2. Backend setup")
        print("3. Database setup")
        print("4. Authentication system")
        
        choice = input("Enter your choice (1-4): ")
        
        # Simulate implementation
        print("\nArchitect Agent: Starting implementation...")
        time.sleep(2)
        
        component = {
            'name': f"Component {choice}",
            'implemented_at': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        self.current_project['components'].append(component)
        print(f"\nArchitect Agent: Component {choice} has been implemented.")
        print("Would you like to implement another component? (y/n)")
        
        if input().lower() == 'y':
            self.request_implementation()

    def request_improvements(self) -> None:
        """Request improvements to existing components"""
        if not self.current_project.get('components'):
            print("\nArchitect Agent: No components to improve yet. Would you like to implement some components?")
            if input().lower() == 'y':
                self.request_implementation()
            return
        
        print("\nArchitect Agent: Which component would you like to improve?")
        for i, component in enumerate(self.current_project['components'], 1):
            print(f"{i}. {component['name']}")
        
        choice = int(input("Enter component number: "))
        
        print("\nArchitect Agent: Please describe the improvements you'd like to make:")
        improvements = input("> ")
        
        # Simulate improvements
        print("\nArchitect Agent: Implementing improvements...")
        time.sleep(2)
        
        self.current_project['components'][choice-1]['improvements'] = improvements
        print("\nArchitect Agent: Improvements have been applied.")
        print("Would you like to review the changes? (y/n)")
        
        if input().lower() == 'y':
            self.review_project()

    def review_project(self) -> None:
        """Review current project state"""
        print("\nProject Review:")
        print(f"Name: {self.current_project['name']}")
        print(f"Description: {self.current_project['description']}")
        print(f"Created: {self.current_project['created_at']}")
        
        if self.current_project.get('architecture'):
            print("\nArchitecture:")
            for key, value in self.current_project['architecture'].items():
                print(f"- {key.title()}: {value}")
        
        if self.current_project.get('components'):
            print("\nComponents:")
            for component in self.current_project['components']:
                print(f"- {component['name']}")
                if component.get('improvements'):
                    print(f"  Improvements: {component['improvements']}")

    def check_status(self) -> None:
        """Check project status"""
        print("\nProject Status:")
        print(f"Name: {self.current_project['name']}")
        print(f"Components: {len(self.current_project.get('components', []))}")
        print(f"Last Modified: {self.current_project.get('last_modified', 'Never')}")
        
        if self.current_project.get('architecture'):
            print("Architecture: Defined")
        else:
            print("Architecture: Not defined")

    def generate_visualizations(self) -> None:
        """Generate visualizations for the project"""
        if not self.current_project:
            self.console.print("[red]No active project to visualize.[/red]")
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            # Generate architecture diagram
            task = progress.add_task("[cyan]Generating architecture diagram...", total=None)
            self._generate_architecture_diagram()
            
            # Generate metrics visualization
            task = progress.add_task("[cyan]Generating metrics visualization...", total=None)
            self._generate_metrics_visualization()
            
            # Generate component relationships
            task = progress.add_task("[cyan]Generating component relationships...", total=None)
            self._generate_component_relationships()
        
        self.console.print(f"\n[green]Visualizations saved to: {self.visualization_dir}[/green]")

    def _generate_architecture_diagram(self) -> None:
        """Generate architecture diagram using networkx"""
        G = nx.DiGraph()
        
        # Add nodes
        G.add_node("Frontend", type="component")
        G.add_node("Backend", type="component")
        G.add_node("Database", type="component")
        G.add_node("Auth", type="component")
        
        # Add edges
        G.add_edge("Frontend", "Backend")
        G.add_edge("Backend", "Database")
        G.add_edge("Frontend", "Auth")
        G.add_edge("Backend", "Auth")
        
        # Draw the diagram
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                node_size=2000, font_size=10, font_weight='bold')
        
        plt.savefig(self.visualization_dir / "architecture.png")
        plt.close()

    def _generate_metrics_visualization(self) -> None:
        """Generate metrics visualization"""
        if not self.current_project.get('metrics'):
            return
        
        metrics = self.current_project['metrics']
        
        # Create subplots
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Plot complexity
        axes[0].plot(metrics['complexity'])
        axes[0].set_title('Complexity Over Time')
        
        # Plot performance
        axes[1].plot(metrics['performance'])
        axes[1].set_title('Performance Over Time')
        
        # Plot documentation
        axes[2].plot(metrics['documentation'])
        axes[2].set_title('Documentation Coverage')
        
        plt.tight_layout()
        plt.savefig(self.visualization_dir / "metrics.png")
        plt.close()

    def _generate_component_relationships(self) -> None:
        """Generate component relationships visualization"""
        if not self.current_project.get('components'):
            return
        
        # Create a graph of component relationships
        G = nx.Graph()
        
        # Add components as nodes
        for component in self.current_project['components']:
            G.add_node(component['name'])
        
        # Add relationships based on dependencies
        for i, comp1 in enumerate(self.current_project['components']):
            for comp2 in self.current_project['components'][i+1:]:
                if self._components_related(comp1, comp2):
                    G.add_edge(comp1['name'], comp2['name'])
        
        # Draw the graph
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightgreen',
                node_size=2000, font_size=10, font_weight='bold')
        
        plt.savefig(self.visualization_dir / "component_relationships.png")
        plt.close()

    def _components_related(self, comp1: Dict, comp2: Dict) -> bool:
        """Check if two components are related"""
        # This is a simple example - you would implement more sophisticated logic
        return comp1.get('type') == comp2.get('type')

    def view_metrics(self) -> None:
        """View project metrics with rich interface"""
        if not self.current_project.get('metrics'):
            self.console.print("[yellow]No metrics available yet.[/yellow]")
            return
        
        metrics_table = Table(title="Project Metrics")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Current Value", style="green")
        metrics_table.add_column("Trend", style="yellow")
        
        metrics = self.current_project['metrics']
        for metric, values in metrics.items():
            current_value = values[-1] if values else 0
            trend = "↑" if len(values) > 1 and values[-1] > values[-2] else "↓"
            metrics_table.add_row(metric.title(), str(current_value), trend)
        
        self.console.print(metrics_table)

    def save_project(self) -> None:
        """Save project to file"""
        if not self.current_project:
            return
        
        project_file = self.project_dir / f"{self.current_project['name']}.json"
        with open(project_file, 'w') as f:
            json.dump(self.current_project, f, indent=2)
        self.console.print(f"\n[green]Project saved to: {project_file}[/green]")

def main():
    """Main entry point for the architect interface"""
    # Get project directory from environment or use default
    project_dir = os.getenv("ADE_PROJECT_DIR", "D:/ade-platform/projects")
    
    # Create projects directory if it doesn't exist
    Path(project_dir).mkdir(parents=True, exist_ok=True)
    
    interface = ArchitectInterface(project_dir)
    
    while True:
        interface.console.print(Panel.fit(
            "[bold blue]ADE Architect Interface[/bold blue]",
            title="Main Menu"
        ))
        
        menu = Table()
        menu.add_column("Option", style="cyan")
        menu.add_column("Description", style="white")
        
        menu.add_row("1", "Start new project")
        menu.add_row("2", "Load existing project")
        menu.add_row("3", "Exit")
        
        interface.console.print(menu)
        
        choice = interface.console.input("\n[bold]Enter your choice (1-3): [/bold]")
        
        if choice == "1":
            interface.start_new_project()
            interface.interact_with_architect()
        elif choice == "2":
            interface.console.print("\n[yellow]Project loading not implemented yet.[/yellow]")
        elif choice == "3":
            interface.console.print("\n[green]Exiting...[/green]")
            break
        else:
            interface.console.print("\n[red]Invalid choice. Please try again.[/red]")
        
        time.sleep(1)

if __name__ == "__main__":
    main() 