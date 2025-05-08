# Splash‑Pad Data Pull – On‑Demand Guide
#
# --------------------------------------------------------------------------
# 0. First‑time setup  (run ONCE per Mac)
#    Skip this entire block if the repo + venv already exist.
# --------------------------------------------------------------------------
git clone https://github.com/lukejohnston12/pw-stormbridge-splashpads.git
cd pw-stormbridge-splashpads
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo 'GEOCODER_EMAIL=you@example.com' > .env    # Nominatim polite contact

# --------------------------------------------------------------------------
# 1. Refresh the CSV (run WHENEVER you need new data)
# --------------------------------------------------------------------------
cd ~/pw-stormbridge-splashpads
source .venv/bin/activate
caffeinate -di python fetch_splashpads.py
# → wait ~6‑7 min for the “✅ Saved … rows → clean_splashpads_<timestamp>.csv”

# --------------------------------------------------------------------------
# 1‑a. One‑liner version (copy/paste)
# --------------------------------------------------------------------------
cd ~/pw-stormbridge-splashpads && source .venv/bin/activate && caffeinate -di python fetch_splashpads.py

# --------------------------------------------------------------------------
# 2. Troubleshooting
# --------------------------------------------------------------------------
# • “command not found: activate”  →  cd to repo, then `source .venv/bin/activate`
# • “No module named …”            →  inside venv: `pip install -r requirements.txt`
# • Overpass timeout / 429         →  up‑arrow & re‑run (mirrors can be busy)
# • Mac sleeps mid‑run             →  always prefix with `caffeinate -di` or use tmux

# --------------------------------------------------------------------------
# 3. Optional tmux wrapper (run survives closed terminal)
# --------------------------------------------------------------------------
brew install tmux                    # run once if tmux isn’t installed
tmux new -s splashrun
source .venv/bin/activate
caffeinate -di python fetch_splashpads.py
# detach:  Ctrl‑B  then  D
# re‑attach: tmux attach -t splashrun

# --------------------------------------------------------------------------
# 4. Why on‑demand, not nightly
# --------------------------------------------------------------------------
# New splash‑pads appear monthly, not daily.  A manual pull keeps the repo
# clean and avoids hammering public Overpass servers.
