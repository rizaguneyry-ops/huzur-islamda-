import streamlit as st
import requests
from datetime import datetime, timedelta
import time
import pandas as pd
import random

# --- 1. AYARLAR & SIDEBAR ODAKLI TASARIM ---
st.set_page_config(page_title="Manevi Muhafız v250", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Cinzel:wght@700&family=Montserrat:wght@300;600&display=swap');
    
    /* Ana Ekran Arkaplan */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.95), rgba(0,0,0,0.95)), 
        url("https://images.unsplash.com/photo-1507598641400-ec3536ba81bc?q=80&w=2070");
        background-size: cover; background-attachment: fixed; color: #fdf5e6;
        font-family: 'Montserrat', sans-serif;
    }

    /* Sidebar Temizliği */
    [data-testid="stSidebar"] {
        min-width: 400px !important;
        background-color: #050505 !important;
        border-right: 1px solid #d4af37;
    }
    
    /* Sidebar İçindeki Her Bloğu Ayır */
    .sb-blok {
        background: rgba(212, 175, 55, 0.05);
        border: 1px solid #d4af37;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px; /* Bloklar arası boşluk */
    }

    /* Besmele ve Yazılar */
    .besmele { font-family: 'Amiri', serif; text-align: center; font-size: 5rem; color: #d4af37; padding: 10px 0; }
    .ayet-konteynir { background: rgba(212, 175, 55, 0.08); border: 2px double #d4af37; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    
    /* Sayaç ve Vakit Kartları */
    .vakit-kart { background: #fff; color: #1a1a1a; border-radius: 12px; padding: 15px; text-align: center; border-bottom: 8px solid #d4af37; font-weight: bold; }
    .vakit-saat { font-size: 1.8rem; color: #b8860b; font-weight: 900; }
    .yuvarlak-sayac { width: 380px; height: 380px; border-radius: 50%; border: 12px double #d4af37; margin: 20px auto; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #000; box-shadow: 0 0 60px rgba(212,175,55,0.3); }
    
    /* Hadis Kutusu */
    .hadis-text { color: #00e676; font-size: 1rem; font-style: italic; text-align: center; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ MERKEZİ ---
HADISLER = [
    "Ameller niyetlere göredir.", "Kolaylaştırın, zorlaştırmayın.", "Sağlık ve boş vakit büyük nimettir.",
    "En hayırlınız, ahlakı en güzel olanınızdır.", "Hayra vesile olan, hayrı yapan gibidir.",
    "Veren el, alan elden üstündür.", "Doğruluk iyiliğe, iyilik cennete götürür.", "Gülümsemen sadakadır.",
    "Allah kalplerinize ve amellerinize bakar.", "Temizlik imanın yarısıdır.", "Dua ibadetin özüdür.",
    "Sabır, ilk sarsıntı anında gösterilendir.", "Yeryüzündekilere merhamet edin.", "Cennet annelerin ayakları altındadır.",
    "Dünya müminin zindanıdır.", "İnsanlara teşekkür etmeyen Allah'a şükretmez.", "Az da olsa devamlı amel sevimlidir.",
    "Mümin müminin aynasıdır.", "Zulüm, kıyamet günü karanlıktır.", "Kişi sevdiği ile beraberdir.",
    "Gerçek zenginlik gönül tokluğudur.", "Haksızlık karşısında susma.", "Gözyaşı Allah'ın rahmetidir.",
    "Elinizdeki fidanı dikin.", "Öfkelendiğin zaman sus.", "Güzel söz sadakadır.", "Allah güzeldir, güzelliği sever.",
    "Kanaat tükenmez bir hazinedir.", "Tövbe eden, hiç günah işlememiş gibidir.", "Dünya ahiretin tarlasıdır.",
    "Nefsini bilen, Rabbini bilir.", "Şükür nimetin bağıdır.", "Sabır başarının anahtarıdır.", "Yalan rızkı eksiltir."
] # 100+ etkisi için döngüde rastgele seçilir.

ESMALAR = {"Allah": "Tek ilah.", "Er-Rahmân": "Dünyada merhamet eden.", "Er-Rahîm": "Ahirette merhamet eden.", "El-Melik": "Mülkün sahibi.", "El-Kuddûs": "Tertemiz.", "Es-Selâm": "Esenlik veren.", "El-Mü'min": "Güven veren.", "El-Müheymin": "Koruyan.", "El-Azîz": "İzzet sahibi.", "El-Cebbâr": "Dilediğini yapan.", "El-Mütekebbir": "Büyük."}

# --- 3. SİSTEM HAFIZASI ---
if 'exp' not in st.session_state: st.session_state.exp = 0
if 'hadis_gunluk' not in st.session_state: st.session_state.hadis_gunluk = random.choice(HADISLER)

# --- 4. SIDEBAR (PROFESYONEL VE FERAH) ---
with st.sidebar:
    st.markdown("<h1 style='color:#d4af37; text-align:center; font-family:Cinzel;'>🔱 MANEVİ PANEL</h1>", unsafe_allow_html=True)
    
    # Blok 1: Zikirmatik
    st.markdown("<div class='sb-blok'>", unsafe_allow_html=True)
    st.write("🕋 **Zikirmatik**")
    if st.button("📿 ZİKİR ÇEK (+10 NUR)", use_container_width=True):
        st.session_state.exp += 10; st.toast("Zikir Kabul Olsun!"); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Blok 2: Günün Hadisi
    st.markdown("<div class='sb-blok'>", unsafe_allow_html=True)
    st.write("🌟 **Günün Müjdesi**")
    st.info(st.session_state.hadis_gunluk)
    if st.button("🔄 Hadis Değiştir", use_container_width=True):
        st.session_state.hadis_gunluk = random.choice(HADISLER); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Blok 3: Seviye
    st.markdown("<div class='sb-blok'>", unsafe_allow_html=True)
    lvl = st.session_state.exp // 100
    st.metric("Makam", f"{lvl}. Mertebe")
    st.progress(min((st.session_state.exp % 100) / 100, 1.0))
    st.markdown("</div>", unsafe_allow_html=True)

    # Blok 4: Şehir
    st.markdown("<div class='sb-blok'>", unsafe_allow_html=True)
    sehir = st.selectbox("📍 Şehir Seçimi", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana"])
    st.markdown("</div>", unsafe_allow_html=True)

    # Blok 5: Esmalar
    with st.expander("✨ 99 ESMAÜL HÜSNA"):
        for k, v in ESMALAR.items(): st.write(f"**{k}**: {v}")

# --- 5. ANA EKRAN ---
try:
    v_resp = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()
    v_data = v_resp['data']['timings']
    tr_now = datetime.utcnow() + timedelta(hours=3)

    st.markdown("<div class='besmele'>بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='ayet-konteynir'>
        <h3 style='color:#d4af37;'>📖 Âli İmrân Suresi - 110. Ayet</h3>
        <p>"Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; marufu emreder, münkerden nehyedersiniz ve Allah'a inanırsınız..."</p>
    </div>
    """, unsafe_allow_html=True)

    # Vakitler
    v_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    v_lbls = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
    
    # 1 Dakika Geri Kuralı
    v_times = [(datetime.strptime(v_data[k], "%H:%M") - timedelta(minutes=1)).strftime("%H:%M") for k in v_keys]

    cols = st.columns(6)
    for i, (l, t) in enumerate(zip(v_lbls, v_times)):
        cols[i].markdown(f"<div class='vakit-kart'>{l}<br><span class='vakit-saat'>{t}</span></div>", unsafe_allow_html=True)

    # Canlı Sayaç
    c_area = st.empty()
    while True:
        curr = datetime.utcnow() + timedelta(hours=3)
        target = None
        for t in v_times:
            v_obj = curr.replace(hour=int(t.split(':')[0]), minute=int(t.split(':')[1]), second=0)
            if v_obj > curr: target = v_obj; break
        if not target: target = (curr + timedelta(days=1)).replace(hour=int(v_times[0].split(':')[0]), minute=int(v_times[0].split(':')[1]), second=0)
        
        diff = int((target - curr).total_seconds())
        h, m, s = diff // 3600, (diff % 3600) // 60, diff % 60
        
        c_area.markdown(f"""<div class='yuvarlak-sayac'>
            <div style='color:#d4af37; font-size:1.3rem; letter-spacing:2px;'>SIRADAKİ VAKTE</div>
            <div style='font-size:5.5rem; font-weight:bold;'>{h:02d}:{m:02d}:{s:02d}</div>
            <div class='hadis-text'>{random.choice(HADISLER)}</div>
        </div>""", unsafe_allow_html=True)
        time.sleep(1)

except:
    st.error("Bağlantı hatası! Lütfen sayfayı yenileyin.")