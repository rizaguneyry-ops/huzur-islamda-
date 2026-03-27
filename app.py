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

# Türkiye 81 İl Listesi
sehirler_81 = [
    "Adana", "Adiyaman", "Afyonkarahisar", "Agri", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydin", "Balikesir", "Bartin", "Batman", "Bayburt", "Bilecik", "Bingol", "Bitlis", "Bolu", "Burdur", "Bursa", "Canakkale", "Cankiri", "Corum", "Denizli", "Diyarbakir", "Duzce", "Edirne", "Elazig", "Erzincan", "Erzurum", "Eskisehir", "Gaziantep", "Giresun", "Gumushane", "Hakkari", "Hatay", "Igdir", "Isparta", "Istanbul", "Izmir", "Kahramanmaras", "Karabuk", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kilis", "Kirikkale", "Kirklareli", "Kirsehir", "Kocaeli", "Konya", "Kutahya", "Malatya", "Manisa", "Mardin", "Mersin", "Mugla", "Mus", "Nevsehir", "Nigde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Sanliurfa", "Siirt", "Sinop", "Sivas", "Sirnak", "Tekirdag", "Tokat", "Trabzon", "Tunceli", "Usak", "Van", "Yalova", "Yozgat", "Zonguldak"
]

EZAN_URL = "https://www.namazvaktim.org/ses/ezan1.mp3"

languages = {
    "Türkçe": {"vakit": "VAKTİNE KALAN", "ezan": "Ezan okunuyor", "hatirlat": "Namaz kılındı mı?"},
    "English": {"vakit": "TIME LEFT", "ezan": "Adhan playing", "hatirlat": "Did you pray?"},
    "العربية": {"vakit": "الوقت المتبقي", "ezan": "الأذان مسموع", "hatirlat": "هل صليت؟"}
}

esmalar_list = "1. Allah, 2. Er-Rahman, 3. Er-Rahim, 4. El-Melik, 5. El-Kuddüs, 6. Es-Selam, 7. El-Mü'min, 8. El-Müheymin, 9. El-Aziz, 10. El-Cebbar, 11. El-Mütekebbir, 12. El-Halık, 13. El-Bari, 14. El-Musavvir, 15. El-Gaffar, 16. El-Kahhar, 17. El-Vehhab, 18. Er-Rezzak, 19. El-Fettah, 20. El-Alim, 21. El-Kabid, 22. El-Basit, 23. El-Hafid, 24. Er-Rafi, 25. El-Muiz, 26. El-Muzil, 27. Es-Semi, 28. El-Basir, 29. El-Hakem, 30. El-Adl, 31. El-Latif, 32. El-Habir, 33. El-Halim, 34. El-Azim, 35. El-Gafur, 36. Es-Şekur, 37. El-Aliyy, 38. El-Kebir, 39. El-Hafiz, 40. El-Mukit, 41. El-Hasib, 42. El-Celil, 43. El-Kerim, 44. Er-Rakib, 45. El-Mucib, 46. El-Vasi, 47. El-Hakim, 48. El-Vedud, 49. El-Mecid, 50. El-Bais, 51. eş-Şehid, 52. el-Hakk, 53. el-Vekil, 54. el-Kaviyy, 55. el-Metin, 56. el-Veliyy, 57. el-Hamid, 58. el-Muhsi, 59. el-Mubdi, 60. el-Muid, 61. el-Muhyi, 62. el-Mumit, 63. el-Hayy, 64. el-Kayyum, 65. el-Vacid, 66. el-Macid, 67. el-Vahid, 68. es-Samed, 69. el-Kadir, 70. el-Muktedir, 71. el-Muahhir, 72. el-Evvel, 73. el-Ahir, 74. ez-Zahir, 75. el-Batin, 76. el-Vali, 77. el-Muteali, 78. el-Berr, 79. et-Tevvab, 80. el-Muntekim, 81. el-Afuvv, 82. er-Rauf, 83. Maliku'l-Mulk, 84. Zu'l-Celali ve'l-Ikram, 85. el-Muksit, 86. el-Cami, 87. el-Ganiyy, 88. el-Mugni, 89. el-Mani, 90. ed-Darr, 91. en-Nafi, 92. en-Nur, 93. el-Hadi, 94. el-Bedî, 95. el-Baki, 96. el-Varis, 97. er-Reşid, 98. es-Sabur, 99. el-Ehad"

