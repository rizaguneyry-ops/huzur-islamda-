import streamlit as st
import requests
import json
from datetime import datetime, timedelta

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda Pro", page_icon="🕋", layout="wide")

# --- 2. VERİ SETLERİ VE ÖNBELLEK ---
@st.cache_data(ttl=3600) # Verileri 1 saat saklar, hızı artırır
def get_prayer_data(sehir):
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
        return requests.get(url).json()['data']
    except: return None

@st.cache_data(ttl=86400)
def get_weekly_data(sehir):
    try:
        url = f"http://api.aladhan.com/v1/calendarByCity?city={sehir}&country=Turkey&method=13"
        return requests.get(url).json()['data']
    except: return None

sehirler_81 = ["Adana", "Adiyaman", "Afyonkarahisar", "Agri", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydin", "Balikesir", "Bartin", "Batman", "Bayburt", "Bilecik", "Bingol", "Bitlis", "Bolu", "Burdur", "Bursa", "Canakkale", "Cankiri", "Corum", "Denizli", "Diyarbakir", "Duzce", "Edirne", "Elazig", "Erzincan", "Erzurum", "Eskisehir", "Gaziantep", "Giresun", "Gumushane", "Hakkari", "Hatay", "Igdir", "Isparta", "Istanbul", "Izmir", "Kahramanmaras", "Karabuk", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kilis", "Kirikkale", "Kirklareli", "Kirsehir", "Kocaeli", "Konya", "Kutahya", "Malatya", "Manisa", "Mardin", "Mersin", "Mugla", "Mus", "Nevsehir", "Nigde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Sanliurfa", "Siirt", "Sinop", "Sivas", "Sirnak", "Tekirdag", "Tokat", "Trabzon", "Tunceli", "Usak", "Van", "Yalova", "Yozgat", "Zonguldak"]

lang_data = {
    "Türkçe": {
        "v1": ["İMSAK", "GÜNEŞ", "ÖĞLE"], "v2": ["İKİNDİ", "AKŞAM", "YATSI"],
        "zikir": "📿 ZİKİRMATİK (Tıklayın)", "sifirla": "SIFIRLA", "ay_110": "Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz..."
    },
    "English": {
        "v1": ["FAJR", "SUNRISE", "DHUHR"], "v2": ["ASR", "MAGHRIB", "ISHA"],
        "zikir": "📿 TASBEEH (Click)", "sifirla": "RESET", "ay_110": "You are the best nation produced for mankind..."
    },
    "العربية": {
        "v1": ["الفجر", "الشروق", "الظهر"], "v2": ["العصر", "المغرب", "العشاء"],
        "zikir": "📿 المسبحة (اضغط)", "sifirla": "إعادة", "ay_110": "كُنتُمْ خَيْرَ أُمَّةٍ أُخْرِجَتْ لِلنَّاسِ..."
    }
}

