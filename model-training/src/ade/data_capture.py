import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class ADEDataCapture:
    """Captures and processes learning data from ADE."""
    
    def __init__(self, config_path: str = "config/ade_integration.json"):
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config['ade_api_key']}"
        })
        self._setup_directories()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load ADE integration configuration."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"ADE integration config not found at {config_path}. Using defaults.")
            return {
                "ade_api_url": "http://localhost:8000",
                "ade_api_key": "",
                "data_capture_enabled": True,
                "learning_data_dir": "data/learning",
                "model_data_dir": "data/models"
            }
    
    def _setup_directories(self):
        """Create necessary directories for data storage."""
        for dir_path in [
            self.config['learning_data_dir'],
            self.config['model_data_dir'],
            os.path.join(self.config['learning_data_dir'], 'prompts'),
            os.path.join(self.config['learning_data_dir'], 'responses'),
            os.path.join(self.config['learning_data_dir'], 'metrics')
        ]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def capture_prompt(self, prompt_id: str) -> Dict:
        """Capture a prompt and its details from ADE."""
        try:
            response = self.session.get(
                f"{self.config['ade_api_url']}/api/prompts/{prompt_id}"
            )
            response.raise_for_status()
            prompt_data = response.json()
            
            # Save prompt data
            prompt_file = Path(self.config['learning_data_dir']) / 'prompts' / f"{prompt_id}.json"
            with open(prompt_file, 'w') as f:
                json.dump(prompt_data, f, indent=2)
            
            return prompt_data
        except RequestException as e:
            logger.error(f"Error capturing prompt {prompt_id}: {e}")
            return {}
    
    def capture_response(self, response_id: str) -> Dict:
        """Capture a response and its details from ADE."""
        try:
            response = self.session.get(
                f"{self.config['ade_api_url']}/api/responses/{response_id}"
            )
            response.raise_for_status()
            response_data = response.json()
            
            # Save response data
            response_file = Path(self.config['learning_data_dir']) / 'responses' / f"{response_id}.json"
            with open(response_file, 'w') as f:
                json.dump(response_data, f, indent=2)
            
            return response_data
        except RequestException as e:
            logger.error(f"Error capturing response {response_id}: {e}")
            return {}
    
    def capture_metrics(self, session_id: str) -> Dict:
        """Capture training metrics from ADE."""
        try:
            response = self.session.get(
                f"{self.config['ade_api_url']}/api/sessions/{session_id}/metrics"
            )
            response.raise_for_status()
            metrics_data = response.json()
            
            # Save metrics data
            metrics_file = Path(self.config['learning_data_dir']) / 'metrics' / f"{session_id}.json"
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            return metrics_data
        except RequestException as e:
            logger.error(f"Error capturing metrics for session {session_id}: {e}")
            return {}
    
    def process_learning_data(self, session_id: str) -> pd.DataFrame:
        """Process captured learning data into a training dataset."""
        try:
            # Load all prompts and responses for the session
            prompts_dir = Path(self.config['learning_data_dir']) / 'prompts'
            responses_dir = Path(self.config['learning_data_dir']) / 'responses'
            
            data = []
            for prompt_file in prompts_dir.glob("*.json"):
                with open(prompt_file, 'r') as f:
                    prompt_data = json.load(f)
                    if prompt_data.get('session_id') == session_id:
                        response_file = responses_dir / f"{prompt_data['response_id']}.json"
                        if response_file.exists():
                            with open(response_file, 'r') as f:
                                response_data = json.load(f)
                                data.append({
                                    'prompt': prompt_data['content'],
                                    'response': response_data['content'],
                                    'timestamp': prompt_data['timestamp'],
                                    'session_id': session_id
                                })
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Save processed dataset
            dataset_file = Path(self.config['learning_data_dir']) / f"dataset_{session_id}.csv"
            df.to_csv(dataset_file, index=False)
            
            return df
        except Exception as e:
            logger.error(f"Error processing learning data for session {session_id}: {e}")
            return pd.DataFrame()
    
    def prepare_training_data(self, session_ids: List[str]) -> pd.DataFrame:
        """Prepare training data from multiple sessions."""
        datasets = []
        for session_id in session_ids:
            df = self.process_learning_data(session_id)
            if not df.empty:
                datasets.append(df)
        
        if datasets:
            combined_df = pd.concat(datasets, ignore_index=True)
            combined_df.to_csv(
                Path(self.config['learning_data_dir']) / "combined_dataset.csv",
                index=False
            )
            return combined_df
        return pd.DataFrame()
    
    def monitor_ade_activity(self):
        """Monitor ADE for new activity and capture data."""
        while True:
            try:
                # Get active sessions
                response = self.session.get(
                    f"{self.config['ade_api_url']}/api/sessions/active"
                )
                response.raise_for_status()
                active_sessions = response.json()
                
                for session in active_sessions:
                    session_id = session['id']
                    
                    # Capture metrics
                    self.capture_metrics(session_id)
                    
                    # Process learning data
                    self.process_learning_data(session_id)
                
                # Wait before next check
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error monitoring ADE activity: {e}")
                time.sleep(60)  # Wait before retrying

def main():
    """Main function to run the ADE data capture service."""
    logging.basicConfig(level=logging.INFO)
    data_capture = ADEDataCapture()
    
    try:
        # Start monitoring ADE activity
        data_capture.monitor_ade_activity()
    except KeyboardInterrupt:
        logger.info("Stopping ADE data capture service...")
    except Exception as e:
        logger.error(f"Error in ADE data capture service: {e}")

if __name__ == "__main__":
    main() 