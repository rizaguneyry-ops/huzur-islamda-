import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. AYARLAR ---
st.set_page_config(page_title="Huzur İslamda Pro Max", page_icon="🕋", layout="wide")

# --- 2. GÜNÜN HADİSİ VE ESMAÜL HÜSNA VERİSİ ---
gunun_hadisi = "“Sizin en hayırlınız, Kur’an’ı öğrenen ve öğreteninizdir.” (Buhârî, Fezâilü’l-Kur’ân, 21)"

esma_full = {
    "Allah": "Eşi benzeri olmayan, tek ilah.", "Er-Rahmân": "Dünyada her kula merhamet eden.",
    "Er-Rahîm": "Ahirette sadece müminlere şefkat eden.", "El-Melik": "Kainatın mutlak sahibi.",
    "El-Kuddûs": "Hatadan münezzeh, tertemiz.", "Es-Selâm": "Kullarını selamete çıkaran.",
    "El-Mü'min": "Gönüllere iman veren.", "El-Müheymin": "Her şeyi görüp gözeten.",
    "El-Azîz": "İzzet ve galibiyet sahibi.", "El-Cebbâr": "Dilediğini yapan ve yaptıran.",
    "El-Mütekebbir": "Büyüklükte eşi olmayan.", "El-Hâlık": "Yoktan var eden, yaratan.",
    "El-Bâri": "Her şeyi kusursuz yaratan.", "El-Musavvir": "Varlıklara suret veren."
}

