import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# --- 2. DİL VE ŞEHİR AYARLARI ---
# Tüm diller ve çevirileri
languages = {
    "Türkçe": {"vakit": "VAKTİNE KALAN", "zikir": "ZİKİRMATİK", "esma": "ESMAÜL HÜSNA", "kuran": "SON 10 SURE", "artir": "ARTIR", "sifirla": "SIFIRLA", "liste": "TÜM LİSTE"},
    "English": {"vakit": "TIME REMAINING", "zikir": "TASBIH", "esma": "99 NAMES", "kuran": "LAST 10 SURAH", "artir": "COUNT", "sifirla": "RESET", "liste": "ALL LIST"},
    "العربية": {"vakit": "الوقت المتبقي", "zikir": "المسبحة", "esma": "أسماء الله", "kuran": "آخر 10 سور", "artir": "تسبيح", "sifirla": "إعادة", "liste": "القائمة"},
    "Deutsch": {"vakit": "VERBLEIBENDE ZEIT", "zikir": "ZÄHLER", "esma": "99 NAMEN", "kuran": "LETZTE 10 SUREN", "artir": "ZÄHLEN", "sifirla": "RESET", "liste": "LISTE"},
    "Español": {"vakit": "TIEMPO RESTANTE", "zikir": "TASBIH", "esma": "99 NOMBRES", "kuran": "10 SURAS", "artir": "CONTAR", "sifirla": "RESETEAR", "liste": "VER TODO"},
    "Italiano": {"vakit": "TEMPO RIMANENTE", "zikir": "TASBIH", "esma": "99 NOMI", "kuran": "10 SURE", "artir": "CONTA", "sifirla": "RESET", "liste": "LISTA"},
    "中文": {"vakit": "剩余时间", "zikir": "念珠", "esma": "真主尊名", "kuran": "最后10章", "artir": "计数", "sifirla": "重置", "liste": "全部列表"}
}

st.sidebar.title("🌙 Ayarlar")
sel_lang = st.sidebar.selectbox("Dil / Language", list(languages.keys()))
sehir = st.sidebar.selectbox("Şehir / City", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])
L = languages[sel_lang]

