# tests/test_data_fetcher.py

import pandas as pd
import pytest

from data_fetcher import fetch_historical_weather, fetch_historical_energy

def test_fetch_weather_monkeypatch(monkeypatch):
    fake = {"results": [
        {"date": "2025-02-01", "datatype": "TMAX", "value": 100},
        {"date": "2025-02-01", "datatype": "TMIN", "value": 50},
    ]}
    class Resp:
        def raise_for_status(self): pass
        def json(self): return fake

    monkeypatch.setattr("data_fetcher.requests.get", lambda *a, **k: Resp())
    df = fetch_historical_weather("GHCND:TEST", days=1, token="tok")
    assert list(df.columns) == ["date", "TMAX", "TMIN"]
    assert df["TMAX"].iloc[0] == (100/10*9/5+32)

def test_fetch_energy_monkeypatch(monkeypatch):
    fake = {"response": {"data": [
        {"period": "2025-02-01", "value": 1234}
    ]}}
    class Resp:
        def raise_for_status(self): pass
        def json(self): return fake

    monkeypatch.setattr("data_fetcher.requests.get", lambda *a, **k: Resp())
    df = fetch_historical_energy(region="NYISO", days=1, api_key="k")
    assert list(df.columns) == ["date", "demand"]
    assert df["demand"].iloc[0] == 1234
