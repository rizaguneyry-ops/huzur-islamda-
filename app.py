import streamlit as st
import requests
from datetime import datetime, timedelta
import random

# --- 1. AYARLAR & SIDEBAR SABİTLEME ---
st.set_page_config(page_title="Manevi Muhafız", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; font-family: 'Montserrat', sans-serif; }
    [data-testid="stSidebar"] { min-width: 450px !important; background-color: #0d0d0d !important; border-right: 3px solid #d4af37; }
    
    /* Okunabilirlik ve Kontrast */
    .sidebar-yazi { color: #ffffff !important; font-size: 1.2rem !important; font-weight: 800 !important; }
    .dil-kutusu { background: #1a1a1a; border-left: 5px solid #00b0ff; padding: 15px; border-radius: 10px; margin-top: 10px; }
    .vakit-kart { background: #ffffff; color: #000000; border-radius: 10px; padding: 15px; text-align: center; border-bottom: 8px solid #d4af37; }
    .vakit-saat { font-size: 2rem; font-weight: 900; color: #b8860b; }
    .kutu { background: #111; border: 1px solid #333; padding: 15px; border-radius: 8px; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SİSTEM HAFIZASI ---
if 'zikir' not in st.session_state: st.session_state.zikir = 0
if 'nur' not in st.session_state: st.session_state.nur = 0
if 'idx' not in st.session_state: st.session_state.idx = random.randint(0, 10)

# --- 3. VERİLER (14 MADDE İÇERİĞİ) ---
HADISLER = ["Ameller niyetlere göredir.", "Temizlik imanın yarısıdır.", "Dua ibadetin özüdür.", "Sabır aydınlıktır."]
DILLER = [
    {"ar": "Sabr (صبر)", "en": "Patience", "tr": "Sabır"},
    {"ar": "Shukr (شكر)", "en": "Gratitude", "tr": "Şükür"},
    {"ar": "Ikhlas (إخلاص)", "en": "Sincerity", "tr": "Samimiyet/İhlas"},
    {"ar": "Ilm (علم)", "en": "Knowledge", "tr": "İlim"},
    {"ar": "Rahmah (رحمة)", "en": "Mercy", "tr": "Merhamet"}
]
ESMALAR = {"Allah": "Eşi benzeri olmayan.", "Er-Rahmân": "Dünyada merhamet eden."}
SURELER = {"İhlas": "Kul hüvallâhü ehad...", "Fatiha": "Elhamdülillâhi rabbil'alemin..."}

# --- 4. SIDEBAR (DİL DESTEĞİ EKLENDİ) ---
with st.sidebar:
    st.markdown("<h1 style='color:#d4af37; text-align:center;'>🔱 MANEVİ PANEL</h1>", unsafe_allow_html=True)
    
    # Madde 1: Zikirmatik
    st.markdown("<div style='background:#1a1a1a; border:2px solid #d4af37; padding:15px; border-radius:15px; text-align:center;'>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:#ffffff; font-size:4.5rem; margin:0;'>{st.session_state.zikir}</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sidebar-yazi'>ZİKİR SAYISI</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📿 ZİKİR ÇEK", use_container_width=True):
            st.session_state.zikir += 1; st.session_state.nur += 5; st.rerun()
    with c2:
        if st.button("🔄 SIFIRLA", use_container_width=True):
            st.session_state.zikir = 0; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Madde 2: Yabancı Dil Hatırlatıcı (Arapça-İngilizce-Türkçe)
    st.markdown("<p class='sidebar-yazi' style='margin-top:20px;'>🌍 GÜNÜN KELİMESİ</p>", unsafe_allow_html=True)
    dil = DILLER[st.session_state.idx % len(DILLER)]
    st.markdown(f"""
    <div class='dil-kutusu'>
        <b style='color:#00b0ff; font-size:1.4rem;'>{dil['ar']}</b><br>
        <span style='color:#ffffff;'>EN: {dil['en']}</span><br>
        <span style='color:#00e676;'>TR: {dil['tr']}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔄 Yeni Kelime Öğren"):
        st.session_state.idx += 1; st.rerun()

    st.markdown("---")
    st.metric("MANEVİ MAKAM", f"{(st.session_state.nur // 100)}. Mertebe")
    sehir = st.selectbox("📍 ŞEHİR", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])

# --- 5. ANA EKRAN ---
try:
    v_data = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']['timings']
    
    st.markdown("<h1 style='font-family:Amiri; font-size:5rem; text-align:center; color:#d4af37;'>بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</h1>", unsafe_allow_html=True)

    # Vakit Kartları
    v_lbls = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
    v_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    cols = st.columns(6)
    for i, (k, l) in enumerate(zip(v_keys, v_lbls)):
        cols[i].markdown(f"<div class='vakit-kart'><b>{l}</b><br><span class='vakit-saat'>{v_data[k]}</span></div>", unsafe_allow_html=True)

    # Hadis & Namaz
    st.markdown(f"<div style='background:#111; border-left:10px solid #00e676; padding:20px; margin:20px 0;'>📜 <b style='color:#00e676;'>Günün Hadisi:</b><br>{HADISLER[st.session_state.idx % len(HADISLER)]}</div>", unsafe_allow_html=True)
    
    if st.button("🕋 NAMAZIMI KILDIM (+50 NUR)", use_container_width=True):
        st.session_state.nur += 50; st.session_state.idx += 1; st.balloons(); st.rerun()

    # Esmaül Hüsna & Sureler
    st.divider()
    ca, cb = st.columns(2)
    with ca:
        with st.expander("✨ 99 ESMAÜL HÜSNA"):
            for k, v in ESMALAR.items(): st.markdown(f"<div class='kutu'><b>{k}</b>: {v}</div>", unsafe_allow_html=True)
    with cb:
        with st.expander("📖 HATIRLATICI SURELER"):
            for k, v in SURELER.items(): st.markdown(f"<div class='kutu'><b>{k} Suresi</b>: {v}</div>", unsafe_allow_html=True)

except:
    st.error("Sistem yükleniyor...")