# --- 3. KESİN ARKA PLAN VE MODÜL CSS ---
st.markdown(f"""
    <style>
    /* Arka Planı Zorla Uygula */
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1542810634-71277d95dcbb?q=80&w=2000&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    /* Vakit Kutuları (Krem) */
    .vakit-item {{
        background: rgba(253, 246, 227, 0.95); border-radius: 12px; padding: 12px;
        text-align: center; border: 1px solid #d4af37; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }}
    /* Alt Modüller (Zümrüt Yeşili) */
    .module-card {{
        background: rgba(15, 45, 35, 0.95); border-radius: 20px; padding: 20px;
        border: 1px solid #d4af37; color: white; min-height: 400px; text-align: center;
    }}
    .scroll-box {{
        height: 220px; overflow-y: auto; text-align: left; background: rgba(0,0,0,0.3);
        padding: 15px; border-radius: 10px; font-size: 0.9rem; margin-top: 10px;
    }}
    .zikir-val {{ font-size: 70px; color: #fbbf24; font-weight: bold; margin: 15px 0; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. VERİ ÇEKME VE BAŞLIK ---
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    g = res['date']['gregorian']
    h = res['date']['hijri']

    # Şehir ve Tarih
    st.markdown(f"""
        <div style='text-align:center; color:white;'>
            <h1 style='margin-bottom:0;'>{sehir.upper()}</h1>
            <p style='color:#fbbf24; font-size:1.1rem;'>{g['day']} {g['month']['en']} {g['year']} | {h['day']} {h['month']['en']} {h['year']}</p>
        </div>
    """, unsafe_allow_html=True)

    # Canlı Geri Sayım Halkası
    v_order = {"SABAH": v['Fajr'], "GÜNEŞ": v['Sunrise'], "ÖĞLE": v['Dhuhr'], "İKİNDİ": v['Asr'], "AKŞAM": v['Maghrib'], "YATSI": v['Isha']}
    js_countdown = f"""
    <div style="display: flex; justify-content: center; margin: 25px 0;">
        <div style="border: 5px solid #d4af37; border-radius: 50%; width: 190px; height: 190px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.5); box-shadow: 0 0 20px rgba(212,175,55,0.4);">
            <div style="color: white; font-size: 11px; letter-spacing: 1px;">{L['vakit']}</div>
            <div id="clock" style="color: #fbbf24; font-size: 38px; font-weight: bold; font-family: monospace;">00:00:00</div>
        </div>
    </div>
    <script>
        const v = {json.dumps(v_order)};
        function upd() {{
            const n = new Date(); const s = n.getHours()*3600 + n.getMinutes()*60 + n.getSeconds();
            let t = null; for(let k in v) {{ let [h,m] = v[k].split(':'); let vs = parseInt(h)*3600+parseInt(m)*60; if(vs>s) {{ t=vs; break; }} }}
            if(!t) {{ let [h,m] = v['SABAH'].split(':'); t = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = t-s; let hrs=Math.floor(d/3600), mns=Math.floor((d%3600)/60), scs=d%60;
            document.getElementById('clock').innerHTML = (hrs<10?'0'+hrs:hrs)+":"+(mns<10?'0'+mns:mns)+":"+(scs<10?'0'+scs:scs);
        }} setInterval(upd, 1000); upd();
    </script>
    """
    st.components.v1.html(js_countdown, height=230)

    # Vakitler (6 Sütun Yan Yana)
    v_cols = st.columns(6)
    v_keys = list(v_order.keys())
    for i in range(6):
        with v_cols[i]:
            st.markdown(f'<div class="vakit-item"><div style="color:#7f8c8d; font-size:11px;">{v_keys[i]}</div><div style="color:#2c3e50; font-size:20px; font-weight:bold;">{v_order[v_keys[i]]}</div></div>', unsafe_allow_html=True)

except:
    st.error("API Error!")

# --- 5. ÜÇLÜ MODÜL (ALT KISIM) ---
st.markdown("<br>", unsafe_allow_html=True)
col_e, col_z, col_s = st.columns(3)

with col_e:
    st.markdown(f"""<div class="module-card">
        <div style="color:#fbbf24; font-weight:bold; font-size:1.2rem; margin-bottom:10px;">{L['esma']}</div>
        <div class="scroll-box">
            1. Allah<br>2. Er-Rahman<br>3. Er-Rahim<br>4. El-Melik<br>5. El-Kuddus<br>6. Es-Selam<br>7. El-Mü'min<br>8. El-Müheymin<br>9. El-Aziz<br>10. El-Cebbar<br>
            11. El-Mütekkebir<br>12. El-Halık<br>13. El-Bari<br>14. El-Musavvir<br>15. El-Gaffar<br>16. El-Kahhar<br>... (99 Isim)
        </div>
    </div>""", unsafe_allow_html=True)
    st.button(L["liste"], key="e_btn")

with col_z:
    if 'count' not in st.session_state: st.session_state.count = 0
    st.markdown(f"""<div class="module-card">
        <div style="color:#fbbf24; font-weight:bold; font-size:1.2rem; margin-bottom:10px;">{L['zikir']}</div>
        <div class="zikir-val">{st.session_state.count}</div>
    </div>""", unsafe_allow_html=True)
    cz1, cz2 = st.columns(2)
    with cz1:
        if st.button(L["artir"]):
            st.session_state.count += 1
            st.rerun()
    with cz2:
        if st.button(L["sifirla"]):
            st.session_state.count = 0
            st.rerun()

with col_s:
    st.markdown(f"""<div class="module-card">
        <div style="color:#fbbf24; font-weight:bold; font-size:1.2rem; margin-bottom:10px;">{L['kuran']}</div>
        <div class="scroll-box">
            <b>1. Fil:</b> Alam tara kayfa fa'ala rabbuka...<br><br>
            <b>2. Kureyş:</b> Li-ilafi kurayş...<br><br>
            <b>3. Maun:</b> Ara'aytallezi yukazzibu bid-din...<br><br>
            <b>4. Kevser:</b> Inna a'taynaka-l-kevser...<br><br>
            <b>5. Kafirun:</b> Kul ya ayyuha-l-kafirun...<br><br>
            <b>6. Nasr:</b> Iza ja'a nasrullahi ve-l-feth...<br><br>
            <b>7. Tebbet:</b> Tabbat yada abi lehebin ve tebb...<br><br>
            <b>8. İhlas:</b> Kul huvallahu ahad...<br><br>
            <b>9. Felak:</b> Kul auzu bi-rabbi-l-felak...<br><br>
            <b>10. Nas:</b> Kul auzu bi-rabbi-n-nas...
        </div>
    </div>""", unsafe_allow_html=True)
    st.button(L["liste"], key="s_btn")