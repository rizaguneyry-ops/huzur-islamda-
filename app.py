import streamlit as st
import requests
import json
import time
import random
from datetime import datetime, timedelta

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda Tam Sürüm", page_icon="🕌", layout="wide")

# --- 2. VERİ TABANI VE SABİTLER ---
EZAN_URL = "https://www.namazvaktim.org/ses/ezan1.mp3"

dini_gunler = {
    "Ramazan Başlangıcı": datetime(2026, 2, 19),
    "Kadir Gecesi": datetime(2026, 3, 15),
    "Ramazan Bayramı": datetime(2026, 3, 20),
    "Kurban Bayramı": datetime(2026, 5, 27)
}

esmalar = "1. Allah, 2. Er-Rahman, 3. Er-Rahim, 4. El-Melik, 5. El-Kuddüs, 6. Es-Selam, 7. El-Mü'min, 8. El-Müheymin, 9. El-Aziz, 10. El-Cebbar, 11. El-Mütekebbir, 12. El-Halık, 13. El-Bari, 14. El-Musavvir, 15. El-Gaffar, 16. El-Kahhar, 17. El-Vehhab, 18. Er-Rezzak, 19. El-Fettah, 20. El-Alim, 21. El-Kabid, 22. El-Basit, 23. El-Hafid, 24. Er-Rafi, 25. El-Muiz, 26. El-Muzil, 27. Es-Semi, 28. El-Basir, 29. El-Hakem, 30. El-Adl, 31. El-Latif, 32. El-Habir, 33. El-Halim, 34. El-Azim, 35. El-Gafur, 36. Es-Şekur, 37. El-Aliyy, 38. El-Kebir, 39. El-Hafiz, 40. El-Mukit, 41. El-Hasib, 42. El-Celil, 43. El-Kerim, 44. Er-Rakib, 45. El-Mucib, 46. El-Vasi, 47. El-Hakim, 48. El-Vedud, 49. El-Mecid, 50. El-Bais, 51. eş-Şehid, 52. el-Hakk, 53. el-Vekil, 54. el-Kaviyy, 55. el-Metin, 56. el-Veliyy, 57. el-Hamid, 58. el-Muhsi, 59. el-Mubdi, 60. el-Muid, 61. el-Muhyi, 62. el-Mumit, 63. el-Hayy, 64. el-Kayyum, 65. el-Vacid, 66. el-Macid, 67. el-Vahid, 68. es-Samed, 69. el-Kadir, 70. el-Muktedir, 71. el-Muahhir, 72. el-Evvel, 73. el-Ahir, 74. ez-Zahir, 75. el-Batin, 76. el-Vali, 77. el-Muteali, 78. el-Berr, 79. et-Tevvab, 80. el-Muntekim, 81. el-Afuvv, 82. er-Rauf, 83. Maliku'l-Mulk, 84. Zu'l-Celali ve'l-Ikram, 85. el-Muksit, 86. el-Cami, 87. el-Ganiyy, 88. el-Mugni, 89. el-Mani, 90. ed-Darr, 91. en-Nafi, 92. en-Nur, 93. el-Hadi, 94. el-Bedî, 95. el-Baki, 96. el-Varis, 97. er-Reşid, 98. es-Sabur, 99. el-Ehad"

