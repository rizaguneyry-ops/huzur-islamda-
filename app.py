import streamlit as st
import requests
from datetime import datetime, timedelta
import time
import random
import pandas as pd

# Kütüphane Güvenlik Kontrolü
try:
    import plotly.express as px
except ImportError:
    st.error("Kritik Hata: 'plotly' kütüphanesi eksik. Lütfen requirements.txt dosyasına ekleyin.")

# --- 1. PRESTİJ TASARIM & ATMOSFER ---
st.set_page_config(page_title="Manevi Muhafız v200", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Cinzel:wght@700&family=Montserrat:wght@300;600&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.92)), 
        url("https://images.unsplash.com/photo-1507598641400-ec3536ba81bc?q=80&w=2070");
        background-size: cover; background-attachment: fixed; color: #fdf5e6;
        font-family: 'Montserrat', sans-serif;
    }
    
    .besmele { 
        font-family: 'Amiri', serif; text-align: center; font-size: 5rem; 
        color: #d4af37; margin-bottom: 5px; text-shadow: 0 0 35px rgba(212,175,55,0.6); 
    }
    
    .ayet-container {
        background: rgba(212, 175, 55, 0.07); border: 2px double #d4af37;
        padding: 30px; border-radius: 20px; text-align: center; margin: 10px auto;
        max-width: 1000px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .yuvarlak-sayac { 
        width: 400px; height: 400px; border-radius: 50%; border: 15px double #d4af37; 
        margin: 25px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: radial-gradient(circle, #1a1a1a 0%, #000 100%);
        box-shadow: 0 0 120px rgba(212,175,55,0.4);
    }

    .vakit-kart { 
        background: #ffffff; color: #1a1a1a; border-radius: 18px; padding: 20px; 
        text-align: center; border-bottom: 10px solid #d4af37; font-weight: bold; 
        transition: 0.4s; box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .vakit-kart:hover { transform: scale(1.05); }
    .vakit-saat { font-size: 2rem; color: #b8860b; font-weight: 900; }
    
    .sidebar-title { color: #d4af37; text-align: center; font-family: 'Cinzel', serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ MERKEZİ (SIFIR EKSİK - TAM LİSTE) ---
ESMALAR = {
    "Allah": "Eşi benzeri olmayan, tek ilah.", "Er-Rahmân": "Dünyada her canlıya merhamet eden.", "Er-Rahîm": "Ahirette müminlere rahmet eden.", "El-Melik": "Mülkün ve kainatın gerçek sahibi.", "El-Kuddûs": "Her türlü eksiklikten uzak, tertemiz.", "Es-Selâm": "Esenlik veren, selamete çıkaran.", "El-Mü'min": "Güven veren, vaadine güvenilen.", "El-Müheymin": "Gözeten, koruyan ve hükmü altına alan.", "El-Azîz": "İzzet sahibi, mağlup edilmesi imkansız.", "El-Cebbâr": "Dilediğini yapan, yaraları saran.", "El-Mütekebbir": "Büyüklükte eşi benzeri olmayan.", "El-Hâlık": "Her şeyi yoktan var eden, yaratan.", "El-Bâri": "Kusursuz ve uyumlu yaratan.", "El-Musavvir": "Her şeye bir şekil ve özellik veren.", "El-Gaffâr": "Günahları çokça bağışlayan.", "El-Kahhâr": "Her şeye galip gelen, kahreden.", "El-Vehhâb": "Karşılıksız veren, hibe eden.", "Er-Razzâk": "Rızık veren, ihtiyacı karşılayan.", "El-Fettâh": "Kapıları açan, her şeyi çözen.", "El-Alîm": "Her şeyi en ince ayrıntısıyla bilen.", "El-Kâbıd": "Dilediğine rızkı daraltan, ruhları alan.", "El-Bâsıt": "Rızkı genişleten, ferahlık veren.", "El-Hâfıd": "Kafirleri alçaltan.", "Er-Râfi": "Müminleri yükselten.", "El-Muiz": "İzzet veren, aziz kılan.", "El-Müzil": "Zelil kılan, alçaltan.", "Es-Semî": "Her şeyi işiten.", "El-Basîr": "Her şeyi gören.", "El-Hakem": "Mutlak hakim, hüküm veren.", "El-Adl": "Tam adaletli olan.", "El-Latîf": "Lütuf sahibi, her şeye nüfuz eden.", "El-Habîr": "Her şeyden haberdar olan.", "El-Halîm": "Cezalandırmada acele etmeyen.", "El-Azîm": "Pek yüce ve azametli.", "El-Gafûr": "Affı ve mağfireti bol.", "Eş-Şekûr": "Az amele çok sevap veren.", "El-Aliyy": "En yüce, en yüksek.", "El-Kebîr": "En büyük, ulu.", "El-Hafîz": "Her şeyi koruyup muhafaza eden.", "El-Mukît": "Her canlının azığını veren.", "El-Hasîb": "Hesaba çeken, kafi gelen.", "El-Celîl": "Celalet ve haşmet sahibi.", "El-Kerîm": "Çok cömert, keremi bol.", "Er-Rakîb": "Her an gözeten, kontrol eden.", "El-Mucîb": "Duaları kabul eden.", "El-Vâsi": "İlmi ve merhameti her şeyi kuşatan.", "El-Hakîm": "Her işi hikmetli olan.", "El-Vedûd": "Kullarını seven ve sevilen.", "El-Mecîd": "Şanı yüce ve keremi bol.", "El-Bâis": "Ölüleri dirilten, peygamber gönderen.", "Eş-Şehîd": "Her şeye şahit olan.", "El-Hakk": "Varlığı hiç değişmeyen, hakikat.", "El-Vekîl": "Kendisine güvenilen, işleri yöneten.", "El-Kaviyy": "Pek güçlü.", "El-Metîn": "Sarsılmaz derecede kudretli.", "El-Veliyy": "Müminlerin dostu ve yardımcısı.", "El-Hamîd": "Her türlü övgüye layık olan.", "El-Muhsî": "Her şeyin sayısını bilen.", "El-Mübdî": "Maddesiz ve örneksiz yaratan.", "El-Muîd": "Öldükten sonra tekrar dirilten.", "El-Muhyî": "Can veren, hayat bağışlayan.", "El-Mümît": "Ölümü yaratan, öldüren.", "El-Hayy": "Ezeli ve ebedi diri olan.", "El-Kayyûm": "Kainatı ayakta tutan.", "El-Vâcid": "İstediğini istediği an bulan.", "El-Mâcid": "Kadri ve şanı büyük olan.", "El-Vâhid": "Zatında ve sıfatlarında tek olan.", "Es-Samed": "Hiçbir şeye muhtaç olmayan.", "El-Kâdir": "Dilediğini yapmaya gücü yeten.", "El-Muktedir": "Kuvvet ve kudret sahipleri üzerinde hüküm süren.", "El-Mukaddim": "Dilediğini öne alan.", "El-Muahhir": "Dilediğini geriye bırakan.", "El-Evvel": "Varlığının başlangıcı olmayan.", "El-Âhir": "Varlığının sonu olmayan.", "Ez-Zâhir": "Varlığı açık olan.", "El-Bâtın": "Zatının mahiyeti gizli olan.", "El-Vâlî": "Kainatı yöneten.", "El-Müteâlî": "Eksikliklerden yüce olan.", "El-Berr": "İyilik ve ihsanı bol olan.", "Et-Tevvâb": "Tövbeleri kabul eden.", "El-Müntakim": "Suçluları cezalandıran.", "El-Afüvv": "Affı bol olan.", "Er-Raûf": "Çok şefkatli.", "Mâlikü’l-Mülk": "Mülkün ebedi sahibi.", "Zü’l-Celâli ve’l-İkrâm": "Celal ve ikram sahibi.", "El-Muksit": "Adaletle hükmeden.", "El-Câmi": "Her şeyi bir araya toplayan.", "El-Ganî": "Çok zengin, kimseye muhtaç olmayan.", "El-Mugnî": "Dilediğini zengin eden.", "El-Mâni": "Dilediğine engel olan.", "Ed-Dârr": "Elem ve zarar verenleri yaratan.", "En-Nâfi": "Fayda veren şeyleri yaratan.", "En-Nûr": "Alemleri nurlandıran.", "El-Hâdî": "Hidayet veren.", "El-Bedî": "Eşsiz ve örneksiz yaratan.", "El-Bâkî": "Varlığı ebedi olan.", "El-Vâris": "Her şeyin gerçek varisi olan.", "Er-Reşîd": "Doğru yolu gösteren.", "Es-Sabûr": "Çok sabırlı olan."
}

SURELER = {
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

# --- 3. AKILLI HAFIZA ---
if 'exp' not in st.session_state: st.session_state.exp = 0
if 'history_df' not in st.session_state:
    st.session_state.history_df = pd.DataFrame({'Gün': ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'], 'Puan': [5, 4, 5, 5, 4, 5, 5]})

# --- 4. YARDIMCI SİSTEMLER ---
def zaman_ayarla(s, d=-1):
    h, m = map(int, s.split(':'))
    return (datetime(2000, 1, 1, h, m) + timedelta(minutes=d)).strftime("%H:%M")

@st.cache_data(ttl=3600)
def get_vakit_api(city):
    try:
        r = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Turkey&method=13")
        return r.json()['data']
    except: return None

# --- 5. SIDEBAR (MANEVİ PANEL) ---
with st.sidebar:
    st.markdown("<h1 class='sidebar-title'>⚜️ Manevi Makam</h1>", unsafe_allow_html=True)
    lvl = st.session_state.exp // 100
    st.metric("Mertebe", f"Kadem-i Şerif {lvl}")
    st.progress(min((st.session_state.exp % 100) / 100, 1.0))
    
    sehir = st.selectbox("📍 Şehriniz", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana"])
    
    if st.button("📿 Zikir Çek (+10 Nur Puanı)"):
        st.session_state.exp += 10; st.balloons(); st.rerun()
    
    with st.expander("✨ 99 Esmaül Hüsna (Eksiksiz)"):
        for k, v in ESMALAR.items(): st.write(f"**{k}**: {v}")
    
    with st.expander("📖 10 Sure ve Mealleri (Eksiksiz)"):
        for k, v in SURELER.items(): st.write(f"**{k}**: {v}")

# --- 6. ANA EKRAN (PROFESYONEL DÜZEN) ---
v_data = get_vakit_api(sehir)
tr_now = datetime.utcnow() + timedelta(hours=3)

if v_data:
    # BESMELE VE AYET-İ KERİME
    st.markdown("<div class='besmele'>بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='ayet-container'>
        <h3 style='color:#d4af37; margin-bottom:15px; font-family:Cinzel;'>📖 Âli İmrân Suresi - 110. Ayet</h3>
        <p style='font-size:1.3rem; line-height:1.7; font-style: italic;'>
        "Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; marufu emreder, münkerden nehyedersiniz ve Allah'a inanırsınız..."
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1 Dakika Geri Alınmış Vakitler
    v_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    v_lbls = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
    v_times = [zaman_ayarla(v_data['timings'][k]) for k in v_keys]

    cols = st.columns(6)
    for i, (l, t) in enumerate(zip(v_lbls, v_times)):
        cols[i].markdown(f"<div class='vakit-kart'>{l}<br><span class='vakit-saat'>{t}</span></div>", unsafe_allow_html=True)

    # HAFTALIK GRAFİK
    with st.expander("📊 Haftalık Manevi İstikrar Raporum"):
        fig = px.area(st.session_state.history_df, x='Gün', y='Puan', markers=True, color_discrete_sequence=['#d4af37'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    # NAMAZ SORGUSU (Gerektiğinde Görünür)
    for i, t_str in enumerate(v_times):
        h, m = map(int, t_str.split(':'))
        v_dt = tr_now.replace(hour=h, minute=m, second=0)
        if v_dt + timedelta(minutes=30) < tr_now < v_dt + timedelta(minutes=105):
            st.markdown(f"<div style='border:2px solid #d4af37; padding:20px; border-radius:15px; text-align:center;'>", unsafe_allow_html=True)
            st.subheader(f"🛡️ {v_lbls[i]} Namazı Vakti")
            st.write("Bu vaktin nurundan nasiplendin mi?")
            c1, c2 = st.columns(2)
            if c1.button("✅ Elhamdülillah Kıldım"):
                st.session_state.exp += 50
                st.session_state.history_df.iloc[tr_now.weekday(), 1] = min(5, st.session_state.history_df.iloc[tr_now.weekday(), 1] + 1)
                st.balloons(); st.rerun()
            if c2.button("❌ Henüz Değil"):
                st.warning("Haydi dostum, vaktin bereketi kaçmadan seccadeye!"); time.sleep(2); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # CANLI SAYAÇ & MEKKE EZANI
    counter_area = st.empty()
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
            st.toast("📣 EZAN VAKTİ!", icon="🕌")
            time.sleep(10); st.rerun()

        h, m, s = diff // 3600, (diff % 3600) // 60, diff % 60
        status_msg = "Abdest alıp huzura hazırlan..." if diff < 600 else "Kalbin her an O'nunla olsun."
        
        counter_area.markdown(f"""<div class='yuvarlak-sayac'>
            <div style='color:#d4af37; font-size:1.4rem; font-family:Cinzel;'>{v_lbls[idx].upper()} VAKTİNE</div>
            <div style='font-size:5.5rem; font-weight:bold;'>{h:02d}:{m:02d}:{s:02d}</div>
            <div style='color:#00e676; font-size:1.1rem; margin-top:15px; font-weight:bold;'>{status_msg}</div>
        </div>""", unsafe_allow_html=True)
        time.sleep(1)