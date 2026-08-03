"""
====================================================================================
ÖDEV 2: GRADIO WEB ARAYÜZÜ (APP.PY) - HUGGING FACE SPACES UYUMLU
====================================================================================
Bu dosya, projemizi Hugging Face Spaces üzerinde ve yerel ortamda canlı test 
edilebilir bir web uygulamasına dönüştürür.

Hugging Face Space Kısıtlamaları & Maliyetsiz İstemci (Client-Side) Çözümü:
- Hugging Face Spaces ücretsiz CPU sunucularında GPU bulunmaz veya kotası sınırlıdır.
- Projemiz Aladhan Public API ve yerel SQLite kullandığı için %100 ÜCRETSİZ ve SUNUCU 
  MALİYETİ OLMAZSIZIN (Zero-Cost Client Architecture) çalışır.
- Ayrıca arayüze kullanıcıların kendi Hugging Face API Token'larını (hf_...) girip 
  canlı LLM inference testi yapabilecekleri istemci ayarları sekmesi eklenmiştir.
====================================================================================
"""

import gradio as gr
from agent import IslamicToolCallingAgent
from database import get_all_inquiries, search_inquiries

# Ajan Motorumuzu Başlatıyoruz
agent = IslamicToolCallingAgent()

def process_query(user_message, history, hf_token_input):
    """
    Kullanıcı mesajını alır, ajanı çalıştırır ve hem sohbet cevabını 
    hem de ödev tesliminde gereken Trace Loglarını üretir.
    Gradio 5+ ve 6 ile tam uyumlu 'messages' (dict listesi) yapısını kullanır.
    """
    if history is None:
        history = []

    if not user_message or not user_message.strip():
        return "", history, "Lütfen geçerli bir soru veya komut girin.", get_database_records_text()

    # Ajanı çalıştırıyoruz: final cevabı, araç çağrı izini ve Jinja2 promptunu alıyoruz
    final_answer, trace_logs, jinja_prompt = agent.run(user_message, hf_token=hf_token_input)

    # -----------------------------------------------------------------------------
    # TRACE LOG VE JINJA2 ŞABLON FORMATLAMA (ÖDEV TESLİM KONTROL ALANI)
    # -----------------------------------------------------------------------------
    logs_formatted = f"=== ÖDEV 1: CUSTOM JINJA2 CHAT TEMPLATE ÇIKTISI ===\n"
    logs_formatted += f"{jinja_prompt}\n\n"
    logs_formatted += f"=== ÖDEV 2: TOOL CALLING TRACE LOGS (ADIM ADIM ÇALIŞTIRMA İZİ) ===\n"
    
    if trace_logs:
        for log in trace_logs:
            logs_formatted += (
                f"[Döngü Adımı / Turn {log['turn']}]\n"
                f"• Çağrılan Fonksiyon / Tool: {log['tool_name']}\n"
                f"• Gönderilen Argümanlar: {log['arguments']}\n"
                f"• Araçtan Dönen Gerçek Veri (Status): {log['response'].get('status')}\n"
                f"• Yanıt İçeriği: {log['response']}\n\n"
            )
    else:
        logs_formatted += "Harici bir araç çağrılmadı (Doğrudan Asistan Yanıtı).\n"

    # Gradio 5/6 Uyumlu Messages Formatında Chatbot Geçmişini Güncelleme
    new_history = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": final_answer}
    ]
    
    return "", new_history, logs_formatted, get_database_records_text()

def get_database_records_text():
    """SQLite veritabanındaki tüm soru ve fetva kayıtlarını çekip metin kutusunda formatlar."""
    res = get_all_inquiries()
    records = res.get("records", [])
    if not records:
        return "Veritabanında henüz kayıtlı soru bulunmamaktadır."
    
    output = f"📊 Veritabanındaki Toplam Kayıt Sayısı: {res['total_count']}\n" + "="*60 + "\n"
    for r in records:
        output += f"ID #{r['id']} | Konu: {r['topic']} | Ekleyen: {r['user_name']} ({r['created_at']})\nSoru: {r['question']}\n" + "-"*60 + "\n"
    return output

def search_database_records(keyword):
    """Veritabanında kelimeye göre arama yapıp sonucu formatlar."""
    if not keyword or not keyword.strip():
        return get_database_records_text()
    
    res = search_inquiries(keyword.strip())
    records = res.get("records", [])
    if not records:
        return f"🔍 '{keyword}' kelimesiyle eşleşen kayıt bulunamadı."
        
    output = f"🔍 '{keyword}' İçin Arama Sonuçları ({res['match_count']} Eşleşme):\n" + "="*60 + "\n"
    for r in records:
        output += f"ID #{r['id']} | Konu: {r['topic']} | Ekleyen: {r['user_name']} ({r['created_at']})\nSoru: {r['question']}\n" + "-"*60 + "\n"
    return output

# ----------------------------------------------------------------------------------
# GRADIO TASARIMI VE TEMA AYARLARI
# ----------------------------------------------------------------------------------
custom_css = """
.main-header { text-align: center; color: #1e3a8a; margin-bottom: 15px; }
.trace-log-box textarea { font-family: monospace; font-size: 13px; background-color: #0f172a; color: #38bdf8; }
.db-box textarea { font-family: monospace; font-size: 13px; background-color: #f8fafc; }
"""

