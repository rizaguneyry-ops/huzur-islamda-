import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# --- 1. AYARLAR VE TASARIM (ARKA PLAN VE CSS) ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1564121211835-e88c852648ab?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
        color: white;
    }
    .besmele { text-align: center; font-size: 3.8rem; font-weight: bold; color: #fbc02d; margin-top: 20px; font-family: 'Times New Roman'; }
    .ayet-meal { text-align: center; background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; border: 2px solid #fbc02d; margin: 10px 10%; font-size: 1.2rem; }
    
    /* 2. Madde: Yuvarlak Geri Sayım */
    .yuvarlak-konteynir { display: flex; justify-content: center; margin: 30px 0; }
    .yuvarlak-sayac { 
        width: 280px; height: 280px; border-radius: 50%; border: 10px solid #fbc02d; 
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
        background: rgba(0,0,0,0.6); box-shadow: 0 0 40px rgba(251, 192, 45, 0.4);
    }
    
    /* 3. Madde: Vakit Kartları */
    .vakit-kart { background: white; color: black; border-radius: 20px; padding: 25px; text-align: center; border-bottom: 12px solid #d4af37; margin: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
    .vakit-ad { font-size: 1.8rem; font-weight: bold; color: #333; }
    .vakit-saat { font-size: 3.5rem; font-weight: 900; color: #d4af37; }
    
    /* Sidebar Tasarımı */
    .sidebar-kutu { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #fbc02d; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI (FARZLAR, SURELER, DİLLER) ---
DIL_PAKETI = {
    "Türkçe": {"imsak": "İmsak", "gunes": "Güneş", "ogle": "Öğle", "ikindi": "İkindi", "aksam": "Akşam", "yatsi": "Yatsı", "kalan": "Kalan Süre", "zikir": "Zikirmatik", "abdest": "Abdest", "pusula": "Kıble"},
    "English": {"imsak": "Imsak", "gunes": "Sunrise", "ogle": "Dhuhr", "ikindi": "Asr", "aksam": "Maghrib", "yatsi": "Isha", "kalan": "Remaining", "zikir": "Tasbeeh", "abdest": "Wudu", "pusula": "Qibla"},
    "العربية": {"imsak": "إمساك", "gunes": "شروق", "ogle": "ظهر", "ikindi": "عصر", "aksam": "مغرب", "yatsi": "عشاء", "kalan": "الوقت المتبقي", "zikir": "مسبحة", "abdest": "وضوء", "pusula": "قبلة"}
    # Diğer diller (Rusça, İspanyolca vb.) benzer şekilde genişletilebilir.
}

ESMAUL_HUSNA_99 = [
    ("Allah", "Eşi benzeri olmayan"), ("Er-Rahman", "Dünyada her kula merhamet eden"), ("Er-Rahim", "Ahirette müminlere şefkat eden"),
    ("El-Melik", "Mülkün sahibi"), ("El-Kuddûs", "Noksanlıktan uzak"), ("Es-Selâm", "Esenlik veren"), ("El-Mü'min", "Güven veren")
    # ... (Buraya 99 ismin tamamı eklenebilir, yer kaplamaması için yapı kuruldu)
]

SURELER_10 = {
    "Fil Suresi": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl...",
    "Kureyş Suresi": "Li îlâfi kureyş...", "İhlas Suresi": "Kul hüvallâhü ehad..."
}

AYETLER = [
    "Şüphesiz namaz, müminlere belirli vakitlerde farz kılınmıştır. (Nisâ, 103)",
    "Sabrederek ve namaz kılarak Allah’tan yardım dileyin. (Bakara, 45)"
]

# --- 3. YAN EKRAN (SIDEBAR) - MADDE 5, 6, 7, 8, 9, 10, 11, 12 ---
with st.sidebar:
    st.markdown("## 🕋 HUZUR REHBERİ")
    
    # 5. Madde: Dil Seçeneği
    secilen_dil = st.selectbox("🌐 Dil / Language", ["Türkçe", "English", "العربية", "Russian", "Spanish", "German", "Chinese", "Italian"])
    dil = DIL_PAKETI.get(secilen_dil, DIL_PAKETI["Türkçe"])
    
    sehir = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Konya", "Antalya", "Gaziantep", "Diyarbakir"])

    # 6. Madde: Zikirmatik (Hızlı ve Sorunsuz)
    st.markdown(f"### 📿 {dil['zikir']}")
    if 'zikir_sayisi' not in st.session_state: st.session_state.zikir_sayisi = 0
    st.markdown(f"<h1 style='text-align:center; color:#fbc02d;'>{st.session_state.zikir_sayisi}</h1>", unsafe_allow_html=True)
    cz1, cz2 = st.columns(2)
    if cz1.button("➕ Artır", use_container_width=True): st.session_state.zikir_sayisi += 1; st.rerun()
    if cz2.button("🔄 Sıfırla", use_container_width=True): st.session_state.zikir_sayisi = 0; st.rerun()

    # 12. Madde: Günün Ayeti (Her girişte yenilenir)
    st.info(f"✨ **Günün Ayeti:**\n{random.choice(AYLAR)}")

    # 7, 8, 9, 10. Maddeler: Detaylı Bilgiler
    tab1, tab2, tab3 = st.tabs(["📌 Bilgiler", "✨ Esmaül Hüsna", "📖 Sureler"])
    with tab1:
        with st.expander("Abdest Nasıl Alınır?"):
            st.write("1. Niyet ve Besmele\n2. Eller yıkanır\n3. Ağız ve Burun (3 kere)\n4. Yüz yıkanır\n5. Kollar (Dirseklere kadar)\n6. Başın meshi ve Kulaklar\n7. Ayaklar")
        with st.expander("32 Farz"):
            st.write("**İmanın Şartları:** 6\n**İslamın Şartları:** 5\n**Abdestin Farzları:** 4\n**Guslün Farzları:** 3\n**Teyemmümün Farzları:** 2\n**Namazın Farzları:** 12")
    with tab2:
        for ad, anl in ESMAUL_HUSNA_99:
            st.markdown(f"**{ad}**: {anl}")
    with tab3:
        for s_ad, s_met in SURELER_10.items():
            st.markdown(f"**{s_ad}**\n{s_met}")

    # 11. Madde: Kıble Pusulası (Bilgi amaçlı)
    st.warning(f"🧭 {dil['pusula']}: 147° (Güneydoğu)")

# --- 4. ANA EKRAN - MADDE 1, 2, 3, 4 ---
# 1. Madde: Besmele ve Ali İmran 110
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
st.markdown("<div class='ayet-meal'>'Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız.' (Âli İmrân, 110)</div>", unsafe_allow_html=True)

try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    t = res['date']

    # 2. Madde: Geri Sayım Hesaplama
    v_liste = {"İmsak": v['Fajr'], "Güneş": v['Sunrise'], "Öğle": v['Dhuhr'], "İkindi": v['Asr'], "Akşam": v['Maghrib'], "Yatsı": v['Isha']}
    simdi = datetime.now()
    siradaki_ad = ""; siradaki_zaman = None
    for ad, saat in v_liste.items():
        v_dt = datetime.strptime(saat, "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day)
        if v_dt > simdi: siradaki_ad = ad; siradaki_zaman = v_dt; break
    if not siradaki_zaman:
        siradaki_ad = "İmsak"; siradaki_zaman = datetime.strptime(v['Fajr'], "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day) + timedelta(days=1)
    
    kalan = siradaki_zaman - simdi
    saat, mod = divmod(kalan.seconds, 3600); dak, san = divmod(mod, 60)

    # Yuvarlak Sayaç Görüntüsü
    st.markdown(f"""
        <div class='yuvarlak-konteynir'>
            <div class='yuvarlak-sayac'>
                <div style='font-size:1.5rem;'>{siradaki_ad.upper()}</div>
                <div style='font-size:4.5rem; font-weight:900;'>{saat:02d}:{dak:02d}</div>
                <div style='font-size:1.2rem; color:#fbc02d;'>{dil['kalan']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Miladi ve Hicri Takvim
    st.markdown(f"<h3 style='text-align:center;'>📅 {t['gregorian']['day']} {t['gregorian']['month']['en']} {t['gregorian']['year']} | 🌙 {t['hijri']['day']} {t['hijri']['month']['ar']} {t['hijri']['year']}</h3>", unsafe_allow_html=True)

    # 3. Madde: Net ve Canlı Vakitler (Ayrı Gruplar)
    st.markdown("### ☀️ GÜNDÜZ VAKİTLERİ")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='vakit-kart'><div class='vakit-ad'>{dil['imsak']}</div><div class='vakit-saat'>{v['Fajr']}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='vakit-kart'><div class='vakit-ad'>{dil['gunes']}</div><div class='vakit-saat'>{v['Sunrise']}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='vakit-kart'><div class='vakit-ad'>{dil['ogle']}</div><div class='vakit-saat'>{v['Dhuhr']}</div></div>", unsafe_allow_html=True)

    st.markdown("### 🌙 GECE VAKİTLERİ")
    c4, c5, c6 = st.columns(3)
    c4.markdown(f"<div class='vakit-kart'><div class='vakit-ad'>{dil['ikindi']}</div><div class='vakit-saat'>{v['Asr']}</div></div>", unsafe_allow_html=True)
    c5.markdown(f"<div class='vakit-kart'><div class='vakit-ad'>{dil['aksam']}</div><div class='vakit-saat'>{v['Maghrib']}</div></div>", unsafe_allow_html=True)
    c6.markdown(f"<div class='vakit-kart'><div class='vakit-ad'>{dil['yatsi']}</div><div class='vakit-saat'>{v['Isha']}</div></div>", unsafe_allow_html=True)

    # 4. Madde: Bir Haftalık Vakitler
    st.divider()
    st.subheader("🗓️ Bir Haftalık Namaz Takvimi")
    cal_res = requests.get(f"http://api.aladhan.com/v1/calendarByCity?city={sehir}&country=Turkey&method=13").json()['data']
    for gun in cal_res[:7]:
        dg = gun['date']['gregorian']; tv = gun['timings']
        st.write(f"**{dg['day']} {dg['month']['en']}**: İmsak: {tv['Fajr']} | Öğle: {tv['Dhuhr']} | Akşam: {tv['Maghrib']}")

    # 14. Madde: Ezan ve Hatırlatıcı (Basit Bildirim)
    if kalan.seconds < 60:
        st.toast("Ezan Okunuyor...", icon="🕌")
        st.audio("https://www.soundboard.com/handler/DownLoadTrack.ashx?cliptoken=ea395b7b-2313-4e6a-8d3c-99f493540f26")

except Exception as e:
    st.error("Veriler alınırken bir hata oluştu. Lütfen bağlantınızı kontrol edin.")

# Uygulamayı canlı tutmak için her dakika yenileme
time.sleep(60)
st.rerun()