"""
agent.py - Tool Calling ve Jinja2 Entegrasyonlu Ajan Motoru
Bu modül; kullanıcının sorgularını analiz eder, uygun aracı (Aladhan API veya SQLite) 
tetikler ve Jinja2 şablonunu kullanarak model bağlamını hazırlar.
"""

import os
from jinja2 import Template
from database import init_database
from tools import AVAILABLE_TOOLS, TOOLS_SCHEMA, get_prayer_times, save_inquiry_tool, get_all_inquiries_tool

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
        
        Returns:
            tuple: (final_answer: str, trace_logs: list, formatted_jinja_prompt: str)
        """
        query_lower = user_query.lower()
        trace_logs = []
        messages = [
            {
                "role": "system", 
                "content": "Sen yetkin bir Dini İlimler ve Fetva Takip Asistanısın. Veritabanı ve API araçlarını kullanarak halüsinasyon görmeden doğru yanıtlar üretirsin."
            },
            {"role": "user", "content": user_query}
        ]

        # 1. Jinja2 şablonu ile prompt oluşturma (Hafta 3.2 1. Ödev Gereksinimi)
        formatted_prompt = self.render_chat_prompt(messages)

        tool_to_call = None
        tool_args = {}
        tool_result = None
        turn_counter = 1

        # 2. Niyet Analizi (Intent Recognition) ve Tool Seçimi (Hafta 3.1 & 3.2 2. Ödev Gereksinimi)
        
        # Senaryo A: Ezan / Namaz Vakitleri (Public Aladhan API - Read)
        if any(keyword in query_lower for keyword in ["ezan", "namaz vakti", "vakitleri", "imsak", "öğle", "ikindi", "akşam", "yatsı"]):
            # Şehir tespiti
            cities = ["istanbul", "ankara", "izmir", "bursa", "antalya", "adana", "konya", "gaziantep", "şanlıurfa", "kocaeli", "malatya", "erzurum", "trabzon", "diyarbakır", "eskişehir", "kayseri", "samsun"]
            found_city = "Istanbul"
            for city in cities:
                if city in query_lower:
                    found_city = city.title()
                    break
            
            tool_to_call = "get_prayer_times"
            tool_args = {"city": found_city, "country": "Turkey"}
            tool_result = get_prayer_times(city=found_city, country="Turkey")
            
            # Trace log ekleme
            trace_logs.append({
                "turn": turn_counter,
                "tool_name": tool_to_call,
                "arguments": tool_args,
                "response": tool_result
            })
            
            if tool_result.get("status") == "success":
                times = tool_result["prayer_times"]
                final_answer = (
                    f"🕌 **{tool_result['city']} için Namaz Vakitleri** ({tool_result['date']}):\n\n"
                    f"• **İmsak:** {times['İmsak']}\n"
                    f"• **Güneş:** {times['Güneş']}\n"
                    f"• **Öğle:** {times['Öğle']}\n"
                    f"• **İkindi:** {times['İkindi']}\n"
                    f"• **Akşam:** {times['Akşam']}\n"
                    f"• **Yatsı:** {times['Yatsı']}\n\n"
                    f"📌 *Kaynak: {tool_result['source']}*"
                )
            else:
                final_answer = f"⚠️ Namaz vakitleri alınamadı: {tool_result.get('message')}"

        # Senaryo B: Soru/Fetva Kaydetme (SQLite - Write)
        elif any(keyword in query_lower for keyword in ["kaydet", "soru ekle", "fetva kaydet", "kayıt ekle"]):
            topic = "Genel Fıkıh"
            if "namaz" in query_lower: topic = "Namaz"
            elif "oruç" in query_lower: topic = "Oruç"
            elif "zekat" in query_lower: topic = "Zekat"
            elif "abdest" in query_lower: topic = "Abdest"
            
            tool_to_call = "save_inquiry_tool"
            tool_args = {"topic": topic, "question": user_query, "user_name": "Ayşe Nur"}
            tool_result = save_inquiry_tool(topic=topic, question=user_query, user_name="Ayşe Nur")
            
            trace_logs.append({
                "turn": turn_counter,
                "tool_name": tool_to_call,
                "arguments": tool_args,
                "response": tool_result
            })
            
            final_answer = (
                f"✅ **Fetva/Soru Talebiniz Başarıyla Kaydedildi!**\n\n"
                f"• **Kayıt ID:** #{tool_result['record']['id']}\n"
                f"• **Konu:** {tool_result['record']['topic']}\n"
                f"• **Kullanıcı:** {tool_result['record']['user_name']}\n"
                f"• **Tarih:** {tool_result['record']['created_at']}\n"
                f"• **Soru:** {tool_result['record']['question']}\n\n"
                f"📌 *Soru veritabanına eklenmiştir. 'Kayıtları listele' yazarak tüm geçmiş soruları görebilirsiniz.*"
            )

        # Senaryo C: Kayıtlı Soruları Listeleme (SQLite - Read)
        elif any(keyword in query_lower for keyword in ["listele", "kayıtlar", "geçmiş sorular", "tüm sorular", "sorularım"]):
            tool_to_call = "get_all_inquiries_tool"
            tool_args = {}
            tool_result = get_all_inquiries_tool()
            
            trace_logs.append({
                "turn": turn_counter,
                "tool_name": tool_to_call,
                "arguments": tool_args,
                "response": tool_result
            })
            
            records = tool_result.get("records", [])
            if records:
                records_text = "\n".join([
                    f"#{r['id']} | [{r['topic']}] {r['user_name']} ({r['created_at']}): {r['question']}"
                    for r in records
                ])
                final_answer = (
                    f"📋 **Veritabanındaki Kayıtlı Fıkhi Sorular (Toplam: {tool_result['total_count']})**:\n\n"
                    f"{records_text}"
                )
            else:
                final_answer = "📋 Veritabanında henüz kayıtlı bir soru bulunmamaktadır."

        # Senaryo D: Genel Fıkhi Soru (Doğrudan Bilgi Verme)
        else:
            final_answer = (
                f"📖 **Fıkhi Bilgi Asistanı**:\n\n"
                f"Sorgunuz: '{user_query}'\n\n"
                f"Namaz, ibadet kuralları ve fıkhi konular ile ilgili sorularınızı sorabilir, "
                f"şehir bazlı namaz vakitlerini öğrenebilir (ör: 'İstanbul namaz vakitleri') "
                f"veya sorunuzu veritabanına kaydedebilirsiniz (ör: 'Bu soruyu kaydet: Sehiv secdesi ne zaman yapılır?')."
            )

        # Mesaj geçmişine asistan cevabını da ekleyip güncellenmiş Jinja2 promptunu alıyoruz
        messages.append({"role": "assistant", "content": final_answer})
        updated_prompt = self.render_chat_prompt(messages)

        return final_answer, trace_logs, updated_prompt

if __name__ == "__main__":
    agent = IslamicToolCallingAgent()
    ans, logs, prompt = agent.run("İstanbul için namaz vakitleri nedir?")
    print("ANSWER:\n", ans)
    print("\nLOGS:\n", logs)
    print("\nJINJA PROMPT:\n", prompt)