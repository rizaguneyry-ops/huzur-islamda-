import streamlit as st
import requests
import json
import os
from datetime import datetime
import random

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# Mobil ve Web İçin Gelişmiş Tasarım
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; font-family: 'Segoe UI', sans-serif; }
    .hero-section {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 20px; border-radius: 20px; text-align: center;
        border: 1px solid #334155; margin-bottom: 20px;
    }
    .date-label { color: #d4af37; font-size: 18px; font-weight: bold; margin: 2px 0; }
    .hijri-label { color: #10b981; font-size: 16px; margin-bottom: 10px; }
    .countdown-timer { color: #fbbf24; font-size: 45px; font-weight: bold; font-family: 'Courier New', monospace; }
    
    .vakit-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }
    .vakit-box {
        background: #1c212b; padding: 15px; border-radius: 15px;
        text-align: center; border-bottom: 3px solid #334155;
    }
    .active-vakit { border-bottom: 3px solid #10b981; background: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
DB_FILE = "user_data.json"
def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump({"zikir": 0, "dualar": []}, f)
    with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_data(d):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

user_data = load_data()

# --- 3. API VE VAKİT SIRALAMASI ---
sehir = st.sidebar.selectbox("📍 Şehir Seç", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])

try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    h = res['date']['hijri']
    g = res['date']['gregorian']
    
    # KESİN DOĞRU SIRALAMA
    v_order = [
        ("İmsak", v['Fajr']), ("Güneş", v['Sunrise']), ("Öğle", v['Dhuhr']),
        ("İkindi", v['Asr']), ("Akşam", v['Maghrib']), ("Yatsı", v['Isha'])
    ]

    # --- ÜST PANEL: TARİHLER VE GERİ SAYIM ---
    st.markdown(f"""
    <div class="hero-section">
        <div class="date-label">📅 {g['day']} {g['month']['en']} {g['year']}</div>
        <div class="hijri-label">🌙 {h['day']} {h['month']['en']} {h['year']} (Hicri)</div>
        <hr style="border: 0.5px solid #334155;">
        <div style="font-size: 12px; color: #94a3b8; letter-spacing: 2px;">SIRADAKİ VAKTE KALAN</div>
        <div id="countdown" class="countdown-timer">00:00:00</div>
    </div>
    
    <script>
    function startTimer() {{
        const times = {json.dumps({n: t for n, t in v_order})};
        setInterval(() => {{
            const now = new Date();
            const nowSec = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();
            let target = null;
            
            for (let n in times) {{
                let [h, m] = times[n].split(':');
                let vSec = parseInt(h) * 3600 + parseInt(m) * 60;
                if (vSec > nowSec) {{ target = vSec; break; }}
            }}
            
            if (!target) {{ // Yatsı geçtiyse yarına İmsak'a kur
                let [h, m] = times["İmsak"].split(':');
                target = parseInt(h) * 3600 + parseInt(m) * 60 + 86400;
            }}
            
            let diff = target - nowSec;
            let hrs = Math.floor(diff / 3600);
            let mins = Math.floor((diff % 3600) / 60);
            let secs = diff % 60;
            document.getElementById('countdown').innerHTML = 
                (hrs<10?'0'+hrs:hrs)+":"+(mins<10?'0'+mins:mins)+":"+(secs<10?'0'+secs:secs);
        }}, 1000);
    }}
    setTimeout(startTimer, 500); // Sayfa yüklenince başlat
    </script>
    """, unsafe_allow_html=True)

    # --- VAKİT KUTUCUKLARI ---
    cols = st.columns(2)
    for i, (name, time) in enumerate(v_order):
        with cols[i % 2]:
            st.markdown(f'<div class="vakit-box"><b>{name}</b><br><span style="color:#d4af37; font-size:20px;">{time}</span></div>', unsafe_allow_html=True)

except:
    st.error("Veriler alınamadı, internet bağlantınızı kontrol edin.")

# --- DİĞER BÖLÜMLER (Ayet, Hadis, Zikirmatik) ---
st.divider()
tab1, tab2, tab3 = st.tabs(["📖 Rehber & Sureler", "📿 Zikirmatik", "📻 Radyo"])

with tab1:
    st.info("📖 'Şüphesiz güçlükle beraber bir kolaylık vardır.' (İnşirah, 5)")
    with st.expander("📜 Kısa Namaz Sureleri"):
        st.write("**İhlas:** Kul hüvallahü ehad...")
        st.write("**Kevser:** İnna a'taynakel kevser...")
    with st.expander("📚 Temel İlmihal"):
        st.write("Abdestin Farzları: 1.Yüz, 2.Kollar, 3.Baş, 4.Ayaklar")

with tab2:
    st.markdown(f"<h2 style='text-align:center; color:#10b981;'>{user_data['zikir']}</h2>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK"):
        user_data['zikir'] += 1
        save_data(user_data)
        st.rerun()

with tab3:
    st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")