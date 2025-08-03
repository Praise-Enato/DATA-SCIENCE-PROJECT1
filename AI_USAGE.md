# AI\_USAGE.md

This document outlines how AI was leveraged throughout the US Weather + Energy Analysis project, including tools used, effective prompts, mistakes identified, and time saved.

---

## 1. AI Tools Used

- **ChatGPT (OpenAI o4-mini)**: Assisted in generating pipeline and dashboard code, troubleshooting API issues, and explaining concepts.
- **Python REPL**: For testing snippets, analyzing JSON structures, and iterating on data transformations.

---

## 2. Most Effective Prompts

1. **Data Fetching Function**:

   ```
   "I need to create a Python function that fetches weather data from NOAA API for multiple cities, handles rate limiting, implements exponential backoff for retries, and logs all errors. The function should return a pandas DataFrame with consistent column names regardless of the city."
   ```
2. **EIA API Troubleshooting**:

   ```
   "Error 404 on EIA v2 daily-region-data: how do I adjust the facet parameter to retrieve daily RTO demand?"
   ```
3. **Streamlit Visualization**:

   ```
   "Show me how to build a dual-axis time series in Streamlit with weekends shaded and a city selector dropdown."
   ```

These prompts yielded clear, modular code and step-by-step explanations.

---

## 3. AI Mistakes Identified & Fixed

1. **Incorrect Facet Parameter**:

   - **What happened**: Initial code used `facets[region][]`, resulting in 404 errors.
   - **Fix**: Switched to `facets[respondent][]`, matching the EIA-930 API requirement.

2. **Region Code Mismatches**:

   - **What happened**: Used `SCL` for Seattle instead of `CISO`, leading to missing data.
   - **Fix**: Updated `config.yaml` and series IDs to use the correct balancing-authority codes.

3. **Pipeline Save Logic**: 
   - **Symptom:** No CSVs being written even after successful fetch.  
   - **Fix:** Added explicit `to_csv(...)` calls and log messages in `pipeline.py`, and ensured `data/raw/` exists.

4. **Missing Statsmodels Dependency**:

   - **What happened**: Plotly trendline code errored without `statsmodels` installed.
   - **Fix**: Added `statsmodels` to dependencies or removed the `trendline='ols'` argument.

5. **API Downtime Fallbacks**:

   - **What happened**: EIA v2 endpoint returned 500 errors.
   - **Fix**: Implemented fallback using the EIA v1 `series` API (`EBA.<REGION>.D.H`) and aggregated hourly to daily.

Each of these fixes was documented in the troubleshooting section and reflected in the final code.

---

## 4. Time Saved Estimate

By using AI assistance for generating boilerplate, troubleshooting API quirks, and drafting visualizations, we estimate:

- **Pipeline scaffolding**: \~3 hours saved
- **API integration & retries**: \~5 hours saved
- **Streamlit dashboard coding**: \~4 hours saved
- **Documentation & debugging**: \~2 hours saved

**Total**: approximately **14 hours** of development time saved.

---

## Troubleshooting & Solutions

### 1. NOAA & EIA v2 Endpoint Errors  
- **Symptom:** Intermittent 500/503 errors fetching daily RTO data via  
  `https://api.eia.gov/v2/electricity/rto/daily-region-data/data/`.  
- **Analysis:** The v2 endpoint was unstable and often returned server errors.  
- **Fix:** Switched to the EIA v1 `series` API (`EBA.<REGION>.D.H`) and aggregated hourly data into daily sums.

### 2. Wrong Facet Key  
- **Symptom:** 404 errors or empty results when using `facets[region][]`.  
- **Analysis:** The EIA-930 API uses `respondent` rather than `region` as the facet key.  
- **Fix:** Updated `fetch_historical_energy` to use `facets[respondent][]` for filtering by balancing authority.

### 3. Region Code Mismatches  
- **Symptom:** 404 errors for Seattle’s series ID (e.g. `EBA.SCL.D.H`).  
- **Analysis:** The config.yaml had an incorrect region code (`SCL` or `CAISO`), not matching the v1 series.  
- **Fix:** Corrected Seattle’s region to `CISO` so the series ID `EBA.CISO.D.H` existed.

### 4. Pipeline Save Logic  
- **Symptom:** Pipeline ran successfully but no CSVs appeared in `data/raw/`.  
- **Analysis:** We forgot to include explicit `to_csv()` calls and didn’t ensure the directory existed.  
- **Fix:** Added `raw_dir.mkdir(...)` and `df.to_csv(...)` with logging for both weather and energy fetches.

### 5. Trendline Dependency in Notebook  
- **Symptom:** Plotly Express trending (`trendline='ols'`) failed with  
  `ModuleNotFoundError: No module named 'statsmodels'` in the exploration notebook.  
- **Analysis:** The notebook cell installed core packages but omitted `statsmodels`, which Plotly uses under the hood.  
- **Fix:** Updated the install cell to `!pip install statsmodels`, or removed the `trendline="ols"` argument to avoid the dependency.

