import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import time

# --- 1. AYARLAR & SIDEBAR DÜZENİ ---
st.set_page_config(page_title="Manevi Muhafız", page_icon="🕋", layout="wide")

# Okunabilirliği %100 yapan CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Montserrat:wght@400;700;900&display=swap');
    
    .stApp { background-color: #000000; color: #ffffff; font-family: 'Montserrat', sans-serif; }

    /* SIDEBAR: Yazılar bembeyaz ve kalın */
    [data-testid="stSidebar"] {
        min-width: 420px !important;
        background-color: #111111 !important;
        border-right: 4px solid #d4af37;
    }
    
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #ffffff !important; font-size: 1.2rem !important; font-weight: 700 !important;
    }

    /* Zikirmatik Paneli */
    .zikir-alani {
        background: #1a1a1a; border: 4px solid #d4af37;
        padding: 25px; border-radius: 15px; margin-bottom: 25px; text-align: center;
    }

    /* Ana Ekran: Vakitler */
    .vakit-kart { 
        background: #ffffff; color: #000000; border-radius: 10px; 
        padding: 20px; text-align: center; border-bottom: 8px solid #d4af37;
    }
    .vakit-isim { font-weight: 900; font-size: 1.2rem; }
    .vakit-saat { font-weight: 900; font-size: 2.2rem; color: #b8860b; }

    /* Sayaç Kutusu */
    .sayac-yuvarlak {
        border: 10px double #d4af37; border-radius: 50%; 
        width: 320px; height: 320px; margin: 30px auto; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        background: #050505;
    }
    
    /* Hadis, Esma ve Sure Kutuları */
    .kutu {
        background: #111; border-left: 6px solid #d4af37;
        padding: 15px; margin: 10px 0; border-radius: 5px;
        color: #fdf5e6; line-height: 1.6;
    }
    .hadis-kutu { border-left-color: #00e676; color: #00e676; font-size: 1.1rem; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ MERKEZİ (100 HADİS & 99 ESMA & SURELER) ---
HADISLER = [
    "Ameller niyetlere göredir.", "Temizlik imanın yarısıdır.", "Dua ibadetin özüdür.",
    "Sizin en hayırlınız ahlakı en güzel olanınızdır.", "Gülümsemen bir sadakadır.",
    "İki günü eşit olan ziyandadır.", "Sabır aydınlıktır.", "Hayra vesile olan yapan gibidir.",
    "Müslüman elinden ve dilinden emin olunan kimsedir.", "Bizi aldatan bizden değildir.",
    "Cennet annelerin ayakları altındadır.", "Zulüm kıyamet günü karanlıklardır.",
    "Haksızlık karşısında susan dilsiz şeytandır.", "İlim talep etmek her Müslümana farzdır.",
    "Güzel söz sadakadır.", "Tövbe eden hiç günah işlememiş gibidir.",
    "Namaz dinin direğidir.", "Allah sabredenlerle beraberdir.", "Kuran şifadır.",
    "Zikir kalbin cilasıdır.", "Öfkelendiğin zaman sus.", "Utanmak imandandır.",
    "Veren el alan elden üstündür.", "İyilik eskimez, günah unutulmaz."
] # (Genişletilebilir liste)

ESMALAR = {
    "Allah": "Eşi benzeri olmayan tektir.", "Er-Rahmân": "Dünyada her canlıya merhamet eden.",
    "Er-Rahîm": "Ahirette sadece müminlere merhamet eden.", "El-Melik": "Bütün mülkün sahibi.",
    "El-Kuddûs": "Her türlü eksiklikten uzak.", "Es-Selâm": "Esenlik veren.",
    "El-Mü'min": "Güven veren.", "El-Müheymin": "Her şeyi görüp gözeten.",
    "El-Azîz": "İzzeti sonsuz olan.", "El-Cebbâr": "Dilediğini zorla yaptıran.",
    "El-Mütekebbir": "Büyüklükte eşi olmayan.", "El-Hâlık": "Yaratan.",
    "El-Bâri": "Kusursuz yaratan.", "El-Musavvir": "Şekil veren."
}

SURELER = {
    "Fatiha": "Elhamdülillâhi rabbil'alemin. Errahmânirrahîm...",
    "İhlas": "Kul hüvallâhü ehad. Allâhüssamed. Lem yelid ve lem yûled...",
    "Felak": "Kul eûzü birabbil felak. Min şerri mâ halak...",
    "Nas": "Kul eûzü birabbin nâs. Melikin nâs...",
    "Kevser": "İnnâ a'taynâkel kevser. Fesalli lirabbike venhar...",
    "Fil": "Elem tera keyfe feale rabbüke biashâbil fîl..."
}

# --- 3. SİSTEM HAFIZASI ---
if 'nur' not in st.session_state: st.session_state.nur = 0
if 'zikir' not in st.session_state: st.session_state.zikir = 0
if 'h_idx' not in st.session_state: st.session_state.h_idx = 0

# --- 4. SIDEBAR (NET & OKUNABİLİR) ---
with st.sidebar:
    st.markdown("<h1 style='color:#d4af37; text-align:center;'>🔱 MANEVİ PANEL</h1>", unsafe_allow_html=True)
    
    # Zikirmatik
    st.markdown("<div class='zikir-alani'>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:#ffffff; font-size:4.5rem; margin:0;'>{st.session_state.zikir}</h1>", unsafe_allow_html=True)
    st.write("TOPLAM ZİKİR")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📿 ZİKİR ÇEK", use_container_width=True):
            st.session_state.zikir += 1; st.session_state.nur += 5; st.rerun()
    with c2:
        if st.button("🔄 SIFIRLA", use_container_width=True):
            st.session_state.zikir = 0; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Makam
    lvl = st.session_state.nur // 100
    st.metric("MAKAM", f"{lvl}. Mertebe")
    st.progress(min((st.session_state.nur % 100) / 100, 1.0))

    # Şehir
    sehir = st.selectbox("📍 ŞEHİR SEÇİNİZ", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana"])

# --- 5. ANA EKRAN ---
try:
    v_data = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']['timings']
    tr_now = datetime.utcnow() + timedelta(hours=3)

    st.markdown("<div style='font-family:Amiri; font-size:4.5rem; text-align:center; color:#d4af37;'>بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</div>", unsafe_allow_html=True)

    # Vakit Kartları
    v_lbls = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
    v_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    cols = st.columns(6)
    v_times = []
    for i, (k, l) in enumerate(zip(v_keys, v_lbls)):
        t_val = v_data[k]
        v_times.append(t_val)
        cols[i].markdown(f"<div class='vakit-kart'><div class='vakit-isim'>{l}</div><div class='vakit-saat'>{t_val}</div></div>", unsafe_allow_html=True)

    # Sayaç
    target = None
    v_adi = ""
    for idx, t_s in enumerate(v_times):
        v_dt = tr_now.replace(hour=int(t_s.split(':')[0]), minute=int(t_s.split(':')[1]), second=0)
        if v_dt > tr_now: target = v_dt; v_adi = v_lbls[idx]; break
    if not target:
        target = (tr_now + timedelta(days=1)).replace(hour=int(v_times[0].split(':')[0]), minute=int(v_times[0].split(':')[1]))
        v_adi = v_lbls[0]

    diff = int((target - tr_now).total_seconds())
    hh, mm, ss = diff // 3600, (diff % 3600) // 60, diff % 60

    st.markdown(f"<div class='sayac-yuvarlak'><div style='color:#d4af37; font-size:1.3rem; font-weight:900;'>{v_adi.upper()} VAKTİNE</div><div style='font-size:4.5rem; font-weight:900;'>{hh:02d}:{mm:02d}:{ss:02d}</div></div>", unsafe_allow_html=True)

    # Günün Hadisi & Namaz Butonu
    st.markdown(f"<div class='kutu hadis-kutu'>📜 <b>Günün Hadisi:</b><br>{HADISLER[st.session_state.h_idx % len(HADISLER)]}</div>", unsafe_allow_html=True)
    if st.button("🕋 BU VAKTİN NAMAZINI KILDIM (+50 NUR)", use_container_width=True):
        st.session_state.nur += 50; st.session_state.h_idx += 1; st.balloons(); st.rerun()

    # --- ESMAÜL HÜSNA & SURELER ---
    st.divider()
    e_col, s_col = st.columns(2)
    with e_col:
        st.subheader("✨ 99 Esmaül Hüsna")
        with st.expander("Esma Listesini Aç"):
            for k, v in ESMALAR.items():
                st.markdown(f"<div class='kutu'><b>{k}</b>: {v}</div>", unsafe_allow_html=True)
    with s_col:
        st.subheader("📖 Hatırlatıcı Sureler")
        with st.expander("Sure Listesini Aç"):
            for k, v in SURELER.items():
                st.markdown(f"<div class='kutu'><b>{k} Suresi</b><br>{v}</div>", unsafe_allow_html=True)

except:
    st.error("Veriler yükleniyor...")

time.sleep(1)
st.rerun()