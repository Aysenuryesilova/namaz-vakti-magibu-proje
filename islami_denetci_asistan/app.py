"""
==============================================================================
İSLÂMİ UYGULAMA DOĞRULUK DENETÇİSİ GRADIO WEB ARAYÜZÜ (APP.PY)
==============================================================================
Bu dosya:
Hugging Face Spaces ve Yerel Kullanım için 3 Sekmeli Modern Gradio Arayüzü sunar.
- Sekme 1: Sohbet Arayüzü ve Örnek Hızlı Sorular
- Sekme 2: Tool Calling & Jinja2 Trace Logları (Ödev Kontrolü İçin)
- Sekme 3: SQLite Veritabanı ve RAG Bilgi Bankası Görüntüleyici
"""

import gradio as gr
from agent_engine import IslamicAgentEngine
from database import get_all_inquiries

engine = IslamicAgentEngine()

def get_db_records_formatted() -> str:
    """Veritabanındaki soru ve fetva kayıtlarını metin olarak döndürür."""
    res = get_all_inquiries()
    if res.get("status") == "success":
        records = res.get("records", [])
        if not records:
            return "📋 Veritabanında (user_inquiries) henüz kayıtlı bir soru bulunmamaktadır."
        
        lines = []
        for r in records:
            lines.append(f"• ID #{r['id']} | Konu: [{r['topic']}] | Kişi: {r['user_name']} ({r['created_at']})\n  Soru: {r['question']}\n")
        return f"📋 SQLite Veritabanında Saklanan Sorular (Toplam: {len(records)} Kayıt):\n\n" + "\n".join(lines)
    return "⚠️ Veritabanı okuma hatası oluştu."

def process_query(user_message, history):
    """Kullanıcı mesajını işler, sohbet cevabını, trace loglarını ve DB durumunu döndürür."""
    if not user_message or not user_message.strip():
        return "", history, "Lütfen geçerli bir soru girin.", get_db_records_formatted()

    final_answer, trace_logs, rendered_prompt = engine.run(user_message)

    # Trace Log Formatlama
    logs_formatted = f"=== JINJA2 / SYSTEM PROMPT ÇIKTISI ===\n{rendered_prompt}\n\n"
    logs_formatted += f"=== TOOL CALLING TRACE LOGS (Ödev Adımları) ===\n"

    if trace_logs:
        for log in trace_logs:
            logs_formatted += (
                f"[Turn {log['turn']}]\n"
                f"• Çağrılan Araç : {log['tool_name']}\n"
                f"• Parametreler   : {log['arguments']}\n"
                f"• Yanıt/Sonuç    : {log['response']}\n\n"
            )
    else:
        logs_formatted += "Bu sorgu için doğrudan yanıt üretilmiştir (Harici araç tetiklenmedi).\n"

    new_history = history + [(user_message, final_answer)]
    return "", new_history, logs_formatted, get_db_records_formatted()

# Gradio Arayüzü Tasarımı
custom_css = """
footer {visibility: hidden;}
.trace-box textarea {font-family: monospace; font-size: 13px; background-color: #1e1e2e; color: #a6e3a1;}
"""

with gr.Blocks(title="🕌 İslami Denetçi & Namaz Vakti Asistanı", css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🕌 İslami Uygulama Doğruluk & Kaynak Denetçisi (Ezan Vakti Agent)
        ### Yerel (Local) LLM + Tool Calling (Araç Kullanımı) + RAG + SQLite Veritabanı + Canlı Web Araması
        *Diyanet namaz vakitleri, zekat hesabı, Kur'an mealleri, hadisler, fıkıh rehberi ve canlı internet araştırması*
        """
    )

    with gr.Tabs():
        # SEKME 1: SOHBET
        with gr.TabItem("💬 İslami Denetçi Sohbet Arayüzü"):
            chatbot = gr.Chatbot(height=450, show_copy_button=True)
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Sorunuzu buraya yazın (Örn: 'İstanbul namaz vakitleri', '100 gr altın 50 bin TL zekat hesabı')...",
                    show_label=False,
                    scale=8
                )
                submit_btn = gr.Button("Gönder 🚀", variant="primary", scale=2)

            gr.Markdown("### 💡 Örnek Hızlı Test Soruları")
            gr.Examples(
                examples=[
                    ["İstanbul için bugün namaz vakitleri nelerdir?"],
                    ["100 gram altınım ve 50.000 TL nakdim var, zekat düşer mi?"],
                    ["Teheccüd namazı ne zaman ve nasıl kılınır?"],
                    ["Bu soruyu veritabanına kaydet: Sehiv secdesi hangi durumlarda vacip olur?"],
                    ["Veritabanındaki tüm kayıtlı soruları listele."],
                    ["2026 Diyanet Ramazan ne zaman başlıyor?"],
                    ["Ankara için kıble açısı kaç derecedir?"],
                    ["'Allah' isminin Esmaül Hüsna anlamı nedir?"],
                ],
                inputs=msg_input
            )

        # SEKME 2: TRACE LOGLARI
        with gr.TabItem("⚙️ Tool Call & Jinja2 Trace Logları"):
            gr.Markdown("### 🔍 Arka Plan Çalışma Adımları (Tool Calling & System Prompt Output)")
            trace_output = gr.Textbox(
                label="Trace Logları ve Araç Parametreleri",
                interactive=False,
                lines=20,
                elem_classes=["trace-box"]
            )

        # SEKME 3: VERİTABANI GÖRÜNTÜLEYİCİ
        with gr.TabItem("🗄️ SQLite Veritabanı & RAG Kayıtları"):
            gr.Markdown("### 📋 Veritabanında (user_inquiries) Saklanan Soru ve Fetva Kayıtları")
            db_output = gr.Textbox(
                label="Veritabanı İçeriği",
                value=get_db_records_formatted(),
                interactive=False,
                lines=15
            )
            refresh_btn = gr.Button("Veritabanını Yenile 🔄")

    # Event İşleyiciler
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

    refresh_btn.click(
        fn=get_db_records_formatted,
        inputs=[],
        outputs=[db_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
