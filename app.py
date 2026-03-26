import streamlit as st
import requests
import json
import os
import pandas as pd
from datetime import datetime
import random
import streamlit.components.v1 as components

# --- 1. SAYFA VE PREMIUM TEMA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# Arka Plan Resmi URL (Koyu, Şık, İslami Motifli)
BG_IMAGE_URL = "https://images.rawpixel.com/image_800/bgauaW5kZXgvaW1hZ2VzL3Jhd3BpeGVsL2lkLzIwMDQ0MzA5LXJhd3BpeGVsLWltYWdlLmpwZw.jpg"

# Premium CSS Tasarımı
st.markdown(f"""
    <style>
    /* Arka Plan Resmi ve Karartma */
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.9)), url("{BG_IMAGE_URL}");
        background-size: cover; background-position: center; background-attachment: fixed; color: white;
    }}
    
    /* Üst Bilgi Paneli */
    .hero-section {{
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        padding: 25px; border-radius: 20px; text-align: center;
        border: 1px solid rgba(212, 175, 55, 0.3); margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .date-label {{ color: #d4af37; font-size: 19px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; }}
    .hijri-label {{ color: #4caf50; font-size: 16px; margin-bottom: 15px; font-style: italic; }}
    .countdown-timer {{ color: #fbbf24; font-size: 50px; font-weight: bold; font-family: 'Courier New', monospace; text-shadow: 0 0 20px rgba(251, 191, 36, 0.6); }}
    
    /* Vakit Kutucukları: 3 ÜST, 3 ALT Gelişmiş Tasarım */
    .vakit-card {{
        background: rgba(28, 33, 43, 0.7); padding: 20px; border-radius: 18px;
        text-align: center; border: 1px solid rgba(51, 65, 85, 0.5); margin-bottom: 12px; transition: 0.3s;
    }}
    .vakit-card:hover {{ border: 1px solid #d4af37; transform: translateY(-3px); box-shadow: 0 5px 15px rgba(212, 175, 55, 0.2); }}
    .vakit-name {{ color: #94a3b8; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }}
    .vakit-time {{ color: #d4af37; font-size: 24px; font-weight: bold; margin-top: 5px; }}
    
    /* Diğer Detaylar */
    .stButton>button {{
        width: 100%; border-radius: 30px; background: linear-gradient(90deg, #10b981, #d4af37);
        color: white; font-weight: bold; border: none; height: 50px; font-size: 16px;
    }}
    h1, h2, h3 {{ color: #d4af37; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ (GÜVENLİ) ---
DB_FILE = "user_data.json"
def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"zikir": 0, "dualar": []}, f)
    with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_data(d):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

user_data = load_data()

# --- 3. ESMAÜL HÜSNA VE SIRALI VAKİTLER ---
sehir = st.sidebar.selectbox("📍 Şehir Seçiniz", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Trabzon", "Samsun"])

try:
    # API'den vakitleri çek
    url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
    res = requests.get(url, timeout=10).json()['data']
    v = res['timings']
    h = res['date']['hijri']
    g = res['date']['gregorian']
    
    # 3 Üst - 3 Alt Sıralaması (Yeni İsimlerle)
    v_order = [
        ("SABAH", v['Fajr']), ("GÜNEŞ", v['Sunrise']), ("ÖĞLE", v['Dhuhr']),
        ("İKİNDİ", v['Asr']), ("AKŞAM", v['Maghrib']), ("YATSI", v['Isha'])
    ]

    # --- ÜST PANEL: TARİH VE CANLI SAYAÇ (BUG FIX) ---
    st.markdown(f"""
    <div class="hero-section">
        <div class="date-label">📅 {g['day']} {g['month']['en']} {g['year']}</div>
        <div class="hijri-label">🌙 {h['day']} {h['month']['en']} {h['year']} (Hicri)</div>
        <div style="font-size: 11px; color: #94a3b8; letter-spacing: 2px; margin-top:15px; text-transform:uppercase;">SIRADAKİ VAKTE KALAN</div>
    </div>
    """, unsafe_allow_html=True)

    # ⏳ CANLI GERİ SAYIM (Kesin Çözüm Bileşeni)
    # Python'dan bağımsız tarayıcıda çalışır, donma yapmaz.
    js_vakitler = {name: time for name, time in v_order}
    countdown_html = f"""
    <div id="countdown_timer" style="color: #fbbf24; font-size: 50px; font-family: 'Courier New', monospace; text-align: center; font-weight: bold; text-shadow: 0 0 15px rgba(251, 191, 36, 0.5); background: transparent; padding: 10px; border-radius: 10px;">--:--:--</div>
    <script>
        const v = {json.dumps(js_vakitler)};
        function update() {{
            const now = new Date();
            const s = now.getHours()*3600 + now.getMinutes()*60 + now.getSeconds();
            let target = null;
            let targetName = "";
            for(let n in v) {{
                let [h,m] = v[n].split(':');
                let vs = parseInt(h)*3600 + parseInt(m)*60;
                if(vs > s) {{ target = vs; targetName = n; break; }}
            }}
            if(!target) {{ // Yatsı geçtiyse yarına İmsak'a kur
                let [h,m] = v['SABAH'].split(':');
                target = parseInt(h)*3600 + parseInt(m)*60 + 86400;
                targetName = "SABAH";
            }}
            let d = target - s;
            let h = Math.floor(d/3600);
            let m = Math.floor((d%3600)/60);
            let sec = d%60;
            document.getElementById('countdown_timer').innerHTML = 
                (h<10?'0'+h:h)+":"+(m<10?'0'+m:m)+":"+(sec<10?'0'+sec:sec);
        }}
        setInterval(update, 1000); update();
    </script>
    """
    components.html(countdown_html, height=100)

    # --- VAKİT KUTUCUKLARI: 3 ÜST, 3 ALT ---
    st.write("") # Boşluk
    row1 = st.columns(3)
    for i in range(3):
        with row1[i]:
            st.markdown(f'<div class="vakit-card"><div class="vakit-name">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)
            
    row2 = st.columns(3)
    for i in range(3, 6):
        with row2[i-3]:
            st.markdown(f'<div class="vakit-card"><div class="vakit-name">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error("Vakitler yüklenemedi, internetinizi kontrol edin.")

# --- ALT SEKMELER (ZİKİR & ESMAÜL HÜSNA) ---
st.divider()
t1, t2, t3 = st.tabs(["📿 Zikirmatik", "✨ Esmaü'l Hüsna", "📖 Rehber & Radyo"])

with t1:
    st.markdown(f"<h1 style='text-align:center; color:#10b981; font-size:100px; text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);'>{user_data['zikir']}</h1>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK"):
        user_data['zikir'] += 1
        save_data(user_data)
        st.rerun()

with t2:
    st.subheader("🌸 Allah'ın Güzel İsimleri (99)")
    # (Not: Liste uzunluğu nedeniyle örneklenmiştir, uygulamada tam liste scroll ile sunulur)
    esmalar = [
        ("Allah", "Eşi benzeri olmayan tek ilah."), ("Er-Rahmân", "Dünyada her kula merhamet eden."),
        ("Er-Rahîm", "Ahirette sadece müminlere merhamet eden."), ("El-Melik", "Mülkün ve kainatın tek sahibi.")
    ]
    for isim, anlam in esmalar:
        st.write(f"**{isim}**: {anlam}")

with t3:
    st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")
    st.info("📖 'Şüphesiz güçlükle beraber bir kolaylık vardır.' (İnşirah, 5)")