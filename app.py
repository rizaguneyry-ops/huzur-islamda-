import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. AYARLAR ---
st.set_page_config(page_title="Huzur İslamda Pro", page_icon="🕋", layout="wide")

# --- 2. TÜRKÇE SÖZLÜKLER ---
AYLAR_TR = {
    "January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", 
    "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", 
    "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"
}

# --- 3. ESMAÜL HÜSNA (TAM LİSTE - 99 İSİM) ---
esma_99 = [
    ("Allah", "Eşi benzeri olmayan tek ilah."), ("Er-Rahmân", "Dünyada her kula merhamet eden."),
    ("Er-Rahîm", "Ahirette müminlere şefkat eden."), ("El-Melik", "Mülkün gerçek sahibi."),
    ("El-Kuddûs", "Hatadan münezzeh, tertemiz."), ("Es-Selâm", "Kullarını selamete çıkaran."),
    ("El-Mü'min", "Gönüllere iman veren."), ("El-Müheymin", "Her şeyi görüp gözeten."),
    ("El-Azîz", "İzzet ve galibiyet sahibi."), ("El-Cebbâr", "Dilediğini yapan ve yaptıran."),
    ("El-Mütekebbir", "Büyüklükte eşi olmayan."), ("El-Hâlık", "Yoktan var eden."),
    ("El-Bâri", "Kusursuz yaratan."), ("El-Musavvir", "Varlıklara suret veren."),
    ("El-Gaffâr", "Mağfireti bol olan."), ("El-Kahhâr", "Her şeye galip gelen."),
    ("El-Vehhâb", "Karşılıksız veren."), ("Er-Rezzâk", "Rızık veren."), ("El-Fettâh", "Kapıları açan."),
    ("El-Alîm", "Her şeyi en iyi bilen."), ("El-Kâbıd", "Sıkan, daraltan."), ("El-Bâsıt", "Açan, genişleten."),
    ("El-Hâfıd", "Dereceleri alçaltan."), ("Er-Râfi", "Dereceleri yükselten."), ("El-Muiz", "İzzet veren."),
    ("El-Müzil", "Zelil kılan."), ("Es-Semî", "Her şeyi işiten."), ("El-Basîr", "Her şeyi gören."),
    ("El-Hakem", "Mutlak hakim."), ("El-Adl", "Mutlak adil."), ("El-Latîf", "Lütfu bol olan."),
    ("El-Habîr", "Her şeyden haberdar."), ("El-Halîm", "Cezada acele etmeyen."), ("El-Azîm", "Pek yüce."),
    ("El-Gafûr", "Affı bol olan."), ("Eş-Şekûr", "Şükre karşılık veren."), ("El-Aliyy", "Yüceler yücesi."),
    ("El-Kebîr", "En büyük."), ("El-Hafîz", "Koruyucu."), ("El-Mukît", "Rızık ve güç veren."),
    ("El-Hasîb", "Hesaba çeken."), ("El-Celîl", "Azamet sahibi."), ("El-Kerîm", "Çok ikram eden."),
    ("Er-Rakîb", "Gözetleyen."), ("El-Mucîb", "Duaları kabul eden."), ("El-Vâsi", "İlmi geniş olan."),
    ("El-Hakîm", "Hikmet sahibi."), ("El-Vedûd", "Sevilmeye layık."), ("El-Mecîd", "Şerefi yüksek."),
    ("El-Bâis", "Ölüleri dirilten."), ("Eş-Şehîd", "Her şeye şahit."), ("El-Hakk", "Gerçeğin ta kendisi."),
    ("El-Vekîl", "Güvenilen."), ("El-Kaviyy", "Pek güçlü."), ("El-Metîn", "Sarsılmaz."),
    ("El-Veliyy", "Dost ve yardımcı."), ("El-Hamîd", "Övgüye layık."), ("El-Muhsî", "Sayan, bilen."),
    ("El-Mübdi", "Örneksiz yaratan."), ("El-Muîd", "Yeniden yaratan."), ("El-Muhyî", "Can veren."),
    ("El-Mümît", "Öldüren."), ("El-Hayy", "Daima diri."), ("El-Kayyûm", "Her şeyi ayakta tutan."),
    ("El-Vâcid", "İstediğini bulan."), ("El-Mâcid", "Şanı yüce."), ("El-Vâhid", "Tek olan."),
    ("Es-Samed", "Hiçbir şeye muhtaç olmayan."), ("El-Kâdir", "Gücü yeten."), ("El-Muktedir", "Dilediğini yapan."),
    ("El-Mukaddim", "Öne alan."), ("El-Muahhir", "Geriye bırakan."), ("El-Evvel", "İlk olan."),
    ("El-Âhir", "Son olan."), ("Ez-Zâhir", "Varlığı aşikar."), ("El-Bâtın", "Varlığı gizli."),
    ("El-Vâlî", "Kainatı yöneten."), ("El-Müteâlî", "Noksanlıktan yüce."), ("El-Berr", "İyiliği bol."),
    ("Et-Tevvâb", "Tövbeleri kabul eden."), ("El-Müntakim", "İntikam alan."), ("El-Afüvv", "Affeden."),
    ("Er-Raûf", "Çok şefkatli."), ("Mâlikü'l-Mülk", "Mülkün ebedi sahibi."), ("Zü'l-Celâli ve'l-İkrâm", "Celal ve ikram sahibi."),
    ("El-Muksit", "Adaletle hükmeden."), ("El-Câmi", "Toplayan."), ("El-Ganiyy", "Çok zengin."),
    ("El-Mugnî", "Zengin kılan."), ("El-Mâni", "Engelleyen."), ("Ed-Dârr", "Zarar veren."),
    ("En-Nâfi", "Fayda veren."), ("En-Nûr", "Nurlandıran."), ("El-Hâdî", "Hidayet veren."),
    ("El-Bedî", "Eşsiz yaratan."), ("El-Bâkî", "Ebedi olan."), ("El-Vâris", "Her şeyin varisi."),
    ("Er-Raşîd", "Doğru yolu gösteren."), ("Es-Sabûr", "Çok sabırlı.")
]

