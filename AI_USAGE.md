## Troubleshooting & Solutions

### 1. Wrong Facet Key  
- **Symptom:** 404 errors or empty results when using `facets[region][]`.  
- **Fix:** The correct facet for EIA-930 is `facets[respondent][]`.  


### 2. Pipeline Save Logic  
- **Symptom:** No CSVs being written even after successful fetch.  
- **Fix:** Added explicit `to_csv(...)` calls and log messages in `pipeline.py`, and ensured `data/raw/` exists.

