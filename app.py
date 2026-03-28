import streamlit as st
import requests
from datetime import datetime, timedelta

# --- 1. TASARIM VE STİL AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; }
    .besmele { text-align: center; color: #d4af37; font-size: 4rem; font-weight: bold; margin-bottom: 5px; }
    .ayet-kutu { text-align: center; color: #fff; background: rgba(212,175,55,0.1); border: 2px solid #d4af37; padding: 25px; border-radius: 15px; margin-bottom: 25px; font-size: 1.4rem; border-left: 15px solid #d4af37; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .geri-sayim { text-align: center; background: #d4af37; color: #000; padding: 15px; border-radius: 12px; font-size: 2rem; font-weight: bold; margin-bottom: 30px; }
    .vakit-baslik { color: #fbbf24; font-size: 2.2rem; font-weight: bold; margin-top: 30px; border-bottom: 2px solid #333; padding-bottom: 10px; text-align: center; }
    .vakit-kutusu { background: #ffffff; border-radius: 20px; padding: 40px; text-align: center; border-bottom: 15px solid #d4af37; margin-bottom: 20px; min-height: 200px; }
    .vakit-ad { color: #000 !important; font-size: 2.5rem; font-weight: bold; margin-bottom: 10px; }
    .vakit-saat { color: #d4af37 !important; font-size: 4.5rem; font-weight: 900; }
    .haftalik-satir { background: #111; border-left: 10px solid #d4af37; padding: 22px; border-radius: 12px; margin-bottom: 15px; font-size: 1.4rem; display: flex; justify-content: space-between; align-items: center; }
    .zikir-sayi { font-size: 15rem !important; color: #fff; font-weight: 900; text-align: center; text-shadow: 0 0 60px #d4af37; margin: 30px 0; }
    .sidebar-kutu { background: #151515; border: 1px solid #d4af37; padding: 15px; border-radius: 10px; margin-bottom: 10px; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TÜRKÇE VERİ SÖZLÜKLERİ ---
AYLAR = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}

FARZ_32 = {
    "İmanın Şartları (6)": "Allah’a, Meleklere, Kitaplara, Peygamberlere, Ahiret gününe ve Kadere inanmak.",
    "İslamın Şartları (5)": "Kelime-i Şehadet, Namaz kılmak, Oruç tutmak, Zekat vermek, Hacca gitmek.",
    "Abdestin Farzları (4)": "Yüzü yıkamak, Kolları yıkamak, Başın 1/4'ünü meshetmek, Ayakları yıkamak.",
    "Guslün Farzları (3)": "Ağza su vermek, Burna su vermek, Bütün vücudu yıkamak.",
    "Teyemmümün Farzları (2)": "Niyet etmek, Yüzü ve kolları meshetmek.",
    "Namazın Farzları (12)": "Hadesten/Necasetten taharet, Setr-i avret, İstikbal-i kıble, Vakit, Niyet, İftitah tekbiri, Kıyam, Kıraat, Rükû, Sücud, Ka'de-i ahîre."
}

# --- 3. YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#d4af37;'>🕋 DİNİ REHBER</h1>", unsafe_allow_html=True)
    sehir = st.selectbox("📍 Şehir", ["İstanbul", "Ankara", "İzmir", "Bursa", "Adana", "Konya", "Antalya", "Gaziantep", "Şanlıurfa", "Kocaeli"])
    
    with st.expander("📌 32 FARZ", expanded=True):
        for b, i in FARZ_32.items():
            st.markdown(f"<div class='sidebar-kutu'><b>{b}</b><br>{i}</div>", unsafe_allow_html=True)

# --- 4. ANA EKRAN AKIŞI ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)

# Âli İmrân 110. Ayet (Besmele Altında)
st.markdown("""
<div class='ayet-kutu'>
    <b style='color:#fbbf24; font-size:1.6rem;'>Âli İmrân Suresi, 110. Ayet:</b><br>
    "Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız."
</div>
""", unsafe_allow_html=True)

try:
    # API Bağlantısı (Türkçe Karakter Düzenlemesiyle)
    s_api = sehir.replace("İ", "I").replace("ı", "i").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    data = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={s_api}&country=Turkey&method=13").json()['data']
    v = data['timings']
    g = data['date']['gregorian']

    # --- DİNAMİK GERİ SAYIM ---
    v_liste = {"İmsak": v['Fajr'], "Güneş": v['Sunrise'], "Öğle": v['Dhuhr'], "İkindi": v['Asr'], "Akşam": v['Maghrib'], "Yatsı": v['Isha']}
    simdi = datetime.now()
    siradaki_ad = ""; siradaki_zaman = None

    for ad, saat in v_liste.items():
        v_dt = datetime.strptime(saat, "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day)
        if v_dt > simdi:
            siradaki_ad = ad; siradaki_zaman = v_dt
            break
    if not siradaki_zaman: # Gece yarısından sonra ise yarına bak
        siradaki_ad = "İmsak"
        siradaki_zaman = datetime.strptime(v['Fajr'], "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day) + timedelta(days=1)

    kalan = siradaki_zaman - simdi
    saat, mod = divmod(kalan.seconds, 3600)
    dak, san = divmod(mod, 60)
    
    st.markdown(f"<div class='geri-sayim'>⏳ {siradaki_ad} Vaktine Kalan: {saat:02d}:{dak:02d}:{san:02d}</div>", unsafe_allow_html=True)

    # Güncel Tarih
    st.markdown(f"<h2 style='text-align:center; color:#fbbf24; font-size:2.5rem;'>{g['day']} {AYLAR.get(g['month']['en'])} {g['year']}</h2>", unsafe_allow_html=True)

    # --- VAKİTLER: 3+3 TAM YAN YANA DÜZEN ---
    # Grup 1: İmsak, Güneş, Öğle
    st.markdown("<div class='vakit-baslik'>☀️ SABAH VE ÖĞLE VAKİTLERİ</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>İMSAK</div><div class='vakit-saat'>{v['Fajr']}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>GÜNEŞ</div><div class='vakit-saat'>{v['Sunrise']}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>ÖĞLE</div><div class='vakit-saat'>{v['Dhuhr']}</div></div>", unsafe_allow_html=True)

    # Grup 2: İkindi, Akşam, Yatsı
    st.markdown("<div class='vakit-baslik'>🌙 AKŞAM VE YATSI VAKİTLERİ</div>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>İKİNDİ</div><div class='vakit-saat'>{v['Asr']}</div></div>", unsafe_allow_html=True)
    with c5: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>AKŞAM</div><div class='vakit-saat'>{v['Maghrib']}</div></div>", unsafe_allow_html=True)
    with c6: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>YATSI</div><div class='vakit-saat'>{v['Isha']}</div></div>", unsafe_allow_html=True)

    # --- HAFTALIK SATIR LİSTESİ ---
    st.divider()
    st.subheader("🗓️ Haftalık Namaz Vakitleri (Okunaklı Satırlar)")
    h_data = requests.get(f"http://api.aladhan.com/v1/calendarByCity?city={s_api}&country=Turkey&method=13").json()['data']
    for gun in h_data[:7]:
        dg = gun['date']['gregorian']; tv = gun['timings']
        st.markdown(f"""
            <div class='haftalik-satir'>
                <b style='color:#fbbf24; min-width:160px;'>{dg['day']} {AYLAR.get(dg['month']['en'])}</b>
                <span>İmsak: <b>{tv['Fajr']}</b> | Öğle: <b>{tv['Dhuhr']}</b> | İkindi: <b>{tv['Asr']}</b> | Akşam: <b>{tv['Maghrib']}</b> | Yatsı: <b>{tv['Isha']}</b></span>
            </div>
        """, unsafe_allow_html=True)

    # --- ZİKİRMATİK ---
    st.divider()
    if 'zkr' not in st.session_state: st.session_state.zkr = 0
    st.markdown(f"<div class='zikir-sayi'>{st.session_state.zkr}</div>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK", use_container_width=True):
        st.session_state.zkr += 1
        st.rerun()

except Exception:
    st.error("Sistem şu an meşgul veya internet bağlantısı yok.")