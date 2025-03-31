import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import yaml
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import (
    TrainingConfig,
    AWSConfig,
    ModelConfig,
    DatasetConfig
)
from .aws_manager import AWSManager
from .model_manager import ModelManager
from .sync_manager import SyncManager
from .utils import setup_logging, load_config

console = Console()

class TrainingManager:
    """Main interface for managing ADE model training."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        self.console = Console()
        
        # Initialize managers
        self.aws_manager = None
        self.model_manager = None
        self.sync_manager = None
        
        # Load configurations
        self.config = None
        self.aws_config = None
        
    def initialize(self) -> bool:
        """Initialize the training manager."""
        try:
            # Load configurations
            self.config = load_config(self.config_path)
            self.aws_config = load_config(self.config.aws_config_path)
            
            # Initialize AWS manager
            self.aws_manager = AWSManager(self.aws_config)
            if not self.aws_manager.verify_credentials():
                self.console.print("[red]Failed to verify AWS credentials[/red]")
                return False
                
            # Initialize model manager
            self.model_manager = ModelManager(self.config)
            
            # Initialize sync manager
            self.sync_manager = SyncManager(
                aws_manager=self.aws_manager,
                model_manager=self.model_manager
            )
            
            self.console.print("[green]Training manager initialized successfully[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Failed to initialize training manager: {e}[/red]")
            return False
            
    def train_model(self, model_name: str, phase: str) -> bool:
        """Train a specific model phase."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                # Prepare training environment
                progress.add_task(description="Preparing training environment...", total=None)
                if not self.model_manager.prepare_environment(model_name, phase):
                    return False
                    
                # Train model
                progress.add_task(description="Training model...", total=None)
                if not self.model_manager.train(model_name, phase):
                    return False
                    
                # Evaluate model
                progress.add_task(description="Evaluating model...", total=None)
                if not self.model_manager.evaluate(model_name, phase):
                    return False
                    
                # Upload to AWS
                progress.add_task(description="Uploading model to AWS...", total=None)
                if not self.aws_manager.upload_model(model_name, phase):
                    return False
                    
                # Sync with ADE platform
                progress.add_task(description="Syncing with ADE platform...", total=None)
                if not self.sync_manager.sync_model(model_name, phase):
                    return False
                    
            self.console.print(f"[green]Successfully completed training for {model_name} - {phase}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error during training: {e}[/red]")
            return False
            
    def evaluate_model(self, model_name: str, phase: str) -> Dict[str, Any]:
        """Evaluate a trained model."""
        try:
            results = self.model_manager.evaluate(model_name, phase)
            
            # Display results in a table
            table = Table(title=f"Evaluation Results - {model_name} - {phase}")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            for metric, value in results.items():
                table.add_row(metric, str(value))
                
            self.console.print(table)
            return results
            
        except Exception as e:
            self.console.print(f"[red]Error during evaluation: {e}[/red]")
            return {}
            
    def deploy_model(self, model_name: str, phase: str, environment: str) -> bool:
        """Deploy a model to a specific environment."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                # Download from AWS
                progress.add_task(description="Downloading model from AWS...", total=None)
                if not self.aws_manager.download_model(model_name, phase):
                    return False
                    
                # Deploy to environment
                progress.add_task(description=f"Deploying to {environment}...", total=None)
                if not self.model_manager.deploy(model_name, phase, environment):
                    return False
                    
                # Verify deployment
                progress.add_task(description="Verifying deployment...", total=None)
                if not self.model_manager.verify_deployment(model_name, phase, environment):
                    return False
                    
            self.console.print(f"[green]Successfully deployed {model_name} - {phase} to {environment}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error during deployment: {e}[/red]")
            return False
            
    def sync_models(self) -> bool:
        """Synchronize all models with the ADE platform."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                # Get list of models to sync
                models = self.model_manager.get_model_list()
                
                for model in models:
                    progress.add_task(description=f"Syncing {model}...", total=None)
                    if not self.sync_manager.sync_model(model):
                        return False
                        
            self.console.print("[green]Successfully synchronized all models[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error during synchronization: {e}[/red]")
            return False
            
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models and their status."""
        try:
            models = self.model_manager.get_model_list()
            
            # Display models in a table
            table = Table(title="Available Models")
            table.add_column("Model Name", style="cyan")
            table.add_column("Phase", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Last Updated", style="magenta")
            
            for model in models:
                status = self.model_manager.get_model_status(model)
                last_updated = self.model_manager.get_last_updated(model)
                table.add_row(
                    model["name"],
                    model["phase"],
                    status,
                    last_updated.strftime("%Y-%m-%d %H:%M:%S")
                )
                
            self.console.print(table)
            return models
            
        except Exception as e:
            self.console.print(f"[red]Error listing models: {e}[/red]")
            return []

@click.group()
@click.option('--config', type=click.Path(exists=True), required=True,
              help='Path to the configuration file')
@click.pass_context
def cli(ctx, config):
    """ADE Training Manager CLI"""
    ctx.ensure_object(dict)
    ctx.obj['manager'] = TrainingManager(config)

@cli.command()
@click.pass_context
def init(ctx):
    """Initialize the training manager"""
    manager = ctx.obj['manager']
    if manager.initialize():
        click.echo("Training manager initialized successfully")
    else:
        click.echo("Failed to initialize training manager", err=True)

@cli.command()
@click.argument('model_name')
@click.argument('phase')
@click.pass_context
def train(ctx, model_name, phase):
    """Train a specific model phase"""
    manager = ctx.obj['manager']
    if manager.train_model(model_name, phase):
        click.echo(f"Successfully trained {model_name} - {phase}")
    else:
        click.echo(f"Failed to train {model_name} - {phase}", err=True)

@cli.command()
@click.argument('model_name')
@click.argument('phase')
@click.pass_context
def evaluate(ctx, model_name, phase):
    """Evaluate a trained model"""
    manager = ctx.obj['manager']
    manager.evaluate_model(model_name, phase)

@cli.command()
@click.argument('model_name')
@click.argument('phase')
@click.argument('environment')
@click.pass_context
def deploy(ctx, model_name, phase, environment):
    """Deploy a model to a specific environment"""
    manager = ctx.obj['manager']
    if manager.deploy_model(model_name, phase, environment):
        click.echo(f"Successfully deployed {model_name} - {phase} to {environment}")
    else:
        click.echo(f"Failed to deploy {model_name} - {phase} to {environment}", err=True)

@cli.command()
@click.pass_context
def sync(ctx):
    """Synchronize all models with the ADE platform"""
    manager = ctx.obj['manager']
    if manager.sync_models():
        click.echo("Successfully synchronized all models")
    else:
        click.echo("Failed to synchronize models", err=True)

@cli.command()
@click.pass_context
def list(ctx):
    """List all available models"""
    manager = ctx.obj['manager']
    manager.list_models()

if __name__ == '__main__':
    cli() 