with gr.Blocks(title="Namaz Vakti & Fıkıh Asistanı") as demo:
    gr.Markdown(
        """
        # 🕌 Namaz Vakti ve Fıkıh Asistanı (Magibu Yapay Zekâ Mimarisi)
        *Public API Entegrasyonu (Aladhan API), SQLite Veritabanı Okuma/Yazma, Custom Jinja2 Chat Template ve Kesintisiz Soru Yanıt Motoru*
        """
    )

    # İstemci Tarafı Token Bilgisi (Zero-Cost / Maliyetsiz İstemci Modu)
    with gr.Accordion("🔑 Hugging Face Token & İstemci Ayarları (Opsiyonel / Ücretsiz Test)", open=False):
        gr.Markdown(
            """
            > **Maliyetsiz İstemci Mimarisi (Client-Side Testing)**:
            > Hugging Face Space üzerinde sunucu kısıtlamalarına takılmamak ve %100 ücretsiz çalışmak için sistem varsayılan olarak 
            > **Aladhan REST API** ve yerel **SQLite veritabanı** motorunu kullanır. 
            > Kendi Hugging Face API Token'ınızı (`hf_...`) aşağıya ekleyerek dış LLM modellerini de test edebilirsiniz.
            """
        )
        hf_token_input = gr.Textbox(
            label="Hugging Face API Token (Opsiyonel)",
            placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            type="password"
        )

    with gr.Tabs():
        # -----------------------------------------------------------------------------
        # SEKME 1: Sohbet Arayüzü
        # -----------------------------------------------------------------------------
        with gr.TabItem("💬 Sohbet Arayüzü"):
            chatbot = gr.Chatbot(label="Asistan Söyleşisi", height=420)
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Örnek: 'İstanbul namaz vakitleri' veya 'Bu soruyu kaydet: Sehiv secdesi ne zaman yapılır?'",
                    label="Mesajınız",
                    lines=2,
                    scale=8
                )
                submit_btn = gr.Button("Gönder 🚀", variant="primary", scale=2)

            gr.Examples(
                examples=[
                    ["İstanbul için namaz vakitleri nelerdir?"],
                    ["Ankara imsak ve akşam ezanı kaçta okunuyor?"],
                    ["Bu fıkhi soruyu kaydet: Sehiv secdesi hangi durumlarda vacip olur?"],
                    ["Veritabanında sehiv hakkındaki kayıtları ara."],
                    ["Veritabanındaki kayıtlı geçmiş soruları listele."]
                ],
                inputs=msg_input
            )

        # -----------------------------------------------------------------------------
        # SEKME 2: Tool Calling & Jinja2 Trace Logları (Ödev Kontrol Alanı)
        # -----------------------------------------------------------------------------
        with gr.TabItem("⚙️ Tool Call & Jinja2 Trace Logları"):
            gr.Markdown("### 🔍 Arka Plan Adımları (Custom Jinja2 Chat Template ve Tool Call İzleri)")
            trace_output = gr.Textbox(
                label="Şablon Çıktısı ve Çalıştırma İzleri (Trace Logs)",
                interactive=False,
                lines=20,
                elem_classes=["trace-log-box"]
            )

        # -----------------------------------------------------------------------------
        # SEKME 3: Veritabanı Görüntüleyici ve Arama
        # -----------------------------------------------------------------------------
        with gr.TabItem("🗄️ SQLite Veritabanı Kayıtları"):
            gr.Markdown("### 📋 Veritabanında (`user_inquiries`) Saklanan Soru ve Fetva Kayıtları")
            with gr.Row():
                db_search_input = gr.Textbox(
                    placeholder="Veritabanında aranacak kelime (ör: sehiv, namaz, oruç)",
                    label="Kelime Arama",
                    scale=7
                )
                db_search_btn = gr.Button("Ara 🔍", variant="secondary", scale=2)
                refresh_db_btn = gr.Button("Yenile 🔄", variant="primary", scale=2)
                
            db_output = gr.Textbox(
                label="Veritabanı İçeriği",
                value=get_database_records_text(),
                interactive=False,
                lines=16,
                elem_classes=["db-box"]
            )

    # -----------------------------------------------------------------------------
    # EVENT BAĞLANTILARI (EVENTS)
    # -----------------------------------------------------------------------------
    submit_btn.click(
        fn=process_query,
        inputs=[msg_input, chatbot, hf_token_input],
        outputs=[msg_input, chatbot, trace_output, db_output]
    )
    
    msg_input.submit(
        fn=process_query,
        inputs=[msg_input, chatbot, hf_token_input],
        outputs=[msg_input, chatbot, trace_output, db_output]
    )

    refresh_db_btn.click(
        fn=get_database_records_text,
        inputs=[],
        outputs=[db_output]
    )
    
    db_search_btn.click(
        fn=search_database_records,
        inputs=[db_search_input],
        outputs=[db_output]
    )

if __name__ == "__main__":
    # Hugging Face Space ve Yerel Sunucu İçin Port Ayarı
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)