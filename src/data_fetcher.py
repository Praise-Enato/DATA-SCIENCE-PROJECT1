import requests
import pandas as pd
from datetime import datetime, timedelta
import time


def _get_with_backoff(url, params, headers=None, max_retries=3, backoff_factor=1):
    """
    GET with retries on 5xx/connection errors.
    """
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            # only retry on server errors
            if status and 500 <= status < 600 and attempt < max_retries:
                wait = backoff_factor * (2 ** (attempt - 1))
                print(f"Warning: HTTP {status}, retrying in {wait}s…")
                time.sleep(wait)
                continue
            raise
        except requests.exceptions.RequestException as e:
            # catch network/timeouts
            if attempt < max_retries:
                wait = backoff_factor * (2 ** (attempt - 1))
                print(f"Warning: {e}, retrying in {wait}s…")
                time.sleep(wait)
                continue
            raise

def fetch_historical_weather(station_id: str, days: int, token: str) -> pd.DataFrame:
    end = datetime.utcnow().date()
    start = end - timedelta(days=days)
    url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    params = {
        "datasetid":  "GHCND",
        "stationid":  station_id,
        "startdate":  start.isoformat(),
        "enddate":    end.isoformat(),
        "datatypeid": "TMAX,TMIN",
        "limit":      1000
    }
    headers = {"token": token}

    resp = _get_with_backoff(url, params, headers)
    data = resp.json().get("results", [])
    df   = pd.DataFrame(data)
    df   = df.pivot(index="date", columns="datatype", values="value").reset_index()

    # Convert tenths °C → °F
    for col in ("TMAX", "TMIN"):
        if col in df:
            df[col] = df[col].apply(lambda x: (x/10 * 9/5) + 32)
    return df

def fetch_historical_energy(region: str, days: int, api_key: str) -> pd.DataFrame:
    """
    Fetches last `days` days of daily demand from EIA v2 (EIA-930).
    """
    # calculate the end date
    end   = datetime.now().date()
    # EIA-930 data is daily, so we need to go back `days`
    # and include the end date.
    if days < 90:
        raise ValueError("EIA-930 data requires at least 90 days of history.")
    
    # Calculate the start date
    start = end - timedelta(days=days)
    url   = "https://api.eia.gov/v2/electricity/rto/daily-region-data/data/"
    params = {
        "api_key":            api_key,
        "frequency":          "daily",
        "start":              start.isoformat(),
        "end":                end.isoformat(),
        "data[0]":            "value",
        "facets[respondent][]": region,           # ← use respondent
        "sort[0][column]":    "period",
        "sort[0][direction]": "asc",
        "offset":             0,
        "length":             5000
    }
    
    resp = _get_with_backoff(url, params)
    resp.raise_for_status()
    js   = resp.json().get("response", {})
    data = js.get("data", [])
    df   = pd.DataFrame(data)
    return df.rename(columns={"period":"date", "value":"demand"})


# def fetch_historical_energy_v1(region: str, days: int, api_key: str) -> pd.DataFrame:
#     """
#     Pulls the last `days` days of hourly demand from EIA v1 series API,
#     then aggregates to daily total demand.
#     """
#     # EIA v1 series IDs for hourly RTO demand all follow “EBA.<REGION>.D.H”
#     series_id = f"EBA.{region}.D.H"

#     url = "https://api.eia.gov/series/"
#     params = {
#         "api_key":   api_key,
#         "series_id": series_id
#     }
#     # we can reuse our backoff helper
#     resp = _get_with_backoff(url, params)
#     resp.raise_for_status()

#     js = resp.json()
#     # The JSON has: series → [ { data: [ [‘YYYYMMDDHH’, value], … ] } ]
#     raw = js["series"][0]["data"]
#     df  = pd.DataFrame(raw, columns=["datetime", "value"])

#     # Parse the hourly timestamp and group into daily sums
#     df["datetime"] = pd.to_datetime(df["datetime"], format="%Y%m%d%H")
#     df["date"]     = df["datetime"].dt.date
#     daily = (
#         df
#         .groupby("date", as_index=False)["value"]
#         .sum()
#         .rename(columns={"value": "demand"})
#     )

#     # Keep only the last `days` days
#     cutoff = pd.to_datetime(daily["date"].max()) - pd.Timedelta(days=days-1)
#     return daily[daily["date"] >= cutoff.dt.date.iloc[0]]
