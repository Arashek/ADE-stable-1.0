import click
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from .config.training_config import ConfigManager
from .checkpoint_manager import CheckpointManager
from .owner.interface.training_monitor import TrainingMonitor
from ...config.logging_config import logger

@click.group()
def cli():
    """ADE Training CLI"""
    pass

@cli.command()
@click.argument('config_name')
@click.option('--output-dir', '-o', help='Output directory for training results')
@click.option('--resume-from', '-r', help='Path to checkpoint to resume from')
@click.option('--port', '-p', default=8000, help='Port for training monitor')
def train(config_name: str, output_dir: str, resume_from: str, port: int):
    """Start a new training session"""
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config(config_name)
        
        # Override output directory if specified
        if output_dir:
            config.output_dir = output_dir
            
        # Override resume path if specified
        if resume_from:
            config.resume_from = resume_from
            
        # Create output directory
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Start training monitor
        monitor = TrainingMonitor(output_dir=str(output_dir))
        monitor.start_session(config_name, config_name)
        
        # Start monitor
        monitor.run(port=port)
        
    except Exception as e:
        logger.error(f"Error starting training: {str(e)}")
        raise click.Abort()

@cli.command()
@click.argument('session_id')
def stop(session_id: str):
    """Stop a training session"""
    try:
        # Load monitor
        monitor = TrainingMonitor()
        
        # End session
        monitor.end_session(session_id)
        click.echo(f"Stopped training session: {session_id}")
        
    except Exception as e:
        logger.error(f"Error stopping session: {str(e)}")
        raise click.Abort()

@cli.command()
def list_sessions():
    """List all active training sessions"""
    try:
        # Load monitor
        monitor = TrainingMonitor()
        
        # Get sessions
        sessions = monitor.active_sessions
        
        if not sessions:
            click.echo("No active training sessions")
            return
            
        # Print sessions
        for session_id, session in sessions.items():
            click.echo(f"\nSession ID: {session_id}")
            click.echo(f"Config: {session['config']}")
            click.echo(f"Started: {session['start_time']}")
            click.echo(f"Current Episode: {session['current_episode']}")
            
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise click.Abort()

@cli.command()
@click.argument('session_id')
def show_metrics(session_id: str):
    """Show metrics for a training session"""
    try:
        # Load monitor
        monitor = TrainingMonitor()
        
        # Get session
        if session_id not in monitor.active_sessions:
            click.echo(f"Session not found: {session_id}")
            return
            
        session = monitor.active_sessions[session_id]
        
        # Print metrics
        click.echo(f"\nMetrics for session {session_id}:")
        click.echo(f"Average Reward: {np.mean(session['metrics']['rewards']):.2f}")
        click.echo(f"Completion Accuracy: {np.mean(session['metrics']['accuracy']):.2f}")
        click.echo(f"Exploration Rate: {np.mean(session['metrics']['exploration']):.2f}")
        
    except Exception as e:
        logger.error(f"Error showing metrics: {str(e)}")
        raise click.Abort()

@cli.command()
@click.argument('config_name')
@click.option('--output', '-o', help='Output file for configuration')
def show_config(config_name: str, output: str):
    """Show or save training configuration"""
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config(config_name)
        
        # Convert to dictionary
        config_dict = config.__dict__
        
        if output:
            # Save to file
            with open(output, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
            click.echo(f"Saved configuration to {output}")
        else:
            # Print to console
            click.echo(yaml.dump(config_dict, default_flow_style=False))
            
    except Exception as e:
        logger.error(f"Error showing config: {str(e)}")
        raise click.Abort()

@cli.command()
@click.argument('checkpoint_path')
def resume(checkpoint_path: str):
    """Resume training from a checkpoint"""
    try:
        # Load checkpoint
        checkpoint_manager = CheckpointManager("data/learning/training")
        checkpoint_data = checkpoint_manager.load_checkpoint(checkpoint_path)
        
        # Get config
        config = checkpoint_data['config']
        
        # Start training
        train(config['name'], resume_from=checkpoint_path)
        
    except Exception as e:
        logger.error(f"Error resuming from checkpoint: {str(e)}")
        raise click.Abort()

@cli.command()
def list_checkpoints():
    """List all available checkpoints"""
    try:
        # Load checkpoint manager
        checkpoint_manager = CheckpointManager("data/learning/training")
        
        # Get checkpoints
        checkpoints = checkpoint_manager.list_checkpoints()
        
        if not checkpoints:
            click.echo("No checkpoints found")
            return
            
        # Print checkpoints
        for checkpoint in checkpoints:
            click.echo(f"\nCheckpoint: {checkpoint['path']}")
            click.echo(f"Episode: {checkpoint['episode']}")
            click.echo(f"Created: {checkpoint['timestamp']}")
            click.echo("Metrics:")
            for metric, value in checkpoint['metrics'].items():
                click.echo(f"  {metric}: {value:.2f}")
                
    except Exception as e:
        logger.error(f"Error listing checkpoints: {str(e)}")
        raise click.Abort()

@cli.command()
@click.argument('checkpoint_path')
def delete_checkpoint(checkpoint_path: str):
    """Delete a checkpoint"""
    try:
        # Load checkpoint manager
        checkpoint_manager = CheckpointManager("data/learning/training")
        
        # Delete checkpoint
        checkpoint_manager.delete_checkpoint(checkpoint_path)
        click.echo(f"Deleted checkpoint: {checkpoint_path}")
        
    except Exception as e:
        logger.error(f"Error deleting checkpoint: {str(e)}")
        raise click.Abort()

if __name__ == '__main__':
    cli() 