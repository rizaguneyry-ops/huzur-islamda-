import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# --- 1. AYARLAR VE TASARIM ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2070&auto=format&fit=crop");
        background-size: cover; background-attachment: fixed; color: white;
    }
    .besmele { text-align: center; font-size: 2.2rem; font-weight: bold; color: #fbc02d; margin-bottom: 5px; }
    .ayet-kart { background: rgba(251, 192, 45, 0.15); border: 2px solid #fbc02d; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 25px; }
    .yuvarlak-sayac { 
        width: 280px; height: 280px; border-radius: 50%; border: 10px solid #fbc02d; 
        margin: 20px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: rgba(0,0,0,0.95); box-shadow: 0 0 50px #fbc02d;
    }
    .vakit-kart { background: white; color: black; border-radius: 12px; padding: 15px; text-align: center; border-bottom: 6px solid #fbc02d; font-weight: bold; }
    .vakit-saat { font-size: 1.8rem; font-weight: 900; color: #d4af37; }
    .ana-takvim { width: 100%; border-collapse: collapse; margin-top: 30px; background: rgba(255,255,255,0.1); color: white; border-radius: 10px; overflow: hidden; border: 1px solid #fbc02d; }
    .ana-takvim th { background: #fbc02d; color: black; padding: 15px; font-size: 1.1rem; }
    .ana-takvim td { padding: 12px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.2); font-size: 1rem; }
    .bugun-satir { background: rgba(251, 192, 45, 0.3); font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 10 SURE VE 99 ESMA (EKSİKSİZ) ---
SURELER = {
    "Fil": {"o": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl...", "m": "Rabbinin fil sahiplerine ne yaptığını görmedin mi?"},
    "Kureyş": {"o": "Li îlâfi kureyş...", "m": "Kureyş'i alıştırmak için..."},
    "Maun": {"o": "Era'eytellezî yükezzibü bi'd-dîn...", "m": "Dini yalanlayanı gördün mü?"},
    "Kevser": {"o": "İnnâ a'taynâke'l-kevser...", "m": "Şüphesiz biz sana Kevser'i verdik."},
    "Kafirun": {"o": "Kul yâ eyyühe'l-kâfirûn...", "m": "De ki: Ey inkarcılar!"},
    "Nasr": {"o": "İzâ câe nasrullâhi ve'l-feth...", "m": "Allah'ın yardımı ve fetih geldiğinde..."},
    "Tebbet": {"o": "Tebbet yedâ ebî lehebin ve tebb...", "m": "Ebu Leheb'in elleri kurusun!"},
    "İhlas": {"o": "Kul hüvallâhü ehad...", "m": "De ki: O Allah tektir."},
    "Felak": {"o": "Kul eûzü bi-rabbi'l-felak...", "m": "De ki: Sabahın Rabbine sığınırım."},
    "Nas": {"o": "Kul eûzü bi-rabbi'n-nâs...", "m": "De ki: İnsanların Rabbine sığınırım."}
}

# 99 Esmaül Hüsna ve Anlamları
ESMA_99 = {
    "Allah": "Eşi benzeri olmayan", "Er-Rahmân": "Dünyada her canlıya merhamet eden", "Er-Rahîm": "Ahirette müminlere rahmet eden",
    "El-Melik": "Mülkün sahibi", "El-Kuddûs": "Eksiklikten uzak", "Es-Selâm": "Esenlik veren", "El-Mü'min": "Güven veren",
    "El-Müheymin": "Gözeten", "El-Azîz": "İzzet sahibi", "El-Cebbâr": "Dilediğini yapan", "El-Mütekebbir": "Büyük",
    "El-Hâlık": "Yaratan", "El-Bâri": "Kusursuz yaratan", "El-Musavvir": "Şekil veren", "El-Gaffâr": "Affı bol",
    "El-Kahhâr": "Galip", "El-Vehhâb": "Veren", "Er-Razzâk": "Rızık veren", "El-Fettâh": "Kapı açan",
    "El-Alîm": "Bilen", "El-Kâbıd": "Sıkan", "El-Bâsıt": "Açan", "El-Hâfıd": "Alçaltan", "Er-Râfi": "Yükselten",
    "El-Muiz": "Aziz kılan", "El-Müzil": "Zelil kılan", "Es-Semî": "İşiten", "El-Basîr": "Gören", "El-Hakem": "Hükmeden",
    "El-Adl": "Adaletli", "El-Latîf": "Lütfeden", "El-Habîr": "Haberdar", "El-Halîm": "Yumuşak", "El-Azîm": "Yüce",
    "El-Gafûr": "Affeden", "Eş-Şekûr": "Mükafat veren", "El-Aliyy": "Yüce", "El-Kebîr": "Büyük", "El-Hafîz": "Koruyan",
    "El-Mukît": "Besleyen", "El-Hasîb": "Hesap soran", "El-Celîl": "Azametli", "El-Kerîm": "Cömert", "Er-Rakîb": "Gözetleyen",
    "El-Mucîb": "Kabul eden", "El-Vâsi": "İlmi geniş", "El-Hakîm": "Hikmetli", "El-Vedûd": "Seven", "El-Mecîd": "Şanlı",
    "El-Bâis": "Dirilten", "Eş-Şehîd": "Şahit", "El-Hakk": "Gerçek", "El-Vekîl": "Güvenilen", "El-Kaviyy": "Güçlü",
    "El-Metîn": "Sarsılmaz", "El-Veliyy": "Dost", "El-Hamîd": "Övülen", "El-Muhsî": "Sayan", "El-Mübdî": "Başlatan",
    "El-Muîd": "Döndüren", "El-Muhyî": "Can veren", "El-Mümît": "Öldüren", "El-Hayy": "Diri", "El-Kayyûm": "Ayakta tutan",
    "El-Vâcid": "Bulan", "El-Mâcid": "Kadri yüce", "El-Vâhid": "Tek", "Es-Samed": "Muhtaç olmayan", "El-Kâdir": "Gücü yeten",
    "El-Muktedir": "Kuvvetli", "El-Muakdim": "Öne alan", "El-Muahhir": "Geriye atan", "El-Evvel": "İlk", "El-Âhir": "Son",
    "Ez-Zâhir": "Açık", "El-Bâtın": "Gizli", "El-Vâlî": "Yöneten", "El-Müteâlî": "Yüce", "El-Berr": "İyiliği bol",
    "Et-Tevvâb": "Tövbe kabul eden", "El-Müntakim": "Cezalandıran", "El-Afüvv": "Affeden", "Er-Raûf": "Şefkatli",
    "Mâlikü’l-Mülk": "Mülk sahibi", "Zü’l-Celâli ve’l-İkrâm": "Celal sahibi", "El-Muksit": "Adil", "El-Câmi": "Toplayan",
    "El-Ganî": "Zengin", "El-Mugnî": "Zengin eden", "El-Mâni": "Engelleyen", "Ed-Dârr": "Zarar veren", "En-Nâfi": "Fayda veren",
    "En-Nûr": "Nur", "El-Hâdî": "Hidayet veren", "El-Bedî": "Eşsiz", "El-Bâkî": "Ebedi", "El-Vâris": "Varis",
    "Er-Reşîd": "Yol gösteren", "Es-Sabûr": "Sabırlı"
}

VAKIT_ADLARI = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]

# --- 3. FONKSİYONLAR ---
@st.cache_data(ttl=3600)
def veri_getir(sehir, tarih):
    url = f"http://api.aladhan.com/v1/calendarByCity?city={sehir}&country=Turkey&method=13&month={tarih.month}&year={tarih.year}"
    try:
        return requests.get(url).json().get('data', [])
    except: return []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("🕋 MENÜ")
    sehir = st.selectbox("📍 Şehir Seçiniz", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana", "Gaziantep"])
    
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.subheader(f"📿 Zikirmatik: {st.session_state.zk}")
    c1, c2 = st.columns(2)
    if c1.button("➕ Artır"): st.session_state.zk += 1; st.rerun()
    if c2.button("🔄 Sıfırla"): st.session_state.zk = 0; st.rerun()

    with st.expander("📖 10 Sure"):
        for k, v in SURELER.items():
            st.write(f"**{k} Suresi**"); st.info(v['m'])

    with st.expander("✨ 99 Esmaül Hüsna"):
        for k, v in ESMA_99.items():
            st.write(f"**{k}:** {v}")

# --- 5. ANA EKRAN ---
# TÜRKİYE SAATİ SABİTLEME (UTC+3)
tr_simdi = datetime.utcnow() + timedelta(hours=3)
data = veri_getir(sehir, tr_simdi)
if tr_simdi.day > 25: data += veri_getir(sehir, tr_simdi.replace(day=28) + timedelta(days=5))

bugun_g = next((g for g in data if g['date']['gregorian']['date'] == tr_simdi.strftime("%d-%m-%Y")), None)

if bugun_g:
    v_vakitler = [bugun_g['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
    
    st.markdown(f"<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
    
    # Âli İmrân 110 (Düzeltildi)
    st.markdown("""
        <div class='ayet-kart'>
            <div style='font-size: 1.6rem; color: #fbc02d; font-family: "serif";'>كُنْتُمْ خَيْرَ اُمَّةٍ اُخْرِجَتْ لِلنَّاسِ تَأْمُرُونَ بِالْمَعْرُوفِ وَتَنْهَوْنَ عَنِ الْمُنْكَرِ وَتُؤْمِنُونَ بِاللّٰهِۜ</div>
            <div style='font-size: 1.1rem; margin-top:15px;'><b>Âli İmrân 110:</b> Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah'a inanırsınız.</div>
        </div>
    """, unsafe_allow_html=True)

    sayac_ekrani = st.empty()
    
    cols = st.columns(6)
    for i, (ad, saat) in enumerate(zip(VAKIT_ADLARI, v_vakitler)):
        cols[i].markdown(f"<div class='vakit-kart'>{ad}<br><span class='vakit-saat'>{saat}</span></div>", unsafe_allow_html=True)

    # ANA EKRAN TÜRKÇE TAKVİM (HİÇBİR ŞEYİ BOZMADAN)
    st.markdown("<br><h3 style='text-align:center; color:#fbc02d;'>🗓️ 7 Günlük Namaz Vakitleri</h3>", unsafe_allow_html=True)
    
    idx = data.index(bugun_g)
    takvim_html = "<table class='ana-takvim'><tr><th>Tarih</th><th>İmsak</th><th>Güneş</th><th>Öğle</th><th>İkindi</th><th>Akşam</th><th>Yatsı</th></tr>"
    
    for g in data[idx:idx+7]:
        tarih_str = g['date']['gregorian']['date']
        is_today = "class='bugun-satir'" if tarih_str == tr_simdi.strftime("%d-%m-%Y") else ""
        v_l = [g['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
        
        takvim_html += f"<tr {is_today}><td>{tarih_str}</td>" + "".join([f"<td>{x}</td>" for x in v_l]) + "</tr>"
    
    st.markdown(takvim_html + "</table>", unsafe_allow_html=True)

    # --- KESİN GERİ SAYIM DÖNGÜSÜ ---
    while True:
        an = datetime.utcnow() + timedelta(hours=3) # Türkiye saati saniyelik güncelleme
        hedef_v, h_idx = None, 0
        
        for i, vt in enumerate(v_vakitler):
            h, m = map(int, vt.split(":"))
            v_obj = an.replace(hour=h, minute=m, second=0, microsecond=0)
            if v_obj > an:
                hedef_v, h_idx = v_obj, i
                break
        
        if not hedef_v:
            y_i = data[data.index(bugun_g)+1]['timings']['Fajr'].split(" ")[0]
            h_y, m_y = map(int, y_i.split(":"))
            hedef_v = (an + timedelta(days=1)).replace(hour=h_y, minute=m_y, second=0)
            h_idx = 0

        fark = int((hedef_v - an).total_seconds())
        h_k, m_k, s_k = fark // 3600, (fark % 3600) // 60, fark % 60
        
        sayac_ekrani.markdown(f"""
            <div class='yuvarlak-sayac'>
                <div style='font-size:1.1rem; color:#fbc02d;'>{VAKIT_ADLARI[h_idx].upper()} VAKTİNE KALAN</div>
                <div style='font-size:4rem; font-weight:bold;'>{h_k:02d}:{m_k:02d}:{s_k:02d}</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)