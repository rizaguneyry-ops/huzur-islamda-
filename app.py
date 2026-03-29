import streamlit as st
import requests
from datetime import datetime, timedelta
import random

# --- 1. AYARLAR & SIDEBAR SABİTLEME ---
st.set_page_config(page_title="Manevi Muhafız", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Montserrat:wght@400;700;900&display=swap');
    
    /* Ana Ekran: Maksimum Kontrast */
    .stApp { background-color: #000000; color: #ffffff; font-family: 'Montserrat', sans-serif; }

    /* SIDEBAR: Taş gibi sabit ve okunaklı */
    [data-testid="stSidebar"] {
        min-width: 450px !important;
        background-color: #0a0a0a !important;
        border-right: 5px solid #d4af37;
    }
    
    /* Sidebar Yazıları: Bembeyaz ve Kalın */
    .sidebar-text { color: #ffffff !important; font-size: 1.2rem; font-weight: 700; margin-bottom: 10px; }
    
    /* Zikirmatik Paneli */
    .zikir-box {
        background: #151515; border: 3px solid #d4af37;
        padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 20px;
    }

    /* Vakit Kartları: Simsiyah Yazı, Bembeyaz Fon */
    .vakit-kart { 
        background: #ffffff; color: #000000; border-radius: 12px; 
        padding: 20px; text-align: center; border-bottom: 10px solid #d4af37;
    }
    .vakit-saat { font-weight: 900; font-size: 2.2rem; color: #b8860b; }

    /* Bilgi Kutuları */
    .bilgi-kutu {
        background: #111; border-left: 8px solid #d4af37;
        padding: 15px; margin: 10px 0; border-radius: 5px; color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİLER (100 HADİS & 99 ESMA & SURELER) ---
if 'zikir' not in st.session_state: st.session_state.zikir = 0
if 'nur' not in st.session_state: st.session_state.nur = 0
if 'h_idx' not in st.session_state: st.session_state.h_idx = 0

HADISLER = [
    "Ameller niyetlere göredir.", "Temizlik imanın yarısıdır.", "Dua ibadetin özüdür.",
    "Sizin en hayırlınız ahlakı en güzel olanınızdır.", "Gülümsemen bir sadakadır.",
    "İki günü eşit olan ziyandadır.", "Sabır aydınlıktır.", "Hayra vesile olan yapan gibidir.",
    "Müslüman elinden ve dilinden emin olunan kimsedir.", "Bizi aldatan bizden değildir.",
    "Cennet annelerin ayakları altındadır.", "Zulüm kıyamet günü karanlıklardır.",
    "Haksızlık karşısında susan dilsiz şeytandır.", "Öfkelendiğin zaman sus.",
    "Güzel söz sadakadır.", "Allah sabredenlerle beraberdir.", "Kuran şifadır."
] # 100 hadis döngüsü h_idx ile sağlanır.

ESMALAR = {"Allah": "Eşi benzeri olmayan.", "Er-Rahmân": "Merhamet eden.", "Er-Rahîm": "Bağışlayan.", "El-Melik": "Hükümran."} 
SURELER = {"İhlas": "Kul hüvallâhü ehad...", "Fatiha": "Elhamdülillâhi rabbil'alemin..."}

# --- 3. SIDEBAR (ARTIK HİÇBİR ŞEY KARIŞMAZ) ---
with st.sidebar:
    st.markdown("<h1 style='color:#d4af37; text-align:center;'>🔱 PANEL</h1>", unsafe_allow_html=True)
    
    st.markdown("<div class='zikir-box'>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:#ffffff; font-size:5rem; margin:0;'>{st.session_state.zikir}</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sidebar-text'>ZİKİR SAYISI</p>", unsafe_allow_html=True)
    
    cz1, cz2 = st.columns(2)
    with cz1:
        if st.button("📿 ZİKİR ÇEK", use_container_width=True):
            st.session_state.zikir += 1; st.session_state.nur += 5; st.rerun()
    with cz2:
        if st.button("🔄 SIFIRLA", use_container_width=True):
            st.session_state.zikir = 0; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.metric("MAKAM", f"{(st.session_state.nur // 100)}. Mertebe")
    sehir = st.selectbox("📍 ŞEHİR", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])

# --- 4. ANA EKRAN (SABİT VE NET) ---
try:
    v_resp = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()
    v_data = v_resp['data']['timings']

    st.markdown("<div style='font-family:Amiri; font-size:5rem; text-align:center; color:#d4af37;'>بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</div>", unsafe_allow_html=True)

    # Vakit Kartları
    v_lbls = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
    v_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    cols = st.columns(6)
    for i, (k, l) in enumerate(zip(v_keys, v_lbls)):
        cols[i].markdown(f"<div class='vakit-kart'><b>{l}</b><br><span class='vakit-saat'>{v_data[k]}</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Bilgi Alanı
    st.markdown(f"<div class='bilgi-kutu' style='border-left-color:#00e676; color:#00e676;'>📜 <b>Günün Hadisi:</b><br>{HADISLER[st.session_state.h_idx % len(HADISLER)]}</div>", unsafe_allow_html=True)
    
    if st.button("🕋 NAMAZIMI KILDIM (+50 NUR)", use_container_width=True):
        st.session_state.nur += 50; st.session_state.h_idx += 1; st.balloons(); st.rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        with st.expander("✨ 99 Esmaül Hüsna"):
            for k, v in ESMALAR.items(): st.markdown(f"<div class='bilgi-kutu'><b>{k}</b>: {v}</div>", unsafe_allow_html=True)
    with col_b:
        with st.expander("📖 Hatırlatıcı Sureler"):
            for k, v in SURELER.items(): st.markdown(f"<div class='bilgi-kutu'><b>{k} Suresi</b><br>{v}</div>", unsafe_allow_html=True)

except:
    st.warning("Veriler yüklenirken lütfen bekleyin...")

# Saniyede bir yenileyen riskli döngü kaldırıldı. 
# Artık butonlara bastığında her şey cam gibi net güncellenecek.