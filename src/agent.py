"""
agent.py - Tool Calling ve Jinja2 Entegrasyonlu Ajan Motoru
Bu modül; kullanıcının sorgularını analiz eder, uygun aracı (Aladhan API veya SQLite) 
tetikler ve Jinja2 şablonunu kullanarak model bağlamını hazırlar.
"""

import os
from jinja2 import Template
from database import init_database
from tools import AVAILABLE_TOOLS, TOOLS_SCHEMA

class IslamicToolCallingAgent:
    def __init__(self):
        # Veritabanı tablolarının ve başlangıç verilerinin hazır olduğundan emin oluyoruz
        init_database()
        
        # Jinja2 şablonumuzu src klasörünün içinden yüklüyoruz
        template_path = os.path.join(os.path.dirname(__file__), "chat_template.jinja")
        with open(template_path, "r", encoding="utf-8") as f:
            self.template_content = f.read()
            
    def render_chat_prompt(self, messages: list) -> str:
        """Jinja2 şablonunu kullanarak mesaj geçmişini modelin anlayacağı formata dönüştürür."""
        template = Template(self.template_content)
        return template.render(messages=messages, add_generation_prompt=True)

    def run(self, user_query: str) -> tuple:
        """
        Kullanıcı sorgusunu işler, niyet analizi yapar, uygun aracı çağırır 
        ve hem nihai yanıtı hem de ödev için gereken trace logları döndürür.
        """
        query_lower = user_query.lower()
        trace_logs = []
        messages = [
            {"role": "system", "content": "Sen yetkin bir Dini İlimler ve Fetva Takip Asistanısın. Veritabanı ve API araçlarını kullanarak doğru yanıtlar üretirsin."},
            {"role": "user", "content": user_query}
        ]

        # 1. Jinja2 şablon testi ve prompt oluşturma
        formatted_prompt = self.render_chat_prompt(messages)

        tool_to_call = None
        tool_args = {}
        tool_result = None

        # 2. Niyet Analizi (Intent Recognition) ve Tool Seçimi
        if "ezan" in query_lower or "vakit" in query_lower:
            tool_to_call = "get_prayer_times"
            # Basit bir şehir çıkarma mantığı (Örn: Ankara ezan -> Ankara)
            words = user_query.split()
            city = "Ankara" # Varsayılan
            for w in words:
                if w.lower() not in ["ezan", "vakit", "nedir", "ne", "saat"]:
                    city = w.capitalize()
                    break
            tool_args = {"city": city}

        elif "kaydet" in query_lower or "soru sor" in query_lower or "fetva" in query_lower:
            tool_to_call = "create_user_inquiry"
            tool_args = {"topic": "Genel Fıkıh", "question": user_query}

        elif "liste" in query_lower or "gecmis" in query_lower or "sorularim" in query_lower:
            tool_to_call = "list_user_inquiries"
            tool_args = {}

        # 3. Aracı (Tool) Çalıştırma
        if tool_to_call:
            tool_function = AVAILABLE_TOOLS[tool_to_call]
            tool_result = tool_function(**tool_args)

            # Trace log kaydı (Ödev şartı olan arka plan izleme ekranı için)
            trace_logs.append({
                "turn": 1,
                "tool_name": tool_to_call,
                "arguments": tool_args,
                "response": tool_result
            })

        # 4. Yanıtı Sentezleme
        if tool_result and tool_result.get("status") == "success":
            if tool_to_call == "get_prayer_times":
                t = tool_result["prayer_times"]
                final_answer = (
                    f"📍 **{tool_result['city']} İçin Namaz Vakitleri:**\n"
                    f"• İmsak: {t['Imsak']}\n"
                    f"• Güneş: {t['Gunes']}\n"
                    f"• Öğle: {t['Ogle']}\n"
                    f"• İkindi: {t['Ikindi']}\n"
                    f"• Akşam: {t['Aksam']}\n"
                    f"• Yatsı: {t['Yatsi']}\n"
                    f"*(Kaynak: {tool_result['source']})*"
                )
            elif tool_to_call == "create_user_inquiry":
                final_answer = (
                    f"✅ **Kayıt İşlemi Başarılı (Veri Yazma):**\n"
                    f"{tool_result['message']}\n"
                    f"Konu: {tool_result['topic']}\n"
                    f"Soru: {tool_result['question']}"
                )
            elif tool_to_call == "list_user_inquiries":
                inquiries = tool_result["inquiries"]
                inquiry_list_str = "\n".join([f"- [{item['topic']}] {item['question']} (Durum: {item['status']})" for item in inquiries])
                final_answer = (
                    f"📋 **Veritabanındaki Kayıtlı Sorular (Veri Okuma):**\n"
                    f"Toplam Kayıt: {tool_result['total_records']}\n\n"
                    f"{inquiry_list_str}"
                )
            else:
                final_answer = "İşleminiz başarıyla tamamlandı."
        else:
            final_answer = "Sorunuzu doğrudan veritabanı veya API araçlarımızla eşleştireemedim. Lütfen 'Ankara ezan vakti', 'Kayıtları listele' şeklinde sorunuz."

        return final_answer, trace_logs, formatted_prompt