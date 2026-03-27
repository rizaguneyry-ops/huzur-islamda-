import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda Pro Max", page_icon="🕌", layout="wide")

# --- 2. VERİ TABANI VE TÜRKÇE TAKVİM ---
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

# --- 3. CSS (TASARIM VE OKUNABİLİRLİK) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2000") !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stMarkdown, p, h1, h2, h3, span { color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.9); }
    .vakit-box { background: rgba(253, 246, 227, 0.9); border-radius: 12px; padding: 15px; text-align: center; border: 2px solid #d4af37; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .vakit-box div { color: #1a2a24 !important; text-shadow: none !important; }
    .sidebar-content { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 10px; border: 1px solid #d4af37; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SOL KENAR MENÜ (TÜM MODÜLLER BURADA) ---
with st.sidebar:
    st.title("🕋 İslami Portal")
    lang = st.selectbox("Dil / Language", ["Türkçe", "English"])
    sehir = st.selectbox("Şehir Seç", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])
    
    st.write("---")
    # ZİKİRMATİK (Sidebar)
    with st.expander("📿 Zikirmatik", expanded=False):
        if 'zk' not in st.session_state: st.session_state.zk = 0
        st.subheader(f"Sayı: {st.session_state.zk}")
        if st.button("Zikir Çek (+1)"): st.session_state.zk += 1; st.rerun()
        if st.button("Sıfırla"): st.session_state.zk = 0; st.rerun()

    # KAZA TAKİBİ (Sidebar)
    with st.expander("📊 Kaza Takibi", expanded=False):
        k_vakitler = ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"]
        for kv in k_vakitler:
            if f'k_{kv}' not in st.session_state: st.session_state[f'k_{kv}'] = 0
            col_a, col_b = st.columns([2, 1])
            col_a.write(f"{kv}: **{st.session_state[f'k_{kv}']}**")
            if col_b.button("+1", key=f"btn_{kv}"): 
                st.session_state[f'k_{kv}'] += 1
                st.rerun()

    # ESMAÜL HÜSNA (Sidebar)
    with st.expander("✨ Esmaül Hüsna", expanded=False):
        st.markdown(f"<div style='font-size:0.8rem; color:#fbbf24;'>{esmalar_list}</div>", unsafe_allow_html=True)

    # 32 FARZ & ABDEST (Sidebar)
    with st.expander("📜 İbadet Rehberi", expanded=False):
        st.markdown("**32 Farz:**")
        st.caption("İman(6), İslam(5), Namaz(12), Abdest(4), Gusül(3), Teyemmüm(2).")
        st.markdown("**Abdestin Alınışı:**")
        st.caption("1. Eller, 2. Ağız, 3. Burun, 4. Yüz, 5. Kollar, 6. Baş, 7. Kulak/Boyun, 8. Ayaklar.")

    st.write("---")
    ezan_on = st.toggle("Ezan Sesi", value=True)
    uyari_on = st.toggle("30 Dk Hatırlatıcı", value=True)

# --- 5. ANA EKRAN (SADECE VAKİTLER VE TAKVİM) ---
try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    t_g = res['date']['gregorian']
    t_h = res['date']['hijri']
    
    # Türkçe Tarih Dönüşümü
    guncel_ay = tr_aylar.get(t_g['month']['en'], t_g['month']['en'])
    tarih_tr = f"{t_g['day']} {guncel_ay} {t_g['year']}"
    
    simdi = datetime.now()
    simdi_str = simdi.strftime("%H:%M")
    v_order = {"İMSAK": v['Fajr'], "GÜNEŞ": v['Sunrise'], "ÖĞLE": v['Dhuhr'], "İKİNDİ": v['Asr'], "AKŞAM": v['Maghrib'], "YATSI": v['Isha']}

    # Ezan & Hatırlatıcı Kontrolü
    for ad, saat in v_order.items():
        if simdi_str == saat and ezan_on:
            st.markdown(f'<audio autoplay><source src="{EZAN_URL}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            st.toast(f"📢 {ad} vakti girdi!", icon="🕌")
        h_saat = (datetime.strptime(saat, "%H:%M") + timedelta(minutes=30)).strftime("%H:%M")
        if simdi_str == h_saat and uyari_on:
            st.warning(f"🕋 {ad} vakti gireli 30 dk oldu. Namaz kılındı mı?", icon="⏳")

    # Başlık Alanı
    st.markdown(f"""
        <div style='text-align:center;'>
            <h1 style='font-size:3rem; margin-bottom:0;'>{sehir.upper()}</h1>
            <p style='color:#fbbf24; font-size:1.2rem;'>📅 {tarih_tr} | 🌙 {t_h['day']} {t_h['month']['en']} {t_h['year']}</p>
        </div>
    """, unsafe_allow_html=True)

    # Canlı Geri Sayım (Halka)
    st.components.v1.html(f"""
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <div style="border: 5px solid #d4af37; border-radius: 50%; width: 160px; height: 160px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.6); box-shadow: 0 0 20px #d4af37;">
            <div id="countdown" style="color: #fbbf24; font-size: 32px; font-weight: bold; font-family: 'Courier New', monospace;">00:00:00</div>
        </div>
    </div>
    <script>
        const v = {json.dumps(v_order)};
        function upd() {{
            const n = new Date(); const s = n.getHours()*3600 + n.getMinutes()*60 + n.getSeconds();
            let target = null; for(let k in v) {{ let [h,m] = v[k].split(':'); let vs = parseInt(h)*3600+parseInt(m)*60; if(vs>s) {{ target=vs; break; }} }}
            if(!target) {{ let [h,m] = v['İMSAK'].split(':'); target = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = target-s; let h=Math.floor(d/3600), m=Math.floor((d%3600)/60), sc=d%60;
            document.getElementById('countdown').innerHTML = (h<10?'0'+h:h)+":"+(m<10?'0'+m:m)+":"+(sc<10?'0'+sc:sc);
        }} setInterval(upd, 1000); upd();
    </script>""", height=200)

    # Vakit Kartları
    cols = st.columns(6)
    keys = list(v_order.keys())
    for i in range(6):
        with cols[i]:
            st.markdown(f"""
                <div class="vakit-box">
                    <div style="font-size:12px; font-weight:bold; color:#7f8c8d;">{keys[i]}</div>
                    <div style="font-size:24px; font-weight:bold; color:#2c3e50;">{v_order[keys[i]]}</div>
                </div>
            """, unsafe_allow_html=True)

    # Önemli Günler Geri Sayımı (Alt Panel)
    st.write("---")
    st.subheader("🗓️ Yaklaşan Mübarek Günler")
    g_cols = st.columns(4)
    for i, (ad, tar) in enumerate(dini_gunler_data.items()):
        with g_cols[i]:
            st.info(f"**{ad}**\n\n{tar}")

except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")

# Sayfayı her dakika yenile
time.sleep(60)
st.rerun()