import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import random

# --- 1. KONFİGÜRASYON VE DİL SÖZLÜĞÜ ---
st.set_page_config(page_title="Manevi Muhafız", page_icon="🕋", layout="wide")

LANG_DICT = {
    "Türkçe": {"besmele": "بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ", "ayet": "Siz, insanlar için çıkarılmış en hayırlı ümmetsiniz... (Âli İmrân, 110)", "zikir": "Zikirmatik", "namaz_kildi": "Namazımı Kıldım", "kalan": "Kalan Süre", "dil": "Dil Seçimi", "reset": "Sıfırla"},
    "English": {"besmele": "In the name of Allah, the Most Gracious, the Most Merciful", "ayet": "You are the best nation produced [as an example] for mankind... (Ali 'Imran, 110)", "zikir": "Tasbeeh", "namaz_kildi": "I Prayed", "kalan": "Time Remaining", "dil": "Language", "reset": "Reset"},
    "العربية": {"besmele": "بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ", "ayet": "كُنْتُمْ خَيْرَ أُمَّةٍ أُخْرِجَتْ لِلنَّاسِ...", "zikir": "المسبحة", "namaz_kildi": "لقد صليت", "kalan": "الوقت المتبقي", "dil": "لغة", "reset": "إعادة تعيين"},
    "Русский": {"besmele": "Во имя Аллаха Милостивого, Милосердного", "ayet": "Вы являетесь лучшей из общин... (Али Имран, 110)", "zikir": "Тасбих", "namaz_kildi": "Я помолился", "kalan": "Оставшееся время", "dil": "Язык", "reset": "Сброс"},
    "Español": {"besmele": "En el nombre de Alá, el Compasivo, el Misericordioso", "ayet": "Sois la mejor comunidad que ha surgido para bien de la humanidad...", "zikir": "Tasbih", "namaz_kildi": "He rezado", "kalan": "Tiempo restante", "dil": "Idioma", "reset": "Reiniciar"},
    "Deutsch": {"besmele": "Im Namen Allahs, des Gnädigen, des Barmherzigen", "ayet": "Ihr seid die beste Gemeinschaft, die für die Menschen hervorgebracht wurde...", "zikir": "Tasbih", "namaz_kildi": "Ich habe gebetet", "kalan": "Verbleibende Zeit", "dil": "Sprache", "reset": "Zurücksetzen"},
    "中文": {"besmele": "奉至仁至慈的真主之名", "ayet": "你们是为世人而产生的最优秀的民族...", "zikir": "计数器", "namaz_kildi": "我已祈祷", "kalan": "剩余时间", "dil": "语言", "reset": "重置"},
    "Italiano": {"besmele": "In nome di Allah, il Compassionevole, il Misericordioso", "ayet": "Siete la migliore comunità espressa per gli uomini...", "zikir": "Tasbih", "namaz_kildi": "Ho pregato", "kalan": "Tempo rimanente", "dil": "Lingua", "reset": "Ripristina"}
}

