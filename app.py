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
    .tarih-bandi { text-align: center; font-size: 1.3rem; background: rgba(0,0,0,0.6); padding: 12px; border-radius: 12px; margin-bottom: 15px; color: #fbc02d; border: 1px solid #fbc02d; font-weight: bold;}
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

# --- 2. ÇOK DİLLİ SİSTEM (YENİ DİLLER EKLENDİ) ---
DIL_AYARLARI = {
    "Türkçe": {
        "v": ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"], "k": "VAKTİNE KALAN", "b": "Bismillahirrahmanirrahim", "p": "Paylaş", "t": "7 Günlük Vakitler",
        "h_ay": {"Muharram": "Muharrem", "Safar": "Safer", "Rabi' al-awwal": "Rebiülevvel", "Rabi' al-thani": "Rebiülahir", "Jumada al-ula": "Cemaziyelevvel", "Jumada al-akhira": "Cemaziyelahir", "Rajab": "Recep", "Sha'ban": "Şaban", "Ramadan": "Ramazan", "Shawwal": "Şevval", "Dhu al-Qi'dah": "Zilkade", "Dhu al-Hijjah": "Zilhicce"},
        "g": {"Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba", "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"}
    },
    "العربية": {
        "v": ["إمساك", "شروق", "ظهر", "عصر", "مغرب", "عشاء"], "k": "الوقت المتبقي لـ", "b": "بسم الله الرحمن الرحيم", "p": "شارك", "t": "مواقيت الصلاة لمدة 7 أيام",
        "h_ay": {}, "g": {"Monday": "الإثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"}
    },
    "Deutsch": {
        "v": ["Imsak", "Sonnenaufgang", "Dhuhr", "Asr", "Maghrib", "Ischa"], "k": "VERBLEIBENDE ZEIT ZU", "b": "Im Namen Allahs", "p": "Teilen", "t": "7 Tage Gebetszeiten",
        "h_ay": {}, "g": {"Monday": "Montag", "Tuesday": "Dienstag", "Wednesday": "Mittwoch", "Thursday": "Donnerstag", "Friday": "Freitag", "Saturday": "Samstag", "Sunday": "Sonntag"}
    },
    "Русский": {
        "v": ["Имсак", "Восход", "Зухр", "Аср", "Магриб", "Иша"], "k": "ОСТАЛОСЬ ВРЕМЕНИ ДО", "b": "Во имя Аллаха", "p": "Поделиться", "t": "Время намаза на 7 дней",
        "h_ay": {}, "g": {"Monday": "Понедельник", "Tuesday": "Вторник", "Wednesday": "Среда", "Thursday": "Четверг", "Friday": "Пятница", "Saturday": "Суббота", "Sunday": "Воскресенье"}
    },
    "Español": {
        "v": ["Imsak", "Amanecer", "Dhuhr", "Asr", "Maghrib", "Isha"], "k": "TIEMPO RESTANTE PARA", "b": "En el nombre de Allah", "p": "Compartir", "t": "Horarios de oración de 7 días",
        "h_ay": {}, "g": {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
    },
    "中文": {
        "v": ["封斋", "日出", "晌礼", "晡礼", "昏礼", "宵礼"], "k": "剩余时间至", "b": "奉至仁至慈的安拉之名", "p": "分享", "t": "7天祷告时间表",
        "h_ay": {}, "g": {"Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三", "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六", "Sunday": "星期日"}
    }
}

# --- 3. SURELER VE ESMALAR (TAM METİN - KORUNDU) ---
SURE_VERILERI = {
    "Fil": {"o": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bi hicâratin min siccîl. Fe ce'alehüm ke'asfin me'kûl.", "m": "Rabbinin fil sahiplerine ne yaptığını görmedin mi? Onların tuzaklarını boşa çıkarmadı mı? Üzerlerine sürü sürü kuşlar gönderdi. Onlara çamurdan sertleşmiş taşlar atan kuşlar... Sonunda onları yenilmiş ekin yaprağı gibi yaptı."},
    "Kureyş": {"o": "Li îlâfi kureyş. Îlâfihim rihlete'ş-şitâi ve's-sayf. Fel ya'büdû rabbe hâze'l-beyt. Ellezî at'amehüm min cû'in ve âmenehüm min havf.", "m": "Kureyş'i alıştırmak için; kış ve yaz yolculuğuna... Bu evin Rabbine kulluk etsinler. O ki onları doyurdu ve korkudan emin kıldı."},
    "Maun": {"o": "Era'eytellezî yükezzibü bi'd-dîn. Fe-zâlikellezî yedü''ul-yetîm. Ve lâ yehuddu alâ ta'âmil miskîn. Fe-veylün lil-müsallîn. Ellezîn hüm an salâtihim sâhûn. Ellezîn hüm yürâûn. Ve yemne'ûne'l-mâ'ûn.", "m": "Dini yalanlayanı gördün mü? Yetimi itip kalkan odur. Yoksulu doyurmaya teşvik etmez. Yazıklar olsun o namaz kılanlara ki ciddiye almazlar. Gösteriş yaparlar ve yardıma engel olurlar."},
    "Kevser": {"o": "İnnâ a'taynâke'l-kevser. Fe-salli li-rabbike venhar. İnne şânieke hüve'l-ebter.", "m": "Şüphesiz biz sana Kevser'i verdik. Rabbin için namaz kıl, kurban kes. Asıl sonu kesik olan sana buğzedendir."},
    "Kafirun": {"o": "Kul yâ eyyühe'l-kâfirûn. Lâ a'büdü mâ ta'büdûn. Ve lâ entüm âbidûne mâ a'büd. Ve lâ ene âbidün mâ abedtüm. Ve entüm âbidûne mâ a'büd. Leküm dînüküm veliye dîn.", "m": "De ki: Ey inkarcılar! Ben sizin taptığınıza tapmam. Siz de benim taptığıma tapmazsınız. Sizin dininiz size, benimki banadır."},
    "Nasr": {"o": "İzâ câe nasrullâhi ve'l-feth. Ve raeyte'n-nâse yedhulûne fî dînillâhi efvâcâ. Fe sebbih bi-hamdi rabbike vestağfirhü innehû kâne tevvâbâ.", "m": "Allah'ın yardımı ve fetih geldiğinde, insanların dalga dalga dine girdiğini gördüğünde Rabbini hamd ile tesbih et, bağışlanma dile."},
    "Tebbet": {"o": "Tebbet yedâ ebî lehebin ve tebb. Mâ ağnâ anhü mâlühû ve mâ keseb. Seyaslâ nâran zâte leheb. Vemraetühû hammâlete'l-hatab. Fî cîdihâ hablün min mesed.", "m": "Ebu Leheb'in elleri kurusun! Malı ve kazandığı ona fayda vermedi. Alevli ateşe girecek. Odun taşıyan karısı da; boynunda bir ip olduğu halde oraya girecektir."},
    "İhlas": {"o": "Kul hüvallâhü ehad. Allâhü's-samed. Lem yelid ve len yûled. Ve len yekün lehû küfüven ehad.", "m": "De ki: O Allah tektir. Allah sameddir. O, doğurmamış ve doğurulmamıştır. Hiçbir şey O'na denk değildir."},
    "Felak": {"o": "Kul eûzü bi-rabbi'l-felak. Min şerri mâ halak. Ve min şerri ğâsikın izâ vekab. Ve min şerri'n-neffâsâti fî'l-ukad. Ve min şerri hâsidin izâ hased.", "m": "De ki: Sabahın Rabbine sığınırım. Yarattıklarının şerrinden, karanlık çöktüğünde gecenin şerrinden, düğümlere üfleyenlerin şerrinden, hasetçinin şerrinden."},
    "Nas": {"o": "Kul eûzü bi-rabbi'n-nâs. Meliki'n-nâs. İlâhi'n-nâs. Min şerri'l-vesvâsi'l-hannâs. Ellezî yüvesvisü fî sudûri'n-nâs. Mine'l-cinneti ven-nâs.", "m": "De ki: İnsanların Rabbine, insanların Melikine, insanların İlahına sığınırım."}
}

ESMA_99 = {
    "Allah": "Eşi benzeri olmayan", "Er-Rahmân": "Dünyada her canlıya merhamet eden", "Er-Rahîm": "Ahirette müminlere rahmet eden", "El-Melik": "Mülkün sahibi", "El-Kuddûs": "Eksiklikten uzak", "Es-Selâm": "Esenlik veren", "El-Mü'min": "Güven veren", "El-Müheymin": "Gözeten", "El-Azîz": "İzzet sahibi", "El-Cebbâr": "Dilediğini yapan", "El-Mütekebbir": "Büyük", "El-Hâlık": "Yaratan", "El-Bâri": "Kusursuz yaratan", "El-Musavvir": "Şekil veren", "El-Gaffâr": "Affı bol", "El-Kahhâr": "Galip", "El-Vehhâb": "Veren", "Er-Razzâk": "Rızık veren", "El-Fettâh": "Kapı açan", "El-Alîm": "Bilen", "El-Kâbıd": "Sıkan", "El-Bâsıt": "Açan", "El-Hâfıd": "Alçaltan", "Er-Râfi": "Yükselten", "El-Muiz": "Aziz kılan", "El-Müzil": "Zelil kılan", "Es-Semî": "İşiten", "El-Basîr": "Gören", "El-Hakem": "Hükmeden", "El-Adl": "Adaletli", "El-Latîf": "Lütfeden", "El-Habîr": "Haberdar", "El-Halîm": "Yumuşak", "El-Azîm": "Yüce", "El-Gafûr": "Affeden", "Eş-Şekûr": "Mükafat veren", "El-Aliyy": "Yüce", "El-Kebîr": "Büyük", "El-Hafîz": "Koruyan", "El-Mukît": "Besleyen", "El-Hasîb": "Hesap soran", "El-Celîl": "Azametli", "El-Kerîm": "Cömert", "Er-Rakîb": "Gözetleyen", "El-Mucîb": "Kabul eden", "El-Vâsi": "İlmi geniş", "El-Hakîm": "Hikmetli", "El-Vedûd": "Seven", "El-Mecîd": "Şanlı", "El-Bâis": "Dirilten", "Eş-Şehîd": "Şahit", "El-Hakk": "Gerçek", "El-Vekîl": "Güvenilen", "El-Kaviyy": "Güçlü", "El-Metîn": "Sarsılmaz", "El-Veliyy": "Dost", "El-Hamîd": "Övülen", "El-Muhsî": "Sayan", "El-Mübdî": "Başlatan", "El-Muîd": "Döndüren", "El-Muhyî": "Can veren", "El-Mümît": "Öldüren", "El-Hayy": "Diri", "El-Kayyûm": "Ayakta tutan", "El-Vâcid": "Bulan", "El-Mâcid": "Kadri yüce", "El-Vâhid": "Tek", "Es-Samed": "Muhtaç olmayan", "El-Kâdir": "Gücü yeten", "El-Muktedir": "Kuvvetli", "El-Muakdim": "Öne alan", "El-Muahhir": "Geriye atan", "El-Evvel": "İlk", "El-Âhir": "Son", "Ez-Zâhir": "Açık", "El-Bâtın": "Gizli", "El-Vâlî": "Yöneten", "El-Müteâlî": "Yüce", "El-Berr": "İyiliği bol", "Et-Tevvâb": "Tövbe kabul eden", "El-Müntakim": "Cezalandıran", "El-Afüvv": "Affeden", "Er-Raûf": "Şefkatli", "Mâlikü’l-Mülk": "Mülk sahibi", "Zü’l-Celâli ve’l-İkrâm": "Celal sahibi", "El-Muksit": "Adil", "El-Câmi": "Toplayan", "El-Ganî": "Zengin", "El-Mugnî": "Zengin eden", "El-Mâni": "Engelleyen", "Ed-Dârr": "Zarar veren", "En-Nâfi": "Fayda veren", "En-Nûr": "Nur", "El-Hâdî": "Hidayet veren", "El-Bedî": "Eşsiz", "El-Bâkî": "Ebedi", "El-Vâris": "Varis", "Er-Reşîd": "Yol gösteren", "Es-Sabûr": "Sabırlı"
}

# --- 4. FONKSİYONLAR ---
@st.cache_data(ttl=3600)
def veri_cek(sehir, tarih):
    url = f"http://api.aladhan.com/v1/calendarByCity?city={sehir}&country=Turkey&method=13&month={tarih.month}&year={tarih.year}"
    try: return requests.get(url).json().get('data', [])
    except: return []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("🕋 MENÜ / MENU")
    dil = st.selectbox("🌐 Dil / Language", list(DIL_AYARLARI.keys()))
    L = DIL_AYARLARI[dil]
    sehir_sec = st.selectbox("📍 Şehir / City", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana"])
    
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.subheader(f"📿 Zikirmatik: {st.session_state.zk}")
    c1, c2 = st.columns(2)
    if c1.button("➕"): st.session_state.zk += 1; st.rerun()
    if c2.button("🔄"): st.session_state.zk = 0; st.rerun()

    with st.expander("📖 10 Sure"):
        for k, v in SURE_VERILERI.items():
            st.write(f"**{k}**"); st.caption(v['o']); st.info(v['m'])
    with st.expander("✨ 99 Esma"):
        for k, v in ESMA_99.items(): st.write(f"**{k}:** {v}")

# --- 6. ANA EKRAN ---
tr_saat = datetime.utcnow() + timedelta(hours=3)
data = veri_cek(sehir_sec, tr_saat)
if tr_saat.day > 25: data += veri_cek(sehir_sec, tr_saat.replace(day=28) + timedelta(days=5))

bugun = next((g for g in data if g['date']['gregorian']['date'] == tr_saat.strftime("%d-%m-%Y")), None)

if bugun:
    v_liste = [bugun['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
    
    st.markdown(f"<div class='besmele'>{L['b']}</div>", unsafe_allow_html=True)
    st.markdown("""<div class='ayet-kart'>
        <div style='font-size: 1.8rem; color: #fbc02d;'>كُنْتُمْ خَيْرَ اُمَّةٍ اُ۟خْرِجَتْ لِلنَّاسِ تَأْمُرُونَ بِالْمَعْرُوفِ وَتَنْهَوْنَ عَنِ الْمُنْكَرِ وَتُؤْمِنُونَ بِاللّٰهِۜ</div>
        <div style='font-size: 1.1rem; margin-top:10px;'><b>Âli İmrân 110</b></div>
    </div>""", unsafe_allow_html=True)

    # TÜRKÇE HİCRİ TAKVİM VE MİLADİ TAKVİM
    h = bugun['date']['hijri']
    h_ay_tr = L.get('h_ay', {}).get(h['month']['en'], h['month']['en'])
    tarih_metni = f"📅 {tr_saat.strftime('%d.%m.%Y')} | 🌙 {h['day']} {h_ay_tr} {h['year']}"
    st.markdown(f"<div class='tarih-bandi'>{tarih_metni}</div>", unsafe_allow_html=True)

    sayac_alani = st.empty()
    
    cols = st.columns(6)
    for i, (ad, saat) in enumerate(zip(L['v'], v_liste)):
        cols[i].markdown(f"<div class='vakit-kart'>{ad}<br><span class='vakit-saat'>{saat}</span></div>", unsafe_allow_html=True)

    if st.button(f"📋 {L['p']}"):
        st.code(f"{sehir_sec} - " + ", ".join([f"{a}:{s}" for a,s in zip(L['v'], v_liste)]))

    # ANA EKRAN TAKVİM
    st.markdown(f"<h3 style='text-align:center; color:#fbc02d;'>{L['t']}</h3>", unsafe_allow_html=True)
    idx = data.index(bugun)
    tablo = f"<table class='ana-takvim'><tr><th>Tarih</th>" + "".join([f"<th>{x}</th>" for x in L['v']]) + "</tr>"
    for g in data[idx:idx+7]:
        d_g = g['date']['gregorian']
        gun_dil = L['g'].get(d_g['weekday']['en'], d_g['weekday']['en'])
        stil = "class='bugun-satir'" if d_g['date'] == tr_saat.strftime("%d-%m-%Y") else ""
        v_l = [g['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
        tablo += f"<tr {stil}><td>{d_g['date']}<br>{gun_dil}</td>" + "".join([f"<td>{x}</td>" for x in v_l]) + "</tr>"
    st.markdown(tablo + "</table>", unsafe_allow_html=True)

    # --- DÖNGÜ VE SES ---
    while True:
        an = datetime.utcnow() + timedelta(hours=3)
        hedef, h_idx = None, 0
        for i, vt in enumerate(v_liste):
            h, m = map(int, vt.split(":"))
            v_o = an.replace(hour=h, minute=m, second=0, microsecond=0)
            if v_o > an: hedef, h_idx = v_o, i; break
        
        if not hedef:
            y_i = data[data.index(bugun)+1]['timings']['Fajr'].split(" ")[0]
            h_y, m_y = map(int, y_i.split(":"))
            hedef = (an + timedelta(days=1)).replace(hour=h_y, minute=m_y, second=0)
            h_idx = 0

        diff = int((hedef - an).total_seconds())
        if diff == 0:
            st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', unsafe_allow_html=True)
            time.sleep(1); st.rerun()

        h_k, m_k, s_k = diff // 3600, (diff % 3600) // 60, diff % 60
        sayac_alani.markdown(f"""<div class='yuvarlak-sayac'>
            <div style='font-size:1.1rem; color:#fbc02d;'>{L['v'][h_idx].upper()} {L['k']}</div>
            <div style='font-size:4.2rem; font-weight:bold;'>{h_k:02d}:{m_k:02d}:{s_k:02d}</div>
        </div>""", unsafe_allow_html=True)
        time.sleep(1)