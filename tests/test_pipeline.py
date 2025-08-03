# tests/test_pipeline.py

import pytest
import pandas as pd
from pathlib import Path

# Now these imports will work, thanks to conftest.py
from pipeline import load_config
from data_processor import clean_weather, clean_energy, merge_weather_energy
from data_fetcher import fetch_historical_weather

def test_load_config(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "noaa_token: A\n"
        "eia_key: B\n"
        "fetch_days: 90\n"
        "cities: []\n"
    )

    result = load_config(str(cfg))
    assert result["noaa_token"] == "A"
    assert result["eia_key"] == "B"
    assert result["fetch_days"] == 90
    assert result["cities"] == []

def test_clean_merge():
    df_w = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-01", "bad"],
        "TMAX": [50, 50, 60],
        "TMIN": [30, 30, 35]
    })
    df_e = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02"],
        "demand": [100, 200]
    })
    cw = clean_weather(df_w)
    ce = clean_energy(df_e)
    merged = merge_weather_energy(cw, ce)
    # cw keeps only one valid date
    assert cw.shape[0] == 1
    # ce keeps both valid rows
    assert ce.shape[0] == 2
    # merged only has the overlapping date
    assert merged.shape == (1, 4)   # columns: date, TMAX, TMIN, demand
    assert merged["date"].iloc[0] == pd.to_datetime("2025-01-01")
