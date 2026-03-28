import streamlit as st
import requests
from datetime import datetime, timedelta

# --- SAYFA AYARI ---
st.set_page_config(
    page_title="Huzur İslamda",
    page_icon="🕋",
    layout="wide"
)

# --- CSS TASARIM ---
st.markdown("""
<style>
.stApp { background-color: #6a1b9a; color: #fff; }

.besmele {
    text-align: center;
    font-size: 3rem;
    font-weight: bold;
}

.geri-sayim-kutu {
    text-align: center;
    background: #fbc02d;
    color: black;
    padding: 20px;
    border-radius: 12px;
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 20px;
}

.vakit-kutusu {
    background: white;
    border-radius: 15px;
    padding: 25px;
    text-align: center;
    color: black;
    margin-bottom: 10px;
}

.vakit-ad {
    font-size: 1.5rem;
    font-weight: bold;
}

.vakit-saat {
    font-size: 2.5rem;
    color: #d4af37;
    font-weight: bold;
}

.zikir-sayi {
    font-size: 6rem;
    text-align: center;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- SABİTLER ---
AYLAR = {
    "January": "Ocak", "February": "Şubat", "March": "Mart",
    "April": "Nisan", "May": "Mayıs", "June": "Haziran",
    "July": "Temmuz", "August": "Ağustos", "September": "Eylül",
    "October": "Ekim", "November": "Kasım", "December": "Aralık"
}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🕋 REHBER")
    sehir = st.selectbox("Şehir", [
        "Istanbul", "Ankara", "Izmir", "Bursa",
        "Adana", "Konya", "Antalya", "Gaziantep"
    ])

# --- BAŞLIK ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)

# --- API ---
try:
    url = f"https://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        st.error("API bağlantı hatası.")
        st.stop()

    data = response.json().get("data", {})
    timings = data.get("timings", {})
    date = data.get("date", {}).get("gregorian", {})

    if not timings:
        st.error("Veri alınamadı.")
        st.stop()

    # --- GERİ SAYIM ---
    vakitler = {
        "İmsak": timings["Fajr"],
        "Güneş": timings["Sunrise"],
        "Öğle": timings["Dhuhr"],
        "İkindi": timings["Asr"],
        "Akşam": timings["Maghrib"],
        "Yatsı": timings["Isha"]
    }

    now = datetime.now()
    next_time = None
    next_name = ""

    for name, t in vakitler.items():
        dt = datetime.strptime(t, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        if dt > now:
            next_time = dt
            next_name = name
            break

    if not next_time:
        next_time = datetime.strptime(timings["Fajr"], "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        ) + timedelta(days=1)
        next_name = "İmsak"

    diff = next_time - now
    h, rem = divmod(diff.seconds, 3600)
    m, s = divmod(rem, 60)

    st.markdown(
        f"<div class='geri-sayim-kutu'>⏳ {next_name} vaktine kalan: {h:02d}:{m:02d}:{s:02d}</div>",
        unsafe_allow_html=True
    )

    # --- TARİH ---
    st.markdown(
        f"<h3 style='text-align:center'>{date.get('day')} {AYLAR.get(date.get('month', {}).get('en'))} {date.get('year')}</h3>",
        unsafe_allow_html=True
    )

    # --- VAKİTLER ---
    cols = st.columns(3)
    for i, (name, t) in enumerate(vakitler.items()):
        with cols[i % 3]:
            st.markdown(
                f"<div class='vakit-kutusu'><div class='vakit-ad'>{name}</div><div class='vakit-saat'>{t}</div></div>",
                unsafe_allow_html=True
            )

    # --- ZİKİRMATİK ---
    st.divider()
    st.subheader("📿 Zikirmatik")

    if "zikir" not in st.session_state:
        st.session_state.zikir = 0

    st.markdown(f"<div class='zikir-sayi'>{st.session_state.zikir}</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    if col1.button("➕ Artır"):
        st.session_state.zikir += 1
        st.rerun()

    if col2.button("🔄 Sıfırla"):
        st.session_state.zikir = 0
        st.rerun()

except Exception as e:
    st.error(f"Hata oluştu: {e}")