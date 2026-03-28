import streamlit as st
import requests
from datetime import datetime, timedelta
import time
import pandas as pd
import random

# Kütüphane Kontrolü
try:
    import plotly.express as px
except ImportError:
    st.error("Kritik Hata: 'plotly' kütüphanesi eksik.")

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Manevi Muhafız v230", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Cinzel:wght@700&family=Montserrat:wght@300;600&display=swap');
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.94), rgba(0,0,0,0.94)), 
        url("https://images.unsplash.com/photo-1507598641400-ec3536ba81bc?q=80&w=2070");
        background-size: cover; background-attachment: fixed; color: #fdf5e6;
        font-family: 'Montserrat', sans-serif;
    }
    .besmele { font-family: 'Amiri', serif; text-align: center; font-size: 5rem; color: #d4af37; padding: 15px 0; text-shadow: 0 0 30px #d4af37; }
    .ayet-konteynir { background: rgba(212, 175, 55, 0.08); border: 2px double #d4af37; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px; }
    .vakit-kart { background: #fff; color: #1a1a1a; border-radius: 12px; padding: 15px; text-align: center; border-bottom: 8px solid #d4af37; font-weight: bold; }
    .vakit-saat { font-size: 1.8rem; color: #b8860b; font-weight: 900; }
    .yuvarlak-sayac { width: 360px; height: 360px; border-radius: 50%; border: 12px double #d4af37; margin: 30px auto; display: flex; flex-direction: column; justify-content: center; align-items: center; background: radial-gradient(circle, #1a1a1a 0%, #000 100%); box-shadow: 0 0 80px rgba(212,175,55,0.4); }
    .hadis-box { background: rgba(0, 230, 118, 0.05); border-left: 5px solid #00e676; padding: 15px; border-radius: 8px; margin: 10px 0; font-style: italic; }
    [data-testid="stSidebar"] { min-width: 380px !important; background-color: #0b0d11; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DEV HADİS VERİ SETİ (100+ HADİS - KISALTMASIZ) ---
HADISLER = [
    "Ameller niyetlere göredir. Herkese niyet ettiği şey vardır.",
    "Kolaylaştırın, zorlaştırmayın; müjdeleyin, nefret ettirmeyin.",
    "İki nimet vardır ki insanların çoğu onlarda aldanmıştır: Sağlık ve boş vakit.",
    "Sizin en hayırlınız, ahlakı en güzel olanınızdır.",
    "Hayra vesile olan, hayrı yapan gibidir.",
    "Veren el, alan elden üstündür.",
    "Müslüman, elinden ve dilinden insanların emin olduğu kimsedir.",
    "Hiçbiriniz kendisi için istediğini kardeşi için de istemedikçe kamil mümin olamaz.",
    "Doğruluktan ayrılmayın. Çünkü doğruluk iyiliğe, iyilik de cennete götürür.",
    "Gülümsemen, sadakadır.",
    "Allah sizin suretlerinize ve mallarınıza bakmaz; kalplerinize ve amellerinize bakar.",
    "Temizlik imanın yarısıdır.",
    "Dua, ibadetin özüdür.",
    "Sabır, ilk sarsıntı anında gösterilendir.",
    "Bizi aldatan bizden değildir.",
    "Yeryüzündekilere merhamet edin ki göktekiler de size merhamet etsin.",
    "Güçlü kimse, güreşte galip gelen değil, öfke anında kendine hakim olandır.",
    "Cennet annelerin ayakları altındadır.",
    "Utanmak imandandır.",
    "İşçinin ücretini teri kurumadan veriniz.",
    "Dünya müminin zindanı, kafirin cennetidir.",
    "Nerede olursan ol Allah'tan kork. Kötülüğün peşinden iyilik yap ki onu silsin.",
    "İnsanlara teşekkür etmeyen, Allah'a da şükretmez.",
    "Komşusu açken tok yatan bizden değildir.",
    "Az da olsa devamlı olan amel Allah katında en sevimlidir.",
    "Mümin müminin aynasıdır.",
    "En faziletli cihad, zalim sultanın yanında adaleti söylemektir.",
    "Sıla-i rahim (akrabayı ziyaret) ömrü uzatır.",
    "Kim bir kulun ayıbını örterse, Allah da kıyamet günü onun ayıbını örter.",
    "Zulüm, kıyamet günü karanlıklardır.",
    "Hasetten sakının. Çünkü haset, ateşin odunu yediği gibi iyilikleri yer.",
    "Kişi sevdiği ile beraberdir.",
    "İyilik eskimez, günah unutulmaz, Allah ölmez. Dilediğini yap!",
    "Rızkının bollaşmasını isteyen akrabasını kollasın.",
    "Gerçek zenginlik mal çokluğu değil, gönül tokluğudur.",
    "Mümin, bir delikten iki defa ısırılmaz.",
    "Allah katında arkadaşların en hayırlısı, arkadaşına en hayırlı olandır.",
    "Birbirinize hediye verin ki birbirinizi sevesiniz.",
    "Haksızlık karşısında susan dilsiz şeytandır.",
    "Kendi nefsine hakim olan, insanların en güçlüsüdür.",
    "Sizin en hayırlınız hanımlarına karşı en iyi davrananınızdır.",
    "Her dinin bir ahlakı vardır, İslam'ın ahlakı da hayadır.",
    "Gözyaşı, Allah'ın rahmetidir.",
    "Kötü zandan sakının, çünkü zan sözlerin en yalanıdır.",
    "Elinizdeki fidanı kıyamet kopsa dahi dikin.",
    "Güneşin doğduğu en hayırlı gün Cuma günüdür.",
    "Sıkıntıya sabretmek, başarının anahtarıdır.",
    "Mümin yumuşak huylu ve naziktir.",
    "Zenginlik, ruhun zenginliğidir.",
    "Öfkelendiğin zaman sus.",
    "İlmi talep etmek her Müslümana farzdır.",
    "İman etmedikçe cennete giremezsiniz, birbirinizi sevmedikçe iman etmiş olmazsınız.",
    "Güzel söz sadakadır.",
    "Allah güzeldir, güzelliği sever.",
    "Dinin başı nasihattir.",
    "İnsanların en hayırlısı, insanlara faydalı olandır.",
    "Bir saat tefekkür, bir sene (nafile) ibadetten hayırlıdır.",
    "Sabır aydınlıktır.",
    "Kanaat tükenmez bir hazinedir.",
    "Affetmek izzeti artırır.",
    "Yalan rızkı eksiltir.",
    "Sadaka ömrü uzatır ve kötü ölümü engeller.",
    "Tövbe eden, hiç günah işlememiş gibidir.",
    "Gözü tok olan zengindir.",
    "Kibir, hakkı inkar etmek ve insanları küçük görmektir.",
    "Vakar müminin süsüdür.",
    "Her fani ölecek, her yeni eskiyecektir.",
    "Akıllı kişi, nefsini hesaba çeken ve ölüm sonrası için çalışandır.",
    "Yemeğin bereketi, yemekten önce ve sonra elleri yıkamaktır.",
    "Dünya ahiretin tarlasıdır.",
    "En faziletli sadaka, küskün olan iki kişinin arasını düzeltmektir.",
    "Alimin uykusu, cahilin ibadetinden üstündür.",
    "Gıybet, kardeşinin hoşlanmadığı şeyle onu anmandır.",
    "Borçlunun borcunu ertelemek sadakadır.",
    "Kalbinde zerre kadar kibir olan cennete giremez.",
    "Zandan kaçının, çünkü zan yalanın kendisidir.",
    "Misafir rızkı ile gelir, ev sahibinin günahlarını götürür.",
    "Selamı yayın, yemek yedirin ve gece herkes uyurken namaz kılın.",
    "Bir mülk küfürle ayakta kalır ama zulümle kalmaz.",
    "İyiliği gizlemek, Allah'ın rızasına daha yakındır.",
    "Hiddet her kötülüğün anahtarıdır.",
    "Müminin ferasetinden sakının, çünkü o Allah'ın nuruyla bakar.",
    "Allah bir kulu sevdiğinde onu imtihan eder.",
    "Zorlukla beraber bir kolaylık vardır.",
    "Hizmet eden, hizmet bulur.",
    "Haya bütünüyle hayırdır.",
    "Küçüğümüze merhamet etmeyen, büyüğümüze saygı gösteyen bizden değildir.",
    "Bir mümin, aç bir mümini doyurursa Allah da onu cennet meyveleriyle doyurur.",
    "İlim Çin'de de olsa ona talip olun.",
    "İki günü bir olan ziyandadır.",
    "Sözünde durmak imandandır.",
    "Cimrilikten sakının; çünkü o sizden öncekileri helak etmiştir.",
    "Kendi elinin emeğinden daha hayırlı bir yemek yoktur.",
    "Borç, gece dert gündüz zillettir.",
    "Kırk hadis ezberleyen, alimlerle haşrolunur.",
    "Kuran okuyun, çünkü o kıyamet günü şefaatçi olarak gelecektir.",
    "Nefsini bilen, Rabbini bilir.",
    "Allah yardımseverdir, yardımı sever.",
    "Müjdeleyin, nefret ettirmeyin.",
    "En hayırlı ev, içinde yetime ikram edilen evdir.",
    "Kalp kırmak, Kabe'yi yıkmaktan daha büyük günahtır.",
    "Her ağacın bir meyvesi vardır, kalbin meyvesi de çocuktur.",
    "Şükür, nimetin bağdır."
]

# --- 3. VERİ MERKEZİ & HAFIZA ---
ESMALAR = {"Allah": "Eşi benzeri olmayan.", "Er-Rahmân": "Dünyada merhamet eden.", "Er-Rahîm": "Ahirette merhamet eden.", "El-Melik": "Mülkün sahibi.", "El-Kuddûs": "Eksiklikten uzak.", "Es-Selâm": "Esenlik veren.", "El-Mü'min": "Güven veren.", "El-Müheymin": "Gözeten.", "El-Azîz": "İzzet sahibi.", "El-Cebbâr": "Yaraları saran.", "El-Mütekebbir": "En büyük.", "El-Hâlık": "Yaratan.", "El-Bâri": "Kusursuz yaratan.", "El-Musavvir": "Şekil veren.", "El-Gaffâr": "Bağışlayan.", "El-Kahhâr": "Galip gelen.", "El-Vehhâb": "Karşılıksız veren.", "Er-Razzâk": "Rızık veren.", "El-Fettâh": "Kapı açan.", "El-Alîm": "Her şeyi bilen.", "El-Kâbıd": "Sıkan.", "El-Bâsıt": "Açan.", "El-Hâfıd": "Alçaltan.", "Er-Râfi": "Yükselten.", "El-Muiz": "Aziz kılan.", "El-Müzil": "Alçaltan.", "Es-Semî": "İşiten.", "El-Basîr": "Gören.", "El-Hakem": "Hükmeden.", "El-Adl": "Adaletli.", "El-Latîf": "Lütfeden.", "El-Habîr": "Haberdar.", "El-Halîm": "Yumuşak.", "El-Azîm": "Yüce.", "El-Gafûr": "Affeden.", "Eş-Şekûr": "Mükafat veren.", "El-Aliyy": "Yüce.", "El-Kebîr": "Büyük.", "El-Hafîz": "Koruyan.", "El-Mukît": "Besleyen.", "El-Hasîb": "Hesap soran.", "El-Celîl": "Azametli.", "El-Kerîm": "Cömert.", "Er-Rakîb": "Gözeten.", "El-Mucîb": "Kabul eden.", "El-Vâsi": "İlmi geniş.", "El-Hakîm": "Hikmetli.", "El-Vedûd": "Seven.", "El-Mecîd": "Şanlı.", "El-Bâis": "Dirilten.", "Eş-Şehîd": "Şahit.", "El-Hakk": "Gerçek.", "El-Vekîl": "Güvenilen.", "El-Kaviyy": "Güçlü.", "El-Metîn": "Sarsılmaz.", "El-Veliyy": "Dost.", "El-Hamîd": "Övülen.", "El-Muhsî": "Sayan.", "El-Mübdî": "Başlatan.", "El-Muîd": "Döndüren.", "El-Muhyî": "Can veren.", "El-Mümît": "Öldüren.", "El-Hayy": "Diri.", "El-Kayyûm": "Ayakta tutan.", "El-Vâcid": "Bulan.", "El-Mâcid": "Şanlı.", "El-Vâhid": "Tek.", "Es-Samed": "Muhtaç olmayan.", "El-Kâdir": "Gücü yeten.", "El-Muktedir": "Kudretli.", "El-Muakdim": "Öne alan.", "El-Muahhir": "Geriye atan.", "El-Evvel": "İlk.", "El-Âhir": "Son.", "Ez-Zâhir": "Açık.", "El-Bâtın": "Gizli.", "El-Vâlî": "Yöneten.", "El-Müteâlî": "Yüce.", "El-Berr": "İyiliği bol.", "Et-Tevvâb": "Tövbe kabul eden.", "El-Müntakim": "Cezalandıran.", "El-Afüvv": "Affeden.", "Er-Raûf": "Şefkatli.", "Mâlikü’l-Mülk": "Mülk sahibi.", "Zü’l-Celâli ve’l-İkrâm": "Celal sahibi.", "El-Muksit": "Adil.", "El-Câmi": "Toplayan.", "El-Ganî": "Zengin.", "El-Mugnî": "Zengin eden.", "El-Mâni": "Engelleyen.", "Ed-Dârr": "Zarar veren.", "En-Nâfi": "Fayda veren.", "En-Nûr": "Nur.", "El-Hâdî": "Hidayet veren.", "El-Bedî": "Eşsiz.", "El-Bâkî": "Ebedi.", "El-Vâris": "Varis.", "Er-Reşîd": "Yol gösteren.", "Es-Sabûr": "Sabırlı."}

if 'exp' not in st.session_state: st.session_state.exp = 0
if 'h_index' not in st.session_state: st.session_state.h_index = random.randint(0, len(HADISLER)-1)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#d4af37; text-align:center;'>🔱 MANEVİ MUHAFIZ</h1>", unsafe_allow_width=True)
    
    # Günün Müjdesi (Hadis Bildirimi)
    st.markdown("<div class='sidebar-box'>", unsafe_allow_html=True)
    st.markdown(f"🌟 **GÜNÜN MÜJDESİ**")
    st.info(HADISLER[st.session_state.h_index])
    if st.button("🔄 Yeni Hadis Oku"):
        st.session_state.h_index = random.randint(0, len(HADISLER)-1)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Zikirmatik
    if st.button("📿 ZİKİR ÇEK (+10 NUR)", use_container_width=True):
        st.session_state.exp += 10; st.toast("Zikriniz kaydedildi."); st.rerun()
    
    lvl = st.session_state.exp // 100
    st.metric("Makam", f"{lvl}. Mertebe")
    st.progress(min((st.session_state.exp % 100) / 100, 1.0))
    
    sehir = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana"])
    
    with st.expander("✨ 99 ESMAÜL HÜSNA"):
        for k, v in ESMALAR.items(): st.write(f"**{k}**: {v}")

# --- 5. ANA EKRAN ---
v_data = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
tr_now = datetime.utcnow() + timedelta(hours=3)

st.markdown("<div class='besmele'>بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</div>", unsafe_allow_html=True)

st.markdown("""
<div class='ayet-konteynir'>
    <h3 style='color:#d4af37;'>📖 Âli İmrân Suresi - 110. Ayet</h3>
    <p>"Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; marufu emreder, münkerden nehyedersiniz ve Allah'a inanırsınız..."</p>
</div>
""", unsafe_allow_html=True)

# Vakitler (1 Dk Geri)
v_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
v_lbls = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
v_times = [(datetime.strptime(v_data['timings'][k], "%H:%M") - timedelta(minutes=1)).strftime("%H:%M") for k in v_keys]

cols = st.columns(6)
for i, (l, t) in enumerate(zip(v_lbls, v_times)):
    cols[i].markdown(f"<div class='vakit-kart'>{l}<br><span class='vakit-saat'>{t}</span></div>", unsafe_allow_html=True)

# NAMAZ MOTİVASYONU
for i, t_str in enumerate(v_times):
    h, m = map(int, t_str.split(':'))
    v_dt = tr_now.replace(hour=h, minute=m, second=0)
    if v_dt < tr_now < v_dt + timedelta(minutes=90):
        st.success(f"🕌 {v_lbls[i]} Vakti İçerisindesin! Ruhuna bir iyilik yap.")
        if st.button("✅ Namazımı Kıldım (+50 EXP)"):
            st.session_state.exp += 50; st.balloons(); st.rerun()

# SAYAÇ
c_area = st.empty()
while True:
    anlik = datetime.utcnow() + timedelta(hours=3)
    target = None
    for t in v_times:
        v_o = anlik.replace(hour=int(t.split(':')[0]), minute=int(t.split(':')[1]), second=0)
        if v_o > anlik: target = v_o; break
    if not target: target = (anlik + timedelta(days=1)).replace(hour=int(v_times[0].split(':')[0]), minute=int(v_times[0].split(':')[1]), second=0)
    
    diff = int((target - anlik).total_seconds())
    if diff <= 0: st.rerun()
    
    h, m, s = diff // 3600, (diff % 3600) // 60, diff % 60
    c_area.markdown(f"""<div class='yuvarlak-sayac'>
        <div style='color:#d4af37; font-size:1.3rem;'>VAKTE KALAN</div>
        <div style='font-size:5.5rem; font-weight:bold;'>{h:02d}:{m:02d}:{s:02d}</div>
        <div class='hadis-box'>{HADISLER[random.randint(0, len(HADISLER)-1)]}</div>
    </div>""", unsafe_allow_html=True)
    time.sleep(1)