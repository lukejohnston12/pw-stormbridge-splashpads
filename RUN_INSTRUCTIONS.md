# Splash‑Pad Data Pull — On‑Demand Guide
#
# PURPOSE
#   One‑time setup + repeatable command to regenerate
#   clean_splashpads_<timestamp>.csv
#
# ────────────────────────────────────────────────────────────────────
# 0. FIRST‑TIME SETUP  (run ONCE per computer)
# ────────────────────────────────────────────────────────────────────
git clone https://github.com/lukejohnston12/pw-stormbridge-splashpads.git
cd pw-stormbridge-splashpads
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo 'GEOCODER_EMAIL=you@example.com' > .env     # polite contact for Nominatim

# ────────────────────────────────────────────────────────────────────
# 1. REFRESH THE CSV  (run WHENEVER you need new data)
# ────────────────────────────────────────────────────────────────────
cd ~/pw-stormbridge-splashpads
source .venv/bin/activate
caffeinate -di python fetch_splashpads.py
#   • Runtime ≈ 6‑7 min
#   • Finished message:
#       ✅  Saved <rows> rows → clean_splashpads_<timestamp>.csv
#     The new CSV appears in the repo root.

# —— one‑liner shortcut ————————————————————————————————————————
cd ~/pw-stormbridge-splashpads && source .venv/bin/activate && caffeinate -di python fetch_splashpads.py

# ────────────────────────────────────────────────────────────────────
# 2. TROUBLESHOOTING
# ────────────────────────────────────────────────────────────────────
# command not found: activate   →  cd to repo, then  source .venv/bin/activate
# No module named overpy        →  pip install -r requirements.txt   (inside venv)
# Overpass timeout / 429        →  up‑arrow & re‑run (mirrors can be busy)
# Mac sleeps mid‑run            →  always prefix with  caffeinate -di  or use tmux below

# ────────────────────────────────────────────────────────────────────
# 3. OPTIONAL: KEEP IT RUNNING IN TMUX
# ────────────────────────────────────────────────────────────────────
brew install tmux                 # first time only
tmux new -s splashrun
source .venv/bin/activate
caffeinate -di python fetch_splashpads.py
# detach:  Ctrl‑B  D
# re‑attach: tmux attach -t splashrun

# ────────────────────────────────────────────────────────────────────
# 4. WHY ON‑DEMAND INSTEAD OF NIGHTLY
# ────────────────────────────────────────────────────────────────────
# Splash‑pad tags change monthly, not daily.  Manual pulls keep the repo
# clean and avoid unnecessary load on public Overpass servers.