# --- 3. CSS ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2000") !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stMarkdown, p, h1, h2, h3, span { color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,1); }
    .vakit-box { background: rgba(253, 246, 227, 0.98); border-radius: 12px; padding: 15px; text-align: center; border: 2px solid #d4af37; }
    .vakit-box div { color: #1a2a24 !important; text-shadow: none !important; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: rgba(10, 30, 25, 0.98) !important; border-right: 2px solid #d4af37; }
    .stExpander { background-color: #ffffff !important; border-radius: 8px !important; margin-bottom: 8px !important; }
    .stExpander p, .stExpander span, .stExpander div { color: #000000 !important; text-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. KENAR MENÜ (TÜM MODÜLLER BURADA) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🕋 İslami Portal</h2>", unsafe_allow_html=True)
    sel_lang = st.selectbox("🌐 Dil / Language", list(languages.keys()))
    sehir = st.selectbox("📍 Şehir Seç (81 İl)", sehirler_81, index=sehirler_81.index("Istanbul"))
    
    st.write("---")
    
    with st.expander("📿 Zikirmatik", expanded=False):
        if 'zk' not in st.session_state: st.session_state.zk = 0
        st.write(f"Sayı: **{st.session_state.zk}**")
        if st.button("Zikir Çek (+1)", key="zk_add"): st.session_state.zk += 1; st.rerun()
        if st.button("Sıfırla", key="zk_res"): st.session_state.zk = 0; st.rerun()

    with st.expander("📊 Kaza Takibi", expanded=False):
        for kv in ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"]:
            k_key = f"kaza_val_{kv}"
            if k_key not in st.session_state: st.session_state[k_key] = 0
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{kv}**")
            if c2.button(f"{st.session_state[k_key]}", key=f"btn_k_{kv}"): st.session_state[k_key] += 1; st.rerun()

    with st.expander("📜 Detaylı 32 Farz", expanded=False):
        st.markdown("**İman(6):** Allah, Melek, Kitap, Peygamber, Ahiret, Kader.\n\n**İslam(5):** Şehadet, Namaz, Oruç, Zekat, Hac.\n\n**Namaz(12):** 6 Dış, 6 İç Şart.\n\n**Abdest(4), Gusül(3), Teyemmüm(2).**")

    with st.expander("📖 Son On Sure", expanded=False):
        sureler = {"Fil": "Elem tera...", "Kureyş": "Li îlâfi...", "Mâûn": "Era'eyte...", "Kevser": "İnnâ a'taynâ...", "Kâfirûn": "Kul yâ...", "Nasr": "İzâ câe...", "Tebbet": "Tebbet yedâ...", "İhlâs": "Kul hüvallâhü...", "Felak": "Kul e'ûzü...", "Nâs": "Kul e'ûzü..."}
        for s, m in sureler.items(): st.write(f"**{s} Suresi**\n{m}"); st.write("---")

    with st.expander("✨ Esmaül Hüsna", expanded=False): st.caption(esmalar_list)
    with st.expander("💧 Abdest Alınışı", expanded=False): st.write("1. Eller, 2. Ağız, 3. Burun, 4. Yüz, 5. Kollar, 6. Baş, 7. Kulak/Boyun, 8. Ayaklar.")

    st.write("---")
    ezan_on = st.toggle("📢 Ezan Sesi", value=True)
    uyari_on = st.toggle("⏳ 30 Dk Hatırlatıcı", value=True)

# --- 5. ANA EKRAN ---
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    t_g = res['date']['gregorian']
    t_h = res['date']['hijri'] # Hicri Bilgi Buradan Geliyor
    
    tarih_tr = f"{t_g['day']} {tr_aylar.get(t_g['month']['en'])} {t_g['year']}"
    # Hicri Tarih Formatı
    hicri_tr = f"{t_h['day']} {t_h['month']['ar']} {t_h['year']} (Hicri)"
    
    simdi_str = datetime.now().strftime("%H:%M")
    v_order = {"İMSAK": v['Fajr'], "GÜNEŞ": v['Sunrise'], "ÖĞLE": v['Dhuhr'], "İKİNDİ": v['Asr'], "AKŞAM": v['Maghrib'], "YATSI": v['Isha']}

    # Ezan & Hatırlatıcı
    for ad, saat in v_order.items():
        if simdi_str == saat and ezan_on: st.markdown(f'<audio autoplay><source src="{EZAN_URL}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        h_saat = (datetime.strptime(saat, "%H:%M") + timedelta(minutes=30)).strftime("%H:%M")
        if simdi_str == h_saat and uyari_on: st.warning(f"🕋 {ad} vakti girdi. Namaz kılındı mı?")

    # Başlık ve Tarihler
    st.markdown(f"<h1 style='text-align:center;'>{sehir.upper()}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#fbbf24 !important;'>📅 {tarih_tr}  |  🌙 {hicri_tr}</p>", unsafe_allow_html=True)

    # Halka Sayaç
    st.components.v1.html(f"""
    <div style="display: flex; justify-content: center; margin: 15px 0;">
        <div style="border: 5px solid #d4af37; border-radius: 50%; width: 140px; height: 140px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.7); box-shadow: 0 0 20px #d4af37;">
            <div id="cnt" style="color: #fbbf24; font-size: 28px; font-weight: bold; font-family: monospace;">00:00:00</div>
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

    cols = st.columns(6)
    keys = list(v_order.keys())
    for i in range(6):
        with cols[i]: st.markdown(f'<div class="vakit-box"><div>{keys[i]}</div><div style="font-size:22px;">{v_order[keys[i]]}</div></div>', unsafe_allow_html=True)

except Exception: st.error("Bağlantı sağlanamadı.")

time.sleep(60)
st.rerun()