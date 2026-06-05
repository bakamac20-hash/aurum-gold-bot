import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AURUM XAUUSD BOT",
    page_icon="📈",
    layout="wide"
)

# --------------------------------------------------
# STYLE
# --------------------------------------------------

st.markdown("""
<style>
.stApp{
    background-color:#0d1117;
    color:white;
}

.buy{
    color:#00ff88;
    font-size:32px;
    font-weight:bold;
}

.sell{
    color:#ff4d4d;
    font-size:32px;
    font-weight:bold;
}

.wait{
    color:#ffd700;
    font-size:32px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATA
# --------------------------------------------------

@st.cache_data(ttl=300)
def load_data():

    symbol = "GC=F"

    data = yf.download(
        symbol,
        period="5d",
        interval="15m",
        auto_adjust=True,
        progress=False
    )

    return data

df = load_data()

if df.empty:
    st.error("Impossible de récupérer les données.")
    st.stop()

# --------------------------------------------------
# EMA
# --------------------------------------------------

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

df["EMA20"] = ema(df["Close"], 20)
df["EMA50"] = ema(df["Close"], 50)

# --------------------------------------------------
# RSI
# --------------------------------------------------

def rsi(series, period=14):

    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))

df["RSI"] = rsi(df["Close"])

# --------------------------------------------------
# ATR
# --------------------------------------------------

def atr(data, period=14):

    high_low = data["High"] - data["Low"]

    high_close = np.abs(
        data["High"] - data["Close"].shift()
    )

    low_close = np.abs(
        data["Low"] - data["Close"].shift()
    )

    ranges = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    )

    true_range = np.max(ranges, axis=1)

    return pd.Series(true_range).rolling(period).mean()

df["ATR"] = atr(df)

# --------------------------------------------------
# MACD
# --------------------------------------------------

ema12 = df["Close"].ewm(span=12).mean()
ema26 = df["Close"].ewm(span=26).mean()

df["MACD"] = ema12 - ema26
df["SIGNAL"] = df["MACD"].ewm(span=9).mean()

# --------------------------------------------------
# PRIX ACTUEL
# --------------------------------------------------

price = float(df["Close"].iloc[-1])

ema20 = float(df["EMA20"].iloc[-1])
ema50 = float(df["EMA50"].iloc[-1])

rsi_now = float(df["RSI"].iloc[-1])
atr_now = float(df["ATR"].iloc[-1])

macd_now = float(df["MACD"].iloc[-1])

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("AURUM XAU/USD BOT")

st.caption(
    f"Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}"
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Prix", round(price, 2))
c2.metric("RSI", round(rsi_now, 2))
c3.metric("ATR", round(atr_now, 2))
c4.metric("MACD", round(macd_now, 2))  
# ==================================================
# GRAPHIQUE CANDLESTICK
# ==================================================

def plot_chart(data):

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="XAUUSD"
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["EMA20"],
        line=dict(color="orange", width=1),
        name="EMA20"
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["EMA50"],
        line=dict(color="blue", width=1),
        name="EMA50"
    ))

    fig.update_layout(
        template="plotly_dark",
        height=600,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_rangeslider_visible=False
    )

    return fig


st.subheader("Graphique XAU/USD")

st.plotly_chart(plot_chart(df), use_container_width=True)


# ==================================================
# BOS / CHOCH / FVG SIMPLIFIÉ
# ==================================================

def detect_structure(data):

    highs = data["High"].values
    lows = data["Low"].values
    closes = data["Close"].values

    bos = []
    choch = []
    fvg = []

    for i in range(5, len(data)-1):

        # Break of Structure
        if closes[i] > max(highs[i-5:i]):
            bos.append("bullish")

        if closes[i] < min(lows[i-5:i]):
            bos.append("bearish")

        # Change of Character
        if closes[i] > closes[i-1] > closes[i-2] and closes[i] < closes[i-3]:
            choch.append("bearish")

        if closes[i] < closes[i-1] < closes[i-2] and closes[i] > closes[i-3]:
            choch.append("bullish")

        # Fair Value Gap simple
        if lows[i] > highs[i-2]:
            fvg.append("bullish")

        if highs[i] < lows[i-2]:
            fvg.append("bearish")

    return bos, choch, fvg


bos, choch, fvg = detect_structure(df)


# ==================================================
# SCORE SIMPLE
# ==================================================

bull = 0
bear = 0

if ema20 > ema50:
    bull += 1
else:
    bear += 1

if rsi_now < 40:
    bull += 1
elif rsi_now > 60:
    bear += 1

if macd_now > 0:
    bull += 1
else:
    bear += 1

if len(bos) > len(choch):
    bull += 1
else:
    bear += 1


total = bull + bear
confidence = round(max(bull, bear) / max(total, 1) * 100)


if bull > bear and confidence >= 60:
    signal = "BUY"
elif bear > bull and confidence >= 60:
    signal = "SELL"
else:
    signal = "WAIT"


# ==================================================
# AFFICHAGE SIGNAL
# ==================================================

st.subheader("Signal SMC")

if signal == "BUY":
    st.markdown(f"<div class='buy'>BUY 🔼</div>", unsafe_allow_html=True)
elif signal == "SELL":
    st.markdown(f"<div class='sell'>SELL 🔽</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='wait'>WAIT ⏸</div>", unsafe_allow_html=True)

st.metric("Confiance", f"{confidence} %")


# ==================================================
# TP / SL
# ==================================================

sl = price - atr_now * 1.5 if signal == "BUY" else price + atr_now * 1.5
tp1 = price + atr_now * 2 if signal == "BUY" else price - atr_now * 2
tp2 = price + atr_now * 3 if signal == "BUY" else price - atr_now * 3

col1, col2, col3 = st.columns(3)

col1.metric("Stop Loss", round(sl, 2))
col2.metric("Take Profit 1", round(tp1, 2))
col3.metric("Take Profit 2", round(tp2, 2))

# ==================================================
# DASHBOARD GLOBAL
# ==================================================

st.subheader("Dashboard SMC")

c1, c2, c3, c4 = st.columns(4)

c1.metric("EMA20", round(ema20, 2))
c2.metric("EMA50", round(ema50, 2))
c3.metric("RSI", round(rsi_now, 2))
c4.metric("ATR", round(atr_now, 2))


# ==================================================
# ANALYSE SMC AVANCÉE (AMÉLIORATION DU SCORE)
# ==================================================

structure_score = 0

# tendance EMA
if ema20 > ema50:
    structure_score += 2
else:
    structure_score -= 2

# momentum RSI
if rsi_now < 30:
    structure_score += 2
elif rsi_now > 70:
    structure_score -= 2

# MACD momentum
if macd_now > 0:
    structure_score += 1
else:
    structure_score -= 1

# structure marché
if len(bos) > len(choch):
    structure_score += 2
else:
    structure_score -= 2

# FVG bias
bull_fvg = len([x for x in fvg if x == "bullish"])
bear_fvg = len([x for x in fvg if x == "bearish"])

structure_score += (bull_fvg - bear_fvg)


# ==================================================
# SIGNAL FINAL (VERSION PROPRE)
# ==================================================

if structure_score >= 4:
    signal = "BUY"
    confidence = min(95, 60 + structure_score * 5)

elif structure_score <= -4:
    signal = "SELL"
    confidence = min(95, 60 + abs(structure_score) * 5)

else:
    signal = "WAIT"
    confidence = 50


# ==================================================
# SIGNAL DISPLAY
# ==================================================

st.subheader("Signal Final (SMC Engine)")

if signal == "BUY":
    st.markdown("<div class='buy'>BUY 🔼</div>", unsafe_allow_html=True)

elif signal == "SELL":
    st.markdown("<div class='sell'>SELL 🔽</div>", unsafe_allow_html=True)

else:
    st.markdown("<div class='wait'>WAIT ⏸</div>", unsafe_allow_html=True)

st.metric("Confiance SMC", f"{confidence} %")


# ==================================================
# MINI TRADE LOG (SESSION)
# ==================================================

if "trade_log" not in st.session_state:
    st.session_state.trade_log = []


trade_entry = {
    "time": datetime.now().strftime("%H:%M:%S"),
    "price": price,
    "signal": signal,
    "confidence": confidence
}

# éviter duplication à chaque refresh
if len(st.session_state.trade_log) == 0 or st.session_state.trade_log[-1] != trade_entry:
    st.session_state.trade_log.append(trade_entry)


# ==================================================
# AFFICHAGE HISTORIQUE
# ==================================================

st.subheader("Historique des signaux")

for trade in reversed(st.session_state.trade_log[-10:]):

    if trade["signal"] == "BUY":
        st.write(f"🟢 {trade['time']} | BUY | {trade['price']} | {trade['confidence']}%")

    elif trade["signal"] == "SELL":
        st.write(f"🔴 {trade['time']} | SELL | {trade['price']} | {trade['confidence']}%")

    else:
        st.write(f"🟡 {trade['time']} | WAIT | {trade['price']} | {trade['confidence']}%")
# ==================================================
# AUTO REFRESH (STREAMLIT LIVE MODE)
# ==================================================

st.markdown("---")

st.subheader("Contrôle")

colA, colB, colC = st.columns(3)

with colA:
    if st.button("🔄 Rafraîchir"):
        st.rerun()

with colB:
    if st.button("🧹 Reset historique"):
        st.session_state.trade_log = []
        st.success("Historique supprimé")

with colC:
    auto = st.toggle("Auto-refresh (30s)", value=False)

if auto:
    time.sleep(30)
    st.rerun()


# ==================================================
# FILTRE ANTI-BRUIT FINAL
# ==================================================

# on stabilise le signal pour éviter flickering
if len(st.session_state.trade_log) >= 3:

    last_signals = [t["signal"] for t in st.session_state.trade_log[-3:]]

    if last_signals.count("BUY") >= 2:
        final_bias = "BUY"
    elif last_signals.count("SELL") >= 2:
        final_bias = "SELL"
    else:
        final_bias = "WAIT"

else:
    final_bias = signal


# ==================================================
# SIGNAL STABILISÉ
# ==================================================

st.subheader("Signal Stabilisé")

if final_bias == "BUY":
    st.markdown("<div class='buy'>BUY CONFIRMÉ 🔼</div>", unsafe_allow_html=True)

elif final_bias == "SELL":
    st.markdown("<div class='sell'>SELL CONFIRMÉ 🔽</div>", unsafe_allow_html=True)

else:
    st.markdown("<div class='wait'>MARCHÉ INCERTAIN ⏸</div>", unsafe_allow_html=True)


# ==================================================
# DISCLAIMER
# ==================================================

st.markdown("""
---
⚠️ Analyse automatique basée sur indicateurs techniques (EMA, RSI, MACD, structure simplifiée SMC).  
Ce système ne constitue pas un conseil financier.  
""")
