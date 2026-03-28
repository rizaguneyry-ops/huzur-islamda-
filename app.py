import streamlit as st
import requests
from datetime import datetime, timedelta
import time
import random

# --- 1. AYARLAR VE TASARIM ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

# Veri Setleri
AYLAR_TR = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}

ESMAUL_HUSNA_99 = [
    ("Allah", "Eşi benzeri olmayan tek ilah"), ("Er-Rahmân", "Dünyada her kula merhamet eden"), ("Er-Rahîm", "Ahirette müminlere şefkat eden"),
    ("El-Melik", "Mülkün gerçek sahibi"), ("El-Kuddûs", "Hata ve noksanlıktan uzak"), ("Es-Selâm", "Esenlik veren"), ("El-Mü'min", "Güven veren"),
    ("El-Müheymin", "Gözetip koruyan"), ("El-Azîz", "İzzet sahibi"), ("El-Cebbâr", "Dilediğini yapan"), ("El-Mütekebbir", "Büyüklükte eşsiz"),
    ("El-Hâlık", "Yaratan"), ("El-Bâri", "Kusursuz yaratan"), ("El-Musavvir", "Şekil veren"), ("El-Gaffâr", "Mağfireti bol olan"),
    ("El-Kahhâr", "Her şeye galip gelen"), ("El-Vehhâb", "Karşılıksız veren"), ("Er-Razzâk", "Rızık veren"), ("El-Fettâh", "Kapıları açan"),
    ("El-Alîm", "Her şeyi bilen"), ("El-Kâbıd", "Sıkan, daraltan"), ("El-Bâsıt", "Açan, genişleten"), ("El-Hâfıd", "Dereceleri alçaltan"),
    ("Er-Râfi", "Dereceleri yükselten"), ("El-Muiz", "İzzet veren"), ("El-Müzil", "Zelil kılan"), ("Es-Semî", "Her şeyi işiten"),
    ("El-Basîr", "Her şeyi gören"), ("El-Hakem", "Mutlak hakim"), ("El-Adl", "Mutlak adalet sahibi"), ("El-Latîf", "Lütfu bol olan"),
    ("El-Habîr", "Her şeyden haberdar"), ("El-Halîm", "Cezada acele etmeyen"), ("El-Azîm", "Pek yüce"), ("El-Gafûr", "Çok bağışlayan"),
    ("Eş-Şekûr", "Şükre karşılık veren"), ("El-Aliyy", "Yüceler yücesi"), ("El-Kebîr", "En büyük"), ("El-Hafîz", "Koruyucu olan"),
    ("El-Mukît", "Rızıkları yaratan"), ("El-Hasîb", "Hesaba çeken"), ("El-Celîl", "Azamet sahibi"), ("El-Kerîm", "Çok cömert"),
    ("Er-Rakîb", "Gözetleyen"), ("El-Mucîb", "Duaları kabul eden"), ("El-Vâsi", "İlmi her şeyi kuşatan"), ("El-Hakîm", "Hikmet sahibi"),
    ("El-Vedûd", "Kullarını seven"), ("El-Mecîd", "Şanı yüce"), ("El-Bâis", "Ölüleri dirilten"), ("Eş-Şehîd", "Her şeye şahit"),
    ("El-Hakk", "Gerçeğin kendisi"), ("El-Vekîl", "Güvenilip dayanılan"), ("El-Kaviyy", "Pek güçlü"), ("El-Metîn", "Sarsılmaz"),
    ("El-Veliyy", "Müminlerin dostu"), ("El-Hamîd", "Övgüye layık"), ("El-Muhsî", "Sayıları bilen"), ("El-Mübdî", "Örneksiz yaratan"),
    ("El-Muîd", "Yeniden dirilten"), ("El-Muhyî", "Can veren"), ("El-Mümît", "Öldüren"), ("El-Hayy", "Daima diri"),
    ("El-Kayyûm", "Her şeyi ayakta tutan"), ("El-Vâcid", "İstediğini bulan"), ("El-Mâcid", "Kadr ü şanı büyük"), ("El-Vâhid", "Tek olan"),
    ("Es-Samed", "Muhtaç olmayan"), ("El-Kâdir", "Kudret sahibi"), ("El-Muktedir", "Gücü yeten"), ("El-Muahhir", "Geride bırakan"),
    ("El-Evvel", "İlk olan"), ("El-Âhir", "Son olan"), ("Ez-Zâhir", "Varlığı aşikar"), ("El-Bâtın", "Varlığı gizli"),
    ("El-Vâlî", "İdare eden"), ("El-Müteâlî", "Noksanlıklardan yüce"), ("El-Berr", "İyiliği bol"), ("Et-Tevvâb", "Tövbeleri kabul eden"),
    ("El-Müntakim", "İntikam alan"), ("El-Afüvv", "Bağışlayan"), ("Er-Raûf", "Şefkatli"), ("Mâlikü’l-Mülk", "Mülkün sahibi"),
    ("Zü’l-Celâli ve’l-İkrâm", "İkram sahibi"), ("El-Muksit", "Adaletle yapan"), ("El-Câmi", "Toplayan"), ("El-Ganî", "Çok zengin"),
    ("El-Mugnî", "Zengin eden"), ("El-Mâni", "Engelleyen"), ("Ed-Dârr", "Zarar veren"), ("En-Nâfi", "Fayda veren"),
    ("En-Nûr", "Nurlandıran"), ("El-Hâdî", "Hidayet veren"), ("El-Bedî", "Eşsiz yaratan"), ("El-Bâkî", "Ebedi olan"),
    ("El-Vâris", "Her şeyin sahibi"), ("Er-Reşîd", "Doğru yolu gösteren"), ("Es-Sabûr", "Çok sabırlı")
]

