import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# --- 2. DİL VE ŞEHİR SEÇİMİ (SIDEBAR) ---
st.sidebar.title("⚙️ Ayarlar")
dil = st.sidebar.selectbox("Dil / Language", ["Türkçe", "English", "العربية", "Deutsch", "Español", "Italiano", "中文"])
sehir = st.sidebar.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])

# Çoklu Dil Sözlüğü
lang_dict = {
    "Türkçe": {"vakit": "VAKTE KALAN", "zikir": "ZİKİRMATİK", "esma": "ESMAÜL HÜSNA", "sure": "SON 10 AYET", "reset": "SIFIRLA", "add": "ARTIR", "tarih": "Tarih"},
    "English": {"vakit": "TIME REMAINING", "zikir": "TASBIH", "esma": "99 NAMES", "sure": "LAST 10 VERSES", "reset": "RESET", "add": "COUNT", "tarih": "Date"},
    "العربية": {"vakit": "الوقت المتبقي", "zikir": "المسبحة", "esma": "أسماء الله الحسنى", "sure": "آخر 10 آيات", "reset": "إعادة تعيين", "add": "تسبيح", "tarih": "تاريخ"},
    "Deutsch": {"vakit": "VERBLEIBENDE ZEIT", "zikir": "GEBETSKETTE", "esma": "99 NAMEN", "sure": "LETZTE 10 VERSES", "reset": "ZURÜCKSETZEN", "add": "ZÄHLEN", "tarih": "Datum"},
    "Español": {"vakit": "TIEMPO RESTANTE", "zikir": "TASBIH", "esma": "99 NOMBRES", "sure": "ÚLTIMOS 10 VERSÍCULOS", "reset": "REINICIAR", "add": "CONTAR", "tarih": "Fecha"},
    "Italiano": {"vakit": "TEMPO RIMANENTE", "zikir": "TASBIH", "esma": "99 NOMI", "sure": "ULTIMI 10 VERSETTI", "reset": "RESET", "add": "CONTA", "tarih": "Data"},
    "中文": {"vakit": "剩余时间", "zikir": "念珠", "esma": "真主的99个尊名", "sure": "最后10节经文", "reset": "重置", "add": "计数", "tarih": "日期"}
}
ld = lang_dict[dil]

