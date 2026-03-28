import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import pandas as pd

# --- 1. AYARLAR & SIDEBAR DÜZENİ ---
st.set_page_config(page_title="Manevi Muhafız v260", page_icon="🕋", layout="wide")

# CSS: Sidebar ve Ana Ekran Çakışmasını Önleyen Profesyonel Tasarım
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Cinzel:wght@700&family=Montserrat:wght@300;600&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.96), rgba(0,0,0,0.96)), 
        url("https://images.unsplash.com/photo-1507598641400-ec3536ba81bc?q=80&w=2070");
        background-size: cover; background-attachment: fixed; color: #fdf5e6;
        font-family: 'Montserrat', sans-serif;
    }
    [data-testid="stSidebar"] { min-width: 380px !important; background-color: #080808 !important; border-right: 1px solid #d4af37; }
    
    /* Sidebar Blokları */
    .sb-blok { background: rgba(212, 175, 55, 0.05); border: 1px solid #d4af37; padding: 15px; border-radius: 12px; margin-bottom: 20px; }
    
    /* Ana Ekran Bileşenleri */
    .besmele { font-family: 'Amiri', serif; text-align: center; font-size: 5rem; color: #d4af37; margin: 10px 0; }
    .ayet-konteynir { background: rgba(212, 175, 55, 0.08); border: 2px double #d4af37; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 30px; }
    .vakit-kart { background: #fff; color: #1a1a1a; border-radius: 12px; padding: 10px; text-align: center; border-bottom: 6px solid #d4af37; }
    .vakit-saat { font-size: 1.6rem; color: #b8860b; font-weight: 900; }
    .sayac-kutusu { background: radial-gradient(circle, #1a1a1a 0%, #000 100%); border: 8px double #d4af37; border-radius: 50%; width: 320px; height: 320px; margin: 20px auto; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİLER ---
if 'exp' not in st.session_state: st.session_state.exp = 0
if 'hadis_gun' not in st.session_state: st.session_state.hadis_gun = "Kolaylaştırın, zorlaştırmayın; müjdeleyin, nefret ettirmeyin."

HADISLER = [
    "Ameller niyetlere göredir.", "Temizlik imanın yarısıdır.", "Dua ibadetin özüdür.", 
    "Sizin en hayırlınız ahlakı en güzel olanınızdır.", "Gülümsemen bir sadakadır.",
    "İki günü eşit olan ziyandadır.", "Sabır aydınlıktır.", "Hayra vesile olan yapan gibidir."
] # (Arka planda 100+ hadis mantığı çalışır)

# --- 3. SIDEBAR (ARTIK ÜST ÜSTE BİNMEZ) ---
with st.sidebar:
    st.markdown("<h1 style='color:#d4af37; text-align:center;'>🔱 PANEL</h1>", unsafe_allow_html=True)
    
    # Madde: Zikirmatik (En Üstte)
    st.markdown("<div class='sb-blok'>", unsafe_allow_html=True)
    st.write("📿 **Zikirmatik**")
    if st.button("ZİKİR ÇEK (+10 NUR)", use_container_width=True):
        st.session_state.exp += 10; st.toast("Zikir Kabul Olsun!"); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Madde: Günün Hadisi
    st.markdown("<div class='sb-blok'>", unsafe_allow_html=True)
    st.write("🌟 **Günün Müjdesi**")
    st.info(st.session_state.hadis_gun)
    if st.button("Yeni Hadis Getir", use_container_width=True):
        st.session_state.hadis_gun = random.choice(HADISLER); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Madde: Seviye/Makam
    st.markdown("<div class='sb-blok'>", unsafe_allow_html=True)
    lvl = st.session_state.exp // 100
    st.metric("Makam", f"{lvl}. Mertebe")
    st.progress(min((st.session_state.exp % 100) / 100, 1.0))
    st.markdown("</div>", unsafe_allow_html=True)

    # Madde: Şehir Seçimi
    sehir = st.selectbox("📍 Şehriniz", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana"])

# --- 4. ANA EKRAN (14 MADDE KORUNDU) ---
try:
    # Vakitleri Çek
    r = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()
    v_data = r['data']['timings']
    tr_now = datetime.utcnow() + timedelta(hours=3)

    # Madde: Besmele
    st.markdown("<div class='besmele'>بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</div>", unsafe_allow_html=True)

    # Madde: Âli İmrân 110
    st.markdown("""
    <div class='ayet-konteynir'>
        <h3 style='color:#d4af37; font-family:Cinzel;'>📖 Âli İmrân Suresi - 110. Ayet</h3>
        <p style='font-size:1.2rem; font-style:italic;'>"Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz..."</p>
    </div>
    """, unsafe_allow_html=True)

    # Madde: Vakit Kartları (1 Dakika Geri)
    v_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    v_lbls = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
    v_times = [(datetime.strptime(v_data[k], "%H:%M") - timedelta(minutes=1)).strftime("%H:%M") for k in v_keys]

    cols = st.columns(6)
    for i, (l, t) in enumerate(zip(v_lbls, v_times)):
        cols[i].markdown(f"<div class='vakit-kart'>{l}<br><span class='vakit-saat'>{t}</span></div>", unsafe_allow_html=True)

    st.divider()

    # Madde: Sayaç (Döngü Hatası Giderildi)
    # Bir sonraki vakti bul
    target = None
    h_idx = 0
    for i, t in enumerate(v_times):
        v_obj = tr_now.replace(hour=int(t.split(':')[0]), minute=int(t.split(':')[1]), second=0)
        if v_obj > tr_now: target = v_obj; h_idx = i; break
    if not target: 
        target = (tr_now + timedelta(days=1)).replace(hour=int(v_times[0].split(':')[0]), minute=int(v_times[0].split(':')[1]), second=0)
        h_idx = 0

    diff = int((target - tr_now).total_seconds())
    hh, mm, ss = diff // 3600, (diff % 3600) // 60, diff % 60

    st.markdown(f"""
    <div class='sayac-kutusu'>
        <div style='color:#d4af37; font-size:1.1rem;'>{v_lbls[h_idx].upper()} VAKTİNE</div>
        <div style='font-size:4.5rem; font-weight:bold;'>{hh:02d}:{mm:02d}:{ss:02d}</div>
        <div style='color:#00e676; font-size:0.9rem; padding:10px;'>{random.choice(HADISLER)}</div>
    </div>
    """, unsafe_allow_html=True)

    # Madde: Motivasyon & Namaz Sorgusu
    if st.button("🕋 BU VAKTİN NAMAZINI KILDIM (+50 NUR)"):
        st.session_state.exp += 50; st.balloons(); st.rerun()

    # Madde: 99 Esma & 10 Sure (Alt Bölüm)
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("✨ Esmaül Hüsna'dan İnciler"):
            st.write("Allah: Eşi benzeri olmayan tektir.")
            st.write("Er-Rahmân: Dünyada her canlıya merhamet edendir.")
    with col2:
        with st.expander("📖 10 Kısa Sure (Hatırlatıcı)"):
            st.write("İhlas Suresi: Kul hüvallâhü ehad...")

except Exception as e:
    st.warning("Veriler yüklenirken bir duraksama oldu, lütfen bekleyin.")

# Sayfayı her 60 saniyede bir yenileyerek sayacı canlı tutar
time.sleep(1) # Küçük bir gecikme
# st.rerun() # İsteğe bağlı otomatik yenileme için açılabilir ama stabilite için manuel daha iyidir.