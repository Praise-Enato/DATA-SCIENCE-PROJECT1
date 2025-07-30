import pandas as pd
from pathlib import Path
from datetime import datetime

RAW_DIR = Path("data/raw")
TODAY   = datetime.utcnow().date()

def check_missing(df: pd.DataFrame):
    return df.isna().sum().to_dict()

def check_outliers_weather(df: pd.DataFrame):
    return {
        "TMAX>130": int((df["TMAX"] > 130).sum()),
        "TMIN<-50": int((df["TMIN"] < -50).sum())
    }

def check_outliers_energy(df: pd.DataFrame):
    return {"demand<0": int((df["demand"] < 0).sum())}

def check_freshness(df: pd.DataFrame, date_col="date"):
    dates = pd.to_datetime(df[date_col]).dt.date
    latest = dates.max()
    return {"latest": str(latest), "days_old": int((TODAY - latest).days)}

def analyze_city(city_slug: str) -> dict:
    weather = pd.read_csv(RAW_DIR / f"{city_slug}_weather.csv")
    energy  = pd.read_csv(RAW_DIR / f"{city_slug}_energy.csv")

    return {
        "missing_weather":  check_missing(weather),
        "missing_energy":   check_missing(energy),
        "outliers_weather": check_outliers_weather(weather),
        "outliers_energy":  check_outliers_energy(energy),
        "freshness_weather": check_freshness(weather, "date"),
        "freshness_energy":  check_freshness(energy,  "date"),
    }

def generate_report() -> dict:
    report = {}
    for weather_file in RAW_DIR.glob("*_weather.csv"):
        slug = weather_file.stem.replace("_weather", "")
        report[slug] = analyze_city(slug)
    return report

if __name__ == "__main__":
    import json
    report = generate_report()
    print(json.dumps(report, indent=2))
