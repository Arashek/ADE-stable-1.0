from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import asyncio
from collections import defaultdict
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

@dataclass
class ResourceRequirement:
    """Represents a resource requirement with its specifications."""
    resource_type: str
    amount: float
    priority: int
    duration: timedelta
    constraints: Dict[str, Any]
    dependencies: List[str]

@dataclass
class ResourceAllocation:
    """Represents a resource allocation with its state."""
    id: str
    requirements: ResourceRequirement
    allocated_amount: float
    start_time: datetime
    end_time: datetime
    status: str
    utilization_history: List[Dict[str, Any]]
    cost_history: List[Dict[str, Any]]

@dataclass
class ResourcePool:
    """Represents a pool of resources."""
    resource_type: str
    total_capacity: float
    available_capacity: float
    unit_cost: float
    constraints: Dict[str, Any]
    performance_metrics: Dict[str, List[float]]

class ResourceManagementService:
    """Service for managing and optimizing resource allocation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.allocation_history: List[ResourceAllocation] = []
        self.optimization_tasks: List[asyncio.Task] = []
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # Initialize optimization parameters
        self.optimization_interval = 300  # 5 minutes
        self.history_window = timedelta(days=7)
        self.min_utilization_threshold = 0.6
        self.max_cost_threshold = 1000.0
    
    async def start_management(self):
        """Start the resource management service."""
        try:
            # Start optimization and monitoring tasks
            self.optimization_tasks.extend([
                asyncio.create_task(self._optimize_allocations()),
                asyncio.create_task(self._analyze_utilization()),
                asyncio.create_task(self._predict_demand())
            ])
            
            self.monitoring_tasks.extend([
                asyncio.create_task(self._monitor_resource_usage()),
                asyncio.create_task(self._track_costs())
            ])
            
            self.logger.info("Resource management service started")
            
        except Exception as e:
            self.logger.error(f"Error starting resource management service: {str(e)}")
            raise
    
    async def stop_management(self):
        """Stop the resource management service."""
        try:
            # Cancel all tasks
            for task in self.optimization_tasks + self.monitoring_tasks:
                task.cancel()
            
            await asyncio.gather(
                *self.optimization_tasks,
                *self.monitoring_tasks,
                return_exceptions=True
            )
            
            self.optimization_tasks.clear()
            self.monitoring_tasks.clear()
            
            self.logger.info("Resource management service stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping resource management service: {str(e)}")
            raise
    
    async def register_resource_pool(self, pool: ResourcePool):
        """Register a new resource pool."""
        try:
            self.resource_pools[pool.resource_type] = pool
            self.logger.info(f"Registered resource pool: {pool.resource_type}")
            
        except Exception as e:
            self.logger.error(f"Error registering resource pool: {str(e)}")
            raise
    
    async def request_allocation(self,
                               requirements: List[ResourceRequirement]) -> List[ResourceAllocation]:
        """Request resource allocations based on requirements."""
        try:
            allocations = []
            
            for req in requirements:
                # Check resource availability
                if req.resource_type not in self.resource_pools:
                    raise ValueError(f"Resource type not available: {req.resource_type}")
                
                pool = self.resource_pools[req.resource_type]
                
                # Validate against pool constraints
                if not self._validate_constraints(req, pool):
                    raise ValueError(f"Requirements violate pool constraints: {req.resource_type}")
                
                # Calculate optimal allocation
                allocation = await self._calculate_optimal_allocation(req, pool)
                
                # Create allocation record
                allocation_record = ResourceAllocation(
                    id=f"alloc_{datetime.now().timestamp()}",
                    requirements=req,
                    allocated_amount=allocation["amount"],
                    start_time=datetime.now(),
                    end_time=datetime.now() + req.duration,
                    status="active",
                    utilization_history=[],
                    cost_history=[]
                )
                
                # Update pool capacity
                pool.available_capacity -= allocation["amount"]
                
                # Store allocation
                self.active_allocations[allocation_record.id] = allocation_record
                allocations.append(allocation_record)
                
                self.logger.info(f"Created allocation: {allocation_record.id}")
            
            return allocations
            
        except Exception as e:
            self.logger.error(f"Error requesting allocation: {str(e)}")
            raise
    
    async def release_allocation(self, allocation_id: str):
        """Release a resource allocation."""
        try:
            if allocation_id not in self.active_allocations:
                raise ValueError(f"Allocation not found: {allocation_id}")
            
            allocation = self.active_allocations[allocation_id]
            pool = self.resource_pools[allocation.requirements.resource_type]
            
            # Update pool capacity
            pool.available_capacity += allocation.allocated_amount
            
            # Update allocation status
            allocation.status = "released"
            allocation.end_time = datetime.now()
            
            # Move to history
            self.allocation_history.append(allocation)
            del self.active_allocations[allocation_id]
            
            self.logger.info(f"Released allocation: {allocation_id}")
            
        except Exception as e:
            self.logger.error(f"Error releasing allocation: {str(e)}")
            raise
    
    async def get_resource_utilization(self,
                                     resource_type: str,
                                     start_time: Optional[datetime] = None,
                                     end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get resource utilization statistics."""
        try:
            if resource_type not in self.resource_pools:
                raise ValueError(f"Resource type not found: {resource_type}")
            
            pool = self.resource_pools[resource_type]
            
            # Get relevant allocations
            allocations = [
                a for a in self.active_allocations.values()
                if a.requirements.resource_type == resource_type
            ]
            
            if start_time:
                allocations = [a for a in allocations if a.start_time >= start_time]
            if end_time:
                allocations = [a for a in allocations if a.end_time <= end_time]
            
            # Calculate utilization metrics
            total_capacity = pool.total_capacity
            allocated_capacity = sum(a.allocated_amount for a in allocations)
            utilization = allocated_capacity / total_capacity if total_capacity > 0 else 0
            
            return {
                "resource_type": resource_type,
                "total_capacity": total_capacity,
                "allocated_capacity": allocated_capacity,
                "available_capacity": pool.available_capacity,
                "utilization": utilization,
                "active_allocations": len(allocations)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting resource utilization: {str(e)}")
            raise
    
    async def get_cost_analysis(self,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get cost analysis for resource usage."""
        try:
            # Get relevant allocations
            allocations = self.active_allocations.values()
            if start_time:
                allocations = [a for a in allocations if a.start_time >= start_time]
            if end_time:
                allocations = [a for a in allocations if a.end_time <= end_time]
            
            # Calculate costs by resource type
            costs = defaultdict(float)
            for allocation in allocations:
                pool = self.resource_pools[allocation.requirements.resource_type]
                duration = (allocation.end_time - allocation.start_time).total_seconds() / 3600  # hours
                cost = allocation.allocated_amount * pool.unit_cost * duration
                costs[allocation.requirements.resource_type] += cost
            
            return {
                "total_cost": sum(costs.values()),
                "costs_by_type": dict(costs),
                "allocation_count": len(allocations)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cost analysis: {str(e)}")
            raise
    
    async def _optimize_allocations(self):
        """Optimize resource allocations periodically."""
        while True:
            try:
                # Analyze current allocations
                for allocation_id, allocation in self.active_allocations.items():
                    # Check utilization
                    utilization = await self._calculate_allocation_utilization(allocation)
                    
                    if utilization < self.min_utilization_threshold:
                        # Consider reallocating or releasing
                        await self._optimize_allocation(allocation)
                
                await asyncio.sleep(self.optimization_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error optimizing allocations: {str(e)}")
                await asyncio.sleep(self.optimization_interval)
    
    async def _analyze_utilization(self):
        """Analyze resource utilization patterns."""
        while True:
            try:
                for resource_type, pool in self.resource_pools.items():
                    # Get historical utilization data
                    history = await self._get_utilization_history(resource_type)
                    
                    if history:
                        # Analyze patterns
                        patterns = self._analyze_utilization_patterns(history)
                        
                        # Update pool metrics
                        pool.performance_metrics.update(patterns)
                
                await asyncio.sleep(3600)  # Analyze every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error analyzing utilization: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _predict_demand(self):
        """Predict future resource demand."""
        while True:
            try:
                for resource_type, pool in self.resource_pools.items():
                    # Get historical data
                    history = await self._get_utilization_history(resource_type)
                    
                    if history:
                        # Train prediction model
                        model = self._train_demand_prediction_model(history)
                        
                        # Generate predictions
                        predictions = self._generate_demand_predictions(model)
                        
                        # Update pool metrics
                        pool.performance_metrics["demand_predictions"] = predictions
                
                await asyncio.sleep(3600)  # Predict every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error predicting demand: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _monitor_resource_usage(self):
        """Monitor resource usage in real-time."""
        while True:
            try:
                for allocation_id, allocation in self.active_allocations.items():
                    # Get current usage
                    usage = await self._get_current_usage(allocation)
                    
                    # Update utilization history
                    allocation.utilization_history.append({
                        "timestamp": datetime.now(),
                        "usage": usage
                    })
                    
                    # Check for anomalies
                    if self._detect_usage_anomaly(usage, allocation):
                        await self._handle_usage_anomaly(allocation)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error monitoring resource usage: {str(e)}")
                await asyncio.sleep(60)
    
    async def _track_costs(self):
        """Track resource costs in real-time."""
        while True:
            try:
                for allocation_id, allocation in self.active_allocations.items():
                    # Calculate current cost
                    cost = await self._calculate_current_cost(allocation)
                    
                    # Update cost history
                    allocation.cost_history.append({
                        "timestamp": datetime.now(),
                        "cost": cost
                    })
                    
                    # Check for cost anomalies
                    if self._detect_cost_anomaly(cost, allocation):
                        await self._handle_cost_anomaly(allocation)
                
                await asyncio.sleep(300)  # Track every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error tracking costs: {str(e)}")
                await asyncio.sleep(300)
    
    def _validate_constraints(self,
                            requirements: ResourceRequirement,
                            pool: ResourcePool) -> bool:
        """Validate requirements against pool constraints."""
        try:
            # Check basic constraints
            if requirements.amount > pool.total_capacity:
                return False
            
            # Check custom constraints
            for constraint, value in requirements.constraints.items():
                if constraint in pool.constraints:
                    if not self._validate_constraint_value(
                        value,
                        pool.constraints[constraint]
                    ):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating constraints: {str(e)}")
            return False
    
    async def _calculate_optimal_allocation(self,
                                          requirements: ResourceRequirement,
                                          pool: ResourcePool) -> Dict[str, Any]:
        """Calculate optimal resource allocation."""
        try:
            # Get historical data
            history = await self._get_utilization_history(requirements.resource_type)
            
            # Analyze patterns
            patterns = self._analyze_utilization_patterns(history)
            
            # Calculate optimal amount
            optimal_amount = self._calculate_optimal_amount(
                requirements,
                pool,
                patterns
            )
            
            return {
                "amount": optimal_amount,
                "confidence": self._calculate_allocation_confidence(
                    optimal_amount,
                    patterns
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating optimal allocation: {str(e)}")
            raise
    
    def _analyze_utilization_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze utilization patterns from historical data."""
        try:
            if not history:
                return {}
            
            # Extract utilization values
            values = [h["usage"] for h in history]
            
            # Calculate basic statistics
            stats = {
                "mean": np.mean(values),
                "std": np.std(values),
                "min": np.min(values),
                "max": np.max(values)
            }
            
            # Perform clustering to identify patterns
            if len(values) >= 3:
                scaler = StandardScaler()
                scaled_values = scaler.fit_transform(np.array(values).reshape(-1, 1))
                
                kmeans = KMeans(n_clusters=3, random_state=42)
                clusters = kmeans.fit_predict(scaled_values)
                
                stats["patterns"] = {
                    "cluster_centers": kmeans.cluster_centers_.flatten().tolist(),
                    "cluster_labels": clusters.tolist()
                }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error analyzing utilization patterns: {str(e)}")
            return {}
    
    def _train_demand_prediction_model(self, history: List[Dict[str, Any]]) -> Any:
        """Train a model to predict future demand."""
        # This is a placeholder for actual model training
        # In a real implementation, this would use a time series model
        return None
    
    def _generate_demand_predictions(self, model: Any) -> List[float]:
        """Generate demand predictions using the trained model."""
        # This is a placeholder for actual prediction generation
        # In a real implementation, this would use the trained model
        return []
    
    def _detect_usage_anomaly(self,
                            usage: float,
                            allocation: ResourceAllocation) -> bool:
        """Detect anomalies in resource usage."""
        try:
            if not allocation.utilization_history:
                return False
            
            # Calculate statistics from history
            values = [h["usage"] for h in allocation.utilization_history]
            mean = np.mean(values)
            std = np.std(values)
            
            # Check if current usage is significantly different
            z_score = abs(usage - mean) / std if std > 0 else 0
            return z_score > 3  # More than 3 standard deviations
            
        except Exception as e:
            self.logger.error(f"Error detecting usage anomaly: {str(e)}")
            return False
    
    def _detect_cost_anomaly(self,
                           cost: float,
                           allocation: ResourceAllocation) -> bool:
        """Detect anomalies in resource costs."""
        try:
            if not allocation.cost_history:
                return False
            
            # Calculate statistics from history
            values = [h["cost"] for h in allocation.cost_history]
            mean = np.mean(values)
            std = np.std(values)
            
            # Check if current cost is significantly different
            z_score = abs(cost - mean) / std if std > 0 else 0
            return z_score > 3  # More than 3 standard deviations
            
        except Exception as e:
            self.logger.error(f"Error detecting cost anomaly: {str(e)}")
            return False
    
    async def _handle_usage_anomaly(self, allocation: ResourceAllocation):
        """Handle detected usage anomalies."""
        try:
            # Log the anomaly
            self.logger.warning(
                f"Usage anomaly detected for allocation {allocation.id}"
            )
            
            # Check if reallocation is needed
            if await self._should_reallocate(allocation):
                await self._optimize_allocation(allocation)
            
        except Exception as e:
            self.logger.error(f"Error handling usage anomaly: {str(e)}")
    
    async def _handle_cost_anomaly(self, allocation: ResourceAllocation):
        """Handle detected cost anomalies."""
        try:
            # Log the anomaly
            self.logger.warning(
                f"Cost anomaly detected for allocation {allocation.id}"
            )
            
            # Check if cost optimization is needed
            if await self._should_optimize_cost(allocation):
                await self._optimize_allocation(allocation)
            
        except Exception as e:
            self.logger.error(f"Error handling cost anomaly: {str(e)}")
    
    async def _should_reallocate(self, allocation: ResourceAllocation) -> bool:
        """Determine if reallocation is needed."""
        try:
            # Check utilization trend
            if len(allocation.utilization_history) < 2:
                return False
            
            recent_usage = [h["usage"] for h in allocation.utilization_history[-5:]]
            trend = np.polyfit(range(len(recent_usage)), recent_usage, 1)[0]
            
            # Reallocate if trend is significantly negative
            return trend < -0.1
            
        except Exception as e:
            self.logger.error(f"Error checking reallocation need: {str(e)}")
            return False
    
    async def _should_optimize_cost(self, allocation: ResourceAllocation) -> bool:
        """Determine if cost optimization is needed."""
        try:
            # Check cost trend
            if len(allocation.cost_history) < 2:
                return False
            
            recent_costs = [h["cost"] for h in allocation.cost_history[-5:]]
            trend = np.polyfit(range(len(recent_costs)), recent_costs, 1)[0]
            
            # Optimize if trend is significantly positive
            return trend > 0.1
            
        except Exception as e:
            self.logger.error(f"Error checking cost optimization need: {str(e)}")
            return False
    
    async def _optimize_allocation(self, allocation: ResourceAllocation):
        """Optimize a resource allocation."""
        try:
            # Calculate new optimal allocation
            pool = self.resource_pools[allocation.requirements.resource_type]
            new_allocation = await self._calculate_optimal_allocation(
                allocation.requirements,
                pool
            )
            
            # Update allocation if significantly different
            if abs(new_allocation["amount"] - allocation.allocated_amount) > 0.1:
                # Release current allocation
                await self.release_allocation(allocation.id)
                
                # Create new allocation
                new_requirements = ResourceRequirement(
                    resource_type=allocation.requirements.resource_type,
                    amount=new_allocation["amount"],
                    priority=allocation.requirements.priority,
                    duration=allocation.requirements.duration,
                    constraints=allocation.requirements.constraints,
                    dependencies=allocation.requirements.dependencies
                )
                
                await self.request_allocation([new_requirements])
            
        except Exception as e:
            self.logger.error(f"Error optimizing allocation: {str(e)}")
    
    def _validate_constraint_value(self, value: Any, constraint: Any) -> bool:
        """Validate a constraint value against its definition."""
        try:
            if isinstance(constraint, (int, float)):
                return value <= constraint
            elif isinstance(constraint, dict):
                if "min" in constraint and value < constraint["min"]:
                    return False
                if "max" in constraint and value > constraint["max"]:
                    return False
                return True
            else:
                return True
                
        except Exception as e:
            self.logger.error(f"Error validating constraint value: {str(e)}")
            return False
    
    def _calculate_optimal_amount(self,
                                requirements: ResourceRequirement,
                                pool: ResourcePool,
                                patterns: Dict[str, Any]) -> float:
        """Calculate optimal resource amount."""
        try:
            # Start with requested amount
            optimal = requirements.amount
            
            # Adjust based on patterns
            if "patterns" in patterns:
                cluster_centers = patterns["patterns"]["cluster_centers"]
                optimal = max(optimal, np.mean(cluster_centers))
            
            # Ensure within constraints
            optimal = min(optimal, pool.total_capacity)
            optimal = max(optimal, requirements.constraints.get("min", 0))
            
            return optimal
            
        except Exception as e:
            self.logger.error(f"Error calculating optimal amount: {str(e)}")
            return requirements.amount
    
    def _calculate_allocation_confidence(self,
                                      amount: float,
                                      patterns: Dict[str, Any]) -> float:
        """Calculate confidence in allocation decision."""
        try:
            if not patterns:
                return 0.5
            
            # Calculate confidence based on pattern consistency
            if "patterns" in patterns:
                cluster_centers = patterns["patterns"]["cluster_centers"]
                std = np.std(cluster_centers)
                mean = np.mean(cluster_centers)
                
                # Higher confidence if amount is close to mean and std is low
                confidence = 1 - (abs(amount - mean) / (std + 1e-6))
                return max(0, min(1, confidence))
            
            return 0.5
            
        except Exception as e:
            self.logger.error(f"Error calculating allocation confidence: {str(e)}")
            return 0.5 