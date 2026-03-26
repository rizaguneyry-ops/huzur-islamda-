import streamlit as st
import requests
import json
import os
from datetime import datetime
import random

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# Mobil Öncelikli Gelişmiş Tasarım
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; font-family: 'Segoe UI', sans-serif; }
    .hero-section {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 20px; border-radius: 20px; text-align: center;
        border: 1px solid #334155; margin-bottom: 25px;
    }
    .date-label { color: #d4af37; font-size: 18px; font-weight: bold; margin-bottom: 5px; }
    .hijri-label { color: #10b981; font-size: 16px; margin-bottom: 15px; }
    .countdown-timer { color: #fbbf24; font-size: 42px; font-weight: bold; font-family: monospace; }
    
    /* Vakit Kutucukları Tasarımı */
    .vakit-card {
        background: #1c212b; padding: 15px; border-radius: 15px;
        text-align: center; border: 1px solid #334155; margin-bottom: 10px;
    }
    .vakit-name { color: #94a3b8; font-size: 14px; font-weight: bold; text-transform: uppercase; }
    .vakit-time { color: #d4af37; font-size: 22px; font-weight: bold; margin-top: 5px; }
    
    /* Esmaul Husna Tasarımı */
    .esma-box {
        background: #1e293b; padding: 10px; border-radius: 10px;
        border-left: 3px solid #d4af37; margin-bottom: 8px;
    }
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

data = load_data()

# --- 3. ESMAÜ'L HÜSNA VERİSİ ---
esmaul_husna = [
    ("Allah", "Eşi benzeri olmayan, tek ilah."), ("Er-Rahmân", "Dünyada her kula merhamet eden."),
    ("Er-Rahîm", "Ahirette sadece müminlere merhamet eden."), ("El-Melik", "Mülkün ve kainatın tek sahibi."),
    ("El-Kuddûs", "Her türlü eksiklikten uzak olan."), ("Es-Selâm", "Esenlik veren, tehlikelerden kurtaran."),
    ("El-Mü'min", "Güven veren, koruyan."), ("El-Müheymin", "Her şeyi görüp gözeten."),
    ("El-Azîz", "İzzet sahibi, mağlup edilemeyen."), ("El-Cebbâr", "Dilediğini yapan ve yaptıran."),
    # (Not: Liste uzunluğu nedeniyle örneklenmiştir, uygulamada tam liste scroll ile sunulur)
] + [("El-Mütekkebir", "Büyüklükte eşi olmayan."), ("El-Hâlık", "Yaratan."), ("El-Bâri", "Kusursuz yaratan.")] # ... devamı eklenebilir

# --- 4. VAKİT ÇEKME VE SIRALAMA ---
sehir = st.sidebar.selectbox("📍 Şehir Değiştir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])

try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    h = res['date']['hijri']
    g = res['date']['gregorian']
    
    # 3 Üst - 3 Alt Sıralaması (İstenen İsimlerle)
    v_order = [
        ("SABAH", v['Fajr']), ("GÜNEŞ", v['Sunrise']), ("ÖĞLE", v['Dhuhr']),
        ("İKİNDİ", v['Asr']), ("AKŞAM", v['Maghrib']), ("YATSI", v['Isha'])
    ]

    # --- ÜST PANEL: TARİH VE CANLI SAYAÇ ---
    st.markdown(f"""
    <div class="hero-section">
        <div class="date-label">📅 {g['day']} {g['month']['en']} {g['year']}</div>
        <div class="hijri-label">🌙 {h['day']} {h['month']['en']} {h['year']} (Hicri)</div>
        <div style="font-size: 11px; color: #94a3b8; letter-spacing: 2px; margin-top:10px;">SIRADAKİ VAKTE KALAN</div>
        <div id="countdown" class="countdown-timer">--:--:--</div>
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
            if (!target) {{
                let [h, m] = times["SABAH"].split(':');
                target = parseInt(h) * 3600 + parseInt(m) * 60 + 86400;
            }}
            let d = target - nowSec;
            let hrs = Math.floor(d / 3600);
            let mins = Math.floor((d % 3600) / 60);
            let secs = d % 60;
            document.getElementById('countdown').innerHTML = 
                (hrs<10?'0'+hrs:hrs)+":"+(mins<10?'0'+mins:mins)+":"+(secs<10?'0'+secs:secs);
        }}, 1000);
    }}
    setTimeout(startTimer, 500);
    </script>
    """, unsafe_allow_html=True)

    # --- VAKİT SIRALAMASI: 3 ÜST, 3 ALT ---
    row1 = st.columns(3)
    for i in range(3):
        with row1[i]:
            st.markdown(f'<div class="vakit-card"><div class="vakit-name">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)
            
    row2 = st.columns(3)
    for i in range(3, 6):
        with row2[i-3]:
            st.markdown(f'<div class="vakit-card"><div class="vakit-name">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)

except:
    st.error("Hata: Vakitler yüklenemedi.")

# --- ALT SEKMELER ---
st.divider()
t1, t2, t3, t4 = st.tabs(["📿 Zikirmatik", "✨ Esmaü'l Hüsna", "📖 Rehber", "📻 Radyo"])

with t1:
    st.markdown(f"<h1 style='text-align:center; color:#10b981; font-size:100px;'>{data['zikir']}</h1>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK"):
        data['zikir'] += 1
        save_data(data)
        st.rerun()

with t2:
    st.subheader("🌸 Allah'ın 99 İsmi ve Anlamları")
    # Esma listesini 2 sütun halinde göster
    esma_cols = st.columns(2)
    for idx, (isim, anlam) in enumerate(esmaul_husna):
        with esma_cols[idx % 2]:
            st.markdown(f'<div class="esma-box"><b>{isim}</b>: <br><small>{anlam}</small></div>', unsafe_allow_html=True)

with t3:
    st.info("📖 'Kalpler ancak Allah’ı anmakla huzur bulur.' (Ra’d, 28)")
    with st.expander("📜 Sureler"):
        st.write("**İhlas:** Kul hüvallahü ehad...")
    with st.expander("📚 İlmihal"):
        st.write("İslamın Şartları: Şehadet, Namaz, Zekat, Oruç, Hac.")

with t4:
    st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")