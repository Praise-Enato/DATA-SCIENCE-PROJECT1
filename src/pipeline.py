import logging
from pathlib import Path
import yaml
import json

# Fetchers
from data_fetcher import fetch_historical_weather, fetch_historical_energy
# Processors
from data_processor import clean_weather, clean_energy, merge_weather_energy
# Quality report
from data_quality_report import generate_report

def load_config(path: str):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def setup_logging(log_file: Path):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    fh = logging.FileHandler(str(log_file))
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger

if __name__ == "__main__":
    # --- Setup ---
    config = load_config("config/config.yaml")

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    logger = setup_logging(logs_dir / "pipeline.log")

    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    proc_dir = Path("data/processed")
    proc_dir.mkdir(parents=True, exist_ok=True)

    logger.info("🔄 Starting pipeline")

    # --- Fetch, Save, Process per City ---
    for city in config["cities"]:
        name        = city["name"]
        station_id  = city["station_id"]
        region_code = city["region"]
        slug        = name.lower().replace(" ", "_")

        # 1) Weather
        logger.info(f"🌡️ Fetching weather for {name}")
        try:
            df_w = fetch_historical_weather(
                station_id=station_id,
                days=92,
                token=config["noaa_token"]
            )
            weather_path = raw_dir / f"{slug}_weather.csv"
            df_w.to_csv(weather_path, index=False)
            logger.info(f"✅ Saved RAW weather → {weather_path}")
        except Exception as e:
            logger.error(f"Error fetching weather for {name}: {e}")
            continue  # skip processing if weather fails

        # 2) Energy
        logger.info(f"⚡ Fetching energy for {name}")
        try:
            df_e = fetch_historical_energy(
                region=region_code,
                days=92,
                api_key=config["eia_key"]
            )
            energy_path = raw_dir / f"{slug}_energy.csv"
            df_e.to_csv(energy_path, index=False)
            logger.info(f"✅ Saved RAW energy → {energy_path}")
        except Exception as e:
            logger.error(f"Error fetching energy for {name}: {e}")
            continue  # skip processing if energy fails

        # 3) Clean & merge
        try:
            cw = clean_weather(df_w)
            ce = clean_energy(df_e)
            df_combined = merge_weather_energy(cw, ce)
            proc_path = proc_dir / f"{slug}.csv"
            df_combined.to_csv(proc_path, index=False)
            logger.info(f"✅ Saved PROCESSED data → {proc_path}")
        except Exception as e:
            logger.error(f"Error processing data for {name}: {e}")

    # --- Data Quality Report (runs once) ---
    try:
        report = generate_report()
        qr_path = Path("data") / "quality_report.json"
        qr_path.write_text(json.dumps(report, indent=2))
        logger.info(f"✅ Data quality report saved → {qr_path}")
    except Exception as e:
        logger.error(f"Error generating quality report: {e}")

    logger.info("✅ Pipeline finished")
