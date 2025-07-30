import pytest
import pandas as pd
from pipeline import load_config
from ..data_fetcher import fetch_historical_weather

def test_load_config(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("noaa_token: abc\neia_key: xyz\ncities: []")
    config = load_config(str(cfg))
    assert config["noaa_token"] == "abc"
    assert config["eia_key"] == "xyz"

def test_fetch_weather_monkeypatched(monkeypatch):
    dummy = {'results': [
        {'date':'2025-01-01','datatype':'TMAX','value':100},
        {'date':'2025-01-01','datatype':'TMIN','value': 50},
    ]}
    class Resp:
        def raise_for_status(self): pass
        def json(self): return dummy
    monkeypatch.setattr('requests.get', lambda *a,**k: Resp())
    df = fetch_historical_weather("GHCND:TEST", 1, "token")
    assert isinstance(df, pd.DataFrame)
    assert "TMAX" in df.columns and "TMIN" in df.columns
