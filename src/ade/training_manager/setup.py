#!/usr/bin/env python3
import os
import sys
import json
import click
import subprocess
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def check_python_version():
    """Check if Python version meets requirements."""
    if sys.version_info < (3, 8):
        console.print("[red]Error: Python 3.8 or higher is required[/red]")
        sys.exit(1)

def setup_virtual_environment():
    """Create and activate virtual environment."""
    console.print("\n[bold]Step 1: Setting up virtual environment[/bold]")
    
    if not os.path.exists("venv"):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating virtual environment...", total=None)
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            progress.update(task, completed=True)
    
    # Get the path to the virtual environment's Python executable
    if sys.platform == "win32":
        python_path = "venv\\Scripts\\python.exe"
    else:
        python_path = "venv/bin/python"
    
    return python_path

def install_dependencies(python_path):
    """Install required packages."""
    console.print("\n[bold]Step 2: Installing dependencies[/bold]")
    
    requirements_path = Path(__file__).parent / "requirements.txt"
    if not requirements_path.exists():
        console.print("[red]Error: requirements.txt not found[/red]")
        sys.exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Installing dependencies...", total=None)
        subprocess.run([python_path, "-m", "pip", "install", "-r", str(requirements_path)], check=True)
        progress.update(task, completed=True)

def configure_aws():
    """Configure AWS credentials."""
    console.print("\n[bold]Step 3: Configuring AWS credentials[/bold]")
    
    aws_config = {
        "region": Prompt.ask("Enter AWS region", default="us-east-1"),
        "access_key": Prompt.ask("Enter AWS access key ID", password=True),
        "secret_key": Prompt.ask("Enter AWS secret access key", password=True),
        "profile_name": Prompt.ask("Enter AWS profile name", default="ade-platform"),
        "s3_bucket": Prompt.ask("Enter S3 bucket name")
    }
    
    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)
    
    with open(config_dir / "aws_config.json", "w") as f:
        json.dump(aws_config, f, indent=2)
    
    console.print("[green]✓ AWS configuration saved[/green]")

def setup_directories():
    """Create necessary directories."""
    console.print("\n[bold]Step 4: Creating directory structure[/bold]")
    
    directories = [
        "data/train",
        "data/validation",
        "data/test",
        "output",
        "checkpoints",
        "logs",
        "sync_status"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓ Created {directory}[/green]")

def create_example_dataset():
    """Create an example dataset file."""
    console.print("\n[bold]Step 5: Creating example dataset[/bold]")
    
    example_data = {
        "data": [
            {
                "input": "def calculate_sum(numbers):",
                "output": "    return sum(numbers)",
                "metadata": {
                    "source": "example",
                    "language": "python",
                    "difficulty": "easy"
                }
            }
        ]
    }
    
    dataset_path = Path("data/train/code_completion.json")
    with open(dataset_path, "w") as f:
        json.dump(example_data, f, indent=2)
    
    console.print(f"[green]✓ Created example dataset at {dataset_path}[/green]")

def verify_setup():
    """Verify the setup is complete."""
    console.print("\n[bold]Step 6: Verifying setup[/bold]")
    
    # Check Python version
    check_python_version()
    console.print("[green]✓ Python version verified[/green]")
    
    # Check virtual environment
    if os.path.exists("venv"):
        console.print("[green]✓ Virtual environment verified[/green]")
    else:
        console.print("[red]✗ Virtual environment not found[/red]")
        return False
    
    # Check AWS configuration
    aws_config_path = Path(__file__).parent / "config" / "aws_config.json"
    if aws_config_path.exists():
        console.print("[green]✓ AWS configuration verified[/green]")
    else:
        console.print("[red]✗ AWS configuration not found[/red]")
        return False
    
    # Check directories
    required_dirs = ["data/train", "data/validation", "data/test", "output", "checkpoints", "logs", "sync_status"]
    for directory in required_dirs:
        if os.path.exists(directory):
            console.print(f"[green]✓ Directory {directory} verified[/green]")
        else:
            console.print(f"[red]✗ Directory {directory} not found[/red]")
            return False
    
    return True

@click.command()
def main():
    """Interactive setup script for ADE Training Manager."""
    console.print(Panel.fit(
        "[bold blue]ADE Training Manager Setup[/bold blue]\n"
        "This script will help you set up the training environment.",
        title="Welcome"
    ))
    
    if not Confirm.ask("Do you want to proceed with the setup?"):
        console.print("[yellow]Setup cancelled[/yellow]")
        return
    
    try:
        # Check Python version
        check_python_version()
        
        # Setup virtual environment
        python_path = setup_virtual_environment()
        
        # Install dependencies
        install_dependencies(python_path)
        
        # Configure AWS
        configure_aws()
        
        # Setup directories
        setup_directories()
        
        # Create example dataset
        create_example_dataset()
        
        # Verify setup
        if verify_setup():
            console.print(Panel.fit(
                "[bold green]Setup completed successfully![/bold green]\n"
                "You can now start using the ADE Training Manager.\n"
                "Run 'python -m ade.training_manager.manager --help' for usage information.",
                title="Success"
            ))
        else:
            console.print(Panel.fit(
                "[bold red]Setup verification failed[/bold red]\n"
                "Please check the errors above and try again.",
                title="Error"
            ))
    
    except Exception as e:
        console.print(f"[red]Error during setup: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main() 