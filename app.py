import streamlit as st
import requests
import json
import os
import pandas as pd
from datetime import datetime
import random

# --- 1. GLOBAL HATA YÖNETİMİ VE SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# CSS ile Profesyonel Logo ve Premium Tasarım
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .logo-container { text-align: center; padding: 20px 0; border-bottom: 2px solid #2e7d32; margin-bottom: 20px; }
    .logo-symbol { font-size: 50px; color: #d4af37; text-shadow: 0 0 15px rgba(212, 175, 55, 0.5); }
    .logo-text { font-size: 30px; font-weight: bold; color: white; letter-spacing: 3px; margin-top: -10px; }
    .vakit-card { padding: 15px; border-radius: 12px; background: #1c212b; border-bottom: 4px solid #d4af37; text-align: center; margin-bottom: 10px; }
    .info-card { padding: 20px; border-radius: 15px; background: #262c36; border: 1px solid #4caf50; margin-bottom: 15px; }
    .stButton>button { width: 100%; border-radius: 30px; background: linear-gradient(135deg, #2e7d32 0%, #d4af37 100%); color: white; font-weight: bold; border: none; height: 50px; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3); }
    </style>
    <div class="logo-container">
        <div class="logo-symbol">🌙🕌</div>
        <div class="logo-text">HUZUR İSLAMDA</div>
        <div style="color: #4caf50; font-style: italic;">Dijital İbadet ve Rehber Portalı</div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. GÜVENLİ VERİ YÖNETİMİ (JSON DATABASE) ---
DB_FILE = "user_data.json"

def initialize_db():
    if not os.path.exists(DB_FILE):
        default_data = {"dualar": [], "zikir": 0, "logs": []}
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False)

def load_safe_data():
    initialize_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"dualar": [], "zikir": 0, "logs": []}

def save_safe_data(d):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Veri kaydedilemedi: {e}")

user_data = load_safe_data()

# --- 3. İÇERİK HAVUZU ---
ayetler = ["'Şüphesiz güçlükle beraber bir kolaylık vardır.' (İnşirah, 5)", "'Allah sabredenlerle beraberdir.' (Bakara, 153)"]
hadisler = ["'Ameller niyetlere göredir.'", "'Temizlik imanın yarısıdır.'"]
dini_gunler = [("Ramazan Başlangıcı", "19 Mart 2026"), ("Kurban Bayramı", "25 Haziran 2026"), ("Mevlid Kandili", "22 Eylül 2026")]

# --- 4. ANA ARAYÜZ (TABS) ---
t1, t2, t3, t4 = st.tabs(["📍 Vakitler", "📅 Takvim & Rehber", "📖 Ayet/Hadis/Radyo", "📿 Zikirmatik"])

with t1:
    sehir = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana"])
    try:
        # Zaman aşımına karşı güvenli API isteği
        response = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13", timeout=10)
        res_data = response.json()['data']
        v = res_data['timings']
        st.info(f"🕌 Hicri: {res_data['date']['hijri']['day']} {res_data['date']['hijri']['month']['en']} {res_data['date']['hijri']['year']}")
        
        c = st.columns(3)
        v_list = [("İmsak", v['Fajr']), ("Öğle", v['Dhuhr']), ("İkindi", v['Asr']), ("Akşam", v['Maghrib']), ("Yatsı", v['Isha']), ("Güneş", v['Sunrise'])]
        for i, (ad, s) in enumerate(v_list):
            with c[i%3]: st.markdown(f'<div class="vakit-card"><b>{ad}</b><br><span style="color:#d4af37; font-size:18px">{s}</span></div>', unsafe_allow_html=True)
    except Exception:
        st.warning("Vakit bilgileri alınırken bir sorun oluştu. Lütfen sayfayı yenileyin.")

with t2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🗓️ Önemli Günler")
        for g, t in dini_gunler:
            st.markdown(f'<div style="background:#1c212b; padding:10px; border-radius:10px; margin-bottom:5px; border-left:3px solid #d4af37;">{g}<br><small>{t}</small></div>', unsafe_allow_html=True)
    with col_b:
        st.subheader("📚 Kısa İlmihal")
        with st.expander("İslamın Şartları"): st.write("1. Şehadet\n2. Namaz\n3. Zekat\n4. Oruç\n5. Hac")
        with st.expander("Abdest"): st.write("1. Yüz\n2. Kollar\n3. Baş\n4. Ayaklar")

with t3:
    st.markdown(f'<div class="info-card"><b>📖 Günün Ayeti:</b><br>{random.choice(ayetler)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card"><b>💬 Günün Hadisi:</b><br>{random.choice(hadisler)}</div>', unsafe_allow_html=True)
    st.subheader("📻 Canlı Radyo")
    st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")

with t4:
    st.markdown(f"<h1 style='text-align: center; color: #4caf50; font-size: 80px;'>{user_data['zikir']}</h1>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK"):
        user_data['zikir'] += 1
        save_safe_data(user_data)
        st.rerun()
    if st.button("🔄 SIFIRLA"):
        user_data['zikir'] = 0
        save_safe_data(user_data)
        st.rerun()