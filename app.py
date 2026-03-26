import streamlit as st
import requests
import json
import os
from datetime import datetime
import random
import streamlit.components.v1 as components

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# Modern Mobil CSS
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; }
    
    /* Üst Bilgi Paneli */
    .hero-section {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 30px;
        border-radius: 25px;
        text-align: center;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
    .next-prayer-label { color: #94a3b8; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; }
    .next-prayer-time { color: #fbbf24; font-size: 45px; font-weight: bold; margin: 10px 0; }
    
    /* Vakit Kartları Grid */
    .vakit-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin-bottom: 20px;
    }
    .vakit-item {
        background: #1e293b;
        padding: 15px;
        border-radius: 18px;
        text-align: center;
        border: 1px solid #334155;
    }
    .vakit-name { color: #94a3b8; font-size: 13px; }
    .vakit-hour { color: white; font-size: 20px; font-weight: bold; margin-top: 5px; }
    .active-vakit { border: 2px solid #10b981 !important; background: #064e3b !important; }

    /* Alt Menü ve Butonlar */
    .stButton>button {
        width: 100%; border-radius: 15px; background: #10b981; color: white;
        font-weight: bold; border: none; height: 50px; font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ VE API ---
DB_FILE = "user_data.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f: json.dump({"zikir": 0, "dualar": []}, f)

def get_vakitler(sehir):
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
        data = requests.get(url).json()['data']
        t = data['timings']
        # Sıralı liste
        return [
            ("İmsak", t['Fajr']), ("Güneş", t['Sunrise']), ("Öğle", t['Dhuhr']),
            ("İkindi", t['Asr']), ("Akşam", t['Maghrib']), ("Yatsı", t['Isha'])
        ], data['date']['hijri']
    except: return None, None

# --- 3. ARAYÜZ ---
st.markdown('<div style="text-align:center; padding:10px;"><h3>🌙 HUZUR İSLAMDA</h3></div>', unsafe_allow_html=True)

sehir = st.sidebar.selectbox("Şehir Değiştir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Trabzon"], index=0)
vakit_listesi, hicri = get_vakitler(sehir)

if vakit_listesi:
    # --- GERİ SAYIM ALGORİTMASI (JavaScript) ---
    now = datetime.now()
    current_time_str = now.strftime("%H:%M:%S")
    
    # JavaScript için vakitleri hazırla
    js_vakitler = {name: time for name, time in vakit_listesi}
    
    st.markdown(f"""
    <div class="hero-section">
        <div class="next-prayer-label">SIRADAKİ VAKİT</div>
        <div id="countdown" class="next-prayer-time">Hesaplanıyor...</div>
        <div style="color:#10b981">{hicri['day']} {hicri['month']['en']} {hicri['year']}</div>
    </div>

    <script>
    function startTimer() {{
        const vakitler = {json.dumps(js_vakitler)};
        const now = new Date();
        const currentTime = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();
        
        let targetTime = null;
        let targetName = "";
        
        for (let name in vakitler) {{
            let [h, m] = vakitler[name].split(':');
            let vSeconds = parseInt(h) * 3600 + parseInt(m) * 60;
            
            if (vSeconds > currentTime) {{
                targetTime = vSeconds;
                targetName = name;
                break;
            }}
        }}
        
        // Eğer tüm vakitler geçtiyse yarına (İmsak) kur
        if (!targetTime) {{
            let [h, m] = vakitler["İmsak"].split(':');
            targetTime = parseInt(h) * 3600 + parseInt(m) * 60 + 86400;
            targetName = "İmsak";
        }}

        setInterval(() => {{
            const n = new Date();
            const curr = n.getHours() * 3600 + n.getMinutes() * 60 + n.getSeconds();
            let diff = targetTime - curr;
            
            let hours = Math.floor(diff / 3600);
            let mins = Math.floor((diff % 3600) / 60);
            let secs = diff % 60;
            
            document.getElementById('countdown').innerHTML = 
                (hours < 10 ? "0"+hours : hours) + ":" + 
                (mins < 10 ? "0"+mins : mins) + ":" + 
                (secs < 10 ? "0"+secs : secs);
        }}, 1000);
    }}
    startTimer();
    </script>
    """, unsafe_allow_html=True)

    # --- VAKİT KUTUCUKLARI (Grid) ---
    cols = st.columns(2)
    for i, (name, time) in enumerate(v_list := vakit_listesi):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="vakit-item">
                    <div class="vakit-name">{name}</div>
                    <div class="vakit-hour">{time}</div>
                </div>
            """, unsafe_allow_html=True)

# --- ALT MENÜ (Zikirmatik & Radyo) ---
st.divider()
tab1, tab2 = st.tabs(["📿 Zikirmatik", "📻 Radyo"])

with tab1:
    with open(DB_FILE, "r") as f: d = json.load(f)
    st.markdown(f"<h2 style='text-align:center;'>{d['zikir']}</h2>", unsafe_allow_html=True)
    if st.button("ZİKİR ÇEK"):
        d['zikir'] += 1
        with open(DB_FILE, "w") as f: json.dump(d, f)
        st.rerun()

with tab2:
    st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")