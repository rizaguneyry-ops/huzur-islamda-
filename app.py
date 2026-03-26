import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta

# --- 1. SAYFA VE SES AYARLARI ---
st.set_page_config(page_title="Huzur İslamda Pro+", page_icon="🕌", layout="wide")

# Ezan Sesi Linki (Diyanet veya güvenilir kaynak)
EZAN_URL = "https://www.namazvaktim.org/ses/ezan1.mp3" 

# --- 2. CSS TASARIM ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.95)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2000") !important;
        background-size: cover !important;
    }
    .status-box {
        padding: 20px; border-radius: 15px; border: 1px solid #d4af37;
        background: rgba(212, 175, 55, 0.1); text-align: center; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. KENAR MENÜ ---
st.sidebar.title("⚙️ Bildirim Ayarları")
sehir = st.sidebar.selectbox("Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"])
ezan_aktif = st.sidebar.toggle("Vakit Gelince Ezan Oku", value=True)
hatirlatici_aktif = st.sidebar.toggle("30 Dakika Sonra Namazı Hatırlat", value=True)

# --- 4. VERİ ÇEKME VE MANTIK ---
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    vakitler = res['timings']
    simdi = datetime.now()
    simdi_str = simdi.strftime("%H:%M")

    # Vakitleri Kontrol Et
    vakit_isimleri = {"Fajr": "Sabah", "Dhuhr": "Öğle", "Asr": "İkindi", "Maghrib": "Akşam", "Isha": "Yatsı"}
    
    ezan_calinsin_mi = False
    hatirlatma_yapilsin_mi = False
    aktif_vakit_adi = ""

    for key, etiket in vakit_isimleri.items():
        vakit_vakti = vakitler[key]
        
        # 1. Ezan Oku (Tam vakit ise)
        if simdi_str == vakit_vakti:
            ezan_calinsin_mi = True
            aktif_vakit_adi = etiket

        # 2. 30 Dakika Sonra Hatırlat
        vakit_dt = datetime.strptime(vakit_vakti, "%H:%M")
        hatirlatma_dt = (vakit_dt + timedelta(minutes=30)).strftime("%H:%M")
        
        if simdi_str == hatirlatma_dt:
            hatirlatma_yapilsin_mi = True
            aktif_vakit_adi = etiket

    # --- GÖRSEL PANEL ---
    st.markdown(f"<h1 style='text-align:center; color:white;'>{sehir.upper()}</h1>", unsafe_allow_html=True)
    
    # Otomatik Ezan Çalar (HTML bileşeni)
    if ezan_aktif and ezan_calinsin_mi:
        st.markdown(f'<audio autoplay><source src="{EZAN_URL}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        st.toast(f"📢 {aktif_vakit_adi} Ezanı Okunuyor...", icon="🕌")

    # 30 Dakika Hatırlatıcı (Toast Bildirimi)
    if hatirlatici_aktif and hatirlatma_yapilsin_mi:
        st.balloons()
        st.warning(f"🕋 {aktif_vakit_adi} vakti gireli 30 dakika oldu. Namazınızı kıldınız mı?", icon="⏳")

    # Vakitleri Listele
    cols = st.columns(5)
    for i, (k, v_label) in enumerate(vakit_isimleri.items()):
        with cols[i]:
            bg = "rgba(212,175,55,0.4)" if simdi_str >= vakitler[k] else "rgba(255,255,255,0.1)"
            st.markdown(f"""
                <div style="background:{bg}; padding:15px; border-radius:10px; text-align:center; color:white; border:1px solid #d4af37;">
                    <div style="font-size:12px;">{v_label}</div>
                    <div style="font-size:20px; font-weight:bold;">{vakitler[k]}</div>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Sistem Hatası: {e}")

# --- 5. DİĞER MODÜLLER (Zikir, Farz, Abdest) ---
st.write("---")
t1, t2, t3 = st.tabs(["📿 Zikirmatik", "📜 32 Farz & Abdest", "📊 Kaza Takibi"])

with t1:
    if 'zk' not in st.session_state: st.session_state.zk = 0
    c1, c2 = st.columns([1, 3])
    with c1:
        st.metric("Zikir", st.session_state.zk)
        if st.button("ÇEK"): st.session_state.zk += 1; st.rerun()
    with c2:
        st.write("**99 Esmaül Hüsna**")
        st.caption("Allah, Er-Rahman, Er-Rahim, El-Melik, El-Kuddüs...")

with t2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### ✨ 32 Farz")
        st.info("İmanın 6, İslamın 5, Namazın 12, Abdestin 4, Guslün 3, Teyemmümün 2 şartı.")
    with col_b:
        st.markdown("### 💧 Abdestin Farzları")
        st.success("1. Yüzü yıkamak\n2. Kolları yıkamak\n3. Başı meshetmek\n4. Ayakları yıkamak")

with t3:
    st.subheader("Kaza Namazı Borçları")
    # Önceki kodlardaki kaza namazı butonları buraya eklenebilir.
    st.write("Buradan kaza namazlarınızı kaydedebilirsiniz.")

# Sayfayı her dakika yenile (Vakit kontrolü için)
time.sleep(60)
st.rerun()