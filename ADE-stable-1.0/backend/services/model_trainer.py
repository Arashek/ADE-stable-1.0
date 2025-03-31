import numpy as np
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from prometheus_client import Counter, Gauge
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Metrics
TRAINING_ITERATIONS = Counter('training_iterations_total', 'Total number of training iterations')
MODEL_PERFORMANCE = Gauge('model_performance', 'Model performance metrics', ['model', 'metric'])

class TestDataset(Dataset):
    def __init__(self, test_history: List[Dict[str, Any]]):
        self.data = test_history
        self.tokenizer = None  # Initialize with your preferred tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        # Convert text to tensor (implement based on your tokenizer)
        prompt_tensor = torch.tensor([0])  # Placeholder
        return {
            'prompt': prompt_tensor,
            'success': torch.tensor(1 if item['success'] else 0),
            'metrics': torch.tensor([
                item['metrics']['total_latency'],
                item['metrics']['iteration']
            ])
        }

class AgentPolicy(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 256):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)

class ModelTrainer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.policies: Dict[str, AgentPolicy] = {}
        self.optimizers: Dict[str, optim.Optimizer] = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.learning_rate = 0.001
        self.batch_size = 32
        self.max_epochs = 10

    def _initialize_policy(self, agent_name: str, input_size: int):
        """Initialize policy network for an agent if not exists."""
        if agent_name not in self.policies:
            self.policies[agent_name] = AgentPolicy(input_size).to(self.device)
            self.optimizers[agent_name] = optim.Adam(
                self.policies[agent_name].parameters(),
                lr=self.learning_rate
            )

    async def train_on_test_data(self, test_history: List[Dict[str, Any]]):
        """Train models on test history data."""
        try:
            # Group data by agent
            agent_data: Dict[str, List[Dict[str, Any]]] = {}
            for test in test_history:
                for agent_metric in test['agent_metrics']:
                    agent_name = agent_metric['name']
                    if agent_name not in agent_data:
                        agent_data[agent_name] = []
                    agent_data[agent_name].append({
                        'prompt': test['prompt'],
                        'success': test['success'],
                        'metrics': agent_metric
                    })

            # Train each agent's policy
            for agent_name, data in agent_data.items():
                await self._train_agent_policy(agent_name, data)

            TRAINING_ITERATIONS.inc()
            self.logger.info("Training completed successfully")

        except Exception as e:
            self.logger.error(f"Error during training: {str(e)}")
            raise

    async def _train_agent_policy(self, agent_name: str, data: List[Dict[str, Any]]):
        """Train policy network for a specific agent."""
        # Prepare dataset
        dataset = TestDataset(data)
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=True
        )

        # Initialize policy if needed
        self._initialize_policy(agent_name, input_size=512)  # Adjust input size as needed

        policy = self.policies[agent_name]
        optimizer = self.optimizers[agent_name]
        criterion = nn.BCELoss()

        # Training loop
        for epoch in range(self.max_epochs):
            total_loss = 0
            correct_predictions = 0
            total_predictions = 0

            for batch in dataloader:
                optimizer.zero_grad()

                # Forward pass
                outputs = policy(batch['prompt'].to(self.device))
                targets = batch['success'].to(self.device)

                # Calculate loss
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

                # Calculate accuracy
                predictions = (outputs > 0.5).float()
                correct_predictions += (predictions == targets).sum().item()
                total_predictions += len(targets)

            # Update metrics
            accuracy = correct_predictions / total_predictions
            MODEL_PERFORMANCE.labels(
                model=agent_name,
                metric='accuracy'
            ).set(accuracy)
            MODEL_PERFORMANCE.labels(
                model=agent_name,
                metric='loss'
            ).set(total_loss / len(dataloader))

            self.logger.info(
                f"Agent {agent_name} - Epoch {epoch + 1}/{self.max_epochs} - "
                f"Loss: {total_loss/len(dataloader):.4f} - Accuracy: {accuracy:.4f}"
            )

    async def get_agent_policy(self, agent_name: str) -> Optional[AgentPolicy]:
        """Get trained policy for an agent."""
        return self.policies.get(agent_name)

    async def save_policies(self, path: str):
        """Save trained policies to disk."""
        try:
            for agent_name, policy in self.policies.items():
                torch.save(
                    policy.state_dict(),
                    f"{path}/{agent_name}_policy.pt"
                )
            self.logger.info(f"Policies saved to {path}")
        except Exception as e:
            self.logger.error(f"Error saving policies: {str(e)}")
            raise

    async def load_policies(self, path: str):
        """Load trained policies from disk."""
        try:
            for agent_name in self.policies:
                policy_path = f"{path}/{agent_name}_policy.pt"
                self.policies[agent_name].load_state_dict(
                    torch.load(policy_path)
                )
            self.logger.info(f"Policies loaded from {path}")
        except Exception as e:
            self.logger.error(f"Error loading policies: {str(e)}")
            raise

# Create singleton instance
model_trainer = ModelTrainer() 