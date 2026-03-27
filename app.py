import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Huzur İslamda Pro Max", page_icon="🕋", layout="wide")

# --- 2. VERİ SETLERİ ---
tr_aylar = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}

sehirler_81 = ["Adana", "Adiyaman", "Afyonkarahisar", "Agri", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydin", "Balikesir", "Bartin", "Batman", "Bayburt", "Bilecik", "Bingol", "Bitlis", "Bolu", "Burdur", "Bursa", "Canakkale", "Cankiri", "Corum", "Denizli", "Diyarbakir", "Duzce", "Edirne", "Elazig", "Erzincan", "Erzurum", "Eskisehir", "Gaziantep", "Giresun", "Gumushane", "Hakkari", "Hatay", "Igdir", "Isparta", "Istanbul", "Izmir", "Kahramanmaras", "Karabuk", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kilis", "Kirikkale", "Kirklareli", "Kirsehir", "Kocaeli", "Konya", "Kutahya", "Malatya", "Manisa", "Mardin", "Mersin", "Mugla", "Mus", "Nevsehir", "Nigde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Sanliurfa", "Siirt", "Sinop", "Sivas", "Sirnak", "Tekirdag", "Tokat", "Trabzon", "Tunceli", "Usak", "Van", "Yalova", "Yozgat", "Zonguldak"]

EZAN_URL = "https://www.namazvaktim.org/ses/ezan1.mp3"

# SON 10 SURE (OKUNUŞ VE ANLAM)
son_on_sure_data = {
    "Fil Suresi": {"oku": "Elem tera keyfe fe'ale rabbüke bi ashâbil fîl. Elem yec'al keydehüm fî tadlîl. Ve ersele aleyhim tayran ebâbîl. Termîhim bi hicâratin min siccîl. Fe ce'alehüm ke'asfin me'kûl.", "meal": "Rabbinin, fil sahiplerine ne yaptığını görmedin mi? Onların tuzaklarını boşa çıkarmadı mı? Onların üzerine sürü sürü kuşlar gönderdi. O kuşlar onlara pişmiş çamurdan taşlar atıyorlardı. Nihayet onları yenilmiş ekin yaprağı gibi yaptı."},
    "Kureyş Suresi": {"oku": "Li îlâfi kureyş. Îlâfihim rihleteş şitâi ves sayf. Felyâ'büdû rabbe hâzel beyt. Ellezî at'amehüm min cû'in ve âmenehüm min havf.", "meal": "Kureyş'e kolaylaştırıldığı, kış ve yaz seyahatleri onlara kolaylaştırıldığı için; onlar da kendilerini açlıktan doyuran ve her çeşit korkudan emin kılan şu evin (Kabe'nin) Rabbine ibadet etsinler."},
    "Mâûn Suresi": {"oku": "Era'eytellezî yükezzibü bid dîn. Fezâlikellezî yedü'ul yetîm. Ve lâ yehuddu alâ taâmil miskîn. Feveylün lil musallîn. Ellezînehüm an salâtihim sâhûn. Ellezînehüm yürâûn. Ve yemne'ûnel mâûn.", "meal": "Dini yalanlayanı gördün mü? İşte o, yetimi itip kakar; yoksulu doyurmaya teşvik etmez. Yazıklar olsun o namaz kılanlara ki, onlar namazlarını ciddiye almazlar. Onlar gösteriş yaparlar ve hayra engel olurlar."},
    "Kevser Suresi": {"oku": "İnnâ a'taynâkel kevser. Fe salli li rabbike venhar. İnne şânieke hüvel ebter.", "meal": "Şüphesiz biz sana Kevser'i verdik. Öyleyse Rabbin için namaz kıl ve kurban kes. Asıl sonu kesik olan, sana buğzeden (sana dil uzatan)dir."},
    "Kâfirûn Suresi": {"oku": "Kul yâ eyyühel kâfirûn. Lâ a'büdü mâ ta'büdûn. Ve lâ entüm âbidûne mâ a'büd. Ve lâ ene âbidün mâ abedtüm. Ve lâ entüm âbidûne mâ a'büd. Leküm dînüküm veliye dîn.", "meal": "De ki: Ey kafirler! Ben sizin tapmakta olduklarınıza tapmam. Siz de benim taptığıma tapmıyorsunuz. Ben sizin taptıklarınıza tapacak değilim. Siz de benim taptığıma tapacak değilsiniz. Sizin dininiz size, benim dinim banadır."},
    "Nasr Suresi": {"oku": "İzâ câe nasrullâhi vel feth. Ve raeyten nâse yedhulûne fî dînillâhi efvâcâ. Fe sebbih bi hamdi rabbike vestagfirh. İnnehû kâne tevvâbâ.", "meal": "Allah'ın yardımı ve fetih (Mekke'nin fethi) geldiğinde; ve insanların bölük bölük Allah'ın dinine girdiklerini gördüğünde; artık Rabbini hamd ile tesbih et ve O'ndan bağışlama dile. Şüphesiz O, tevbeleri çok kabul edendir."},
    "Tebbet Suresi": {"oku": "Tebbet yedâ ebî lehebin ve tebb. Mâ agnâ anhü mâlühû ve mâ keseb. Seyaslâ nâran zâte leheb. Vemraetühû hammâletel hatab. Fî cîdihâ hablün min mesed.", "meal": "Ebu Leheb'in iki eli kurusun! Kurudu da. Malı ve kazandıkları ona fayda vermedi. O, alevli bir ateşe girecektir. Boynunda bükülmüş hurma lifinden bir ip olduğu halde odun taşıyıcı karısı da ateşe girecektir."},
    "İhlâs Suresi": {"oku": "Kul hüvallâhü ehad. Allâhüs samed. Lem yelid ve lem yûled. Ve len yekün lehû küfüven ehad.", "meal": "De ki: O Allah birdir. Allah sameddir (her şey O'na muhtaçtır, O hiçbir şeye muhtaç değildir). O, doğurmamış ve doğmamıştır. Onun hiçbir dengi yoktur."},
    "Felak Suresi": {"oku": "Kul e'ûzü bi rabbil felak. Min şerri mâ halak. Ve min şerri gâsikin izâ vekab. Ve min şerrin neffâsâti fîl ukad. Ve min şerri hâsidin izâ hased.", "meal": "De ki: Yarattığı şeylerin kötülüğünden, karanlığı çöktüğü zaman gecenin kötülüğünden, düğümlere üfleyenlerin kötülüğünden ve haset ettiği vakit hasetçinin kötülüğünden, sabah aydınlığının Rabbine sığınırım."},
    "Nâs Suresi": {"oku": "Kul e'ûzü bi rabbin nâs. Melikin nâs. İlâhin nâs. Min şerril vesvâsil hannâs. Ellezî yüvesvisü fî sudûrin nâs. Minel cinneti ven nâs.", "meal": "De ki: İnsanların Rabbine, insanların Melik'ine, insanların İlâh'ına; insanların göğüslerine vesvese veren, sinsi vesvesecinin şerrinden Allah'a sığınırım. O vesveseci, cinlerden de olur insanlardan da."}
}

