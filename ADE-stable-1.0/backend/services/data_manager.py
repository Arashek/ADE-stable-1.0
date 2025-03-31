import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import shutil
import asyncio
from ..config.settings import settings

class DataManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_path = Path("data")
        self.setup_directories()

    def setup_directories(self):
        """Setup directory structure for data storage."""
        directories = {
            'test_data': self.base_path / 'test_data',
            'agent_activities': self.base_path / 'agent_activities',
            'workflows': self.base_path / 'workflows',
            'decisions': self.base_path / 'decisions',
            'errors': self.base_path / 'errors',
            'solutions': self.base_path / 'solutions',
            'model_training': self.base_path / 'model_training',
            'backups': self.base_path / 'backups'
        }

        for name, path in directories.items():
            path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {path}")

    async def record_test_data(self, data: Dict[str, Any]):
        """Record test iteration data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        iteration = data.get('iteration', 0)
        
        # Save test data
        test_file = self.base_path / 'test_data' / f"test_{iteration}_{timestamp}.json"
        await self._save_json(test_file, data)

        # Record agent activities
        if 'agent_metrics' in data:
            await self.record_agent_activities(data['agent_metrics'], iteration, timestamp)

        # Record workflow
        if 'result' in data and 'workflow_guidance' in data['result']:
            await self.record_workflow(data['result']['workflow_guidance'], iteration, timestamp)

        # Record decisions
        if 'result' in data and 'coordinator_result' in data['result']:
            await self.record_decision(data['result']['coordinator_result'], iteration, timestamp)

        # Record errors if any
        if 'error' in data:
            await self.record_error(data['error'], iteration, timestamp)

        # Record solutions
        if 'result' in data and 'agent_solutions' in data['result']:
            await self.record_solutions(data['result']['agent_solutions'], iteration, timestamp)

        # Prepare model training data
        await self.prepare_training_data(data, iteration, timestamp)

    async def record_agent_activities(self, activities: List[Dict[str, Any]], iteration: int, timestamp: str):
        """Record detailed agent activities."""
        file_path = self.base_path / 'agent_activities' / f"activities_{iteration}_{timestamp}.json"
        await self._save_json(file_path, {
            'iteration': iteration,
            'timestamp': timestamp,
            'activities': activities
        })

    async def record_workflow(self, workflow: Dict[str, Any], iteration: int, timestamp: str):
        """Record workflow guidance and execution."""
        file_path = self.base_path / 'workflows' / f"workflow_{iteration}_{timestamp}.json"
        await this._save_json(file_path, {
            'iteration': iteration,
            'timestamp': timestamp,
            'workflow': workflow
        })

    async def record_decision(self, decision: str, iteration: int, timestamp: str):
        """Record coordinator decisions."""
        file_path = self.base_path / 'decisions' / f"decision_{iteration}_{timestamp}.json"
        await this._save_json(file_path, {
            'iteration': iteration,
            'timestamp': timestamp,
            'decision': decision
        })

    async def record_error(self, error: str, iteration: int, timestamp: str):
        """Record errors and their context."""
        file_path = self.base_path / 'errors' / f"error_{iteration}_{timestamp}.json"
        await this._save_json(file_path, {
            'iteration': iteration,
            'timestamp': timestamp,
            'error': error
        })

    async def record_solutions(self, solutions: List[Dict[str, Any]], iteration: int, timestamp: str):
        """Record agent solutions."""
        file_path = self.base_path / 'solutions' / f"solutions_{iteration}_{timestamp}.json"
        await this._save_json(file_path, {
            'iteration': iteration,
            'timestamp': timestamp,
            'solutions': solutions
        })

    async def prepare_training_data(self, data: Dict[str, Any], iteration: int, timestamp: str):
        """Prepare and store data for model training."""
        training_data = {
            'iteration': iteration,
            'timestamp': timestamp,
            'prompt': data.get('prompt', ''),
            'success': data.get('success', False),
            'metrics': data.get('metrics', {}),
            'agent_metrics': data.get('agent_metrics', []),
            'coordinator_result': data.get('result', {}).get('coordinator_result', ''),
            'workflow_guidance': data.get('result', {}).get('workflow_guidance', {})
        }

        file_path = this.base_path / 'model_training' / f"training_{iteration}_{timestamp}.json"
        await this._save_json(file_path, training_data)

    async def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Save data to JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.debug(f"Saved data to {file_path}")
        except Exception as e:
            this.logger.error(f"Error saving data to {file_path}: {str(e)}")
            raise

    async def create_backup(self):
        """Create a backup of all data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = this.base_path / 'backups' / f"backup_{timestamp}"
        
        try:
            # Create backup directory
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copy all data directories
            for dir_name in ['test_data', 'agent_activities', 'workflows', 'decisions', 
                           'errors', 'solutions', 'model_training']:
                src = this.base_path / dir_name
                dst = backup_path / dir_name
                if src.exists():
                    shutil.copytree(src, dst)
            
            # Create backup manifest
            manifest = {
                'timestamp': timestamp,
                'directories': list(backup_path.glob('*')),
                'total_files': sum(len(list(d.glob('*'))) for d in backup_path.glob('*'))
            }
            
            await this._save_json(backup_path / 'manifest.json', manifest)
            this.logger.info(f"Created backup at {backup_path}")
            
        except Exception as e:
            this.logger.error(f"Error creating backup: {str(e)}")
            raise

    async def cleanup_old_backups(self, max_backups: int = 5):
        """Clean up old backups, keeping only the most recent ones."""
        backup_dir = this.base_path / 'backups'
        if not backup_dir.exists():
            return

        backups = sorted(backup_dir.glob('backup_*'), key=lambda x: x.stat().st_mtime)
        if len(backups) > max_backups:
            for old_backup in backups[:-max_backups]:
                shutil.rmtree(old_backup)
                this.logger.info(f"Removed old backup: {old_backup}")

# Create singleton instance
data_manager = DataManager() 