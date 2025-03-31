import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta

def preprocess_learning_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess learning data by extracting features and cleaning the data.
    
    Args:
        data: DataFrame containing learning data
        
    Returns:
        pd.DataFrame: Preprocessed data with additional features
    """
    # Create a copy to avoid modifying the original data
    df = data.copy()
    
    # Convert timestamp to datetime if it's not already
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract time-based features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    
    # Extract features from context
    if 'context' in df.columns:
        # Assuming context is a JSON string or dictionary
        if isinstance(df['context'].iloc[0], str):
            df['context'] = df['context'].apply(eval)
        
        # Extract specific features from context
        df['session_duration'] = df['context'].apply(
            lambda x: x.get('session_duration', 0)
        )
        df['previous_actions'] = df['context'].apply(
            lambda x: x.get('previous_actions', [])
        )
        df['user_level'] = df['context'].apply(
            lambda x: x.get('user_level', 1)
        )
    
    # Create action-based features
    action_counts = df.groupby('user_id')['action'].value_counts().unstack(fill_value=0)
    df = df.merge(action_counts, on='user_id', how='left')
    
    # Create time-based features
    df['time_since_last_action'] = df.groupby('user_id')['timestamp'].diff().dt.total_seconds()
    
    # Create features dictionary
    df['features'] = df.apply(
        lambda row: {
            'time_features': {
                'hour': row['hour'],
                'day_of_week': row['day_of_week'],
                'month': row['month'],
                'time_since_last_action': row['time_since_last_action']
            },
            'user_features': {
                'user_level': row['user_level'],
                'session_duration': row['session_duration']
            },
            'action_features': {
                'previous_actions': row['previous_actions']
            }
        },
        axis=1
    )
    
    # Drop intermediate columns
    columns_to_drop = [
        'hour', 'day_of_week', 'month', 'session_duration',
        'previous_actions', 'user_level', 'time_since_last_action'
    ]
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
    
    return df

def aggregate_model_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate model metrics over time windows.
    
    Args:
        data: DataFrame containing model metrics
        
    Returns:
        pd.DataFrame: Aggregated metrics
    """
    # Create a copy to avoid modifying the original data
    df = data.copy()
    
    # Convert timestamp to datetime if it's not already
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Define time windows for aggregation
    windows = {
        '1h': '1H',
        '6h': '6H',
        '24h': '24H',
        '7d': '7D'
    }
    
    # Initialize aggregated metrics dictionary
    aggregated_metrics = {}
    
    # Aggregate metrics for each time window
    for window_name, window_size in windows.items():
        window_metrics = df.groupby(['model_id', pd.Grouper(key='timestamp', freq=window_size)])[
            'value'
        ].agg(['mean', 'std', 'min', 'max', 'count']).reset_index()
        
        # Rename columns to include window size
        window_metrics.columns = [
            f"{col}_{window_name}" if col != 'model_id' and col != 'timestamp'
            else col
            for col in window_metrics.columns
        ]
        
        aggregated_metrics[window_name] = window_metrics
    
    # Merge all window metrics
    result = aggregated_metrics['1h']  # Start with 1-hour window
    for window_name in ['6h', '24h', '7d']:
        result = result.merge(
            aggregated_metrics[window_name],
            on=['model_id', 'timestamp'],
            how='outer'
        )
    
    # Create metrics dictionary
    result['aggregated_metrics'] = result.apply(
        lambda row: {
            '1h': {
                'mean': row['mean_1h'],
                'std': row['std_1h'],
                'min': row['min_1h'],
                'max': row['max_1h'],
                'count': row['count_1h']
            },
            '6h': {
                'mean': row['mean_6h'],
                'std': row['std_6h'],
                'min': row['min_6h'],
                'max': row['max_6h'],
                'count': row['count_6h']
            },
            '24h': {
                'mean': row['mean_24h'],
                'std': row['std_24h'],
                'min': row['min_24h'],
                'max': row['max_24h'],
                'count': row['count_24h']
            },
            '7d': {
                'mean': row['mean_7d'],
                'std': row['std_7d'],
                'min': row['min_7d'],
                'max': row['max_7d'],
                'count': row['count_7d']
            }
        },
        axis=1
    )
    
    # Drop intermediate columns
    columns_to_drop = [
        col for col in result.columns
        if any(window in col for window in ['1h', '6h', '24h', '7d'])
        and col != 'aggregated_metrics'
    ]
    result = result.drop(columns=columns_to_drop)
    
    return result

def merge_learning_and_metrics(
    learning_data: pd.DataFrame,
    metrics_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge learning data with model metrics.
    
    Args:
        learning_data: DataFrame containing preprocessed learning data
        metrics_data: DataFrame containing aggregated model metrics
        
    Returns:
        pd.DataFrame: Merged data
    """
    # Create a copy to avoid modifying the original data
    df = learning_data.copy()
    
    # Convert timestamps to datetime if they're not already
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    metrics_data['timestamp'] = pd.to_datetime(metrics_data['timestamp'])
    
    # Merge data based on timestamp
    # Use a time window of 1 hour for the merge
    df['merge_timestamp'] = df['timestamp'].dt.floor('H')
    metrics_data['merge_timestamp'] = metrics_data['timestamp'].dt.floor('H')
    
    # Merge the data
    result = df.merge(
        metrics_data,
        on=['merge_timestamp'],
        how='left',
        suffixes=('', '_metrics')
    )
    
    # Drop merge timestamp and duplicate columns
    result = result.drop(columns=['merge_timestamp'])
    if 'timestamp_metrics' in result.columns:
        result = result.drop(columns=['timestamp_metrics'])
    
    # Add model metrics to features
    result['features'] = result.apply(
        lambda row: {
            **row['features'],
            'model_metrics': row['aggregated_metrics']
        },
        axis=1
    )
    
    # Drop the aggregated_metrics column as it's now part of features
    result = result.drop(columns=['aggregated_metrics'])
    
    return result 