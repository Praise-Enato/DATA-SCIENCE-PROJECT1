"""
src/analysis.py
Statistical analysis functions.
"""

import pandas as pd

def compute_correlation(df: pd.DataFrame, x: str='TMAX', y: str='demand') -> float:
    """Return Pearson’s r between two columns."""
    return df[x].corr(df[y])

def weekday_vs_weekend(df: pd.DataFrame) -> dict:
    """Return average demand & temp on weekdays vs weekends."""
    df = df.copy()
    df['is_weekend'] = df['date'].dt.dayofweek >= 5
    stats = {}
    for key, grp in df.groupby('is_weekend'):
        label = 'weekend' if key else 'weekday'
        stats[label] = {
            'avg_temp': grp['TMAX'].mean(),
            'avg_demand': grp['demand'].mean()
        }
    return stats
