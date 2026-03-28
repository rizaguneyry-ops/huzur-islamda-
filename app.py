import streamlit as st
import requests
from datetime import datetime, timedelta
import time
import random
import pandas as pd

# Kütüphane Kontrolü (Hata almamak için önlem)
try:
    import plotly.express as px
except ImportError:
    st.error("Sistemde 'plotly' kütüphanesi eksik. Lütfen requirements.txt dosyasını kontrol edin.")

# --- 1. TASARIM VE ATMOSFER ---
st.set_page_config(page_title="Manevi Yol Arkadaşı v170", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Cinzel:wght@700&family=Montserrat:wght@300;600&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1519817650390-84a93dbad994?q=80&w=2000");
        background-size: cover; background-attachment: fixed; color: #fdf5e6;
        font-family: 'Montserrat', sans-serif;
    }
    .main-header { font-family: 'Cinzel', serif; text-align: center; font-size: 3.5rem; color: #d4af37; text-shadow: 0 0 20px #d4af37; }
    .quote-card { background: rgba(212, 175, 55, 0.1); border-left: 5px solid #d4af37; padding: 25px; border-radius: 12px; margin: 20px 0; font-size: 1.2rem; }
    .yuvarlak-sayac { 
        width: 380px; height: 380px; border-radius: 50%; border: 12px double #d4af37; 
        margin: 30px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: radial-gradient(circle, #222 0%, #000 100%);
        box-shadow: 0 0 100px rgba(212,175,55,0.4);
    }
    .vakit-kart { background: #fff; color: #000; border-radius: 15px; padding: 15px; text-align: center; border-bottom: 8px solid #d4af37; font-weight: bold; }
    .vakit-saat { font-size: 1.8rem; color: #b8860b; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ MERKEZİ (TAM LİSTELER) ---
ESMALAR = {
    "Allah": "Eşi benzeri olmayan", "Er-Rahmân": "Dünyada her canlıya merhamet eden", "Er-Rahîm": "Ahirette müminlere rahmet eden",
    "El-Melik": "Mülkün sahibi", "El-Kuddûs": "Eksiklikten uzak", "Es-Selâm": "Esenlik veren", "El-Mü'min": "Güven veren",
    "El-Müheymin": "Gözeten", "El-Azîz": "İzzet sahibi", "El-Cebbâr": "Dilediğini yapan", "El-Mütekebbir": "Büyük",
    "El-Hâlık": "Yaratan", "El-Bâri": "Kusursuz yaratan", "El-Musavvir": "Şekil veren", "El-Gaffâr": "Affı bol",
    "El-Kahhâr": "Galip", "El-Vehhâb": "Veren", "Er-Razzâk": "Rızık veren", "El-Fettâh": "Kapı açan", "El-Alîm": "Bilen",
    "El-Kâbıd": "Sıkan", "El-Bâsıt": "Açan", "El-Hâfıd": "Alçaltan", "Er-Râfi": "Yükselten", "El-Muiz": "Aziz kılan",
    "El-Müzil": "Zelil kılan", "Es-Semî": "İşiten", "El-Basîr": "Gören", "El-Hakem": "Hükmeden", "El-Adl": "Adaletli",
    "El-Latîf": "Lütfeden", "El-Habîr": "Haberdar", "El-Halîm": "Yumuşak", "El-Azîm": "Yüce", "El-Gafûr": "Affeden",
    "Eş-Şekûr": "Mükafat veren", "El-Aliyy": "Yüce", "El-Kebîr": "Büyük", "El-Hafîz": "Koruyan", "El-Mukît": "Besleyen",
    "El-Hasîb": "Hesap soran", "El-Celîl": "Azametli", "El-Kerîm": "Cömert", "Er-Rakîb": "Gözetleyen", "El-Mucîb": "Kabul eden",
    "El-Vâsi": "İlmi geniş", "El-Hakîm": "Hikmetli", "El-Vedûd": "Seven", "El-Mecîd": "Şanlı", "El-Bâis": "Dirilten",
    "Eş-Şekûr": "Mükafat veren", "El-Aliyy": "Yüce", "El-Kebîr": "Büyük", "El-Hafîz": "Koruyan", "El-Mukît": "Besleyen",
    "El-Hasîb": "Hesap soran", "El-Celîl": "Azametli", "El-Kerîm": "Cömert", "Er-Rakîb": "Gözetleyen", "El-Mucîb": "Kabul eden",
    "El-Vâsi": "İlmi geniş", "El-Hakîm": "Hikmetli", "El-Vedûd": "Seven", "El-Mecîd": "Şanlı", "El-Bâis": "Dirilten",
    "Eş-Şehîd": "Şahit", "El-Hakk": "Gerçek", "El-Vekîl": "Güvenilen", "El-Kaviyy": "Güçlü", "El-Metîn": "Sarsılmaz",
    "El-Veliyy": "Dost", "El-Hamîd": "Övülen", "El-Muhsî": "Sayan", "El-Mübdî": "Başlatan", "El-Muîd": "Döndüren",
    "El-Muhyî": "Can veren", "El-Mümît": "Öldüren", "El-Hayy": "Diri", "El-Kayyûm": "Ayakta tutan", "El-Vâcid": "Bulan",
    "El-Mâcid": "Kadri yüce", "El-Vâhid": "Tek", "Es-Samed": "Muhtaç olmayan", "El-Kâdir": "Gücü yeten", "El-Muktedir": "Kuvvetli",
    "El-Muakdim": "Öne alan", "El-Muahhir": "Geriye atan", "El-Evvel": "İlk", "El-Âhir": "Son", "Ez-Zâhir": "Açık",
    "El-Bâtın": "Gizli", "El-Vâlî": "Yöneten", "El-Müteâlî": "Yüce", "El-Berr": "İyiliği bol", "Et-Tevvâb": "Tövbe kabul eden",
    "El-Müntakim": "İntikam alan", "El-Afüvv": "Affeden", "Er-Raûf": "Şefkatli", "Mâlikü’l-Mülk": "Mülk sahibi",
    "Zü’l-Celâli ve’l-İkrâm": "Celal ve ikram sahibi", "El-Muksit": "Adil", "El-Câmi": "Toplayan", "El-Ganî": "Zengin",
    "El-Mugnî": "Zengin eden", "El-Mâni": "Engelleyen", "Ed-Dârr": "Zarar veren", "En-Nâfi": "Fayda veren", "En-Nûr": "Nur",
    "El-Hâdî": "Hidayet veren", "El-Bedî": "Eşsiz", "El-Bâkî": "Ebedi", "El-Vâris": "Varis", "Er-Reşîd": "Yol gösteren", "Es-Sabûr": "Sabırlı"
}

SURELER = {
    "Fil": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bi hicâratin min siccîl. Fe ce'alehüm ke'asfin me'kûl.",
    "Kureyş": "Li îlâfi kureyş. Îlâfihim rihlete'ş-şitâi ve's-sayf. Fel ya'büdû rabbe hâze'l-beyt. Ellezî at'amehüm min cû'in ve âmenehüm min havf.",
    "Maun": "Era'eytellezî yükezzibü bi'd-dîn. Fe-zâlikellezî yedü''ul-yetîm. Ve lâ yehuddu alâ ta'âmil miskîn. Fe-veylün lil-müsallîn. Ellezîn hüm an salâtihim sâhûn. Ellezîn hüm yürâûn. Ve yemne'ûne'l-mâ'ûn.",
    "Kevser": "İnnâ a'taynâke'l-kevser. Fe-salli li-rabbike venhar. İnne şânieke hüve'l-ebter.",
    "Kafirun": "Kul yâ eyyühe'l-kâfirûn. Lâ a'büdü mâ ta'büdûn. Ve lâ entüm âbidûne mâ a'büd. Ve lâ ene âbidün mâ abedtüm. Ve entüm âbidûne mâ a'büd. Leküm dînüküm veliye dîn.",
    "Nasr": "İzâ câe nasrullâhi ve'l-feth. Ve raeyte'n-nâse yedhulûne fî dînillâhi efvâcâ. Fe sebbih bi-hamdi rabbike vestağfirhü innehû kâne tevvâbâ.",
    "Tebbet": "Tebbet yedâ ebî lehebin ve tebb. Mâ ağnâ anhü mâlühû ve mâ keseb. Seyaslâ nâran zâte leheb. Vemraetühû hammâlete'l-hatab. Fî cîdihâ hablün min mesed.",
    "İhlas": "Kul hüvallâhü ehad. Allâhü's-samed. Lem yelid ve len yûled. Ve len yekün lehû küfüven ehad.",
    "Felak": "Kul eûzü bi-rabbi'l-felak. Min şerri mâ halak. Ve min şerri ğâsikın izâ vekab. Ve min şerri'n-neffâsâti fî'l-ukad. Ve min şerri hâsidin izâ hased.",
    "Nas": "Kul eûzü bi-rabbi'n-nâs. Meliki'n-nâs. İlâhi'n-nâs. Min şerri'l-vesvâsi'l-hannâs. Ellezî yüvesvisü fî sudûri'n-nâs. Mine'l-cinneti ven-nâs."
}

MOTIVASYON_LISTE = [
    "✨ 'Kalk, silkelen, kendine gel. Umutsuzluk şeytandandır. Ümit etmek Allah'tandır.'",
    "✨ 'Dünya bir misafirhanedir, kalıcı olana yatırım yap.'",
    "✨ 'Sen Allah'ın rızasını gözet, O senin işlerini rast getirir.'",
    "✨ 'Namaz, müminin miracıdır.'",
    "✨ 'Sabret, zira Allah sabredenlerle beraberdir.'",
    "✨ 'Allah bir kapıyı kaparsa, bin kapıyı açar.'"
]

# --- 3. AKILLI HAFIZA ---
if 'exp' not in st.session_state: st.session_state.exp = 0
if 'namaz_skorlari' not in st.session_state:
    st.session_state.namaz_skorlari = [5, 4, 5, 4, 5, 3, 5] # Örnek Pzt-Paz verisi

# --- 4. FONKSİYONLAR ---
def vakit_duzelt(s, d=-1):
    h, m = map(int, s.split(':'))
    return (datetime(2000,1,1,h,m) + timedelta(minutes=d)).strftime("%H:%M")

@st.cache_data(ttl=3600)
def api_verisi_al(city):
    try:
        r = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Turkey&method=13")
        return r.json()['data']
    except: return None

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#d4af37; text-align:center;'>Manevi Panel</h1>", unsafe_allow_html=True)
    lvl = st.session_state.exp // 100
    st.markdown(f"<div style='text-align:center; font-size:1.4rem;'>⭐ Seviye {lvl}</div>", unsafe_allow_html=True)
    st.progress(min((st.session_state.exp % 100) / 100, 1.0))
    
    sehir = st.selectbox("📍 Şehriniz", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Adana", "Konya"])
    
    if st.button("📿 Zikirmatik (+10 EXP)"):
        st.session_state.exp += 10; st.balloons(); st.rerun()
    
    with st.expander("📖 99 Esmaül Hüsna"):
        for k, v in ESMALAR.items(): st.write(f"**{k}:** {v}")
    with st.expander("📖 10 Sure ve Meali"):
        for k, v in SURELER.items(): st.write(f"**{k}:** {v}")

# --- 6. ANA EKRAN ---
data = api_verisi_al(sehir)
tr_now = datetime.utcnow() + timedelta(hours=3)

if data:
    st.markdown("<h1 class='main-header'>MANEVİ YOL ARKADAŞI</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='quote-card'>{random.choice(MOTIVASYON_LISTE)}</div>", unsafe_allow_html=True)

    # 1 Dakika Geri Çekilmiş Vakitler
    v_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    v_lbls = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
    v_times = [vakit_duzelt(data['timings'][k]) for k in v_keys]

    cols = st.columns(6)
    for i, (l, t) in enumerate(zip(v_lbls, v_times)):
        cols[i].markdown(f"<div class='vakit-kart'>{l}<br><span class='vakit-saat'>{t}</span></div>", unsafe_allow_html=True)

    # --- HAFTALIK RAPOR ---
    with st.expander("📊 Haftalık Namaz İstikrar Grafiğim"):
        gunler = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
        df = pd.DataFrame({'Gün': gunler, 'Kılınan': st.session_state.namaz_skorlari})
        try:
            fig = px.line(df, x='Gün', y='Kılınan', markers=True, title="Haftalık Performans", color_discrete_sequence=['#d4af37'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Grafik şu an oluşturulamıyor, ama verileriniz kayıt altında.")

    # --- NAMAZ TAKİBİ (30-90 DK SONRA) ---
    for i, t_str in enumerate(v_times):
        h, m = map(int, t_str.split(':'))
        v_dt = tr_now.replace(hour=h, minute=m, second=0)
        if v_dt + timedelta(minutes=30) < tr_now < v_dt + timedelta(minutes=90):
            st.markdown(f"### 🛡️ {v_lbls[i]} Namazını Kıldınız mı?")
            c1, c2 = st.columns(2)
            if c1.button("✅ Elhamdülillah Kıldım"):
                st.session_state.exp += 50
                # Bugünün skorunu güncelle
                gun_idx = tr_now.weekday()
                st.session_state.namaz_skorlari[gun_idx] = min(5, st.session_state.namaz_skorlari[gun_idx] + 1)
                st.balloons(); st.success("Nurunuz artsın!"); time.sleep(2); st.rerun()
            if c2.button("❌ Henüz Değil"):
                st.warning("Allah nasip etsin, acele et!"); time.sleep(2); st.rerun()

    # --- CANLI SAYAÇ & EZAN ---
    counter_placeholder = st.empty()
    while True:
        curr = datetime.utcnow() + timedelta(hours=3)
        target, idx = None, 0
        for i, t in enumerate(v_times):
            vo = curr.replace(hour=int(t.split(':')[0]), minute=int(t.split(':')[1]), second=0)
            if vo > curr: target, idx = vo, i; break
        
        if not target:
            target = (curr + timedelta(days=1)).replace(hour=int(v_times[0].split(':')[0]), minute=int(v_times[0].split(':')[1]), second=0)
            idx = 0

        diff = int((target - curr).total_seconds())
        if diff <= 0:
            st.markdown('<audio autoplay><source src="https://www.islamcan.com/audio/adhan/azan1.mp3"></audio>', unsafe_allow_html=True)
            time.sleep(5); st.rerun()

        h, m, s = diff // 3600, (diff % 3600) // 60, diff % 60
        motive_msg = "Abdest alıp huzura hazırlan..." if diff < 600 else "Kalbin her an Allah ile olsun."
        
        counter_placeholder.markdown(f"""<div class='yuvarlak-sayac'>
            <div style='color:#d4af37; font-size:1.3rem; letter-spacing:2px;'>{v_lbls[idx].upper()} VAKTİNE</div>
            <div style='font-size:5.5rem; font-weight:bold;'>{h:02d}:{m:02d}:{s:02d}</div>
            <div style='color:#00e676; font-size:1rem; margin-top:10px;'>{motive_msg}</div>
        </div>""", unsafe_allow_html=True)
        time.sleep(1)