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

# --- 2. 10 SURE (TAM METİN - KISALTMA YOK) ---
SURE_VERILERI = {
    "Fil": {
        "o": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bi hicâratin min siccîl. Fe ce'alehüm ke'asfin me'kûl.",
        "m": "Rabbinin fil sahiplerine ne yaptığını görmedin mi? Onların tuzaklarını boşa çıkarmadı mı? Üzerlerine sürü sürü kuşlar gönderdi. Onlara çamurdan sertleşmiş taşlar atan kuşlar... Sonunda onları yenilmiş ekin yaprağı gibi yaptı."
    },
    "Kureyş": {
        "o": "Li îlâfi kureyş. Îlâfihim rihlete'ş-şitâi ve's-sayf. Fel ya'büdû rabbe hâze'l-beyt. Ellezî at'amehüm min cû'in ve âmenehüm min havf.",
        "m": "Kureyş'i alıştırmak için; kış ve yaz yolculuğuna... Bu evin Rabbine kulluk etsinler. O ki onları doyurdu ve korkudan emin kıldı."
    },
    "Maun": {
        "o": "Era'eytellezî yükezzibü bi'd-dîn. Fe-zâlikellezî yedü''ul-yetîm. Ve lâ yehuddu alâ ta'âmil miskîn. Fe-veylün lil-müsallîn. Ellezîn hüm an salâtihim sâhûn. Ellezîn hüm yürâûn. Ve yemne'ûne'l-mâ'ûn.",
        "m": "Dini yalanlayanı gördün mü? Yetimi itip kalkan odur. Yoksulu doyurmaya teşvik etmez. Yazıklar olsun o namaz kılanlara ki ciddiye almazlar. Gösteriş yaparlar ve yardıma engel olurlar."
    },
    "Kevser": {
        "o": "İnnâ a'taynâke'l-kevser. Fe-salli li-rabbike venhar. İnne şânieke hüve'l-ebter.",
        "m": "Şüphesiz biz sana Kevser'i verdik. Rabbin için namaz kıl, kurban kes. Asıl sonu kesik olan sana buğzedendir."
    },
    "Kafirun": {
        "o": "Kul yâ eyyühe'l-kâfirûn. Lâ a'büdü mâ ta'büdûn. Ve lâ entüm âbidûne mâ a'büd. Ve lâ ene âbidün mâ abedtüm. Ve entüm âbidûne mâ a'büd. Leküm dînüküm veliye dîn.",
        "m": "De ki: Ey inkarcılar! Ben sizin taptığınıza tapmam. Siz de benim taptığıma tapmazsınız. Sizin dininiz size, benimki banadır."
    },
    "Nasr": {
        "o": "İzâ câe nasrullâhi ve'l-feth. Ve raeyte'n-nâse yedhulûne fî dînillâhi efvâcâ. Fe sebbih bi-hamdi rabbike vestağfirhü innehû kâne tevvâbâ.",
        "m": "Allah'ın yardımı ve fetih geldiğinde, insanların dalga dalga dine girdiğini gördüğünde Rabbini hamd ile tesbih et, bağışlanma dile. Şüphesiz O, tövbeleri çok kabul edendir."
    },
    "Tebbet": {
        "o": "Tebbet yedâ ebî lehebin ve tebb. Mâ ağnâ anhü mâlühû ve mâ keseb. Seyaslâ nâran zâte leheb. Vemraetühû hammâlete'l-hatab. Fî cîdihâ hablün min mesed.",
        "m": "Ebu Leheb'in elleri kurusun! Malı ve kazandığı ona fayda vermedi. Alevli ateşe girecek. Odun taşıyan karısı da; boynunda bir ip olduğu halde oraya girecektir."
    },
    "İhlas": {
        "o": "Kul hüvallâhü ehad. Allâhü's-samed. Lem yelid ve len yûled. Ve lem yekün lehû küfüven ehad.",
        "m": "De ki: O Allah tektir. Allah sameddir (her şey O'na muhtaçtır). O, doğurmamış ve doğurulmamıştır. Hiçbir şey O'na denk değildir."
    },
    "Felak": {
        "o": "Kul eûzü bi-rabbi'l-felak. Min şerri mâ halak. Ve min şerri ğâsikın izâ vekab. Ve min şerri'n-neffâsâti fî'l-ukad. Ve min şerri hâsidin izâ hased.",
        "m": "De ki: Sabahın Rabbine sığınırım. Yarattıklarının şerrinden, karanlık çöktüğünde gecenin şerrinden, düğümlere üfleyenlerin şerrinden, hasetçinin şerrinden."
    },
    "Nas": {
        "o": "Kul eûzü bi-rabbi'n-nâs. Meliki'n-nâs. İlâhi'n-nâs. Min şerri'l-vesvâsi'l-hannâs. Ellezî yüvesvisü fî sudûri'n-nâs. Mine'l-cinneti ven-nâs.",
        "m": "De ki: İnsanların Rabbine, insanların Melikine, insanların İlahına sığınırım. O sinsi vesvesecinin şerrinden; insanların göğsüne vesvese veren cin ve insanlardan."
    }
}

