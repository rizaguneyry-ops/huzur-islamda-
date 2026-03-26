import streamlit as st
import requests
import json
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. SAYFA VE PREMIUM TEMA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# PREMIUM İSLAMİ ARKA PLAN RESMİ URL (Hat Sanatı ve Cami Silüeti, Koyu Tema Uyulu)
BG_IMAGE_URL = "https://images.rawpixel.com/image_800/bgauaW5kZXgvaW1hZ2VzL3Jhd3BpeGVsL2lkLzIwMDQ0MzA5LXJhd3BpeGVsLWltYWdlLmpwZw.jpg"

st.markdown(f"""
    <style>
    /* Arka Plan Resmi ve Karartma */
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.95)), url("{BG_IMAGE_URL}");
        background-size: cover; background-position: center; background-attachment: fixed; color: white;
    }}
    
    /* Üst Bilgi Paneli */
    .hero-section {{
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        padding: 25px; border-radius: 20px; text-align: center;
        border: 1px solid rgba(212, 175, 55, 0.3); margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .date-label {{ color: #d4af37; font-size: 20px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; }}
    .hijri-label {{ color: #4caf50; font-size: 17px; margin-bottom: 10px; font-style: italic; }}
    
    /* Vakit Kartları (3 ÜST, 3 ALT Gelişmiş Tasarım) */
    .vakit-card {{
        background: rgba(28, 33, 43, 0.7); padding: 20px; border-radius: 18px;
        text-align: center; border: 1px solid rgba(51, 65, 85, 0.5); margin-bottom: 12px; transition: 0.3s;
    }}
    .vakit-card:hover {{ border: 1px solid #d4af37; transform: translateY(-3px); box-shadow: 0 5px 15px rgba(212, 175, 55, 0.2); }}
    .vakit-name {{ color: #94a3b8; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }}
    .vakit-time {{ color: #d4af37; font-size: 24px; font-weight: bold; margin-top: 5px; }}

    /* EKSTRA UYGULAMA KUTULARI (Kapsül Tasarım) */
    .app-box {{
        background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }}
    
    .stButton>button {{
        width: 100%; border-radius: 15px; background: linear-gradient(90deg, #10b981, #d4af37);
        color: white; font-weight: bold; border: none; height: 55px; font-size: 18px;
    }}
    h1, h2, h3 {{ color: #d4af37; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. TÜRKÇE AY İSİMLERİ SÖZLÜĞÜ ---
tr_aylar = {
    "January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran",
    "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"
}
tr_hicri_aylar = {
    "Muharram": "Muharrem", "Safar": "Safer", "Rabi' al-awwal": "Rebiülevvel", "Rabi' al-thani": "Rebiülahir",
    "Jumada al-ula": "Cemaziyelevvel", "Jumada al-akhira": "Cemaziyelahir", "Rajab": "Recep", "Sha'ban": "Şaban",
    "Ramadan": "Ramazan", "Shawwal": "Şevval", "Dhu al-Qi'dah": "Zilkade", "Dhu al-Hijjah": "Zilhicce"
}

# --- 3. VERİ YÖNETİMİ ---
DB_FILE = "user_data.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump({"zikir": 0, "dualar": []}, f)
def load_data():
    with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
def save_data(d):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

user_data = load_data()

# --- 4. API VE GÖRÜNÜM ---
sehir = st.sidebar.selectbox("📍 Şehir Seç", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])

try:
    url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
    res = requests.get(url, timeout=10).json()['data']
    v = res['timings']
    h = res['date']['hijri']
    g = res['date']['gregorian']
    
    # Türkçe Tarih Dönüşümü
    g_tarih = f"{g['day']} {tr_aylar.get(g['month']['en'], g['month']['en'])} {g['year']}"
    h_tarih = f"{h['day']} {tr_hicri_aylar.get(h['month']['en'], h['month']['en'])} {h['year']}"

    # Vakit Sıralaması
    v_order = [("SABAH", v['Fajr']), ("GÜNEŞ", v['Sunrise']), ("ÖĞLE", v['Dhuhr']), ("İKİNDİ", v['Asr']), ("AKŞAM", v['Maghrib']), ("YATSI", v['Isha'])]

    # ÜST PANEL
    st.markdown(f"""
    <div class="hero-section">
        <div class="date-label">📅 {g_tarih}</div>
        <div class="hijri-label">🌙 {h_tarih}</div>
        <div style="font-size: 11px; color: #94a3b8; letter-spacing: 2px;">SIRADAKİ VAKTE KALAN</div>
    </div>
    """, unsafe_allow_html=True)

    # CANLI SAYAÇ (JS)
    countdown_html = f"""
    <div id="c_timer" style="color:#fbbf24; font-size:50px; font-family: 'Courier New', monospace; text-align:center; font-weight:bold; text-shadow:0 0 15px rgba(251,191,36,0.5);">--:--:--</div>
    <script>
        const v = {json.dumps({n: t for n, t in v_order})};
        function up() {{
            const now = new Date();
            const s = now.getHours()*3600 + now.getMinutes()*60 + now.getSeconds();
            let t = null;
            for(let n in v) {{
                let [h,m] = v[n].split(':');
                let vs = parseInt(h)*3600 + parseInt(m)*60;
                if(vs > s) {{ t = vs; break; }}
            }}
            if(!t) {{ let [h,m] = v['SABAH'].split(':'); t = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = t - s;
            let hrs = Math.floor(d/3600); let mns = Math.floor((d%3600)/60); let scs = d%60;
            document.getElementById('c_timer').innerHTML = (hrs<10?'0'+hrs:hrs)+":"+(mns<10?'0'+mns:mns)+":"+(scs<10?'0'+scs:scs);
        }}
        setInterval(up, 1000); up();
    </script>
    """
    components.html(countdown_html, height=100)

    # 3 ÜST - 3 ALT VAKİTLER (Gelişmiş Kart Tasarımı)
    st.write("") # Boşluk
    r1 = st.columns(3)
    for i in range(3):
        with r1[i]: st.markdown(f'<div class="vakit-card"><div class="vakit-name">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)
    r2 = st.columns(3)
    for i in range(3, 6):
        with r2[i-3]: st.markdown(f'<div class="vakit-card"><div class="vakit-name">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)

except: st.error("Vakitler yüklenemedi, internetinizi kontrol edin.")

# --- 5. EKSTRA UYGULAMA KUTULARI (Kapsül Tasarım) ---
st.divider()

# ZİKİRMATİK KUTUSU
with st.container():
    st.markdown('<div class="app-box">', unsafe_allow_html=True)
    st.subheader("📿 Zikirmatik")
    st.markdown(f"<h1 style='text-align:center; color:#fbbf24; font-size:90px; text-shadow:0 0 15px rgba(251,191,36,0.3);'>{user_data['zikir']}</h1>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK"):
        user_data['zikir'] += 1
        save_data(user_data)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ESMAÜ'L HÜSNA KUTUSU (Örneklenmiştir)
with st.container():
    st.markdown('<div class="app-box">', unsafe_allow_html=True)
    st.subheader("✨ Esmaü'l Hüsna")
    esma_list = [("Allah", "Tek İlah"), ("er-Rahmân", "Merhamet Eden"), ("er-Rahîm", "Bağışlayan"), ("el-Melik", "Hükümdar")]
    for i, a in esma_list: st.write(f"**{i}**: {a}")
    st.markdown('</div>', unsafe_allow_html=True)

# RADYO VE REHBER KUTUSU
with st.container():
    st.markdown('<div class="app-box">', unsafe_allow_html=True)
    st.subheader("📻 Diyanet Radyo")
    st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")
    st.info("📖 'Şüphesiz güçlükle beraber bir kolaylık vardır.'")
    st.markdown('</div>', unsafe_allow_html=True)