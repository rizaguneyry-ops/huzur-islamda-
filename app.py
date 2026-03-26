import streamlit as st
import requests
import json
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# Şık İslami Arka Plan (Cami & Hilal)
BG_IMAGE_URL = "https://cdn.pixabay.com/photo/2023/03/05/13/21/mosque-7831383_1280.png"

st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.9)), url("{BG_IMAGE_URL}");
        background-size: cover !important;
        background-position: center center !important;
        background-attachment: fixed !important;
    }}
    .hero-section {{
        background: rgba(30, 41, 59, 0.6); padding: 20px; border-radius: 25px; text-align: center;
        border: 1px solid rgba(212, 175, 55, 0.3); margin-bottom: 25px;
    }}
    .date-label {{ color: #d4af37; font-size: 20px; font-weight: bold; }}
    .hijri-label {{ color: #4caf50; font-size: 17px; }}
    .vakit-card {{
        background: rgba(28, 33, 43, 0.85); padding: 15px; border-radius: 15px;
        text-align: center; border: 1px solid rgba(212, 175, 55, 0.2); margin-bottom: 10px;
    }}
    .vakit-time {{ color: #d4af37; font-size: 22px; font-weight: bold; }}
    .esma-container {{
        background: rgba(15, 23, 42, 0.9); padding: 15px; border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.4); height: 400px; overflow-y: scroll;
    }}
    .esma-item {{ padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }}
    .esma-name {{ color: #d4af37; font-weight: bold; font-size: 16px; }}
    .app-box {{
        background: rgba(15, 23, 42, 0.8); padding: 20px; border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px;
    }}
    .stButton>button {{
        width: 100%; border-radius: 12px; background: linear-gradient(90deg, #10b981, #d4af37);
        color: white; font-weight: bold; height: 50px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİLER (99 ESMA) ---
esma_99 = [
    ("Allah", "Her türlü eksiklikten uzak, tek ilah."), ("Er-Rahmân", "Dünyada her canlıya merhamet eden."),
    ("Er-Rahîm", "Ahirette sadece müminlere merhamet eden."), ("El-Melik", "Mülkün ve kainatın tek sahibi."),
    ("El-Kuddûs", "Her türlü eksiklikten uzak olan."), ("Es-Selâm", "Esenlik veren, selamete çıkaran."),
    ("El-Mü'min", "Güven veren, koruyan."), ("El-Müheymin", "Her şeyi görüp gözeten."),
    ("El-Azîz", "İzzet sahibi, mağlup edilemeyen."), ("El-Cebbâr", "Dilediğini yapan ve yaptıran."),
    ("El-Mütekkebir", "Büyüklükte eşi benzeri olmayan."), ("El-Hâlık", "Yaratan, yoktan var eden."),
    ("El-Bâri", "Her şeyi kusursuz yaratan."), ("El-Musavvir", "Her şeye şekil veren."),
    ("El-Gaffâr", "Günahları çokça bağışlayan."), ("El-Kahhâr", "Her şeye galip gelen."),
    ("El-Vehhâb", "Karşılıksız bolca veren."), ("Er-Rezzâk", "Rızık veren."),
    ("El-Fettâh", "Kapıları açan, darlıkları gideren."), ("El-Alîm", "Her şeyi en iyi bilen."),
    ("El-Kâbıd", "Dilediğine darlık veren."), ("El-Bâsıt", "Dilediğine bolluk veren."),
    ("El-Hâfıd", "Dereceleri alçaltan."), ("Er-Râfi", "Dereceleri yükselten."),
    ("El-Muiz", "İzzet veren, aziz kılan."), ("El-Müzil", "Zelil kılan."),
    ("Es-Semî", "Her şeyi işiten."), ("El-Basîr", "Her şeyi gören."),
    ("El-Hakem", "Mutlak hakim olan."), ("El-Adl", "Mutlak adalet sahibi."),
    ("El-Latîf", "Lütfu bol olan."), ("El-Habîr", "Her şeyden haberdar olan."),
    ("El-Halîm", "Cezalandırmada acele etmeyen."), ("El-Azîm", "Pek yüce olan."),
    ("El-Gafûr", "Çok bağışlayan."), ("Eş-Şekûr", "Şükredilenlerin karşılığını veren."),
    ("El-Aliyy", "Çok yüce olan."), ("El-Kebîr", "Pek büyük olan."),
    ("El-Hafîz", "Koruyup gözeten."), ("El-Mukît", "Rızıklarını veren."),
    ("El-Hasîb", "Hesaba çeken."), ("El-Celîl", "Celal sahibi olan."),
    ("El-Kerîm", "Çok cömert olan."), ("Er-Rakîb", "Gözetleyen."),
    ("El-Mucîb", "Duaları kabul eden."), ("El-Vâsi", "İlmi her şeyi kuşatan."),
    ("El-Hakîm", "Hikmet sahibi olan."), ("El-Vedûd", "Kullarını çok seven."),
    ("El-Mecîd", "Şerefi çok yüce olan."), ("El-Bâis", "Ölüleri dirilten."),
    ("Eş-Şehîd", "Her şeye şahit olan."), ("El-Hakk", "Varlığı hiç değişmeyen."),
    ("El-Vekîl", "Kendine dayanılan."), ("El-Kaviyy", "Pek kuvvetli."),
    ("El-Metîn", "Çok dayanıklı."), ("El-Veliyy", "Müminlerin dostu."),
    ("El-Hamîd", "Övgüye layık olan."), ("El-Muhsî", "Sınırsız ilmiyle her şeyi sayan."),
    ("El-Mübdi", "Örneksiz yaratan."), ("El-Muîd", "Yeniden dirilten."),
    ("El-Muhyî", "Hayat veren."), ("El-Mümît", "Öldüren."),
    ("El-Hayy", "Daima diri olan."), ("El-Kayyûm", "Her şeyi ayakta tutan."),
    ("El-Vâcid", "İstediğini istediği an bulan."), ("El-Mâcid", "Kadr ü şanı büyük."),
    ("El-Vâhid", "Tek olan."), ("Es-Samed", "Muhtaç olmayan."),
    ("El-Kâdir", "Dilediğini yapmaya gücü yeten."), ("El-Muktedir", "Kuvvet sahipleri üzerinde hüküm süren."),
    ("El-Mukaddim", "Dilediğini öne alan."), ("El-Muahhir", "Dilediğini geriye bırakan."),
    ("El-Evvel", "Başlangıcı olmayan."), ("El-Âhir", "Sonu olmayan."),
    ("Ez-Zâhir", "Varlığı aşikar olan."), ("El-Bâtın", "Gizli olan."),
    ("El-Vâlî", "Kainatı yöneten."), ("El-Müteâlî", "Noksanlıklardan yüce."),
    ("El-Berr", "İyiliği bol olan."), ("Et-Tevvâb", "Tövbeleri kabul eden."),
    ("El-Müntakim", "Suçluları cezalandıran."), ("El-Afüvv", "Affeden."),
    ("Er-Raûf", "Çok merhametli."), ("Mâlikü'l-Mülk", "Mülkün ebedi sahibi."),
    ("Zü'l-Celâli ve'l-İkrâm", "Azamet ve ikram sahibi."), ("El-Muksit", "Adaletle yapan."),
    ("El-Câmi", "İstediğini toplayan."), ("El-Ganiyy", "Çok zengin."),
    ("El-Mugnî", "Zengin kılan."), ("El-Mâni", "Engelleyen."),
    ("Ed-Dârr", "Zarar veren."), ("En-Nâfi", "Fayda veren."),
    ("En-Nûr", "Nurlandıran."), ("El-Hâdî", "Hidayet veren."),
    ("El-Bedî", "Eşsiz yaratan."), ("El-Bâkî", "Ebedi olan."),
    ("El-Vâris", "Her şeyin gerçek sahibi."), ("Er-Reşîd", "Doğru yolu gösteren."),
    ("Es-Sabûr", "Çok sabırlı olan.")
]

tr_aylar = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}
tr_hicri = {"Muharram": "Muharrem", "Safar": "Safer", "Rabi' al-awwal": "Rebiülevvel", "Rabi' al-thani": "Rebiülahir", "Jumada al-ula": "Cemaziyelevvel", "Jumada al-akhira": "Cemaziyelahir", "Rajab": "Recep", "Sha'ban": "Şaban", "Ramadan": "Ramazan", "Shawwal": "Şevval", "Dhu al-Qi'dah": "Zilkade", "Dhu al-Hijjah": "Zilhicce"}

# --- 3. MANTIK VE API ---
sehir = st.sidebar.selectbox("📍 Şehir Seç", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])

try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v, h, g = res['timings'], res['date']['hijri'], res['date']['gregorian']
    
    g_txt = f"{g['day']} {tr_aylar.get(g['month']['en'], g['month']['en'])} {g['year']}"
    h_txt = f"{h['day']} {tr_hicri.get(h['month']['en'], h['month']['en'])} {h['year']}"
    v_order = [("SABAH", v['Fajr']), ("GÜNEŞ", v['Sunrise']), ("ÖĞLE", v['Dhuhr']), ("İKİNDİ", v['Asr']), ("AKŞAM", v['Maghrib']), ("YATSI", v['Isha'])]

    # ÜST PANEL
    st.markdown(f'<div class="hero-section"><div class="date-label">📅 {g_txt}</div><div class="hijri-label">🌙 {h_txt}</div></div>', unsafe_allow_html=True)

    # CANLI SAYAÇ (JS)
    js_v = {n: t for n, t in v_order}
    countdown_html = f"""
    <div id="c" style="color:#fbbf24; font-size:45px; font-family:monospace; text-align:center; font-weight:bold; text-shadow:0 0 10px rgba(251,191,36,0.5);">--:--:--</div>
    <script>
        const v = {json.dumps(js_v)};
        function u() {{
            const n = new Date(); const s = n.getHours()*3600 + n.getMinutes()*60 + n.getSeconds();
            let t = null; for(let k in v) {{ let [h,m] = v[k].split(':'); let vs = parseInt(h)*3600+parseInt(m)*60; if(vs>s) {{ t=vs; break; }} }}
            if(!t) {{ let [h,m] = v['SABAH'].split(':'); t = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = t-s; let hrs=Math.floor(d/3600), mns=Math.floor((d%3600)/60), scs=d%60;
            document.getElementById('c').innerHTML = (hrs<10?'0'+hrs:hrs)+":"+(mns<10?'0'+mns:mns)+":"+(scs<10?'0'+scs:scs);
        }} setInterval(u, 1000); u();
    </script>
    """
    components.html(countdown_html, height=80)

    # VAKİT DÜZENİ (HATASIZ)
    st.write("")
    c1 = st.columns(3)
    for i in range(3):
        with c1[i]:
            st.markdown(f'<div class="vakit-card"><div style="font-size:12px; opacity:0.7;">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)
    
    c2 = st.columns(3)
    for i in range(3, 6):
        with c2[i-3]:
            st.markdown(f'<div class="vakit-card"><div style="font-size:12px; opacity:0.7;">{v_order[i][0]}</div><div class="vakit-time">{v_order[i][1]}</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Bağlantı hatası: {e}")

# --- 4. ALT BÖLÜMLER ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="app-box"><h3>📿 Zikirmatik</h3>', unsafe_allow_html=True)
    if 'zk' not in st.session_state: st.session_state.zk = 0
    st.markdown(f"<h1 style='text-align:center; color:#fbbf24;'>{st.session_state.zk}</h1>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK"):
        st.session_state.zk += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="app-box"><h3>📻 Radyo</h3>', unsafe_allow_html=True)
    st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="app-box"><h3>✨ Esmaü\'l Hüsna (99)</h3><div class="esma-container">', unsafe_allow_html=True)
    for isim, anlam in esma_99:
        st.markdown(f'<div class="esma-item"><span class="esma-name">{isim}</span><br><small>{anlam}</small></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)