# --- 3. CSS (TASARIM VE OKUNABİLİRLİK) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?q=80&w=2000") !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .besmele { text-align: center; color: #d4af37 !important; font-size: 2.8rem; font-family: 'Times New Roman', serif; margin-bottom: 20px; font-style: italic; text-shadow: 2px 2px 10px rgba(212,175,55,0.5); }
    .stMarkdown, p, h1, h2, h3, span { color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,1); }
    .vakit-box { background: rgba(253, 246, 227, 0.98); border-radius: 12px; padding: 15px; text-align: center; border: 2px solid #d4af37; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .vakit-box div { color: #1a2a24 !important; text-shadow: none !important; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: rgba(10, 30, 25, 0.98) !important; border-right: 2px solid #d4af37; }
    .stExpander { background-color: #ffffff !important; border-radius: 8px !important; border: 1px solid #d4af37; margin-bottom: 10px; }
    .stExpander p, .stExpander span, .stExpander label, .stExpander div { color: #000000 !important; text-shadow: none !important; font-weight: 500; }
    .sure-box { background: #f9f9f9; padding: 10px; border-radius: 5px; border-left: 4px solid #d4af37; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. KENAR MENÜ (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🕋 İslami Portal</h2>", unsafe_allow_html=True)
    sel_lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English", "العربية"])
    sehir = st.selectbox("📍 Şehir Seç", sehirler_81, index=sehirler_81.index("Istanbul"))
    
    st.write("---")
    
    with st.expander("📖 Son On Sure (Okunuş ve Anlam)", expanded=False):
        for s_ad, s_içerik in son_on_sure_data.items():
            st.markdown(f"##### 🔹 {s_ad}")
            st.markdown(f"<div class='sure-box'><b>Okunuşu:</b><br><i>{s_içerik['oku']}</i></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sure-box'><b>Anlamı:</b><br>{s_içerik['meal']}</div>", unsafe_allow_html=True)
            st.write("---")

    with st.expander("📿 Zikirmatik", expanded=False):
        if 'zk' not in st.session_state: st.session_state.zk = 0
        st.write(f"Sayı: **{st.session_state.zk}**")
        if st.button("Zikir Çek (+1)", key="zk_plus"): st.session_state.zk += 1; st.rerun()
        if st.button("Sıfırla", key="zk_zero"): st.session_state.zk = 0; st.rerun()

    with st.expander("📊 Kaza Takibi", expanded=False):
        for kv in ["Sabah", "Öğle", "İkindi", "Akşam", "Yatsı"]:
            k_key = f"kaza_st_{kv}"
            if k_key not in st.session_state: st.session_state[k_key] = 0
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{kv}**")
            if c2.button(f"{st.session_state[k_key]}", key=f"btn_kaza_side_{kv}"): st.session_state[k_key] += 1; st.rerun()

    with st.expander("📜 Detaylı 32 Farz", expanded=False):
        st.markdown("**İman (6):** Allah, Melek, Kitap, Peygamber, Ahiret, Kader.\n\n**İslam (5):** Şehadet, Namaz, Oruç, Zekat, Hac.\n\n**Namaz (12):** *Dış:* Hadesten Taharet, Necasetten Taharet, Setr-i Avret, İstikbal-i Kıble, Vakit, Niyet. *İç:* İftitah Tekbiri, Kıyam, Kıraat, Rükû, Sücud, Ka'de-i Ahire.\n\n**Abdest (4), Gusül (3), Teyemmüm (2).**")

    st.write("---")
    ezan_on = st.toggle("📢 Ezan Sesi", value=True)
    uyari_on = st.toggle("⏳ 30 Dk Hatırlatıcı", value=True)

# --- 5. ANA EKRAN ---
st.markdown("<div class='besmele'>Bismillahirrahmanirrahim</div>", unsafe_allow_html=True)

try:
    url = f"http://api.aladhan.com/v1/timingsByCity?city={sehir}&country=Turkey&method=13"
    data = requests.get(url).json()['data']
    v = data['timings']
    t_g = data['date']['gregorian']
    t_h = data['date']['hijri']
    
    miladi = f"{t_g['day']} {tr_aylar.get(t_g['month']['en'])} {t_g['year']}"
    hicri = f"{t_h['day']} {t_h['month']['ar']} {t_h['year']}"
    
    simdi_str = datetime.now().strftime("%H:%M")
    v_order = {"İMSAK": v['Fajr'], "GÜNEŞ": v['Sunrise'], "ÖĞLE": v['Dhuhr'], "İKİNDİ": v['Asr'], "AKŞAM": v['Maghrib'], "YATSI": v['Isha']}

    for ad, saat in v_order.items():
        if simdi_str == saat and ezan_on: st.markdown(f'<audio autoplay><source src="{EZAN_URL}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        h_saat = (datetime.strptime(saat, "%H:%M") + timedelta(minutes=30)).strftime("%H:%M")
        if simdi_str == h_saat and uyari_on: st.warning(f"🕋 {ad} vakti girdi. Namaz kılındı mı?")

    st.markdown(f"<h1 style='text-align:center;'>{sehir.upper()}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#fbbf24 !important;'>📅 {miladi} | 🌙 {hicri}</p>", unsafe_allow_html=True)

    # Geri Sayım Halka
    st.components.v1.html(f"""
    <div style="display: flex; justify-content: center; margin: 15px 0;">
        <div style="border: 5px solid #d4af37; border-radius: 50%; width: 140px; height: 140px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.7); box-shadow: 0 0 20px #d4af37;">
            <div id="c" style="color: #fbbf24; font-size: 28px; font-weight: bold; font-family: monospace;">00:00:00</div>
        </div>
    </div>
    <script>
        const v = {json.dumps(v_order)};
        function u() {{
            const n = new Date(); const s = n.getHours()*3600 + n.getMinutes()*60 + n.getSeconds();
            let t = null; for(let k in v) {{ let [h,m] = v[k].split(':'); let vs = parseInt(h)*3600+parseInt(m)*60; if(vs>s) {{ t=vs; break; }} }}
            if(!t) {{ let [h,m] = v['İMSAK'].split(':'); t = parseInt(h)*3600+parseInt(m)*60+86400; }}
            let d = t-s; let h=Math.floor(d/3600), m=Math.floor((d%3600)/60), sc=d%60;
            document.getElementById('c').innerHTML = (h<10?'0'+h:h)+":"+(m<10?'0'+m:m)+":"+(sc<10?'0'+sc:sc);
        }} setInterval(u, 1000); u();
    </script>""", height=180)

    cols = st.columns(6)
    keys = list(v_order.keys())
    for i in range(6):
        with cols[i]: st.markdown(f'<div class="vakit-box"><div>{keys[i]}</div><div style="font-size:22px;">{v_order[keys[i]]}</div></div>', unsafe_allow_html=True)

except Exception: st.error("Lütfen internet bağlantınızı kontrol edin.")

time.sleep(60)
st.rerun()