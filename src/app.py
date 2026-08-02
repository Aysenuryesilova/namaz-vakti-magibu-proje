"""
app.py - Gradio Web Arayüzü (ChatInterface Kararlı Sürüm)
"""

import gradio as gr
from agent import IslamicToolCallingAgent

# Ajan sınıfımızı başlatıyoruz
agent = IslamicToolCallingAgent()

def model_response(user_message, history):
    """Kullanıcı mesajını alır, ajanı çalıştırır ve doğrudan metin yanıtı döner."""
    if not user_message.strip():
        return "Lütfen bir soru yazın."
    
    # Ajanı çalıştırıp yanıt ve trace logları alıyoruz
    final_answer, trace_logs, jinja_prompt = agent.run(user_message)
    
    # Trace logları ve Jinja2 promptunu birleştirip şık bir format oluşturuyoruz
    logs_formatted = f"=== JINJA2 ŞABLON ÇIKTISI ===\n{jinja_prompt}\n\n=== TOOL CALLING TRACE LOGS ===\n"
    for log in trace_logs:
        logs_formatted += f"Turn {log['turn']}: Araç -> {log['tool_name']}\nGirdi -> {log['arguments']}\nYanıt -> {log['response']}\n\n"
    
    # Gradio ChatInterface için yanıtı ve arka plan loglarını konsola veya ekrana basabiliriz.
    # Burada kullanıcıya hem asistan yanıtını hem de alt kısımda ödev modunu sunuyoruz.
    return f"{final_answer}\n\n---\n\n🔍 **Ödev Modu (Trace & Jinja2 Logları):**\n```text\n{logs_formatted}\n```"

# Gradio'nun en kararlı arayüz bileşeni (ChatInterface) ile hata ihtimalini sıfırlıyoruz
demo = gr.ChatInterface(
    fn=model_response,
    title="🕌 Dini İlimler & Tool-Calling Asistanı",
    description="Bu proje; Jinja2 Chat Template, SQLite Veritabanı (Veri Okuma/Yazma) ve Aladhan API entegrasyonuyla geliştirilmiştir.",
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)