import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# --- 1. AYARLAR VE TASARIM (Madde 13) ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2070&auto=format&fit=crop");
        background-size: cover; background-attachment: fixed; color: white;
    }
    .besmele { text-align: center; font-size: 2.8rem; font-weight: bold; color: #fbc02d; margin-bottom: 5px; }
    .ayet-meal { text-align: center; background: rgba(255,192,45,0.1); padding: 15px; border-radius: 15px; border: 1px solid #fbc02d; margin: 0 10% 20px 10%; font-size: 1.1rem; }
    .yuvarlak-sayac { 
        width: 240px; height: 240px; border-radius: 50%; border: 8px solid #fbc02d; 
        margin: 10px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: rgba(0,0,0,0.9); box-shadow: 0 0 30px #fbc02d;
    }
    .vakit-kart { background: white; color: black; border-radius: 12px; padding: 10px; text-align: center; border-bottom: 6px solid #fbc02d; }
    .vakit-saat { font-size: 1.8rem; font-weight: 900; color: #d4af37; }
    .haftalik-tablo { width: 100%; border-collapse: collapse; margin-top: 20px; background: rgba(255,255,255,0.05); }
    .haftalik-tablo th { background: #fbc02d; color: black; padding: 10px; }
    .haftalik-tablo td { padding: 10px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ SETLERİ: SURELER (Madde 10) ---
SURELER_DATA = {
    "Fil Suresi": {"ok": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bi hicâratin min siccîl. Fe ce'alehüm ke'asfin me'kûl.", "tr": "Rabbinin, fil sahiplerine ne yaptığını görmedin mi? Onların tuzaklarını boşa çıkarmadı mı? Onların üzerine sürü sürü kuşlar gönderdi. Kuşlar onlara pişmiş çamurdan taşlar atıyorlardı. Sonunda onları yenilmiş ekin yaprağı gibi yaptı."},
    "Kureyş Suresi": {"ok": "Li îlâfi kureyş. Îlâfihim rihlete'ş-şitâi ve's-sayf. Fel ya'büdû rabbe hâze'l-beyt. Ellezî at'amehüm min cû'in ve âmenehüm min havf.", "tr": "Kureyş'i alıştırmak, onları kış ve yaz yolculuğuna alıştırmak için; öyleyse bu evin (Kabe'nin) Rabbine kulluk etsinler. O ki, onları açlıktan doyurdu ve korkudan emin kıldı."},
    "Maun Suresi": {"ok": "Era'eytellezî yükezzibü bi'd-dîn. Fe-zâlikellezî yedü''ul-yetîm. Ve lâ yehuddu alâ ta'âmil miskîn. Fe-veylün lil-müsallîn. Ellezîn hüm an salâtihim sâhûn. Ellezîn hüm yürâûn. Ve yemne'ûne'l-mâ'ûn.", "tr": "Dini yalanlayanı gördün mü? İşte yetimi itip kalkan, yoksulu doyurmaya teşvik etmeyen odur. Yazıklar olsun o namaz kılanlara ki, onlar namazlarını ciddiye almazlar. Onlar gösteriş yaparlar ve hayra engel olurlar."},
    "Kevser Suresi": {"ok": "İnnâ a'taynâke'l-kevser. Fe-salli li-rabbike venhar. İnne şânieke hüve'l-ebter.", "tr": "Şüphesiz biz sana Kevser'i verdik. Öyleyse Rabbin için namaz kıl ve kurban kes. Asıl sonu kesik olan, sana buğzedenin kendisidir."},
    "Kafirun Suresi": {"ok": "Kul yâ eyyühe'l-kâfirûn. Lâ a'büdü mâ ta'büdûn. Ve lâ entüm âbidûne mâ a'büd. Ve lâ ene âbidün mâ abedtüm. Ve entüm âbidûne mâ a'büd. Leküm dînüküm veliye dîn.", "tr": "De ki: Ey inkarcılar! Ben sizin taptıklarınıza tapmam. Siz de benim taptığıma tapıcılar değilsiniz. Ben sizin taptıklarınıza tapacak değilim. Siz de benim taptığıma tapacak değilsiniz. Sizin dininiz size, benim dinim banadır."},
    "Nasr Suresi": {"ok": "İzâ câe nasrullâhi ve'l-feth. Ve raeyte'n-nâse yedhulûne fî dînillâhi efvâcâ. Fe sebbih bi-hamdi rabbike vestağfirhü innehû kâne tevvâbâ.", "tr": "Allah'ın yardımı ve fetih geldiğinde, ve insanların Allah'ın dinine dalga dalga girdiklerini gördüğünde; artık Rabbini hamd ile tesbih et ve O'ndan bağışlanma dile. Çünkü O, tövbeleri çok kabul edendir."},
    "Tebbet Suresi": {"ok": "Tebbet yedâ ebî lehebin ve tebb. Mâ ağnâ anhü mâlühû ve mâ keseb. Seyaslâ nâran zâte leheb. Vemraetühû hammâlete'l-hatab. Fî cîdihâ hablün min mesed.", "tr": "Ebu Leheb'in elleri kurusun, kurudu da! Malı ve kazandıkları ona fayda vermedi. O, alevli bir ateşe girecek. Boynunda bükülmüş bir ip olduğu halde odun taşıyan karısı da."},
    "İhlas Suresi": {"ok": "Kul hüvallâhü ehad. Allâhü's-samed. Lem yelid ve len yûled. Ve lem yekün lehû küfüven ehad.", "tr": "De ki: O Allah tektir. Allah sameddir (her şey O'na muhtaçtır, O hiçbir şeye muhtaç değildir). O doğurmamış ve doğurulmamıştır. Hiçbir şey O'na denk değildir."},
    "Felak Suresi": {"ok": "Kul eûzü bi-rabbi'l-felak. Min şerri mâ halak. Ve min şerri ğâsikın izâ vekab. Ve min şerri'n-neffâsâti fî'l-ukad. Ve min şerri hâsidin izâ hased.", "tr": "De ki: Yarattığı şeylerin şerrinden, karanlığı çöktüğü zaman gecenin şerrinden, düğümlere üfleyenlerin şerrinden ve haset ettiği vakit hasetçinin şerrinden sabahın Rabbine sığınırım."},
    "Nas Suresi": {"ok": "Kul eûzü bi-rabbi'n-nâs. Meliki'n-nâs. İlâhi'n-nâs. Min şerri'l-vesvâsi'l-hannâs. Ellezî yüvesvisü fî sudûri'n-nâs. Mine'l-cinneti ven-nâs.", "tr": "De ki: İnsanların kalplerine vesvese veren, (insanlardan ve cinlerden olan) o sinsi vesvesecinin şerrinden insanların Rabbine, insanların melikine, insanların ilahına sığınırım."}
}

# --- 2.1 ESMAÜL HÜSNA (Madde 8) ---
ESMA_99 = {
    "Allah": "Tek İlah", "Er-Rahmân": "Dünyada her canlıya merhamet eden", "Er-Rahîm": "Ahirette sadece müminlere rahmet eden", "El-Melik": "Mülkün gerçek sahibi", "El-Kuddûs": "Eksiklikten uzak", "Es-Selâm": "Esenlik veren", "El-Mü'min": "Güven veren", "El-Müheymin": "Gözeten", "El-Azîz": "İzzet sahibi", "El-Cebbâr": "Dilediğini yapan", "El-Mütekebbir": "Büyüklükte eşsiz", "El-Hâlık": "Yaratan", "El-Bâri": "Kusursuz yaratan", "El-Musavvir": "Şekil veren", "El-Gaffâr": "Mağfireti bol", "El-Kahhâr": "Her şeye galip", "El-Vehhâb": "Karşılıksız veren", "Er-Razzâk": "Rızık veren", "El-Fettâh": "Kapıları açan", "El-Alîm": "Her şeyi bilen", "El-Kâbıd": "Darlık veren", "El-Bâsıt": "Bolluk veren", "El-Hâfıd": "Alçaltan", "Er-Râfi": "Yükselten", "El-Muiz": "İzzet veren", "El-Müzil": "Zelil kılan", "Es-Semî": "İşiten", "El-Basîr": "Gören", "El-Hakem": "Hükmeden", "El-Adl": "Adaletli", "El-Latîf": "Lütfeden", "El-Habîr": "Haberdar olan", "El-Halîm": "Yumuşak davranan", "El-Azîm": "Pek yüce", "El-Gafûr": "Affeden", "Eş-Şekûr": "Mükafat veren", "El-Aliyy": "Yüce", "El-Kebîr": "Büyük", "El-Hafîz": "Koruyan", "El-Mukît": "Besleyen", "El-Hasîb": "Hesaba çeken", "El-Celîl": "Azametli", "El-Kerîm": "Cömert", "Er-Rakîb": "Gözetleyen", "El-Mucîb": "Kabul eden", "El-Vâsi": "İlmi geniş", "El-Hakîm": "Hikmetli", "El-Vedûd": "Seven", "El-Mecîd": "Şanı yüce", "El-Bâis": "Dirilten", "Eş-Şehîd": "Şahit olan", "El-Hakk": "Varlığı değişmeyen", "El-Vekîl": "Güvenilen", "El-Kaviyy": "Güçlü", "El-Metîn": "Sarsılmaz", "El-Veliyy": "Dost olan", "El-Hamîd": "Övülen", "El-Muhsî": "Sayan", "El-Mübdî": "Başlatan", "El-Muîd": "Döndüren", "El-Muhyî": "Can veren", "El-Mümît": "Öldüren", "El-Hayy": "Diri", "El-Kayyûm": "Ayakta tutan", "El-Vâcid": "Bulan", "El-Mâcid": "Kadri büyük", "El-Vâhid": "Tek", "Es-Samed": "Muhtaç olmayan", "El-Kâdir": "Gücü yeten", "El-Muktedir": "Kuvvetli", "El-Muakdim": "Öne alan", "El-Muahhir": "Geriye bırakan", "El-Evvel": "İlk", "El-Âhir": "Son", "Ez-Zâhir": "Açık", "El-Bâtın": "Gizli", "El-Vâlî": "Yöneten", "El-Müteâlî": "Yüce", "El-Berr": "İyiliği bol", "Et-Tevvâb": "Tövbeyi kabul eden", "El-Müntakim": "Cezalandıran", "El-Afüvv": "Affeden", "Er-Raûf": "Şefkatli", "Mâlikü’l-Mülk": "Mülkün sahibi", "Zü’l-Celâli ve’l-İkrâm": "Celal ve İkram sahibi", "El-Muksit": "Adil", "El-Câmi": "Toplayan", "El-Ganî": "Zengin", "El-Mugnî": "Zengin eden", "El-Mâni": "Engelleyen", "Ed-Dârr": "Zarar veren", "En-Nâfi": "Fayda veren", "En-Nûr": "Nur", "El-Hâdî": "Hidayet veren", "El-Bedî": "Eşsiz yaratan", "El-Bâkî": "Ebedi", "El-Vâris": "Gerçek varis", "Er-Reşîd": "Doğru yol gösteren", "Es-Sabûr": "Sabırlı"
}

# --- 3. SIDEBAR (Madde 6, 7, 8, 9, 10, 11) ---
with st.sidebar:
    st.header("🕋 HUZUR MENÜSÜ")
    sehir = st.selectbox("📍 Şehir Seçin", ["Istanbul", "Ankara", "Izmir", "Bursa", "Konya", "Antalya", "Adana", "Gaziantep", "Sanliurfa"])
    
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f"<h3 style='text-align:center;'>📿 Zikirmatik: {st.session_state.zk}</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("➕ Artır"): st.session_state.zk += 1; st.rerun()
    if c2.button("🔄 Sıfırla"): st.session_state.zk = 0; st.rerun()

    with st.expander("📖 10 Sure (Okunuş & Meal)"):
        for isim, veri in SURELER_DATA.items():
            st.markdown(f"**{isim}**")
            st.caption(f"Arapça: {veri['ok']}")
            st.write(f"Meal: {veri['tr']}")
            st.divider()

    with st.expander("✨ Esmaül Hüsna (99 İsim)"):
        for isim, anlam in ESMA_99.items():
            st.write(f"**{isim}:** {anlam}")

    with st.expander("📌 Dini Rehber (32 Farz)"):
        st.write("İmanın Şartları: 6, İslamın Şartları: 5, Abdestin Farzları: 4, Guslün Farzları: 3, Teyemmümün Farzları: 2, Namazın Farzları: 12")
    st.info("🧭 **Kıble:** 147° (Güneydoğu)")

# --- 4. ANA DÖNGÜ (Takvim ve Geri Sayım) ---
@st.cache_data(ttl=86400)
def veri_al(sehir_adi, tarih):
    url = f"http://api.aladhan.com/v1/calendarByCity?city={sehir_adi}&country=Turkey&method=13&month={tarih.month}&year={tarih.year}"
    return requests.get(url).json()['data']

placeholder = st.empty()

try:
    simdi = datetime.now()
    takvim = veri_al(sehir, simdi)
    if simdi.day > 24: # Mart-Nisan Geçiş Düzeltmesi (Madde 4)
        takvim += veri_al(sehir, (simdi.replace(day=28) + timedelta(days=5)))

    while True:
        simdi = datetime.now()
        bugun_str = simdi.strftime("%d-%m-%Y")
        
        for i, gun in enumerate(takvim):
            if gun['date']['gregorian']['date'] == bugun_str:
                v_bugun = gun['timings']
                haftalik = takvim[i:i+7]
                break

        # Saat Temizleme (30 dk geri sayım hatası çözümü)
        v_map = {k: v_bugun[k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]}
        v_etiket = {"Fajr": "İmsak", "Sunrise": "Güneş", "Dhuhr": "Öğle", "Asr": "İkindi", "Maghrib": "Akşam", "Isha": "Yatsı"}

        hedef_vakit = None; hedef_ad = ""
        for k, v_saat in v_map.items():
            h, m = map(int, v_saat.split(":"))
            v_dt = simdi.replace(hour=h, minute=m, second=0, microsecond=0)
            if v_dt > simdi: hedef_vakit = v_dt; hedef_ad = v_etiket[k]; break
        
        if not hedef_vakit:
            h_imsak, m_imsak = map(int, takvim[takvim.index(gun)+1]['timings']['Fajr'].split(" ")[0].split(":"))
            hedef_vakit = (simdi + timedelta(days=1)).replace(hour=h_imsak, minute=m_imsak, second=0, microsecond=0)
            hedef_ad = "İmsak"

        fark = hedef_vakit - simdi
        sn = int(fark.total_seconds())
        h, m, s = sn // 3600, (sn % 3600) // 60, sn % 60

        with placeholder.container():
            st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
            st.markdown("<div class='ayet-meal'>'Şüphesiz namaz, müminler üzerine vakitleri belirlenmiş bir farzdır.' (Nisâ, 103)</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='yuvarlak-sayac'><div style='font-size:1.1rem; color:#fbc02d;'>{hedef_ad.upper()} VAKTİNE</div><div style='font-size:3.5rem; font-weight:900;'>{h:02d}:{m:02d}:{s:02d}</div></div>", unsafe_allow_html=True)
            
            cols = st.columns(6)
            for idx, (k, label) in enumerate(v_etiket.items()):
                cols[idx].markdown(f"<div class='vakit-kart'><b>{label}</b><br><span class='vakit-saat'>{v_map[k]}</span></div>", unsafe_allow_html=True)

            st.divider()
            st.subheader("🗓️ 7 Günlük Kesintisiz Takvim")
            tablo = "<table class='haftalik-tablo'><tr><th>Tarih</th><th>İmsak</th><th>Öğle</th><th>İkindi</th><th>Akşam</th><th>Yatsı</th></tr>"
            for h_gun in haftalik:
                vt = h_gun['timings']
                tablo += f"<tr><td>{h_gun['date']['gregorian']['day']} {h_gun['date']['gregorian']['month']['en'][:3]}</td><td>{vt['Fajr'].split(' ')[0]}</td><td>{vt['Dhuhr'].split(' ')[0]}</td><td>{vt['Asr'].split(' ')[0]}</td><td>{vt['Maghrib'].split(' ')[0]}</td><td>{vt['Isha'].split(' ')[0]}</td></tr>"
            st.markdown(tablo + "</table>", unsafe_allow_html=True)

        time.sleep(1)
except:
    st.rerun()