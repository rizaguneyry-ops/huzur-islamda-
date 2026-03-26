import streamlit as st
import requests
import json
import os

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# Arka Plan Görseli (Cami ve Gece Gökyüzü)
BG_IMAGE = "https://cdn.pixabay.com/photo/2023/03/05/13/21/mosque-7831383_1280.png"

# --- 2. GELİŞMİŞ CSS (Görseldeki Tasarımın Aynısı) ---
st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.85)), url("{BG_IMAGE}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    
    /* Vakit Kartları (Krem Rengi - Görseldeki Gibi) */
    .vakit-container {{
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 20px;
    }}
    .vakit-box {{
        background: #fdf6e3; border-radius: 15px; padding: 15px; text-align: center;
        border: 1px solid #d4af37; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    .vakit-title {{ color: #7f8c8d; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
    .vakit-time {{ color: #2c3e50; font-size: 22px; font-weight: bold; }}

    /* Alt Üçlü Modül (Zümrüt Yeşili) */
    .bottom-module {{
        background: #153e35; border-radius: 20px; padding: 20px; text-align: center;
        border: 1px solid #d4af37; height: 280px; position: relative;
    }}
    .module-head {{ color: #fbbf24; font-size: 16px; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid rgba(251,191,36,0.2); }}
    
    /* Buton Tasarımları */
    .stButton>button {{
        width: 100%; border-radius: 25px; background: linear-gradient(90deg, #d4af37, #b8860b);
        color: white; font-weight: bold; border: none; height: 45px; margin-top: 10px;
    }}
    
    /* Tarih Bilgisi */
    .header-info {{ text-align: center; color: white; margin-bottom: 10px; }}
    .hijri {{ color: #10b981; font-style: italic; font-size: 16px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. VERİ ÇEKME VE TÜRKÇELEŞTİRME ---
tr_aylar = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}
sehir = st.sidebar.selectbox("📍 Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya"])

try:
    res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13").json()['data']
    v = res['timings']
    g = res['date']['gregorian']
    h = res['date']['hijri']
    
    # Başlık Alanı
    st.markdown(f"""
        <div class="header-info">
            <h2 style='margin-bottom:0;'>{g['day']} {tr_aylar.get(g['month']['en'])} {g['year']}</h2>
            <div class="hijri">{h['day']} {h['month']['en']} {h['year']}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 4. CANLI GERİ SAYIM (GÖRSELDEKİ YUVARLAK TASARIM) ---
    # JavaScript ile doğrudan HTML/CSS kullanarak geri sayımı çalıştırıyoruz
    v_times = {"SABAH": v['Fajr'], "GÜNEŞ": v['Sunrise'], "ÖĞLE": v['Dhuhr'], "İKİNDİ": v['Asr'], "AKŞAM": v['Maghrib'], "YATSI": v['Isha']}
    
    countdown_js = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: sans-serif;">
        <div style="border: 4px solid #d4af37; border-radius: 50%; width: 220px; height: 220px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.4); box-shadow: 0 0 20px rgba(212,175,55,0.4);">
            <div style="color: white; font-size: 12px; letter-spacing: 2px; margin-bottom: 5px;">YATSI VAKTİNE KALAN</div>
            <div id="timer" style="color: #fbbf24; font-size: 42px; font-weight: bold; font-family: monospace;">00:00:00</div>
        </div>
    </div>

    <script>
        const v = {json.dumps(v_times)};
        function update() {{
            const now = new Date();
            const s = now.getHours()*3600 + now.getMinutes()*60 + now.getSeconds();
            let target = null;
            for(let k in v) {{
                let [h,m] = v[k].split(':');
                let vs = parseInt(h)*3600 + parseInt(m)*60;
                if(vs > s) {{ target = vs; break; }}
            }}
            if(!target) {{ let [h,m] = v['SABAH'].split(':'); target = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = target - s;
            let h = Math.floor(d/3600); let m = Math.floor((d%3600)/60); let sec = d%60;
            document.getElementById('timer').innerHTML = (h<10?'0'+h:h)+":"+(m<10?'0'+m:m)+":"+(sec<10?'0'+sec:sec);
        }}
        setInterval(update, 1000); update();
    </script>
    """
    st.components.v1.html(countdown_js, height=250)

    # --- 5. VAKİT KARTLARI (3 ÜST, 3 ALT) ---
    v_list = list(v_times.items())
    c1 = st.columns(3)
    for i in range(3):
        with c1[i]:
            st.markdown(f'<div class="vakit-box"><div class="vakit-title">{v_list[i][0]}</div><div class="vakit-time">{v_list[i][1]}</div></div>', unsafe_allow_html=True)
    c2 = st.columns(3)
    for i in range(3, 6):
        with c2[i-3]:
            st.markdown(f'<div class="vakit-box"><div class="vakit-title">{v_list[i][0]}</div><div class="vakit-time">{v_list[i][1]}</div></div>', unsafe_allow_html=True)

except:
    st.error("Veri alınırken hata oluştu.")

# --- 6. ALT MODÜLLER (YAN YANA ÜÇLÜ) ---
st.write("")
col_esma, col_zikir, col_sure = st.columns(3)

with col_esma:
    st.markdown("""<div class="bottom-module"><div class="module-head">ESMAÜL HÜSNA</div>
    <div style="font-size:35px; color:#fbbf24; margin:10px 0;">الله</div>
    <div style="font-size:14px; color:#ecf0f1;">Ya Rahman, Ya Rahim, Ya Melik...</div><br>
    </div>""", unsafe_allow_html=True)
    st.button("TÜM LİSTE", key="e1")

with col_zikir:
    if 'count' not in st.session_state: st.session_state.count = 0
    st.markdown(f"""<div class="bottom-module"><div class="module-head">ZİKİRMATİK</div>
    <div style="font-size:60px; color:#fbbf24; font-weight:bold; margin:20px 0;">{st.session_state.count}</div>
    </div>""", unsafe_allow_html=True)
    if st.button("➕ ZİKİR EKLE"):
        st.session_state.count += 1
        st.rerun()

with col_sure:
    st.markdown("""<div class="bottom-module"><div class="module-head">SÜRELER</div>
    <div style="text-align:left; font-size:13px; color:#bdc3c7;">
    Yasin, Mülk, Nebe...<br><br>Kısa Namaz Süreleri ve Dualar bu bölümde yer alır.
    </div></div>""", unsafe_allow_html=True)
    st.button("SURE SEÇ", key="s1")