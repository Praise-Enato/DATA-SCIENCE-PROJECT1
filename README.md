# Energy Analysis Project

US Weather + Energy Analysis Pipeline.

## Setup

1. Create virtual environment:
```bash
# Create a new virtual environment
python -m venv energy_analysis_env

# Activate it on Linux/Mac
source energy_analysis_env/bin/activate

# Your prompt should now show (energy_analysis_env)
```

2. Install dependencies:
```bash
# Make sure you're in the virtual environment (should see (energy_analysis_env) in prompt)
pip install -r requirements.txt
```

3. Add your API keys & city list to `config/config.yaml`:
```yaml
noaa_token: "your-noaa-token"
eia_key: "your-eia-key"
cities:
  - name: New York
    station_id: GHCND:USW00094728
    region: NYIS
  - name: Chicago
    station_id: GHCND:USW00094846
    region: PJM
  - name: Houston
    station_id: GHCND:USW00012960
    region: ERCO
  - name: Phoenix
    station_id: GHCND:USW00023183
    region: AZPS
  - name: Seattle
    station_id: GHCND:USW00024233
    region: CISO

# city_coords = {
#     "new_york": {"lat": 40.7128, "lon": -74.0060},
#     "chicago":  {"lat": 41.8781, "lon": -87.6298},
#     "houston":  {"lat": 29.7604, "lon": -95.3698},
#     "phoenix":  {"lat": 33.4484, "lon": -112.0740},
#     "seattle":  {"lat": 47.6062, "lon": -122.3321},
# }
```

## Usage

1. Run data pipeline:
```bash
python src/pipeline.py
```

2. Launch dashboard:
```bash
streamlit run dashboards/app.py
```

## Project Structure

```
project1-energy-analysis/
├── config/
│   └── config.yaml
├── src/
│   ├── pipeline.py
│   ├── data_fetcher.py
│   └── data_processor.py
├── dashboards/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
└── logs/
```
