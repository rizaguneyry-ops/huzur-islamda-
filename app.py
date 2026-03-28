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
    .ana-takvim { width: 100%; border-collapse: collapse; margin-top: 30px; background: rgba(0,0,0,0.8); color: white; border-radius: 10px; overflow: hidden; border: 2px solid #fbc02d; }
    .ana-takvim th { background: #fbc02d; color: black; padding: 15px; font-size: 1.1rem; }
    .ana-takvim td { padding: 12px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.2); font-size: 1rem; }
    .bugun-satir { background: rgba(251, 192, 45, 0.4) !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 10 SURE (TAM METİN - HİÇBİR EKSİK YOK) ---
SURE_VERILERI = {
    "Fil": {
        "okunus": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bi hicâratin min siccîl. Fe ce'alehüm ke'asfin me'kûl.",
        "meal": "Rabbinin fil sahiplerine ne yaptığını görmedin mi? Onların tuzaklarını boşa çıkarmadı mı? Üzerlerine sürü sürü kuşlar gönderdi. Onlara çamurdan sertleşmiş taşlar atan kuşlar... Sonunda onları yenilmiş ekin yaprağı gibi yaptı."
    },
    "Kureyş": {
        "okunus": "Li îlâfi kureyş. Îlâfihim rihlete'ş-şitâi ve's-sayf. Fel ya'büdû rabbe hâze'l-beyt. Ellezî at'amehüm min cû'in ve âmenehüm min havf.",
        "meal": "Kureyş'i alıştırmak için; kış ve yaz yolculuğuna... Bu evin Rabbine kulluk etsinler. O ki onları doyurdu ve korkudan emin kıldı."
    },
    "Maun": {
        "okunus": "Era'eytellezî yükezzibü bi'd-dîn. Fe-zâlikellezî yedü''ul-yetîm. Ve lâ yehuddu alâ ta'âmil miskîn. Fe-veylün lil-müsallîn. Ellezîn hüm an salâtihim sâhûn. Ellezîn hüm yürâûn. Ve yemne'ûne'l-mâ'ûn.",
        "meal": "Dini yalanlayanı gördün mü? Yetimi itip kalkan odur. Yoksulu doyurmaya teşvik etmez. Yazıklar olsun o namaz kılanlara ki ciddiye almazlar. Gösteriş yaparlar ve yardıma engel olurlar."
    },
    "Kevser": {
        "okunus": "İnnâ a'taynâke'l-kevser. Fe-salli li-rabbike venhar. İnne şânieke hüve'l-ebter.",
        "meal": "Şüphesiz biz sana Kevser'i verdik. Rabbin için namaz kıl, kurban kes. Asıl sonu kesik olan sana buğzedendir."
    },
    "Kafirun": {
        "okunus": "Kul yâ eyyühe'l-kâfirûn. Lâ a'büdü mâ ta'büdûn. Ve lâ entüm âbidûne mâ a'büd. Ve lâ ene âbidün mâ abedtüm. Ve entüm âbidûne mâ a'büd. Leküm dînüküm veliye dîn.",
        "meal": "De ki: Ey inkarcılar! Ben sizin taptığınıza tapmam. Siz de benim taptığıma tapmazsınız. Sizin dininiz size, benimki banadır."
    },
    "Nasr": {
        "okunus": "İzâ câe nasrullâhi ve'l-feth. Ve raeyte'n-nâse yedhulûne fî dînillâhi efvâcâ. Fe sebbih bi-hamdi rabbike vestağfirhü innehû kâne tevvâbâ.",
        "meal": "Allah'ın yardımı ve fetih geldiğinde, insanların dalga dalga dine girdiğini gördüğünde Rabbini hamd ile tesbih et, bağışlanma dile. Şüphesiz O, tövbeleri çok kabul edendir."
    },
    "Tebbet": {
        "okunus": "Tebbet yedâ ebî lehebin ve tebb. Mâ ağnâ anhü mâlühû ve mâ keseb. Seyaslâ nâran zâte leheb. Vemraetühû hammâlete'l-hatab. Fî cîdihâ hablün min mesed.",
        "meal": "Ebu Leheb'in elleri kurusun! Malı ve kazandığı ona fayda vermedi. Alevli ateşe girecek. Odun taşıyan karısı da; boynunda bir ip olduğu halde oraya girecektir."
    },
    "İhlas": {
        "okunus": "Kul hüvallâhü ehad. Allâhü's-samed. Lem yelid ve len yûled. Ve lem yekün lehû küfüven ehad.",
        "meal": "De ki: O Allah tektir. Allah sameddir (her şey O'na muhtaçtır). O, doğurmamış ve doğurulmamıştır. Hiçbir şey O'na denk değildir."
    },
    "Felak": {
        "okunus": "Kul eûzü bi-rabbi'l-felak. Min şerri mâ halak. Ve min şerri ğâsikın izâ vekab. Ve min şerri'n-neffâsâti fî'l-ukad. Ve min şerri hâsidin izâ hased.",
        "meal": "De ki: Sabahın Rabbine sığınırım. Yarattıklarının şerrinden, karanlık çöktüğünde gecenin şerrinden, düğümlere üfleyenlerin şerrinden, hasetçinin şerrinden."
    },
    "Nas": {
        "okunus": "Kul eûzü bi-rabbi'n-nâs. Meliki'n-nâs. İlâhi'n-nâs. Min şerri'l-vesvâsi'l-hannâs. Ellezî yüvesvisü fî sudûri'n-nâs. Mine'l-cinneti ven-nâs.",
        "meal": "De ki: İnsanların Rabbine, insanların Melikine, insanların İlahına sığınırım. O sinsi vesvesecinin şerrinden; insanların göğsüne vesvese veren cin ve insanlardan."
    }
}

# --- 3. 99 ESMAÜL HÜSNA (TAM LİSTE) ---
ESMA_LISTESI = {
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

# --- 4. YARDIMCI FONKSİYONLAR ---
@st.cache_data(ttl=3600)
def veri_al(sehir, tarih):
    url = f"http://api.aladhan.com/v1/calendarByCity?city={sehir}&country=Turkey&method=13&month={tarih.month}&year={tarih.year}"
    try:
        r = requests.get(url).json()
        return r.get('data', [])
    except:
        return []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("🕋 MENÜ")
    sehir_secimi = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana", "Gaziantep", "Samsun", "Diyarbakir"])
    
    if 'zk_sayi' not in st.session_state: st.session_state.zk_sayi = 0
    st.subheader(f"📿 Zikirmatik: {st.session_state.zk_sayi}")
    c1, c2 = st.columns(2)
    if c1.button("➕"): st.session_state.zk_sayi += 1; st.rerun()
    if c2.button("🔄"): st.session_state.zk_sayi = 0; st.rerun()

    with st.expander("📖 10 Sure ve Mealleri"):
        for ad, icerik in SURE_VERILERI.items():
            st.write(f"**{ad} Suresi**")
            st.caption(icerik['okunus'])
            st.info(icerik['meal'])

    with st.expander("✨ 99 Esmaül Hüsna"):
        for isim, anlam in ESMA_LISTESI.items():
            st.write(f"**{isim}:** {anlam}")

# --- 6. ANA EKRAN İŞLEMLERİ ---
tr_saat = datetime.utcnow() + timedelta(hours=3)
vakitler = veri_al(sehir_secimi, tr_saat)

# Ay sonu geçiş kontrolü
if tr_saat.day > 25:
    vakitler += veri_al(sehir_secimi, tr_saat.replace(day=28) + timedelta(days=5))

bugun_verisi = next((gun for gun in vakitler if gun['date']['gregorian']['date'] == tr_saat.strftime("%d-%m-%Y")), None)

if bugun_verisi:
    # 1. Başlık ve Ayet
    st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='ayet-kart'>
            <div style='font-size: 1.8rem; color: #fbc02d; font-family: "serif";'>كُنْتُمْ خَيْرَ اُمَّةٍ اُخْرِجَتْ لِلنَّاسِ تَأْمُرُونَ بِالْمَعْرُوفِ وَتَنْهَوْنَ عَنِ الْمُنْكَرِ وَتُؤْمِنُونَ بِاللّٰهِۜ</div>
            <div style='font-size: 1.2rem; margin-top:15px; color: white;'><b>Âli İmrân 110:</b> Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah'a inanırsınız.</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Geri Sayım Alanı
    sayac_alani = st.empty()

    # 3. Günlük Vakitler
    v_adlari = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
    v_saatleri = [bugun_verisi['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
    
    cols = st.columns(6)
    for i, (ad, saat) in enumerate(zip(v_adlari, v_saatleri)):
        cols[i].markdown(f"<div class='vakit-kart'>{ad}<br><span class='vakit-saat'>{saat}</span></div>", unsafe_allow_html=True)

    # 4. ANA EKRAN TÜRKÇE TAKVİM (SABİTLENDİ)
    st.markdown("<br><h3 style='text-align:center; color:#fbc02d;'>🗓️ 7 Günlük Namaz Vakitleri</h3>", unsafe_allow_html=True)
    
    idx = vakitler.index(bugun_verisi)
    takvim_kod = "<table class='ana-takvim'><tr><th>Tarih</th><th>İmsak</th><th>Güneş</th><th>Öğle</th><th>İkindi</th><th>Akşam</th><th>Yatsı</th></tr>"
    
    for g in vakitler[idx:idx+7]:
        t_str = g['date']['gregorian']['date']
        h_str = g['date']['gregorian']['weekday']['en']
        # Gün ismini Türkçeleştirme (Basit)
        gunler = {"Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba", "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"}
        t_turkce = f"{t_str} ({gunler.get(h_str, h_str)})"
        
        stil = "class='bugun-satir'" if t_str == tr_saat.strftime("%d-%m-%Y") else ""
        v_l = [g['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
        
        takvim_kod += f"<tr {stil}><td>{t_turkce}</td>" + "".join([f"<td>{x}</td>" for x in v_l]) + "</tr>"
    
    st.markdown(takvim_kod + "</table>", unsafe_allow_html=True)

    # --- 7. DÖNGÜ: GERİ SAYIM ---
    while True:
        simdi = datetime.utcnow() + timedelta(hours=3)
        hedef, h_idx = None, 0
        
        for i, vt in enumerate(v_saatleri):
            h, m = map(int, vt.split(":"))
            v_obj = simdi.replace(hour=h, minute=m, second=0, microsecond=0)
            if v_obj > simdi:
                hedef, h_idx = v_obj, i
                break
        
        if not hedef: # Ertesi güne geçiş
            sonraki_imsak = vakitler[vakitler.index(bugun_verisi)+1]['timings']['Fajr'].split(" ")[0]
            h_y, m_y = map(int, sonraki_imsak.split(":"))
            hedef = (simdi + timedelta(days=1)).replace(hour=h_y, minute=m_y, second=0)
            h_idx = 0

        saniye_fark = int((hedef - simdi).total_seconds())
        saat_k, dak_k, san_k = saniye_fark // 3600, (saniye_fark % 3600) // 60, saniye_fark % 60
        
        sayac_alani.markdown(f"""
            <div class='yuvarlak-sayac'>
                <div style='font-size:1.1rem; color:#fbc02d;'>{v_adlari[h_idx].upper()} VAKTİNE KALAN</div>
                <div style='font-size:4rem; font-weight:bold;'>{saat_k:02d}:{dak_k:02d}:{san_k:02d}</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)