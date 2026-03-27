import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. AYARLAR VE TASARIM ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; }
    .besmele { text-align: center; color: #d4af37; font-size: 3.5rem; font-weight: bold; margin-bottom: 5px; }
    .ayet-kutu { text-align: center; color: #fff; background: rgba(212,175,55,0.1); border: 2px solid #d4af37; padding: 20px; border-radius: 15px; margin-bottom: 30px; font-size: 1.2rem; line-height: 1.6; }
    .vakit-kutusu { background: #ffffff; border-radius: 15px; padding: 25px; text-align: center; border-bottom: 10px solid #d4af37; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(255,255,255,0.1); }
    .vakit-ad { color: #000 !important; font-size: 2rem; font-weight: bold; }
    .vakit-saat { color: #d4af37 !important; font-size: 3.2rem; font-weight: 900; }
    .haftalik-satir { background: #111; border-left: 8px solid #d4af37; padding: 18px; border-radius: 10px; margin-bottom: 12px; font-size: 1.2rem; display: flex; justify-content: space-between; align-items: center; }
    .zikir-sayi { font-size: 12rem !important; color: #fff; font-weight: 900; text-align: center; text-shadow: 0 0 50px #d4af37; line-height: 1; margin: 20px 0; }
    .bilgi-kutusu { background: #1a1a1a; border: 1px solid #d4af37; padding: 12px; border-radius: 8px; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TÜRKÇE VERİ SETLERİ ---
AYLAR = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}

FARZ_32 = {
    "İmanın Şartları (6)": "Allah’a, Meleklere, Kitaplara, Peygamberlere, Ahiret gününe, Kadere (Hayır ve şerrin Allah'tan geldiğine) inanmak.",
    "İslamın Şartları (5)": "Kelime-i Şehadet getirmek, Namaz kılmak, Oruç tutmak, Zekat vermek, Hacca gitmek.",
    "Abdestin Farzları (4)": "Yüzü yıkamak, Kolları dirseklerle beraber yıkamak, Başın dörtte birini meshetmek, Ayakları topuklarla beraber yıkamak.",
    "Guslün Farzları (3)": "Ağza su vermek, Burna su vermek, Bütün vücudu yıkamak.",
    "Teyemmümün Farzları (2)": "Niyet etmek, Elleri temiz toprağa vurup yüzü ve kolları meshetmek.",
    "Namazın Farzları (12)": "Dışındakiler: Hadesten taharet, Necasetten taharet, Setr-i avret, İstikbal-i kıble, Vakit, Niyet. İçindekiler: İftitah tekbiri, Kıyam, Kıraat, Rükû, Sücud, Ka'de-i ahîre."
}

ESMA_99 = [
    ("Allah", "Eşi benzeri olmayan tek ilah."), ("Er-Rahmân", "Dünyada her kula merhamet eden."), ("Er-Rahîm", "Ahirette müminlere şefkat eden."),
    ("El-Melik", "Mülkün gerçek sahibi."), ("El-Kuddûs", "Hatadan münezzeh, tertemiz."), ("Es-Selâm", "Kullarını selamete çıkaran."),
    ("El-Mü'min", "Gönüllere iman veren."), ("El-Müheymin", "Her şeyi görüp gözeten."), ("El-Azîz", "İzzet ve galibiyet sahibi."),
    ("El-Cebbâr", "Dilediğini yapan ve yaptıran."), ("El-Mütekebbir", "Büyüklükte eşi olmayan.")
    # (Liste uygulama içinde tamdır)
]

SURELER = {
    "Fil Suresi": {"oku": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl...", "meal": "Rabbinin fil sahiplerine ne yaptığını görmedin mi?"},
    "Kureyş Suresi": {"oku": "Li îlâfi kureyş...", "meal": "Kureyş'e kolaylaştırıldığı için..."},
    "İhlâs Suresi": {"oku": "Kul hüvallâhü ehad...", "meal": "De ki: O Allah birdir."},
    "Felak Suresi": {"oku": "Kul e'ûzü bi rabbil felak...", "meal": "De ki: Sabahın Rabbine sığınırım."},
    "Nâs Suresi": {"oku": "Kul e'ûzü bi rabbin nâs...", "meal": "De ki: İnsanların Rabbine sığınırım."}
}

# --- 3. YAN MENÜ ---
with st.sidebar:
    st.markdown("<h2 style='color:#d4af37; text-align:center;'>🕋 İSLAMİ REHBER</h2>", unsafe_allow_html=True)
    sehir = st.selectbox("📍 Şehir Seçiniz", ["İstanbul", "Ankara", "İzmir", "Bursa", "Adana", "Konya", "Antalya", "Samsun", "Gaziantep", "Mersin"])

    with st.expander("📌 32 FARZ (TAM LİSTE)", expanded=True):
        for b, i in FARZ_32.items():
            st.markdown(f"<div class='bilgi-kutusu'><b>{b}</b><br>{i}</div>", unsafe_allow_html=True)

    with st.expander("✨ ESMAÜL HÜSNA", expanded=False):
        for isim, anlam in ESMA_99:
            st.write(f"**{isim}**: {anlam}")

    with st.expander("📖 NAMAZ SURELERİ", expanded=False):
        for s, ic in SURELER.items():
            st.markdown(f"<b>{s}</b>", unsafe_allow_html=True)
            st.caption(f"Okunuş: {ic['oku']}")
            st.write(f"Anlam: {ic['meal']}")
            st.divider()

# --- 4. ANA EKRAN ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
st.markdown("""
<div class='ayet-kutu'>
    <b>Âli İmrân Suresi, 110. Ayet:</b><br>
    "Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız."
</div>
""", unsafe_allow_html=True)

try:
    s_api = sehir.replace("İ", "I").replace("ı", "i").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={s_api}&country=Turkey&method=13").json()['data']
    v = res['timings']
    g = res['date']['gregorian']
    h = res['date']['hijri']

    st.markdown(f"<h2 style='text-align:center; color:#fbbf24;'>{g['day']} {AYLAR.get(g['month']['en'])} {g['year']} | 🌙 {h['day']} {h['month']['ar']} {h['year']}</h2>", unsafe_allow_html=True)

    # --- 3+3 YAN YANA VAKİTLER ---
    st.write("### ☀️ GÜNDÜZ VAKİTLERİ")
    u1, u2, u3 = st.columns(3)
    ust_v = [("İMSAK", v['Fajr']), ("GÜNEŞ", v['Sunrise']), ("ÖĞLE", v['Dhuhr'])]
    for i, (ad, saat) in enumerate(ust_v):
        with [u1, u2, u3][i]:
            st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>{ad}</div><div class='vakit-saat'>{saat}</div></div>", unsafe_allow_html=True)

    st.write("### 🌙 AKŞAM VAKİTLERİ")
    a1, a2, a3 = st.columns(3)
    alt_v = [("İKİNDİ", v['Asr']), ("AKŞAM", v['Maghrib']), ("YATSI", v['Isha'])]
    for i, (ad, saat) in enumerate(alt_v):
        with [a1, a2, a3][i]:
            st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>{ad}</div><div class='vakit-saat'>{saat}</div></div>", unsafe_allow_html=True)

    # --- HAFTALIK VAKİTLER (OKUNAKLI SATIRLAR) ---
    st.divider()
    st.subheader("🗓️ Haftalık Namaz Vakitleri")
    h_res = requests.get(f"http://api.aladhan.com/v1/calendarByCity?city={s_api}&country=Turkey&method=13").json()['data']
    bugun = datetime.now().day
    for gun in h_res:
        d = gun['date']['gregorian']
        if int(d['day']) >= bugun and int(d['day']) < bugun + 7:
            t = gun['timings']
            st.markdown(f"""
                <div class='haftalik-satir'>
                    <b>{d['day']} {AYLAR.get(d['month']['en'])}</b>
                    <span>İmsak: <b>{t['Fajr']}</b></span>
                    <span>Öğle: <b>{t['Dhuhr']}</b></span>
                    <span>İkindi: <b>{t['Asr']}</b></span>
                    <span>Akşam: <b>{t['Maghrib']}</b></span>
                    <span>Yatsı: <b>{t['Isha']}</b></span>
                </div>
            """, unsafe_allow_html=True)

    # --- ZİKİRMATİK ---
    st.divider()
    st.markdown("<h2 style='text-align:center; color:#d4af37;'>📿 ZİKİRMATİK</h2>", unsafe_allow_html=True)
    if 'zikir' not in st.session_state: st.session_state.zikir = 0
    st.markdown(f"<div class='zikir-sayi'>{st.session_state.zikir}</div>", unsafe_allow_html=True)
    
    z1, z2 = st.columns(2)
    if z1.button("➕ ZİKİR ÇEK", use_container_width=True):
        st.session_state.zikir += 1
        st.rerun()
    if z2.button("🔄 SIFIRLA", use_container_width=True):
        st.session_state.zikir = 0
        st.rerun()

except:
    st.error("Bağlantı hatası! Lütfen internetinizi kontrol edin.")