son_on_sure = {
    "Fil Suresi": {"oku": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl...", "meal": "Rabbinin, fil sahiplerine ne yaptığını görmedin mi?"},
    "Kureyş Suresi": {"oku": "Li îlâfi kureyş...", "meal": "Kureyş'e kolaylaştırıldığı için..."},
    "Mâûn Suresi": {"oku": "Era'eytellezî yükezzibü bid dîn...", "meal": "Dini yalanlayanı gördün mü?"},
    "Kevser Suresi": {"oku": "İnnâ a'taynâkel kevser...", "meal": "Şüphesiz biz sana Kevser'i verdik."},
    "Kâfirûn Suresi": {"oku": "Kul yâ eyyühel kâfirûn...", "meal": "De ki: Ey kafirler! Ben sizin taptıklarınıza tapmam."},
    "Nasr Suresi": {"oku": "İzâ câe nasrullâhi vel feth...", "meal": "Allah'ın yardımı ve fetih geldiğinde..."},
    "Tebbet Suresi": {"oku": "Tebbet yedâ ebî lehebin ve tebb...", "meal": "Ebu Leheb'in iki eli kurusun!"},
    "İhlâs Suresi": {"oku": "Kul hüvallâhü ehad...", "meal": "De ki: O Allah birdir."},
    "Felak Suresi": {"oku": "Kul e'ûzü bi rabbil felak...", "meal": "De ki: Sabahın Rabbine sığınırım."},
    "Nâs Suresi": {"oku": "Kul e'ûzü bi rabbin nâs...", "meal": "De ki: İnsanların Rabbine sığınırım."}
}

sehirler_81 = ["Adana", "Adiyaman", "Afyonkarahisar", "Agri", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydin", "Balikesir", "Bartin", "Batman", "Bayburt", "Bilecik", "Bingol", "Bitlis", "Bolu", "Burdur", "Bursa", "Canakkale", "Cankiri", "Corum", "Denizli", "Diyarbakir", "Duzce", "Edirne", "Elazig", "Erzincan", "Erzurum", "Eskisehir", "Gaziantep", "Giresun", "Gumushane", "Hakkari", "Hatay", "Igdir", "Isparta", "Istanbul", "Izmir", "Kahramanmaras", "Karabuk", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kilis", "Kirikkale", "Kirklareli", "Kirsehir", "Kocaeli", "Konya", "Kutahya", "Malatya", "Manisa", "Mardin", "Mersin", "Mugla", "Mus", "Nevsehir", "Nigde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Sanliurfa", "Siirt", "Sinop", "Sivas", "Sirnak", "Tekirdag", "Tokat", "Trabzon", "Tunceli", "Usak", "Van", "Yalova", "Yozgat", "Zonguldak"]

# --- 3. CSS (TASARIM GÜNCELLEMESİ) ---
st.markdown("""
    <style>
    .stApp { background-color: #040807; color: white; }
    .besmele { text-align: center; color: #d4af37; font-size: 3.5rem; font-family: 'Times New Roman', serif; margin: 15px 0; font-weight: bold; }
    .ayet-hadis-box { text-align: center; color: #f1f1f1; background: rgba(212,175,55,0.1); border-left: 5px solid #d4af37; padding: 20px; border-radius: 10px; margin-bottom: 25px; }
    .vakit-kart { background: #ffffff; border-radius: 15px; padding: 18px; text-align: center; border-bottom: 8px solid #d4af37; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .vakit-ad { color: #1a1a1a !important; font-size: 1.6rem; font-weight: bold; }
    .vakit-saat { color: #d4af37 !important; font-size: 2.8rem; font-weight: 900; }
    .takvim-banner { text-align: center; font-size: 1.8rem; color: #fbbf24; font-weight: bold; padding: 10px; border-top: 1px solid #333; }
    .zikir-bolumu { background: linear-gradient(145deg, #111, #222); border: 3px solid #d4af37; border-radius: 40px; padding: 50px; text-align: center; margin-top: 40px; }
    .zikir-sayi { color: #ffffff !important; font-size: 9rem !important; font-weight: 900; line-height: 1; margin: 30px 0; text-shadow: 0 0 20px #d4af37; }
    .pusula-box { background: #000; border: 4px dashed #d4af37; border-radius: 50%; width: 180px; height: 180px; margin: 0 auto; display: flex; align-items: center; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (İÇERİK) ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center;'>🕋 PORTAL</h1>", unsafe_allow_html=True)
    sehir = st.selectbox("📍 Şehir Seçin", sehirler_81, index=sehirler_81.index("Istanbul"))
    
    with st.expander("📖 SON 10 SURE", expanded=False):
        for s_ad, s_ic in son_on_sure.items():
            st.markdown(f"**{s_ad}**")
            st.caption(f"Okunuş: {s_ic['oku']}")
            st.write(f"Meal: {s_ic['meal']}")
            st.divider()

    with st.expander("✨ ESMAÜL HÜSNA", expanded=False):
        for isim, anlam in esma_full.items():
            st.write(f"**{isim}**: {anlam}")

    st.info("Kıble Yönü ve Haftalık Çizelge ana ekrandadır.")

# --- 5. ANA EKRAN ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)

# Ayet ve Hadis Bölümü
c_a1, c_a2 = st.columns(2)
with c_a1:
    st.markdown(f"<div class='ayet-hadis-box'><b>Günün Ayeti (Ali İmran 110):</b><br>Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz...</div>", unsafe_allow_html=True)
with c_a2:
    st.markdown(f"<div class='ayet-hadis-box'><b>Günün Hadisi:</b><br>{gunun_hadisi}</div>", unsafe_allow_html=True)

# Veri Çekme
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    t_m = res['date']['gregorian']
    t_h = res['date']['hijri']

    # Takvim Banner
    st.markdown(f"<div class='takvim-banner'>📅 {t_m['day']} {t_m['month']['en']} {t_m['year']} | 🌙 {t_h['day']} {t_h['month']['ar']} {t_h['year']}</div>", unsafe_allow_html=True)

    # 3 ÜSTTE VAKİTLER
    row1 = st.columns(3)
    v_ust = [("İMSAK", v['Fajr']), ("GÜNEŞ", v['Sunrise']), ("ÖĞLE", v['Dhuhr'])]
    for i, (ad, saat) in enumerate(v_ust):
        row1[i].markdown(f"<div class='vakit-kart'><div class='vakit-ad'>{ad}</div><div class='vakit-saat'>{saat}</div></div>", unsafe_allow_html=True)

    # 3 ALTTA VAKİTLER
    row2 = st.columns(3)
    v_alt = [("İKİNDİ", v['Asr']), ("AKŞAM", v['Maghrib']), ("YATSI", v['Isha'])]
    for i, (ad, saat) in enumerate(v_alt):
        row2[i].markdown(f"<div class='vakit-kart'><div class='vakit-ad'>{ad}</div><div class='vakit-saat'>{saat}</div></div>", unsafe_allow_html=True)

    # --- KIBLE VE HAFTALIK ---
    st.divider()
    col_k1, col_k2 = st.columns([1, 2])
    
    with col_k1:
        st.subheader("🧭 Kıble Pusulası")
        # Statik ama şık bir pusula tasarımı
        st.markdown(f"""
        <div class='pusula-box'>
            <div style='font-size:50px; transform: rotate(0deg);'>🕋</div>
        </div>
        <p style='text-align:center; margin-top:10px;'>{sehir} için Kıble Yönü</p>
        """, unsafe_allow_html=True)
    
    with col_k2:
        st.subheader("🗓️ Haftalık Takvim")
        h_res = requests.get(f"http://api.aladhan.com/v1/calendarByCity?city={sehir}&country=Turkey&method=13").json()['data']
        today = datetime.now().day
        tablo = [[d['date']['gregorian']['date'], d['timings']['Fajr'], d['timings']['Dhuhr'], d['timings']['Asr'], d['timings']['Maghrib'], d['timings']['Isha']] for d in h_res if int(d['date']['gregorian']['day']) >= today][:7]
        st.table(tablo)

    # --- ZİKİRMATİK (EN BÜYÜK HALİYLE) ---
    st.markdown("<div class='zikir-bolumu'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#d4af37; letter-spacing: 5px;'>📿 ZİKİRMATİK</h2>", unsafe_allow_html=True)
    
    if 'zikir_count' not in st.session_state: st.session_state.zikir_count = 0
    
    st.markdown(f"<div class='zikir-sayi'>{st.session_state.zikir_count}</div>", unsafe_allow_html=True)
    
    z_c1, z_c2 = st.columns(2)
    if z_c1.button("✨ ZİKİR ÇEK (TİTREŞİMLİ)", use_container_width=True, help="Zikri artırır ve titreşim verir"):
        st.session_state.zikir_count += 1
        st.components.v1.html("<script>window.navigator.vibrate(70);</script>", height=0)
        st.rerun()
    if z_c2.button("🔄 SIFIRLA", use_container_width=True):
        st.session_state.zikir_count = 0
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error("Bir hata oluştu. Lütfen bağlantınızı kontrol edin.")

# Sayfayı canlı tutmak için gizli yenileme
st.empty()