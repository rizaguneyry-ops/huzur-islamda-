import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# --- 2. DİL VE TÜRKÇE TAKVİM AYARLARI ---
languages = {
    "Türkçe": {"vakit": "VAKTİNE KALAN", "zikir": "ZİKİRMATİK", "esma": "ESMAÜL HÜSNA", "kuran": "SON 10 SURE", "artir": "ARTIR", "sifirla": "SIFIRLA", "farz": "32 FARZ", "abdest": "ABDEST"},
    "English": {"vakit": "TIME LEFT", "zikir": "TASBIH", "esma": "99 NAMES", "kuran": "LAST 10 SURAH", "artir": "COUNT", "sifirla": "RESET", "farz": "32 OBLIGATIONS", "abdest": "WUDU"},
    "العربية": {"vakit": "الوقت المتبقي", "zikir": "المسبحة", "esma": "أسماء الله", "kuran": "آخر 10 سور", "artir": "تسبيح", "sifirla": "إعادة", "farz": "32 فرض", "abdest": "الوضوء"},
    "Deutsch": {"vakit": "RESTZEIT", "zikir": "ZÄHLER", "esma": "99 NAMEN", "kuran": "10 SUREN", "artir": "ZÄHLEN", "sifirla": "RESET", "farz": "32 PFLICHTEN", "abdest": "WUDU"},
    "Español": {"vakit": "TIEMPO", "zikir": "TASBIH", "esma": "99 NOMBRES", "kuran": "10 SURAS", "artir": "CONTAR", "sifirla": "RESETEAR", "farz": "32 OBLIGACIONES", "abdest": "WUDU"},
    "Italiano": {"vakit": "TEMPO", "zikir": "TASBIH", "esma": "99 NOMI", "kuran": "10 SURE", "artir": "CONTA", "sifirla": "RESET", "farz": "32 OBBLIGHI", "abdest": "WUDU"},
    "中文": {"vakit": "剩余时间", "zikir": "念珠", "esma": "真主尊名", "kuran": "最后10章", "artir": "计数", "sifirla": "重置", "farz": "32 义务", "abdest": "小净"}
}

tr_aylar = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}

st.sidebar.title("🌙 Ayarlar")
sel_lang = st.sidebar.selectbox("Dil / Language", list(languages.keys()))
sehir = st.sidebar.selectbox("Şehir / City", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])
L = languages[sel_lang]