# --- 3. CSS (GELİŞMİŞ GÖRÜNÜM) ---
st.markdown("""
    <style>
    .stApp { background: #0a0e0d; color: white; }
    .besmele { text-align: center; color: #d4af37 !important; font-size: 3.5rem; font-weight: bold; margin: 10px 0; }
    .ayet-box { text-align: center; color: #ffffff !important; font-size: 1.4rem; background: rgba(212,175,55,0.2); padding: 25px; border-radius: 20px; border: 2px solid #d4af37; margin-bottom: 30px; }
    .vakit-card { background: #ffffff; border-radius: 15px; padding: 20px; text-align: center; border-bottom: 5px solid #d4af37; margin: 10px 0; }
    .vakit-card div { color: #000000 !important; font-size: 1.5rem; font-weight: 800; }
    .vakit-card span { color: #d4af37 !important; font-size: 2.2rem; font-weight: 900; }
    .zikir-btn { background: radial-gradient(#d4af37, #b8860b); border-radius: 50%; width: 220px; height: 220px; border: 8px solid #fff; color: white; font-size: 3rem; font-weight: bold; cursor: pointer; box-shadow: 0 10px 20px rgba(0,0,0,0.5); transition: 0.1s; }
    .zikir-btn:active { transform: scale(0.9); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    sel_lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English", "العربية"])
    L = lang_data[sel_lang]
    sehir = st.selectbox("📍 Şehir Seç", sehirler_81, index=sehirler_81.index("Istanbul"))
    st.info("Zikirmatik artık ana ekranın en altında!")

# --- 5. ANA EKRAN ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
st.markdown(f"<div class='ayet-box'><b>Ali İmran 110:</b><br>{L['ay_110']}</div>", unsafe_allow_html=True)

data = get_prayer_data(sehir)
if data:
    v = data['timings']
    t_h = data['date']['hijri']
    st.markdown(f"<p style='text-align:center; font-size:1.5rem;'>🌙 {t_h['day']} {t_h['month']['ar']} {t_h['year']} (Hicri)</p>", unsafe_allow_html=True)

    # 3+3 Vakit Düzeni
    row1 = st.columns(3)
    v1_vals = [v['Fajr'], v['Sunrise'], v['Dhuhr']]
    for i, name in enumerate(L['v1']):
        row1[i].markdown(f'<div class="vakit-card"><div>{name}</div><span>{v1_vals[i]}</span></div>', unsafe_allow_html=True)

    row2 = st.columns(3)
    v2_vals = [v['Asr'], v['Maghrib'], v['Isha']]
    for i, name in enumerate(L['v2']):
        row2[i].markdown(f'<div class="vakit-card"><div>{name}</div><span>{v2_vals[i]}</span></div>', unsafe_allow_html=True)

    # Geri Sayım (Sadeleştirilmiş)
    st.components.v1.html(f"""
        <div style="text-align:center; color:#fbbf24; font-size:40px; font-weight:bold; font-family:monospace; margin:20px 0;" id="timer">00:00:00</div>
        <script>
            const times = {json.dumps(v)};
            function update() {{
                const now = new Date();
                const s = now.getHours()*3600 + now.getMinutes()*60 + now.getSeconds();
                let target = 0;
                // Basit bir sonraki vakit bulucu
                const vks = [times.Fajr, times.Sunrise, times.Dhuhr, times.Asr, times.Maghrib, times.Isha];
                for(let vt of vks) {{
                    let [h,m] = vt.split(':'); let vs = parseInt(h)*3600+parseInt(m)*60;
                    if(vs > s) {{ target = vs; break; }}
                }}
                if(target === 0) target = 86400 + (parseInt(times.Fajr.split(':')[0])*3600);
                let diff = target - s;
                let h=Math.floor(diff/3600), m=Math.floor((diff%3600)/60), sc=diff%60;
                document.getElementById('timer').innerHTML = (h<10?'0'+h:h)+":"+(m<10?'0'+m:m)+":"+(sc<10?'0'+sc:sc);
            }} setInterval(update, 1000); update();
        </script>
    """, height=80)

    # Haftalık (Bugünden İtibaren)
    st.divider()
    st.subheader("🗓️ Haftalık Vakitler (Bugünden İtibaren)")
    h_data = get_weekly_data(sehir)
    if h_data:
        # Bugünden itibaren 7 günü filtrele
        today_day = int(datetime.now().day)
        weekly_slice = [d for d in h_data if int(d['date']['gregorian']['day']) >= today_day][:7]
        tablo = [[d['date']['gregorian']['day']+" "+d['date']['gregorian']['month']['en'], d['timings']['Fajr'], d['timings']['Dhuhr'], d['timings']['Asr'], d['timings']['Maghrib'], d['timings']['Isha']] for d in weekly_slice]
        st.table(tablo)

    # --- ZİKİRMATİK (YENİ TASARIM & TİTREŞİM) ---
    st.divider()
    st.markdown(f"<h2 style='text-align:center;'>{L['zikir']}</h2>", unsafe_allow_html=True)
    
    if 'zk_count' not in st.session_state: st.session_state.zk_count = 0

    col_z1, col_z2, col_z3 = st.columns([1, 2, 1])
    with col_z2:
        # Titreşim (Vibrate) JavaScript ile sağlanır
        if st.button(f"{st.session_state.zk_count}", key="zikir_ana_btn", help="Tıkla ve Zikir Çek", use_container_width=True):
            st.session_state.zk_count += 1
            st.components.v1.html("<script>window.navigator.vibrate(50);</script>", height=0)
            st.rerun()
        
        if st.button(L['sifirla'], key="res_btn"):
            st.session_state.zk_count = 0
            st.rerun()

else:
    st.error("Veri yüklenemedi, lütfen sayfayı yenileyin.")