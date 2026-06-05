"""
AURUM — XAU/USD SMC Trading Bot
Déployable sur share.streamlit.io (gratuit)
"""

import streamlit as st
import requests
import json
import math
from datetime import datetime, timedelta
import time

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aurum — XAU/USD SMC",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS CUSTOM ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

:root {
  --ink:    #0c0c0e;
  --paper:  #0f0f12;
  --panel:  #141418;
  --border: #1f1f26;
  --gold:   #d4a843;
  --gold2:  #f0c060;
  --bull:   #2ecc8f;
  --bear:   #e8445a;
  --blue:   #5b8cff;
  --muted:  #6e6e85;
  --text:   #c8c8d8;
  --bright: #eeeef5;
  --mono:   'IBM Plex Mono', monospace;
  --serif:  'DM Serif Display', serif;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace !important;
    background-color: #0c0c0e !important;
    color: #c8c8d8 !important;
}

/* Hide Streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 1rem 2rem 1rem !important; max-width: 520px !important; margin: 0 auto !important; }

/* ── HEADER ── */
.aurum-header {
    background: #141418;
    border: 1px solid #1f1f26;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
}

.brand-name {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    color: #f0c060;
    line-height: 1;
    margin: 0;
}

.brand-sub {
    font-size: 9px;
    color: #6e6e85;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 3px;
}

/* ── SIGNAL CARD ── */
.signal-card {
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 10px;
    border: 1px solid #1f1f26;
}