SURELER = {
    "Fil": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl...", "Kureyş": "Li îlâfi kureyş...", "Mâûn": "Era'eytellezî yükezzibü bi'd-dîn...",
    "Kevser": "İnnâ a'taynâke'l-kevser...", "Kâfirûn": "Kul yâ eyyühe'l-kâfirûn...", "Nasr": "İzâ câe nasrullâhi ve'l-feth...",
    "Tebbet": "Tebbet yedâ ebî lehebin ve tebb...", "İhlâs": "Kul hüvallâhü ehad...", "Felak": "Kul eûzü bi-rabbi'l-felak...", "Nâs": "Kul eûzü bi-rabbi'n-nâs..."
}

# --- CSS VE ARKA PLAN (Madde 13) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2070&auto=format&fit=crop");
        background-size: cover; background-attachment: fixed; color: white;
    }
    .besmele { text-align: center; font-size: 3.5rem; font-weight: bold; color: #fbc02d; margin-top: 10px; }
    .ayet-meal { text-align: center; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 15px; border: 1px solid #fbc02d; margin: 0 10% 20px 10%; }
    .yuvarlak-sayac { 
        width: 250px; height: 250px; border-radius: 50%; border: 8px solid #fbc02d; 
        margin: 20px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: rgba(0,0,0,0.8); box-shadow: 0 0 30px #fbc02d;
    }
    .vakit-kart { background: white; color: black; border-radius: 15px; padding: 15px; text-align: center; border-bottom: 8px solid #fbc02d; margin-bottom: 10px; }
    .vakit-saat { font-size: 2.3rem; font-weight: 900; color: #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Maddeler: 5, 6, 7, 8, 9, 10, 11, 12) ---
with st.sidebar:
    st.header("🕋 HUZUR REHBERİ")
    lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English", "العربية", "Russian", "Spanish", "German", "Chinese", "Italian"])
    sehir = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Konya", "Antalya", "Adana", "Gaziantep"])

    # Madde 6: Zikirmatik
    st.divider()
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f"<h2 style='text-align:center;'>📿 {st.session_state.zk}</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("➕ Zikir", use_container_width=True): st.session_state.zk += 1; st.rerun()
    if c2.button("🔄 Sıfırla", use_container_width=True): st.session_state.zk = 0; st.rerun()

    # Madde 12: Günün Ayeti
    st.info(f"✨ **Günün Ayeti:**\nNamaza kalktığınız zaman Allah'ın huzurunda olduğunuzu unutmayın.")

    # Detaylı Bilgiler (Maddeler: 7, 8, 9, 10)
    with st.expander("📌 32 Farz"):
        st.write("İmanın Şartları: 6, İslamın Şartları: 5, Abdestin Farzları: 4, Guslün Farzları: 3, Teyemmümün Farzları: 2, Namazın Farzları: 12")
    with st.expander("✨ Esmaül Hüsna (99 İsim)"):
        for i, (ad, anl) in enumerate(ESMAUL_HUSNA_99, 1):
            st.write(f"**{i}. {ad}**: {anl}")
    with st.expander("🚿 Abdest Nasıl Alınır?"):
        st.write("Niyet, Eller, Ağız(3), Burun(3), Yüz, Kollar, Baş Mesh, Kulak, Ayak.")
    with st.expander("📖 Son 10 Sure"):
        for ad, metin in SURELER.items(): st.write(f"**{ad}**: {metin}")
    
    st.write("🧭 **Kıble Pusulası:** 147° (Güneydoğu)")

# --- ANA EKRAN (Maddeler: 1, 2, 3, 4) ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
st.markdown("<div class='ayet-meal'>'Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız.' (Âli İmrân, 110)</div>", unsafe_allow_html=True)

sayac_alani = st.empty()

# API'den Veri Çekme
try:
    url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
    res = requests.get(url).json()['data']
    v = res['timings']
    t = res['date']

    # Madde 2: Saniye Saniye Geri Sayım Döngüsü
    while True:
        simdi = datetime.now()
        v_liste = {"İmsak": v['Fajr'], "Güneş": v['Sunrise'], "Öğle": v['Dhuhr'], "İkindi": v['Asr'], "Akşam": v['Maghrib'], "Yatsı": v['Isha']}
        
        siradaki_ad = ""; siradaki_zaman = None
        for ad, saat in v_liste.items():
            v_dt = datetime.strptime(saat, "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day)
            if v_dt > simdi: siradaki_ad = ad; siradaki_zaman = v_dt; break
        if not siradaki_zaman:
            siradaki_ad = "İmsak"; siradaki_zaman = datetime.strptime(v['Fajr'], "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day) + timedelta(days=1)

        kalan = siradaki_zaman - simdi
        saat, mod = divmod(kalan.seconds, 3600); dak, san = divmod(mod, 60)

        with sayac_alani.container():
            st.markdown(f"""
                <div class='yuvarlak-sayac'>
                    <div style='font-size:1.4rem;'>{siradaki_ad.upper()}</div>
                    <div style='font-size:3.5rem; font-weight:900;'>{saat:02d}:{dak:02d}:{san:02d}</div>
                    <div style='font-size:0.9rem; color:#fbc02d;'>KALAN SÜRE</div>
                </div>
            """, unsafe_allow_html=True)

            # Türkçe Takvim
            st.markdown(f"<p style='text-align:center; font-size:1.2rem;'>📅 {simdi.day} {AYLAR_TR[simdi.month]} {simdi.year} | 🌙 {t['hijri']['day']} {t['hijri']['month']['ar']} {t['hijri']['year']}</p>", unsafe_allow_html=True)

            # Madde 3: Vakitler
            st.markdown("### ☀️ Sabah & Öğle")
            u1, u2, u3 = st.columns(3)
            u1.markdown(f"<div class='vakit-kart'><b>İMSAK</b><div class='vakit-saat'>{v['Fajr']}</div></div>", unsafe_allow_html=True)
            u2.markdown(f"<div class='vakit-kart'><b>GÜNEŞ</b><div class='vakit-saat'>{v['Sunrise']}</div></div>", unsafe_allow_html=True)
            u3.markdown(f"<div class='vakit-kart'><b>ÖĞLE</b><div class='vakit-saat'>{v['Dhuhr']}</div></div>", unsafe_allow_html=True)

            st.markdown("### 🌙 İkindi & Akşam & Yatsı")
            a1, a2, a3 = st.columns(3)
            a1.markdown(f"<div class='vakit-kart'><b>İKİNDİ</b><div class='vakit-saat'>{v['Asr']}</div></div>", unsafe_allow_html=True)
            a2.markdown(f"<div class='vakit-kart'><b>AKŞAM</b><div class='vakit-saat'>{v['Maghrib']}</div></div>", unsafe_allow_html=True)
            a3.markdown(f"<div class='vakit-kart'><b>YATSI</b><div class='vakit-saat'>{v['Isha']}</div></div>", unsafe_allow_html=True)

            # Madde 4: Haftalık Vakit (Bugünden İtibaren)
            st.divider()
            st.subheader("🗓️ Haftalık Namaz Vakitleri")
            for i in range(7):
                h_gun = simdi + timedelta(days=i)
                st.write(f"**{h_gun.day} {AYLAR_TR[h_gun.month]}**: İmsak: {v['Fajr']} | Akşam: {v['Maghrib']} | Yatsı: {v['Isha']}")
            
            # Madde 14: Bildirim & Ses (Vakit Gelince)
            if kalan.seconds < 2:
                st.audio("https://www.soundboard.com/handler/DownLoadTrack.ashx?cliptoken=ea395b7b-2313-4e6a-8d3c-99f493540f26")
                st.toast("Ezan Okunuyor! Namazını kıldın mı?")

        time.sleep(1)

except:
    st.error("Bağlantı bekleniyor...")
    time.sleep(5)
    st.rerun()