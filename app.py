import streamlit as st
import requests
import json
import os
from datetime import datetime

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# Arka Plan Görseli (Mavi Camii)
BG_IMAGE = "https://cdn.pixabay.com/photo/2023/03/05/13/21/mosque-7831383_1280.png"

# --- 2. DİL VE ŞEHİR SEÇİMİ (SIDEBAR) ---
st.sidebar.title("⚙️ Ayarlar / Settings")
dil = st.sidebar.radio("Dil Seçin / Language", ["Türkçe", "English"])
sehir = st.sidebar.selectbox("📍 Şehir / City", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])

# Sözlükler
texts = {
    "Türkçe": {
        "vakit_kalan": "VAKTİNE KALAN SÜRE", "sabah": "SABAH", "gunes": "GÜNEŞ", "ogle": "ÖĞLE", "ikindi": "İKİNDİ", "aksam": "AKŞAM", "yatsi": "YATSI",
        "esma": "ESMAÜL HÜSNA", "zikir": "ZİKİRMATİK", "sureler": "SÜRELER", "liste_btn": "TÜM LİSTE", "sure_btn": "SURE SEÇ", "zikir_btn": "➕ ZİKİR EKLE"
    },
    "English": {
        "vakit_kalan": "TIME REMAINING TO", "sabah": "FAJR", "gunes": "SUNRISE", "ogle": "DHUHR", "ikindi": "ASR", "aksam": "MAGHRIB", "yatsi": "ISHA",
        "esma": "99 NAMES", "zikir": "TASBIH", "sureler": "SURAH", "liste_btn": "ALL LIST", "sure_btn": "SELECT SURAH", "zikir_btn": "➕ ADD TASBIH"
    }
}
t = texts[dil]

# --- 3. KESİN ARKA PLAN VE MODÜL CSS ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.8)), url("{BG_IMAGE}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    .vakit-box {{
        background: #fdf6e3; border-radius: 12px; padding: 10px; text-align: center;
        border: 1px solid #d4af37; margin-bottom: 10px;
    }}
    .vakit-name {{ color: #7f8c8d; font-size: 11px; font-weight: bold; }}
    .vakit-val {{ color: #2c3e50; font-size: 20px; font-weight: bold; }}
    
    .module-card {{
        background: rgba(21, 62, 53, 0.95); border-radius: 15px; padding: 15px; 
        text-align: center; border: 1px solid #d4af37; min-height: 250px; color: white;
    }}
    .module-head {{ color: #fbbf24; font-weight: bold; border-bottom: 1px solid rgba(251,191,36,0.3); padding-bottom: 5px; margin-bottom: 10px; }}
    
    .stButton>button {{
        width: 100%; border-radius: 20px; background: #d4af37; color: white; border: none; font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. VERİ ÇEKME ---
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    v_order = [(t['sabah'], v['Fajr']), (t['gunes'], v['Sunrise']), (t['ogle'], v['Dhuhr']), (t['ikindi'], v['Asr']), (t['aksam'], v['Maghrib']), (t['yatsi'], v['Isha'])]

    # ÜST PANEL: GERİ SAYIM
    st.markdown(f"<h1 style='text-align:center; color:white;'>{sehir}</h1>", unsafe_allow_html=True)
    
    countdown_js = f"""
    <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 20px;">
        <div style="border: 4px solid #d4af37; border-radius: 50%; width: 180px; height: 180px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.5);">
            <div style="color: white; font-size: 10px;">{t['vakit_kalan']}</div>
            <div id="tmr" style="color: #fbbf24; font-size: 35px; font-weight: bold; font-family: monospace;">00:00:00</div>
        </div>
    </div>
    <script>
        const v = {json.dumps({n: x for n, x in v_order})};
        function update() {{
            const now = new Date();
            const s = now.getHours()*3600 + now.getMinutes()*60 + now.getSeconds();
            let target = null;
            for(let k in v) {{
                let [h,m] = v[k].split(':');
                let vs = parseInt(h)*3600 + parseInt(m)*60;
                if(vs > s) {{ target = vs; break; }}
            }}
            if(!target) {{ let [h,m] = v['{t['sabah']}'].split(':'); target = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = target - s;
            let h = Math.floor(d/3600); let m = Math.floor((d%3600)/60); let sec = d%60;
            document.getElementById('tmr').innerHTML = (h<10?'0'+h:h)+":"+(m<10?'0'+m:m)+":"+(sec<10?'0'+sec:sec);
        }}
        setInterval(update, 1000); update();
    </script>
    """
    st.components.v1.html(countdown_js, height=200)

    # VAKİT KUTULARI
    c_v = st.columns(6)
    for i in range(6):
        with c_v[i]:
            st.markdown(f'<div class="vakit-box"><div class="vakit-name">{v_order[i][0]}</div><div class="vakit-val">{v_order[i][1]}</div></div>', unsafe_allow_html=True)

except:
    st.error("Bağlantı Hatası!")

# --- 5. YAN YANA ÜÇLÜ MODÜL (ALT KISIM) ---
st.write("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f'<div class="module-card"><div class="module-head">{t["esma"]}</div><br><h1 style="color:#fbbf24;">الله</h1><p>Ya Rahman, Ya Rahim...</p></div>', unsafe_allow_html=True)
    if st.button(t["liste_btn"]):
        st.info("99 Esma listesi burada açılacak.")

with col2:
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f'<div class="module-card"><div class="module-head">{t["zikir"]}</div><br><h1 style="font-size:60px; color:#fbbf24;">{st.session_state.zk}</h1></div>', unsafe_allow_html=True)
    if st.button(t["zikir_btn"]):
        st.session_state.zk += 1
        st.rerun()

with col3:
    st.markdown(f'<div class="module-card"><div class="module-head">{t["sureler"]}</div><br><p>Yasin, Mülk, Nebe ve Kısa Sureler</p></div>', unsafe_allow_html=True)
    if st.button(t["sure_btn"]):
        st.info("Sure seçme menüsü burada açılacak.")