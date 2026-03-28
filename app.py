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
    .besmele { text-align: center; font-size: 2.2rem; font-weight: bold; color: #fbc02d; margin-bottom: 10px; }
    .yuvarlak-sayac { 
        width: 260px; height: 260px; border-radius: 50%; border: 8px solid #fbc02d; 
        margin: 20px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: rgba(0,0,0,0.9); box-shadow: 0 0 40px #fbc02d;
    }
    .vakit-kart { background: white; color: black; border-radius: 12px; padding: 15px; text-align: center; border-bottom: 6px solid #fbc02d; }
    .vakit-saat { font-size: 1.8rem; font-weight: 900; color: #d4af37; }
    .haftalik-tablo { width: 100%; border-collapse: collapse; margin-top: 20px; background: rgba(0,0,0,0.7); color: white; border-radius: 10px; overflow: hidden; }
    .haftalik-tablo th { background: #fbc02d; color: black; padding: 12px; }
    .haftalik-tablo td { padding: 10px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 10 SURE (TAM LİSTE - OKUNUŞ VE MEAL) ---
SURELER = {
    "Fil": {"o": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bi hicâratin min siccîl. Fe ce'alehüm ke'asfin me'kûl.", "m": "Rabbinin fil sahiplerine ne yaptığını görmedin mi? Onların tuzaklarını boşa çıkarmadı mı? Üzerlerine sürü sürü kuşlar gönderdi. Onlara çamurdan sertleşmiş taşlar atan kuşlar... Sonunda onları yenilmiş ekin yaprağı gibi yaptı."},
    "Kureyş": {"o": "Li îlâfi kureyş. Îlâfihim rihlete'ş-şitâi ve's-sayf. Fel ya'büdû rabbe hâze'l-beyt. Ellezî at'amehüm min cû'in ve âmenehüm min havf.", "m": "Kureyş'i alıştırmak için; kış ve yaz yolculuğuna... Bu evin Rabbine kulluk etsinler. O ki onları doyurdu ve korkudan emin kıldı."},
    "Maun": {"o": "Era'eytellezî yükezzibü bi'd-dîn. Fe-zâlikellezî yedü''ul-yetîm. Ve lâ yehuddu alâ ta'âmil miskîn. Fe-veylün lil-müsallîn. Ellezîn hüm an salâtihim sâhûn. Ellezîn hüm yürâûn. Ve yemne'ûne'l-mâ'ûn.", "m": "Dini yalanlayanı gördün mü? Yetimi itip kalkan odur. Yoksulu doyurmaya teşvik etmez. Yazıklar olsun o namaz kılanlara ki ciddiye almazlar. Gösteriş yaparlar ve yardıma engel olurlar."},
    "Kevser": {"o": "İnnâ a'taynâke'l-kevser. Fe-salli li-rabbike venhar. İnne şânieke hüve'l-ebter.", "m": "Şüphesiz biz sana Kevser'i verdik. Rabbin için namaz kıl, kurban kes. Asıl sonu kesik olan sana buğzedendir."},
    "Kafirun": {"o": "Kul yâ eyyühe'l-kâfirûn. Lâ a'büdü mâ ta'büdûn. Ve lâ entüm âbidûne mâ a'büd. Ve lâ ene âbidün mâ abedtüm. Ve entüm âbidûne mâ a'büd. Leküm dînüküm veliye dîn.", "m": "De ki: Ey inkarcılar! Ben sizin taptığınıza tapmam. Siz de benim taptığıma tapmazsınız. Sizin dininiz size, benimki banadır."},
    "Nasr": {"o": "İzâ câe nasrullâhi ve'l-feth. Ve raeyte'n-nâse yedhulûne fî dînillâhi efvâcâ. Fe sebbih bi-hamdi rabbike vestağfirhü innehû kâne tevvâbâ.", "m": "Allah'ın yardımı ve fetih geldiğinde, insanların dalga dalga dine girdiğini gördüğünde Rabbini hamd ile tesbih et, bağışlanma dile."},
    "Tebbet": {"o": "Tebbet yedâ ebî lehebin ve tebb. Mâ ağnâ anhü mâlühû ve mâ keseb. Seyaslâ nâran zâte leheb. Vemraetühû hammâlete'l-hatab. Fî cîdihâ hablün min mesed.", "m": "Ebu Leheb'in elleri kurusun! Malı fayda vermedi. Alevli ateşe girecek. Odun taşıyan karısı da; boynunda bir ip olduğu halde."},
    "İhlas": {"o": "Kul hüvallâhü ehad. Allâhü's-samed. Lem yelid ve len yûled. Ve lem yekün lehû küfüven ehad.", "m": "De ki: O Allah tektir. Sameddir. Doğurmamış ve doğurulmamıştır. Dengi yoktur."},
    "Felak": {"o": "Kul eûzü bi-rabbi'l-felak. Min şerri mâ halak. Ve min şerri ğâsikın izâ vekab. Ve min şerri'n-neffâsâti fî'l-ukad. Ve min şerri hâsidin izâ hased.", "m": "De ki: Sabahın Rabbine sığınırım. Yarattıklarının şerrinden, karanlık çöktüğünde gecenin şerrinden, düğümlere üfleyenlerin şerrinden, hasetçinin şerrinden."},
    "Nas": {"o": "Kul eûzü bi-rabbi'n-nâs. Meliki'n-nâs. İlâhi'n-nâs. Min şerri'l-vesvâsi'l-hannâs. Ellezî yüvesvisü fî sudûri'n-nâs. Mine'l-cinneti ven-nâs.", "m": "De ki: İnsanların Rabbine, Melikine, İlahına sığınırım. O sinsi vesvesecinin şerrinden; insanların göğsüne vesvese veren cin ve insanlardan."}
}

# --- 3. 99 ESMAÜL HÜSNA (EKSİKSİZ) ---
ESMA_99 = {
    "Allah": "Eşi benzeri olmayan", "Er-Rahmân": "Dünyada her canlıya merhamet eden", "Er-Rahîm": "Ahirette müminlere rahmet eden", "El-Melik": "Mülkün sahibi", "El-Kuddûs": "Eksiklikten uzak", "Es-Selâm": "Esenlik veren", "El-Mü'min": "Güven veren", "El-Müheymin": "Gözeten", "El-Azîz": "İzzet sahibi", "El-Cebbâr": "Dilediğini yapan", "El-Mütekebbir": "Büyük", "El-Hâlık": "Yaratan", "El-Bâri": "Kusursuz yaratan", "El-Musavvir": "Şekil veren", "El-Gaffâr": "Affı bol", "El-Kahhâr": "Galip", "El-Vehhâb": "Veren", "Er-Razzâk": "Rızık veren", "El-Fettâh": "Kapı açan", "El-Alîm": "Bilen", "El-Kâbıd": "Sıkan", "El-Bâsıt": "Açan", "El-Hâfıd": "Alçaltan", "Er-Râfi": "Yükselten", "El-Muiz": "Aziz kılan", "El-Müzil": "Zelil kılan", "Es-Semî": "İşiten", "El-Basîr": "Gören", "El-Hakem": "Hükmeden", "El-Adl": "Adil", "El-Latîf": "Lütfeden", "El-Habîr": "Haberdar", "El-Halîm": "Yumuşak", "El-Azîm": "Yüce", "El-Gafûr": "Affeden", "Eş-Şekûr": "Mükafat veren", "El-Aliyy": "Yüce", "El-Kebîr": "Büyük", "El-Hafîz": "Koruyan", "El-Mukît": "Besleyen", "El-Hasîb": "Hesap soran", "El-Celîl": "Azametli", "El-Kerîm": "Cömert", "Er-Rakîb": "Gözetleyen", "El-Mucîb": "Kabul eden", "El-Vâsi": "İlmi geniş", "El-Hakîm": "Hikmetli", "El-Vedûd": "Seven", "El-Mecîd": "Şanlı", "El-Bâis": "Dirilten", "Eş-Şehîd": "Şahit", "El-Hakk": "Gerçek", "El-Vekîl": "Güvenilen", "El-Kaviyy": "Güçlü", "El-Metîn": "Sarsılmaz", "El-Veliyy": "Dost", "El-Hamîd": "Övülen", "El-Muhsî": "Sayan", "El-Mübdî": "Başlatan", "El-Muîd": "Döndüren", "El-Muhyî": "Can veren", "El-Mümît": "Öldüren", "El-Hayy": "Diri", "El-Kayyûm": "Ayakta tutan", "El-Vâcid": "Bulan", "El-Mâcid": "Kadri yüce", "El-Vâhid": "Tek", "Es-Samed": "Muhtaç olmayan", "El-Kâdir": "Gücü yeten", "El-Muktedir": "Kuvvetli", "El-Muakdim": "Öne alan", "El-Muahhir": "Geriye atan", "El-Evvel": "İlk", "El-Âhir": "Son", "Ez-Zâhir": "Açık", "El-Bâtın": "Gizli", "El-Vâlî": "Yöneten", "El-Müteâlî": "Yüce", "El-Berr": "İyiliği bol", "Et-Tevvâb": "Tövbe kabul eden", "El-Müntakim": "Cezalandıran", "El-Afüvv": "Affeden", "Er-Raûf": "Şefkatli", "Mâlikü’l-Mülk": "Mülk sahibi", "Zü’l-Celâli ve’l-İkrâm": "Celal sahibi", "El-Muksit": "Adil", "El-Câmi": "Toplayan", "El-Ganî": "Zengin", "El-Mugnî": "Zengin eden", "El-Mâni": "Engelleyen", "Ed-Dârr": "Zarar veren", "En-Nâfi": "Fayda veren", "En-Nûr": "Nur", "El-Hâdî": "Hidayet veren", "El-Bedî": "Eşsiz", "El-Bâkî": "Ebedi", "El-Vâris": "Varis", "Er-Reşîd": "Yol gösteren", "Es-Sabûr": "Sabırlı"
}

# --- 4. DİLLER VE FONKSİYONLAR ---
LANGS = {
    "Türkçe": {"v": ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"], "k": "KALAN", "b": "Bismillahirrahmanirrahim", "t": "Haftalık Takvim"},
    "English": {"v": ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"], "k": "REMAINING", "b": "In the name of Allah", "t": "Weekly Schedule"},
    "العربية": {"v": ["الفجر", "الشروق", "الظهر", "العصر", "المغرب", "العشاء"], "k": "الوقت المتبقي لـ", "b": "بسم الله الرحمن الرحيم", "t": "تقويم أسبوعي"}
}

@st.cache_data(ttl=3600)
def fetch_data(city, date_obj):
    url = f"http://api.aladhan.com/v1/calendarByCity?city={city}&country=Turkey&method=13&month={date_obj.month}&year={date_obj.year}"
    try:
        return requests.get(url).json().get('data', [])
    except: return []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("🕋 MENÜ")
    dil = st.selectbox("🌐 Dil", list(LANGS.keys()))
    L = LANGS[dil]
    sehir = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana"])
    
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.subheader(f"📿 Zikir: {st.session_state.zk}")
    c1, c2 = st.columns(2)
    if c1.button("➕"): st.session_state.zk += 1; st.rerun()
    if c2.button("🔄"): st.session_state.zk = 0; st.rerun()

    with st.expander("📖 10 Sure ve Mealleri"):
        for k, v in SURELER.items():
            st.write(f"**{k}**"); st.caption(v['o']); st.info(v['m'])

    with st.expander("✨ 99 Esma"):
        for k, v in ESMA_99.items(): st.write(f"**{k}:** {v}")

# --- 6. ANA EKRAN ---
now = datetime.now()
data = fetch_data(sehir, now)
if now.day > 25: data += fetch_data(sehir, now.replace(day=28) + timedelta(days=5))

today = next((g for g in data if g['date']['gregorian']['date'] == now.strftime("%d-%m-%Y")), None)

if today:
    v_times = [today['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
    st.markdown(f"<div class='besmele'>{L['b']}</div>", unsafe_allow_html=True)
    sayac = st.empty()
    
    cols = st.columns(6)
    for i, (ad, saat) in enumerate(zip(L['v'], v_times)):
        cols[i].markdown(f"<div class='vakit-kart'><b>{ad}</b><div class='vakit-saat'>{saat}</div></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader(f"🗓️ {L['t']}")
    tab_html = f"<table class='haftalik-tablo'><tr><th>Tarih</th>" + "".join([f"<th>{x}</th>" for x in L['v']]) + "</tr>"
    idx = data.index(today)
    for g in data[idx:idx+7]:
        d = g['date']['gregorian']
        v_l = [g['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
        tab_html += f"<tr><td>{d['day']} {d['month']['en'][:3]}</td>" + "".join([f"<td>{x}</td>" for x in v_l]) + "</tr>"
    st.markdown(tab_html + "</table>", unsafe_allow_html=True)

    # --- GERİ SAYIM DÖNGÜSÜ ---
    while True:
        curr = datetime.now()
        target, t_idx = None, 0
        for i, vt in enumerate(v_times):
            hr, mn = map(int, vt.split(":"))
            t_obj = curr.replace(hour=hr, minute=mn, second=0, microsecond=0)
            if t_obj > curr:
                target, t_idx = t_obj, i
                break
        
        if not target:
            h_i, m_i = map(int, data[data.index(today)+1]['timings']['Fajr'].split(" ")[0].split(":"))
            target = (curr + timedelta(days=1)).replace(hour=h_i, minute=m_i, second=0, microsecond=0)
            t_idx = 0

        diff = int((target - curr).total_seconds())
        sayac.markdown(f"""
            <div class='yuvarlak-sayac'>
                <div style='font-size:1rem; color:#fbc02d;'>{L['v'][t_idx].upper()} {L['k']}</div>
                <div style='font-size:3.5rem; font-weight:bold;'>{diff//3600:02d}:{(diff%3600)//60:02d}:{diff%60:02d}</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)