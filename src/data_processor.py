"""
src/data_processor.py
Cleaning and transformation of raw weather & energy data.
"""

import pandas as pd
from typing import Optional

def clean_weather(df: pd.DataFrame, interpolate: bool = False) -> pd.DataFrame:
    """
    Clean weather data by handling dates and duplicates.
    
    Args:
        df: Input weather DataFrame
        interpolate: Whether to interpolate missing daily values
    
    Returns:
        Cleaned DataFrame with proper date handling
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])  # drop invalid dates
    df = df.drop_duplicates(subset=['date'])
    
    if interpolate:
        df = df.set_index('date').resample('D').interpolate(limit=2).reset_index()
        
    return df

def clean_energy(df: pd.DataFrame, interpolate: bool = False) -> pd.DataFrame:
    """
    Clean energy data by handling dates and duplicates.
    
    Args:
        df: Input energy DataFrame
        interpolate: Whether to interpolate missing daily values
    
    Returns:
        Cleaned DataFrame with proper date handling
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])  # drop invalid dates
    df = df.drop_duplicates(subset=['date'])
    
    if interpolate:
        df = df.set_index('date').resample('D').interpolate(limit=2).reset_index()
        
    return df

def merge_weather_energy(df_w: pd.DataFrame, df_e: pd.DataFrame) -> pd.DataFrame:
    """
    Merge weather and energy data on date column.
    
    Args:
        df_w: Weather DataFrame with 'date' column
        df_e: Energy DataFrame with 'date' column
    
    Returns:
        Merged DataFrame containing only dates present in both datasets
    """
    return pd.merge(df_w, df_e, on='date', how='inner')
