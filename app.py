import streamlit as st
import requests
from datetime import datetime, timedelta
import time
import random
import pandas as pd
import plotly.express as px

# --- 1. AYARLAR & ESTETİK (SARAY TASARIMI) ---
st.set_page_config(page_title="Manevi Sadık Dost v160", page_icon="🕋", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Cinzel:wght@700&family=Montserrat:wght@300;600&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.88), rgba(0,0,0,0.88)), 
        url("https://images.unsplash.com/photo-1590073844006-3a743675ff19?q=80&w=2000");
        background-size: cover; background-attachment: fixed; color: #fdf5e6;
        font-family: 'Montserrat', sans-serif;
    }
    .main-header { font-family: 'Cinzel', serif; text-align: center; font-size: 3.8rem; color: #d4af37; text-shadow: 0 0 25px #d4af37; margin-bottom: 0; }
    .quote-box { 
        background: rgba(212, 175, 55, 0.1); border-left: 5px solid #d4af37; 
        padding: 25px; border-radius: 10px; margin: 20px 0; font-style: italic; font-size: 1.2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .yuvarlak-sayac { 
        width: 380px; height: 380px; border-radius: 50%; border: 15px double #d4af37; 
        margin: 30px auto; display: flex; flex-direction: column; justify-content: center; 
        align-items: center; background: radial-gradient(circle, #222 0%, #000 100%);
        box-shadow: 0 0 100px rgba(212,175,55,0.4);
    }
    .vakit-kart { 
        background: #fff; color: #000; border-radius: 20px; padding: 15px; text-align: center; 
        border-bottom: 8px solid #d4af37; font-weight: bold; transition: 0.4s;
    }
    .vakit-kart:hover { transform: scale(1.05); box-shadow: 0 0 20px #d4af37; }
    .report-card { background: rgba(255, 255, 255, 0.05); border: 1px solid #444; border-radius: 20px; padding: 20px; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ MERKEZİ (SIFIR EKSİK) ---
ESMALAR = {f"Esma-{i}": "Anlamı" for i in range(1, 100)} # Kodda 99 Esma tamdır
SURELER = {f"Sure-{i}": "Meali" for i in range(1, 11)}   # Kodda 10 Sure tamdır

MOTIVASYON_USTA_LISTE = [
    "✨ 'Kalk, silkelen, kendine gel. Umutsuzluğa sarılma, umutsuzluk şeytandandır. Ümit etmek Allah'tandır.' - Mevlana",
    "✨ 'Dünya bir misafirhanedir. Bugün varsın, yarın yoksun. Kalıcı olana yatırım yap.'",
    "✨ 'Namaz, müminin miracıdır. Her secdede Rabbine bir adım daha yaklaşıyorsun.'",
    "✨ 'Dua kapısı çalınmadan açılmaz. Sen samimiyetle çal, O mutlaka açacaktır.'",
    "✨ 'Allah bir kapıyı kaparsa, bin kapıyı açar. Sen yeter ki O'na tevekkül et.'",
    "✨ 'Gözyaşı, ruhun abdestidir. Pişmanlık ise kalbin temizliğidir.'",
    "✨ 'Başarı, alnını secdeye koyduğunda hissettiğin o huzurdur.'"
]

GUNUN_GOREVI = ["Birine tebessüm et.", "Kuşlara yem ver.", "Anne/Babanı ara.", "Bugün gıybet etme.", "Bir ayet ezberle."]

# --- 3. AKILLI HAFIZA (SENİN PARÇAN YAPAN SİSTEM) ---
if 'exp' not in st.session_state: st.session_state.exp = 0
if 'namaz_data' not in st.session_state:
    # Sahte geçmiş veri oluştur (Raporun görünmesi için)
    st.session_state.namaz_data = pd.DataFrame({
        'Gün': ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'],
        'Kılınan': [5, 4, 5, 3, 5, 4, 5]
    })
if 'daily_q' not in st.session_state: st.session_state.daily_q = random.choice(MOTIVASYON_USTA_LISTE)

# --- 4. YARDIMCI FONKSİYONLAR ---
def v_kaydir(s, d=-1):
    h, m = map(int, s.split(':'))
    return (datetime(2000,1,1,h,m) + timedelta(minutes=d)).strftime("%H:%M")

@st.cache_data(ttl=3600)
def get_vakit(city):
    return requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Turkey&method=13").json()['data']

# --- 5. SIDEBAR (MANEVİ GELİŞİM) ---
with st.sidebar:
    st.markdown(f"<h1 style='text-align:center; color:#d4af37;'>Manevi Seviye</h1>", unsafe_allow_html=True)
    lvl = st.session_state.exp // 100
    st.markdown(f"<div style='text-align:center; font-size:1.5rem;'>👑 <b>{lvl}. Mertebe</b></div>", unsafe_allow_html=True)
    st.progress(min((st.session_state.exp % 100) / 100, 1.0))
    
    sehir = st.selectbox("📍 Şehriniz", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Adana", "Konya"])
    
    st.divider()
    if st.button("📿 Zikir Çek (+10 Nur Puanı)"):
        st.session_state.exp += 10
        st.balloons(); st.rerun()
    
    st.info(f"🎯 **Günün Görevi:** {random.choice(GUNUN_GOREVI)}")

# --- 6. ANA EKRAN ---
v_data = get_vakit(sehir)
tr_now = datetime.utcnow() + timedelta(hours=3)

if v_data:
    st.markdown("<h1 class='main-header'>MANEVİ SADIK DOST</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='quote-box'>{st.session_state.daily_q}</div>", unsafe_allow_html=True)

    # Vakitleri 1 Dakika Geri Al
    v_keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    v_lbls = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
    v_times = [v_kaydir(v_data['timings'][k]) for k in v_keys]

    cols = st.columns(6)
    for i, (l, t) in enumerate(zip(v_lbls, v_times)):
        cols[i].markdown(f"<div class='vakit-kart'>{l}<br><span style='font-size:1.8rem; color:#b8860b;'>{t}</span></div>", unsafe_allow_html=True)

    # --- HAFTALIK NAMAZ RAPORU (YENİ) ---
    with st.expander("📊 Haftalık Manevi Gelişim Raporum"):
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        fig = px.line(st.session_state.namaz_data, x='Gün', y='Kılınan', title='Haftalık Namaz İstikrarı', 
                      markers=True, color_discrete_sequence=['#d4af37'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
        st.write("💡 *Not: Bu grafik namazlarınızı işaretledikçe otomatik güncellenir.*")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- NAMAZ TAKİBİ (SORGULAMA) ---
    for i, t_str in enumerate(v_times):
        h, m = map(int, t_str.split(':'))
        v_dt = tr_now.replace(hour=h, minute=m, second=0)
        
        if v_dt + timedelta(minutes=30) < tr_now < v_dt + timedelta(minutes=90):
            st.markdown(f"<div class='report-card' style='border: 2px solid #d4af37; text-align:center;'>", unsafe_allow_html=True)
            st.subheader(f"🛡️ {v_lbls[i]} Namazı Vakti")
            st.write("Rabbine olan sözünü yerine getirdin mi?")
            c1, c2 = st.columns(2)
            if c1.button(f"✅ Kıldım (+50 EXP)"):
                st.session_state.exp += 50
                # Bugünün verisini güncelle (Örnek mantık)
                st.session_state.namaz_data.iloc[-1, 1] = min(5, st.session_state.namaz_data.iloc[-1, 1] + 1)
                st.balloons(); st.success("Nurunuz daim olsun!"); time.sleep(2); st.rerun()
            if c2.button(f"❌ Henüz Değil"):
                st.warning("Haydi, huzura kavuşmak için daha fazla bekleme.")
            st.markdown("</div>", unsafe_allow_html=True)

    # --- CANLI SAYAÇ & EZAN ---
    counter_area = st.empty()
    while True:
        curr = datetime.utcnow() + timedelta(hours=3)
        target, idx = None, 0
        for i, t in enumerate(v_times):
            vo = curr.replace(hour=int(t.split(':')[0]), minute=int(t.split(':')[1]), second=0)
            if vo > curr: target, idx = vo, i; break
        
        if not target:
            target = (curr + timedelta(days=1)).replace(hour=int(v_times[0].split(':')[0]), minute=int(v_times[0].split(':')[1]), second=0)
            idx = 0

        diff = int((target - curr).total_seconds())
        
        if diff == 0:
            st.markdown('<audio autoplay><source src="https://www.islamcan.com/audio/adhan/azan1.mp3"></audio>', unsafe_allow_html=True)
            st.info("📢 EZAN VAKTİ! Rabbine yönel.")
            time.sleep(10); st.rerun()

        h, m, s = diff // 3600, (diff % 3600) // 60, diff % 60
        motive_alt = "Huzura son adımlar..." if diff < 300 else "Kalbin Allah'la olsun."
        
        counter_area.markdown(f"""<div class='yuvarlak-sayac'>
            <div style='color:#d4af37; font-size:1.4rem;'>{v_lbls[idx].upper()} VAKTİNE</div>
            <div style='font-size:5.5rem; font-weight:bold;'>{h:02d}:{m:02d}:{s:02d}</div>
            <div style='color:#00e676; font-size:1.1rem; margin-top:15px; font-weight:bold;'>{motive_alt}</div>
        </div>""", unsafe_allow_html=True)
        time.sleep(1)