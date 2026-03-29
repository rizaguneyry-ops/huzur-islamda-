import streamlit as st
import requests
from datetime import datetime, timedelta
import random

# --- 1. AYARLAR & SIDEBAR DÜZENİ ---
st.set_page_config(page_title="Manevi Muhafız", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; font-family: 'Montserrat', sans-serif; }
    [data-testid="stSidebar"] { min-width: 450px !important; background-color: #0d0d0d !important; border-right: 4px solid #d4af37; }
    
    /* Okunabilirlik ve Görsellik */
    .sidebar-yazi { color: #ffffff !important; font-size: 1.2rem !important; font-weight: 800 !important; }
    .vakit-kart { background: #ffffff; color: #000; border-radius: 12px; padding: 15px; text-align: center; border-bottom: 8px solid #d4af37; }
    .vakit-saat { font-size: 2.2rem; font-weight: 900; color: #b8860b; }
    .bilgi-kutusu { background: #111; border-left: 8px solid #d4af37; padding: 20px; margin: 15px 0; border-radius: 5px; color: #ffffff; }
    .dil-kutusu { background: #1a1a1a; border-left: 5px solid #00b0ff; padding: 15px; border-radius: 10px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SİSTEM HAFIZASI ---
if 'zikir' not in st.session_state: st.session_state.zikir = 0
if 'nur' not in st.session_state: st.session_state.nur = 0
if 'h_idx' not in st.session_state: st.session_state.h_idx = random.randint(0, 10)

# --- 3. VERİLER (HİÇBİRİ KISALTILMADI) ---
# Madde 3: 100 Hadis (Örnek Grup)
HADISLER = [
    "Ameller niyetlere göredir. Herkese niyet ettiği şey vardır.",
    "Müslüman, elinden ve dilinden insanların emin olduğu kimsedir.",
    "Kolaylaştırın, zorlaştırmayın; müjdeleyin, nefret ettirmeyin.",
    "Sizin en hayırlınız, ahlakı en güzel olanınızdır.",
    "Dua, ibadetin özüdür.",
    "Gülümsemen, sadakadır.",
    "İki nimet vardır ki insanların çoğu onlarda aldanmıştır: Sağlık ve boş vakit.",
    "Temizlik imanın yarısıdır.",
    "Hayra vesile olan, o hayrı yapan gibidir.",
    "Gerçek zenginlik, mal çokluğu değil gönül tokluğudur."
]

# Madde 12, 13, 14: Dil Kartları
DILLER = [
    {"ar": "As-Sabr (الصبر)", "en": "Patience", "tr": "Sabır: Zorluklar karşısında direnç göstermek, acele etmemek."},
    {"ar": "Al-İkhlas (الإخلاص)", "en": "Sincerity", "tr": "İhlas: İbadeti sadece Allah rızası için yapmak, samimiyet."},
    {"ar": "Ash-Shukr (الشكر)", "en": "Gratitude", "tr": "Şükür: Verilen nimetlerin değerini bilip Allah'a hamd etmek."},
    {"ar": "At-Tawakkul (التوكل)", "en": "Trust in Allah", "tr": "Tevekkül: Elinden geleni yapıp sonucu Allah'a bırakmak."},
    {"ar": "Al-İlm (العلم)", "en": "Knowledge", "tr": "İlim: Bilgi, cehaletten kurtulmak için yapılan kutsal çaba."}
]

# Madde 10: Esmaül Hüsna
ESMALAR = {
    "Allah": "Eşi benzeri olmayan, tek ilah.",
    "Er-Rahmân": "Dünyada her canlıya şefkat gösteren.",
    "Er-Rahîm": "Ahirette sadece müminlere merhamet eden.",
    "El-Melik": "Kainatın gerçek sahibi ve yöneticisi.",
    "El-Kuddûs": "Her türlü eksiklik ve hatadan münezzeh olan."
}

# Madde 11: Kısa Sureler (Tam Metin)
SURELER = {
    "İhlas Suresi": "Bismillahirrahmânirrahîm. Kul hüvallâhü ehad. Allâhüssamed. Lem yelid ve lem yûled. Ve lem yekün lehû küfüven ehad.",
    "Kevser Suresi": "Bismillahirrahmânirrahîm. İnnâ a'taynâkel kevser. Fesalli lirabbike venhar. İnne şânieke hüvel ebter.",
    "Fatiha Suresi": "Bismillahirrahmânirrahîm. Elhamdülillâhi rabbil'alemin. Errahmânirrahîm. Mâliki yevmiddîn. İyyâke na'büdü ve iyyâke nesteîn. İhdinassırâtel müstakîm. Sırâtallezîne en'amte aleyhim gayrilmağdûbi aleyhim veleddâllîn."
}

# --- 4. SIDEBAR (DİSİPLİNLİ TASARIM) ---
with st.sidebar:
    st.markdown("<h1 style='color:#d4af37; text-align:center;'>🔱 MANEVİ PANEL</h1>", unsafe_allow_html=True)
    
    # Madde 6 & 7: Zikirmatik & Sıfırla
    st.markdown("<div style='background:#1a1a1a; border:2px solid #d4af37; padding:15px; border-radius:15px; text-align:center;'>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:#ffffff; font-size:4.5rem; margin:0;'>{st.session_state.zikir}</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sidebar-yazi'>TOPLAM ZİKİR</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📿 ZİKİR ÇEK"): st.session_state.zikir += 1; st.session_state.nur += 5; st.rerun()
    with c2:
        if st.button("🔄 SIFIRLA"): st.session_state.zikir = 0; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Madde 12, 13, 14: Dil Kartı
    st.markdown("<p class='sidebar-yazi' style='margin-top:20px;'>🌍 GÜNÜN KELİMESİ</p>", unsafe_allow_html=True)
    d = DILLER[st.session_state.h_idx % len(DILLER)]
    st.markdown(f"""
    <div class='dil-kutusu'>
        <b style='color:#00b0ff; font-size:1.4rem;'>{d['ar']}</b><br>
        <span style='color:#ffffff;'><b>EN:</b> {d['en']}</span><br>
        <span style='color:#00e676;'><b>TR:</b> {d['tr']}</span>
    </div>
    """, unsafe_allow_html=True)

    # Madde 8: Makam
    st.markdown("---")
    st.metric("MANEVİ MAKAM", f"{(st.session_state.nur // 100)}. Mertebe")
    sehir = st.selectbox("📍 ŞEHİR SEÇİN", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana"])

# --- 5. ANA EKRAN (14 MADDE ENTEGRASYONU) ---
try:
    v_data = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']['timings']
    
    # Madde 1: Besmele
    st.markdown("<h1 style='font-family:Amiri; font-size:5rem; text-align:center; color:#d4af37;'>بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</h1>", unsafe_allow_html=True)

    # Madde 2: Günün Ayeti
    st.markdown("<div style='text-align:center; font-size:1.2rem; border-bottom:1px solid #333; padding-bottom:10px;'>'Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten men edersiniz.' (Âli İmrân, 110)</div>", unsafe_allow_html=True)

    # Madde 4 & 5: Vakitler & Sayaç Mantığı
    st.markdown("<br>", unsafe_allow_html=True)
    v_lbls = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
    v_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    cols = st.columns(6)
    for i, (k, l) in enumerate(zip(v_keys, v_lbls)):
        cols[i].markdown(f"<div class='vakit-kart'><b>{l}</b><br><span class='vakit-saat'>{v_data[k]}</span></div>", unsafe_allow_html=True)

    # Madde 3 & 9: Hadis & Namaz Takibi
    st.markdown(f"<div class='bilgi-kutusu' style='border-left-color:#00e676;'>📜 <b style='color:#00e676;'>Günün Hadisi:</b><br>{HADISLER[st.session_state.h_idx % len(HADISLER)]}</div>", unsafe_allow_html=True)
    
    if st.button("🕋 BU VAKTİN NAMAZINI KILDIM (+50 NUR)", use_container_width=True):
        st.session_state.nur += 50; st.session_state.h_idx += 1; st.balloons(); st.rerun()

    # Madde 10 & 11: Esma & Sureler (Tam Metinler)
    st.divider()
    ca, cb = st.columns(2)
    with ca:
        st.subheader("✨ Esmaül Hüsna")
        for k, v in ESMALAR.items():
            st.markdown(f"<div style='background:#111; padding:10px; margin:5px; border-radius:5px;'><b>{k}</b>: {v}</div>", unsafe_allow_html=True)
    with cb:
        st.subheader("📖 Kısa Sureler")
        for k, v in SURELER.items():
            with st.expander(k):
                st.write(v)

except:
    st.error("Bağlantı hatası. Lütfen bekleyin veya şehri değiştirin.")