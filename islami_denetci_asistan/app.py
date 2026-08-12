"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN - GRADIO WEB KULLANICI ARAYÜZÜ (APP.PY)
==============================================================================
BU MODÜL NEYİ SAĞLAR? (EĞİTİCİ VE TEKNİK DÜZELTME):
------------------------------------------------------------------------------
1. Gradio 5 / 6 Chatbot Sözlük Biçimi (Messages Format Compatibility):
   Yeni Gradio sürümlerindeki (Gradio 5/6) Chatbot bileşeni tuple [("user", "bot")]
   yerine `{"role": "user", "content": "..."}` dict formatı bekler. Bu nedenle
   sohbet geçmişi evrensel 'role/content' formatına güncellenmiştir.

2. Windows Uyumlu Sunucu Adresi (127.0.0.1):
   Chrome/Edge tarayıcılarında 'ERR_ADDRESS_INVALID' hatasını önlemek için
   sunucu adresi '127.0.0.1' (localhost) olarak çalışır.
==============================================================================
"""

import sys
import gradio as gr
from agent_engine import IslamicAgentEngine
from database import get_all_inquiries

# Agent motoru tekil örneği
engine = IslamicAgentEngine()

def respond(user_message, chat_history):
    """
    Gradio Sohbet Fonksiyonu:
    Kullanıcı mesajını alır, Agent Engine'i çalıştırır ve yanıtı 'messages' biçiminde ekler.
    """
    if not chat_history:
        chat_history = []

    if not user_message or not user_message.strip():
        return "", chat_history, "Henüz araç çağrılmadı."

    # Agent Engine çalıştırma
    bot_response, trace_logs, _ = engine.run(user_message)
    
    # Evrensel Gradio 'role' / 'content' mesaj formatına ekleme
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": bot_response})
    
    # Trace log formatlama
    logs_str = ""
    for log in trace_logs:
        logs_str += f"🔧 Tur #{log['turn']}: Araç '{log['tool_name']}' Çalıştırıldı\n"
        logs_str += f"   • Parametreler: {log['arguments']}\n"
        logs_str += f"   • Yanıt Çıktısı: {str(log['response'])[:200]}...\n\n"
        
    if not logs_str:
        logs_str = "ℹ️ Bu yanıt doğrudan bilgi bankasından veya NLU motorundan üretildi."

    return "", chat_history, logs_str

def refresh_db():
    """SQLite veritabanı kayıtlarını okuyup tablo halinde döndürür."""
    res = get_all_inquiries()
    if res.get("status") == "success":
        records = res.get("records", [])
        return [[r["id"], r["topic"], r["user_name"], r["question"], r["created_at"]] for r in records]
    return []

# ==============================================================================
# GRADIO BLOCKS ARAYÜZ TASARIMI
# ==============================================================================
with gr.Blocks(title="🕌 İslami Denetçi Asistanı") as demo:
    gr.Markdown(
        """
        # 🕌 İslami Uygulama Doğruluk ve Kaynak Denetçisi
        ### Local LLM + Tool Calling + Vector RAG + SQLite DB + DuckDuckGo Web Search
        """
    )
    
    with gr.Tabs():
        # Sekme 1: Canlı Sohbet Arayüzü
        with gr.TabItem("💬 Canlı Sohbet"):
            chatbot = gr.Chatbot(
                height=450,
                label="İslami Denetçi Asistanı Sohbeti",
                type="messages"
            )
            with gr.Row():
                msg_input = gr.Textbox(placeholder="Mesajınızı yazın (Örn: 'İzmit ezan vakitleri', '504. ayet nedir?')...", scale=8)
                submit_btn = gr.Button("Gönder", variant="primary", scale=2)
                clear_btn = gr.Button("Temizle", scale=1)
                
            trace_output = gr.Textbox(label="🔍 En Son Araç Çağrı Logu (Trace Log)", lines=5, interactive=False)
            
            # Olay Bağlantıları (Event Bindings)
            msg_input.submit(respond, [msg_input, chatbot], [msg_input, chatbot, trace_output])
            submit_btn.click(respond, [msg_input, chatbot], [msg_input, chatbot, trace_output])
            clear_btn.click(lambda: ([], ""), None, [chatbot, trace_output])

        # Sekme 2: SQLite Veritabanı İnceleyici
        with gr.TabItem("📋 SQLite Veritabanı İnceleyici"):
            gr.Markdown("### SQLite Veritabanındaki Kayıtlı Fetva ve Sorular")
            refresh_btn = gr.Button("Verileri Yenile", variant="secondary")
            db_table = gr.Dataframe(
                headers=["ID", "Konu", "Kullanıcı", "Soru", "Tarih"],
                datatype=["number", "str", "str", "str", "str"],
                value=refresh_db()
            )
            refresh_btn.click(refresh_db, None, db_table)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
