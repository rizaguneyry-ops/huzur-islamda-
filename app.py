import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# --- 1. AYARLAR VE TASARIM ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2070&auto=format&fit=crop");
        background-size: cover; background-attachment: fixed; color: white;
    }
    .besmele { text-align: center; font-size: 3rem; font-weight: bold; color: #fbc02d; margin-bottom: 5px; }
    .ayet-meal { text-align: center; background: rgba(255,192,45,0.1); padding: 15px; border-radius: 15px; border: 1px solid #fbc02d; margin: 0 10% 20px 10%; font-size: 1.1rem; }
    .yuvarlak-sayac { 
        width: 250px; height: 250px; border-radius: 50%; border: 8px solid #fbc02d; 
        margin: 15px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: rgba(0,0,0,0.9); box-shadow: 0 0 35px #fbc02d;
    }
    .vakit-kart { background: white; color: black; border-radius: 12px; padding: 10px; text-align: center; border-bottom: 6px solid #fbc02d; }
    .vakit-saat { font-size: 1.9rem; font-weight: 900; color: #d4af37; }
    .haftalik-tablo { width: 100%; border-collapse: collapse; margin-top: 20px; background: rgba(255,255,255,0.05); }
    .haftalik-tablo th { background: #fbc02d; color: black; padding: 12px; font-weight: bold; }
    .haftalik-tablo td { padding: 12px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ SETLERİ ---
AYLAR_TR = {1:"Ocak", 2:"Şubat", 3:"Mart", 4:"Nisan", 5:"Mayıs", 6:"Haziran", 7:"Temmuz", 8:"Ağustos", 9:"Eylül", 10:"Ekim", 11:"Kasım", 12:"Aralık"}

SURELER_TAM = {
    "Fil Suresi": "Bismillahirrahmânirrahîm. Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bi hicâratin min siccîl. Fe ce'alehüm ke'asfin me'kûl.",
    "Kureyş Suresi": "Bismillahirrahmânirrahîm. Li îlâfi kureyş. Îlâfihim rihlete'ş-şitâi ve's-sayf. Fel ya'büdû rabbe hâze'l-beyt. Ellezî at'amehüm min cû'in ve âmenehüm min havf.",
    "Maun Suresi": "Bismillahirrahmânirrahîm. Era'eytellezî yükezzibü bi'd-dîn. Fe-zâlikellezî yedü''ul-yetîm. Ve lâ yehuddu alâ ta'âmil miskîn. Fe-veylün lil-müsallîn. Ellezîn hüm an salâtihim sâhûn. Ellezîn hüm yürâûn. Ve yemne'ûne'l-mâ'ûn.",
    "Kevser Suresi": "Bismillahirrahmânirrahîm. İnnâ a'taynâke'l-kevser. Fe-salli li-rabbike venhar. İnne şânieke hüve'l-ebter.",
    "Kafirun Suresi": "Bismillahirrahmânirrahîm. Kul yâ eyyühe'l-kâfirûn. Lâ a'büdü mâ ta'büdûn. Ve lâ entüm âbidûne mâ a'büd. Ve lâ ene âbidün mâ abedtüm. Ve entüm âbidûne mâ a'büd. Leküm dînüküm veliye dîn.",
    "Nasr Suresi": "Bismillahirrahmânirrahîm. İzâ câe nasrullâhi ve'l-feth. Ve raeyte'n-nâse yedhulûne fî dînillâhi efvâcâ. Fe sebbih bi-hamdi rabbike vestağfirhü innehû kâne tevvâbâ.",
    "Tebbet Suresi": "Bismillahirrahmânirrahîm. Tebbet yedâ ebî lehebin ve tebb. Mâ ağnâ anhü mâlühû ve mâ keseb. Seyaslâ nâran zâte leheb. Vemraetühû hammâlete'l-hatab. Fî cîdihâ hablün min mesed.",
    "İhlas Suresi": "Bismillahirrahmânirrahîm. Kul hüvallâhü ehad. Allâhü's-samed. Lem yelid ve len yûled. Ve len yekün lehû küfüven ehad.",
    "Felak Suresi": "Bismillahirrahmânirrahîm. Kul eûzü bi-rabbi'l-felak. Min şerri mâ halak. Ve min şerri ğâsikın izâ vekab. Ve min şerri'n-neffâsâti fî'l-ukad. Ve min şerri hâsidin izâ hased.",
    "Nas Suresi": "Bismillahirrahmânirrahîm. Kul eûzü bi-rabbi'n-nâs. Meliki'n-nâs. İlâhi'n-nâs. Min şerri'l-vesvâsi'l-hannâs. Ellezî yüvesvisü fî sudûri'n-nâs. Mine'l-cinneti ven-nâs."
}

ESMAUL_HUSNA = ["Allah", "Er-Rahmân", "Er-Rahîm", "El-Melik", "El-Kuddûs", "Es-Selâm", "El-Mü'min", "El-Müheymin", "El-Azîz", "El-Cebbâr", "El-Mütekebbir", "El-Hâlık", "El-Bâri", "El-Musavvir", "El-Gaffâr", "El-Kahhâr", "El-Vehhâb", "Er-Razzâk", "El-Fettâh", "El-Alîm", "El-Kâbıd", "El-Bâsıt", "El-Hâfıd", "Er-Râfi", "El-Muiz", "El-Müzil", "Es-Semî", "El-Basîr", "El-Hakem", "El-Adl", "El-Latîf", "El-Habîr", "El-Halîm", "El-Azîm", "El-Gafûr", "Eş-Şekûr", "El-Aliyy", "El-Kebîr", "El-Hafîz", "El-Mukît", "El-Hasîb", "El-Celîl", "El-Kerîm", "Er-Rakîb", "El-Mucîb", "El-Vâsi", "El-Hakîm", "El-Vedûd", "El-Mecîd", "El-Bâis", "Eş-Şehîd", "El-Hakk", "El-Vekîl", "El-Kaviyy", "El-Metîn", "El-Veliyy", "El-Hamîd", "El-Muhsî", "El-Mübdî", "El-Muîd", "El-Muhyî", "El-Mümît", "El-Hayy", "El-Kayyûm", "El-Vâcid", "El-Mâcid", "El-Vâhid", "Es-Samed", "El-Kâdir", "El-Muktedir", "El-Muahhir", "El-Evvel", "El-Âhir", "Ez-Zâhir", "El-Bâtın", "El-Vâlî", "El-Müteâlî", "El-Berr", "Et-Tevvâb", "El-Müntakim", "El-Afüvv", "Er-Raûf", "Mâlikü’l-Mülk", "Zü’l-Celâli ve’l-İkrâm", "El-Muksit", "El-Câmi", "El-Ganî", "El-Mugnî", "El-Mâni", "Ed-Dârr", "En-Nâfi", "En-Nûr", "El-Hâdî", "El-Bedî", "El-Bâkî", "El-Vâris", "Er-Reşîd", "Es-Sabûr"]

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("🕋 HUZUR MENÜSÜ")
    sehir = st.selectbox("📍 Şehir Seçin", ["Istanbul", "Ankara", "Izmir", "Bursa", "Konya", "Antalya", "Adana", "Gaziantep", "Sanliurfa"])
    
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f"<h3 style='text-align:center;'>📿 Zikir Sayısı: {st.session_state.zk}</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("➕ Zikir Artır"): st.session_state.zk += 1; st.rerun()
    if c2.button("🔄 Sıfırla"): st.session_state.zk = 0; st.rerun()

    with st.expander("✨ Esmaül Hüsna (Tam 99 İsim)"):
        st.write(", ".join(ESMAUL_HUSNA))
    with st.expander("📖 10 Sure (Tam Metinler)"):
        for isim, metin in SURELER_TAM.items():
            st.markdown(f"**{isim}**\n{metin}")
            st.divider()
    with st.expander("📌 32 Farz & Rehber"):
        st.write("İmanın Şartları: 6\nİslamın Şartları: 5\nAbdestin Farzları: 4\nGuslün Farzları: 3\nTeyemmümün Farzları: 2\nNamazın Farzları: 12")
    st.info("🧭 **Kıble Yönü:** 147°")

# --- 4. ANA EKRAN ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
st.markdown("<div class='ayet-meal'>'Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız.' (Âli İmrân, 110)</div>", unsafe_allow_html=True)

govde = st.empty()

@st.cache_data(ttl=3600)
def api_verisi_al(sehir_adi):
    return requests.get(f"http://api.aladhan.com/v1/calendarByCity?city={sehir_adi}&country=Turkey&method=13").json()['data']

try:
    calendar_data = api_verisi_al(sehir)
    
    while True:
        simdi = datetime.now()
        bugun_data = calendar_data[simdi.day - 1]
        v = bugun_data['timings']
        
        v_map = {
            "İmsak": v['Fajr'].split(" ")[0], "Güneş": v['Sunrise'].split(" ")[0], "Öğle": v['Dhuhr'].split(" ")[0],
            "İkindi": v['Asr'].split(" ")[0], "Akşam": v['Maghrib'].split(" ")[0], "Yatsı": v['Isha'].split(" ")[0]
        }

        # --- DÜZELTİLMİŞ GERİ SAYIM MANTIĞI ---
        hedef_ad = ""
        hedef_vakit = None
        
        # Tüm vakitleri datetime objesine çevirip sıralı kontrol ediyoruz
        vakit_sirasi = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
        
        for ad in vakit_sirasi:
            saat_parcalari = v_map[ad].split(":")
            v_dt = simdi.replace(hour=int(saat_parcalari[0]), minute=int(saat_parcalari[1]), second=0, microsecond=0)
            
            if v_dt > simdi:
                hedef_ad = ad
                hedef_vakit = v_dt
                break
        
        # Eğer yatsı da geçtiyse hedef yarınki imsaktır
        if not hedef_vakit:
            hedef_ad = "İmsak"
            saat_parcalari = v_map["İmsak"].split(":")
            hedef_vakit = (simdi + timedelta(days=1)).replace(hour=int(saat_parcalari[0]), minute=int(saat_parcalari[1]), second=0, microsecond=0)

        fark = hedef_vakit - simdi
        toplam_saniye = int(fark.total_seconds())
        h = toplam_saniye // 3600
        m = (toplam_saniye % 3600) // 60
        s = toplam_saniye % 60

        with govde.container():
            st.markdown(f"""
                <div class='yuvarlak-sayac'>
                    <div style='font-size:1.2rem; color:#fbc02d;'>{hedef_ad.upper()} VAKTİNE</div>
                    <div style='font-size:3.5rem; font-weight:900;'>{h:02d}:{m:02d}:{s:02d}</div>
                    <div style='font-size:0.9rem;'>KALAN SÜRE</div>
                </div>
            """, unsafe_allow_html=True)

            kollar = st.columns(6)
            for i, (ad, saat) in enumerate(v_map.items()):
                kollar[i].markdown(f"<div class='vakit-kart'><b>{ad}</b><div class='vakit-saat'>{saat}</div></div>", unsafe_allow_html=True)

            # Haftalık Tablo
            st.divider()
            tablo = "<table class='haftalik-tablo'><tr><th>Tarih</th><th>İmsak</th><th>Güneş</th><th>Öğle</th><th>İkindi</th><th>Akşam</th><th>Yatsı</th></tr>"
            for i in range(7):
                idx = (simdi.day - 1 + i) % len(calendar_data)
                gun = calendar_data[idx]
                d = gun['date']['gregorian']
                vt = gun['timings']
                tablo += f"<tr><td><b>{d['day']} {AYLAR_TR[int(d['month']['number'])]}</b></td>" \
                         f"<td>{vt['Fajr'].split(' ')[0]}</td><td>{vt['Sunrise'].split(' ')[0]}</td>" \
                         f"<td>{vt['Dhuhr'].split(' ')[0]}</td><td>{vt['Asr'].split(' ')[0]}</td>" \
                         f"<td>{vt['Maghrib'].split(' ')[0]}</td><td>{vt['Isha'].split(' ')[0]}</td></tr>"
            tablo += "</table>"
            st.markdown(tablo, unsafe_allow_html=True)

        time.sleep(1)

except Exception as e:
    st.error("Sistem başlatılıyor...")
    time.sleep(2)
    st.rerun()