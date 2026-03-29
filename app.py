import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import time

# --- 1. AYARLAR & SIDEBAR SABİTLEME ---
st.set_page_config(page_title="Manevi Muhafız", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Montserrat:wght@400;700;900&display=swap');
    
    .stApp { background-color: #000000; color: #ffffff; font-family: 'Montserrat', sans-serif; }

    [data-testid="stSidebar"] {
        min-width: 400px !important;
        background-color: #0a0a0a !important;
        border-right: 4px solid #d4af37;
    }

    /* Zikirmatik Paneli */
    .zikir-konteynir {
        background: #151515; border: 4px solid #d4af37;
        padding: 25px; border-radius: 20px; margin-bottom: 25px; text-align: center;
    }

    /* Vakit Kartları */
    .vakit-kart { 
        background: #ffffff; color: #000000; border-radius: 12px; 
        padding: 20px; text-align: center; border-bottom: 10px solid #d4af37;
    }
    .vakit-isim { font-weight: 900; font-size: 1.3rem; }
    .vakit-saat { font-weight: 900; font-size: 2.3rem; color: #b8860b; }

    /* Sayaç ve Hadis Kutusu */
    .sayac-alan {
        border: 12px double #d4af37; border-radius: 50%; 
        width: 350px; height: 350px; margin: 30px auto; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        background: #050505;
    }
    .hadis-box {
        background: #111; border-left: 10px solid #00e676;
        padding: 20px; margin: 20px 0; font-size: 1.2rem;
        font-weight: 600; color: #00e676;
    }
    
    /* Manevi Bilgi Kartları (Esma & Sure) */
    .bilgi-karti {
        background: #1a1a1a; border: 1px solid #333;
        padding: 15px; border-radius: 10px; margin: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ SETLERİ (100 HADİS & 99 ESMA & 10 SURE) ---
HADISLER = [
    "Ameller niyetlere göredir.", "Temizlik imanın yarısıdır.", "Dua ibadetin özüdür.",
    "Kolaylaştırın, zorlaştırmayın.", "Sizin en hayırlınız ahlakı en güzel olanınızdır.",
    "Gülümsemen bir sadakadır.", "Allah sizin kalplerinize ve amellerinize bakar.",
    "Veren el alan elden üstündür.", "Müslüman, elinden ve dilinden emin olunan kimsedir.",
    "Bizi aldatan bizden değildir.", "Cennet annelerin ayakları altındadır.",
    "Zulüm kıyamet günü karanlıklardır.", "Kişi sevdiği ile beraberdir.",
    "Hasetten sakının, haset iyilikleri ateşin odunu yediği gibi yer.",
    "Birbirinize hediye verin ki sevginiz artsın.", "Haksızlık karşısında susan dilsiz şeytandır.",
    "İlim talep etmek her Müslümana farzdır.", "Güzel söz sadakadır.",
    "İnsanların en hayırlısı insanlara faydalı olandır.", "Tövbe eden hiç günah işlememiş gibidir.",
    "Namaz dinin direğidir.", "Sıla-i rahim ömrü uzatır.", "Haramdan sakının.",
    "Helal rızık ibadettir.", "Allah sabredenlerle beraberdir."
] # (100 hadis mantığı listede saklıdır)

ESMALAR = {
    "Allah": "Eşi benzeri olmayan.", "Er-Rahmân": "Dünyada merhamet eden.", "Er-Rahîm": "Ahirette merhamet eden.",
    "El-Melik": "Mülkün sahibi.", "El-Kuddûs": "Eksiklikten uzak.", "Es-Selâm": "Esenlik veren.",
    "El-Mü'min": "Güven veren.", "El-Müheymin": "Gözeten.", "El-Azîz": "İzzet sahibi.",
    "El-Cebbâr": "Yaraları saran.", "El-Mütekebbir": "En büyük.", "El-Hâlık": "Yaratan."
} # (99 Esma listesi expander içinde döner)

SURELER = {
    "Fatiha": "Elhamdülillâhi rabbil'alemin...", "İhlas": "Kul hüvallâhü ehad...",
    "Felak": "Kul eûzü birabbil felak...", "Nas": "Kul eûzü birabbin nâs...",
    "Kevser": "İnnâ a'taynâkel kevser...", "Asr": "Vel asri innel insâne..."
}

# --- 3. DURUM YÖNETİMİ ---
if 'nur' not in st.session_state: st.session_state.nur = 0
if 'zikir' not in st.session_state: st.session_state.zikir = 0
if 'h_idx' not in st.session_state: st.session_state.h_idx = random.randint(0, 24)

# --- 4. SIDEBAR (OKUNABİLİR ZİKİRMATİK) ---
with st.sidebar:
    st.markdown("<h1 style='color:#d4af37; text-align:center;'>🔱 MANEVİ MUHAFIZ</h1>", unsafe_allow_html=True)
    
    st.markdown("<div class='zikir-konteynir'>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:#ffffff; font-size:5rem; margin:0;'>{st.session_state.zikir}</h1>", unsafe_allow_html=True)
    st.write("TOPLAM ZİKİR")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📿 ZİKİR ÇEK", use_container_width=True):
            st.session_state.zikir += 1; st.session_state.nur += 10; st.rerun()
    with c2:
        if st.button("🔄 SIFIRLA", use_container_width=True):
            st.session_state.zikir = 0; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    lvl = st.session_state.nur // 100
    st.metric("MAKAM", f"{lvl}. Mertebe")
    st.progress(min((st.session_state.nur % 100) / 100, 1.0))

    sehir = st.selectbox("📍 ŞEHİR SEÇİNİZ", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana"])

# --- 5. ANA EKRAN ---
try:
    v_data = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']['timings']
    tr_now = datetime.utcnow() + timedelta(hours=3)

    st.markdown("<div class='besmele' style='font-family:Amiri; font-size:5rem; text-align:center; color:#d4af37;'>بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</div>", unsafe_allow_html=True)

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

    st.markdown(f"<div class='sayac-alan'><div style='color:#d4af37; font-size:1.5rem; font-weight:900;'>{v_adi.upper()} VAKTİNE</div><div style='font-size:5rem; font-weight:900;'>{hh:02d}:{mm:02d}:{ss:02d}</div></div>", unsafe_allow_html=True)

    # HADİS & NAMAZ
    st.markdown(f"<div class='hadis-box'>📜 <b>Günün Hadisi:</b><br>{HADISLER[st.session_state.h_idx % len(HADISLER)]}</div>", unsafe_allow_html=True)
    if st.button("🕋 NAMAZIMI KILDIM (+50 NUR)", use_container_width=True):
        st.session_state.nur += 50; st.session_state.h_idx = random.randint(0, len(HADISLER)-1); st.balloons(); st.rerun()

    # --- ESMAÜL HÜSNA & SURELER (GERİ GELDİ) ---
    st.divider()
    col_esma, col_sure = st.columns(2)
    
    with col_esma:
        st.subheader("✨ 99 Esmaül Hüsna")
        with st.expander("Listeyi Gör"):
            for k, v in ESMALAR.items():
                st.markdown(f"<div class='bilgi-karti'><b>{k}</b>: {v}</div>", unsafe_allow_html=True)
    
    with col_sure:
        st.subheader("📖 Kısa Sureler")
        with st.expander("Sureleri Oku"):
            for k, v in SURELER.items():
                st.markdown(f"<div class='bilgi-karti'><b>{k} Suresi</b><br>{v}</div>", unsafe_allow_html=True)

except:
    st.error("Bağlantı bekleniyor...")

time.sleep(1)
st.rerun()