# --- 3. 99 ESMAÜL HÜSNA (TAM LİSTE - KISALTMA YOK) ---
ESMA_99 = {
    "Allah": "Eşi benzeri olmayan, tek ilah.", "Er-Rahmân": "Dünyada her canlıya merhamet eden.", "Er-Rahîm": "Ahirette sadece müminlere rahmet eden.",
    "El-Melik": "Mülkün gerçek sahibi.", "El-Kuddûs": "Her türlü eksiklikten uzak olan.", "Es-Selâm": "Esenlik veren, selamete çıkaran.", "El-Mü'min": "Güven veren, koruyan.",
    "El-Müheymin": "Her şeyi görüp gözeten.", "El-Azîz": "İzzet sahibi, mağlup edilemeyen.", "El-Cebbâr": "Dilediğini zorla yaptıran, eksikleri tamamlayan.", "El-Mütekebbir": "Büyüklükte eşi olmayan.",
    "El-Hâlık": "Yaratan.", "El-Bâri": "Kusursuz yaratan.", "El-Musavvir": "Şekil ve özellik veren.", "El-Gaffâr": "Günahları çokça affeden.",
    "El-Kahhâr": "Her şeye galip gelen.", "El-Vehhâb": "Karşılıksız veren.", "Er-Razzâk": "Rızık veren.", "El-Fettâh": "Hayırlı kapıları açan.",
    "El-Alîm": "Her şeyi en ince detayına kadar bilen.", "El-Kâbıd": "Rızkı daraltan, ruhları alan.", "El-Bâsıt": "Rızkı genişleten, ferahlık veren.", "El-Hâfıd": "Alçaltan.", "Er-Râfi": "Yükselten.",
    "El-Muiz": "İzzet veren, aziz kılan.", "El-Müzil": "Zelil kılan, değersizleştiren.", "Es-Semî": "Her şeyi işiten.", "El-Basîr": "Her şeyi gören.", "El-Hakem": "Mutlak hükmeden.",
    "El-Adl": "Tam adaletli olan.", "El-Latîf": "Lütufta bulunan, her şeye nüfuz eden.", "El-Habîr": "Her şeyden haberdar olan.", "El-Halîm": "Yumuşak davranan, hemen cezalandırmayan.", "El-Azîm": "Pek yüce olan.",
    "El-Gafûr": "Mağfireti bol olan.", "Eş-Şekûr": "Şükürleri kabul eden, mükafatlandıran.", "El-Aliyy": "Çok yüce.", "El-Kebîr": "Çok büyük.", "El-Hafîz": "Koruyup kollayan.",
    "El-Mukît": "Besleyen, rızıkları yaratan.", "El-Hasîb": "Hesaba çeken.", "El-Celîl": "Azamet ve celal sahibi.", "El-Kerîm": "Keremi bol, cömert.", "Er-Rakîb": "Gözetleyen.",
    "El-Mucîb": "Duaları kabul eden.", "El-Vâsi": "İlmi ve merhameti geniş.", "El-Hakîm": "Her işi hikmetli olan.", "El-Vedûd": "Kullarını seven ve sevilmeye layık olan.", "El-Mecîd": "Şanı yüce olan.",
    "El-Bâis": "Ölüleri dirilten.", "Eş-Şehîd": "Her şeye şahit olan.", "El-Hakk": "Varlığı hiç değişmeyen, gerçek.", "El-Vekîl": "Güvenilip dayanılan.", "El-Kaviyy": "Pek güçlü.",
    "El-Metîn": "Sarsılmaz güç sahibi.", "El-Veliyy": "Müminlere dost olan.", "El-Hamîd": "Hamd edilen, övülen.", "El-Muhsî": "Her şeyin sayısını bilen.", "El-Mübdî": "Örneksiz yaratan.",
    "El-Muîd": "Yeniden dirilten.", "El-Muhyî": "Can veren.", "El-Mümît": "Öldüren.", "El-Hayy": "Sonsuz diri.", "El-Kayyûm": "Her şeyi ayakta tutan.",
    "El-Vâcid": "İstediğini bulan.", "El-Mâcid": "Kadri ve şanı büyük.", "El-Vâhid": "Zatında tek olan.", "Es-Samed": "Kimseye muhtaç olmayan.", "El-Kâdir": "Dilediğini yapmaya gücü yeten.",
    "El-Muktedir": "Kuvvet sahibi.", "El-Muakdim": "Dilediğini öne alan.", "El-Muahhir": "Dilediğini geriye atan.", "El-Evvel": "Başlangıcı olmayan.", "El-Âhir": "Sonu olmayan.",
    "Ez-Zâhir": "Varlığı apaçık olan.", "El-Bâtın": "Gizli olan, mahiyeti bilinmeyen.", "El-Vâlî": "Yöneten.", "El-Müteâlî": "En yüce.", "El-Berr": "İyiliği bol olan.",
    "Et-Tevvâb": "Tövbeleri kabul eden.", "El-Müntakim": "İntikam alan, suçluları cezalandıran.", "El-Afüvv": "Affı çok olan.", "Er-Raûf": "Çok şefkatli.",
    "Mâlikü’l-Mülk": "Mülkün ebedi sahibi.", "Zü’l-Celâli ve’l-İkrâm": "Celal ve ikram sahibi.", "El-Muksit": "Adaletle hükmeden.", "El-Câmi": "Toplayan.",
    "El-Ganî": "Çok zengin, muhtaç olmayan.", "El-Mugnî": "Zengin eden.", "El-Mâni": "Engelleyen.", "Ed-Dârr": "Zarar veren (imtihan eden).", "En-Nâfi": "Fayda veren.",
    "En-Nûr": "Nurlandıran.", "El-Hâdî": "Hidayet veren.", "El-Bedî": "Eşsiz yaratan.", "El-Bâkî": "Varlığı sonsuz olan.", "El-Vâris": "Her şeyin son sahibi.",
    "Er-Reşîd": "Doğru yolu gösteren.", "Es-Sabûr": "Çok sabırlı."
}

