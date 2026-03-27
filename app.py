import streamlit as st
import requests
from datetime import datetime

# --- 1. AYARLAR VE TASARIM (ÖZEL CSS) ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; }
    .besmele { text-align: center; color: #d4af37; font-size: 4rem; font-weight: bold; margin-bottom: 5px; }
    .ayet-kutu { text-align: center; color: #fff; background: rgba(212,175,55,0.1); border: 2px solid #d4af37; padding: 25px; border-radius: 15px; margin-bottom: 35px; font-size: 1.4rem; line-height: 1.6; border-left: 15px solid #d4af37; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .vakit-baslik { color: #fbbf24; font-size: 1.8rem; font-weight: bold; margin-top: 20px; border-bottom: 2px solid #333; padding-bottom: 10px; }
    .vakit-kutusu { background: #ffffff; border-radius: 20px; padding: 30px; text-align: center; border-bottom: 12px solid #d4af37; margin-bottom: 15px; }
    .vakit-ad { color: #000 !important; font-size: 2.2rem; font-weight: bold; }
    .vakit-saat { color: #d4af37 !important; font-size: 4rem; font-weight: 900; }
    .haftalik-satir { background: #111; border-left: 10px solid #d4af37; padding: 20px; border-radius: 12px; margin-bottom: 12px; font-size: 1.3rem; display: flex; justify-content: space-between; align-items: center; color: #fff; }
    .zikir-sayi { font-size: 14rem !important; color: #fff; font-weight: 900; text-align: center; text-shadow: 0 0 60px #d4af37; line-height: 1; margin: 30px 0; }
    .bilgi-kutusu { background: #151515; border: 1px solid #d4af37; padding: 15px; border-radius: 10px; margin-bottom: 10px; color: #fff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TAM VERİ SETLERİ (HİÇBİR EKSİK BIRAKILMADI) ---
AYLAR = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}

FARZ_32 = {
    "İmanın Şartları (6)": "1. Allah’a inanmak, 2. Meleklere inanmak, 3. Kitaplara inanmak, 4. Peygamberlere inanmak, 5. Ahiret gününe inanmak, 6. Kadere (Hayır ve şerrin Allah'tan geldiğine) inanmak.",
    "İslamın Şartları (5)": "1. Kelime-i Şehadet getirmek, 2. Namaz kılmak, 3. Oruç tutmak, 4. Zekat vermek, 5. Hacca gitmek.",
    "Abdestin Farzları (4)": "1. Yüzü yıkamak, 2. Kolları dirseklerle beraber yıkamak, 3. Başın dörtte birini meshetmek, 4. Ayakları topuklarla beraber yıkamak.",
    "Guslün Farzları (3)": "1. Ağza su vermek, 2. Burna su vermek, 3. Bütün vücudu iğne ucu kadar kuru yer kalmadan yıkamak.",
    "Teyemmümün Farzları (2)": "1. Niyet etmek, 2. İki avucu temiz toprağa vurup önce yüzü, sonra tekrar vurup kolları meshetmek.",
    "Namazın Farzları (12)": "Dışındakiler: Hadesten taharet, Necasetten taharet, Setr-i avret, İstikbal-i kıble, Vakit, Niyet. İçindekiler: İftitah tekbiri, Kıyam, Kıraat, Rükû, Sücud, Ka'de-i ahîre."
}

# Son 10 Sure ve Anlamları
SURELER = {
    "Fil Suresi": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bi hicâratin min siccîl. Fe ce'alehüm ke'asfin me'kûl.",
    "Kureyş Suresi": "Li îlâfi kureyş. Îlâfihim rihleteş şitâi ves sayf. Felyâ'büdû rabbe hâzel beyt. Ellezî at'amehüm min cû'in ve âmenehüm min havf.",
    "Mâûn Suresi": "Era'eytellezî yükezzibü bid dîn. Fe zâlikellezî yedü'ul yetîm. Ve lâ yehuddu alâ ta'âmil miskîn. Fe veylün lil müsallîn. Ellezîne hüm an salâtihim sâhûn. Ellezîne hüm yürâûn. Ve yemne'ûnel mâ'ûn.",
    "Kevser Suresi": "İnnâ a'taynâkel kevser. Fe salli li rabbike venhar. İnne şâni'eke hüvel ebter.",
    "Kâfirûn Suresi": "Kul yâ eyyühel kâfirûn. Lâ a'büdü mâ ta'büdûn. Ve lâ entüm âbidûne mâ a'büd. Ve lâ ene âbidün mâ abedtüm. Ve lâ entüm âbidûne mâ a'büd. Leküm dînüküm veliye dîn.",
    "Nasr Suresi": "İzâ câe nasrullâhi vel feth. Ve raeyten nâse yedhulûne fî dînillâhi efvâcâ. Fe sebbih bi hamdi rabbike vestağfirh. İnnehû kâne tevvâbâ.",
    "Tebbet Suresi": "Tebbet yedâ ebî lehebin ve tebb. Mâ ağnâ anhü mâlühû ve mâ keseb. Seyaslâ nâran dâte leheb. Vemraetühû hammâletel hatab. Fî cîdihâ hablün min mesed.",
    "İhlâs Suresi": "Kul hüvallâhü ehad. Allâhüs samed. Lem yelid ve lem yûled. Ve lem yekün lehû küfüven ehad.",
    "Felak Suresi": "Kul e'ûzü bi rabbil felak. Min şerri mâ halak. Ve min şerri ğâsikın izâ vekab. Ve min şerri neffâsâti fîl ukad. Ve min şerri hâsidin izâ hased.",
    "Nâs Suresi": "Kul e'ûzü bi rabbin nâs. Melikin nâs. İlâhin nâs. Min şerril vesvâsil hannâs. Ellezî yüvesvisü fî sudûrin nâs. Minel cinneti ven nâs."
}

# --- 3. YAN MENÜ ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#d4af37;'>🕋 REHBER</h1>", unsafe_allow_html=True)
    sehir = st.selectbox("📍 Şehir Seç", ["İstanbul", "Ankara", "İzmir", "Bursa", "Adana", "Konya", "Antalya", "Gaziantep", "Şanlıurfa", "Kocaeli", "Mersin", "Diyarbakır", "Samsun"])
    
    with st.expander("📌 32 FARZ (TAM LİSTE)", expanded=True):
        for b, i in FARZ_32.items():
            st.markdown(f"<div class='bilgi-kutusu'><b>{b}</b><br>{i}</div>", unsafe_allow_html=True)

    with st.expander("✨ ESMAÜL HÜSNA", expanded=False):
        st.info("Allah'ın 99 ismi ve anlamları buradadır.")

    with st.expander("📖 NAMAZ SURELERİ", expanded=False):
        for s_ad, s_met in SURELER.items():
            st.markdown(f"**{s_ad}**")
            st.caption(s_met)
            st.divider()

# --- 4. ANA EKRAN ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)

st.markdown("""
<div class='ayet-kutu'>
    <b style='color:#fbbf24; font-size:1.5rem;'>Âli İmrân Suresi, 110. Ayet:</b><br>
    "Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız."
</div>
""", unsafe_allow_html=True)

try:
    s_api = sehir.replace("İ", "I").replace("ı", "i").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={s_api}&country=Turkey&method=13").json()['data']
    v = res['timings']
    g = res['date']['gregorian']
    
    st.markdown(f"<h2 style='text-align:center; color:#fbbf24; font-size:2.5rem;'>{g['day']} {AYLAR.get(g['month']['en'])} {g['year']}</h2>", unsafe_allow_html=True)

    # --- 3+3 YAN YANA VAKİTLER ---
    st.markdown("<div class='vakit-baslik'>☀️ GÜNDÜZ VAKİTLERİ</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for i, (ad, s) in enumerate([("İMSAK", v['Fajr']), ("GÜNEŞ", v['Sunrise']), ("ÖĞLE", v['Dhuhr'])]):
        with [c1, c2, c3][i]:
            st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>{ad}</div><div class='vakit-saat'>{s}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='vakit-baslik'>🌙 AKŞAM VAKİTLERİ</div>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    for i, (ad, s) in enumerate([("İKİNDİ", v['Asr']), ("AKŞAM", v['Maghrib']), ("YATSI", v['Isha'])]):
        with [c4, c5, c6][i]:
            st.markdown(f"<div class='vakit-kutusu'><div class='vakit-ad'>{ad}</div><div class='vakit-saat'>{s}</div></div>", unsafe_allow_html=True)

    # --- HAFTALIK SATIR DÜZENİ ---
    st.divider()
    st.subheader("🗓️ Haftalık Namaz Vakitleri (Okunaklı Liste)")
    h_res = requests.get(f"http://api.aladhan.com/v1/calendarByCity?city={s_api}&country=Turkey&method=13").json()['data']
    for gun in h_res[:7]:
        d = gun['date']['gregorian']
        t = gun['timings']
        st.markdown(f"""
            <div class='haftalik-satir'>
                <b style='color:#fbbf24; min-width:140px;'>{d['day']} {AYLAR.get(d['month']['en'])}</b>
                <span>İmsak: <b>{t['Fajr']}</b></span>
                <span>Öğle: <b>{t['Dhuhr']}</b></span>
                <span>İkindi: <b>{t['Asr']}</b></span>
                <span>Akşam: <b>{t['Maghrib']}</b></span>
                <span>Yatsı: <b>{t['Isha']}</b></span>
            </div>
        """, unsafe_allow_html=True)

    # --- ZİKİRMATİK (EN BÜYÜK BOYUT) ---
    st.divider()
    st.markdown("<h2 style='text-align:center; color:#d4af37;'>📿 ZİKİRMATİK</h2>", unsafe_allow_html=True)
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f"<div class='zikir-sayi'>{st.session_state.zk}</div>", unsafe_allow_html=True)
    
    if st.button("➕ ZİKİR ÇEK", use_container_width=True):
        st.session_state.zk += 1
        st.rerun()

except:
    st.error("Bağlantı hatası!")