import streamlit as st
import requests
import json
import os
from datetime import datetime
import random

# --- 1. GELİŞMİŞ SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda", page_icon="🌙", layout="wide")

# Premium CSS Tasarımı (Altın ve Zümrüt Teması)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    
    /* Logo ve Başlık */
    .header-box { text-align: center; padding: 30px; border-bottom: 2px solid #d4af37; margin-bottom: 25px; background: linear-gradient(180deg, #1c212b 0%, #0e1117 100%); }
    .logo-main { font-size: 60px; margin-bottom: 10px; }
    .title-main { font-size: 35px; font-weight: bold; letter-spacing: 3px; color: #d4af37; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    
    /* Kartlar ve Kutular */
    .vakit-card { padding: 20px; border-radius: 15px; background: #1c212b; border-top: 5px solid #2e7d32; text-align: center; margin-bottom: 15px; transition: 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .vakit-card:hover { border-top: 5px solid #d4af37; transform: translateY(-5px); }
    .info-card { padding: 25px; border-radius: 20px; background: #1c212b; border: 1px solid #2e7d32; margin-bottom: 20px; font-size: 18px; line-height: 1.6; }
    
    /* Butonlar */
    .stButton>button { width: 100%; border-radius: 50px; background: linear-gradient(135deg, #2e7d32 0%, #d4af37 100%); color: white; font-weight: bold; border: none; height: 55px; font-size: 18px; box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4); }
    .stButton>button:hover { background: linear-gradient(135deg, #4caf50 0%, #f1c40f 100%); }
    
    /* Sekme Fontları */
    .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: 600; padding: 12px 25px; }
    </style>
    
    <div class="header-box">
        <div class="logo-main">🌙🕌</div>
        <div class="title-main">HUZUR İSLAMDA</div>
        <div style="color: #4caf50; letter-spacing: 5px; font-size: 14px;">DİJİTAL İBADET REHBERİ v5.2</div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
DB_FILE = "user_data.json"
def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"zikir": 0, "dualar": []}, f)
    with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_data(d):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# --- 3. İÇERİK HAVUZU ---
ayetler = [
    "Şüphesiz güçlükle beraber bir kolaylık vardır. (İnşirah, 5)",
    "Allah sabredenlerle beraberdir. (Bakara, 153)",
    "Kalpler ancak Allah’ı anmakla huzur bulur. (Ra’d, 28)",
    "İyilik yapın, kuşkusuz Allah iyilik yapanları sever. (Bakara, 195)"
]
dini_gunler_2026 = [
    ("Ramazan Başlangıcı", "19 Mart 2026 Perşembe"),
    ("Kadir Gecesi", "14 Nisan 2026 Salı"),
    ("Ramazan Bayramı", "18 Nisan 2026 Cumartesi"),
    ("Kurban Bayramı", "25 Haziran 2026 Perşembe"),
    ("Aşure Günü", "25 Temmuz 2026 Cumartesi"),
    ("Mevlid Kandili", "22 Eylül 2026 Salı")
]

# --- 4. ANA SEKME YAPISI ---
t1, t2, t3, t4, t5 = st.tabs(["📍 Vakitler", "🗓️ Takvim", "📖 Rehber", "📿 Zikirmatik", "📝 Dualarım"])

# --- VAKİTLER ---
with t1:
    sehir = st.selectbox("Şehir Seçiniz", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Konya", "Adana", "Trabzon", "Gaziantep", "Samsun"])
    try:
        res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13", timeout=10).json()['data']
        v = res['timings']
        st.success(f"🕌 Hicri Tarih: {res['date']['hijri']['day']} {res['date']['hijri']['month']['en']} {res['date']['hijri']['year']}")
        
        cols = st.columns(3)
        v_list = [("İmsak", v['Fajr']), ("Güneş", v['Sunrise']), ("Öğle", v['Dhuhr']), ("İkindi", v['Asr']), ("Akşam", v['Maghrib']), ("Yatsı", v['Isha'])]
        for i, (ad, s) in enumerate(v_list):
            with cols[i%3]:
                st.markdown(f'<div class="vakit-card"><b style="color:#d4af37">{ad}</b><br><span style="font-size:22px">{s}</span></div>', unsafe_allow_html=True)
    except: st.error("Vakitler şu an alınamıyor.")

# --- TAKVİM ---
with t2:
    st.subheader("🗓️ 2026 Önemli Dini Günler")
    for g, t in dini_gunler_2026:
        st.markdown(f'<div style="background:#1c212b; padding:15px; border-radius:12px; margin-bottom:10px; border-left:4px solid #d4af37;"><b>{g}</b><br><span style="color:#4caf50">{t}</span></div>', unsafe_allow_html=True)

# --- REHBER (AYET/HADİS/İLMİHAL) ---
with t3:
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown(f'<div class="info-card"><b style="color:#d4af37">📖 Günün Ayeti</b><br>{random.choice(ayetler)}</div>', unsafe_allow_html=True)
    with col_right:
        st.markdown(f'<div class="info-card"><b style="color:#d4af37">📻 Diyanet Radyo</b><br>Canlı Yayını Dinleyin</div>', unsafe_allow_html=True)
        st.audio("https://dyradyo.motiwe.com/diyanetradyo/diyanetradyo/playlist.m3u8")
    
    with st.expander("📚 Temel İlmihal Bilgileri"):
        st.write("**İslamın Şartları:** 1. Şehadet, 2. Namaz, 3. Zekat, 4. Oruç, 5. Hac.")
        st.write("**Abdestin Farzları:** 1. Yüzü yıkamak, 2. Kolları yıkamak, 3. Başın 1/4'ünü meshetmek, 4. Ayakları yıkamak.")

# --- ZİKİRMATİK ---
with t4:
    st.markdown(f"<h1 style='text-align: center; color: #4caf50; font-size: 120px; text-shadow: 0 0 20px rgba(76, 175, 80, 0.4);'>{data['zikir']}</h1>", unsafe_allow_html=True)
    if st.button("➕ ZİKİR ÇEK"):
        data['zikir'] += 1
        save_data(data)
        st.rerun()
    if st.button("🔄 SIFIRLA"):
        data['zikir'] = 0
        save_data(data)
        st.rerun()

# --- DUALARIM ---
with t5:
    y_dua = st.text_area("Kalbinizden geçen duayı yazın...")
    if st.button("Dua Defterime Kaydet") and y_dua:
        data['dualar'].append({"m": y_dua, "t": datetime.now().strftime("%d.%m.%Y %H:%M")})
        save_data(data)
        st.success("Duanız kaydedildi.")
        st.rerun()
    
    st.divider()
    for d in reversed(data['dualar'][-10:]):
        st.info(f"🙏 {d['m']} \n\n *({d['t']})*")