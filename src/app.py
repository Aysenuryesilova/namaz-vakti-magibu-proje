"""
app.py - Gradio Web Arayüzü (Gradio 6.x Tam Uyumlu Kararlı Sürüm)
"""

import gradio as gr
from agent import IslamicToolCallingAgent
from database import get_all_inquiries

# Ajan motorumuzu başlatıyoruz
agent = IslamicToolCallingAgent()

def process_query(user_message, history):
    """Kullanıcı mesajını alır, ajanı çalıştırır ve sohbet cevabı ile trace loglarını döner."""
    if not user_message or not user_message.strip():
        return "", history or [], "Lütfen geçerli bir soru girin.", get_database_records_text()

    history = history or []

    # Ajanı çalıştırıp yanıt, trace logları ve Jinja2 promptunu alıyoruz
    final_answer, trace_logs, jinja_prompt = agent.run(user_message)

    # Log formatlama
    logs_formatted = f"=== JINJA2 ŞABLON ÇIKTISI (Hafta 3.2 1. Ödev) ===\n{jinja_prompt}\n\n"
    logs_formatted += f"=== TOOL CALLING TRACE LOGS (Hafta 3.1 & 3.2 2. Ödev) ===\n"
    
    if trace_logs:
        for log in trace_logs:
            logs_formatted += (
                f"[Turn {log['turn']}]\n"
                f"• Çağrılan Araç: {log['tool_name']}\n"
                f"• Parametreler: {log['arguments']}\n"
                f"• Yanıt/Sonuç: {log['response']}\n\n"
            )
    else:
        logs_formatted += "Bu sorgu için harici bir araç çağrılmadı (Bilgi Tabanı / Doğrudan Asistan Yanıtı).\n"

    # Gradio 6 uyumlu tuple konuşma geçmişi ekleme
    updated_history = history + [(user_message, final_answer)]
    
    return "", updated_history, logs_formatted, get_database_records_text()

def get_database_records_text():
    """Veritabanındaki kayıtları formatlı bir metin olarak döner."""
    res = get_all_inquiries()
    records = res.get("records", [])
    if not records:
        return "Veritabanında henüz kayıtlı soru bulunmamaktadır."
    
    output = f"📊 Toplam Kayıt Sayısı: {res['total_count']}\n" + "="*50 + "\n"
    for r in records:
        output += f"ID #{r['id']} | Konu: {r['topic']} | Ekleyen: {r['user_name']} ({r['created_at']})\nSoru: {r['question']}\n" + "-"*50 + "\n"
    return output

# Gradio Arayüz Tasarımı
custom_css = """
.main-header { text-align: center; color: #1e3a8a; margin-bottom: 20px; }
.trace-log-box textarea { font-family: monospace; font-size: 13px; background-color: #f8fafc; }
"""

with gr.Blocks(title="Namaz Vakti & Fıkıh Asistanı") as demo:
    gr.Markdown(
        """
        # 🕌 Namaz Vakti ve Fıkıh Asistanı (Magibu Yapay Zekâ Mimarisi)
        *Public API Entegrasyonu (Aladhan API), SQLite Veritabanı Okuma/Yazma, Custom Jinja2 Chat Template ve Tool Calling Trace Logları*
        """
    )

    with gr.Tabs():
        # SEKME 1: Sohbet Arayüzü
        with gr.TabItem("💬 Sohbet Arayüzü"):
            chatbot = gr.Chatbot(label="Asistan Söyleşisi", height=450)
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Örnek: 'İstanbul için namaz vakitleri nelerdir?' veya 'Sehiv secdesi ne zaman yapılır?' veya 'Bu soruyu kaydet: Orucu ne bozar?'",
                    label="Mesajınız",
                    lines=2,
                    scale=8
                )
                submit_btn = gr.Button("Gönder 🚀", variant="primary", scale=2)

            gr.Examples(
                examples=[
                    ["İstanbul için namaz vakitleri nelerdir?"],
                    ["Sehiv secdesi ne zaman yapılır?"],
                    ["Abdestin farzları nelerdir?"],
                    ["Bu fıkhi soruyu kaydet: Sehiv secdesi hangi durumlarda vacip olur?"],
                    ["Veritabanındaki kayıtlı geçmiş soruları listele."]
                ],
                inputs=msg_input
            )

        # SEKME 2: Tool Calling & Jinja2 Trace Logları (Ödev Teslim Kontrolü İçin)
        with gr.TabItem("⚙️ Tool Call & Jinja2 Trace Logları"):
            gr.Markdown("### 🔍 Arka Plan Adımları (Tool Calling & Jinja2 Template Output)")
            trace_output = gr.Textbox(
                label="Trace Logs ve Şablon Çıktısı",
                interactive=False,
                lines=18,
                elem_classes=["trace-log-box"]
            )

        # SEKME 3: Veritabanı Görüntüleyici
        with gr.TabItem("🗄️ SQLite Veritabanı Kayıtları"):
            gr.Markdown("### 📋 Veritabanında (user_inquiries) Saklanan Soru ve Fetva Kayıtları")
            db_output = gr.Textbox(
                label="Veritabanı İçeriği",
                value=get_database_records_text(),
                interactive=False,
                lines=15
            )
            refresh_db_btn = gr.Button("Veritabanını Yenile 🔄")

    # Event Bağlantıları
    submit_btn.click(
        fn=process_query,
        inputs=[msg_input, chatbot],
        outputs=[msg_input, chatbot, trace_output, db_output]
    )
    
    msg_input.submit(
        fn=process_query,
        inputs=[msg_input, chatbot],
        outputs=[msg_input, chatbot, trace_output, db_output]
    )

    refresh_db_btn.click(
        fn=get_database_records_text,
        inputs=[],
        outputs=[db_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, css=custom_css, theme=gr.themes.Soft())