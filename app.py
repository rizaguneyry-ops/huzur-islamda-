import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda Pro Max", page_icon="🕋", layout="wide")

# --- 2. TÜM VERİ SETLERİ (Hata Almamak İçin En Başta) ---
sehirler_81 = ["Adana", "Adiyaman", "Afyonkarahisar", "Agri", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydin", "Balikesir", "Bartin", "Batman", "Bayburt", "Bilecik", "Bingol", "Bitlis", "Bolu", "Burdur", "Bursa", "Canakkale", "Cankiri", "Corum", "Denizli", "Diyarbakir", "Duzce", "Edirne", "Elazig", "Erzincan", "Erzurum", "Eskisehir", "Gaziantep", "Giresun", "Gumushane", "Hakkari", "Hatay", "Igdir", "Isparta", "Istanbul", "Izmir", "Kahramanmaras", "Karabuk", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kilis", "Kirikkale", "Kirklareli", "Kirsehir", "Kocaeli", "Konya", "Kutahya", "Malatya", "Manisa", "Mardin", "Mersin", "Mugla", "Mus", "Nevsehir", "Nigde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Sanliurfa", "Siirt", "Sinop", "Sivas", "Sirnak", "Tekirdag", "Tokat", "Trabzon", "Tunceli", "Usak", "Van", "Yalova", "Yozgat", "Zonguldak"]

tr_aylar = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}

EZAN_URL = "https://www.namazvaktim.org/ses/ezan1.mp3"

