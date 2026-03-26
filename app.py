import streamlit as st
import requests
import json
import os
from datetime import datetime
import random

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# Gelişmiş Mobil CSS
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Üst Bilgi Paneli */
    .hero-section {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 25px; border-radius: 20px; text-align: center;
        border: 1px solid #334155; margin-bottom: 20px; box-shadow: 0 10px 15px rgba(0,0,0,0.3);
    }
    .next-label { color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 2px; }
    .countdown-timer { color: #fbbf24; font-size: 40px; font-weight: bold; margin: 5px 0; font-family: monospace; }
    
    /* Vakit Kartları Grid */
    .vakit-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px; }
    .vakit-item {
        background: #1e293b; padding: 12px; border-radius: 15px;
        text-align: center; border: 1px solid #334155;
    }
    .v_name { color: #94a3b8; font-size: 11px; font-weight: bold; }
    .v_time { color: white; font-size: 18px; font-weight: bold; }

    /* Bilgi Kartları */
    .info-box {
        background: #1c212b; padding: 20px; border-radius: 15px;
        border-left: 5px solid #10b981; margin-bottom: 15px;
    }
    
    /* Buton Tasarımı */
    .stButton>button {
        width: 100%; border-radius: 15px; background: linear-gradient(90deg, #10b981, #059669);
        color: white; font-weight: bold; border: none; height: 50px; font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
DB_FILE = "user_data.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"zikir": 0, "dualar": []}, f)

def load_data():
    with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_data(d):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# --- 3. İÇERİKLER ---
ayetler = ["'Şüphesiz güçlükle beraber bir kolaylık vardır.' (İnşirah, 5)", "'Allah sabredenlerle beraberdir.' (Bakara, 153)"]
hadisler = ["'Ameller niyetlere göredir.'", "'Sizin en hayırlınız, Kur'an'ı öğrenen ve öğreteninizdir.'"]
sureler = {
    "İhlas Suresi": "Kul hüvallahü ehad. Allahüssamed. Lem yelid ve lem yüled. Ve lem yekün lehü küfüven ehad.",
    "Felak Suresi": "Kul eüzü birabbil felak. Min şerri ma halak. Ve min şerri ğasikın iza vekab...",
    "Nas Suresi": "Kul eüzü birabbin nas. Melikin nas. İlahin nas. Min şerril vesvasil hannas..."
}

# --- 4. ANA ARAYÜZ ---
st.sidebar.title("⚙️ Ayarlar")
sehir = st.sidebar.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Trabzon"])

# API'den Vakitleri Çek
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    h = res['date']['hijri']
    v_order = [("İmsak", v['Fajr']), ("Güneş", v['Sunrise']), ("Öğle", v['Dhuhr']), ("İkindi", v['Asr']), ("Akşam", v['Maghrib']), ("Yatsı", v['Isha'])]
    
    # ⏳ CANLI GERİ SAYIM (JavaScript)
    js_vakitler = {name: time for name, time in v_order}
    st.markdown(f"""
    <div class="hero-section">
        <div class="next-label">SIRADAKİ VAKİT İÇİN KALAN SÜRE</div>
        <div id="timer" class="countdown-timer">00:00:00</div>
        <div style="color:#10b981; font-weight:bold;">{h['day']} {h['month']['en']} {h['year']}</div>
    </div>
    <script>
    const v = {json.dumps(js_vakitler)};
    function update() {{
        const now = new Date();
        const s = now.getHours()*3600 + now.getMinutes()*60 + now.getSeconds();
        let target = null;
        for(let n in v) {{
            let [h,m] = v[n].split(':');
            let vs = parseInt(h)*3600 + parseInt(m)*60;
            if(vs > s) {{ target = vs; break; }}
        }}
        if(!target) {{
            let [h,m] = v['İmsak'].split(':');
            target = parseInt(h)*3600 + parseInt(m)*60 + 86400;
        }}
        let d = target - s;
        let h = Math.floor(d/3600);
        let m = Math.floor((d%3600)/60);
        let sec = d%60;
        document.getElementById('timer').innerHTML = 
            (h<10?'0'+h:h)+":"+(m<10?'0'+m:m)+":"+(sec<10?'0'+sec:sec);
    }}
    setInterval(update, 1000); update();
    </script>
    """, unsafe_allow_html=True)

    # 📱 VAKİT KUTUCUKLARI (Grid)
    cols = st.columns(3)
    for i, (name, time) in enumerate(v_order):
        with cols[i % 3]:
            st.markdown(f'<div class="vakit-item"><div class="v_name">{name}</div><div class="v_time">{time}</div></div>', unsafe_allow_html=True)

except: st.error("Bağlantı hatası!")

# --- SEKME SİSTEMİ (Tüm Kayıp Özellikler Burada) ---
t1, t2, t3, t4 = st.tabs(["📿 Zikirmatik", "📖 Ayet/Sure/İlmihal", "📝 Dualarım", "📻 Radyo"])

with t1:
    st.markdown(f"<h1 style='text-align:center; color:#10b981;'>{data['zikir']}</h1>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK"):
        data['zikir'] += 1
        save_data(data)
        st.rerun()
    if st.button("🔄 Sıfırla"):
        data['zikir'] = 0
        save_data(data)
        st.rerun()

with t2:
    st.markdown(f'<div class="info-box"><b>📖 Günün Ayeti:</b><br>{random.choice(ayetler)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-box"><b>💬 Günün Hadisi:</b><br>{random.choice(hadisler)}</div>', unsafe_allow_html=True)
    
    with st.expander("📜 Namaz Sureleri (Son 10)"):
        for ad, metin in sureler.items():
            st.write(f"**{ad}:** {metin}")
            st.divider()
            
    with st.expander("📚 Temel İlmihal Bilgileri"):
        st.write("**İslamın Şartları:** 1. Şehadet, 2. Namaz, 3. Zekat, 4. Oruç, 5. Hac.")
        st.write("**Abdestin Farzları:** 1. Yüzü yıkamak, 2. Kolları yıkamak, 3. Başın 1/4'ünü meshetmek, 4. Ayakları yıkamak.")

with t3:
    y_dua = st.text_input("Duanızı yazın...")
    if st.button("Kaydet") and y_dua:
        data['dualar'].append(y_dua)
        save_data(data)
        st.rerun()
    for d in reversed(data['dualar'][-5:]):
        st.caption(f"🙏 {d}")

with t4:
    st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")
    st.write("📻 Diyanet Radyo - Canlı Yayın")