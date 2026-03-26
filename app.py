import streamlit as st
import requests
import json
import os
from datetime import datetime
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# Premium CSS Tasarım ve Logo
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .logo-container { text-align: center; padding: 20px; border-bottom: 2px solid #d4af37; }
    .vakit-card { padding: 15px; border-radius: 12px; background: #1c212b; border-bottom: 4px solid #d4af37; text-align: center; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 30px; background: linear-gradient(135deg, #2e7d32, #d4af37); color: white; font-weight: bold; border: none; height: 50px; }
    .info-card { padding: 20px; border-radius: 15px; background: #262c36; border: 1px solid #4caf50; margin-bottom: 15px; }
    </style>
    <div class="logo-container">
        <div style="font-size: 50px;">🌙🕌</div>
        <div style="font-size: 30px; font-weight: bold; letter-spacing: 2px;">HUZUR İSLAMDA</div>
        <div style="color: #4caf50; font-style: italic;">Dijital İbadet Rehberi</div>
    </div>
    """, unsafe_allow_html=True)

# --- VERİ YÖNETİMİ ---
DB_FILE = "user_data.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"zikir": 0, "dualar": []}, f)

def load_data():
    with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_data(d):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# --- İÇERİKLER ---
ayetler = ["'Şüphesiz güçlükle beraber bir kolaylık vardır.' (İnşirah, 5)", "'Allah sabredenlerle beraberdir.' (Bakara, 153)"]
dini_gunler = [("Ramazan Başlangıcı", "19 Mart 2026"), ("Kurban Bayramı", "25 Haziran 2026")]

# --- SEKME YAPISI ---
t1, t2, t3, t4 = st.tabs(["📍 Vakitler", "📅 Rehber", "📖 Ayet/Hadis", "📿 Zikirmatik"])

with t1:
    sehir = st.selectbox("📍 Şehir Seç", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])
    try:
        res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
        st.success(f"🕌 Hicri: {res['date']['hijri']['day']} {res['date']['hijri']['month']['en']} {res['date']['hijri']['year']}")
        v = res['timings']
        cols = st.columns(3)
        v_list = [("İmsak", v['Fajr']), ("Öğle", v['Dhuhr']), ("İkindi", v['Asr']), ("Akşam", v['Maghrib']), ("Yatsı", v['Isha']), ("Güneş", v['Sunrise'])]
        for i, (ad, s) in enumerate(v_list):
            with cols[i%3]: st.markdown(f'<div class="vakit-card"><b>{ad}</b><br><span style="color:#d4af37">{s}</span></div>', unsafe_allow_html=True)
    except: st.error("Vakitler yüklenemedi.")

with t2:
    st.subheader("🗓️ 2026 Önemli Günler")
    for g, t in dini_gunler:
        st.info(f"**{g}**: {t}")
    with st.expander("📚 Kısa İlmihal"):
        st.write("İslamın Şartları: Kelime-i Şehadet, Namaz, Zekat, Oruç, Hac.")

with t3:
    st.markdown(f'<div class="info-card"><b>📖 Günün Ayeti:</b><br>{random.choice(ayetler)}</div>', unsafe_allow_html=True)
    st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")

with t4:
    st.markdown(f"<h1 style='text-align: center; color: #4caf50; font-size: 80px;'>{data['zikir']}</h1>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK"):
        data['zikir'] += 1
        save_data(data)
        st.rerun()