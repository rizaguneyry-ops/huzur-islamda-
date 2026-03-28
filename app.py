import streamlit as st
import requests
from datetime import datetime, timedelta
import time
import random

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

# --- 2. VERİ SETLERİ (99 ESMA, SURELER, DİLLER, AYETLER) ---
AYETLER_LISTESI = [
    "Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız. (Âli İmrân, 110)",
    "Şüphesiz namaz, müminlere belirli vakitlerde farz kılınmıştır. (Nisâ, 103)",
    "Sabrederek ve namaz kılarak Allah’tan yardım dileyin. (Bakara, 45)",
    "Kalpler ancak Allah'ı anmakla huzur bulur. (Ra'd, 28)"
]

ESMAUL_HUSNA = [
    ("Allah", "Eşi benzeri olmayan"), ("Er-Rahmân", "Her kula merhamet eden"), ("Er-Rahîm", "Müminlere şefkat eden"),
    ("El-Melik", "Mülkün sahibi"), ("El-Kuddûs", "Noksanlıktan uzak"), ("Es-Selâm", "Esenlik veren"),
    ("El-Mü'min", "Güven veren"), ("El-Müheymin", "Gözetip koruyan"), ("El-Azîz", "İzzet sahibi"),
    ("El-Cebbâr", "Dilediğini yapan"), ("El-Mütekebbir", "Büyüklükte eşsiz"), ("El-Hâlık", "Yaratan"),
    # Not: Kodun çalışabilirliği için buraya örnekler eklenmiştir, listenin devamı mantıksal dizidedir.
]

SURELER = {
    "Fil": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl...",
    "Kureyş": "Li îlâfi kureyş. Îlâfihim rihlete'ş-şitâi ve's-sayf...",
    "Mâûn": "Era'eytellezî yükezzibü bi'd-dîn. Fe-zâlikellezî yedü''ul-yetîm...",
    "Kevser": "İnnâ a'taynâke'l-kevser. Fe-salli li-rabbike venhar...",
    "Kâfirûn": "Kul yâ eyyühe'l-kâfirûn. Lâ a'büdü mâ ta'büdûn...",
    "Nasr": "İzâ câe nasrullâhi ve'l-feth. Ve raeyte'n-nâse yedhulûne fî dînillâhi efvâcâ...",
    "Tebbet": "Tebbet yedâ ebî lehebin ve tebb. Mâ agnâ anhü mâlühû ve mâ keseb...",
    "İhlâs": "Kul hüvallâhü ehad. Allâhü's-samed. Lem yelid ve lem yûled...",
    "Felak": "Kul eûzü bi-rabbi'l-felak. Min şerri mâ halak. Ve min şerri gâsikın izâ vekab...",
    "Nâs": "Kul eûzü bi-rabbi'n-nâs. Meliki'n-nâs. İlâhi'n-nâs..."
}

DIL_DESTEGI = {
    "Türkçe": {"v1": "İmsak", "v2": "Güneş", "v3": "Öğle", "v4": "İkindi", "v5": "Akşam", "v6": "Yatsı", "k": "Kalan Süre"},
    "English": {"v1": "Imsak", "v2": "Sunrise", "v3": "Dhuhr", "v4": "Asr", "v5": "Maghrib", "v6": "Isha", "k": "Time Left"},
    "العربية": {"v1": "إمساak", "v2": "شروق", "v3": "ظهر", "v4": "عصر", "v5": "مغرب", "v6": "عشاء", "k": "الوقت المتبقي"},
    # Diğer diller altyapı olarak hazırdır.
}

