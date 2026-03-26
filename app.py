import streamlit as st
import requests
import json
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; font-family: 'Segoe UI', sans-serif; }
    .hero-section {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 20px; border-radius: 20px; text-align: center;
        border: 1px solid #334155; margin-bottom: 25px;
    }
    .date-info { color: #d4af37; font-size: 18px; font-weight: bold; margin-bottom: 5px; }
    .vakit-card {
        background: #1c212b; padding: 15px; border-radius: 15px;
        text-align: center; border: 1px solid #334155; margin-bottom: 10px;
    }
    .vakit-name { color: #94a3b8; font-size: 13px; font-weight: bold; }
    .vakit-time { color: #d4af37; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
DB_FILE = "user_data.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump({"zikir": 0, "dualar": []}, f)

def load_data():
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
    
    # 3 Üst - 3 Alt Sıralaması
    v_order = [
        ("SABAH", v['Fajr']), ("GÜNEŞ", v['Sunrise']), ("ÖĞLE", v['Dhuhr']),
        ("İKİNDİ", v['Asr']), ("AKŞAM", v['Maghrib']), ("YATSI", v['Isha'])
    ]

    # --- ÜST PANEL: TARİHLER ---
    st.markdown(f"""
    <div class="hero-section">
        <div class="date-info">📅 {g['day']} {g['month']['en']} {g['year']}</div>
        <div style="color: #10b981; font-weight: bold;">🌙 {h['day']} {h['month']['en']} {h['year']}</div>
        <div style="font-size: 11px; color: #94a3b8; letter-spacing: 2px; margin-top:15px;">SIRADAKİ VAKTE KALAN</div>
    </div>
    """, unsafe_allow_html=True)

    # --- CANLI GERİ SAYIM (Kesin Çözüm Bileşeni) ---
    # Bu kısım tarayıcıda izole çalışır, donma yapmaz.
    countdown_html = f"""
    <div id="timer" style="color: #fbbf24; font-size: 45px; font-family: monospace; text-align: center; font-weight: bold; background: #0b0e14; padding: 10px; border-radius: 10px;">00:00:00</div>
    <script>
        const times = {json.dumps({n: t for n, t in v_order})};
        function update() {{
            const now = new Date();
            const nowS = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();
            let target = null;
            for (let n in times) {{
                let [h, m] = times[n].split(':');
                let vS = parseInt(h) * 3600 + parseInt(m) * 60;
                if (vS > nowS) {{ target = vS; break; }}
            }}
            if (!target) {{
                let [h, m] = times["SABAH"].split(':');
                target = parseInt(h) * 3600 + parseInt(m) * 60 + 86400;
            }}
            let d = target - nowS;
            let hrs = Math.floor(d / 3600);
            let mns = Math.floor((d % 3600) / 60);
            let scs = d % 60;
            document.getElementById('timer').innerHTML = 
                (hrs<10?'0'+hrs:hrs)+":"+(mns<10?'0'+mns:mns)+":"+(scs<10?'0'+scs:scs);
        }}
        setInterval(update, 1000); update();
    </script>
    """
    components.html(countdown_html, height=100)

    # --- VAKİT KUTUCUKLARI: 3 ÜST, 3 ALT ---
    row1 = st.columns(3)
    for i in range(3):
        with row1[i]:
            st.markdown(f'<div class="vakit-card"><div class="vakit-name">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)
            
    row2 = st.columns(3)
    for i in range(3, 6):
        with row2[i-3]:
            st.markdown(f'<div class="vakit-card"><div class="vakit-name">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")

# --- ALT SEKMELER ---
st.divider()
t1, t2, t3 = st.tabs(["📿 Zikirmatik", "✨ Esmaü'l Hüsna", "📖 Rehber & Radyo"])

with t1:
    st.markdown(f"<h1 style='text-align:center; color:#10b981;'>{user_data['zikir']}</h1>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK"):
        user_data['zikir'] += 1
        save_data(user_data)
        st.rerun()

with t2:
    st.subheader("🌸 Allah'ın Güzel İsimleri")
    # Esma listesi (Örneklenmiştir, ihtiyaca göre 99'a tamamlanabilir)
    esmalar = [("Allah", "Tek İlah"), ("er-Rahmân", "Merhamet Eden"), ("er-Rahîm", "Bağışlayan"), ("el-Melik", "Hükümdar")]
    for isim, anlam in esmalar:
        st.write(f"**{isim}**: {anlam}")

with t3:
    st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")
    st.info("📖 'Şüphesiz güçlükle beraber bir kolaylık vardır.' (İnşirah, 5)")