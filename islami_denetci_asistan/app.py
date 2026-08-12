"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN - GRADIO WEB KULLANICI ARAYÜZÜ (APP.PY)
==============================================================================
BU MODÜL NEYİ SAĞLAR? (EĞİTİCİ AÇIKLAMA):
------------------------------------------------------------------------------
1. Gradio Web UI (Web Kullanıcı Arayüzü):
   Kullanıcıların web tarayıcısı üzerinden (http://localhost:7860) asistanla
   etkileşime girmesini sağlayan görsel kullanıcı arayüzüdür.

2. 3 Sekmeli Profesyonel Görsel Düzen:
   - Sekme 1: Canlı Sohbet ve Bot (Chatbot Interface)
   - Sekme 2: Araç Çağrı Logları & Şeffaf Trace İzleyici (Trace Logs Inspector)
   - Sekme 3: SQLite Veritabanı Kayıt İnceleyici (Database Inspector Table)
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
    Kullanıcı mesajını alır, Agent Engine'i çalıştırır ve yanıtı web sohbetine ekler.
    """
    if not user_message.strip():
        return "", chat_history, "Henüz araç çağrılmadı."

    # Agent Engine çalıştırma
    bot_response, trace_logs, _ = engine.run(user_message)
    
    # Sohbet geçmişini güncelle (Gradio chatbot formatı)
    chat_history.append((user_message, bot_response))
    
    # Log ekranı metnini hazırlama
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
with gr.Blocks(title="🕌 İslami Denetçi Asistanı", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🕌 İslami Uygulama Doğruluk ve Kaynak Denetçisi
        ### Local LLM + Tool Calling + Vector RAG + SQLite DB + DuckDuckGo Web Search
        """
    )
    
    with gr.Tabs():
        # Sekme 1: Canlı Sohbet Arayüzü
        with gr.TabItem("💬 Canlı Sohbet"):
            chatbot = gr.Chatbot(height=450, label="İslami Denetçi Asistanı Sohbeti")
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
    # Gradio Web Sunucusunu 7860 portunda başlat
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