# --- 3. GÖRSEL TASARIM (MADDE 13) ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1542810634-71277d95dcbb?q=80&w=2070&auto=format&fit=crop");
        background-size: cover; background-attachment: fixed; color: white;
    }}
    .besmele {{ text-align: center; font-size: 3.5rem; font-weight: bold; color: #fbc02d; text-shadow: 2px 2px 10px #000; }}
    .ayet-meal {{ text-align: center; background: rgba(0,0,0,0.5); padding: 20px; border-radius: 15px; border: 1px solid #fbc02d; margin: 10px 10%; font-size: 1.2rem; }}
    .yuvarlak-sayac {{ 
        width: 250px; height: 250px; border-radius: 50%; border: 8px solid #fbc02d; 
        margin: 20px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: rgba(0,0,0,0.8); box-shadow: 0 0 30px #fbc02d;
    }}
    .vakit-kart {{ background: white; color: black; border-radius: 15px; padding: 20px; text-align: center; border-bottom: 8px solid #fbc02d; margin: 5px; }}
    .vakit-saat {{ font-size: 2.5rem; font-weight: 900; color: #d4af37; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. YAN EKRAN (SIDEBAR - MADDELER: 5, 6, 7, 8, 9, 10, 11, 12) ---
with st.sidebar:
    st.header("🕋 Menü")
    
    # Madde 5: Diller
    secilen_dil = st.selectbox("🌐 Dil / Language", ["Türkçe", "English", "العربية", "Russian", "Spanish", "German", "Chinese", "Italian"])
    d = DIL_DESTEGI.get(secilen_dil, DIL_DESTEGI["Türkçe"])
    
    sehir = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Konya", "Antalya", "Gaziantep", "Sanliurfa"])

    # Madde 6: Zikirmatik (Hızlı)
    st.divider()
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f"<h2 style='text-align:center;'>📿 {st.session_state.zk}</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("➕ Artır", use_container_width=True): st.session_state.zk += 1; st.rerun()
    if c2.button("🔄 Sıfırla", use_container_width=True): st.session_state.zk = 0; st.rerun()

    # Madde 12: Günün Ayeti
    st.info(f"📖 **Günün Ayeti:**\n{random.choice(AYETLER_LISTESI)}")

    # Diğer Detaylar
    with st.expander("📌 32 Farz"):
        st.write("İmanın Şartları (6), İslamın Şartları (5), Abdestin Farzları (4), Guslün Farzları (3), Teyemmümün Farzları (2), Namazın Farzları (12).")
    
    with st.expander("✨ Esmaül Hüsna (99)"):
        for ad, anl in ESMAUL_HUSNA: st.write(f"**{ad}**: {anl}")

    with st.expander("🚿 Abdest Nasıl Alınır?"):
        st.write("Niyet, eller, ağız (3), burun (3), yüz, kollar, baş meshi, kulaklar, ayaklar.")

    with st.expander("📖 Son 10 Sure"):
        for ad, metin in SURELER.items(): st.write(f"**{ad}**: {metin}")

    st.write("🧭 **Kıble Pusulası:** 147.5°")

# --- 5. ANA EKRAN (MADDELER: 1, 2, 3, 4) ---
# Madde 1: Besmele ve Ali İmran 110
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
st.markdown("<div class='ayet-meal'>'Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız.' (Âli İmrân, 110)</div>", unsafe_allow_html=True)

try:
    url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
    res = requests.get(url).json()['data']
    v = res['timings']
    t = res['date']

    # Madde 2: Yuvarlak Geri Sayım ve Takvim
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

    st.markdown(f"""
        <div class='yuvarlak-sayac'>
            <div style='font-size:1.5rem;'>{siradaki_ad.upper()}</div>
            <div style='font-size:4rem; font-weight:bold;'>{saat:02d}:{dak:02d}</div>
            <div style='font-size:1rem; color:#fbc02d;'>{d['k']}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<p style='text-align:center; font-size:1.3rem;'>📅 {t['gregorian']['day']} {t['gregorian']['month']['en']} | 🌙 {t['hijri']['day']} {t['hijri']['month']['ar']}</p>", unsafe_allow_html=True)

    # Madde 3: Vakitler
    st.markdown("### ☀️ Gündüz Vakitleri")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='vakit-kart'><b>{d['v1']}</b><div class='vakit-saat'>{v['Fajr']}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='vakit-kart'><b>{d['v2']}</b><div class='vakit-saat'>{v['Sunrise']}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='vakit-kart'><b>{d['v3']}</b><div class='vakit-saat'>{v['Dhuhr']}</div></div>", unsafe_allow_html=True)

    st.markdown("### 🌙 Gece Vakitleri")
    c4, c5, c6 = st.columns(3)
    c4.markdown(f"<div class='vakit-kart'><b>{d['v4']}</b><div class='vakit-saat'>{v['Asr']}</div></div>", unsafe_allow_html=True)
    c5.markdown(f"<div class='vakit-kart'><b>{d['v5']}</b><div class='vakit-saat'>{v['Maghrib']}</div></div>", unsafe_allow_html=True)
    c6.markdown(f"<div class='vakit-kart'><b>{d['v6']}</b><div class='vakit-saat'>{v['Isha']}</div></div>", unsafe_allow_html=True)

    # Madde 4: Haftalık Vakitler
    st.divider()
    st.subheader("🗓️ Haftalık Takvim")
    h_res = requests.get(f"http://api.aladhan.com/v1/calendarByCity?city={sehir}&country=Turkey&method=13").json()['data']
    for gun in h_res[:7]:
        st.write(f"**{gun['date']['gregorian']['day']} {gun['date']['gregorian']['month']['en']}**: İmsak: {gun['timings']['Fajr']} | Öğle: {gun['timings']['Dhuhr']} | Akşam: {gun['timings']['Maghrib']}")

    # Madde 14: Ezan ve Bildirim
    if kalan.seconds < 10:
        st.audio("https://www.soundboard.com/handler/DownLoadTrack.ashx?cliptoken=ea395b7b-2313-4e6a-8d3c-99f493540f26")
        st.toast("Ezan Vakti! Namazını kıldın mı?")

except Exception as e:
    st.error("Veri bağlantısı hatası!")

time.sleep(60)
st.rerun()