# --- 3. KESİN ARKA PLAN VE STİL ---
# Not: Resim çıkmıyorsa tarayıcı çerezlerini temizleyip tekrar deneyin.
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.85)), url("https://images.unsplash.com/photo-1542810634-71277d95dcbb?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
    }}
    .vakit-box {{
        background: rgba(253, 246, 227, 0.9); border-radius: 12px; padding: 10px; text-align: center;
        border: 1px solid #d4af37; margin-bottom: 5px;
    }}
    .module-card {{
        background: rgba(21, 62, 53, 0.9); border-radius: 20px; padding: 20px; 
        text-align: center; border: 1px solid #d4af37; color: white; min-height: 350px;
    }}
    .zikir-val {{ font-size: 60px; color: #fbbf24; font-weight: bold; margin: 10px 0; }}
    .verse-box {{ text-align: left; font-size: 13px; height: 200px; overflow-y: auto; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. VERİ ÇEKME ---
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    g = res['date']['gregorian']
    h = res['date']['hijri']

    # TARİH ALANI (Geri Getirildi)
    st.markdown(f"""
        <div style='text-align:center; color:white; margin-bottom:20px;'>
            <h1 style='margin-bottom:0;'>{sehir}</h1>
            <p style='font-size:18px; color:#d4af37;'>{g['day']} {g['month']['en']} {g['year']} | {h['day']} {h['month']['en']} {h['year']}</p>
        </div>
    """, unsafe_allow_html=True)

    # GERİ SAYIM HALKASI
    v_order = {"SABAH": v['Fajr'], "GÜNEŞ": v['Sunrise'], "ÖĞLE": v['Dhuhr'], "İKİNDİ": v['Asr'], "AKŞAM": v['Maghrib'], "YATSI": v['Isha']}
    
    js_code = f"""
    <div style="display: flex; justify-content: center; margin-bottom: 25px;">
        <div style="border: 5px solid #d4af37; border-radius: 50%; width: 200px; height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.4); box-shadow: 0 0 20px #d4af3766;">
            <div style="color: white; font-size: 12px; letter-spacing: 1px;">{ld['vakit']}</div>
            <div id="countdown" style="color: #fbbf24; font-size: 40px; font-weight: bold; font-family: monospace;">00:00:00</div>
        </div>
    </div>
    <script>
        const times = {json.dumps(v_order)};
        function upd() {{
            const now = new Date();
            const s = now.getHours()*3600 + now.getMinutes()*60 + now.getSeconds();
            let target = null;
            for(let k in times) {{
                let [h,m] = times[k].split(':');
                let vs = parseInt(h)*3600 + parseInt(m)*60;
                if(vs > s) {{ target = vs; break; }}
            }}
            if(!target) {{ let [h,m] = times['SABAH'].split(':'); target = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = target - s;
            let h = Math.floor(d/3600); let m = Math.floor((d%3600)/60); let sec = d%60;
            document.getElementById('countdown').innerHTML = (h<10?'0'+h:h)+":"+(m<10?'0'+m:m)+":"+(sec<10?'0'+sec:sec);
        }}
        setInterval(upd, 1000); upd();
    </script>
    """
    st.components.v1.html(js_code, height=230)

    # VAKİTLER (Yan Yana 6 Sütun)
    cv = st.columns(6)
    v_keys = list(v_order.keys())
    for i in range(6):
        with cv[i]:
            st.markdown(f'<div class="vakit-box"><div style="color:#7f8c8d; font-size:10px;">{v_keys[i]}</div><div style="color:#2c3e50; font-size:18px; font-weight:bold;">{v_order[v_keys[i]]}</div></div>', unsafe_allow_html=True)

except:
    st.error("API Error!")

# --- 5. ÜÇLÜ MODÜL (ALT KISIM) ---
st.write("---")
col_e, col_z, col_s = st.columns(3)

with col_e:
    st.markdown(f"""<div class="module-card"><h3>{ld['esma']}</h3><br><h1 style='color:#fbbf24;'>الله</h1>
    <p>Ya Rahman, Ya Rahim, Ya Melik, Ya Kuddüs, Ya Selam, Ya Mü'min, Ya Müheymin...</p>
    </div>""", unsafe_allow_html=True)
    st.button("TÜM LİSTE / ALL LIST", key="esma_btn")

with col_z:
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f"""<div class="module-card"><h3>{ld['zikir']}</h3>
    <div class="zikir-val">{st.session_state.zk}</div></div>""", unsafe_allow_html=True)
    
    # Artırma ve Sıfırlama Butonları
    cz1, cz2 = st.columns(2)
    with cz1:
        if st.button(ld['add']):
            st.session_state.zk += 1
            st.rerun()
    with cz2:
        if st.button(ld['reset']):
            st.session_state.zk = 0
            st.rerun()

with col_s:
    # Son 10 Ayet (Fatiha'dan bir örnek ve son kısa sureler)
    st.markdown(f"""<div class="module-card"><h3>{ld['sure']}</h3>
    <div class="verse-box">
    <b>Nas 1-6:</b> De ki: "Cinlerden ve insanlardan; insanların kalplerine vesvese veren sinsi vesvesecinin kötülüğünden, insanların Rabbine, insanların Melik'ine, insanların İlâh'ına sığınırım."<br><br>
    <b>Felak 1-5:</b> De ki: "Yarattığı şeylerin kötülüğünden, karanlığı çöktüğü zaman gecenin kötülüğünden..."<br><br>
    <b>İhlas 1-4:</b> De ki: "O, Allah'tır, tektir. Allah Samed'dir..."
    </div></div>""", unsafe_allow_html=True)
    st.button("KUR'AN-I KERİM", key="quran_btn")