# --- 3. CSS VE GÖRSEL TASARIM ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), 
        url("https://images.unsplash.com/photo-1542810634-71277d95dcbb?q=80&w=2000") !important;
        background-size: cover !important; background-attachment: fixed !important;
    }}
    .vakit-item {{ background: #fdf6e3; border-radius: 10px; padding: 10px; text-align: center; border: 2px solid #d4af37; color: #1a2a24; }}
    .scroll-box {{ max-height: 200px; overflow-y: auto; background: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; color: white; border-left: 3px solid #d4af37; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. KENAR MENÜ (AYARLAR) ---
st.sidebar.title("🕌 İslami Ayarlar")
sehir = st.sidebar.selectbox("Şehir Seç", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])
ezan_on = st.sidebar.toggle("Ezan Oku", value=True)
uyari_on = st.sidebar.toggle("30 Dk Sonra Hatırlat", value=True)

# --- 5. VAKİT VERİLERİ VE OTOMATİK SİSTEMLER ---
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    v_order = {"SABAH": v['Fajr'], "GÜNEŞ": v['Sunrise'], "ÖĞLE": v['Dhuhr'], "İKİNDİ": v['Asr'], "AKŞAM": v['Maghrib'], "YATSI": v['Isha']}
    
    simdi = datetime.now()
    simdi_str = simdi.strftime("%H:%M")

    # Ezan ve Hatırlatıcı Kontrolü
    for ad, saat in v_order.items():
        if simdi_str == saat and ezan_on:
            st.markdown(f'<audio autoplay><source src="{EZAN_URL}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.toast(f"📢 {ad} vakti girdi, Ezan okunuyor...", icon="🕌")
        
        # 30 Dakika Sonrası
        h_vakit = (datetime.strptime(saat, "%H:%M") + timedelta(minutes=30)).strftime("%H:%M")
        if simdi_str == h_vakit and uyari_on:
            st.warning(f"⚠️ {ad} vakti gireli 30 dakika oldu. Namazı kıldınız mı?", icon="🕋")

    # Üst Başlık ve Tarih
    st.markdown(f"<h1 style='text-align:center; color:white;'>{sehir.upper()}</h1>", unsafe_allow_html=True)
    
    # Canlı Geri Sayım (JS)
    js_code = f"""
    <div style="display: flex; justify-content: center; margin-bottom: 15px;">
        <div style="border: 4px solid #d4af37; border-radius: 50%; width: 140px; height: 140px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.5);">
            <div id="tmr" style="color: #fbbf24; font-size: 28px; font-weight: bold;">00:00:00</div>
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
    st.components.v1.html(js_code, height=160)

    # Vakitler
    v_cols = st.columns(6)
    v_keys = list(v_order.keys())
    for i in range(6):
        with v_cols[i]: st.markdown(f'<div class="vakit-item"><div style="font-size:10px;">{v_keys[i]}</div><div style="font-size:18px; font-weight:bold;">{v_order[v_keys[i]]}</div></div>', unsafe_allow_html=True)
except: st.error("Bağlantı Hatası!")

# --- 6. GERİ SAYIM & QUIZ ---
st.write("---")
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.subheader("⏳ Mübarek Günlere Kalan")
    for ad, tar in dini_gunler.items():
        fark = (tar - datetime.now()).days
        if fark >= 0: st.write(f"🔹 **{ad}:** {fark} Gün")

with col_g2:
    st.subheader("🧠 Bilgi Yarışması")
    if 'q' not in st.session_state: st.session_state.q = {"s": "Peygamberimizin devesinin adı nedir?", "c": ["Kusva", "Ebva", "Hicret"], "d": "Kusva"}
    st.write(st.session_state.q['s'])
    ans = st.radio("Cevap:", st.session_state.q['c'], horizontal=True)
    if st.button("Kontrol Et"):
        if ans == st.session_state.q['d']: st.success("Doğru!")
        else: st.error("Yanlış!")

# --- 7. ANA MODÜLLER (ZİKİR, KAZA, ESMA) ---
st.write("---")
t1, t2, t3, t4 = st.tabs(["📿 Zikirmatik", "📊 Kaza Takibi", "✨ Esmaül Hüsna", "📜 32 Farz & Abdest"])

with t1:
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.metric("Çekilen Zikir", st.session_state.zk)
    if st.button("📿 Zikir Çek (+1)"): st.session_state.zk += 1; st.rerun()
    if st.button("🔄 Sıfırla"): st.session_state.zk = 0; st.rerun()

with t2:
    k_vakitler = ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"]
    k_cols = st.columns(5)
    for i, kv in enumerate(k_vakitler):
        if f'k_{kv}' not in st.session_state: st.session_state[f'k_{kv}'] = 0
        with k_cols[i]:
            st.metric(kv, st.session_state[f'k_{kv}'])
            if st.button(f"+1 {kv}"): st.session_state[f'k_{kv}'] += 1; st.rerun()

with t3:
    st.markdown("### ✨ Allah'ın 99 İsmi")
    st.markdown(f'<div class="scroll-box">{esmalar}</div>', unsafe_allow_html=True)

with t4:
    st.markdown("### 📜 Tam 32 Farz Listesi")
    st.write("**İmanın Şartları (6):** Allah'a, Meleklere, Kitaplara, Peygamberlere, Ahirete, Kadere inanmak.")
    st.write("**İslamın Şartları (5):** Kelime-i Şehadet, Namaz, Oruç, Zekat, Hac.")
    st.write("**Namazın Farzları (12):** Hadesten Taharet, Necasetten Taharet, Setr-i Avret, İstikbal-i Kıble, Vakit, Niyet, İftitah Tekbiri, Kıyam, Kıraat, Rükû, Sücud, Ka'de-i Ahire.")
    st.write("**Abdestin Farzları (4):** Yüzü yıkamak, Kolları yıkamak, Başı meshetmek, Ayakları yıkamak.")
    st.write("**Guslün Farzları (3):** Ağza su, Burna su, Tüm vücudu yıkamak.")
    st.write("**Teyemmümün Farzları (2):** Niyet, Elleri toprağa vurup yüzü ve kolları meshetmek.")
    st.write("---")
    st.markdown("### 💧 Abdest Nasıl Alınır?")
    st.write("1. Niyet ve Besmele, 2. Eller (bileklere kadar), 3. Ağız (3 kez), 4. Burun (3 kez), 5. Yüz (3 kez), 6. Sağ-Sol kollar, 7. Baş meshi, 8. Kulak ve Boyun, 9. Ayaklar.")

# Sayfayı her dakika tazele
time.sleep(60)
st.rerun()