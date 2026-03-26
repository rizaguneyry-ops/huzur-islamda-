‎import streamlit as st
‎import requests
‎import json
‎import os
‎import pandas as pd
‎from datetime import datetime
‎
‎# 1. SAYFA AYARLARI
‎st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")
‎
‎# 2. GÖRSEL TASARIM (CSS)
‎st.markdown("""
‎    <style>
‎    .stApp { background-color: #0e1117; color: white; }
‎    .vakit-card { padding: 15px; border-radius: 12px; background: #1c1f26; border: 1px solid #2e7d32; text-align: center; margin-bottom: 10px; }
‎    .stButton>button { width: 100%; border-radius: 20px; background-color: #2e7d32; color: white; border: none; }
‎    .stButton>button:hover { background-color: #4caf50; }
‎    </style>
‎    """, unsafe_allow_html=True)
‎
‎# 3. VERİ TABANI SİSTEMİ
‎DB_FILE = "user_data.json"
‎if not os.path.exists(DB_FILE):
‎    with open(DB_FILE, "w") as f: json.dump({"dualar":[], "zikir":0}, f)
‎
‎def load_data():
‎    with open(DB_FILE, "r") as f: return json.load(f)
‎def save_data(d):
‎    with open(DB_FILE, "w") as f: json.dump(d, f)
‎
‎data = load_data()
‎
‎# 4. ANA BAŞLIK VE SEKME YAPISI
‎st.title("🌙 Huzur İslamda v2.0")
‎tabs = st.tabs(["📍 Vakitler", "📿 Zikirmatik", "📝 Dualarım", "📻 Radyo"])
‎
‎# --- SEKME 1: VAKİTLER ---
‎with tabs[0]:
‎    sehir = st.selectbox("Şehir Seç", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])
‎    try:
‎        url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
‎        v = requests.get(url).json()['data']['timings']
‎        cols = st.columns(3)
‎        v_list = [("İmsak", v['Fajr']), ("Öğle", v['Dhuhr']), ("İkindi", v['Asr']), ("Akşam", v['Maghrib']), ("Yatsı", v['Isha']), ("Güneş", v['Sunrise'])]
‎        for i, (ad, s) in enumerate(v_list):
‎            with cols[i%3]: st.markdown(f'<div class="vakit-card"><b style="color:#4caf50">{ad}</b><br>{s}</div>', unsafe_allow_html=True)
‎    except: st.warning("İnternet bağlantısını kontrol edin.")
‎
‎# --- SEKME 2: ZİKİRMATİK ---
‎with tabs[1]:
‎    st.markdown(f"<h1 style='text-align: center; color: #4caf50;'>{data['zikir']}</h1>", unsafe_allow_html=True)
‎    if st.button("➕ ZİKİR ÇEK", use_container_width=True):
‎        data['zikir'] += 1
‎        save_data(data)
‎        st.rerun()
‎    if st.button("🔄 Sıfırla"):
‎        data['zikir'] = 0
‎        save_data(data)
‎        st.rerun()
‎
‎# --- SEKME 3: DUALARIM ---
‎with tabs[2]:
‎    yeni = st.text_area("Duanızı buraya yazın...")
‎    if st.button("Kaydet") and yeni:
‎        data['dualar'].append({"m": yeni, "t": datetime.now().strftime("%d.%m %H:%M")})
‎        save_data(data)
‎        st.success("Duanız kaydedildi.")
‎        st.rerun()
‎    st.divider()
‎    for d in reversed(data['dualar']):
‎        st.info(f"{d['m']} \n\n *Tarih: {d['t']}*")
‎
‎# --- SEKME 4: RADYO ---
‎with tabs[3]:
‎    st.subheader("📻 Diyanet Radyo Canlı")
‎    st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")
‎    st.write("Zikir çekerken arka planda dinleyebilirsiniz.")
‎