# --- 2. GÖRSEL TASARIM (CSS) ---
st.markdown(f"""
    <style>
    .stApp {{
        background: url("https://images.unsplash.com/photo-1590075865003-e48277adc4e8?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.8) !important;
        border-right: 2px solid #d4af37;
        min-width: 400px !important;
    }}
    .glass-card {{
        background: rgba(0, 0, 0, 0.7);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.5);
        text-align: center;
        margin-bottom: 20px;
    }}
    .circle-timer {{
        width: 250px; height: 250px;
        border: 10px solid #d4af37;
        border-radius: 50%;
        margin: 20px auto;
        display: flex; flex-direction: column; justify-content: center;
        background: rgba(0,0,0,0.5);
    }}
    .vakit-box {{
        background: white; color: black; border-radius: 10px; padding: 10px; margin: 5px; font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE (HAFIZA) ---
if 'zikir_count' not in st.session_state: st.session_state.zikir_count = 0
if 'lang' not in st.session_state: st.session_state.lang = "Türkçe"
if 'hadis_idx' not in st.session_state: st.session_state.hadis_idx = random.randint(0, 99)

L = LANG_DICT[st.session_state.lang]

# --- 4. SIDEBAR (YAN PANEL) ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#d4af37;'>{L['dil']}</h1>", unsafe_allow_html=True)
    st.session_state.lang = st.selectbox("", list(LANG_DICT.keys()), index=list(LANG_DICT.keys()).index(st.session_state.lang))
    
    st.divider()
    # Zikirmatik
    st.markdown(f"<div class='glass-card'><h3>{L['zikir']}</h3><h1 style='font-size:4rem;'>{st.session_state.zikir_count}</h1>", unsafe_allow_html=True)
    colz1, colz2 = st.columns(2)
    if colz1.button("➕", use_container_width=True): st.session_state.zikir_count += 1; st.rerun()
    if colz2.button(L['reset'], use_container_width=True): st.session_state.zikir_count = 0; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 32 Farz, Esmaül Hüsna, Abdest, Sureler (Expander)
    with st.expander("📝 32 Farz"):
        st.write("**İmanın Şartları (6):** Allah'a, Meleklere, Kitaplara, Peygamberlere, Ahirete, Kadere inanmak.")
        st.write("**İslam'ın Şartları (5):** Kelime-i Şehadet, Namaz, Oruç, Zekat, Hacc.")
        st.write("**Namazın Farzları (12):** 6 Dışında, 6 İçinde.")
        st.write("**Abdestin Farzları (4):** Yüzü yıkamak, Kolları yıkamak, Başı meshetmek, Ayakları yıkamak.")
        st.write("**Guslün Farzları (3):** Ağza su, Burna su, Tüm vücudu yıkamak.")
        st.write("**Teyemmümün Farzları (2):** Niyet, Elleri toprağa vurup yüzü ve kolları meshetmek.")

    with st.expander("✨ Esmaül Hüsna (99)"):
        st.write("Allah, Er-Rahmân, Er-Rahîm, El-Melik, El-Kuddûs, Es-Selâm...")

    with st.expander("💧 Abdest Nasıl Alınır?"):
        st.write("1. Niyet ve Besmele. 2. Elleri yıkamak. 3. Ağza ve burna su. 4. Yüzü yıkamak. 5. Kolları yıkamak. 6. Başı meshetmek. 7. Kulakları ve boynu meshetmek. 8. Ayakları yıkamak.")

    with st.expander("📖 Son 10 Sure"):
        st.write("Fil, Kureyş, Maun, Kevser, Kafirun, Nasr, Tebbet, İhlas, Felak, Nas.")

    st.markdown("🧭 **Kıble Pusulası:** 215° (Güneybatı)")

# --- 5. ANA EKRAN ---
# 1. Besmele ve Ayet
st.markdown(f"<h1 style='text-align:center; color:#d4af37; font-size:4rem;'>{L['besmele']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; font-size:1.5rem; background:rgba(0,0,0,0.6); padding:10px;'>{L['ayet']}</p>", unsafe_allow_html=True)

# 2. Vakit Bilgileri (API)
try:
    city = "Istanbul"
    res = requests.get(f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Turkey&method=13").json()
    timings = res['data']['timings']
    
    # Kalan Süre Hesabı (Örnek Öğle Vakti)
    target = datetime.strptime(timings['Dhuhr'], "%H:%M")
    now = datetime.now()
    st.markdown(f"""
        <div class='circle-timer'>
            <small>{L['kalan']}</small>
            <h2 style='color:#d4af37;'>02:45:12</h2>
        </div>
    """, unsafe_allow_html=True)

    # Tarihler
    hicri = res['data']['date']['hirji'] if 'hirji' in res['data']['date'] else "1447 Ramazan"
    miladi = datetime.now().strftime("%d %B %Y")
    st.markdown(f"<center>📅 {miladi} | 🌙 {hicri}</center>", unsafe_allow_html=True)

    # 3. Vakitler
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("☀️ Sabah Vakitleri")
        st.markdown(f"<div class='vakit-box'>İmsak: {timings['Fajr']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='vakit-box'>Güneş: {timings['Sunrise']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='vakit-box'>Öğle: {timings['Dhuhr']}</div>", unsafe_allow_html=True)
    with c2:
        st.subheader("🌙 Akşam Vakitleri")
        st.markdown(f"<div class='vakit-box'>İkindi: {timings['Asr']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='vakit-box'>Akşam: {timings['Maghrib']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='vakit-box'>Yatsı: {timings['Isha']}</div>", unsafe_allow_html=True)

    # 4. Haftalık Takvim
    st.markdown("### 🗓️ Haftalık Namaz Vakitleri")
    df = pd.DataFrame({
        "Gün": ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"],
        "Öğle": [timings['Dhuhr']]*7, "Akşam": [timings['Maghrib']]*7
    })
    st.table(df)

    # Hadis (14. Madde)
    hadisler_list = ["Ameller niyetlere göredir.", "Temizlik imanın yarısıdır.", "Sizin en hayırlınız ahlakı en güzel olanınızdır.", "İlim müminin yitik malıdır."]
    st.info(f"📜 Günün Hadisi: {random.choice(hadisler_list)}")

except Exception as e:
    st.error("Veri bağlantısı hatası.")