son_on_sure_data = {
    "Fil Suresi": {"oku": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl...", "meal": "Rabbinin, fil sahiplerine ne yaptığını görmedin mi?"},
    "Kureyş Suresi": {"oku": "Li îlâfi kureyş...", "meal": "Kureyş'e kolaylaştırıldığı için..."},
    "Mâûn Suresi": {"oku": "Era'eytellezî yükezzibü bid dîn...", "meal": "Dini yalanlayanı gördün mü?"},
    "Kevser Suresi": {"oku": "İnnâ a'taynâkel kevser...", "meal": "Şüphesiz biz sana Kevser'i verdik."},
    "Kâfirûn Suresi": {"oku": "Kul yâ eyyühel kâfirûn...", "meal": "De ki: Ey kafirler! Ben sizin taptıklarınıza tapmam."},
    "Nasr Suresi": {"oku": "İzâ câe nasrullâhi vel feth...", "meal": "Allah'ın yardımı ve fetih geldiğinde..."},
    "Tebbet Suresi": {"oku": "Tebbet yedâ ebî lehebin ve tebb...", "meal": "Ebu Leheb'in iki eli kurusun!"},
    "İhlâs Suresi": {"oku": "Kul hüvallâhü ehad...", "meal": "De ki: O Allah birdir."},
    "Felak Suresi": {"oku": "Kul e'ûzü bi rabbil felak...", "meal": "De ki: Sabahın Rabbine sığınırım."},
    "Nâs Suresi": {"oku": "Kul e'ûzü bi rabbin nâs...", "meal": "De ki: İnsanların Rabbine sığınırım."}
}

lang_data = {
    "Türkçe": {
        "vakitler": ["İMSAK", "GÜNEŞ", "ÖĞLE", "İKİNDİ", "AKŞAM", "YATSI"],
        "sehir_sec": "📍 Şehir Seç", "zikir_baslik": "📿 Zikirmatik", "zikir_cek": "Zikir Çek", "sifirla": "Sıfırla",
        "haftalik": "🗓️ Haftalık Namaz Vakitleri", "kaza": "📊 Kaza Takibi", "hata": "Bağlantı Hatası!",
        "ay_110": "Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız."
    },
    "English": {
        "vakitler": ["FAJR", "SUNRISE", "DHUHR", "ASR", "MAGHRIB", "ISHA"],
        "sehir_sec": "📍 Select City", "zikir_baslik": "📿 Tasbeeh", "zikir_cek": "Count", "sifirla": "Reset",
        "haftalik": "🗓️ Weekly Times", "kaza": "📊 Qaza", "hata": "Connection Error!",
        "ay_110": "You are the best nation produced [as an example] for mankind. You enjoin what is right and forbid what is wrong."
    },
    "العربية": {
        "vakitler": ["الفجر", "الشروق", "الظهر", "العصر", "المغرب", "العشاء"],
        "sehir_sec": "📍 اختر المدينة", "zikir_baslik": "📿 المسبحة", "zikir_cek": "تسبيح", "sifirla": "إعادة",
        "haftalik": "🗓️ الجدول الأسبوعي", "kaza": "📊 صلوات القضاء", "hata": "خطأ في الاتصال",
        "ay_110": "كُنتُمْ خَيْرَ أُمَّةٍ أُخْرِجَتْ لِلنَّاسِ تَأْمُرُونَ بِالْمَعْرُوفِ وَتَنْهَوْنَ عَنِ الْمُنكَرِ"
    }
}

# --- 3. CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2000"); background-size: cover; background-attachment: fixed; }
    .besmele { text-align: center; color: #d4af37 !important; font-size: 3rem; font-family: 'Times New Roman', serif; margin-top: 10px; text-shadow: 2px 2px 10px rgba(212,175,55,0.4); }
    .ayet-box { text-align: center; color: #f1f1f1 !important; font-size: 1.1rem; background: rgba(212,175,55,0.15); border: 1px solid #d4af37; padding: 20px; border-radius: 15px; margin: 20px auto; max-width: 850px; }
    .vakit-box { background: rgba(253, 246, 227, 0.98); border-radius: 12px; padding: 15px; text-align: center; border: 2px solid #d4af37; }
    .vakit-box div { color: #1a2a24 !important; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: rgba(10, 30, 25, 0.98) !important; border-right: 2px solid #d4af37; }
    .stExpander { background-color: #ffffff !important; border-radius: 8px !important; border: 1px solid #d4af37; }
    .stExpander p, .stExpander span, .stExpander div { color: #000000 !important; }
    .zikir-ana { background: rgba(255,255,255,0.05); padding: 30px; border-radius: 20px; text-align: center; border: 2px solid #d4af37; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    sel_lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English", "العربية"])
    L = lang_data[sel_lang]
    sehir = st.selectbox(L['sehir_sec'], sehirler_81, index=sehirler_81.index("Istanbul"))
    
    st.write("---")
    with st.expander("📖 Son On Sure", expanded=False):
        for s_ad, s_ic in son_on_sure_data.items():
            st.markdown(f"**{s_ad}**")
            st.caption(s_ic['oku'])
            st.write(f"*Meal:* {s_ic['meal']}")
            st.write("---")

    with st.expander(L['kaza'], expanded=False):
        for kv in L['vakitler']:
            k_key = f"kaza_{kv}_{sel_lang}"
            if k_key not in st.session_state: st.session_state[k_key] = 0
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{kv}**")
            if c2.button(f"{st.session_state[k_key]}", key=f"btn_{k_key}"): 
                st.session_state[k_key] += 1; st.rerun()

# --- 5. ANA EKRAN ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
st.markdown(f"<div class='ayet-box'><b>Ali İmran 110:</b><br>{L['ay_110']}</div>", unsafe_allow_html=True)

try:
    # API Verileri
    r = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = r['timings']
    v_dict = dict(zip(L['vakitler'], [v['Fajr'], v['Sunrise'], v['Dhuhr'], v['Asr'], v['Maghrib'], v['Isha']]))

    # Günlük Vakit Kartları
    st.markdown(f"<h2 style='text-align:center;'>{sehir.upper()}</h2>", unsafe_allow_html=True)
    cols = st.columns(6)
    for i, (name, val) in enumerate(v_dict.items()):
        cols[i].markdown(f'<div class="vakit-box"><div>{name}</div><div style="font-size:22px;">{val}</div></div>', unsafe_allow_html=True)

    # Geri Sayım Halka
    st.components.v1.html(f"""
    <div style="display: flex; justify-content: center; margin: 20px 0;"><div style="border: 5px solid #d4af37; border-radius: 50%; width: 140px; height: 140px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.7); box-shadow: 0 0 20px #d4af37;"><div id="c" style="color: #fbbf24; font-size: 28px; font-weight: bold; font-family: monospace;">00:00:00</div></div></div>
    <script>
        const v = {json.dumps(v_dict)};
        function u() {{
            const n = new Date(); const s = n.getHours()*3600 + n.getMinutes()*60 + n.getSeconds();
            let t = null; for(let k in v) {{ let [h,m] = v[k].split(':'); let vs = parseInt(h)*3600+parseInt(m)*60; if(vs>s) {{ t=vs; break; }} }}
            if(!t) {{ let [h,m] = v['{L['vakitler'][0]}'].split(':'); t = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = t-s; let h=Math.floor(d/3600), m=Math.floor((d%3600)/60), sc=d%60;
            document.getElementById('c').innerHTML = (h<10?'0'+h:h)+":"+(m<10?'0'+m:m)+":"+(sc<10?'0'+sc:sc);
        }} setInterval(u, 1000); u();
    </script>""", height=170)

    # Haftalık Çizelge
    st.markdown(f"### {L['haftalik']}")
    h_data = requests.get(f"http://api.aladhan.com/v1/calendarByCity?city={sehir}&country=Turkey&method=13").json()['data']
    weekly = [[d['date']['gregorian']['day']+" "+d['date']['gregorian']['month']['en'], d['timings']['Fajr'], d['timings']['Dhuhr'], d['timings']['Asr'], d['timings']['Maghrib'], d['timings']['Isha']] for d in h_data[:7]]
    st.table(weekly)

    # Zikirmatik (En Alt Ana Ekran)
    st.markdown(f"<div class='zikir-ana'><h2>{L['zikir_baslik']}</h2>", unsafe_allow_html=True)
    if 'zk_val' not in st.session_state: st.session_state.zk_val = 0
    st.markdown(f"<h1 style='color:#fbbf24; font-size:5rem; margin:0;'>{st.session_state.zk_val}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button(L['zikir_cek'], key="main_zk_btn", use_container_width=True): st.session_state.zk_val += 1; st.rerun()
    if c2.button(L['sifirla'], key="main_zk_res", use_container_width=True): st.session_state.zk_val = 0; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

except Exception: st.error(L['hata'])

time.sleep(60)
st.rerun()