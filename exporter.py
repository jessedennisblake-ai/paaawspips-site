#!/usr/bin/env python3
"""
PAAAWS PIPS - public feed exporter.

Run this ON THE PC that runs PIPS (with PIPS open so its engines answer on
localhost). It reads ONLY safe fields from the three engines and writes
feed.js next to the website. No strategy code, settings, magic numbers,
account logins or API keys ever leave the machine.

  python exporter.py          # updates feed.js every 60s
  python exporter.py --once   # write once and exit
"""
import json, time, os, sys, urllib.request

BASE = "http://127.0.0.1:8000"
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "feed.js")
COLOUR = {"red": "#ff4256", "blue": "#308dff", "orange": "#f7931a",
          "purple": "#a779f5", "teal": "#00ddc7", "pink": "#ed3d9c", "yellow": "#e9c94b"}


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=15) as r:
        return json.load(r)


def card(c):
    """Only the safe, public fields - name, round, a short type, and results."""
    s = c.get("summary") or {}
    return {
        "name":    c.get("name"),
        "type":    c.get("subtitle"),           # short label only; no mechanics
        "pnl":     s.get("total_pnl"),
        "today":   s.get("today_pnl"),
        "win":     s.get("win_rate"),
        "trades":  s.get("total_trades"),
        "running": bool(c.get("running")),
        "accent":  COLOUR.get(c.get("colour"), "#a779f5"),
    }


def acct(o):
    a = o.get("account") or {}
    return {"balance": a.get("balance"), "equity": a.get("equity")}


def totals(cards):
    tr = sum((b["trades"] or 0) for b in cards)
    today = sum((b["today"] or 0) for b in cards)
    wins = sum(round((b["win"] or 0) / 100 * (b["trades"] or 0)) for b in cards)
    return {"total_trades": tr, "today_closed": round(today, 2),
            "win_rate": round(wins / tr * 100, 1) if tr else None, "floating": None}


def build():
    champs = get("/api/bots/overview")           # main engine  = CHAMPS
    new    = get("/api/new/bots/overview")        # new engine   = ROUND 1 / 2 / 3
    grave  = get("/api/grave/bots/overview")      # grave engine = THE GRAVE
    nb = new.get("bots", [])
    rounds = {
        "CHAMPS":    [card(c) for c in champs.get("bots", [])],
        "ROUND 1":   [card(c) for c in nb if not c.get("stage")],
        "ROUND 2":   [card(c) for c in nb if c.get("stage") == "round2"],
        "ROUND 3":   [card(c) for c in nb if c.get("stage") == "round3"],
        "THE GRAVE": [card(c) for c in grave.get("bots", [])],
    }
    feed = {
        "updated": int(time.time()),
        "mt5":     bool(champs.get("mt5") or new.get("mt5") or grave.get("mt5")),
        "rounds":  rounds,
        "totals":  {k: totals(v) for k, v in rounds.items()},
        "accounts": {"CHAMPS": acct(champs), "ROUND 1": acct(new), "ROUND 2": acct(new),
                     "ROUND 3": acct(new), "THE GRAVE": acct(grave)},
    }
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("window.FEED = " + json.dumps(feed, separators=(",", ":")) + ";")
    return feed


def git_push():
    """If this folder is a git repo, commit + push feed.js so the live site updates by itself."""
    import subprocess
    d = os.path.dirname(OUT)
    if not os.path.isdir(os.path.join(d, ".git")):
        return
    try:
        subprocess.run(["git", "-C", d, "add", "feed.js"], capture_output=True)
        subprocess.run(["git", "-C", d, "commit", "-m", "live feed " + time.strftime("%H:%M:%S")], capture_output=True)
        r = subprocess.run(["git", "-C", d, "push", "-q"], capture_output=True, text=True)
        if r.returncode == 0:
            print("   pushed to GitHub")
    except Exception as e:
        print("   push skipped:", e)


if __name__ == "__main__":
    once = "--once" in sys.argv
    while True:
        try:
            f = build()
            n = sum(len(v) for v in f["rounds"].values())
            print(time.strftime("%H:%M:%S"), "feed.js written -", n, "bots")
            git_push()
        except Exception as e:
            print("exporter error:", e, "(is PIPS open?)")
        if once:
            break
        time.sleep(60)
