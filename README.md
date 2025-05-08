
# Splash Pad Data Pull Guide

Python script for discovering and enriching splash pads across the United States.

- Finds splash‑pad, spray‑ground, and small water‑park objects in OpenStreetMap via the Overpass API — looping state by state to avoid time‑outs

- Cleans and deduplicates the results, then reverse‑geocodes latitude/longitude → city, state, ZIP

- Applies a lightweight ruleset to classify each site (commercial water‑park, HOA, school, or municipal/unknown)

- Exports a timestamped CSV (clean_splashpads_<ts>.csv) ready for Clay enrichment and HubSpot import


## Contents
```bash
fetch_splashpads.py     # main ETL script
requirements.txt        # Python deps
RUN_INSTRUCTIONS.md     # copy/paste run book
clean_splashpads_*.csv  # generated output (not version‑controlled long term)
```

## Run Locally

Clone the project

```bash
  git clone https://github.com/lukejohnston12/pw-stormbridge-splashpads.git
```

Go to the project directory

```bash
  cd pw-stormbridge-splashpads
```

Create & activate a virtual‑environment, then install dependencies

```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  echo 'GEOCODER_EMAIL=you@example.com' > .env
```

Pull the latest splash pad CSV

```bash
  caffeinate -di python fetch_splashpads.py
```
When you see: 
```bash
  ✅  Saved <rows> rows → clean_splashpads_<timestamp>.csv
```
the new CSV is in the repo root! 🎉


## Notes

- Classification uses data tags in the response from Overpass. If there were no tags, the script defaults to "municipal_park". These should be validated in Clay with AI or manually.

## Authors

[@lukejohnston12](https://github.com/lukejohnston12)

