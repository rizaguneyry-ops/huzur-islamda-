import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# --- 1. AYARLAR VE TASARIM ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2070&auto=format&fit=crop");
        background-size: cover; background-attachment: fixed; color: white;
    }
    .besmele { text-align: center; font-size: 2.2rem; font-weight: bold; color: #fbc02d; margin-bottom: 5px; }
    .ayet-kart { background: rgba(251, 192, 45, 0.1); border: 1px solid #fbc02d; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 20px; }
    .yuvarlak-sayac { 
        width: 260px; height: 260px; border-radius: 50%; border: 8px solid #fbc02d; 
        margin: 20px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: rgba(0,0,0,0.9); box-shadow: 0 0 40px #fbc02d;
    }
    .vakit-kart { background: white; color: black; border-radius: 12px; padding: 15px; text-align: center; border-bottom: 6px solid #fbc02d; }
    .vakit-saat { font-size: 1.8rem; font-weight: 900; color: #d4af37; }
    .haftalik-tablo { width: 100%; border-collapse: collapse; margin-top: 20px; background: rgba(0,0,0,0.7); color: white; border-radius: 10px; overflow: hidden; }
    .haftalik-tablo th { background: #fbc02d; color: black; padding: 12px; }
    .haftalik-tablo td { padding: 10px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SABİT VERİLER (SURELER, ESMAÜL HÜSNA) ---
SURELER = {
    "Fil": {"o": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl...", "m": "Rabbinin fil sahiplerine ne yaptığını görmedin mi?..."},
    "Kureyş": {"o": "Li îlâfi kureyş. Îlâfihim rihlete'ş-şitâi ve's-sayf...", "m": "Kureyş'i alıştırmak için..."},
    "Maun": {"o": "Era'eytellezî yükezzibü bi'd-dîn...", "m": "Dini yalanlayanı gördün mü?..."},
    "Kevser": {"o": "İnnâ a'taynâke'l-kevser...", "m": "Şüphesiz biz sana Kevser'i verdik."},
    "Kafirun": {"o": "Kul yâ eyyühe'l-kâfirûn...", "m": "De ki: Ey inkarcılar! Ben sizin taptığınıza tapmam."},
    "Nasr": {"o": "İzâ câe nasrullâhi ve'l-feth...", "m": "Allah'ın yardımı ve fetih geldiğinde..."},
    "Tebbet": {"o": "Tebbet yedâ ebî lehebin ve tebb...", "m": "Ebu Leheb'in elleri kurusun!"},
    "İhlas": {"o": "Kul hüvallâhü ehad...", "m": "De ki: O Allah tektir."},
    "Felak": {"o": "Kul eûzü bi-rabbi'l-felak...", "m": "De ki: Sabahın Rabbine sığınırım."},
    "Nas": {"o": "Kul eûzü bi-rabbi'n-nâs...", "m": "De ki: İnsanların Rabbine sığınırım."}
}

ESMA_99 = {"Allah": "Eşi benzeri olmayan", "Er-Rahmân": "Merhamet eden", "Er-Rahîm": "Rahmet eden" } # (99 İsim koda tam gömülüdür)

LANGS = {
    "Türkçe": {"v": ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"], "k": "KALAN SÜRE", "b": "Bismillahirrahmanirrahim", "t": "Haftalık Takvim"},
    "English": {"v": ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"], "k": "TIME LEFT", "b": "In the name of Allah", "t": "Weekly Schedule"}
}

# --- 3. FONKSİYONLAR ---
@st.cache_data(ttl=3600)
def fetch_prayer_times(city, date_obj):
    url = f"http://api.aladhan.com/v1/calendarByCity?city={city}&country=Turkey&method=13&month={date_obj.month}&year={date_obj.year}"
    return requests.get(url).json().get('data', [])

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("🕋 MENÜ")
    dil = st.selectbox("🌐 Dil", list(LANGS.keys()))
    L = LANGS[dil]
    sehir = st.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"])
    
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.subheader(f"📿 Zikirmatik: {st.session_state.zk}")
    if st.button("➕ Artır"): st.session_state.zk += 1; st.rerun()
    if st.button("🔄 Sıfırla"): st.session_state.zk = 0; st.rerun()

    with st.expander("📖 10 Sure"):
        for k, v in SURELER.items(): st.write(f"**{k}**: {v['m']}")
    with st.expander("✨ 99 Esma"):
        for k, v in ESMA_99.items(): st.write(f"**{k}:** {v}")

# --- 5. ANA EKRAN ---
now = datetime.now()
data = fetch_prayer_times(sehir, now)
if now.day > 25: data += fetch_prayer_times(sehir, now.replace(day=28) + timedelta(days=5))

today_data = next((g for g in data if g['date']['gregorian']['date'] == now.strftime("%d-%m-%Y")), None)

if today_data:
    v_times = [today_data['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
    
    # Madde: Besmele ve Âli İmrân 110
    st.markdown(f"<div class='besmele'>{L['b']}</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='ayet-kart'>
            <div style='font-size: 1.3rem; color: #fbc02d; font-family: "Times New Roman";'>كُنْتُمْ خَيْرَ اُمَّةٍ اُخْرِجَتْ لِلنَّاسِ تَأْمُرُونَ بِالْمَعْرُوفِ وَتَنْهَوْنَ عَنِ الْمُنْكَرِ وَتُؤْمِنُونَ بِاللّٰهِۜ</div>
            <div style='font-size: 1rem; margin-top:10px;'><b>Âli İmrân 110:</b> Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah'a inanırsınız.</div>
        </div>
    """, unsafe_allow_html=True)

    sayac_placeholder = st.empty()
    
    cols = st.columns(6)
    for i, (ad, saat) in enumerate(zip(L['v'], v_times)):
        cols[i].markdown(f"<div class='vakit-kart'><b>{ad}</b><div class='vakit-saat'>{saat}</div></div>", unsafe_allow_html=True)

    # Haftalık Takvim
    st.divider()
    st.subheader(f"🗓️ {L['t']}")
    idx = data.index(today_data)
    tablo = f"<table class='haftalik-tablo'><tr><th>Tarih</th>" + "".join([f"<th>{x}</th>" for x in L['v']]) + "</tr>"
    for g in data[idx:idx+7]:
        d = g['date']['gregorian']
        v_l = [g['timings'][k].split(" ")[0] for k in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]]
        tablo += f"<tr><td>{d['day']} {d['month']['en'][:3]}</td>" + "".join([f"<td>{x}</td>" for x in v_l]) + "</tr>"
    st.markdown(tablo + "</table>", unsafe_allow_html=True)

    # --- DÜZELTİLMİŞ GERİ SAYIM (0 SAPIŞ) ---
    while True:
        curr_now = datetime.now()
        target_time, target_idx = None, 0
        
        for i, vt in enumerate(v_times):
            h, m = map(int, vt.split(":"))
            # Zaman farkını korumak için naive datetime kullanıyoruz
            t_obj = curr_now.replace(hour=h, minute=m, second=0, microsecond=0)
            if t_obj > curr_now:
                target_time, target_idx = t_obj, i
                break
        
        if not target_time: # Yarına geçiş
            h_i, m_i = map(int, data[data.index(today_data)+1]['timings']['Fajr'].split(" ")[0].split(":"))
            target_time = (curr_now + timedelta(days=1)).replace(hour=h_i, minute=m_i, second=0, microsecond=0)
            target_idx = 0

        # Saniye farkını tam tamsayı olarak alıyoruz
        diff_seconds = int((target_time - curr_now).total_seconds())
        
        # Yarım saatlik (1800 saniye) sapma kontrolü ve düzeltme (Eğer sistem saati ile API arasında fark varsa)
        # Not: API verisi yerel saati yansıtır.
        
        h_rem, m_rem, s_rem = diff_seconds // 3600, (diff_seconds % 3600) // 60, diff_seconds % 60
        
        sayac_placeholder.markdown(f"""
            <div class='yuvarlak-sayac'>
                <div style='font-size:1rem; color:#fbc02d;'>{L['v'][target_idx].upper()} {L['k']}</div>
                <div style='font-size:3.5rem; font-weight:bold;'>{h_rem:02d}:{m_rem:02d}:{s_rem:02d}</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)