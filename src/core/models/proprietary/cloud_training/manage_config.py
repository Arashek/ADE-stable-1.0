import os
import logging
import json
import boto3
from datetime import datetime
from pathlib import Path
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ConfigManager:
    def __init__(self):
        """Initialize configuration manager"""
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.s3 = boto3.client('s3')
        self.bucket = os.getenv('S3_BUCKET', 'ade-training-data')
        self.config_prefix = 'configs/'
        
    def save_config(self, name: str, config: dict, description: str = None):
        """Save a training configuration"""
        try:
            # Add metadata
            config_data = {
                'name': name,
                'description': description,
                'created_at': datetime.utcnow().isoformat(),
                'config': config
            }
            
            # Save configuration
            key = f"{self.config_prefix}{name}/config.json"
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(config_data, indent=2),
                Metadata={
                    'name': name,
                    'created_at': config_data['created_at']
                }
            )
            
            logger.info(f"Saved configuration: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            return False
            
    def load_config(self, name: str):
        """Load a training configuration"""
        try:
            key = f"{self.config_prefix}{name}/config.json"
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            logger.error(f"Failed to load configuration: {str(e)}")
            return None
            
    def list_configs(self):
        """List all training configurations"""
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.config_prefix,
                Delimiter='/'
            )
            
            configs = []
            for prefix in response.get('CommonPrefixes', []):
                name = prefix['Prefix'].split('/')[-2]
                config = self.load_config(name)
                if config:
                    configs.append(config)
                    
            return sorted(configs, key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list configurations: {str(e)}")
            return []
            
    def delete_config(self, name: str):
        """Delete a training configuration"""
        try:
            key = f"{self.config_prefix}{name}/config.json"
            self.s3.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted configuration: {name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete configuration: {str(e)}")
            return False
            
    def update_config(self, name: str, config: dict, description: str = None):
        """Update an existing training configuration"""
        try:
            existing = self.load_config(name)
            if not existing:
                return False
                
            # Update configuration
            existing['config'] = config
            if description:
                existing['description'] = description
            existing['updated_at'] = datetime.utcnow().isoformat()
            
            key = f"{self.config_prefix}{name}/config.json"
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(existing, indent=2),
                Metadata={
                    'name': name,
                    'updated_at': existing['updated_at']
                }
            )
            
            logger.info(f"Updated configuration: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            return False
            
    def get_default_config(self):
        """Get the default training configuration"""
        return {
            'training': {
                'instance_type': 'ml.p3.2xlarge',
                'instance_count': 1,
                'volume_size': 100,
                'max_runtime': 86400,  # 24 hours
                'checkpoint_interval': 3600,  # 1 hour
                'metrics_interval': 60  # 1 minute
            },
            'model': {
                'base_model': 'deepseek-ai/deepseek-coder-1.3b-instruct',
                'num_examples': 1000,
                'synthetic_ratio': 0.3,
                'batch_size': 8,
                'learning_rate': 2e-5,
                'num_epochs': 3
            },
            'monitoring': {
                'metrics_interval': 60,  # 1 minute
                'cost_alert_threshold': 100  # USD
            },
            'sync': {
                'sync_interval': 300,  # 5 minutes
                'checkpoint_interval': 3600  # 1 hour
            }
        }

def main():
    """Main function to manage training configurations"""
    try:
        manager = ConfigManager()
        
        # List all configurations
        print("\nTraining Configurations:")
        print("-" * 50)
        configs = manager.list_configs()
        for config in configs:
            print(f"Name: {config['name']}")
            if config.get('description'):
                print(f"Description: {config['description']}")
            print(f"Created: {config['created_at']}")
            if config.get('updated_at'):
                print(f"Updated: {config['updated_at']}")
            print("-" * 30)
            
        # Get user input for action
        print("\nAvailable actions:")
        print("1. Create new configuration")
        print("2. Load configuration")
        print("3. Update configuration")
        print("4. Delete configuration")
        print("5. Get default configuration")
        print("6. Exit")
        
        while True:
            action = input("\nEnter action number (1-6): ")
            
            if action == '6':
                break
                
            if action == '1':
                name = input("Enter configuration name: ")
                description = input("Enter description (optional): ")
                
                # Get configuration from user
                config = {}
                print("\nEnter configuration values (press Enter to skip):")
                print("Training Settings:")
                config['training'] = {
                    'instance_type': input("Instance type (default: ml.p3.2xlarge): ") or 'ml.p3.2xlarge',
                    'instance_count': int(input("Instance count (default: 1): ") or 1),
                    'volume_size': int(input("Volume size in GB (default: 100): ") or 100),
                    'max_runtime': int(input("Max runtime in seconds (default: 86400): ") or 86400),
                    'checkpoint_interval': int(input("Checkpoint interval in seconds (default: 3600): ") or 3600),
                    'metrics_interval': int(input("Metrics interval in seconds (default: 60): ") or 60)
                }
                
                print("\nModel Settings:")
                config['model'] = {
                    'base_model': input("Base model (default: deepseek-ai/deepseek-coder-1.3b-instruct): ") or 'deepseek-ai/deepseek-coder-1.3b-instruct',
                    'num_examples': int(input("Number of examples (default: 1000): ") or 1000),
                    'synthetic_ratio': float(input("Synthetic ratio (default: 0.3): ") or 0.3),
                    'batch_size': int(input("Batch size (default: 8): ") or 8),
                    'learning_rate': float(input("Learning rate (default: 2e-5): ") or 2e-5),
                    'num_epochs': int(input("Number of epochs (default: 3): ") or 3)
                }
                
                print("\nMonitoring Settings:")
                config['monitoring'] = {
                    'metrics_interval': int(input("Metrics interval in seconds (default: 60): ") or 60),
                    'cost_alert_threshold': float(input("Cost alert threshold in USD (default: 100): ") or 100)
                }
                
                print("\nSync Settings:")
                config['sync'] = {
                    'sync_interval': int(input("Sync interval in seconds (default: 300): ") or 300),
                    'checkpoint_interval': int(input("Checkpoint interval in seconds (default: 3600): ") or 3600)
                }
                
                if manager.save_config(name, config, description):
                    print(f"Successfully created configuration: {name}")
                    
            elif action == '2':
                name = input("Enter configuration name: ")
                config = manager.load_config(name)
                if config:
                    print("\nConfiguration Details:")
                    print(f"Name: {config['name']}")
                    if config.get('description'):
                        print(f"Description: {config['description']}")
                    print(f"Created: {config['created_at']}")
                    if config.get('updated_at'):
                        print(f"Updated: {config['updated_at']}")
                    print("\nConfiguration:")
                    print(json.dumps(config['config'], indent=2))
                else:
                    print(f"Configuration {name} not found")
                    
            elif action == '3':
                name = input("Enter configuration name: ")
                description = input("Enter new description (optional): ")
                
                # Get updated configuration from user
                config = {}
                print("\nEnter updated configuration values (press Enter to keep current):")
                current = manager.load_config(name)
                if not current:
                    print(f"Configuration {name} not found")
                    continue
                    
                current_config = current['config']
                
                print("\nTraining Settings:")
                config['training'] = {
                    'instance_type': input(f"Instance type (current: {current_config['training']['instance_type']}): ") or current_config['training']['instance_type'],
                    'instance_count': int(input(f"Instance count (current: {current_config['training']['instance_count']}): ") or current_config['training']['instance_count']),
                    'volume_size': int(input(f"Volume size in GB (current: {current_config['training']['volume_size']}): ") or current_config['training']['volume_size']),
                    'max_runtime': int(input(f"Max runtime in seconds (current: {current_config['training']['max_runtime']}): ") or current_config['training']['max_runtime']),
                    'checkpoint_interval': int(input(f"Checkpoint interval in seconds (current: {current_config['training']['checkpoint_interval']}): ") or current_config['training']['checkpoint_interval']),
                    'metrics_interval': int(input(f"Metrics interval in seconds (current: {current_config['training']['metrics_interval']}): ") or current_config['training']['metrics_interval'])
                }
                
                print("\nModel Settings:")
                config['model'] = {
                    'base_model': input(f"Base model (current: {current_config['model']['base_model']}): ") or current_config['model']['base_model'],
                    'num_examples': int(input(f"Number of examples (current: {current_config['model']['num_examples']}): ") or current_config['model']['num_examples']),
                    'synthetic_ratio': float(input(f"Synthetic ratio (current: {current_config['model']['synthetic_ratio']}): ") or current_config['model']['synthetic_ratio']),
                    'batch_size': int(input(f"Batch size (current: {current_config['model']['batch_size']}): ") or current_config['model']['batch_size']),
                    'learning_rate': float(input(f"Learning rate (current: {current_config['model']['learning_rate']}): ") or current_config['model']['learning_rate']),
                    'num_epochs': int(input(f"Number of epochs (current: {current_config['model']['num_epochs']}): ") or current_config['model']['num_epochs'])
                }
                
                print("\nMonitoring Settings:")
                config['monitoring'] = {
                    'metrics_interval': int(input(f"Metrics interval in seconds (current: {current_config['monitoring']['metrics_interval']}): ") or current_config['monitoring']['metrics_interval']),
                    'cost_alert_threshold': float(input(f"Cost alert threshold in USD (current: {current_config['monitoring']['cost_alert_threshold']}): ") or current_config['monitoring']['cost_alert_threshold'])
                }
                
                print("\nSync Settings:")
                config['sync'] = {
                    'sync_interval': int(input(f"Sync interval in seconds (current: {current_config['sync']['sync_interval']}): ") or current_config['sync']['sync_interval']),
                    'checkpoint_interval': int(input(f"Checkpoint interval in seconds (current: {current_config['sync']['checkpoint_interval']}): ") or current_config['sync']['checkpoint_interval'])
                }
                
                if manager.update_config(name, config, description):
                    print(f"Successfully updated configuration: {name}")
                    
            elif action == '4':
                name = input("Enter configuration name: ")
                if manager.delete_config(name):
                    print(f"Successfully deleted configuration: {name}")
                    
            elif action == '5':
                config = manager.get_default_config()
                print("\nDefault Configuration:")
                print(json.dumps(config, indent=2))
                
    except Exception as e:
        logger.error(f"Failed to manage configurations: {str(e)}")
        print("\nFailed to manage configurations. Please check the logs above.")

if __name__ == "__main__":
    main() 