.signal-buy  { background: linear-gradient(135deg, rgba(46,204,143,.08), #141418); border-top: 2px solid #2ecc8f !important; }
.signal-sell { background: linear-gradient(135deg, rgba(232,68,90,.08), #141418);  border-top: 2px solid #e8445a !important; }
.signal-wait { background: linear-gradient(135deg, rgba(212,168,67,.08), #141418); border-top: 2px solid #d4a843 !important; }

.signal-direction-buy  { font-family: 'DM Serif Display', serif; font-size: 52px; color: #2ecc8f; line-height: 1; }
.signal-direction-sell { font-family: 'DM Serif Display', serif; font-size: 52px; color: #e8445a; line-height: 1; }
.signal-direction-wait { font-family: 'DM Serif Display', serif; font-size: 52px; color: #d4a843; line-height: 1; }

.conf-num { font-size: 32px; font-weight: 700; color: #eeeef5; letter-spacing: -.03em; }
.conf-label { font-size: 8px; color: #6e6e85; letter-spacing: .12em; text-transform: uppercase; }

/* ── METRIC CARD ── */
.metric-card {
    background: #141418;
    border: 1px solid #1f1f26;
    border-radius: 6px;
    padding: 10px 12px;
    text-align: center;
}
.metric-val { font-size: 20px; font-weight: 700; color: #eeeef5; letter-spacing: -.02em; font-family: 'DM Serif Display', serif; }
.metric-label { font-size: 8px; color: #6e6e85; letter-spacing: .12em; text-transform: uppercase; margin-top: 2px; }

/* ── SMC BADGE ── */
.badge-bull { background: rgba(46,204,143,.08); border: 1px solid rgba(46,204,143,.25); color: #2ecc8f; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: 600; }
.badge-bear { background: rgba(232,68,90,.08);  border: 1px solid rgba(232,68,90,.25);  color: #e8445a; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: 600; }
.badge-purp { background: rgba(167,139,250,.08); border: 1px solid rgba(167,139,250,.25); color: #a78bfa; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: 600; }

/* ── SECTION HEADER ── */
.section-hdr {
    font-size: 9px;
    letter-spacing: .18em;
    color: #6e6e85;
    text-transform: uppercase;
    padding: 8px 0 6px;
    border-bottom: 1px solid #1f1f26;
    margin-bottom: 8px;
}

/* ── ROW ── */
.smc-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid #1a1a22;
    font-size: 11px;
}
.smc-val  { color: #6e6e85; font-size: 10px; }
.smc-str  { color: #d4a843; font-size: 10px; }

/* ── REASON ITEM ── */
.reason-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid #1a1a22;
    font-size: 11px;
    color: #c8c8d8;
}
.dot-bull { width: 6px; height: 6px; border-radius: 50%; background: #2ecc8f; display: inline-block; flex-shrink: 0; }
.dot-bear { width: 6px; height: 6px; border-radius: 50%; background: #e8445a; display: inline-block; flex-shrink: 0; }

/* ── SLTP ── */
.sltp-box {
    background: #0f0f12;
    border: 1px solid #1f1f26;
    border-radius: 5px;
    padding: 10px;
    text-align: center;
}
.sltp-label { font-size: 8px; color: #6e6e85; letter-spacing: .12em; text-transform: uppercase; }
.sltp-sl  { font-size: 14px; font-weight: 700; color: #e8445a; }
.sltp-tp1 { font-size: 14px; font-weight: 700; color: #2ecc8f; }
.sltp-tp2 { font-size: 14px; font-weight: 700; color: #5b8cff; }

/* ── LIVE DOT ── */
.live-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(46,204,143,.08);
    border: 1px solid rgba(46,204,143,.2);
    border-radius: 3px;
    padding: 3px 8px;
    font-size: 9px;
    color: #2ecc8f;
    letter-spacing: .12em;
}

/* ── SCORE BAR ── */
.score-bar-bg {
    background: #1f1f26;
    border-radius: 2px;
    height: 3px;
    margin: 8px 0;
    overflow: hidden;
}

/* ── TRADE ITEM ── */
.trade-item {
    background: #141418;
    border: 1px solid #1f1f26;
    border-radius: 5px;
    padding: 9px 12px;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.t-dir-buy  { font-size: 11px; font-weight: 700; color: #2ecc8f; }
.t-dir-sell { font-size: 11px; font-weight: 700; color: #e8445a; }
.t-meta { font-size: 9px; color: #454555; }
.t-win  { font-size: 11px; font-weight: 700; color: #2ecc8f; }
.t-loss { font-size: 11px; font-weight: 700; color: #e8445a; }
.t-be   { font-size: 11px; font-weight: 700; color: #d4a843; }

/* Streamlit buttons override */
.stButton > button {
    background: #141418 !important;
    color: #d4a843 !important;
    border: 1px solid #2a2a35 !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    padding: 8px 16px !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #1f1f28 !important;
    border-color: #d4a843 !important;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    background: #141418;
    border-bottom: 1px solid #1f1f26;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #6e6e85;
    background: transparent;
    border: none;
    padding: 10px 14px;
}
.stTabs [aria-selected="true"] {
    color: #d4a843 !important;
    border-bottom: 2px solid #d4a843 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent;
    padding: 12px 0 0 0;
}

/* Select & input */
.stSelectbox > div, .stTextArea > div {
    background: #141418 !important;
    border-color: #1f1f26 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    color: #c8c8d8 !important;
}
</style>
""", unsafe_allow_html=True)


# ─── DATA FETCHING ────────────────────────────────────────────────────────────
@st.cache_data(ttl=900)  # cache 15 minutes
def fetch_gold_candles():
    """Fetch real XAU/USD 15-min candles. Deux sources gratuites."""
    import random

    # Source 1 : Yahoo Finance
    try:
        end = int(datetime.now().timestamp())
        start = int((datetime.now() - timedelta(days=5)).timestamp())
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=15m&period1={start}&period2={end}"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        data = resp.json()
        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        q = result["indicators"]["quote"][0]
        candles = []
        for i in range(len(timestamps)):
            try:
                if q["open"][i] and q["close"][i] and q["high"][i] and q["low"][i]:
                    candles.append({
                        "time": datetime.fromtimestamp(timestamps[i]).strftime("%H:%M"),
                        "open":  round(q["open"][i], 2),
                        "high":  round(q["high"][i], 2),
                        "low":   round(q["low"][i], 2),
                        "close": round(q["close"][i], 2),
                        "vol":   round(q.get("volume", [1000]*len(timestamps))[i] or 1000, 1)
                    })
            except Exception:
                continue
        if len(candles) >= 20:
            return candles, "Yahoo Finance (réel)"
    except Exception:
        pass

    # Source 2 : Stooq
    try:
        url = "https://stooq.com/q/d/l/?s=xauusd&i=15m"
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200 and len(resp.text) > 100:
            lines = resp.text.strip().split("\n")[1:]
            candles = []
            for line in lines[-120:]:
                parts = line.split(",")
                if len(parts) >= 5:
                    try:
                        candles.append({
                            "time": parts[0],
                            "open":  float(parts[-4]),
                            "high":  float(parts[-3]),
                            "low":   float(parts[-2]),
                            "close": float(parts[-1]),
                            "vol":   1000.0
                        })
                    except Exception:
                        continue
            if len(candles) >= 20:
                return candles, "Stooq (réel)"
    except Exception:
        pass

    # Fallback synthétique
    candles = []
    price = 2340.0
    now = datetime.now()
    for i in range(100, -1, -1):
        dt = now - timedelta(minutes=i * 15)
        move = (random.random() - 0.48) * 6
        o = price
        c = round(price + move, 2)
        h = round(max(o, c) + random.random() * 3, 2)
        l = round(min(o, c) - random.random() * 3, 2)
        candles.append({"time": dt.strftime("%H:%M"), "open": o, "high": h, "low": l, "close": c, "vol": round(800 + random.random() * 1200, 1)})
        price = c
    return candles, "Synthétique (API indisponible)"


# ─── SMC ENGINE ───────────────────────────────────────────────────────────────
def detect_order_blocks(candles):
    obs = []
    for i in range(2, len(candles) - 1):
        p, c, n = candles[i-1], candles[i], candles[i+1]
        if p["close"] < p["open"] and n["close"] > n["open"]:
            ratio = (n["close"] - n["open"]) / max(p["open"] - p["close"], 0.01)
            if ratio > 1.5:
                obs.append({"type": "bullish", "top": p["open"], "bottom": p["close"], "strength": min(100, int(ratio * 50))})
        if p["close"] > p["open"] and n["close"] < n["open"]:
            ratio = (n["open"] - n["close"]) / max(p["close"] - p["open"], 0.01)
            if ratio > 1.5:
                obs.append({"type": "bearish", "top": p["close"], "bottom": p["open"], "strength": min(100, int(ratio * 50))})
    return obs[-6:]

def detect_fvg(candles):
    fvgs = []
    for i in range(1, len(candles) - 1):
        prev, nxt = candles[i-1], candles[i+1]
        if nxt["low"] > prev["high"]:
            fvgs.append({"type": "bullish", "top": nxt["low"], "bottom": prev["high"], "size": round(nxt["low"] - prev["high"], 2)})
        if nxt["high"] < prev["low"]:
            fvgs.append({"type": "bearish", "top": prev["low"], "bottom": nxt["high"], "size": round(prev["low"] - nxt["high"], 2)})
    return fvgs[-6:]

def detect_bos(candles, lookback=10):
    signals = []
    for i in range(lookback, len(candles)):
        window = candles[i-lookback:i]
        hh = max(c["high"] for c in window)
        ll = min(c["low"] for c in window)
        curr = candles[i]
        if curr["close"] > hh:
            signals.append({"type": "bullish", "level": round(hh, 2)})
        if curr["close"] < ll:
            signals.append({"type": "bearish", "level": round(ll, 2)})
    return signals[-3:]

def detect_liquidity_sweep(candles):
    sweeps = []
    for i in range(5, len(candles)):
        window = candles[i-5:i]
        lh = max(c["high"] for c in window)
        ll = min(c["low"] for c in window)
        curr = candles[i]
        if curr["high"] > lh and curr["close"] < lh:
            sweeps.append({"type": "sell_side", "level": round(lh, 2)})
        if curr["low"] < ll and curr["close"] > ll:
            sweeps.append({"type": "buy_side", "level": round(ll, 2)})
    return sweeps[-3:]

def detect_choch(candles):
    changes = []
    for i in range(3, len(candles) - 1):
        p3, p2, p1, curr = candles[i-3], candles[i-2], candles[i-1], candles[i]
        if p3["close"] < p2["close"] < p1["close"] and curr["close"] < p1["low"]:
            changes.append({"type": "bearish"})
        if p3["close"] > p2["close"] > p1["close"] and curr["close"] > p1["high"]:
            changes.append({"type": "bullish"})
    return changes[-2:]

def calc_ema(values, period):
    if not values: return 0
    k = 2 / (period + 1)
    ema = values[0]
    for v in values[1:]: ema = v * k + ema * (1 - k)
    return round(ema, 2)

def calc_rsi(candles, period=14):
    if len(candles) < period + 1: return 50
    closes = [c["close"] for c in candles[-(period+1):]]
    gains = losses = 0
    for i in range(1, len(closes)):
        d = closes[i] - closes[i-1]
        if d > 0: gains += d
        else: losses -= d
    rs = gains / max(losses, 0.0001)
    return round(100 - 100 / (1 + rs), 1)

def calc_atr(candles, period=14):
    trs = []
    cs = candles[-period:]
    for i in range(1, len(cs)):
        c, p = cs[i], cs[i-1]
        trs.append(max(c["high"]-c["low"], abs(c["high"]-p["close"]), abs(c["low"]-p["close"])))
    return round(sum(trs) / max(len(trs), 1), 2)

def compute_signal(candles):
    if len(candles) < 20:
        return None

    obs     = detect_order_blocks(candles)
    fvgs    = detect_fvg(candles)
    bos     = detect_bos(candles)
    sweeps  = detect_liquidity_sweep(candles)
    choch   = detect_choch(candles)
    rsi     = calc_rsi(candles)
    atr     = calc_atr(candles)
    closes  = [c["close"] for c in candles]
    ema20   = calc_ema(closes[-20:], 20)
    ema50   = calc_ema(closes[-50:], 50) if len(closes) >= 50 else calc_ema(closes, 20)

    k12, k26 = 2/13, 2/27
    e12 = e26 = closes[-1]
    for v in closes[-26:]:
        e12 = v*k12 + e12*(1-k12)
        e26 = v*k26 + e26*(1-k26)
    macd_val = round(e12 - e26, 3)

    recent_vols = [c["vol"] for c in candles[-20:]]
    avg_vol = sum(recent_vols) / len(recent_vols)
    vol_ratio = round(recent_vols[-1] / max(avg_vol, 0.01), 2)
    vol_spike = vol_ratio > 1.5

    price = candles[-1]["close"]
    bull_score = bear_score = 0
    reasons = []

    bull_obs = [o for o in obs if o["type"]=="bullish" and o["bottom"] <= price <= o["top"]+atr]
    bear_obs = [o for o in obs if o["type"]=="bearish" and o["bottom"]-atr <= price <= o["top"]]
    if bull_obs: bull_score += 25; reasons.append({"type":"bull","text":f"OB haussier actif (force {bull_obs[0]['strength']}%)"})
    if bear_obs: bear_score += 25; reasons.append({"type":"bear","text":f"OB baissier actif (force {bear_obs[0]['strength']}%)"})

    bull_fvg = [f for f in fvgs if f["type"]=="bullish" and f["bottom"]-atr/2 <= price <= f["top"]+atr]
    bear_fvg = [f for f in fvgs if f["type"]=="bearish" and f["bottom"]-atr <= price <= f["top"]+atr/2]
    if bull_fvg: bull_score += 20; reasons.append({"type":"bull","text":f"FVG haussier ({bull_fvg[0]['size']}$)"})
    if bear_fvg: bear_score += 20; reasons.append({"type":"bear","text":f"FVG baissier ({bear_fvg[0]['size']}$)"})

    if bos:
        lb = bos[-1]
        if lb["type"]=="bullish": bull_score += 15; reasons.append({"type":"bull","text":f"BOS haussier @ {lb['level']}"})
        else: bear_score += 15; reasons.append({"type":"bear","text":f"BOS baissier @ {lb['level']}"})

    if sweeps:
        ls = sweeps[-1]
        if ls["type"]=="buy_side": bull_score += 15; reasons.append({"type":"bull","text":f"Sweep acheteurs @ {ls['level']}"})
        else: bear_score += 15; reasons.append({"type":"bear","text":f"Sweep vendeurs @ {ls['level']}"})

    if choch:
        lc = choch[-1]
        if lc["type"]=="bullish": bull_score += 10; reasons.append({"type":"bull","text":"ChoCH haussier détecté"})
        else: bear_score += 10; reasons.append({"type":"bear","text":"ChoCH baissier détecté"})

    if rsi < 35: bull_score += 10; reasons.append({"type":"bull","text":f"RSI survendu ({rsi})"})
    elif rsi > 65: bear_score += 10; reasons.append({"type":"bear","text":f"RSI suracheté ({rsi})"})

    if price > ema20 > ema50: bull_score += 10; reasons.append({"type":"bull","text":f"EMA20 > EMA50 ({ema20})"})
    elif price < ema20 < ema50: bear_score += 10; reasons.append({"type":"bear","text":f"EMA20 < EMA50 ({ema20})"})

    if macd_val > 0: bull_score += 5; reasons.append({"type":"bull","text":f"MACD positif (+{macd_val})"})
    else: bear_score += 5; reasons.append({"type":"bear","text":f"MACD négatif ({macd_val})"})

    if vol_spike:
        lc2 = candles[-1]
        if lc2["close"] > lc2["open"]: bull_score += 8; reasons.append({"type":"bull","text":f"Volume spike haussier ({vol_ratio}x)"})
        else: bear_score += 8; reasons.append({"type":"bear","text":f"Volume spike baissier ({vol_ratio}x)"})

    total = bull_score + bear_score
    confidence = round(max(bull_score, bear_score) / max(total, 1) * 100)
    direction = "WAIT"
    if bull_score > bear_score and confidence >= 60: direction = "BUY"
    elif bear_score > bull_score and confidence >= 60: direction = "SELL"

    sl  = round(price - atr*1.5, 2) if direction=="BUY" else round(price + atr*1.5, 2)
    tp1 = round(price + atr*2,   2) if direction=="BUY" else round(price - atr*2,   2)
    tp2 = round(price + atr*3.5, 2) if direction=="BUY" else round(price - atr*3.5, 2)
    rr  = round(abs(tp1-price) / max(abs(sl-price), 0.01), 2)

    return {
        "direction": direction, "confidence": confidence,
        "bull_score": bull_score, "bear_score": bear_score,
        "reasons": reasons[:7], "price": price,
        "rsi": rsi, "atr": atr, "ema20": ema20, "ema50": ema50,
        "macd": macd_val, "vol_ratio": vol_ratio, "vol_spike": vol_spike,
        "obs": obs, "fvgs": fvgs, "bos": bos, "sweeps": sweeps, "choch": choch,
        "sl": sl, "tp1": tp1, "tp2": tp2, "rr": rr,
        "candles": candles[-40:], "candles_total": len(candles),
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }


# ─── AI ANALYSIS ─────────────────────────────────────────────────────────────
def get_ai_analysis(s, trades):
    wr = round(len([t for t in trades if t["result"]=="win"]) / max(len(trades),1) * 100) if trades else "N/A"
    prompt = f"""Tu es un expert SMC (Smart Money Concepts) spécialisé scalping XAU/USD 15min.
Donne une analyse directe, professionnelle et actionnable (max 130 mots) en français.

SIGNAL: {s['direction']} | Confiance: {s['confidence']}%
Prix: {s['price']} | RSI: {s['rsi']} | ATR: {s['atr']}
EMA20: {s['ema20']} | EMA50: {s['ema50']} | MACD: {s['macd']}
OB actifs: {len(s['obs'])} | FVG actifs: {len(s['fvgs'])}
BOS: {s['bos'][-1]['type'] if s['bos'] else 'aucun'}
Sweep: {s['sweeps'][-1]['type'] if s['sweeps'] else 'aucun'