# --- 4. SON 10 SURE ---
son_on_sure = {
    "Fil Suresi": {"oku": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl...", "meal": "Rabbinin, fil sahiplerine ne yaptığını görmedin mi?..."},
    "Kureyş Suresi": {"oku": "Li îlâfi kureyş...", "meal": "Kureyş'e kolaylaştırıldığı için..."},
    "Mâûn Suresi": {"oku": "Era'eytellezî yükezzibü bid dîn...", "meal": "Dini yalanlayanı gördün mü?"},
    "Kevser Suresi": {"oku": "İnnâ a'taynâkel kevser...", "meal": "Şüphesiz biz sana Kevser'i verdik."},
    "Kâfirûn Suresi": {"oku": "Kul yâ eyyühel kâfirûn...", "meal": "De ki: Ey kâfirler! Ben sizin taptıklarınıza tapmam."},
    "Nasr Suresi": {"oku": "İzâ câe nasrullâhi vel feth...", "meal": "Allah'ın yardımı ve fetih geldiğinde..."},
    "Tebbet Suresi": {"oku": "Tebbet yedâ ebî lehebin ve tebb...", "meal": "Ebu Leheb'in iki eli kurusun!"},
    "İhlâs Suresi": {"oku": "Kul hüvallâhü ehad...", "meal": "De ki: O Allah birdir."},
    "Felak Suresi": {"oku": "Kul e'ûzü bi rabbil felak...", "meal": "De ki: Sabahın Rabbine sığınırım."},
    "Nâs Suresi": {"oku": "Kul e'ûzü bi rabbin nâs...", "meal": "De ki: İnsanların Rabbine sığınırım."}
}

sehirler_81 = ["Adana", "Adiyaman", "Afyonkarahisar", "Agri", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydin", "Balikesir", "Bartin", "Batman", "Bayburt", "Bilecik", "Bingol", "Bitlis", "Bolu", "Burdur", "Bursa", "Canakkale", "Cankiri", "Corum", "Denizli", "Diyarbakir", "Duzce", "Edirne", "Elazig", "Erzincan", "Erzurum", "Eskisehir", "Gaziantep", "Giresun", "Gumushane", "Hakkari", "Hatay", "Igdir", "Isparta", "Istanbul", "Izmir", "Kahramanmaras", "Karabuk", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kilis", "Kirikkale", "Kirklareli", "Kirsehir", "Kocaeli", "Konya", "Kutahya", "Malatya", "Manisa", "Mardin", "Mersin", "Mugla", "Mus", "Nevsehir", "Nigde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Sanliurfa", "Siirt", "Sinop", "Sivas", "Sirnak", "Tekirdag", "Tokat", "Trabzon", "Tunceli", "Usak", "Van", "Yalova", "Yozgat", "Zonguldak"]

# --- 5. CSS (MODERN SİYAH & ALTIN) ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; font-family: 'Segoe UI', sans-serif; }
    .besmele { text-align: center; color: #d4af37; font-size: 3.5rem; font-weight: bold; padding: 10px; }
    .ayet-box { text-align: center; color: #fff; background: rgba(212,175,55,0.1); border: 2px solid #d4af37; padding: 20px; border-radius: 15px; margin-bottom: 25px; }
    .vakit-kart { background: #fff; border-radius: 15px; padding: 20px; text-align: center; border-bottom: 8px solid #d4af37; box-shadow: 0 4px 10px rgba(255,255,255,0.1); }
    .vakit-ad { color: #000 !important; font-size: 1.6rem; font-weight: bold; }
    .vakit-saat { color: #d4af37 !important; font-size: 2.8rem; font-weight: 900; }
    .zikir-alan { background: #111; border: 4px solid #d4af37; border-radius: 30px; padding: 30px; text-align: center; margin-top: 30px; }
    .zikir-sayi { font-size: 11rem !important; color: #fff; font-weight: 900; text-shadow: 0 0 30px #d4af37; line-height: 1; }
    .tarih-banner { text-align: center; font-size: 1.8rem; color: #fbbf24; font-weight: bold; margin-bottom: 20px; }
    thead tr th { background-color: #d4af37 !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#d4af37;'>🕋 MENÜ</h1>", unsafe_allow_html=True)
    sehir = st.selectbox("📍 Şehir Seç", sehirler_81, index=sehirler_81.index("Istanbul"))
    
    with st.expander("✨ ESMAÜL HÜSNA (99 İSİM)", expanded=False):
        for ad, anlam in esma_99:
            st.write(f"**{ad}**: {anlam}")

    with st.expander("📖 SON 10 SURE", expanded=False):
        for s_ad, s_ic in son_on_sure.items():
            st.markdown(f"**{s_ad}**")
            st.caption(f"Okunuş: {s_ic['oku']}")
            st.write(f"Meal: {s_ic['meal']}")
            st.divider()

# --- 7. ANA EKRAN ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
st.markdown("<div class='ayet-box'><b>Günün Ayeti:</b> Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız.</div>", unsafe_allow_html=True)

try:
    # Veri Çekme
    url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
    data = requests.get(url).json()['data']
    v = data['timings']
    
    # Tarih Türkçeleştirme
    g = data['date']['gregorian']
    h = data['date']['hijri']
    ay_tr = AYLAR_TR.get(g['month']['en'], g['month']['en'])
    st.markdown(f"<div class='tarih-banner'>🗓️ {g['day']} {ay_tr} {g['year']} | 🌙 {h['day']} {h['month']['ar']} {h['year']}</div>", unsafe_allow_html=True)

    # VAKİT DİZİLİMİ (3 ÜST - 3 ALT)
    st.write("### ☀️ GÜNDÜZ VAKİTLERİ")
    c1, c2, c3 = st.columns(3)
    v_ust = [("İMSAK", v['Fajr']), ("GÜNEŞ", v['Sunrise']), ("ÖĞLE", v['Dhuhr'])]
    for i, (ad, saat) in enumerate(v_ust):
        [c1, c2, c3][i].markdown(f"<div class='vakit-kart'><div class='vakit-ad'>{ad}</div><div class='vakit-saat'>{saat}</div></div>", unsafe_allow_html=True)

    st.write("### 🌙 AKŞAM VAKİTLERİ")
    c4, c5, c6 = st.columns(3)
    v_alt = [("İKİNDİ", v['Asr']), ("AKŞAM", v['Maghrib']), ("YATSI", v['Isha'])]
    for i, (ad, saat) in enumerate(v_alt):
        [c4, c5, c6][i].markdown(f"<div class='vakit-kart'><div class='vakit-ad'>{ad}</div><div class='vakit-saat'>{saat}</div></div>", unsafe_allow_html=True)

    # PUSULA VE HAFTALIK
    st.divider()
    cp1, cp2 = st.columns([1, 2])
    with cp1:
        st.subheader("🧭 Kıble Pusulası")
        st.components.v1.html("""
            <div style="width:150px; height:150px; border:5px solid #d4af37; border-radius:50%; margin:auto; display:flex; align-items:center; justify-content:center; background:#111;">
                <div id="kabe" style="font-size:50px; transition:0.1s;">🕋</div>
            </div>
            <script>
                window.addEventListener('deviceorientation', function(e) {
                    var alpha = e.alpha;
                    if(alpha !== null) document.getElementById('kabe').style.transform = 'rotate('+(360-alpha)+'deg)';
                });
            </script>
        """, height=180)
    
    with cp2:
        st.subheader("🗓️ Haftalık Vakitler (Türkçe)")
        h_url = f"http://api.aladhan.com/v1/calendarByCity?city={sehir}&country=Turkey&method=13"
        h_data = requests.get(h_url).json()['data']
        today_d = datetime.now().day
        tablo = [[f"{d['date']['gregorian']['day']} {AYLAR_TR.get(d['date']['gregorian']['month']['en'])}", d['timings']['Fajr'], d['timings']['Dhuhr'], d['timings']['Asr'], d['timings']['Maghrib'], d['timings']['Isha']] for d in h_data if int(d['date']['gregorian']['day']) >= today_d][:7]
        st.table(tablo)

    # ZİKİRMATİK
    st.divider()
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown("<div class='zikir-alan'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#d4af37;'>📿 ZİKİRMATİK</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='zikir-sayi'>{st.session_state.zk}</div>", unsafe_allow_html=True)
    zc1, zc2 = st.columns(2)
    if zc1.button("➕ ZİKİR ÇEK (TİTREŞİMLİ)", use_container_width=True):
        st.session_state.zk += 1
        st.components.v1.html("<script>window.navigator.vibrate(60);</script>", height=0)
        st.rerun()
    if zc2.button("🔄 SIFIRLA", use_container_width=True):
        st.session_state.zk = 0
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

except:
    st.error("Bağlantı hatası.")