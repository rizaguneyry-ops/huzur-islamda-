import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# --- 1. AYARLAR VE TASARIM (GÖRSELE UYGUN LİLA TEMA) ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #6a1b9a; color: #fff; } 
    .besmele { text-align: center; color: #fff; font-size: 3rem; font-weight: bold; margin-bottom: 5px; }
    .geri-sayim-kutu { text-align: center; background: #fbc02d; color: #000; padding: 20px; border-radius: 12px; font-size: 2.2rem; font-weight: 900; margin-bottom: 30px; border: 3px solid #f9a825; }
    .vakit-baslik { color: #fff; font-size: 2rem; font-weight: bold; margin-top: 25px; border-bottom: 3px solid #fff; padding-bottom: 10px; text-align: center; }
    .vakit-kutusu { background: #ffffff; border-radius: 20px; padding: 40px; text-align: center; border-bottom: 15px solid #d4af37; margin-bottom: 15px; }
    .vakit-ad { color: #000 !important; font-size: 2.5rem; font-weight: bold; }
    .vakit-saat { color: #d4af37 !important; font-size: 4.5rem; font-weight: 900; }
    .haftalik-satir { background: #fff; border-left: 10px solid #d4af37; padding: 20px; border-radius: 12px; margin-bottom: 12px; color: #000; display: flex; justify-content: space-between; align-items: center; }
    .zikir-sayi { font-size: 15rem !important; color: #fff; font-weight: 900; text-align: center; line-height: 1; margin: 40px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ SETLERİ ---
AYLAR = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}

FARZ_32 = {
    "İmanın Şartları": "Allah’a, Meleklere, Kitaplara, Peygamberlere, Ahiret gününe ve Kadere inanmak.",
    "İslamın Şartları": "Kelime-i Şehadet, Namaz, Oruç, Zekat, Hac.",
    "Abdestin Farzları": "Yüzü yıkamak, Kolları yıkamak, Başın 1/4'ünü meshetmek, Ayakları yıkamak.",
    "Guslün Farzları": "Ağza su, Burna su, Bütün vücudu yıkamak.",
    "Teyemmümün Farzları": "Niyet, Yüzü ve kolları meshetmek.",
    "Namazın Farzları": "Hadesten/Necasetten taharet, Setr-i avret, İstikbal-i kıble, Vakit, Niyet, İftitah tekbiri, Kıyam, Kıraat, Rükû, Sücud, Ka'de-i ahîre."
}

# --- 3. YAN MENÜ ---
with st.sidebar:
    st.markdown("<h1 style='color:#fff;'>🕋 REHBER</h1>", unsafe_allow_html=True)
    sehir = st.selectbox("📍 Şehir", ["İstanbul", "Ankara", "İzmir", "Bursa", "Adana", "Konya", "Antalya"])
    with st.expander("📌 32 FARZ", expanded=True):
        for b, i in FARZ_32.items():
            st.write(f"**{b}:** {i}")

# --- 4. ANA EKRAN ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)

# Geri Sayım Alanı (Hata vermeyen yöntem)
geri_sayim_alani = st.empty()

try:
    s_api = sehir.replace("İ", "I").replace("ı", "i").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    data = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={s_api}&country=Turkey&method=13").json()['data']
    v = data['timings']
    
    # GERİ SAYIM DÖNGÜSÜ (Canlı akış için)
    v_tr = {"İmsak": v['Fajr'], "Güneş": v['Sunrise'], "Öğle": v['Dhuhr'], "İkindi": v['Asr'], "Akşam": v['Maghrib'], "Yatsı": v['Isha']}
    simdi = datetime.now()
    siradaki_ad = ""; siradaki_zaman = None

    for ad, saat in v_tr.items():
        v_dt = datetime.strptime(saat, "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day)
        if v_dt > simdi:
            siradaki_ad = ad; siradaki_zaman = v_dt; break
    if not siradaki_zaman:
        siradaki_ad = "İmsak"; siradaki_zaman = datetime.strptime(v['Fajr'], "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day) + timedelta(days=1)

    kalan = siradaki_zaman - simdi
    saat, mod = divmod(kalan.seconds, 3600); dak, san = divmod(mod, 60)
    
    # SARI BANT TASARIMI
    geri_sayim_alani.markdown(f"<div class='geri-sayim-kutu'>⏳ {siradaki_ad.upper()} Vaktine Kalan: {saat:02d}:{dak:02d}:{san:02d}</div>", unsafe_allow_html=True)

    # VAKİTLER (3+3 YAN YANA)
    st.markdown("<div class='vakit-baslik'>☀️ GÜNDÜZ VAKİTLERİ</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>İMSAK</div><div class='vakit-saat'>{v['Fajr']}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>GÜNEŞ</div><div class='vakit-saat'>{v['Sunrise']}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>ÖĞLE</div><div class='vakit-saat'>{v['Dhuhr']}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='vakit-baslik'>🌙 AKŞAM VAKİTLERİ</div>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>İKİNDİ</div><div class='vakit-saat'>{v['Asr']}</div></div>", unsafe_allow_html=True)
    with c5: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>AKŞAM</div><div class='vakit-saat'>{v['Maghrib']}</div></div>", unsafe_allow_html=True)
    with c6: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>YATSI</div><div class='vakit-saat'>{v['Isha']}</div></div>", unsafe_allow_html=True)

    # ZİKİRMATİK
    st.divider()
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f"<div class='zikir-sayi'>{st.session_state.zk}</div>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK", use_container_width=True):
        st.session_state.zk += 1
        st.rerun()

except:
    st.error("Bağlantı hatası!")

# Sayfayı 30 saniyede bir otomatik tazeler (Dış kütüphanesiz yedek yöntem)
time.sleep(30)
st.rerun()