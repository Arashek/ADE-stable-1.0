from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, XGBRegressor
from prophet import Prophet
from scipy import stats
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

@dataclass
class OptimizationStrategy:
    """Base class for resource optimization strategies."""
    resource_type: str
    parameters: Dict[str, Any]
    constraints: Dict[str, Any]
    performance_metrics: Dict[str, List[float]]

class ComputeOptimizationStrategy(OptimizationStrategy):
    """Strategy for optimizing compute resources."""
    
    def optimize_allocation(self,
                          current_usage: float,
                          historical_data: List[Dict[str, Any]],
                          constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize compute resource allocation."""
        try:
            # Extract usage patterns
            usage_patterns = self._analyze_usage_patterns(historical_data)
            
            # Predict future demand
            demand_forecast = self._predict_demand(historical_data)
            
            # Calculate optimal allocation
            optimal_allocation = self._calculate_optimal_compute(
                current_usage,
                usage_patterns,
                demand_forecast,
                constraints
            )
            
            return {
                "amount": optimal_allocation["amount"],
                "confidence": optimal_allocation["confidence"],
                "reasoning": optimal_allocation["reasoning"]
            }
            
        except Exception as e:
            logging.error(f"Error optimizing compute allocation: {str(e)}")
            return {"amount": current_usage, "confidence": 0.5, "reasoning": "Error in optimization"}
    
    def _analyze_usage_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze compute usage patterns."""
        try:
            # Convert to time series
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate daily patterns
            daily_patterns = df.groupby(df['timestamp'].dt.hour)['usage'].mean()
            
            # Calculate weekly patterns
            weekly_patterns = df.groupby(df['timestamp'].dt.dayofweek)['usage'].mean()
            
            # Calculate seasonality
            seasonal_patterns = self._calculate_seasonality(df)
            
            return {
                "daily": daily_patterns.to_dict(),
                "weekly": weekly_patterns.to_dict(),
                "seasonal": seasonal_patterns
            }
            
        except Exception as e:
            logging.error(f"Error analyzing usage patterns: {str(e)}")
            return {}
    
    def _predict_demand(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future compute demand using Prophet."""
        try:
            # Prepare data for Prophet
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.rename(columns={'timestamp': 'ds', 'usage': 'y'})
            
            # Fit Prophet model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True,
                changepoint_prior_scale=0.05
            )
            model.fit(df)
            
            # Generate future dates
            future = model.make_future_dataframe(periods=24, freq='H')
            
            # Make predictions
            forecast = model.predict(future)
            
            return {
                "forecast": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
                "trend": forecast['trend'].tolist(),
                "seasonality": forecast['yearly'].tolist()
            }
            
        except Exception as e:
            logging.error(f"Error predicting demand: {str(e)}")
            return {}
    
    def _calculate_seasonality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate seasonal patterns in usage."""
        try:
            # Calculate monthly seasonality
            monthly = df.groupby(df['timestamp'].dt.month)['usage'].mean()
            
            # Calculate quarterly seasonality
            quarterly = df.groupby(df['timestamp'].dt.quarter)['usage'].mean()
            
            # Calculate yearly seasonality
            yearly = df.groupby(df['timestamp'].dt.dayofyear)['usage'].mean()
            
            return {
                "monthly": monthly.to_dict(),
                "quarterly": quarterly.to_dict(),
                "yearly": yearly.to_dict()
            }
            
        except Exception as e:
            logging.error(f"Error calculating seasonality: {str(e)}")
            return {}
    
    def _calculate_optimal_compute(self,
                                 current_usage: float,
                                 patterns: Dict[str, Any],
                                 forecast: Dict[str, Any],
                                 constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal compute allocation."""
        try:
            # Get current hour and day patterns
            current_hour = datetime.now().hour
            current_day = datetime.now().dayofweek
            
            # Get pattern-based adjustment
            hour_adjustment = patterns.get("daily", {}).get(current_hour, 1.0)
            day_adjustment = patterns.get("weekly", {}).get(current_day, 1.0)
            
            # Get forecast-based adjustment
            forecast_values = forecast.get("forecast", [])
            if forecast_values:
                next_hour_forecast = forecast_values[-1]["yhat"]
                forecast_adjustment = next_hour_forecast / current_usage if current_usage > 0 else 1.0
            else:
                forecast_adjustment = 1.0
            
            # Calculate optimal amount
            optimal = current_usage * hour_adjustment * day_adjustment * forecast_adjustment
            
            # Apply constraints
            optimal = min(optimal, constraints.get("max", float('inf')))
            optimal = max(optimal, constraints.get("min", 0))
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                patterns,
                forecast,
                optimal,
                current_usage
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                optimal,
                current_usage,
                patterns,
                forecast
            )
            
            return {
                "amount": optimal,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logging.error(f"Error calculating optimal compute: {str(e)}")
            return {
                "amount": current_usage,
                "confidence": 0.5,
                "reasoning": "Error in calculation"
            }
    
    def _calculate_confidence(self,
                            patterns: Dict[str, Any],
                            forecast: Dict[str, Any],
                            optimal: float,
                            current: float) -> float:
        """Calculate confidence in the optimization decision."""
        try:
            # Pattern consistency
            pattern_std = np.std(list(patterns.get("daily", {}).values()))
            pattern_confidence = 1 - (pattern_std / np.mean(list(patterns.get("daily", {}).values())))
            
            # Forecast confidence
            if forecast.get("forecast"):
                forecast_std = np.std([f["yhat_upper"] - f["yhat_lower"] for f in forecast["forecast"]])
                forecast_confidence = 1 - (forecast_std / np.mean([f["yhat"] for f in forecast["forecast"]]))
            else:
                forecast_confidence = 0.5
            
            # Change magnitude confidence
            change_magnitude = abs(optimal - current) / current if current > 0 else 0
            magnitude_confidence = 1 - min(change_magnitude, 1)
            
            # Combine confidences
            confidence = (pattern_confidence + forecast_confidence + magnitude_confidence) / 3
            return max(0, min(1, confidence))
            
        except Exception as e:
            logging.error(f"Error calculating confidence: {str(e)}")
            return 0.5
    
    def _generate_reasoning(self,
                          optimal: float,
                          current: float,
                          patterns: Dict[str, Any],
                          forecast: Dict[str, Any]) -> str:
        """Generate reasoning for the optimization decision."""
        try:
            reasons = []
            
            # Pattern-based reasoning
            if patterns.get("daily"):
                current_hour = datetime.now().hour
                hour_pattern = patterns["daily"].get(current_hour, 1.0)
                if hour_pattern > 1.1:
                    reasons.append(f"High usage pattern detected for current hour ({hour_pattern:.2f}x)")
                elif hour_pattern < 0.9:
                    reasons.append(f"Low usage pattern detected for current hour ({hour_pattern:.2f}x)")
            
            # Forecast-based reasoning
            if forecast.get("forecast"):
                next_hour_forecast = forecast["forecast"][-1]["yhat"]
                if next_hour_forecast > current * 1.1:
                    reasons.append(f"Forecast predicts increase in demand ({next_hour_forecast:.2f})")
                elif next_hour_forecast < current * 0.9:
                    reasons.append(f"Forecast predicts decrease in demand ({next_hour_forecast:.2f})")
            
            # Change magnitude reasoning
            change_percent = ((optimal - current) / current) * 100 if current > 0 else 0
            if abs(change_percent) > 10:
                reasons.append(f"Significant change recommended ({change_percent:.1f}%)")
            
            return " | ".join(reasons) if reasons else "No significant changes needed"
            
        except Exception as e:
            logging.error(f"Error generating reasoning: {str(e)}")
            return "Error generating reasoning"

class StorageOptimizationStrategy(OptimizationStrategy):
    """Strategy for optimizing storage resources."""
    
    def optimize_allocation(self,
                          current_usage: float,
                          historical_data: List[Dict[str, Any]],
                          constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize storage resource allocation."""
        try:
            # Analyze storage patterns
            storage_patterns = self._analyze_storage_patterns(historical_data)
            
            # Predict storage growth
            growth_forecast = self._predict_storage_growth(historical_data)
            
            # Calculate optimal allocation
            optimal_allocation = self._calculate_optimal_storage(
                current_usage,
                storage_patterns,
                growth_forecast,
                constraints
            )
            
            return {
                "amount": optimal_allocation["amount"],
                "confidence": optimal_allocation["confidence"],
                "reasoning": optimal_allocation["reasoning"]
            }
            
        except Exception as e:
            logging.error(f"Error optimizing storage allocation: {str(e)}")
            return {"amount": current_usage, "confidence": 0.5, "reasoning": "Error in optimization"}
    
    def _analyze_storage_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze storage usage patterns."""
        try:
            # Convert to time series
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate growth rate
            df['growth'] = df['usage'].pct_change()
            
            # Calculate daily growth patterns
            daily_growth = df.groupby(df['timestamp'].dt.hour)['growth'].mean()
            
            # Calculate weekly growth patterns
            weekly_growth = df.groupby(df['timestamp'].dt.dayofweek)['growth'].mean()
            
            # Calculate storage efficiency
            efficiency = self._calculate_storage_efficiency(df)
            
            return {
                "daily_growth": daily_growth.to_dict(),
                "weekly_growth": weekly_growth.to_dict(),
                "efficiency": efficiency
            }
            
        except Exception as e:
            logging.error(f"Error analyzing storage patterns: {str(e)}")
            return {}
    
    def _predict_storage_growth(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future storage growth using Prophet."""
        try:
            # Prepare data for Prophet
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.rename(columns={'timestamp': 'ds', 'usage': 'y'})
            
            # Fit Prophet model with growth rate
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True,
                changepoint_prior_scale=0.05
            )
            model.fit(df)
            
            # Generate future dates
            future = model.make_future_dataframe(periods=24, freq='H')
            
            # Make predictions
            forecast = model.predict(future)
            
            # Calculate growth rate
            forecast['growth_rate'] = forecast['yhat'].pct_change()
            
            return {
                "forecast": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
                "growth_rate": forecast['growth_rate'].tolist(),
                "trend": forecast['trend'].tolist()
            }
            
        except Exception as e:
            logging.error(f"Error predicting storage growth: {str(e)}")
            return {}
    
    def _calculate_storage_efficiency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate storage efficiency metrics."""
        try:
            # Calculate utilization rate
            utilization = df['usage'].mean() / df['usage'].max() if df['usage'].max() > 0 else 0
            
            # Calculate growth rate
            growth_rate = df['usage'].pct_change().mean()
            
            # Calculate fragmentation
            fragmentation = self._calculate_fragmentation(df)
            
            return {
                "utilization": utilization,
                "growth_rate": growth_rate,
                "fragmentation": fragmentation
            }
            
        except Exception as e:
            logging.error(f"Error calculating storage efficiency: {str(e)}")
            return {}
    
    def _calculate_fragmentation(self, df: pd.DataFrame) -> float:
        """Calculate storage fragmentation."""
        try:
            # Calculate usage gaps
            usage_gaps = df['usage'].diff().dropna()
            
            # Calculate fragmentation score
            fragmentation = np.std(usage_gaps) / np.mean(usage_gaps) if np.mean(usage_gaps) > 0 else 0
            
            return fragmentation
            
        except Exception as e:
            logging.error(f"Error calculating fragmentation: {str(e)}")
            return 0
    
    def _calculate_optimal_storage(self,
                                 current_usage: float,
                                 patterns: Dict[str, Any],
                                 forecast: Dict[str, Any],
                                 constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal storage allocation."""
        try:
            # Get current growth patterns
            current_hour = datetime.now().hour
            current_day = datetime.now().dayofweek
            
            # Get pattern-based adjustment
            hour_growth = patterns.get("daily_growth", {}).get(current_hour, 0)
            day_growth = patterns.get("weekly_growth", {}).get(current_day, 0)
            
            # Get forecast-based adjustment
            forecast_values = forecast.get("forecast", [])
            if forecast_values:
                next_hour_forecast = forecast_values[-1]["yhat"]
                forecast_adjustment = next_hour_forecast / current_usage if current_usage > 0 else 1.0
            else:
                forecast_adjustment = 1.0
            
            # Calculate optimal amount with growth buffer
            growth_buffer = 1.2  # 20% buffer for unexpected growth
            optimal = current_usage * (1 + hour_growth + day_growth) * forecast_adjustment * growth_buffer
            
            # Apply constraints
            optimal = min(optimal, constraints.get("max", float('inf')))
            optimal = max(optimal, constraints.get("min", 0))
            
            # Calculate confidence
            confidence = self._calculate_storage_confidence(
                patterns,
                forecast,
                optimal,
                current_usage
            )
            
            # Generate reasoning
            reasoning = self._generate_storage_reasoning(
                optimal,
                current_usage,
                patterns,
                forecast
            )
            
            return {
                "amount": optimal,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logging.error(f"Error calculating optimal storage: {str(e)}")
            return {
                "amount": current_usage,
                "confidence": 0.5,
                "reasoning": "Error in calculation"
            }
    
    def _calculate_storage_confidence(self,
                                    patterns: Dict[str, Any],
                                    forecast: Dict[str, Any],
                                    optimal: float,
                                    current: float) -> float:
        """Calculate confidence in the storage optimization decision."""
        try:
            # Pattern consistency
            growth_std = np.std(list(patterns.get("daily_growth", {}).values()))
            pattern_confidence = 1 - (growth_std / abs(np.mean(list(patterns.get("daily_growth", {}).values()))) if np.mean(list(patterns.get("daily_growth", {}).values())) != 0 else 0.5)
            
            # Forecast confidence
            if forecast.get("forecast"):
                forecast_std = np.std([f["yhat_upper"] - f["yhat_lower"] for f in forecast["forecast"]])
                forecast_confidence = 1 - (forecast_std / np.mean([f["yhat"] for f in forecast["forecast"]]))
            else:
                forecast_confidence = 0.5
            
            # Efficiency confidence
            efficiency = patterns.get("efficiency", {})
            efficiency_confidence = efficiency.get("utilization", 0.5)
            
            # Combine confidences
            confidence = (pattern_confidence + forecast_confidence + efficiency_confidence) / 3
            return max(0, min(1, confidence))
            
        except Exception as e:
            logging.error(f"Error calculating storage confidence: {str(e)}")
            return 0.5
    
    def _generate_storage_reasoning(self,
                                  optimal: float,
                                  current: float,
                                  patterns: Dict[str, Any],
                                  forecast: Dict[str, Any]) -> str:
        """Generate reasoning for the storage optimization decision."""
        try:
            reasons = []
            
            # Growth pattern reasoning
            if patterns.get("daily_growth"):
                current_hour = datetime.now().hour
                hour_growth = patterns["daily_growth"].get(current_hour, 0)
                if hour_growth > 0.01:
                    reasons.append(f"High growth rate detected for current hour ({hour_growth:.2%})")
                elif hour_growth < -0.01:
                    reasons.append(f"Negative growth rate detected for current hour ({hour_growth:.2%})")
            
            # Forecast reasoning
            if forecast.get("forecast"):
                next_hour_forecast = forecast["forecast"][-1]["yhat"]
                if next_hour_forecast > current * 1.1:
                    reasons.append(f"Forecast predicts significant growth ({next_hour_forecast:.2f})")
                elif next_hour_forecast < current * 0.9:
                    reasons.append(f"Forecast predicts storage reduction ({next_hour_forecast:.2f})")
            
            # Efficiency reasoning
            efficiency = patterns.get("efficiency", {})
            if efficiency.get("utilization", 0) > 0.8:
                reasons.append("High storage utilization detected")
            if efficiency.get("fragmentation", 0) > 0.5:
                reasons.append("High storage fragmentation detected")
            
            # Change magnitude reasoning
            change_percent = ((optimal - current) / current) * 100 if current > 0 else 0
            if abs(change_percent) > 10:
                reasons.append(f"Significant change recommended ({change_percent:.1f}%)")
            
            return " | ".join(reasons) if reasons else "No significant changes needed"
            
        except Exception as e:
            logging.error(f"Error generating storage reasoning: {str(e)}")
            return "Error generating reasoning"

class NetworkOptimizationStrategy(OptimizationStrategy):
    """Strategy for optimizing network resources."""
    
    def optimize_allocation(self,
                          current_usage: float,
                          historical_data: List[Dict[str, Any]],
                          constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize network resource allocation."""
        try:
            # Analyze network patterns
            network_patterns = self._analyze_network_patterns(historical_data)
            
            # Predict network traffic
            traffic_forecast = self._predict_network_traffic(historical_data)
            
            # Calculate optimal allocation
            optimal_allocation = self._calculate_optimal_network(
                current_usage,
                network_patterns,
                traffic_forecast,
                constraints
            )
            
            return {
                "amount": optimal_allocation["amount"],
                "confidence": optimal_allocation["confidence"],
                "reasoning": optimal_allocation["reasoning"]
            }
            
        except Exception as e:
            logging.error(f"Error optimizing network allocation: {str(e)}")
            return {"amount": current_usage, "confidence": 0.5, "reasoning": "Error in optimization"}
    
    def _analyze_network_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze network usage patterns."""
        try:
            # Convert to time series
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate traffic patterns
            df['traffic'] = df['usage'].diff()
            
            # Calculate daily traffic patterns
            daily_traffic = df.groupby(df['timestamp'].dt.hour)['traffic'].mean()
            
            # Calculate weekly traffic patterns
            weekly_traffic = df.groupby(df['timestamp'].dt.dayofweek)['traffic'].mean()
            
            # Calculate network quality metrics
            quality_metrics = self._calculate_network_quality(df)
            
            return {
                "daily_traffic": daily_traffic.to_dict(),
                "weekly_traffic": weekly_traffic.to_dict(),
                "quality_metrics": quality_metrics
            }
            
        except Exception as e:
            logging.error(f"Error analyzing network patterns: {str(e)}")
            return {}
    
    def _predict_network_traffic(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future network traffic using Prophet."""
        try:
            # Prepare data for Prophet
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.rename(columns={'timestamp': 'ds', 'usage': 'y'})
            
            # Fit Prophet model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True,
                changepoint_prior_scale=0.05
            )
            model.fit(df)
            
            # Generate future dates
            future = model.make_future_dataframe(periods=24, freq='H')
            
            # Make predictions
            forecast = model.predict(future)
            
            # Calculate traffic patterns
            forecast['traffic'] = forecast['yhat'].diff()
            
            return {
                "forecast": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
                "traffic_patterns": forecast['traffic'].tolist(),
                "trend": forecast['trend'].tolist()
            }
            
        except Exception as e:
            logging.error(f"Error predicting network traffic: {str(e)}")
            return {}
    
    def _calculate_network_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate network quality metrics."""
        try:
            # Calculate bandwidth utilization
            utilization = df['usage'].mean() / df['usage'].max() if df['usage'].max() > 0 else 0
            
            # Calculate traffic volatility
            volatility = df['traffic'].std() / df['traffic'].mean() if df['traffic'].mean() > 0 else 0
            
            # Calculate peak usage
            peak_usage = df['usage'].max()
            
            return {
                "utilization": utilization,
                "volatility": volatility,
                "peak_usage": peak_usage
            }
            
        except Exception as e:
            logging.error(f"Error calculating network quality: {str(e)}")
            return {}
    
    def _calculate_optimal_network(self,
                                 current_usage: float,
                                 patterns: Dict[str, Any],
                                 forecast: Dict[str, Any],
                                 constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal network allocation."""
        try:
            # Get current traffic patterns
            current_hour = datetime.now().hour
            current_day = datetime.now().dayofweek
            
            # Get pattern-based adjustment
            hour_traffic = patterns.get("daily_traffic", {}).get(current_hour, 0)
            day_traffic = patterns.get("weekly_traffic", {}).get(current_day, 0)
            
            # Get forecast-based adjustment
            forecast_values = forecast.get("forecast", [])
            if forecast_values:
                next_hour_forecast = forecast_values[-1]["yhat"]
                forecast_adjustment = next_hour_forecast / current_usage if current_usage > 0 else 1.0
            else:
                forecast_adjustment = 1.0
            
            # Calculate optimal amount with traffic buffer
            traffic_buffer = 1.3  # 30% buffer for traffic spikes
            optimal = current_usage * (1 + hour_traffic + day_traffic) * forecast_adjustment * traffic_buffer
            
            # Apply constraints
            optimal = min(optimal, constraints.get("max", float('inf')))
            optimal = max(optimal, constraints.get("min", 0))
            
            # Calculate confidence
            confidence = self._calculate_network_confidence(
                patterns,
                forecast,
                optimal,
                current_usage
            )
            
            # Generate reasoning
            reasoning = self._generate_network_reasoning(
                optimal,
                current_usage,
                patterns,
                forecast
            )
            
            return {
                "amount": optimal,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logging.error(f"Error calculating optimal network: {str(e)}")
            return {
                "amount": current_usage,
                "confidence": 0.5,
                "reasoning": "Error in calculation"
            }
    
    def _calculate_network_confidence(self,
                                    patterns: Dict[str, Any],
                                    forecast: Dict[str, Any],
                                    optimal: float,
                                    current: float) -> float:
        """Calculate confidence in the network optimization decision."""
        try:
            # Pattern consistency
            traffic_std = np.std(list(patterns.get("daily_traffic", {}).values()))
            pattern_confidence = 1 - (traffic_std / abs(np.mean(list(patterns.get("daily_traffic", {}).values()))) if np.mean(list(patterns.get("daily_traffic", {}).values())) != 0 else 0.5)
            
            # Forecast confidence
            if forecast.get("forecast"):
                forecast_std = np.std([f["yhat_upper"] - f["yhat_lower"] for f in forecast["forecast"]])
                forecast_confidence = 1 - (forecast_std / np.mean([f["yhat"] for f in forecast["forecast"]]))
            else:
                forecast_confidence = 0.5
            
            # Quality confidence
            quality = patterns.get("quality_metrics", {})
            quality_confidence = 1 - quality.get("volatility", 0.5)
            
            # Combine confidences
            confidence = (pattern_confidence + forecast_confidence + quality_confidence) / 3
            return max(0, min(1, confidence))
            
        except Exception as e:
            logging.error(f"Error calculating network confidence: {str(e)}")
            return 0.5
    
    def _generate_network_reasoning(self,
                                  optimal: float,
                                  current: float,
                                  patterns: Dict[str, Any],
                                  forecast: Dict[str, Any]) -> str:
        """Generate reasoning for the network optimization decision."""
        try:
            reasons = []
            
            # Traffic pattern reasoning
            if patterns.get("daily_traffic"):
                current_hour = datetime.now().hour
                hour_traffic = patterns["daily_traffic"].get(current_hour, 0)
                if hour_traffic > 0.1:
                    reasons.append(f"High traffic expected for current hour ({hour_traffic:.2f})")
                elif hour_traffic < -0.1:
                    reasons.append(f"Low traffic expected for current hour ({hour_traffic:.2f})")
            
            # Forecast reasoning
            if forecast.get("forecast"):
                next_hour_forecast = forecast["forecast"][-1]["yhat"]
                if next_hour_forecast > current * 1.1:
                    reasons.append(f"Forecast predicts traffic increase ({next_hour_forecast:.2f})")
                elif next_hour_forecast < current * 0.9:
                    reasons.append(f"Forecast predicts traffic decrease ({next_hour_forecast:.2f})")
            
            # Quality reasoning
            quality = patterns.get("quality_metrics", {})
            if quality.get("utilization", 0) > 0.8:
                reasons.append("High bandwidth utilization detected")
            if quality.get("volatility", 0) > 0.5:
                reasons.append("High traffic volatility detected")
            
            # Change magnitude reasoning
            change_percent = ((optimal - current) / current) * 100 if current > 0 else 0
            if abs(change_percent) > 10:
                reasons.append(f"Significant change recommended ({change_percent:.1f}%)")
            
            return " | ".join(reasons) if reasons else "No significant changes needed"
            
        except Exception as e:
            logging.error(f"Error generating network reasoning: {str(e)}")
            return "Error generating reasoning"

class MemoryOptimizationStrategy(OptimizationStrategy):
    """Strategy for optimizing memory resources."""
    
    def optimize_allocation(self,
                          current_usage: float,
                          historical_data: List[Dict[str, Any]],
                          constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize memory resource allocation."""
        try:
            # Analyze memory patterns
            memory_patterns = self._analyze_memory_patterns(historical_data)
            
            # Predict memory usage
            usage_forecast = self._predict_memory_usage(historical_data)
            
            # Calculate optimal allocation
            optimal_allocation = self._calculate_optimal_memory(
                current_usage,
                memory_patterns,
                usage_forecast,
                constraints
            )
            
            return {
                "amount": optimal_allocation["amount"],
                "confidence": optimal_allocation["confidence"],
                "reasoning": optimal_allocation["reasoning"]
            }
            
        except Exception as e:
            logging.error(f"Error optimizing memory allocation: {str(e)}")
            return {"amount": current_usage, "confidence": 0.5, "reasoning": "Error in optimization"}
    
    def _analyze_memory_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze memory usage patterns."""
        try:
            # Convert to time series
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate memory patterns
            df['memory_usage'] = df['usage']
            df['memory_pressure'] = df['memory_usage'].pct_change()
            
            # Calculate daily memory patterns
            daily_memory = df.groupby(df['timestamp'].dt.hour)['memory_usage'].mean()
            
            # Calculate weekly memory patterns
            weekly_memory = df.groupby(df['timestamp'].dt.dayofweek)['memory_usage'].mean()
            
            # Calculate memory efficiency metrics
            efficiency = self._calculate_memory_efficiency(df)
            
            return {
                "daily_memory": daily_memory.to_dict(),
                "weekly_memory": weekly_memory.to_dict(),
                "efficiency": efficiency
            }
            
        except Exception as e:
            logging.error(f"Error analyzing memory patterns: {str(e)}")
            return {}
    
    def _predict_memory_usage(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future memory usage using Prophet and ARIMA."""
        try:
            # Prepare data for Prophet
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.rename(columns={'timestamp': 'ds', 'usage': 'y'})
            
            # Fit Prophet model with memory-specific parameters
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0
            )
            model.fit(df)
            
            # Generate future dates
            future = model.make_future_dataframe(periods=24, freq='H')
            
            # Make predictions
            forecast = model.predict(future)
            
            # Calculate memory pressure
            forecast['memory_pressure'] = forecast['yhat'].pct_change()
            
            return {
                "forecast": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
                "memory_pressure": forecast['memory_pressure'].tolist(),
                "trend": forecast['trend'].tolist()
            }
            
        except Exception as e:
            logging.error(f"Error predicting memory usage: {str(e)}")
            return {}
    
    def _calculate_memory_efficiency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate memory efficiency metrics."""
        try:
            # Calculate memory utilization
            utilization = df['memory_usage'].mean() / df['memory_usage'].max() if df['memory_usage'].max() > 0 else 0
            
            # Calculate memory pressure
            pressure = df['memory_pressure'].mean()
            
            # Calculate memory fragmentation
            fragmentation = self._calculate_memory_fragmentation(df)
            
            return {
                "utilization": utilization,
                "pressure": pressure,
                "fragmentation": fragmentation
            }
            
        except Exception as e:
            logging.error(f"Error calculating memory efficiency: {str(e)}")
            return {}
    
    def _calculate_memory_fragmentation(self, df: pd.DataFrame) -> float:
        """Calculate memory fragmentation."""
        try:
            # Calculate memory usage gaps
            usage_gaps = df['memory_usage'].diff().dropna()
            
            # Calculate fragmentation score
            fragmentation = np.std(usage_gaps) / np.mean(usage_gaps) if np.mean(usage_gaps) > 0 else 0
            
            return fragmentation
            
        except Exception as e:
            logging.error(f"Error calculating memory fragmentation: {str(e)}")
            return 0
    
    def _calculate_optimal_memory(self,
                                 current_usage: float,
                                 patterns: Dict[str, Any],
                                 forecast: Dict[str, Any],
                                 constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal memory allocation."""
        try:
            # Get current memory patterns
            current_hour = datetime.now().hour
            current_day = datetime.now().dayofweek
            
            # Get pattern-based adjustment
            hour_memory = patterns.get("daily_memory", {}).get(current_hour, 0)
            day_memory = patterns.get("weekly_memory", {}).get(current_day, 0)
            
            # Get forecast-based adjustment
            forecast_values = forecast.get("forecast", [])
            if forecast_values:
                next_hour_forecast = forecast_values[-1]["yhat"]
                forecast_adjustment = next_hour_forecast / current_usage if current_usage > 0 else 1.0
            else:
                forecast_adjustment = 1.0
            
            # Calculate optimal amount with memory buffer
            memory_buffer = 1.25  # 25% buffer for memory spikes
            optimal = current_usage * (1 + hour_memory + day_memory) * forecast_adjustment * memory_buffer
            
            # Apply constraints
            optimal = min(optimal, constraints.get("max", float('inf')))
            optimal = max(optimal, constraints.get("min", 0))
            
            # Calculate confidence
            confidence = self._calculate_memory_confidence(
                patterns,
                forecast,
                optimal,
                current_usage
            )
            
            # Generate reasoning
            reasoning = self._generate_memory_reasoning(
                optimal,
                current_usage,
                patterns,
                forecast
            )
            
            return {
                "amount": optimal,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logging.error(f"Error calculating optimal memory: {str(e)}")
            return {
                "amount": current_usage,
                "confidence": 0.5,
                "reasoning": "Error in calculation"
            }
    
    def _calculate_memory_confidence(self,
                                    patterns: Dict[str, Any],
                                    forecast: Dict[str, Any],
                                    optimal: float,
                                    current: float) -> float:
        """Calculate confidence in the memory optimization decision."""
        try:
            # Pattern consistency
            memory_std = np.std(list(patterns.get("daily_memory", {}).values()))
            pattern_confidence = 1 - (memory_std / abs(np.mean(list(patterns.get("daily_memory", {}).values()))) if np.mean(list(patterns.get("daily_memory", {}).values())) != 0 else 0.5)
            
            # Forecast confidence
            if forecast.get("forecast"):
                forecast_std = np.std([f["yhat_upper"] - f["yhat_lower"] for f in forecast["forecast"]])
                forecast_confidence = 1 - (forecast_std / np.mean([f["yhat"] for f in forecast["forecast"]]))
            else:
                forecast_confidence = 0.5
            
            # Efficiency confidence
            efficiency = patterns.get("efficiency", {})
            efficiency_confidence = 1 - efficiency.get("pressure", 0.5)
            
            # Combine confidences
            confidence = (pattern_confidence + forecast_confidence + efficiency_confidence) / 3
            return max(0, min(1, confidence))
            
        except Exception as e:
            logging.error(f"Error calculating memory confidence: {str(e)}")
            return 0.5
    
    def _generate_memory_reasoning(self,
                                  optimal: float,
                                  current: float,
                                  patterns: Dict[str, Any],
                                  forecast: Dict[str, Any]) -> str:
        """Generate reasoning for the memory optimization decision."""
        try:
            reasons = []
            
            # Memory pattern reasoning
            if patterns.get("daily_memory"):
                current_hour = datetime.now().hour
                hour_memory = patterns["daily_memory"].get(current_hour, 0)
                if hour_memory > 0.1:
                    reasons.append(f"High memory usage expected for current hour ({hour_memory:.2f})")
                elif hour_memory < -0.1:
                    reasons.append(f"Low memory usage expected for current hour ({hour_memory:.2f})")
            
            # Forecast reasoning
            if forecast.get("forecast"):
                next_hour_forecast = forecast["forecast"][-1]["yhat"]
                if next_hour_forecast > current * 1.1:
                    reasons.append(f"Forecast predicts memory increase ({next_hour_forecast:.2f})")
                elif next_hour_forecast < current * 0.9:
                    reasons.append(f"Forecast predicts memory decrease ({next_hour_forecast:.2f})")
            
            # Efficiency reasoning
            efficiency = patterns.get("efficiency", {})
            if efficiency.get("utilization", 0) > 0.8:
                reasons.append("High memory utilization detected")
            if efficiency.get("pressure", 0) > 0.5:
                reasons.append("High memory pressure detected")
            
            # Change magnitude reasoning
            change_percent = ((optimal - current) / current) * 100 if current > 0 else 0
            if abs(change_percent) > 10:
                reasons.append(f"Significant change recommended ({change_percent:.1f}%)")
            
            return " | ".join(reasons) if reasons else "No significant changes needed"
            
        except Exception as e:
            logging.error(f"Error generating memory reasoning: {str(e)}")
            return "Error generating reasoning"

class GPUOptimizationStrategy(OptimizationStrategy):
    """Strategy for optimizing GPU resources."""
    
    def optimize_allocation(self,
                          current_usage: float,
                          historical_data: List[Dict[str, Any]],
                          constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize GPU resource allocation."""
        try:
            # Analyze GPU patterns
            gpu_patterns = self._analyze_gpu_patterns(historical_data)
            
            # Predict GPU usage
            usage_forecast = self._predict_gpu_usage(historical_data)
            
            # Calculate optimal allocation
            optimal_allocation = self._calculate_optimal_gpu(
                current_usage,
                gpu_patterns,
                usage_forecast,
                constraints
            )
            
            return {
                "amount": optimal_allocation["amount"],
                "confidence": optimal_allocation["confidence"],
                "reasoning": optimal_allocation["reasoning"]
            }
            
        except Exception as e:
            logging.error(f"Error optimizing GPU allocation: {str(e)}")
            return {"amount": current_usage, "confidence": 0.5, "reasoning": "Error in optimization"}
    
    def _analyze_gpu_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze GPU usage patterns."""
        try:
            # Convert to time series
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate GPU patterns
            df['gpu_usage'] = df['usage']
            df['gpu_utilization'] = df['gpu_usage'].pct_change()
            
            # Calculate daily GPU patterns
            daily_gpu = df.groupby(df['timestamp'].dt.hour)['gpu_usage'].mean()
            
            # Calculate weekly GPU patterns
            weekly_gpu = df.groupby(df['timestamp'].dt.dayofweek)['gpu_usage'].mean()
            
            # Calculate GPU efficiency metrics
            efficiency = self._calculate_gpu_efficiency(df)
            
            return {
                "daily_gpu": daily_gpu.to_dict(),
                "weekly_gpu": weekly_gpu.to_dict(),
                "efficiency": efficiency
            }
            
        except Exception as e:
            logging.error(f"Error analyzing GPU patterns: {str(e)}")
            return {}
    
    def _predict_gpu_usage(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future GPU usage using Prophet and ARIMA."""
        try:
            # Prepare data for Prophet
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.rename(columns={'timestamp': 'ds', 'usage': 'y'})
            
            # Fit Prophet model with GPU-specific parameters
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0
            )
            model.fit(df)
            
            # Generate future dates
            future = model.make_future_dataframe(periods=24, freq='H')
            
            # Make predictions
            forecast = model.predict(future)
            
            # Calculate GPU utilization
            forecast['gpu_utilization'] = forecast['yhat'].pct_change()
            
            return {
                "forecast": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
                "gpu_utilization": forecast['gpu_utilization'].tolist(),
                "trend": forecast['trend'].tolist()
            }
            
        except Exception as e:
            logging.error(f"Error predicting GPU usage: {str(e)}")
            return {}
    
    def _calculate_gpu_efficiency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate GPU efficiency metrics."""
        try:
            # Calculate GPU utilization
            utilization = df['gpu_usage'].mean() / df['gpu_usage'].max() if df['gpu_usage'].max() > 0 else 0
            
            # Calculate GPU utilization rate
            utilization_rate = df['gpu_utilization'].mean()
            
            # Calculate GPU efficiency
            efficiency = self._calculate_gpu_efficiency_score(df)
            
            return {
                "utilization": utilization,
                "utilization_rate": utilization_rate,
                "efficiency": efficiency
            }
            
        except Exception as e:
            logging.error(f"Error calculating GPU efficiency: {str(e)}")
            return {}
    
    def _calculate_gpu_efficiency_score(self, df: pd.DataFrame) -> float:
        """Calculate GPU efficiency score."""
        try:
            # Calculate GPU usage stability
            usage_stability = 1 - (df['gpu_usage'].std() / df['gpu_usage'].mean() if df['gpu_usage'].mean() > 0 else 0)
            
            # Calculate GPU utilization efficiency
            utilization_efficiency = 1 - (df['gpu_utilization'].std() / df['gpu_utilization'].mean() if df['gpu_utilization'].mean() > 0 else 0)
            
            # Combine efficiency metrics
            efficiency = (usage_stability + utilization_efficiency) / 2
            
            return efficiency
            
        except Exception as e:
            logging.error(f"Error calculating GPU efficiency score: {str(e)}")
            return 0
    
    def _calculate_optimal_gpu(self,
                              current_usage: float,
                              patterns: Dict[str, Any],
                              forecast: Dict[str, Any],
                              constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal GPU allocation."""
        try:
            # Get current GPU patterns
            current_hour = datetime.now().hour
            current_day = datetime.now().dayofweek
            
            # Get pattern-based adjustment
            hour_gpu = patterns.get("daily_gpu", {}).get(current_hour, 0)
            day_gpu = patterns.get("weekly_gpu", {}).get(current_day, 0)
            
            # Get forecast-based adjustment
            forecast_values = forecast.get("forecast", [])
            if forecast_values:
                next_hour_forecast = forecast_values[-1]["yhat"]
                forecast_adjustment = next_hour_forecast / current_usage if current_usage > 0 else 1.0
            else:
                forecast_adjustment = 1.0
            
            # Calculate optimal amount with GPU buffer
            gpu_buffer = 1.15  # 15% buffer for GPU spikes
            optimal = current_usage * (1 + hour_gpu + day_gpu) * forecast_adjustment * gpu_buffer
            
            # Apply constraints
            optimal = min(optimal, constraints.get("max", float('inf')))
            optimal = max(optimal, constraints.get("min", 0))
            
            # Calculate confidence
            confidence = self._calculate_gpu_confidence(
                patterns,
                forecast,
                optimal,
                current_usage
            )
            
            # Generate reasoning
            reasoning = self._generate_gpu_reasoning(
                optimal,
                current_usage,
                patterns,
                forecast
            )
            
            return {
                "amount": optimal,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logging.error(f"Error calculating optimal GPU: {str(e)}")
            return {
                "amount": current_usage,
                "confidence": 0.5,
                "reasoning": "Error in calculation"
            }
    
    def _calculate_gpu_confidence(self,
                                 patterns: Dict[str, Any],
                                 forecast: Dict[str, Any],
                                 optimal: float,
                                 current: float) -> float:
        """Calculate confidence in the GPU optimization decision."""
        try:
            # Pattern consistency
            gpu_std = np.std(list(patterns.get("daily_gpu", {}).values()))
            pattern_confidence = 1 - (gpu_std / abs(np.mean(list(patterns.get("daily_gpu", {}).values()))) if np.mean(list(patterns.get("daily_gpu", {}).values())) != 0 else 0.5)
            
            # Forecast confidence
            if forecast.get("forecast"):
                forecast_std = np.std([f["yhat_upper"] - f["yhat_lower"] for f in forecast["forecast"]])
                forecast_confidence = 1 - (forecast_std / np.mean([f["yhat"] for f in forecast["forecast"]]))
            else:
                forecast_confidence = 0.5
            
            # Efficiency confidence
            efficiency = patterns.get("efficiency", {})
            efficiency_confidence = efficiency.get("efficiency", 0.5)
            
            # Combine confidences
            confidence = (pattern_confidence + forecast_confidence + efficiency_confidence) / 3
            return max(0, min(1, confidence))
            
        except Exception as e:
            logging.error(f"Error calculating GPU confidence: {str(e)}")
            return 0.5
    
    def _generate_gpu_reasoning(self,
                               optimal: float,
                               current: float,
                               patterns: Dict[str, Any],
                               forecast: Dict[str, Any]) -> str:
        """Generate reasoning for the GPU optimization decision."""
        try:
            reasons = []
            
            # GPU pattern reasoning
            if patterns.get("daily_gpu"):
                current_hour = datetime.now().hour
                hour_gpu = patterns["daily_gpu"].get(current_hour, 0)
                if hour_gpu > 0.1:
                    reasons.append(f"High GPU usage expected for current hour ({hour_gpu:.2f})")
                elif hour_gpu < -0.1:
                    reasons.append(f"Low GPU usage expected for current hour ({hour_gpu:.2f})")
            
            # Forecast reasoning
            if forecast.get("forecast"):
                next_hour_forecast = forecast["forecast"][-1]["yhat"]
                if next_hour_forecast > current * 1.1:
                    reasons.append(f"Forecast predicts GPU increase ({next_hour_forecast:.2f})")
                elif next_hour_forecast < current * 0.9:
                    reasons.append(f"Forecast predicts GPU decrease ({next_hour_forecast:.2f})")
            
            # Efficiency reasoning
            efficiency = patterns.get("efficiency", {})
            if efficiency.get("utilization", 0) > 0.8:
                reasons.append("High GPU utilization detected")
            if efficiency.get("efficiency", 0) < 0.5:
                reasons.append("Low GPU efficiency detected")
            
            # Change magnitude reasoning
            change_percent = ((optimal - current) / current) * 100 if current > 0 else 0
            if abs(change_percent) > 10:
                reasons.append(f"Significant change recommended ({change_percent:.1f}%)")
            
            return " | ".join(reasons) if reasons else "No significant changes needed"
            
        except Exception as e:
            logging.error(f"Error generating GPU reasoning: {str(e)}")
            return "Error generating reasoning"

class DatabaseOptimizationStrategy(OptimizationStrategy):
    """Strategy for optimizing database resources."""
    
    def optimize_allocation(self,
                          current_usage: float,
                          historical_data: List[Dict[str, Any]],
                          constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize database resource allocation."""
        try:
            # Analyze database patterns
            db_patterns = self._analyze_database_patterns(historical_data)
            
            # Predict database usage
            usage_forecast = self._predict_database_usage(historical_data)
            
            # Calculate optimal allocation
            optimal_allocation = self._calculate_optimal_database(
                current_usage,
                db_patterns,
                usage_forecast,
                constraints
            )
            
            return {
                "amount": optimal_allocation["amount"],
                "confidence": optimal_allocation["confidence"],
                "reasoning": optimal_allocation["reasoning"]
            }
            
        except Exception as e:
            logging.error(f"Error optimizing database allocation: {str(e)}")
            return {"amount": current_usage, "confidence": 0.5, "reasoning": "Error in optimization"}
    
    def _analyze_database_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze database usage patterns."""
        try:
            # Convert to time series
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate database patterns
            df['db_usage'] = df['usage']
            df['db_load'] = df['db_usage'].pct_change()
            
            # Calculate daily database patterns
            daily_db = df.groupby(df['timestamp'].dt.hour)['db_usage'].mean()
            
            # Calculate weekly database patterns
            weekly_db = df.groupby(df['timestamp'].dt.dayofweek)['db_usage'].mean()
            
            # Calculate database efficiency metrics
            efficiency = self._calculate_database_efficiency(df)
            
            return {
                "daily_db": daily_db.to_dict(),
                "weekly_db": weekly_db.to_dict(),
                "efficiency": efficiency
            }
            
        except Exception as e:
            logging.error(f"Error analyzing database patterns: {str(e)}")
            return {}
    
    def _predict_database_usage(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future database usage using Prophet and ARIMA."""
        try:
            # Prepare data for Prophet
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.rename(columns={'timestamp': 'ds', 'usage': 'y'})
            
            # Fit Prophet model with database-specific parameters
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0
            )
            model.fit(df)
            
            # Generate future dates
            future = model.make_future_dataframe(periods=24, freq='H')
            
            # Make predictions
            forecast = model.predict(future)
            
            # Calculate database load
            forecast['db_load'] = forecast['yhat'].pct_change()
            
            return {
                "forecast": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
                "db_load": forecast['db_load'].tolist(),
                "trend": forecast['trend'].tolist()
            }
            
        except Exception as e:
            logging.error(f"Error predicting database usage: {str(e)}")
            return {}
    
    def _calculate_database_efficiency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate database efficiency metrics."""
        try:
            # Calculate database utilization
            utilization = df['db_usage'].mean() / df['db_usage'].max() if df['db_usage'].max() > 0 else 0
            
            # Calculate database load
            load = df['db_load'].mean()
            
            # Calculate database performance
            performance = self._calculate_database_performance(df)
            
            return {
                "utilization": utilization,
                "load": load,
                "performance": performance
            }
            
        except Exception as e:
            logging.error(f"Error calculating database efficiency: {str(e)}")
            return {}
    
    def _calculate_database_performance(self, df: pd.DataFrame) -> float:
        """Calculate database performance score."""
        try:
            # Calculate database usage stability
            usage_stability = 1 - (df['db_usage'].std() / df['db_usage'].mean() if df['db_usage'].mean() > 0 else 0)
            
            # Calculate database load stability
            load_stability = 1 - (df['db_load'].std() / df['db_load'].mean() if df['db_load'].mean() > 0 else 0)
            
            # Combine performance metrics
            performance = (usage_stability + load_stability) / 2
            
            return performance
            
        except Exception as e:
            logging.error(f"Error calculating database performance: {str(e)}")
            return 0
    
    def _calculate_optimal_database(self,
                                   current_usage: float,
                                   patterns: Dict[str, Any],
                                   forecast: Dict[str, Any],
                                   constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal database allocation."""
        try:
            # Get current database patterns
            current_hour = datetime.now().hour
            current_day = datetime.now().dayofweek
            
            # Get pattern-based adjustment
            hour_db = patterns.get("daily_db", {}).get(current_hour, 0)
            day_db = patterns.get("weekly_db", {}).get(current_day, 0)
            
            # Get forecast-based adjustment
            forecast_values = forecast.get("forecast", [])
            if forecast_values:
                next_hour_forecast = forecast_values[-1]["yhat"]
                forecast_adjustment = next_hour_forecast / current_usage if current_usage > 0 else 1.0
            else:
                forecast_adjustment = 1.0
            
            # Calculate optimal amount with database buffer
            db_buffer = 1.35  # 35% buffer for database spikes
            optimal = current_usage * (1 + hour_db + day_db) * forecast_adjustment * db_buffer
            
            # Apply constraints
            optimal = min(optimal, constraints.get("max", float('inf')))
            optimal = max(optimal, constraints.get("min", 0))
            
            # Calculate confidence
            confidence = self._calculate_database_confidence(
                patterns,
                forecast,
                optimal,
                current_usage
            )
            
            # Generate reasoning
            reasoning = self._generate_database_reasoning(
                optimal,
                current_usage,
                patterns,
                forecast
            )
            
            return {
                "amount": optimal,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logging.error(f"Error calculating optimal database: {str(e)}")
            return {
                "amount": current_usage,
                "confidence": 0.5,
                "reasoning": "Error in calculation"
            }
    
    def _calculate_database_confidence(self,
                                     patterns: Dict[str, Any],
                                     forecast: Dict[str, Any],
                                     optimal: float,
                                     current: float) -> float:
        """Calculate confidence in the database optimization decision."""
        try:
            # Pattern consistency
            db_std = np.std(list(patterns.get("daily_db", {}).values()))
            pattern_confidence = 1 - (db_std / abs(np.mean(list(patterns.get("daily_db", {}).values()))) if np.mean(list(patterns.get("daily_db", {}).values())) != 0 else 0.5)
            
            # Forecast confidence
            if forecast.get("forecast"):
                forecast_std = np.std([f["yhat_upper"] - f["yhat_lower"] for f in forecast["forecast"]])
                forecast_confidence = 1 - (forecast_std / np.mean([f["yhat"] for f in forecast["forecast"]]))
            else:
                forecast_confidence = 0.5
            
            # Performance confidence
            efficiency = patterns.get("efficiency", {})
            performance_confidence = efficiency.get("performance", 0.5)
            
            # Combine confidences
            confidence = (pattern_confidence + forecast_confidence + performance_confidence) / 3
            return max(0, min(1, confidence))
            
        except Exception as e:
            logging.error(f"Error calculating database confidence: {str(e)}")
            return 0.5
    
    def _generate_database_reasoning(self,
                                    optimal: float,
                                    current: float,
                                    patterns: Dict[str, Any],
                                    forecast: Dict[str, Any]) -> str:
        """Generate reasoning for the database optimization decision."""
        try:
            reasons = []
            
            # Database pattern reasoning
            if patterns.get("daily_db"):
                current_hour = datetime.now().hour
                hour_db = patterns["daily_db"].get(current_hour, 0)
                if hour_db > 0.1:
                    reasons.append(f"High database usage expected for current hour ({hour_db:.2f})")
                elif hour_db < -0.1:
                    reasons.append(f"Low database usage expected for current hour ({hour_db:.2f})")
            
            # Forecast reasoning
            if forecast.get("forecast"):
                next_hour_forecast = forecast["forecast"][-1]["yhat"]
                if next_hour_forecast > current * 1.1:
                    reasons.append(f"Forecast predicts database increase ({next_hour_forecast:.2f})")
                elif next_hour_forecast < current * 0.9:
                    reasons.append(f"Forecast predicts database decrease ({next_hour_forecast:.2f})")
            
            # Performance reasoning
            efficiency = patterns.get("efficiency", {})
            if efficiency.get("utilization", 0) > 0.8:
                reasons.append("High database utilization detected")
            if efficiency.get("performance", 0) < 0.5:
                reasons.append("Low database performance detected")
            
            # Change magnitude reasoning
            change_percent = ((optimal - current) / current) * 100 if current > 0 else 0
            if abs(change_percent) > 10:
                reasons.append(f"Significant change recommended ({change_percent:.1f}%)")
            
            return " | ".join(reasons) if reasons else "No significant changes needed"
            
        except Exception as e:
            logging.error(f"Error generating database reasoning: {str(e)}")
            return "Error generating reasoning"

class CacheOptimizationStrategy(OptimizationStrategy):
    """Strategy for optimizing cache resources."""
    
    def optimize_allocation(self,
                          current_usage: float,
                          historical_data: List[Dict[str, Any]],
                          constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize cache resource allocation."""
        try:
            # Analyze cache patterns
            cache_patterns = self._analyze_cache_patterns(historical_data)
            
            # Predict cache usage with multiple models
            usage_forecast = self._predict_cache_usage(historical_data)
            
            # Calculate optimal allocation
            optimal_allocation = self._calculate_optimal_cache(
                current_usage,
                cache_patterns,
                usage_forecast,
                constraints
            )
            
            return {
                "amount": optimal_allocation["amount"],
                "confidence": optimal_allocation["confidence"],
                "reasoning": optimal_allocation["reasoning"]
            }
            
        except Exception as e:
            logging.error(f"Error optimizing cache allocation: {str(e)}")
            return {"amount": current_usage, "confidence": 0.5, "reasoning": "Error in optimization"}
    
    def _analyze_cache_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cache usage patterns."""
        try:
            # Convert to time series
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate cache patterns
            df['cache_usage'] = df['usage']
            df['cache_hit_rate'] = df.get('hit_rate', 0.5)  # Default to 0.5 if not provided
            df['cache_miss_rate'] = df.get('miss_rate', 0.5)  # Default to 0.5 if not provided
            
            # Calculate daily cache patterns
            daily_cache = df.groupby(df['timestamp'].dt.hour)['cache_usage'].mean()
            
            # Calculate weekly cache patterns
            weekly_cache = df.groupby(df['timestamp'].dt.dayofweek)['cache_usage'].mean()
            
            # Calculate cache efficiency metrics
            efficiency = self._calculate_cache_efficiency(df)
            
            return {
                "daily_cache": daily_cache.to_dict(),
                "weekly_cache": weekly_cache.to_dict(),
                "efficiency": efficiency
            }
            
        except Exception as e:
            logging.error(f"Error analyzing cache patterns: {str(e)}")
            return {}
    
    def _predict_cache_usage(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future cache usage using multiple models."""
        try:
            # Prepare data
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Prophet forecast
            prophet_forecast = self._prophet_forecast(df)
            
            # LSTM forecast
            lstm_forecast = self._lstm_forecast(df)
            
            # XGBoost forecast
            xgb_forecast = self._xgboost_forecast(df)
            
            # Combine forecasts with weights
            combined_forecast = self._combine_forecasts(
                prophet_forecast,
                lstm_forecast,
                xgb_forecast
            )
            
            return combined_forecast
            
        except Exception as e:
            logging.error(f"Error predicting cache usage: {str(e)}")
            return {}
    
    def _prophet_forecast(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate forecast using Prophet."""
        try:
            prophet_df = df.rename(columns={'timestamp': 'ds', 'usage': 'y'})
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True,
                changepoint_prior_scale=0.05
            )
            model.fit(prophet_df)
            
            future = model.make_future_dataframe(periods=24, freq='H')
            forecast = model.predict(future)
            
            return {
                "model": "prophet",
                "forecast": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
                "trend": forecast['trend'].tolist()
            }
            
        except Exception as e:
            logging.error(f"Error in Prophet forecast: {str(e)}")
            return {}
    
    def _lstm_forecast(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate forecast using LSTM."""
        try:
            # Prepare data
            data = df['usage'].values.reshape(-1, 1)
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data)
            
            # Create sequences
            X, y = self._create_sequences(scaled_data)
            
            # Build LSTM model
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # Train model
            model.fit(X, y, epochs=50, batch_size=32, verbose=0)
            
            # Generate forecast
            last_sequence = scaled_data[-X.shape[1]:]
            forecast = []
            for _ in range(24):
                next_pred = model.predict(last_sequence.reshape(1, X.shape[1], 1))
                forecast.append(next_pred[0][0])
                last_sequence = np.append(last_sequence[1:], next_pred)
            
            # Inverse transform
            forecast = scaler.inverse_transform(np.array(forecast).reshape(-1, 1))
            
            return {
                "model": "lstm",
                "forecast": forecast.tolist()
            }
            
        except Exception as e:
            logging.error(f"Error in LSTM forecast: {str(e)}")
            return {}
    
    def _xgboost_forecast(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate forecast using XGBoost."""
        try:
            # Prepare features
            df['hour'] = df['timestamp'].dt.hour
            df['day'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            
            # Create sequences
            X, y = self._create_sequences(df[['usage', 'hour', 'day', 'month']].values)
            
            # Train model
            model = XGBRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            model.fit(X.reshape(X.shape[0], -1), y)
            
            # Generate forecast
            last_sequence = df[['usage', 'hour', 'day', 'month']].values[-X.shape[1]:]
            forecast = []
            for i in range(24):
                next_hour = (df['hour'].iloc[-1] + i + 1) % 24
                next_day = (df['day'].iloc[-1] + (i + 1) // 24) % 7
                next_month = df['month'].iloc[-1]
                
                next_features = np.append(last_sequence[1:], [[forecast[-1][0] if forecast else df['usage'].iloc[-1],
                                                             next_hour,
                                                             next_day,
                                                             next_month]])
                
                next_pred = model.predict(next_features.reshape(1, -1))
                forecast.append([next_pred[0]])
                last_sequence = next_features
            
            return {
                "model": "xgboost",
                "forecast": [f[0] for f in forecast]
            }
            
        except Exception as e:
            logging.error(f"Error in XGBoost forecast: {str(e)}")
            return {}
    
    def _create_sequences(self, data: np.ndarray, seq_length: int = 24) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for time series prediction."""
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:(i + seq_length)])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)
    
    def _combine_forecasts(self,
                          prophet_forecast: Dict[str, Any],
                          lstm_forecast: Dict[str, Any],
                          xgb_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Combine forecasts from multiple models."""
        try:
            # Get forecasts
            prophet_values = [f["yhat"] for f in prophet_forecast.get("forecast", [])]
            lstm_values = lstm_forecast.get("forecast", [])
            xgb_values = xgb_forecast.get("forecast", [])
            
            # Calculate weights based on model performance
            weights = self._calculate_model_weights(prophet_values, lstm_values, xgb_values)
            
            # Combine forecasts
            combined = []
            for i in range(24):
                combined_value = (
                    weights["prophet"] * prophet_values[i] +
                    weights["lstm"] * lstm_values[i] +
                    weights["xgboost"] * xgb_values[i]
                )
                combined.append(combined_value)
            
            return {
                "forecast": combined,
                "weights": weights
            }
            
        except Exception as e:
            logging.error(f"Error combining forecasts: {str(e)}")
            return {}
    
    def _calculate_model_weights(self,
                                prophet_values: List[float],
                                lstm_values: List[float],
                                xgb_values: List[float]) -> Dict[str, float]:
        """Calculate weights for model combination."""
        try:
            # Calculate model errors
            prophet_error = np.mean(np.abs(np.diff(prophet_values)))
            lstm_error = np.mean(np.abs(np.diff(lstm_values)))
            xgb_error = np.mean(np.abs(np.diff(xgb_values)))
            
            # Calculate weights (inverse of errors)
            total_error = prophet_error + lstm_error + xgb_error
            if total_error == 0:
                return {"prophet": 0.33, "lstm": 0.33, "xgboost": 0.34}
            
            weights = {
                "prophet": 1 - (prophet_error / total_error),
                "lstm": 1 - (lstm_error / total_error),
                "xgboost": 1 - (xgb_error / total_error)
            }
            
            # Normalize weights
            total_weight = sum(weights.values())
            return {k: v/total_weight for k, v in weights.items()}
            
        except Exception as e:
            logging.error(f"Error calculating model weights: {str(e)}")
            return {"prophet": 0.33, "lstm": 0.33, "xgboost": 0.34}
    
    def _calculate_cache_efficiency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate cache efficiency metrics."""
        try:
            # Calculate cache utilization
            utilization = df['cache_usage'].mean() / df['cache_usage'].max() if df['cache_usage'].max() > 0 else 0
            
            # Calculate hit rate
            hit_rate = df['cache_hit_rate'].mean()
            
            # Calculate miss rate
            miss_rate = df['cache_miss_rate'].mean()
            
            # Calculate cache effectiveness
            effectiveness = self._calculate_cache_effectiveness(df)
            
            return {
                "utilization": utilization,
                "hit_rate": hit_rate,
                "miss_rate": miss_rate,
                "effectiveness": effectiveness
            }
            
        except Exception as e:
            logging.error(f"Error calculating cache efficiency: {str(e)}")
            return {}
    
    def _calculate_cache_effectiveness(self, df: pd.DataFrame) -> float:
        """Calculate cache effectiveness score."""
        try:
            # Calculate hit rate stability
            hit_stability = 1 - (df['cache_hit_rate'].std() / df['cache_hit_rate'].mean() if df['cache_hit_rate'].mean() > 0 else 0)
            
            # Calculate usage stability
            usage_stability = 1 - (df['cache_usage'].std() / df['cache_usage'].mean() if df['cache_usage'].mean() > 0 else 0)
            
            # Combine metrics
            effectiveness = (hit_stability + usage_stability) / 2
            
            return effectiveness
            
        except Exception as e:
            logging.error(f"Error calculating cache effectiveness: {str(e)}")
            return 0
    
    def _calculate_optimal_cache(self,
                                current_usage: float,
                                patterns: Dict[str, Any],
                                forecast: Dict[str, Any],
                                constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal cache allocation."""
        try:
            # Get current cache patterns
            current_hour = datetime.now().hour
            current_day = datetime.now().dayofweek
            
            # Get pattern-based adjustment
            hour_cache = patterns.get("daily_cache", {}).get(current_hour, 0)
            day_cache = patterns.get("weekly_cache", {}).get(current_day, 0)
            
            # Get forecast-based adjustment
            forecast_values = forecast.get("forecast", [])
            if forecast_values:
                next_hour_forecast = forecast_values[0]
                forecast_adjustment = next_hour_forecast / current_usage if current_usage > 0 else 1.0
            else:
                forecast_adjustment = 1.0
            
            # Calculate optimal amount with cache buffer
            cache_buffer = 1.2  # 20% buffer for cache spikes
            optimal = current_usage * (1 + hour_cache + day_cache) * forecast_adjustment * cache_buffer
            
            # Apply constraints
            optimal = min(optimal, constraints.get("max", float('inf')))
            optimal = max(optimal, constraints.get("min", 0))
            
            # Calculate confidence
            confidence = self._calculate_cache_confidence(
                patterns,
                forecast,
                optimal,
                current_usage
            )
            
            # Generate reasoning
            reasoning = self._generate_cache_reasoning(
                optimal,
                current_usage,
                patterns,
                forecast
            )
            
            return {
                "amount": optimal,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logging.error(f"Error calculating optimal cache: {str(e)}")
            return {
                "amount": current_usage,
                "confidence": 0.5,
                "reasoning": "Error in calculation"
            }
    
    def _calculate_cache_confidence(self,
                                   patterns: Dict[str, Any],
                                   forecast: Dict[str, Any],
                                   optimal: float,
                                   current: float) -> float:
        """Calculate confidence in the cache optimization decision."""
        try:
            # Pattern consistency
            cache_std = np.std(list(patterns.get("daily_cache", {}).values()))
            pattern_confidence = 1 - (cache_std / abs(np.mean(list(patterns.get("daily_cache", {}).values()))) if np.mean(list(patterns.get("daily_cache", {}).values())) != 0 else 0.5)
            
            # Forecast confidence
            if forecast.get("forecast"):
                forecast_std = np.std(forecast["forecast"])
                forecast_confidence = 1 - (forecast_std / np.mean(forecast["forecast"]))
            else:
                forecast_confidence = 0.5
            
            # Effectiveness confidence
            efficiency = patterns.get("efficiency", {})
            effectiveness_confidence = efficiency.get("effectiveness", 0.5)
            
            # Combine confidences
            confidence = (pattern_confidence + forecast_confidence + effectiveness_confidence) / 3
            return max(0, min(1, confidence))
            
        except Exception as e:
            logging.error(f"Error calculating cache confidence: {str(e)}")
            return 0.5
    
    def _generate_cache_reasoning(self,
                                 optimal: float,
                                 current: float,
                                 patterns: Dict[str, Any],
                                 forecast: Dict[str, Any]) -> str:
        """Generate reasoning for the cache optimization decision."""
        try:
            reasons = []
            
            # Cache pattern reasoning
            if patterns.get("daily_cache"):
                current_hour = datetime.now().hour
                hour_cache = patterns["daily_cache"].get(current_hour, 0)
                if hour_cache > 0.1:
                    reasons.append(f"High cache usage expected for current hour ({hour_cache:.2f})")
                elif hour_cache < -0.1:
                    reasons.append(f"Low cache usage expected for current hour ({hour_cache:.2f})")
            
            # Forecast reasoning
            if forecast.get("forecast"):
                next_hour_forecast = forecast["forecast"][0]
                if next_hour_forecast > current * 1.1:
                    reasons.append(f"Forecast predicts cache increase ({next_hour_forecast:.2f})")
                elif next_hour_forecast < current * 0.9:
                    reasons.append(f"Forecast predicts cache decrease ({next_hour_forecast:.2f})")
            
            # Efficiency reasoning
            efficiency = patterns.get("efficiency", {})
            if efficiency.get("effectiveness", 0) < 0.5:
                reasons.append("Low cache effectiveness detected")
            
            # Change magnitude reasoning
            change_percent = ((optimal - current) / current) * 100 if current > 0 else 0
            if abs(change_percent) > 10:
                reasons.append(f"Significant change recommended ({change_percent:.1f}%)")
            
            return " | ".join(reasons) if reasons else "No significant changes needed"
            
        except Exception as e:
            logging.error(f"Error generating cache reasoning: {str(e)}")
            return "Error generating reasoning"

class LoadBalancerOptimizationStrategy(OptimizationStrategy):
    """Strategy for optimizing load balancer resources."""
    
    def optimize_allocation(self,
                          current_usage: float,
                          historical_data: List[Dict[str, Any]],
                          constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize load balancer resource allocation."""
        try:
            # Analyze load balancer patterns
            lb_patterns = self._analyze_lb_patterns(historical_data)
            
            # Predict load balancer usage
            usage_forecast = self._predict_lb_usage(historical_data)
            
            # Calculate optimal allocation
            optimal_allocation = self._calculate_optimal_lb(
                current_usage,
                lb_patterns,
                usage_forecast,
                constraints
            )
            
            return {
                "amount": optimal_allocation["amount"],
                "confidence": optimal_allocation["confidence"],
                "reasoning": optimal_allocation["reasoning"]
            }
            
        except Exception as e:
            logging.error(f"Error optimizing load balancer allocation: {str(e)}")
            return {"amount": current_usage, "confidence": 0.5, "reasoning": "Error in optimization"}
    
    def _analyze_lb_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze load balancer usage patterns."""
        try:
            # Convert to time series
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate load balancer patterns
            df['lb_usage'] = df['usage']
            df['lb_connections'] = df.get('connections', 0)
            df['lb_throughput'] = df.get('throughput', 0)
            
            # Calculate daily load balancer patterns
            daily_lb = df.groupby(df['timestamp'].dt.hour)['lb_usage'].mean()
            
            # Calculate weekly load balancer patterns
            weekly_lb = df.groupby(df['timestamp'].dt.dayofweek)['lb_usage'].mean()
            
            # Calculate load balancer efficiency metrics
            efficiency = self._calculate_lb_efficiency(df)
            
            return {
                "daily_lb": daily_lb.to_dict(),
                "weekly_lb": weekly_lb.to_dict(),
                "efficiency": efficiency
            }
            
        except Exception as e:
            logging.error(f"Error analyzing load balancer patterns: {str(e)}")
            return {}
    
    def _predict_lb_usage(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future load balancer usage using multiple models."""
        try:
            # Prepare data
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Prophet forecast
            prophet_forecast = self._prophet_forecast(df)
            
            # LSTM forecast
            lstm_forecast = self._lstm_forecast(df)
            
            # XGBoost forecast
            xgb_forecast = self._xgboost_forecast(df)
            
            # Combine forecasts with weights
            combined_forecast = self._combine_forecasts(
                prophet_forecast,
                lstm_forecast,
                xgb_forecast
            )
            
            return combined_forecast
            
        except Exception as e:
            logging.error(f"Error predicting load balancer usage: {str(e)}")
            return {}
    
    def _calculate_lb_efficiency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate load balancer efficiency metrics."""
        try:
            # Calculate load balancer utilization
            utilization = df['lb_usage'].mean() / df['lb_usage'].max() if df['lb_usage'].max() > 0 else 0
            
            # Calculate connection efficiency
            connection_efficiency = df['lb_connections'].mean() / df['lb_connections'].max() if df['lb_connections'].max() > 0 else 0
            
            # Calculate throughput efficiency
            throughput_efficiency = df['lb_throughput'].mean() / df['lb_throughput'].max() if df['lb_throughput'].max() > 0 else 0
            
            # Calculate load balancer performance
            performance = self._calculate_lb_performance(df)
            
            return {
                "utilization": utilization,
                "connection_efficiency": connection_efficiency,
                "throughput_efficiency": throughput_efficiency,
                "performance": performance
            }
            
        except Exception as e:
            logging.error(f"Error calculating load balancer efficiency: {str(e)}")
            return {}
    
    def _calculate_lb_performance(self, df: pd.DataFrame) -> float:
        """Calculate load balancer performance score."""
        try:
            # Calculate usage stability
            usage_stability = 1 - (df['lb_usage'].std() / df['lb_usage'].mean() if df['lb_usage'].mean() > 0 else 0)
            
            # Calculate connection stability
            connection_stability = 1 - (df['lb_connections'].std() / df['lb_connections'].mean() if df['lb_connections'].mean() > 0 else 0)
            
            # Calculate throughput stability
            throughput_stability = 1 - (df['lb_throughput'].std() / df['lb_throughput'].mean() if df['lb_throughput'].mean() > 0 else 0)
            
            # Combine performance metrics
            performance = (usage_stability + connection_stability + throughput_stability) / 3
            
            return performance
            
        except Exception as e:
            logging.error(f"Error calculating load balancer performance: {str(e)}")
            return 0
    
    def _calculate_optimal_lb(self,
                             current_usage: float,
                             patterns: Dict[str, Any],
                             forecast: Dict[str, Any],
                             constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal load balancer allocation."""
        try:
            # Get current load balancer patterns
            current_hour = datetime.now().hour
            current_day = datetime.now().dayofweek
            
            # Get pattern-based adjustment
            hour_lb = patterns.get("daily_lb", {}).get(current_hour, 0)
            day_lb = patterns.get("weekly_lb", {}).get(current_day, 0)
            
            # Get forecast-based adjustment
            forecast_values = forecast.get("forecast", [])
            if forecast_values:
                next_hour_forecast = forecast_values[-1]["yhat"]
                forecast_adjustment = next_hour_forecast / current_usage if current_usage > 0 else 1.0
            else:
                forecast_adjustment = 1.0
            
            # Calculate optimal amount with load balancer buffer
            lb_buffer = 1.3  # 30% buffer for load balancer spikes
            optimal = current_usage * (1 + hour_lb + day_lb) * forecast_adjustment * lb_buffer
            
            # Apply constraints
            optimal = min(optimal, constraints.get("max", float('inf')))
            optimal = max(optimal, constraints.get("min", 0))
            
            # Calculate confidence
            confidence = self._calculate_lb_confidence(
                patterns,
                forecast,
                optimal,
                current_usage
            )
            
            # Generate reasoning
            reasoning = self._generate_lb_reasoning(
                optimal,
                current_usage,
                patterns,
                forecast
            )
            
            return {
                "amount": optimal,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logging.error(f"Error calculating optimal load balancer: {str(e)}")
            return {
                "amount": current_usage,
                "confidence": 0.5,
                "reasoning": "Error in calculation"
            }
    
    def _calculate_lb_confidence(self,
                                patterns: Dict[str, Any],
                                forecast: Dict[str, Any],
                                optimal: float,
                                current: float) -> float:
        """Calculate confidence in the load balancer optimization decision."""
        try:
            # Pattern consistency
            lb_std = np.std(list(patterns.get("daily_lb", {}).values()))
            pattern_confidence = 1 - (lb_std / abs(np.mean(list(patterns.get("daily_lb", {}).values()))) if np.mean(list(patterns.get("daily_lb", {}).values())) != 0 else 0.5)
            
            # Forecast confidence
            if forecast.get("forecast"):
                forecast_std = np.std([f["yhat_upper"] - f["yhat_lower"] for f in forecast["forecast"]])
                forecast_confidence = 1 - (forecast_std / np.mean([f["yhat"] for f in forecast["forecast"]]))
            else:
                forecast_confidence = 0.5
            
            # Performance confidence
            efficiency = patterns.get("efficiency", {})
            performance_confidence = efficiency.get("performance", 0.5)
            
            # Combine confidences
            confidence = (pattern_confidence + forecast_confidence + performance_confidence) / 3
            return max(0, min(1, confidence))
            
        except Exception as e:
            logging.error(f"Error calculating load balancer confidence: {str(e)}")
            return 0.5
    
    def _generate_lb_reasoning(self,
                              optimal: float,
                              current: float,
                              patterns: Dict[str, Any],
                              forecast: Dict[str, Any]) -> str:
        """Generate reasoning for the load balancer optimization decision."""
        try:
            reasons = []
            
            # Load balancer pattern reasoning
            if patterns.get("daily_lb"):
                current_hour = datetime.now().hour
                hour_lb = patterns["daily_lb"].get(current_hour, 0)
                if hour_lb > 0.1:
                    reasons.append(f"High load balancer usage expected for current hour ({hour_lb:.2f})")
                elif hour_lb < -0.1:
                    reasons.append(f"Low load balancer usage expected for current hour ({hour_lb:.2f})")
            
            # Forecast reasoning
            if forecast.get("forecast"):
                next_hour_forecast = forecast["forecast"][-1]["yhat"]
                if next_hour_forecast > current * 1.1:
                    reasons.append(f"Forecast predicts load balancer increase ({next_hour_forecast:.2f})")
                elif next_hour_forecast < current * 0.9:
                    reasons.append(f"Forecast predicts load balancer decrease ({next_hour_forecast:.2f})")
            
            # Performance reasoning
            efficiency = patterns.get("efficiency", {})
            if efficiency.get("utilization", 0) > 0.8:
                reasons.append("High load balancer utilization detected")
            if efficiency.get("performance", 0) < 0.5:
                reasons.append("Low load balancer performance detected")
            
            # Change magnitude reasoning
            change_percent = ((optimal - current) / current) * 100 if current > 0 else 0
            if abs(change_percent) > 10:
                reasons.append(f"Significant change recommended ({change_percent:.1f}%)")
            
            return " | ".join(reasons) if reasons else "No significant changes needed"
            
        except Exception as e:
            logging.error(f"Error generating load balancer reasoning: {str(e)}")
            return "Error generating reasoning"

class QueueOptimizationStrategy(OptimizationStrategy):
    """Strategy for optimizing queue resources."""
    
    def optimize_allocation(self,
                          current_usage: float,
                          historical_data: List[Dict[str, Any]],
                          constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize queue resource allocation."""
        try:
            # Analyze queue patterns
            queue_patterns = self._analyze_queue_patterns(historical_data)
            
            # Predict queue usage
            usage_forecast = self._predict_queue_usage(historical_data)
            
            # Calculate optimal allocation
            optimal_allocation = self._calculate_optimal_queue(
                current_usage,
                queue_patterns,
                usage_forecast,
                constraints
            )
            
            return {
                "amount": optimal_allocation["amount"],
                "confidence": optimal_allocation["confidence"],
                "reasoning": optimal_allocation["reasoning"]
            }
            
        except Exception as e:
            logging.error(f"Error optimizing queue allocation: {str(e)}")
            return {"amount": current_usage, "confidence": 0.5, "reasoning": "Error in optimization"}
    
    def _analyze_queue_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze queue usage patterns."""
        try:
            # Convert to time series
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate queue patterns
            df['queue_usage'] = df['usage']
            df['queue_length'] = df.get('length', 0)
            df['queue_processing_rate'] = df.get('processing_rate', 0)
            
            # Calculate daily queue patterns
            daily_queue = df.groupby(df['timestamp'].dt.hour)['queue_usage'].mean()
            
            # Calculate weekly queue patterns
            weekly_queue = df.groupby(df['timestamp'].dt.dayofweek)['queue_usage'].mean()
            
            # Calculate queue efficiency metrics
            efficiency = self._calculate_queue_efficiency(df)
            
            return {
                "daily_queue": daily_queue.to_dict(),
                "weekly_queue": weekly_queue.to_dict(),
                "efficiency": efficiency
            }
            
        except Exception as e:
            logging.error(f"Error analyzing queue patterns: {str(e)}")
            return {}
    
    def _predict_queue_usage(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future queue usage using multiple models."""
        try:
            # Prepare data
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Prophet forecast
            prophet_forecast = self._prophet_forecast(df)
            
            # LSTM forecast
            lstm_forecast = self._lstm_forecast(df)
            
            # XGBoost forecast
            xgb_forecast = self._xgboost_forecast(df)
            
            # Combine forecasts with weights
            combined_forecast = self._combine_forecasts(
                prophet_forecast,
                lstm_forecast,
                xgb_forecast
            )
            
            return combined_forecast
            
        except Exception as e:
            logging.error(f"Error predicting queue usage: {str(e)}")
            return {}
    
    def _calculate_queue_efficiency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate queue efficiency metrics."""
        try:
            # Calculate queue utilization
            utilization = df['queue_usage'].mean() / df['queue_usage'].max() if df['queue_usage'].max() > 0 else 0
            
            # Calculate queue length efficiency
            length_efficiency = df['queue_length'].mean() / df['queue_length'].max() if df['queue_length'].max() > 0 else 0
            
            # Calculate processing rate efficiency
            processing_efficiency = df['queue_processing_rate'].mean() / df['queue_processing_rate'].max() if df['queue_processing_rate'].max() > 0 else 0
            
            # Calculate queue performance
            performance = self._calculate_queue_performance(df)
            
            return {
                "utilization": utilization,
                "length_efficiency": length_efficiency,
                "processing_efficiency": processing_efficiency,
                "performance": performance
            }
            
        except Exception as e:
            logging.error(f"Error calculating queue efficiency: {str(e)}")
            return {}
    
    def _calculate_queue_performance(self, df: pd.DataFrame) -> float:
        """Calculate queue performance score."""
        try:
            # Calculate usage stability
            usage_stability = 1 - (df['queue_usage'].std() / df['queue_usage'].mean() if df['queue_usage'].mean() > 0 else 0)
            
            # Calculate length stability
            length_stability = 1 - (df['queue_length'].std() / df['queue_length'].mean() if df['queue_length'].mean() > 0 else 0)
            
            # Calculate processing rate stability
            processing_stability = 1 - (df['queue_processing_rate'].std() / df['queue_processing_rate'].mean() if df['queue_processing_rate'].mean() > 0 else 0)
            
            # Combine performance metrics
            performance = (usage_stability + length_stability + processing_stability) / 3
            
            return performance
            
        except Exception as e:
            logging.error(f"Error calculating queue performance: {str(e)}")
            return 0
    
    def _calculate_optimal_queue(self,
                                current_usage: float,
                                patterns: Dict[str, Any],
                                forecast: Dict[str, Any],
                                constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal queue allocation."""
        try:
            # Get current queue patterns
            current_hour = datetime.now().hour
            current_day = datetime.now().dayofweek
            
            # Get pattern-based adjustment
            hour_queue = patterns.get("daily_queue", {}).get(current_hour, 0)
            day_queue = patterns.get("weekly_queue", {}).get(current_day, 0)
            
            # Get forecast-based adjustment
            forecast_values = forecast.get("forecast", [])
            if forecast_values:
                next_hour_forecast = forecast_values[-1]["yhat"]
                forecast_adjustment = next_hour_forecast / current_usage if current_usage > 0 else 1.0
            else:
                forecast_adjustment = 1.0
            
            # Calculate optimal amount with queue buffer
            queue_buffer = 1.4  # 40% buffer for queue spikes
            optimal = current_usage * (1 + hour_queue + day_queue) * forecast_adjustment * queue_buffer
            
            # Apply constraints
            optimal = min(optimal, constraints.get("max", float('inf')))
            optimal = max(optimal, constraints.get("min", 0))
            
            # Calculate confidence
            confidence = self._calculate_queue_confidence(
                patterns,
                forecast,
                optimal,
                current_usage
            )
            
            # Generate reasoning
            reasoning = self._generate_queue_reasoning(
                optimal,
                current_usage,
                patterns,
                forecast
            )
            
            return {
                "amount": optimal,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logging.error(f"Error calculating optimal queue: {str(e)}")
            return {
                "amount": current_usage,
                "confidence": 0.5,
                "reasoning": "Error in calculation"
            }
    
    def _calculate_queue_confidence(self,
                                   patterns: Dict[str, Any],
                                   forecast: Dict[str, Any],
                                   optimal: float,
                                   current: float) -> float:
        """Calculate confidence in the queue optimization decision."""
        try:
            # Pattern consistency
            queue_std = np.std(list(patterns.get("daily_queue", {}).values()))
            pattern_confidence = 1 - (queue_std / abs(np.mean(list(patterns.get("daily_queue", {}).values()))) if np.mean(list(patterns.get("daily_queue", {}).values())) != 0 else 0.5)
            
            # Forecast confidence
            if forecast.get("forecast"):
                forecast_std = np.std([f["yhat_upper"] - f["yhat_lower"] for f in forecast["forecast"]])
                forecast_confidence = 1 - (forecast_std / np.mean([f["yhat"] for f in forecast["forecast"]]))
            else:
                forecast_confidence = 0.5
            
            # Performance confidence
            efficiency = patterns.get("efficiency", {})
            performance_confidence = efficiency.get("performance", 0.5)
            
            # Combine confidences
            confidence = (pattern_confidence + forecast_confidence + performance_confidence) / 3
            return max(0, min(1, confidence))
            
        except Exception as e:
            logging.error(f"Error calculating queue confidence: {str(e)}")
            return 0.5
    
    def _generate_queue_reasoning(self,
                                 optimal: float,
                                 current: float,
                                 patterns: Dict[str, Any],
                                 forecast: Dict[str, Any]) -> str:
        """Generate reasoning for the queue optimization decision."""
        try:
            reasons = []
            
            # Queue pattern reasoning
            if patterns.get("daily_queue"):
                current_hour = datetime.now().hour
                hour_queue = patterns["daily_queue"].get(current_hour, 0)
                if hour_queue > 0.1:
                    reasons.append(f"High queue usage expected for current hour ({hour_queue:.2f})")
                elif hour_queue < -0.1:
                    reasons.append(f"Low queue usage expected for current hour ({hour_queue:.2f})")
            
            # Forecast reasoning
            if forecast.get("forecast"):
                next_hour_forecast = forecast["forecast"][-1]["yhat"]
                if next_hour_forecast > current * 1.1:
                    reasons.append(f"Forecast predicts queue increase ({next_hour_forecast:.2f})")
                elif next_hour_forecast < current * 0.9:
                    reasons.append(f"Forecast predicts queue decrease ({next_hour_forecast:.2f})")
            
            # Performance reasoning
            efficiency = patterns.get("efficiency", {})
            if efficiency.get("utilization", 0) > 0.8:
                reasons.append("High queue utilization detected")
            if efficiency.get("performance", 0) < 0.5:
                reasons.append("Low queue performance detected")
            
            # Change magnitude reasoning
            change_percent = ((optimal - current) / current) * 100 if current > 0 else 0
            if abs(change_percent) > 10:
                reasons.append(f"Significant change recommended ({change_percent:.1f}%)")
            
            return " | ".join(reasons) if reasons else "No significant changes needed"
            
        except Exception as e:
            logging.error(f"Error generating queue reasoning: {str(e)}")
            return "Error generating reasoning"

class ResourceOptimizationFactory:
    """Factory for creating resource-specific optimization strategies."""
    
    @staticmethod
    def create_strategy(resource_type: str) -> OptimizationStrategy:
        """Create appropriate optimization strategy for the resource type."""
        strategies = {
            "compute": ComputeOptimizationStrategy(),
            "storage": StorageOptimizationStrategy(),
            "network": NetworkOptimizationStrategy(),
            "memory": MemoryOptimizationStrategy(),
            "gpu": GPUOptimizationStrategy(),
            "database": DatabaseOptimizationStrategy(),
            "cache": CacheOptimizationStrategy(),
            "load_balancer": LoadBalancerOptimizationStrategy(),
            "queue": QueueOptimizationStrategy()
        }
        return strategies.get(resource_type, OptimizationStrategy()) 