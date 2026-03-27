import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda Pro Max", page_icon="🕌", layout="wide")

# --- 2. VERİ TABANI ---
tr_aylar = {
    "January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan",
    "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos",
    "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"
}

EZAN_URL = "https://www.namazvaktim.org/ses/ezan1.mp3"

dini_gunler_data = {
    "Ramazan Başlangıcı": "19 Şubat 2026",
    "Kadir Gecesi": "15 Mart 2026",
    "Ramazan Bayramı": "20 Mart 2026",
    "Kurban Bayramı": "27 Mayıs 2026"
}

esmalar_list = "1. Allah, 2. Er-Rahman, 3. Er-Rahim, 4. El-Melik, 5. El-Kuddüs, 6. Es-Selam, 7. El-Mü'min, 8. El-Müheymin, 9. El-Aziz, 10. El-Cebbar, 11. El-Mütekebbir, 12. El-Halık, 13. El-Bari, 14. El-Musavvir, 15. El-Gaffar, 16. El-Kahhar, 17. El-Vehhab, 18. Er-Rezzak, 19. El-Fettah, 20. El-Alim, 21. El-Kabid, 22. El-Basit, 23. El-Hafid, 24. Er-Rafi, 25. El-Muiz, 26. El-Muzil, 27. Es-Semi, 28. El-Basir, 29. El-Hakem, 30. El-Adl, 31. El-Latif, 32. El-Habir, 33. El-Halim, 34. El-Azim, 35. El-Gafur, 36. Es-Şekur, 37. El-Aliyy, 38. El-Kebir, 39. El-Hafiz, 40. El-Mukit, 41. El-Hasib, 42. El-Celil, 43. El-Kerim, 44. Er-Rakib, 45. El-Mucib, 46. El-Vasi, 47. El-Hakim, 48. El-Vedud, 49. El-Mecid, 50. El-Bais, 51. eş-Şehid, 52. el-Hakk, 53. el-Vekil, 54. el-Kaviyy, 55. el-Metin, 56. el-Veliyy, 57. el-Hamid, 58. el-Muhsi, 59. el-Mubdi, 60. el-Muid, 61. el-Muhyi, 62. el-Mumit, 63. el-Hayy, 64. el-Kayyum, 65. el-Vacid, 66. el-Macid, 67. el-Vahid, 68. es-Samed, 69. el-Kadir, 70. el-Muktedir, 71. el-Muahhir, 72. el-Evvel, 73. el-Ahir, 74. ez-Zahir, 75. el-Batin, 76. el-Vali, 77. el-Muteali, 78. el-Berr, 79. et-Tevvab, 80. el-Muntekim, 81. el-Afuvv, 82. er-Rauf, 83. Maliku'l-Mulk, 84. Zu'l-Celali ve'l-Ikram, 85. el-Muksit, 86. el-Cami, 87. el-Ganiyy, 88. el-Mugni, 89. el-Mani, 90. ed-Darr, 91. en-Nafi, 92. en-Nur, 93. el-Hadi, 94. el-Bedî, 95. el-Baki, 96. el-Varis, 97. er-Reşid, 98. es-Sabur, 99. el-Ehad"

