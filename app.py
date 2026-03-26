import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# --- 2. DİL VE TÜRKÇE TAKVİM ---
languages = {
    "Türkçe": {"vakit": "VAKTİNE KALAN", "zikir": "ZİKİRMATİK", "esma": "ESMAÜL HÜSNA", "kuran": "SON 10 SURE", "artir": "ARTIR", "sifirla": "SIFIRLA", "farz": "32 FARZ", "abdest": "ABDEST", "liste": "LİSTEYİ AÇ"},
    "English": {"vakit": "TIME LEFT", "zikir": "TASBIH", "esma": "99 NAMES", "kuran": "LAST 10 SURAH", "artir": "COUNT", "sifirla": "RESET", "farz": "32 OBLIGATIONS", "abdest": "WUDU", "liste": "OPEN LIST"}
}
# Diğer diller (Arapça, Almanca vb.) v26'daki gibi eklenebilir, hata almamak için v27'de en stabil haliyle tutulmuştur.

tr_aylar = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}

st.sidebar.title("🌙 Ayarlar")
sel_lang = st.sidebar.selectbox("Dil / Language", list(languages.keys()))
sehir = st.sidebar.selectbox("Şehir / City", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])
L = languages[sel_lang]

# --- 3. GÜÇLÜ ARKA PLAN VE STİL ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000&auto=format&fit=crop") !important;
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
        border: 1px solid #d4af37; color: white; min-height: 420px; text-align: center;
        margin-bottom: 20px;
    }}
    .content-box {{
        text-align: left; background: rgba(0,0,0,0.4); padding: 15px; 
        border-radius: 10px; font-size: 0.85rem; max-height: 250px; overflow-y: auto;
        color: #ecf0f1; line-height: 1.6; border: 1px solid rgba(212,175,55,0.3);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. VERİ ÇEKME VE TÜRKÇE TAKVİM ---
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    g = res['date']['gregorian']
    h = res['date']['hijri']
    tarih_str = f"{g['day']} {tr_aylar.get(g['month']['en'])} {g['year']}"

    st.markdown(f"<div style='text-align:center; color:white;'><h1 style='margin-bottom:0;'>{sehir.upper()}</h1><p style='color:#fbbf24;'>📅 {tarih_str} | 🌙 {h['day']} {h['month']['en']} {h['year']}</p></div>", unsafe_allow_html=True)

    v_order = {"SABAH": v['Fajr'], "GÜNEŞ": v['Sunrise'], "ÖĞLE": v['Dhuhr'], "İKİNDİ": v['Asr'], "AKŞAM": v['Maghrib'], "YATSI": v['Isha']}
    js_code = f"""
    <div style="display: flex; justify-content: center; margin: 15px 0;">
        <div style="border: 5px solid #d4af37; border-radius: 50%; width: 170px; height: 170px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.5);">
            <div style="color: white; font-size: 10px;">{L['vakit']}</div>
            <div id="tmr" style="color: #fbbf24; font-size: 32px; font-weight: bold;">00:00:00</div>
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
    </script>"""
    st.components.v1.html(js_code, height=200)

    vc = st.columns(6)
    vk = list(v_order.keys())
    for i in range(6):
        with vc[i]: st.markdown(f'<div class="vakit-item"><div style="color:#7f8c8d; font-size:10px;">{vk[i]}</div><div style="color:#2c3e50; font-size:18px; font-weight:bold;">{v_order[vk[i]]}</div></div>', unsafe_allow_html=True)
except: st.error("Bağlantı Hatası!")

# --- 5. ÜÇLÜ MODÜL (ESMA, ZİKİR, SURE) ---
st.write("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f'<div class="module-card"><h3>{L["esma"]}</h3>', unsafe_allow_html=True)
    esmalar = "1. Allah, 2. Er-Rahman, 3. Er-Rahim, 4. El-Melik, 5. El-Kuddüs, 6. Es-Selam, 7. El-Mü'min, 8. El-Müheymin, 9. El-Aziz, 10. El-Cebbar, 11. El-Mütekebbir, 12. El-Halık, 13. El-Bari, 14. El-Musavvir, 15. El-Gaffar, 16. El-Kahhar, 17. El-Vehhab, 18. Er-Rezzak, 19. El-Fettah, 20. El-Alim, 21. El-Kabid, 22. El-Basit, 23. El-Hafid, 24. Er-Rafi, 25. El-Muiz, 26. El-Muzil, 27. Es-Semi, 28. El-Basir, 29. El-Hakem, 30. El-Adl, 31. El-Latif, 32. El-Habir, 33. El-Halim, 34. El-Azim, 35. El-Gafur, 36. Es-Şekur, 37. El-Aliyy, 38. El-Kebir, 39. El-Hafiz, 40. El-Mukit, 41. El-Hasib, 42. El-Celil, 43. El-Kerim, 44. Er-Rakib, 45. El-Mucib, 46. El-Vasi, 47. El-Hakim, 48. El-Vedud, 49. El-Mecid, 50. El-Bais, 51. eş-Şehid, 52. el-Hakk, 53. el-Vekil, 54. el-Kaviyy, 55. el-Metin, 56. el-Veliyy, 57. el-Hamid, 58. el-Muhsi, 59. el-Mubdi, 60. el-Muid, 61. el-Muhyi, 62. el-Mumit, 63. el-Hayy, 64. el-Kayyum, 65. el-Vacid, 66. el-Macid, 67. el-Vahid, 68. es-Samed, 69. el-Kadir, 70. el-Muktedir, 71. el-Muahhir, 72. el-Evvel, 73. el-Ahir, 74. ez-Zahir, 75. el-Batin, 76. el-Vali, 77. el-Muteali, 78. el-Berr, 79. et-Tevvab, 80. el-Muntekim, 81. el-Afuvv, 82. er-Rauf, 83. Maliku'l-Mulk, 84. Zu'l-Celali ve'l-Ikram, 85. el-Muksit, 86. el-Cami, 87. el-Ganiyy, 88. el-Mugni, 89. el-Mani, 90. ed-Darr, 91. en-Nafi, 92. en-Nur, 93. el-Hadi, 94. el-Bedî, 95. el-Baki, 96. el-Varis, 97. er-Reşid, 98. es-Sabur, 99. el-Ehad"
    st.markdown(f'<div class="content-box">{esmalar}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    if 'count' not in st.session_state: st.session_state.count = 0
    st.markdown(f'<div class="module-card"><h3>{L["zikir"]}</h3><div style="font-size:70px; color:#fbbf24; font-weight:bold; margin-top:30px;">{st.session_state.count}</div>', unsafe_allow_html=True)
    cz1, cz2 = st.columns(2)
    with cz1:
        if st.button(L["artir"]): st.session_state.count += 1; st.rerun()
    with cz2:
        if st.button(L["sifirla"]): st.session_state.count = 0; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown(f'<div class="module-card"><h3>{L["kuran"]}</h3>', unsafe_allow_html=True)
    sureler = "<b>1. Fil:</b> E lem tera keyfe...<br><b>2. Kureyş:</b> Li-îlâfi kureyş...<br><b>3. Maun:</b> Era'eytellezî...<br><b>4. Kevser:</b> İnnâ a'taynâ...<br><b>5. Kafirun:</b> Kul yâ eyyuhel kâfirûn...<br><b>6. Nasr:</b> İzâ câe nasrullâhi...<br><b>7. Tebbet:</b> Tebbet yedâ ebî lehebin...<br><b>8. İhlas:</b> Kul huvallâhu ehad...<br><b>9. Felak:</b> Kul eûzu bi rabbil felak...<br><b>10. Nas:</b> Kul eûzu bi rabbin nâs..."
    st.markdown(f'<div class="content-box">{sureler}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. 32 FARZ VE ABDEST (TAM LİSTE) ---
st.write("---")
f1, f2 = st.columns(2)
with f1:
    st.markdown(f'<div class="module-card" style="min-height:500px;"><h3>✨ {L["farz"]}</h3>', unsafe_allow_html=True)
    farz_text = """<b>İmanın Şartları (6):</b> Allah'a, Meleklere, Kitaplara, Peygamberlere, Ahirete, Kadere inanmak.<br>
    <b>İslamın Şartları (5):</b> Şehadet etmek, Namaz kılmak, Oruç tutmak, Zekat vermek, Hacca gitmek.<br>
    <b>Namazın Farzları (12):</b> Dışındakiler: Hadesten taharet, Necasetten taharet, Setr-i avret, İstikbal-i kıble, Vakit, Niyet. İçindekiler: İftitah tekbiri, Kıyam, Kıraat, Rükû, Sücud, Ka'de-i ahire.<br>
    <b>Abdestin Farzları (4):</b> Yüzü yıkamak, Kolları yıkamak, Başı meshetmek, Ayakları yıkamak.<br>
    <b>Guslün Farzları (3):</b> Ağıza su, Burna su, Tüm vücudu yıkamak.<br>
    <b>Teyemmümün Farzları (2):</b> Niyet, Elleri toprağa vurup yüzü ve kolları meshetmek."""
    st.markdown(f'<div class="content-box" style="max-height:350px;">{farz_text}</div></div>', unsafe_allow_html=True)

with f2:
    st.markdown(f'<div class="module-card" style="min-height:500px;"><h3>💧 {L["abdest"]} ALINIŞI</h3>', unsafe_allow_html=True)
    abdest_text = """1. Niyet edilir, 'Euzü besmele' çekilir.<br>2. Eller bileklere kadar 3 kez yıkanır.<br>3. Sağ el ile ağıza 3 kez su verilir.<br>4. Sağ el ile burnuna 3 kez su verilir, sol el ile temizlenir.<br>5. Yüz 3 kez yıkanır.<br>6. Önce sağ, sonra sol kol dirseklerle beraber yıkanır.<br>7. Eller ıslatılarak başın dörtte biri meshedilir.<br>8. Eller ıslatılarak kulaklar ve boyun meshedilir.<br>9. Önce sağ, sonra sol ayak parmak uçlarından başlanarak topuklarla beraber yıkanır."""
    st.markdown(f'<div class="content-box" style="max-height:350px;">{abdest_text}</div></div>', unsafe_allow_html=True)