# --- 4. DİL VE YARDIMCI FONKSİYONLAR ---
LANGS = {
    "Türkçe": {
        "vakitler": ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"],
        "kalan": "VAKTİNE KALAN", "besmele": "Bismillahirrahmanirrahim",
        "paylas": "Kopyala ve Paylaş", "takvim_baslik": "7 Günlük Namaz Vakitleri",
        "gunler": {"Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba", "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"}
    },
    "English": {
        "vakitler": ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"],
        "kalan": "TIME REMAINING", "besmele": "In the name of Allah",
        "paylas": "Copy and Share", "takvim_baslik": "7 Days Prayer Times",
        "gunler": {"Monday": "Monday", "Tuesday": "Tuesday", "Wednesday": "Wednesday", "Thursday": "Thursday", "Friday": "Friday", "Saturday": "Saturday", "Sunday": "Sunday"}
    }
}

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
    dil_secim = st.selectbox("🌐 Dil", ["Türkçe", "English"])
    L = LANGS[dil_secim]
    sehir_secim = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana", "Gaziantep", "Samsun", "Diyarbakir"])
    
    if 'zk_deger' not in st.session_state: st.session_state.zk_deger = 0
    st.subheader(f"📿 Zikirmatik: {st.session_state.zk_deger}")
    c1, c2 = st.columns(2)
    if c1.button("➕ Artır"): st.session_state.zk_deger += 1; st.rerun()
    if c2.button("🔄 Sıfırla"): st.session_state.zk_deger = 0; st.rerun()

    with st.expander("📖 10 Sure"):
        for ad, icerik in SURE_VERILERI.items():
            st.write(f"**{ad} Suresi**")
            st.caption(icerik['o'])
            st.info(icerik['m'])

    with st.expander("✨ 99 Esma"):
        for isim, anlam in ESMA_99.items():
            st.write(f"**{isim}:** {anlam}")

# --- 6. ANA EKRAN ---
tr_an = datetime.utcnow() + timedelta(hours=3)
vakitler_listesi = veri_al(sehir_secim, tr_an)

# Ay sonu kontrolü
if tr_an.day > 25:
    vakitler_listesi += veri_al(sehir_secim, tr_an.replace(day=28) + timedelta(days=5))

bugun_data = next((gun for gun in vakitler_listesi if gun['date']['gregorian']['date'] == tr_an.strftime("%d-%m-%Y")), None)

