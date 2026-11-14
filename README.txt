PAAAWS PIPS - BATTLE ARENA (live-wired)
=======================================

FILES
  index.html    ChatGPT's Battle Arena design, wired to read live bot results.
  exporter.py   Reads your real PIPS results and writes feed.js (safe fields only).
  feed.js       Created by exporter.py. Until it exists the site shows placeholders.
  CNAME         The custom domain for GitHub Pages (paaawspips.co.uk).

HOW THE LIVE DATA WORKS
  The website loads feed.js, which the exporter rewrites from your three PIPS
  engines (CHAMPS / ROUND 1-2-3 / THE GRAVE). Only name, round, a short type,
  P&L, win rate and trade count leave the PC. No strategy code, settings, magic
  numbers, logins or API keys are ever written to the feed. No trading controls.

RUN IT (on the PIPS PC, with PIPS open)
  python exporter.py           -> updates feed.js every 60 seconds
  python exporter.py --once    -> write feed.js once
  Then open index.html.

GO LIVE (GitHub Pages + IONOS)
  1. Push this folder to a public GitHub repo.
  2. Repo Settings - Pages - Deploy from branch (main / root).
  3. Set the custom domain to paaawspips.co.uk (the CNAME file does this).
  4. In IONOS DNS, point the domain at GitHub Pages:
       four A records on @  -> 185.199.108.153 / .109.153 / .110.153 / .111.153
       one CNAME on www     -> <your-github-username>.github.io
  5. To keep it live, have exporter.py also push feed.js to the repo each run
     (git commit + push), or run it on the PC and host the feed alongside.

DEMO: every figure is from demo accounts and is labelled as such.
