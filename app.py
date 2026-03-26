import streamlit as st
import requests
import json
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. SAYFA VE PREMIUM TEMA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# Tasarımdaki Cami Arka Planı (Mavi Camii - İstanbul)
BG_IMAGE_URL = "https://cdn.pixabay.com/photo/2023/03/05/13/21/mosque-7831383_1280.png"

# Premium CSS Tasarımı (Altın, Zümrüt Yeşili ve Krem Tonları)
st.markdown(f"""
    <style>
    /* Arka Plan Resmi ve Karartma (Okunabilirlik için) */
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.9)), url("{BG_IMAGE_URL}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Tarih ve Saat Paneli (Görseldeki gibi Şık) */
    .hero-section {{
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid rgba(212, 175, 55, 0.3);
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .date-label {{ color: #d4af37; font-size: 19px; font-weight: bold; margin-bottom: 5px; }}
    .hijri-label {{ color: #10b981; font-size: 16px; margin-bottom: 15px; font-style: italic; }}
    .countdown-label {{ color: white; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; margin-top: 15px; }}
    .countdown-timer {{ color: #fbbf24; font-size: 50px; font-weight: bold; margin-bottom: 10px; font-family: 'Courier New', monospace; text-shadow: 0 0 15px rgba(251, 191, 36, 0.5); }}
    
    /* Vakit Kartları Grid (Krem Arka Plan) */
    .vakit-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 25px;
    }}
    .vakit-item {{
        background: #fdf6e3;
        padding: 18px;
        border-radius: 18px;
        text-align: center;
        border: 1px solid #e2e8f0;
        transition: 0.3s;
    }}
    .vakit-item:hover {{
        border: 1px solid #d4af37;
        transform: translateY(-3px);
    }}
    .vakit-name {{ color: #64748b; font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }}
    .vakit-time {{ color: #2e3b4e; font-size: 24px; font-weight: bold; margin-top: 5px; }}
    .active-vakit {{
        border: 3px solid #10b981 !important;
        background: #e6fffa !important;
    }}
    .active-vakit .vakit-name {{ color: #10b981; }}
    .active-vakit .vakit-time {{ color: #10b981; }}

    /* ALT ÜÇLÜ MODÜL (Zümrüt Yeşili Kapsüller) */
    .module-container {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        margin-top: 20px;
    }}
    .module-card {{
        background: #153e35;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        color: white;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }}
    .module-header {{ color: #fbbf24; font-size: 16px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; border-bottom: 1px solid rgba(251, 191, 36, 0.2); padding-bottom: 5px; }}
    .module-content {{ color: #e2e8f0; font-size: 14px; line-height: 1.6; height: 120px; overflow-y: auto; }}
    .zikir-count {{ font-size: 55px; font-weight: bold; color: #fbbf24; text-align: center; margin: 10px 0; }}
    
    /* Premium Butonlar */
    .stButton>button {{
        width: 100%; border-radius: 30px; background: linear-gradient(90deg, #10b981 0%, #d4af37 100%);
        color: white; font-weight: bold; border: none; height: 48px; font-size: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: 0.3s;
    }}
    .stButton>button:hover {{ background: linear-gradient(90deg, #14c78c 0%, #f1c40f 100%); }}
    .btn-secondary>button {{ background: white !important; color: #2e3b4e !important; border: 1px solid #e2e8f0 !important; height: 35px; font-size: 13px; }}
    
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ VE TÜRKÇE TARİH ---
DB_FILE = "user_data.json"
def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"zikir": 0, "dualar": []}, f)
    with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_data(d):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# Türkçe Ay İsimleri Sözlükleri
tr_aylar = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}
tr_hicri_aylar = {"Muharram": "Muharrem", "Safar": "Safer", "Rabi' al-awwal": "Rebiülevvel", "Rabi' al-thani": "Rebiülahir", "Jumada al-ula": "Cemaziyelevvel", "Jumada al-akhira": "Cemaziyelahir", "Rajab": "Recep", "Sha'ban": "Şaban", "Ramadan": "Ramazan", "Shawwal": "Şevval", "Dhu al-Qi'dah": "Zilkade", "Dhu al-Hijjah": "Zilhicce"}

# --- 3. API VE VAKİT ÇEKME ---
sehir = st.sidebar.selectbox("📍 Şehir Seçiniz", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])

try:
    url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
    res = requests.get(url, timeout=10).json()['data']
    v = res['timings']
    h = res['date']['hijri']
    g = res['date']['gregorian']
    
    # Tarihleri Türkçeleştirme
    g_txt = f"{g['weekday']['en'] == 'Thursday' and 'Perşembe' or g['weekday']['en']}, {g['day']} {tr_aylar.get(g['month']['en'], g['month']['en'])} {g['year']}"
    h_txt = f"{h['day']} {tr_hicri_aylar.get(h['month']['en'], h['month']['en'])} {h['year']}"

    # Vakitleri Hazırlama
    v_order = [("SABAH", v['Fajr']), ("GÜNEŞ", v['Sunrise']), ("ÖĞLE", v['Dhuhr']), ("İKİNDİ", v['Asr']), ("AKŞAM", v['Maghrib']), ("YATSI", v['Isha'])]

    # --- ÜST PANEL (Dizayndaki gibi) ---
    st.markdown(f"""
    <div class="hero-section">
        <div class="date-label">📅 {g_txt}</div>
        <div class="hijri-label">🌙 {h_txt}</div>
        <div class="countdown-label">YATSI VAKTİNE KALAN SÜRE</div>
        <div id="countdown" class="countdown-timer">00:00:00</div>
    </div>
    
    <script>
    function startTimer() {{
        const vakitler = {json.dumps({n: t for n, t in v_order})};
        setInterval(() => {{
            const now = new Date();
            const nowSec = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();
            
            let target = null;
            let targetName = "";
            
            // Sıradaki vakti bul
            for (let name in vakitler) {{
                let [h, m] = vakitler[name].split(':');
                let vSec = parseInt(h) * 3600 + parseInt(m) * 60;
                
                if (vSec > nowSec) {{
                    target = vSec;
                    targetName = name;
                    break;
                }}
            }}
            
            // Eğer tüm vakitler geçtiyse yarına kur (İmsak)
            if (!target) {{
                let [h, m] = vakitler["SABAH"].split(':');
                target = parseInt(h) * 3600 + parseInt(m) * 60 + 86400;
                targetName = "SABAH";
            }}

            let diff = target - nowSec;
            let hrs = Math.floor(diff / 3600);
            let mins = Math.floor((diff % 3600) / 60);
            let secs = diff % 60;
            
            document.getElementById('countdown').innerHTML = 
                (hrs < 10 ? "0"+hrs : hrs) + ":" + 
                (mins < 10 ? "0"+mins : mins) + ":" + 
                (secs < 10 ? "0"+secs : secs);
        }}, 1000);
    }}
    startTimer();
    </script>
    """, unsafe_allow_html=True)

    # --- VAKİT GRİDİ (3x2 Düzeni) ---
    # Bu kısmı Streamlit columns ile yapmalıyız, HTML grid session_state'i bozabilir.
    c1 = st.columns(3)
    for i in range(3):
        with c1[i]:
            st.markdown(f'<div class="vakit-item"><div class="vakit-name">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)
            
    c2 = st.columns(3)
    for i in range(3, 6):
        with c2[i-3]:
            st.markdown(f'<div class="vakit-item"><div class="vakit-name">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)

except:
    st.error("Namaz vakitleri şu an alınamıyor, internet bağlantınızı kontrol edin.")

# --- 4. ALT ÜÇLÜ MODÜL (Dizayndaki gibi Yan Yana) ---
st.divider()
col_esma, col_zikir, col_sure = st.columns(3)

with col_esma:
    # ESMAÜL HÜSNA MODÜLÜ
    st.markdown("""
        <div class="module-card">
            <div class="module-header">✨ Esmaü'l Hüsna</div>
            <div class="esma-scroll module-content">
                <b>Allah</b>: Eşi benzeri olmayan.<br>
                <b>er-Rahmân</b>: Merhamet Eden.<br>
                <b>er-Rahîm</b>: Bağışlayan.<br>
                <b>el-Melik</b>: Mülkün Sahibi.<br>
                <b>el-Kuddûs</b>: Noksanlıktan Uzak.<br>
                ...<br>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
    st.button("📜 Tüm Liste", key="esma_all")
    st.markdown('</div>', unsafe_allow_html=True)

with col_zikir:
    # ZİKİRMATİK MODÜLÜ
    st.markdown(f"""
        <div class="module-card">
            <div class="module-header">📿 Zikirmatik</div>
            <div class="zikir-count">{data['zikir']}</div>
        </div>
    """, unsafe_allow_html=True)
    # Butonlar (Dizayndaki gibi Gold ve Beyaz)
    c_add, c_reset = st.columns([2, 1])
    with c_add:
        if st.button("➕ Zikir Ekle"):
            data['zikir'] += 1
            save_data(data)
            st.rerun()
    with c_reset:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("🔄 Sıfırla"):
            data['zikir'] = 0
            save_data(data)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with col_sure:
    # SÜRELER MODÜLÜ
    st.markdown("""
        <div class="module-card">
            <div class="module-header">📖 Kısa Sureler</div>
            <div class="module-content">
                <b>İhlas Suresi</b><br>
                <b>Felak Suresi</b><br>
                <b>Nas Suresi</b><br>
                <b>Kevser Suresi</b><br>
                <b>Fatiha Suresi</b><br>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
    st.button("Sure Seç", key="sure_select")
    st.markdown('</div>', unsafe_allow_html=True)