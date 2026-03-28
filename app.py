import streamlit as st
import requests
from datetime import datetime, timedelta
import time
from streamlit_autorefresh import st_autorefresh # Canlı geri sayım için

# --- 1. AYARLAR VE TASARIM (ÖZEL CSS) ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

# Her 1 saniyede sayfayı yeniler (Geri sayımı canlandırır)
st_autorefresh(interval=1000, key="prayer_countdown")

st.markdown("""
    <style>
    .stApp { background-color: #6a1b9a; color: #fff; } /* Lila Arka Plan */
    .stApp > div { padding-top: 0 !important; }

    /* Ana Başlık */
    .besmele { text-align: center; color: #fff; font-size: 3rem; font-weight: bold; margin-bottom: 5px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    
    /* Geri Sayım (Sarı Bant) */
    .geri-sayim-kutu { text-align: center; background: #fbc02d; color: #000; padding: 20px; border-radius: 12px; font-size: 2.2rem; font-weight: 900; margin-bottom: 30px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); border: 3px solid #f9a825; }
    
    /* Vakit Başlıkları */
    .vakit-baslik { color: #fff; font-size: 2rem; font-weight: bold; margin-top: 25px; border-bottom: 3px solid #fff; padding-bottom: 10px; margin-bottom: 20px; text-align: center; text-transform: uppercase; }
    
    /* Vakit Kartları */
    .vakit-kutusu { background: #ffffff; border-radius: 20px; padding: 40px; text-align: center; border-bottom: 15px solid #d4af37; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .vakit-ad { color: #000 !important; font-size: 2.5rem; font-weight: bold; margin-bottom: 10px; }
    .vakit-saat { color: #d4af37 !important; font-size: 4.5rem; font-weight: 900; line-height: 1; }
    
    /* Haftalık Satırlar */
    .haftalik-satir { background: #fff; border-left: 10px solid #d4af37; padding: 22px; border-radius: 12px; margin-bottom: 15px; font-size: 1.4rem; display: flex; justify-content: space-between; align-items: center; color: #000; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
    
    /* Yan Menü (Sidebar) */
    .sidebar-baslik { text-align: center; color: #fff; font-size: 1.8rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 2px solid #fff; padding-bottom: 10px; }
    .stSelectbox { color: #fff; }
    .stTabs [data-baseweb="tab-list"] { background-color: #4a148c; }
    .stTabs [data-baseweb="tab"] { color: #aaa; font-weight: bold; }
    .stTabs [data-baseweb="tab"]:hover { color: #fff; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #fff; border-bottom-color: #d4af37; }
    
    /* Veri Kutuları */
    .bilgi-kutusu { background: #4a148c; padding: 15px; border-radius: 8px; margin-bottom: 10px; color: #fff; font-size: 1rem; line-height: 1.6; border: 1px solid #7c43bd; }
    .bilgi-baslik { color: #fbbf24; font-weight: bold; font-size: 1.2rem; margin-bottom: 5px; }
    
    /* Zikirmatik */
    .zikir-sayi { font-size: 15rem !important; color: #fff; font-weight: 900; text-align: center; text-shadow: 0 0 50px rgba(0,0,0,0.5); line-height: 1; margin: 40px 0; }
    .stButton > button { background-color: #fbc02d !important; color: #000 !important; font-weight: bold !important; font-size: 1.2rem !important; border-radius: 10px !important; border: 2px solid #f9a825 !important; }
    .stButton > button:hover { background-color: #f9a825 !important; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TAM TÜRKÇE VERİ SETLERİ ---
AYLAR = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}

FARZ_32 = {
    "İmanın Şartları": "Allah’a, Meleklere, Kitaplara, Peygamberlere, Ahiret gününe ve Kadere inanmak.",
    "İslamın Şartları": "Kelime-i Şehadet, Namaz, Oruç, Zekat, Hac.",
    "Abdestin Farzları": "Yüzü yıkamak, Kolları dirseklerle beraber yıkamak, Başın 1/4'ünü meshetmek, Ayakları topuklarla beraber yıkamak.",
    "Guslün Farzları": "Ağza su, Burna su, Bütün vücudu iğne ucu kadar kuru yer kalmadan yıkamak.",
    "Teyemmümün Farzları": "Niyet, Elleri temiz toprağa vurup yüzü ve kolları meshetmek.",
    "Namazın Farzları": "Hadesten/Necasetten taharet, Setr-i avret, İstikbal-i kıble, Vakit, Niyet, İftitah tekbiri, Kıyam, Kıraat, Rükû, Sücud, Ka'de-i ahîre."
}

# Son 10 Sure ve Anlamları
SURELER = {
    "Fil Suresi": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl...",
    "Kureyş Suresi": "Li îlâfi kureyş...",
    "Mâûn Suresi": "Era'eytellezî yükezzibü bid dîn...",
    "Kevser Suresi": "İnnâ a'taynâkel kevser...",
    "Kâfirûn Suresi": "Kul yâ eyyühel kâfirûn...",
    "Nasr Suresi": "İzâ câe nasrullâhi vel feth...",
    "Tebbet Suresi": "Tebbet yedâ ebî lehebin ve tebb...",
    "İhlâs Suresi": "Kul hüvallâhü ehad. Allâhüs samed...",
    "Felak Suresi": "Kul e'ûzü bi rabbil felak...",
    "Nâs Suresi": "Kul e'ûzü bi rabbin nâs..."
}

# --- 3. YAN MENÜ ---
with st.sidebar:
    st.markdown("<div class='sidebar-baslik'>🕋 REHBER</div>", unsafe_allow_html=True)
    
    # Şehir Seçimi
    sehir = st.selectbox("📍 Şehir Seçiniz", ["İstanbul", "Ankara", "İzmir", "Bursa", "Adana", "Konya", "Antalya", "Gaziantep", "Şanlıurfa", "Kocaeli"])
    
    # Bilgi Sekmeleri (Tabs)
    tab1, tab2, tab3 = st.tabs(["📌 32 Farz", "✨ Sureler", "💫 Esmaül Hüsna"])
    
    with tab1:
        for b, i in FARZ_32.items():
            st.markdown(f"<div class='bilgi-kutusu'><div class='bilgi-baslik'>{b}:</div><br>{i}</div>", unsafe_allow_html=True)
            
    with tab2:
        for s_ad, s_met in SURELER.items():
            st.markdown(f"<div class='bilgi-kutusu'><div class='bilgi-baslik'>{s_ad}:</div><br>{s_met}</div>", unsafe_allow_html=True)

    with tab3:
        st.write("**Esmaül Hüsna ve anlamları buradadır.**")

# --- 4. ANA EKRAN ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)

try:
    # Şehir ismini API için uygun hale getir (Türkçe karakterleri düzelt)
    s_api = sehir.replace("İ", "I").replace("ı", "i").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    data = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={s_api}&country=Turkey&method=13").json()['data']
    v = data['timings']
    g = data['date']['gregorian']
    h = data['date']['hijri']

    # --- CANLI GERİ SAYIM (SARI BANT) ---
    # Türkçe etiketler üzerinden sıradaki vakit hesaplaması
    v_tr = {"İmsak": v['Fajr'], "Güneş": v['Sunrise'], "Öğle": v['Dhuhr'], "İkindi": v['Asr'], "Akşam": v['Maghrib'], "Yatsı": v['Isha']}
    
    simdi = datetime.now()
    siradaki_ad = ""; siradaki_zaman = None

    for ad, saat in v_tr.items():
        v_dt = datetime.strptime(saat, "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day)
        if v_dt > simdi:
            siradaki_ad = ad; siradaki_zaman = v_dt; break
    if not siradaki_zaman: # Gece yarısından sonra ise yarına bak
        siradaki_ad = "İmsak"
        siradaki_zaman = datetime.strptime(v['Fajr'], "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day) + timedelta(days=1)

    kalan = siradaki_zaman - simdi
    saat, mod = divmod(kalan.seconds, 3600)
    dak, san = divmod(mod, 60)
    
    st.markdown(f"<div class='geri-sayim-kutu'>⏳ {siradaki_ad.upper()} Vaktine Kalan: {saat:02d}:{dak:02d}:{san:02d}</div>", unsafe_allow_html=True)

    # Güncel Tarih
    st.markdown(f"<h2 style='text-align:center; color:#fff; font-size:2.5rem; font-weight:700; margin-bottom:30px; text-shadow:1px 1px 2px #000;'>{g['day']} {AYLAR.get(g['month']['en'])} {g['year']} | 🌙 {h['day']} {h['month']['ar']} {h['year']}</h2>", unsafe_allow_html=True)

    # --- VAKİTLER: 3+3 TAM YAN YANA DÜZEN ---
    # Grup 1: İmsak, Güneş, Öğle
    st.markdown("<div class='vakit-baslik'>☀️ GÜNDÜZ VAKİTLERİ</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>İMSAK</div><div class='vakit-saat'>{v['Fajr']}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>GÜNEŞ</div><div class='vakit-saat'>{v['Sunrise']}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>ÖĞLE</div><div class='vakit-saat'>{v['Dhuhr']}</div></div>", unsafe_allow_html=True)

    # Grup 2: İkindi, Akşam, Yatsı
    st.markdown("<div class='vakit-baslik'>🌙 AKŞAM VAKİTLERİ</div>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>İKİNDİ</div><div class='vakit-saat'>{v['Asr']}</div></div>", unsafe_allow_html=True)
    with c5: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>AKŞAM</div><div class='vakit-saat'>{v['Maghrib']}</div></div>", unsafe_allow_html=True)
    with c6: st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>YATSI</div><div class='vakit-saat'>{v['Isha']}</div></div>", unsafe_allow_html=True)

    # --- ZİKİRMATİK (TÜM GENİŞLİK) ---
    st.divider()
    st.markdown("<div class='besmele' style='font-size:3.5rem;'>📿 ZİKİRMATİK</div>", unsafe_allow_html=True)
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f"<div class='zikir-sayi'>{st.session_state.zk}</div>", unsafe_allow_html=True)
    
    col_z1, col_z2 = st.columns(2)
    if col_z1.button("➕ ZİKİR ÇEK", use_container_width=True):
        st.session_state.zk += 1
        st.rerun()
    if col_z2.button("🔄 SIFIRLA", use_container_width=True):
        st.session_state.zk = 0
        st.rerun()

    # --- HAFTALIK SATIR GÖRÜNÜMÜ (DEVAMLILIK) ---
    st.divider()
    st.subheader("🗓️ Haftalık Namaz Vakitleri (7 Gün)")
    h_data = requests.get(f"http://api.aladhan.com/v1/calendarByCity?city={s_api}&country=Turkey&method=13").json()['data']
    bugun = datetime.now().day
    for gun in h_data:
        dg = gun['date']['gregorian']; tv = gun['timings']
        if int(dg['day']) >= bugun and int(dg['day']) < bugun + 7:
            st.markdown(f"""
                <div class='haftalik-satir'>
                    <b style='color:#000; min-width:160px;'>{dg['day']} {AYLAR.get(dg['month']['en'])}</b>
                    <span>İmsak: <b>{tv['Fajr']}</b> | Öğle: <b>{tv['Dhuhr']}</b> | İkindi: <b>{tv['Asr']}</b> | Akşam: <b>{tv['Maghrib']}</b> | Yatsı: <b>{tv['Isha']}</b></span>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error("Veri güncellenemedi.")