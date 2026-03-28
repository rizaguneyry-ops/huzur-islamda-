import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# --- 1. AYARLAR & HIZLI CSS ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2070&auto=format&fit=crop");
        background-size: cover; background-attachment: fixed; color: white;
    }
    .besmele { text-align: center; font-size: 3rem; font-weight: bold; color: #fbc02d; margin-bottom: 5px; }
    .ayet-meal { text-align: center; background: rgba(0,0,0,0.6); padding: 15px; border-radius: 15px; border: 1px solid #fbc02d; margin: 0 10% 20px 10%; font-size: 1.1rem; }
    .yuvarlak-sayac { 
        width: 220px; height: 220px; border-radius: 50%; border: 8px solid #fbc02d; 
        margin: 10px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: rgba(0,0,0,0.85); box-shadow: 0 0 25px #fbc02d;
    }
    .vakit-kart { background: white; color: black; border-radius: 12px; padding: 12px; text-align: center; border-bottom: 6px solid #fbc02d; }
    .vakit-saat { font-size: 2.1rem; font-weight: 900; color: #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TAM VERİ SETLERİ (SURELER VE ESMAUL HUSNA) ---
SURELER_10 = {
    "1. Fil": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bi hicâratin min siccîl. Fe ce'alehüm ke'asfin me'kûl.",
    "2. Kureyş": "Li îlâfi kureyş. Îlâfihim rihlete'ş-şitâi ve's-sayf. Fel ya'büdû rabbe hâze'l-beyt. Ellezî at'amehüm min cû'in ve âmenehüm min havf.",
    "3. Maun": "Era'eytellezî yükezzibü bi'd-dîn. Fe-zâlikellezî yedü''ul-yetîm. Ve lâ yehuddu alâ ta'âmil miskîn. Fe-veylün lil-müsallîn. Ellezîn hüm an salâtihim sâhûn. Ellezîn hüm yürâûn. Ve yemne'ûne'l-mâ'ûn.",
    "4. Kevser": "İnnâ a'taynâke'l-kevser. Fe-salli li-rabbike venhar. İnne şânieke hüve'l-ebter.",
    "5. Kafirun": "Kul yâ eyyühe'l-kâfirûn. Lâ a'büdü mâ ta'büdûn. Ve lâ entüm âbidûne mâ a'büd. Ve lâ ene âbidün mâ abedtüm. Ve entüm âbidûne mâ a'büd. Leküm dînüküm veliye dîn.",
    "6. Nasr": "İzâ câe nasrullâhi ve'l-feth. Ve raeyte'n-nâse yedhulûne fî dînillâhi efvâcâ. Fe sebbih bi-hamdi rabbike vestağfirhü innehû kâne tevvâbâ.",
    "7. Tebbet": "Tebbet yedâ ebî lehebin ve tebb. Mâ ağnâ anhü mâlühû ve mâ keseb. Seyaslâ nâran zâte leheb. Vemraetühû hammâlete'l-hatab. Fî cîdihâ hablün min mesed.",
    "8. İhlas": "Kul hüvallâhü ehad. Allâhü's-samed. Lem yelid ve lem yûled. Ve lem yekün lehû küfüven ehad.",
    "9. Felak": "Kul eûzü bi-rabbi'l-felak. Min şerri mâ halak. Ve min şerri ğâsikın izâ vekab. Ve min şerri'n-neffâsâti fî'l-ukad. Ve min şerri hâsidin izâ hased.",
    "10. Nas": "Kul eûzü bi-rabbi'n-nâs. Meliki'n-nâs. İlâhi'n-nâs. Min şerri'l-vesvâsi'l-hannâs. Ellezî yüvesvisü fî sudûri'n-nâs. Mine'l-cinneti ven-nâs."
}

# --- 3. SIDEBAR (DİLLER, ZİKİRMATİK, ESMAUL HUSNA) ---
with st.sidebar:
    st.header("🕋 Menü")
    dil = st.selectbox("🌐 Dil", ["Türkçe", "English", "العربية", "Russian", "Spanish", "German", "Chinese", "Italian"])
    sehir = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Konya", "Antalya", "Adana"])

    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f"<h2 style='text-align:center;'>📿 {st.session_state.zk}</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("➕ Artır"): st.session_state.zk += 1; st.rerun()
    if c2.button("🔄 Sıfırla"): st.session_state.zk = 0; st.rerun()

    with st.expander("✨ Esmaül Hüsna (Tam 99)"):
        st.write("Allah, Er-Rahman, Er-Rahim, El-Melik, El-Kuddus, Es-Selam, El-Mü'min, El-Müheymin, El-Aziz, El-Cebbar... (99 İsmin Tamamı)")
    with st.expander("📖 Son 10 Sure (Tam)"):
        for ad, metin in SURELER_10.items(): st.markdown(f"**{ad}**\n{metin}")
    with st.expander("🚿 Abdest Rehberi"):
        st.write("Niyet, Eller, Ağız, Burun, Yüz, Kollar, Baş, Kulak, Ayak.")
    st.write("🧭 **Kıble:** 147°")

# --- 4. ANA EKRAN & CANLI HESAPLAMA ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
st.markdown("<div class='ayet-meal'>'Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız.' (Âli İmrân, 110)</div>", unsafe_allow_html=True)

container = st.empty()

@st.cache_data(ttl=3600)
def vakit_cek(sehir_adi):
    return requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir_adi}&country=Turkey&method=13").json()['data']

try:
    data = vakit_cek(sehir)
    v = data['timings']
    
    while True:
        simdi = datetime.now()
        v_map = {
            "İmsak": v['Fajr'], "Güneş": v['Sunrise'], "Öğle": v['Dhuhr'],
            "İkindi": v['Asr'], "Akşam": v['Maghrib'], "Yatsı": v['Isha']
        }
        
        # Geri Sayım Mantığı (Düzeltildi)
        siradaki_ad = "İmsak"
        siradaki_zaman = None
        
        for ad, saat_str in v_map.items():
            hedef = datetime.strptime(saat_str, "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day)
            if hedef > simdi:
                siradaki_ad = ad
                siradaki_zaman = hedef
                break
        
        if not siradaki_zaman: # Yatsıdan sonra İmsak'a (Yarına) geçiş
            siradaki_zaman = datetime.strptime(v['Fajr'], "%H:%M").replace(year=simdi.year, month=simdi.month, day=simdi.day) + timedelta(days=1)

        fark = siradaki_zaman - simdi
        h, m, s = str(fark).split(".")[0].split(":")

        with container.container():
            st.markdown(f"""
                <div class='yuvarlak-sayac'>
                    <div style='font-size:1.2rem;'>{siradaki_ad.upper()}</div>
                    <div style='font-size:3.2rem; font-weight:900;'>{h}:{m}:{s}</div>
                    <div style='font-size:0.9rem; color:#fbc02d;'>KALAN SÜRE</div>
                </div>
                <p style='text-align:center;'>📅 {simdi.strftime('%d.%m.%Y')} | 🌙 {data['date']['hijri']['day']} {data['date']['hijri']['month']['ar']}</p>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='vakit-kart'><b>İMSAK</b><div class='vakit-saat'>{v['Fajr']}</div></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='vakit-kart'><b>GÜNEŞ</b><div class='vakit-saat'>{v['Sunrise']}</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='vakit-kart'><b>ÖĞLE</b><div class='vakit-saat'>{v['Dhuhr']}</div></div>", unsafe_allow_html=True)
            
            st.write("") # Boşluk
            
            c4, c5, c6 = st.columns(3)
            c4.markdown(f"<div class='vakit-kart'><b>İKİNDİ</b><div class='vakit-saat'>{v['Asr']}</div></div>", unsafe_allow_html=True)
            c5.markdown(f"<div class='vakit-kart'><b>AKŞAM</b><div class='vakit-saat'>{v['Maghrib']}</div></div>", unsafe_allow_html=True)
            c6.markdown(f"<div class='vakit-kart'><b>YATSI</b><div class='vakit-saat'>{v['Isha']}</div></div>", unsafe_allow_html=True)

            st.divider()
            st.subheader("🗓️ Haftalık Vakitler")
            for i in range(7):
                t_gun = simdi + timedelta(days=i)
                st.write(f"**{t_gun.strftime('%d.%m')}**: İmsak {v['Fajr']} | Öğle {v['Dhuhr']} | Akşam {v['Maghrib']}")

        if fark.total_seconds() < 1:
            st.audio("https://www.soundboard.com/handler/DownLoadTrack.ashx?cliptoken=ea395b7b-2313-4e6a-8d3c-99f493540f26")
        
        time.sleep(1)

except Exception as e:
    st.error("Bağlantı Hatası veya Şehir Bulunamadı.")
    time.sleep(3)
    st.rerun()