"""
app.py - Gradio Canlı Arayüzü ve Hugging Face Spaces Başlatıcı
Bu modül; Gradio ile kullanıcı sohbet arayüzünü, Tool Call & Jinja2 Trace Loglarını 
ve SQLite Veritabanı görüntüleyicisini canlıya alır.
"""

import gradio as gr
from agent import IslamicToolCallingAgent
from database import get_all_inquiries

# Ajan Motorumuzu Başlatıyoruz
agent = IslamicToolCallingAgent()

def process_query(user_message, history):
    """Kullanıcı mesajını işler ve Gradio bileşenlerini günceller."""
    if not user_message or user_message.strip() == "":
        return "", history, "Lütfen geçerli bir soru giriniz.", get_database_records_text()
    
    # Agent motorunu çalıştırıyoruz
    final_answer, trace_logs, jinja_prompt_output = agent.run(user_message)
    
    # Trace log ve Jinja2 şablon çıktısını formatlama
    logs_formatted = f"=== 📜 JINJA2 CHAT TEMPLATE INPUT/OUTPUT ===\n{jinja_prompt_output}\n\n"
    logs_formatted += f"=== ⚙️ TOOL CALLING & INTENT TRACE LOGS ===\n"
    
    if trace_logs:
        for log in trace_logs:
            logs_formatted += (
                f"[Turn {log['turn']}] {log['action']}\n"
                f"• Çağrılan Araç: {log['tool_name']}\n"
                f"• Parametreler: {log['arguments']}\n"
                f"• Dönen Yanıt: {log['response']}\n\n"
            )
    else:
        logs_formatted += "Harici bir araç çağrılmadı (Doğrudan Asistan Yanıtı).\n"

    # Chatbot geçmişini güncelleme
    new_history = history + [(user_message, final_answer)]
    
    return "", new_history, logs_formatted, get_database_records_text()

def get_database_records_text():
    """Veritabanındaki tüm kayıtları formatlı metin olarak döner."""
    res = get_all_inquiries()
    records = res.get("records", [])
    if not records:
        return "Veritabanında henüz kayıtlı soru bulunmamaktadır."
    
    output = f"📊 Toplam Veritabanı Kayıt Sayısı: {res['total_count']}\n" + "="*60 + "\n"
    for r in records:
        output += f"ID #{r['id']} | Konu: {r['topic']} | Ekleyen: {r['user_name']} ({r['created_at']})\nSoru: {r['question']}\n" + "-"*60 + "\n"
    return output

# Gradio Özel Tasarım Sistemi
custom_css = """
.main-header { text-align: center; color: #1e3a8a; margin-bottom: 20px; }
.trace-log-box textarea { font-family: monospace; font-size: 13px; background-color: #0f172a; color: #38bdf8; }
.db-box textarea { font-family: monospace; font-size: 13px; background-color: #f8fafc; color: #0f172a; }
"""

with gr.Blocks(title="Namaz Vakti ve Fıkıh Asistanı", css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🕌 Namaz Vakti ve Fıkıh Asistanı (Magibu Yapay Zekâ Mimarisi)
        *Public API Entegrasyonu (Aladhan API), SQLite Veritabanı Okuma/Yazma, Custom Jinja2 Chat Template ve Kesintisiz Soru Yanıt Motoru*
        """
    )

    with gr.Tabs():
        # SEKME 1: Sohbet Arayüzü (Tüm Sorulara Yanıt Verir!)
        with gr.TabItem("💬 Sohbet Arayüzü"):
            chatbot = gr.Chatbot(label="Asistan Söyleşisi", height=480)
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Soru sorun (ör: 'Sehiv secdesi ne zaman yapılır?', 'İstanbul namaz vakitleri', 'Bu soruyu kaydet: Teheccüd kaç rekat kılınır?')",
                    label="Mesajınız",
                    lines=2,
                    scale=8
                )
                submit_btn = gr.Button("Gönder 🚀", variant="primary", scale=2)

            gr.Examples(
                examples=[
                    ["Sehiv secdesi ne zaman vacip olur ve nasıl yapılır?"],
                    ["İstanbul için bugünkü namaz vakitleri nelerdir?"],
                    ["Abdesti bozan durumlar nelerdir?"],
                    ["Bu fıkhi soruyu kaydet: Kaza namazı niyeti nasıl yapılır?"],
                    ["Veritabanındaki kayıtlı tüm soruları listele."]
                ],
                inputs=msg_input
            )

        # SEKME 2: Tool Calling & Jinja2 Trace Logları (Ödev Kontrol Alanı)
        with gr.TabItem("⚙️ Tool Call & Jinja2 Trace Logları"):
            gr.Markdown("### 🔍 Arka Plan Adımları (Tool Calling & Jinja2 Template Input/Output)")
            trace_output = gr.Textbox(
                label="Trace Logs ve Şablon Çıktısı",
                interactive=False,
                lines=20,
                elem_classes=["trace-log-box"]
            )

        # SEKME 3: Veritabanı Görüntüleyici
        with gr.TabItem("🗄️ SQLite Veritabanı Kayıtları"):
            gr.Markdown("### 📋 Veritabanında (user_inquiries) Saklanan Soru ve Fetva Kayıtları")
            db_output = gr.Textbox(
                label="Veritabanı İçeriği",
                value=get_database_records_text(),
                interactive=False,
                lines=16,
                elem_classes=["db-box"]
            )
            refresh_db_btn = gr.Button("Veritabanını Yenile 🔄", variant="secondary")

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
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)