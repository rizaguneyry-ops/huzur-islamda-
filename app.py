import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# --- 1. SAYFA AYARLARI VE TASARIM ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2070&auto=format&fit=crop");
        background-size: cover; background-attachment: fixed; color: white;
    }
    .besmele { text-align: center; font-size: 2.2rem; font-weight: bold; color: #fbc02d; margin-bottom: 10px; }
    .yuvarlak-sayac { 
        width: 240px; height: 240px; border-radius: 50%; border: 7px solid #fbc02d; 
        margin: 15px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: rgba(0,0,0,0.85); box-shadow: 0 0 30px #fbc02d;
    }
    .vakit-kart { background: white; color: black; border-radius: 12px; padding: 12px; text-align: center; border-bottom: 5px solid #fbc02d; }
    .vakit-saat { font-size: 1.6rem; font-weight: 900; color: #d4af37; }
    .haftalik-tablo { width: 100%; border-collapse: collapse; margin-top: 15px; background: rgba(0,0,0,0.7); color: white; border-radius: 8px; overflow: hidden; }
    .haftalik-tablo th { background: #fbc02d; color: black; padding: 10px; }
    .haftalik-tablo td { padding: 8px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SABİT VERİLER (10 SURE VE 99 ESMA) ---
SURELER = {
    "Fil Suresi": {
        "ok": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bi hicâratin min siccîl. Fe ce'alehüm ke'asfin me'kûl.",
        "tr": "Rabbinin, fil sahiplerine ne yaptığını görmedin mi? Onların tuzaklarını boşa çıkarmadı mı? Onların üzerine sürü sürü kuşlar gönderdi. Kuşlar onlara pişmiş çamurdan taşlar atıyorlardı. Sonunda onları yenilmiş ekin yaprağı gibi yaptı."
    },
    "Kureyş Suresi": {
        "ok": "Li îlâfi kureyş. Îlâfihim rihlete'ş-şitâi ve's-sayf. Fel ya'büdû rabbe hâze'l-beyt. Ellezî at'amehüm min cû'in ve âmenehüm min havf.",
        "tr": "Kureyş'i alıştırmak, onları kış ve yaz yolculuğuna alıştırmak için; öyleyse bu evin (Kabe'nin) Rabbine kulluk etsinler. O ki, onları açlıktan doyurdu ve korkudan emin kıldı."
    },
    "Maun Suresi": {
        "ok": "Era'eytellezî yükezzibü bi'd-dîn. Fe-zâlikellezî yedü''ul-yetîm. Ve lâ yehuddu alâ ta'âmil miskîn. Fe-veylün lil-müsallîn. Ellezîn hüm an salâtihim sâhûn. Ellezîn hüm yürâûn. Ve yemne'ûne'l-mâ'ûn.",
        "tr": "Dini yalanlayanı gördün mü? İşte yetimi itip kalkan, yoksulu doyurmaya teşvik etmeyen odur. Yazıklar olsun o namaz kılanlara ki, onlar namazlarını ciddiye almazlar. Onlar gösteriş yaparlar ve hayra engel olurlar."
    },
    "Kevser Suresi": {
        "ok": "İnnâ a'taynâke'l-kevser. Fe-salli li-rabbike venhar. İnne şânieke hüve'l-ebter.",
        "tr": "Şüphesiz biz sana Kevser'i verdik. Öyleyse Rabbin için namaz kıl ve kurban kes. Asıl sonu kesik olan, sana buğzedenin kendisidir."
    },
    "Kafirun Suresi": {
        "ok": "Kul yâ eyyühe'l-kâfirûn. Lâ a'büdü mâ ta'büdûn. Ve lâ entüm âbidûne mâ a'büd. Ve lâ ene âbidün mâ abedtüm. Ve entüm âbidûne mâ a'büd. Leküm dînüküm veliye dîn.",
        "tr": "De ki: Ey inkarcılar! Ben sizin taptıklarınıza tapmam. Siz de benim taptığıma tapıcılar değilsiniz. Ben sizin taptıklarınıza tapacak değilim. Siz de benim taptığıma tapacak değilsiniz. Sizin dininiz size, benim dinim banadır."
    },
    "Nasr Suresi": {
        "ok": "İzâ câe nasrullâhi ve'l-feth. Ve raeyte'n-nâse yedhulûne fî dînillâhi efvâcâ. Fe sebbih bi-hamdi rabbike vestağfirhü innehû kâne tevvâbâ.",
        "tr": "Allah'ın yardımı ve fetih geldiğinde, ve insanların Allah'ın dinine dalga dalga girdiklerini gördüğünde; artık Rabbini hamd ile tesbih et ve O'ndan bağışlanma dile. Çünkü O, tövbeleri çok kabul edendir."
    },
    "Tebbet Suresi": {
        "ok": "Tebbet yedâ ebî lehebin ve tebb. Mâ ağnâ anhü mâlühû ve mâ keseb. Seyaslâ nâran zâte leheb. Vemraetühû hammâlete'l-hatab. Fî cîdihâ hablün min mesed.",
        "tr": "Ebu Leheb'in elleri kurusun, kurudu da! Malı ve kazandıkları ona fayda vermedi. O, alevli bir ateşe girecek. Boynunda bükülmüş bir ip olduğu halde odun taşıyan karısı da."
    },
    "İhlas Suresi": {
        "ok": "Kul hüvallâhü ehad. Allâhü's-samed. Lem yelid ve len yûled. Ve lem yekün lehû küfüven ehad.",
        "tr": "De ki: O Allah tektir. Allah sameddir. O doğurmamış ve doğurulmamıştır. Hiçbir şey O'na denk değildir."
    },
    "Felak Suresi": {
        "ok": "Kul eûzü bi-rabbi'l-felak. Min şerri mâ halak. Ve min şerri ğâsikın izâ vekab. Ve min şerri'n-neffâsâti fî'l-ukad. Ve min şerri hâsidin izâ hased.",
        "tr": "De ki: Yarattığı şeylerin şerrinden, karanlığı çöktüğü zaman gecenin şerrinden, düğümlere üfleyenlerin şerrinden ve haset ettiği vakit hasetçinin şerrinden sabahın Rabbine sığınırım."
    },
    "Nas Suresi": {
        "ok": "Kul eûzü bi-rabbi'n-nâs. Meliki'n-nâs. İlâhi'n-nâs. Min şerri'l-vesvâsi'l-hannâs. Ellezî yüvesvisü fî sudûri'n-nâs. Mine'l-cinneti ven-nâs.",
        "tr": "De ki: İnsanların kalplerine vesvese veren, o sinsi vesvesecinin şerrinden insanların Rabbine, insanların melikine, insanların ilahına sığınırım."
    }
}

ESMA_99 = {
    "Allah": "Eşi benzeri olmayan", "Er-Rahmân": "Dünyada her canlıya merhamet eden", "Er-Rahîm": "Ahirette sadece müminlere rahmet eden", 
    "El-Melik": "Mülkün sahibi", "El-Kuddûs": "Hatadan münezzeh", "Es-Selâm": "Esenlik veren", "El-Mü'min": "Güven veren", 
    "El-Müheymin": "Gözeten", "El-Azîz": "İzzet sahibi", "El-Cebbâr": "Dilediğini yapan", "El-Mütekebbir": "Büyüklükte eşsiz", 
    "El-Hâlık": "Yaratan", "El-Bâri": "Kusursuz yaratan", "El-Musavvir": "Şekil veren", "El-Gaffâr": "Mağfireti bol", 
    "El-Kahhâr": "Her şeye galip", "El-Vehhâb": "Karşılıksız veren", "Er-Razzâk": "Rızık veren", "El-Fettâh": "Kapıları açan", 
    "El-Alîm": "Her şeyi bilen", "El-Kâbıd": "Darlık veren", "El-Bâsıt": "Bolluk veren", "El-Hâfıd": "Alçaltan", 
    "Er-Râfi": "Yükselten", "El-Muiz": "İzzet veren", "El-Müzil": "Zelil kılan", "Es-Semî": "İşiten", "El-Basîr": "Gören", 
    "El-Hakem": "Hükmeden", "El-Adl": "Adaletli", "El-Latîf": "Lütfeden", "El-Habîr": "Haberdar olan", "El-Halîm": "Yumuşak davranan", 
    "El-Azîm": "Pek yüce", "El-Gafûr": "Affeden", "Eş-Şekûr": "Mükafat veren", "El-Aliyy": "Yüce", "El-Kebîr": "Büyük", 
    "El-Hafîz": "Koruyan", "El-Mukît": "Besleyen", "El-Hasîb": "Hesaba çeken", "El-Celîl": "Azametli", "El-Kerîm": "Cömert", 
    "Er-Rakîb": "Gözetleyen", "El-Mucîb": "Kabul eden", "El-Vâsi": "İlmi geniş", "El-Hakîm": "Hikmetli", "El-Vedûd": "Seven", 
    "El-Mecîd": "Şanı yüce", "El-Bâis": "Dirilten", "Eş-Şehîd": "Şahit olan", "El-Hakk": "Gerçek olan", "El-Vekîl": "Güvenilen", 
    "El-Kaviyy": "Güçlü", "El-Metîn": "Sarsılmaz", "El-Veliyy": "Dost olan", "El-Hamîd": "Övülen", "El-Muhsî": "Sayan", 
    "El-Mübdî": "Başlatan", "El-Muîd": "Döndüren", "El-Muhyî": "Can veren", "El-Mümît": "Öldüren", "El-Hayy": "Diri", 
    "El-Kayyûm": "Ayakta tutan", "El-Vâcid": "Bulan", "El-Mâcid": "Kadri büyük", "El-Vâhid": "Tek", "Es-Samed": "Muhtaç olmayan", 
    "El-Kâdir": "Gücü yeten", "El-Muktedir": "Kuvvetli", "El-Muakdim": "Öne alan", "El-Muahhir": "Geriye bırakan", 
    "El-Evvel": "İlk", "El-Âhir": "Son", "Ez-Zâhir": "Açık", "El-Bâtın": "Gizli", "El-Vâlî": "Yöneten", "El-Müteâlî": "Yüce", 
    "El-Berr": "İyiliği bol", "Et-Tevvâb": "Tövbeyi kabul eden", "El-Müntakim": "Cezalandıran", "El-Afüvv": "Affeden", 
    "Er-Raûf": "Şefkatli", "Mâlikü’l-Mülk": "Mülkün sahibi", "Zü’l-Celâli ve’l-İkrâm": "Celal sahibi", "El-Muksit": "Adil", 
    "El-Câmi": "Toplayan", "El-Ganî": "Zengin", "El-Mugnî": "Zengin eden", "El-Mâni": "Engelleyen", "Ed-Dârr": "Zarar veren", 
    "En-Nâfi": "Fayda veren", "En-Nûr": "Nur", "El-Hâdî": "Yol gösteren", "El-Bedî": "Eşsiz yaratan", "El-Bâkî": "Ebedi", 
    "El-Vâris": "Gerçek varis", "Er-Reşîd": "Doğru yol gösteren", "Es-Sabûr": "Sabırlı"
}

LANGS = {
    "Türkçe": {"v": ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"], "k": "VAKTİNE KALAN", "b": "Bismillahirrahmanirrahim"},
    "English": {"v": ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"], "k": "TIME REMAINING", "b": "In the name of Allah"},
    "العربية": {"v": ["الفجر", "الشروق", "الظهر", "العصر", "المغرب", "العشاء"], "k": "الوقت المتبقي لـ", "b": "بسم الله الرحمن الرحيم"}
}

# --- 3. FONKSİYONLAR ---
@st.cache_data(ttl=3600)
def vakit_cek(city, date_obj):
    url = f"http://api.aladhan.com/v1/calendarByCity?city={city}&country=Turkey&method=13&month={date_obj.month}&year={date_obj.year}"
    try:
        return requests.get(url).json().get('data', [])
    except:
        return []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("🕋 MENÜ")
    dil = st.selectbox("🌐 Dil / Language", ["Türkçe", "English", "العربية"])
    L = LANGS[dil]
    sehir = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana"])
    
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.subheader(f"📿 Zikir: {st.session_state.zk}")
    c1, c2 = st.columns(2)
    if c1.button("➕"): st.session_state.zk += 1; st.rerun()
    if c2.button("🔄"): st.session_state.zk = 0; st.rerun()

    with st.expander("📖 10 Sure (Okunuş & Meal)"):
        for isim, icerik in SURELER.items():
            st.write(f"**{isim}**")
            st.caption(icerik['ok'])
            st.info(icerik['tr'])

    with st.expander("✨ Esmaül Hüsna (99 İsim)"):
        for isim, anlam in ESMA_99.items():
            st.write(f"**{isim}:** {anlam}")

# --- 5. ANA EKRAN VE AKICI DÖNGÜ ---
simdi = datetime.now()
takvim = vakit_cek(sehir, simdi)
if simdi.day > 25:
    takvim += vakit_cek(sehir, simdi.replace(day=28) + timedelta(days=5))

bugun_data = next((g for g in takvim if g['date']['gregorian']['date'] == simdi.strftime("%d-%m-%Y")), None)

if bugun_data:
    v_raw = bugun_data['timings']
    v_list = [v_raw[k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
    
    st.markdown(f"<div class='besmele'>{L['b']}</div>", unsafe_allow_html=True)
    
    sayac_alani = st.empty()
    
    cols = st.columns(6)
    for i, (ad, saat) in enumerate(zip(L['v'], v_list)):
        cols[i].markdown(f"<div class='vakit-kart'><b>{ad}</b><div class='vakit-saat'>{saat}</div></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader(f"🗓️ {dil} 7 Günlük Takvim")
    tablo = f"<table class='haftalik-tablo'><tr><th>Tarih</th>" + "".join([f"<th>{x}</th>" for x in L['v']]) + "</tr>"
    idx = takvim.index(bugun_data)
    for g in takvim[idx:idx+7]:
        d = g['date']['gregorian']
        v_line = [g['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
        tablo += f"<tr><td>{d['day']} {d['month']['en'][:3]}</td>" + "".join([f"<td>{x}</td>" for x in v_line]) + "</tr>"
    st.markdown(tablo + "</table>", unsafe_allow_html=True)

    # --- GERİ SAYIM DÖNGÜSÜ (TAKILMAYI ÖNLEYEN YAPI) ---
    while True:
        simdi_loop = datetime.now()
        hedef, h_idx = None, 0
        for i, vt in enumerate(v_list):
            hr, mn = map(int, vt.split(":"))
            target = simdi_loop.replace(hour=hr, minute=mn, second=0, microsecond=0)
            if target > simdi_loop:
                hedef, h_idx = target, i
                break
        
        if not hedef:
            h_i, m_i = map(int, takvim[takvim.index(bugun_data)+1]['timings']['Fajr'].split(" ")[0].split(":"))
            hedef = (simdi_loop + timedelta(days=1)).replace(hour=h_i, minute=m_i, second=0, microsecond=0)
            h_idx = 0

        sn = int((hedef - simdi_loop).total_seconds())
        sayac_alani.markdown(f"""
            <div class='yuvarlak-sayac'>
                <div style='font-size:0.9rem; color:#fbc02d;'>{L['v'][h_idx].upper()} {L['k']}</div>
                <div style='font-size:3.5rem; font-weight:bold;'>{sn//3600:02d}:{(sn%3600)//60:02d}:{sn%60:02d}</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)