import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda Pro Max", page_icon="🕋", layout="wide")

# --- 2. DİL VE ÇEVİRİ SÖZLÜĞÜ ---
lang_data = {
    "Türkçe": {
        "vakitler": ["İMSAK", "GÜNEŞ", "ÖĞLE", "İKİNDİ", "AKŞAM", "YATSI"],
        "baslik": "İslami Portal",
        "sehir_sec": "📍 Şehir Seç",
        "dil_sec": "🌐 Dil Seçin",
        "zikir_baslik": "📿 Zikirmatik",
        "zikir_cek": "Zikir Çek",
        "sifirla": "Sıfırla",
        "haftalik_tablo": "🗓️ Haftalık Namaz Vakitleri",
        "kaza_baslik": "📊 Kaza Takibi",
        "ay_110": "Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz; iyiliği emreder, kötülükten meneder ve Allah’a inanırsınız.",
        "hata": "Bağlantı hatası oluştu.",
        "ezan_sesi": "📢 Ezan Sesi",
        "hatirlatici": "⏳ 30 Dk Hatırlatıcı"
    },
    "English": {
        "vakitler": ["FAJR", "SUNRISE", "DHUHR", "ASR", "MAGHRIB", "ISHA"],
        "baslik": "Islamic Portal",
        "sehir_sec": "📍 Select City",
        "dil_sec": "🌐 Select Language",
        "zikir_baslik": "📿 Tasbeeh Counter",
        "zikir_cek": "Count",
        "sifirla": "Reset",
        "haftalik_tablo": "🗓️ Weekly Prayer Times",
        "kaza_baslik": "📊 Qaza Prayers",
        "ay_110": "You are the best nation produced [as an example] for mankind. You enjoin what is right and forbid what is wrong and believe in Allah.",
        "hata": "Connection error occurred.",
        "ezan_sesi": "📢 Adhan Sound",
        "hatirlatici": "⏳ 30 Min Reminder"
    },
    "العربية": {
        "vakitler": ["الفجر", "الشروق", "الظهر", "العصر", "المغرب", "العشاء"],
        "baslik": "البوابة الإسلامية",
        "sehir_sec": "📍 اختر المدينة",
        "dil_sec": "🌐 اختر اللغة",
        "zikir_baslik": "📿 المسبحة الإلكترونية",
        "zikir_cek": "تسبيح",
        "sifirla": "إعادة تعيين",
        "haftalik_tablo": "🗓️ مواقيت الصلاة الأسبوعية",
        "kaza_baslik": "📊 صلوات القضاء",
        "ay_110": "كُنتُمْ خَيْرَ أُمَّةٍ أُخْرِجَتْ لِلنَّاسِ تَأْمُرُونَ بِالْمَعْرُوفِ وَتَنْهَوْنَ عَنِ الْمُنكَرِ وَتُؤْمِنُونَ بِاللَّهِ",
        "hata": "حدث خطا في الاتصال",
        "ezan_sesi": "📢 صوت الأذان",
        "hatirlatici": "⏳ تذكير ٣٠ دقيقة"
    }
}

