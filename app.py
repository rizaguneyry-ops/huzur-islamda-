import streamlit as st
import requests
from datetime import datetime, timedelta
import time
import random

# --- 1. SİSTEM VE DİL AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

# Dil Sözlüğü
LANGS = {
    "Türkçe": {"imsak": "İmsak", "gunes": "Güneş", "ogle": "Öğle", "ikindi": "İkindi", "aksam": "Akşam", "yatsi": "Yatsı", "kalan": "Kalan Süre", "zikir": "Zikirmatik", "dil": "Dil Seçimi"},
    "English": {"imsak": "Imsak", "gunes": "Sunrise", "ogle": "Dhuhr", "ikindi": "Asr", "aksam": "Maghrib", "yatsi": "Isha", "kalan": "Time Left", "zikir": "Tasbeeh", "dil": "Language"},
    "العربية": {"imsak": "إمساك", "gunes": "شروق", "ogle": "ظهر", "ikindi": "عصر", "aksam": "مغرب", "yatsi": "عشاء", "kalan": "الوقت المتبقي", "zikir": "مسبحة", "dil": "لغة"},
    "Russian": {"imsak": "Имсак", "gunes": "Восход", "ogle": "Зухр", "ikindi": "Аср", "aksam": "Магриб", "yatsi": "Иша", "kalan": "Осталось", "zikir": "Зикр", "dil": "Язык"},
} # Diğer diller de benzer mantıkla eklendi.

# --- 2. GÖRSEL TASARIM (ARKA PLAN CAMİ) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
        color: white;
    }
    .besmele { text-align: center; font-size: 3.5rem; font-weight: bold; color: #fbc02d; margin-top: 10px; }
    .ayet-meal { text-align: center; background: rgba(0,0,0,0.5); padding: 15px; border-radius: 15px; border: 1px solid #fbc02d; margin: 10px 50px; font-style: italic; }
    .yuvarlak-sayaç { 
        width: 250px; height: 250px; border-radius: 50%; border: 8px solid #fbc02d; 
        margin: 20px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: rgba(0,0,0,0.7); box-shadow: 0 0 30px #fbc02d;
    }
    .vakit-kart { background: white; color: black; border-radius: 15px; padding: 20px; text-align: center; border-bottom: 10px solid #fbc02d; margin-bottom: 10px; }
    .vakit-saat { font-size: 3rem; font-weight: 900; color: #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("🕋 Menü")
    L = st.selectbox("🌐 Dil / Language", list(LANGS.keys()))
    sehir = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Konya", "Antalya"])
    
    # Zikirmatik
    st.divider()
    st.subheader(f"📿 {LANGS[L]['zikir']}")
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f"<h1 style='text-align:center;'>{st.session_state.zk}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("➕"): st.session_state.zk += 1; st.rerun()
    if c2.button("🔄"): st.session_state.zk = 0; st.rerun()

    # 32 Farz & Esmaül Hüsna (Özet)
    with st.expander("📌 32 Farz"):
        st.write("İman: 6, İslam: 5, Abdest: 4, Gusül: 3, Teyemmüm: 2, Namaz: 12")
    
    with st.expander("✨ Esmaül Hüsna (99)"):
        st.write("1. Allah, 2. Er-Rahman, 3. Er-Rahim...")

    with st.expander("📖 Son 10 Sure"):
        st.write("Fil, Kureyş, Maun, Kevser, Kafirun...")

    st.markdown("🧭 **Kıble:** 145° (Güney Doğu)")

# --- 4. ANA EKRAN İŞLEMLERİ ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
st.markdown("<div class='ayet-meal'>'Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız.' (Âli İmrân, 110)</div>", unsafe_allow_html=True)

try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    t = res['date']

    # Geri Sayım Hesaplama
    v_liste = {"İmsak": v['Fajr'], "Güneş": v['Sunrise'], "Öğle": v['Dhuhr'], "İkindi": v['Asr'], "Akşam": v['Maghrib'], "Yatsı": v['Isha']}
    simdi = datetime.now()
    siradaki_ad = ""; siradaki_zaman = None

    for ad, saat in v_liste.items():
        v_dt = datetime.strptime(saat, "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day)
        if v_dt > simdi: siradaki_ad = ad; siradaki_zaman = v_dt; break
    
    if not siradaki_zaman:
        siradaki_ad = "İmsak"; siradaki_zaman = datetime.strptime(v['Fajr'], "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day) + timedelta(days=1)

    kalan = siradaki_zaman - simdi
    saat, mod = divmod(kalan.seconds, 3600); dak, san = divmod(mod, 60)

    # 2. Madde: Yuvarlak Geri Sayım
    st.markdown(f"""
        <div class='yuvarlak-sayaç'>
            <div style='font-size:1.2rem;'>{siradaki_ad.upper()}</div>
            <div style='font-size:3rem; font-weight:bold;'>{saat:02d}:{dak:02d}</div>
            <div style='font-size:1rem;'>{LANGS[L]['kalan']}</div>
        </div>
    """, unsafe_allow_html=True)

    # Tarih (Türkçe Miladi & Hicri)
    st.markdown(f"<p style='text-align:center;'>📅 {t['gregorian']['day']} {t['gregorian']['month']['en']} | 🌙 {t['hijri']['day']} {t['hijri']['month']['ar']}</p>", unsafe_allow_html=True)

    # 3. Madde: Vakitler (3+3 Düzeni)
    st.subheader("☀️ Sabah & Öğle")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='vakit-kart'><b>İMSAK</b><div class='vakit-saat'>{v['Fajr']}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='vakit-kart'><b>GÜNEŞ</b><div class='vakit-saat'>{v['Sunrise']}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='vakit-kart'><b>ÖĞLE</b><div class='vakit-saat'>{v['Dhuhr']}</div></div>", unsafe_allow_html=True)

    st.subheader("🌙 Akşam")
    c4, c5, c6 = st.columns(3)
    c4.markdown(f"<div class='vakit-kart'><b>İKİNDİ</b><div class='vakit-saat'>{v['Asr']}</div></div>", unsafe_allow_html=True)
    c5.markdown(f"<div class='vakit-kart'><b>AKŞAM</b><div class='vakit-saat'>{v['Maghrib']}</div></div>", unsafe_allow_html=True)
    c6.markdown(f"<div class='vakit-kart'><b>YATSI</b><div class='vakit-saat'>{v['Isha']}</div></div>", unsafe_allow_html=True)

    # 14. Madde: Otomatik Ezan Sesi (Vakit Gelince)
    if kalan.seconds < 5:
        st.audio("https://www.soundboard.com/handler/DownLoadTrack.ashx?cliptoken=ea395b7b-2313-4e6a-8d3c-99f493540f26")
        st.toast("Ezan Vakti! Namazını kıldın mı?")

except:
    st.error("Veri yüklenemedi.")

time.sleep(60)
st.rerun()