# --- 3. GÜÇLÜ ARKA PLAN VE STİL (KESİN ÇÖZÜM) ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1590075865003-e48277faf551?auto=format&fit=crop&w=1920&q=80") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    .vakit-item {{
        background: rgba(253, 246, 227, 0.95); border-radius: 12px; padding: 12px;
        text-align: center; border: 1px solid #d4af37; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }}
    .module-card {{
        background: rgba(15, 45, 35, 0.92); border-radius: 20px; padding: 20px;
        border: 1px solid #d4af37; color: white; min-height: 400px; text-align: center;
        margin-bottom: 20px;
    }}
    .list-area {{
        text-align: left; background: rgba(0,0,0,0.3); padding: 15px; 
        border-radius: 10px; font-size: 0.9rem; max-height: 250px; overflow-y: auto;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. VERİ ÇEKME VE TÜRKÇE TAKVİM ---
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    g = res['date']['gregorian']
    h = res['date']['hijri']

    # Türkçe Tarih Formatı
    gun = g['day']
    ay = tr_aylar.get(g['month']['en'], g['month']['en'])
    yil = g['year']
    tarih_str = f"{gun} {ay} {yil}"

    st.markdown(f"""
        <div style='text-align:center; color:white;'>
            <h1 style='margin-bottom:0;'>{sehir.upper()}</h1>
            <p style='color:#fbbf24; font-size:1.2rem;'>📅 {tarih_str} | 🌙 {h['day']} {h['month']['en']} {h['year']}</p>
        </div>
    """, unsafe_allow_html=True)

    # Geri Sayım (JS)
    v_order = {"SABAH": v['Fajr'], "GÜNEŞ": v['Sunrise'], "ÖĞLE": v['Dhuhr'], "İKİNDİ": v['Asr'], "AKŞAM": v['Maghrib'], "YATSI": v['Isha']}
    js_code = f"""
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <div style="border: 5px solid #d4af37; border-radius: 50%; width: 180px; height: 180px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.5);">
            <div style="color: white; font-size: 10px;">{L['vakit']}</div>
            <div id="tmr" style="color: #fbbf24; font-size: 35px; font-weight: bold;">00:00:00</div>
        </div>
    </div>
    <script>
        const v = {json.dumps(v_order)};
        function u() {{
            const n = new Date(); const s = n.getHours()*3600 + n.getMinutes()*60 + n.getSeconds();
            let t = null; for(let k in v) {{ let [h,m] = v[k].split(':'); let vs = parseInt(h)*3600+parseInt(m)*60; if(vs>s) {{ t=vs; break; }} }}
            if(!t) {{ let [h,m] = v['SABAH'].split(':'); t = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = t-s; let hrs=Math.floor(d/3600), mns=Math.floor((d%3600)/60), scs=d%60;
            document.getElementById('tmr').innerHTML = (hrs<10?'0'+hrs:hrs)+":"+(mns<10?'0'+mns:mns)+":"+(scs<10?'0'+scs:scs);
        }} setInterval(u, 1000); u();
    </script>
    """
    st.components.v1.html(js_code, height=210)

    # Vakitler
    vc = st.columns(6)
    vk = list(v_order.keys())
    for i in range(6):
        with vc[i]:
            st.markdown(f'<div class="vakit-item"><div style="color:#7f8c8d; font-size:10px;">{vk[i]}</div><div style="color:#2c3e50; font-size:18px; font-weight:bold;">{v_order[vk[i]]}</div></div>', unsafe_allow_html=True)

except:
    st.error("Bağlantı Hatası!")

# --- 5. ALT ÜÇLÜ MODÜLLER ---
st.write("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f'<div class="module-card"><h3>{L["esma"]}</h3><h1 style="color:#fbbf24;">الله</h1>', unsafe_allow_html=True)
    with st.expander(f"{L['liste']} (Tıkla ve Aç)"):
        st.write("1. Allah, 2. Er-Rahman, 3. Er-Rahim, 4. El-Melik, 5. El-Kuddüs, 6. Es-Selam, 7. El-Mü'min, 8. El-Müheymin, 9. El-Aziz, 10. El-Cebbar...")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    if 'count' not in st.session_state: st.session_state.count = 0
    st.markdown(f'<div class="module-card"><h3>{L["zikir"]}</h3><div style="font-size:70px; color:#fbbf24; font-weight:bold;">{st.session_state.count}</div>', unsafe_allow_html=True)
    cz1, cz2 = st.columns(2)
    with cz1:
        if st.button(L["artir"]): st.session_state.count += 1; st.rerun()
    with cz2:
        if st.button(L["sifirla"]): st.session_state.count = 0; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown(f'<div class="module-card"><h3>{L["kuran"]}</h3>', unsafe_allow_html=True)
    with st.expander("Sure Listesini Gör"):
        st.write("1. Fil, 2. Kureyş, 3. Maun, 4. Kevser, 5. Kafirun, 6. Nasr, 7. Tebbet, 8. İhlas, 9. Felak, 10. Nas")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. EK BİLGİLER: 32 FARZ & ABDEST ---
st.write("---")
col_farz, col_abdest = st.columns(2)

with col_farz:
    with st.expander(f"✨ {L['farz']} Listesi"):
        st.markdown("""
        **İmanın Şartları (6):** Allah'a, Meleklere, Kitaplara, Peygamberlere, Ahirete, Kadere inanmak.  
        **İslamın Şartları (5):** Kelime-i Şehadet, Namaz, Oruç, Zekat, Hac.  
        **Namazın Farzları (12):** 6'sı dışında (Hazırlık), 6'sı içinde (Kılınış).  
        **Abdestin Farzları (4):** Yüzü yıkamak, Kolları yıkamak, Başı meshetmek, Ayakları yıkamak.  
        **Guslün Farzları (3):** Ağıza su, Burna su, Tüm vücudu yıkamak.  
        **Teyemmümün Farzları (2):** Niyet, Elleri toprağa vurup yüzü ve kolları meshetmek.
        """)

with col_abdest:
    with st.expander(f"💧 {L['abdest']} Nasıl Alınır?"):
        st.markdown("""
        1. Niyet ve Besmele  
        2. Elleri bileklere kadar yıkamak  
        3. Ağıza 3 kez su vermek  
        4. Burnuna 3 kez su vermek  
        5. Yüzü 3 kez yıkamak  
        6. Sağ ve sol kolları dirseklerle beraber yıkamak  
        7. Başı meshetmek, kulakları ve boynu temizlemek  
        8. Ayakları topuklarla beraber yıkamak.
        """)