# --- 3. CSS (TASARIM) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2000") !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .besmele { text-align: center; color: #d4af37 !important; font-size: 3rem; font-family: 'Times New Roman', serif; margin-top: 10px; font-style: italic; text-shadow: 2px 2px 10px rgba(212,175,55,0.4); }
    .ayet-box { text-align: center; color: #f1f1f1 !important; font-size: 1.2rem; background: rgba(212,175,55,0.1); border: 1px solid #d4af37; padding: 15px; border-radius: 15px; margin: 20px auto; max-width: 800px; line-height: 1.6; }
    .vakit-box { background: rgba(253, 246, 227, 0.98); border-radius: 12px; padding: 15px; text-align: center; border: 2px solid #d4af37; }
    .vakit-box div { color: #1a2a24 !important; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: rgba(10, 30, 25, 0.98) !important; border-right: 2px solid #d4af37; }
    .stExpander { background-color: #ffffff !important; border-radius: 8px !important; border: 1px solid #d4af37; }
    .stExpander p, .stExpander span, .stExpander div { color: #000000 !important; text-shadow: none !important; }
    .zikir-ana { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 20px; text-align: center; border: 2px solid #d4af37; margin-top: 40px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    sel_lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English", "العربية"])
    L = lang_data[sel_lang]
    
    st.markdown(f"<h2 style='text-align:center;'>{L['baslik']}</h2>", unsafe_allow_html=True)
    sehir = st.selectbox(L['sehir_sec'], sehirler_81, index=sehirler_81.index("Istanbul"))
    
    st.write("---")
    
    with st.expander("📖 Son On Sure", expanded=False):
        for s_ad, s_içerik in son_on_sure_data.items():
            st.markdown(f"**{s_ad}**")
            st.caption(s_içerik['oku'])
            st.write(f"*Anlamı:* {s_içerik['meal']}")
            st.write("---")

    with st.expander(L['kaza_baslik'], expanded=False):
        for i, kv in enumerate(L['vakitler']):
            k_key = f"kaza_v_{kv}_{sel_lang}"
            if k_key not in st.session_state: st.session_state[k_key] = 0
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{kv}**")
            if c2.button(f"{st.session_state[k_key]}", key=f"btn_k_{i}_{sel_lang}"): 
                st.session_state[k_key] += 1; st.rerun()

    ezan_on = st.toggle(L['ezan_sesi'], value=True)
    uyari_on = st.toggle(L['hatirlatici'], value=True)

# --- 5. ANA EKRAN ÜST KISIM ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)
st.markdown(f"<div class='ayet-box'><b>Ali İmran 110:</b><br>{L['ay_110']}</div>", unsafe_allow_html=True)

# --- 6. VERİ ÇEKME VE GÖRSELLEŞTİRME ---
try:
    # Günlük Vakitler
    url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
    data = requests.get(url).json()['data']
    v = data['timings']
    
    # Haftalık Vakitler
    h_url = f"http://api.aladhan.com/v1/calendarByCity?city={sehir}&country=Turkey&method=13"
    h_data = requests.get(h_url).json()['data']

    v_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    v_values = [v[k] for k in v_keys]
    v_dict = dict(zip(L['vakitler'], v_values))

    # Vakit Kartları
    st.markdown(f"<h1 style='text-align:center;'>{sehir.upper()}</h1>", unsafe_allow_html=True)
    cols = st.columns(6)
    for i, (name, time_val) in enumerate(v_dict.items()):
        cols[i].markdown(f'<div class="vakit-box"><div>{name}</div><div style="font-size:24px;">{time_val}</div></div>', unsafe_allow_html=True)

    # Geri Sayım Halka
    st.components.v1.html(f"""
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <div style="border: 6px solid #d4af37; border-radius: 50%; width: 150px; height: 150px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.7); box-shadow: 0 0 25px #d4af37;">
            <div id="c" style="color: #fbbf24; font-size: 32px; font-weight: bold; font-family: monospace;">00:00:00</div>
        </div>
    </div>
    <script>
        const v = {json.dumps(v_dict)};
        function u() {{
            const n = new Date(); const s = n.getHours()*3600 + n.getMinutes()*60 + n.getSeconds();
            let t = null; for(let k in v) {{ let [h,m] = v[k].split(':'); let vs = parseInt(h)*3600+parseInt(m)*60; if(vs>s) {{ t=vs; break; }} }}
            if(!t) {{ let [h,m] = v['{L['vakitler'][0]}'].split(':'); t = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = t-s; let h=Math.floor(d/3600), m=Math.floor((d%3600)/60), sc=d%60;
            document.getElementById('c').innerHTML = (h<10?'0'+h:h)+":"+(m<10?'0'+m:m)+":"+(sc<10?'0'+sc:sc);
        }} setInterval(u, 1000); u();
    </script>""", height=180)

    # --- 7. HAFTALIK ÇİZELGE ---
    st.subheader(L['haftalik_tablo'])
    weekly_list = []
    for day_data in h_data[:7]:
        day_name = day_data['date']['gregorian']['day'] + " " + day_data['date']['gregorian']['month']['en']
        t = day_data['timings']
        weekly_list.append([day_name, t['Fajr'], t['Sunrise'], t['Dhuhr'], t['Asr'], t['Maghrib'], t['Isha']])
    
    st.table(weekly_list)

    # --- 8. ANA EKRAN ZİKİRMATİK ---
    st.markdown(f"<div class='zikir-ana'><h3>{L['zikir_baslik']}</h3>", unsafe_allow_html=True)
    if 'zk_main' not in st.session_state: st.session_state.zk_main = 0
    
    st.markdown(f"<h1 style='color:#d4af37; font-size:4rem;'>{st.session_state.zk_main}</h1>", unsafe_allow_html=True)
    zc1, zc2 = st.columns(2)
    if zc1.button(L['zikir_cek'], key="main_zk_btn", use_container_width=True):
        st.session_state.zk_main += 1
        st.rerun()
    if zc2.button(L['sifirla'], key="main_zk_res", use_container_width=True):
        st.session_state.zk_main = 0
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

except Exception:
    st.error(L['hata'])

time.sleep(60)
st.rerun()