if bugun_data:
    st.markdown(f"<div class='besmele'>{L['besmele']}</div>", unsafe_allow_html=True)
    
    # Âli İmrân 110
    st.markdown("""<div class='ayet-kart'>
        <div style='font-size: 1.8rem; color: #fbc02d;'>كُنْتُمْ خَيْرَ اُمَّةٍ اُخْرِجَتْ لِلنَّاسِ تَأْمُرُونَ بِالْمَعْرُوفِ وَتَنْهَوْنَ عَنِ الْمُنْكَرِ وَتُؤْمِنُونَ بِاللّٰهِۜ</div>
        <div style='font-size: 1.1rem; margin-top:12px;'><b>Âli İmrân 110:</b> Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah'a inanırsınız.</div>
    </div>""", unsafe_allow_html=True)

    # Takvim Bandı (Sayacın Üstüne)
    hic_gun = bugun_data['date']['hijri']
    st.markdown(f"<div class='tarih-bandi'>📅 {tr_an.strftime('%d.%m.%Y')} | 🌙 {hic_gun['day']} {hic_gun['month']['en']} {hic_gun['year']}</div>", unsafe_allow_html=True)

    sayac_ekran = st.empty()

    # Vakit Kartları
    v_saatler = [bugun_data['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
    cols = st.columns(6)
    for i, (ad, saat) in enumerate(zip(L['vakitler'], v_saatler)):
        cols[i].markdown(f"<div class='vakit-kart'>{ad}<br><span class='vakit-saat'>{saat}</span></div>", unsafe_allow_html=True)

    # Paylaş Butonu
    if st.button(f"📋 {L['paylas']}"):
        mesaj = f"🕋 {sehir_secim} Vakitleri:\n" + "\n".join([f"{a}: {s}" for a,s in zip(L['vakitler'], v_saatler)])
        st.code(mesaj)

    # HAFTALIK TAKVİM (SABİT)
    st.markdown(f"<h3 style='text-align:center; color:#fbc02d;'>{L['takvim_baslik']}</h3>", unsafe_allow_html=True)
    idx = vakitler_listesi.index(bugun_data)
    takvim_html = "<table class='ana-takvim'><tr><th>Tarih</th><th>İmsak</th><th>Güneş</th><th>Öğle</th><th>İkindi</th><th>Akşam</th><th>Yatsı</th></tr>"
    for g in vakitler_listesi[idx:idx+7]:
        d_greg = g['date']['gregorian']
        gun_adi = L['gunler'].get(d_greg['weekday']['en'], d_greg['weekday']['en'])
        stil = "class='bugun-satir'" if d_greg['date'] == tr_an.strftime("%d-%m-%Y") else ""
        v_l = [g['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
        takvim_html += f"<tr {stil}><td>{d_greg['date']}<br>{gun_adi}</td>" + "".join([f"<td>{x}</td>" for x in v_l]) + "</tr>"
    st.markdown(takvim_html + "</table>", unsafe_allow_html=True)

    # --- SAYAÇ VE SESLİ BİLDİRİM DÖNGÜSÜ ---
    while True:
        simdi = datetime.utcnow() + timedelta(hours=3)
        target, t_idx = None, 0
        for i, vt in enumerate(v_saatler):
            h, m = map(int, vt.split(":"))
            v_o = simdi.replace(hour=h, minute=m, second=0, microsecond=0)
            if v_o > simdi: target, t_idx = v_o, i; break
        
        if not target:
            y_i = vakitler_listesi[vakitler_listesi.index(bugun_data)+1]['timings']['Fajr'].split(" ")[0]
            h_y, m_y = map(int, y_i.split(":"))
            target = (simdi + timedelta(days=1)).replace(hour=h_y, minute=m_y, second=0)
            t_idx = 0

        diff_s = int((target - simdi).total_seconds())
        
        if diff_s == 0: # VAKİT GELDİĞİNDE SESLİ UYARI
            st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', unsafe_allow_html=True)
            time.sleep(1); st.rerun()

        h_k, m_k, s_k = diff_s // 3600, (diff_s % 3600) // 60, diff_s % 60
        sayac_ekran.markdown(f"""<div class='yuvarlak-sayac'>
            <div style='font-size:1.1rem; color:#fbc02d;'>{L['vakitler'][t_idx].upper()} {L['kalan']}</div>
            <div style='font-size:4rem; font-weight:bold;'>{h_k:02d}:{m_k:02d}:{s_k:02d}</div>
        </div>""", unsafe_allow_html=True)
        time.sleep(1)