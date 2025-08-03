import pytest
import pandas as pd
from datetime import datetime
from src.data_processor import clean_weather, clean_energy, merge_weather_energy

@pytest.fixture
def sample_weather_data():
    return pd.DataFrame({
        'date': ['2025-01-01', '2025-01-02', '2025-01-02', None],
        'TMAX': [100, 102, 102, 103],
        'TMIN': [50, 52, 52, 53]
    })

@pytest.fixture
def sample_energy_data():
    return pd.DataFrame({
        'date': ['2025-01-01', '2025-01-02', '2025-01-03'],
        'demand': [1000, 1100, 1200]
    })

def test_clean_weather(sample_weather_data):
    df = clean_weather(sample_weather_data)
    assert len(df) == 2  # Should remove duplicate and None dates
    assert df['date'].isna().sum() == 0
    assert df['TMAX'].iloc[0] == 100

def test_clean_energy(sample_energy_data):
    df = clean_energy(sample_energy_data)
    assert len(df) == 3
    assert df['date'].isna().sum() == 0
    assert df['demand'].iloc[0] == 1000

def test_merge_weather_energy(sample_weather_data, sample_energy_data):
    weather = clean_weather(sample_weather_data)
    energy = clean_energy(sample_energy_data)
    merged = merge_weather_energy(weather, energy)
    assert len(merged) == 2  # Only matching dates
    assert set(merged.columns) == {'date', 'TMAX', 'TMIN', 'demand'}