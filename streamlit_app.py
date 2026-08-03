"""
====================================================================================
STREAMLIT COMMUNITY CLOUD ARAYÜZÜ (STREAMLIT_APP.PY)
====================================================================================
Hugging Face Spaces CPU kota sınırlarına takılmadan %100 ÜCRETSİZ ve KESİNTİSİZ 
canlı yayın yapmak için hazırlanan Streamlit arayüzü.

Özellikler:
- Streamlit Community Cloud (share.streamlit.io) üzerinde sınırsız yayınlanır.
- Aladhan Public API, SQLite veritabanı okuma/yazma/arama, Jinja2 sohbet şablonu ve 
  Trace Loglarını canlı görüntüler.
====================================================================================
"""

import sys
import os
import streamlit as st

# src klasöründeki modüllere erişim sağlama
src_path = os.path.join(os.path.dirname(__file__), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from agent import IslamicToolCallingAgent
    from database import get_all_inquiries, search_inquiries
except ImportError:
    from src.agent import IslamicToolCallingAgent
    from src.database import get_all_inquiries, search_inquiries

# Sayfa yapılandırması
st.set_page_config(
    page_title="Namaz Vakti & Fıkıh Asistanı",
    page_icon="🕌",
    layout="wide"
)

# Ajan örneğini önbelleğe alma (Caching)
@st.cache_resource
def load_agent():
    return IslamicToolCallingAgent()

agent = load_agent()

# Başlık ve Açıklama
st.title("🕌 Namaz Vakti ve Fıkıh Asistanı (Magibu AI)")
st.caption("Public API Entegrasyonu (Aladhan API), SQLite Veritabanı, Custom Jinja2 Chat Template ve Tool Calling Trace Logları")

# Sekme Yapısı
tab1, tab2, tab3 = st.tabs(["💬 Sohbet Arayüzü", "⚙️ Tool Call & Jinja2 Trace Logları", "🗄️ SQLite Veritabanı Kayıtları"])

# Sohbet Geçmişi Durumu
if "messages" not in st.session_state:
    st.session_state.messages = []
if "latest_trace" not in st.session_state:
    st.session_state.latest_trace = "Henüz bir sorgu çalıştırılmadı."

# ----------------------------------------------------------------------------------
# SEKME 1: SOHBET ARAYÜZÜ
# ----------------------------------------------------------------------------------
with tab1:
    st.markdown("#### 💡 Örnek Sorular:")
    col_ex1, col_ex2, col_ex3 = st.columns(3)
    
    prompt_to_submit = None
    if col_ex1.button("🕌 İstanbul Namaz Vakitleri"):
        prompt_to_submit = "İstanbul için namaz vakitleri nelerdir?"
    if col_ex2.button("✍️ Soruyu Kaydet (Sehiv Secdesi)"):
        prompt_to_submit = "Bu fıkhi soruyu kaydet: Sehiv secdesi hangi durumlarda vacip olur?"
    if col_ex3.button("📋 Veritabanındaki Soruları Listele"):
        prompt_to_submit = "Veritabanındaki kayıtlı geçmiş soruları listele."

    # Kullanıcı sohbet geçmişini ekrana basma
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Kullanıcı girdisi (chat input veya örnek buton)
    user_input = st.chat_input("Mesajınızı yazın (ör: 'Ankara ezan vakitleri' veya 'Sehiv hakkında arama yap')...")
    
    if prompt_to_submit:
        user_input = prompt_to_submit

    if user_input:
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Ajanı çalıştır
        with st.spinner("Asistan ve dış araçlar çalışıyor..."):
            final_answer, trace_logs, jinja_prompt = agent.run(user_input)

        # Asistan cevabını ekle
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        with st.chat_message("assistant"):
            st.markdown(final_answer)

        # Trace logları güncelle
        logs_text = f"=== ÖDEV 1: CUSTOM JINJA2 CHAT TEMPLATE ÇIKTISI ===\n{jinja_prompt}\n\n"
        logs_text += f"=== ÖDEV 2: TOOL CALLING TRACE LOGS ===\n"
        if trace_logs:
            for log in trace_logs:
                logs_text += f"[Turn {log['turn']}]\n• Tool: {log['tool_name']}\n• Args: {log['arguments']}\n• Response: {log['response']}\n\n"
        else:
            logs_text += "Doğrudan Asistan Yanıtı (Araç çağrılmadı).\n"
        
        st.session_state.latest_trace = logs_text

# ----------------------------------------------------------------------------------
# SEKME 2: TRACE LOGLARI
# ----------------------------------------------------------------------------------
with tab2:
    st.subheader("🔍 Arka Plan Adımları (Custom Jinja2 Chat Template & Tool Calls)")
    st.code(st.session_state.latest_trace, language="yaml")

# ----------------------------------------------------------------------------------
# SEKME 3: VERİTABANI GÖRÜNTÜLEYİCİ
# ----------------------------------------------------------------------------------
with tab3:
    st.subheader("📋 SQLite Veritabanı Kayıtları (`user_inquiries`)")
    
    search_query = st.text_input("Veritabanında kelime arama (ör: sehiv, namaz, oruç):")
    if search_query:
        res = search_inquiries(search_query)
        st.success(f"'{search_query}' İçin Arama Sonuçları ({res.get('match_count', 0)} Eşleşme)")
        records = res.get("records", [])
    else:
        res = get_all_inquiries()
        st.info(f"Toplam Kayıt Sayısı: {res.get('total_count', 0)}")
        records = res.get("records", [])

    if records:
        st.dataframe(records, use_container_width=True)
    else:
        st.warning("Veritabanında kayıt bulunamadı.")