# --- 3. CSS (PROFESYONEL TASARIM & NETLİK) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2000") !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    /* Ana Ekran Yazı Gölgesi */
    .stMarkdown, p, h1, h2, h3, span { color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,1); }
    
    /* Vakit Kartları */
    .vakit-box { background: rgba(253, 246, 227, 0.95); border-radius: 12px; padding: 15px; text-align: center; border: 2px solid #d4af37; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
    .vakit-box div { color: #1a2a24 !important; text-shadow: none !important; font-weight: bold; }

    /* KENAR MENÜ (SIDEBAR) OKUNABİLİRLİK AYARI */
    [data-testid="stSidebar"] { background-color: rgba(15, 45, 35, 0.98) !important; border-right: 2px solid #d4af37; }
    .stExpander { background-color: rgba(255, 255, 255, 0.95) !important; border-radius: 10px !important; margin-bottom: 10px !important; }
    .stExpander p, .stExpander span, .stExpander label { color: #1a2a24 !important; text-shadow: none !important; font-weight: 500 !important; }
    .stExpander blockquote { color: #2c3e50 !important; border-left: 5px solid #d4af37 !important; background: #f9f9f9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. KENAR MENÜ (TÜM MODÜLLER BURADA) ---
with st.sidebar:
    st.title("🕋 İslami Portal")
    sehir = st.selectbox("📍 Şehir Seç", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])
    
    st.write("---")
    
    # 1. ZİKİRMATİK
    with st.expander("📿 Zikirmatik", expanded=False):
        if 'zk' not in st.session_state: st.session_state.zk = 0
        st.markdown(f"### Sayı: <span style='color:green;'>{st.session_state.zk}</span>", unsafe_allow_html=True)
        if st.button("Zikir Çek (+1)"): st.session_state.zk += 1; st.rerun()
        if st.button("Sıfırla"): st.session_state.zk = 0; st.rerun()

    # 2. KAZA TAKİBİ
    with st.expander("📊 Kaza Takibi", expanded=False):
        for kv in ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"]:
            if f'k_{kv}' not in st.session_state: st.session_state[f'k_{kv}'] = 0
            c_a, c_b = st.columns([3, 1])
            c_a.write(f"**{kv}**")
            if c_b.button(f"{st.session_state[f'k_{kv}']}", key=f"k_{kv}"): 
                st.session_state[f'k_{kv}'] += 1
                st.rerun()

    # 3. DETAYLI 32 FARZ
    with st.expander("📜 Detaylı 32 Farz", expanded=False):
        st.markdown("""
        **İmanın Şartları (6):**
        1- Allah'ın varlığına ve birliğine inanmak.
        2- Meleklere inanmak.
        3- Kitaplara inanmak.
        4- Peygamberlere inanmak.
        5- Ahiret gününe inanmak.
        6- Kadere, hayır ve şerrin Allah'tan geldiğine inanmak.

        **İslam'ın Şartları (5):**
        1- Kelime-i Şehadet getirmek.
        2- Namaz kılmak.
        3- Oruç tutmak.
        4- Zekat vermek.
        5- Hacca gitmek.

        **Namazın Farzları (12):**
        *Dışındakiler:* Hadesten Taharet, Necasetten Taharet, Setr-i Avret, İstikbal-i Kıble, Vakit, Niyet.
        *İçindekiler:* İftitah Tekbiri, Kıyam, Kıraat, Rükû, Sücud, Ka'de-i Ahire.

        **Abdestin Farzları (4):**
        1- Yüzü yıkamak. 2- Kolları yıkamak. 3- Başı meshetmek. 4- Ayakları yıkamak.

        **Guslün Farzları (3):**
        1- Ağza su vermek. 2- Burna su vermek. 3- Bütün vücudu yıkamak.

        **Teyemmümün Farzları (2):**
        1- Niyet etmek. 2- İki darp (Elleri toprağa vurup yüzü ve kolları meshetmek).
        """)

    # 4. SON ON SURE (TAM LİSTE)
    with st.expander("📖 Son On Sure", expanded=False):
        sureler = {
            "Fil": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl...",
            "Kureyş": "Li îlâfi kureyş. Îlâfihim rihleteş şitâi ves sayf...",
            "Mâûn": "Era'eytellezî yükezzibü bid dîn...",
            "Kevser": "İnnâ a'taynâkel kevser. Fe salli li rabbike venhar...",
            "Kâfirûn": "Kul yâ eyyühel kâfirûn. Lâ a'büdü mâ ta'büdûn...",
            "Nasr": "İzâ câe nasrullâhi vel feth...",
            "Tebbet": "Tebbet yedâ ebî lehebin ve tebb...",
            "İhlâs": "Kul hüvallâhü ehad. Allâhüs samed...",
            "Felak": "Kul e'ûzü bi rabbil felak. Min şerri mâ halak...",
            "Nâs": "Kul e'ûzü bi rabbin nâs. Melikin nâs..."
        }
        for s_ad, s_metin in sureler.items():
            st.write(f"**{s_ad} Suresi**")
            st.caption(s_metin)
            st.write("---")

    # 5. ESMAÜL HÜSNA
    with st.expander("✨ Esmaül Hüsna", expanded=False):
        st.write(esmalar_list)

    # 6. ABDEST REHBERİ
    with st.expander("💧 Abdestin Alınışı", expanded=False):
        st.write("1- Niyet ve Besmele. 2- Eller. 3- Ağız (3 kez). 4- Burun (3 kez). 5- Yüz. 6- Kollar. 7- Baş meshi. 8- Kulak ve Boyun. 9- Ayaklar.")

    st.write("---")
    ezan_on = st.toggle("📢 Ezan Sesi", value=True)
    uyari_on = st.toggle("⏳ 30 Dk Hatırlatıcı", value=True)

# --- 5. ANA EKRAN ---
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    t_g = res['date']['gregorian']
    
    tarih_tr = f"{t_g['day']} {tr_aylar.get(t_g['month']['en'], t_g['month']['en'])} {t_g['year']}"
    simdi_str = datetime.now().strftime("%H:%M")
    v_order = {"İMSAK": v['Fajr'], "GÜNEŞ": v['Sunrise'], "ÖĞLE": v['Dhuhr'], "İKİNDİ": v['Asr'], "AKŞAM": v['Maghrib'], "YATSI": v['Isha']}

    # Ezan & Hatırlatıcı Mantığı
    for ad, saat in v_order.items():
        if simdi_str == saat and ezan_on:
            st.markdown(f'<audio autoplay><source src="{EZAN_URL}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        h_saat = (datetime.strptime(saat, "%H:%M") + timedelta(minutes=30)).strftime("%H:%M")
        if simdi_str == h_saat and uyari_on:
            st.warning(f"🕋 {ad} vakti girdi. Namaz kılındı mı?")

    # Başlık ve Takvim
    st.markdown(f"<h1 style='text-align:center;'>{sehir.upper()}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#fbbf24 !important;'>📅 {tarih_tr}</p>", unsafe_allow_html=True)

    # Halka Sayaç (JS)
    st.components.v1.html(f"""
    <div style="display: flex; justify-content: center; margin: 15px 0;">
        <div style="border: 5px solid #d4af37; border-radius: 50%; width: 150px; height: 150px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.7); box-shadow: 0 0 20px #d4af37;">
            <div id="cnt" style="color: #fbbf24; font-size: 30px; font-weight: bold; font-family: monospace;">00:00:00</div>
        </div>
    </div>
    <script>
        const v = {json.dumps(v_order)};
        function upd() {{
            const n = new Date(); const s = n.getHours()*3600 + n.getMinutes()*60 + n.getSeconds();
            let target = null; for(let k in v) {{ let [h,m] = v[k].split(':'); let vs = parseInt(h)*3600+parseInt(m)*60; if(vs>s) {{ target=vs; break; }} }}
            if(!target) {{ let [h,m] = v['İMSAK'].split(':'); target = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = target-s; let h=Math.floor(d/3600), m=Math.floor((d%3600)/60), sc=d%60;
            document.getElementById('cnt').innerHTML = (h<10?'0'+h:h)+":"+(m<10?'0'+m:m)+":"+(sc<10?'0'+sc:sc);
        }} setInterval(upd, 1000); upd();
    </script>""", height=180)

    # Vakit Kartları
    cols = st.columns(6)
    keys = list(v_order.keys())
    for i in range(6):
        with cols[i]:
            st.markdown(f'<div class="vakit-box"><div>{keys[i]}</div><div style="font-size:22px;">{v_order[keys[i]]}</div></div>', unsafe_allow_html=True)

    st.write("---")
    st.subheader("🗓️ Dini Günler")
    g_cols = st.columns(4)
    for i, (ad, tar) in enumerate(dini_gunler_data.items()):
        g_cols[i].info(f"**{ad}**\n\n{tar}")

except Exception as e: st.error("Hata!")

time.sleep(60)
st.rerun()