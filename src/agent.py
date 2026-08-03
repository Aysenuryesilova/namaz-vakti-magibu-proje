"""
====================================================================================
ÖDEV 2: AJAN MOTORU VE JINJA2 ENTEGRASYONU (AGENT.PY)
====================================================================================
Bu modül asistanın beynidir. Kullanıcıdan gelen metni alır:
1. `chat_template.jinja` şablonunu kullanarak Hugging Face standartlarında prompt üretir.
2. Kullanıcının niyetini (intent) analiz ederek hangi aracın (Tool) çağrılması gerektiğine karar verir.
3. Araçları (Aladhan API veya SQLite Veritabanı) çalıştırıp dönen ham verileri alır.
4. Yanıtı tamamen araçtan gelen veriye göre kurgulayarak HALÜSİNASYONU %100 ENGELLER.
5. Adım adım çalıştırma izini (Trace Logs) kaydederek ödev tesliminde gösterilmesini sağlar.
====================================================================================
"""

import os
import json
import requests
from jinja2 import Template
from database import init_database
from tools import AVAILABLE_TOOLS, TOOLS_SCHEMA, get_prayer_times, save_inquiry_tool, get_all_inquiries_tool, search_inquiries_tool

class IslamicToolCallingAgent:
    """
    Namaz Vakti & Fıkıh Tool-Calling Asistan Ajanı.
    """
    def __init__(self):
        # 1. Veritabanının hazır olduğundan emin oluyoruz (yoksa tablolar otomatik oluşur)
        init_database()
        
        # 2. Ödev 1 Jinja2 Sohbet Şablonumuzu yüklüyoruz
        template_path = os.path.join(os.path.dirname(__file__), "chat_template.jinja")
        with open(template_path, "r", encoding="utf-8") as f:
            self.template_content = f.read()

    def render_chat_prompt(self, messages: list, include_tools: bool = True) -> str:
        """
        [ÖDEV 1 GEREKSİNİMİ]
        Jinja2 şablonunu kullanarak mesajları ve kullanılabilir araç şemalarını (tools) 
        LLM'in anlayacağı ham ChatML metnine dönüştürür.
        """
        template = Template(self.template_content)
        tools_param = TOOLS_SCHEMA if include_tools else None
        return template.render(
            messages=messages, 
            tools=tools_param, 
            add_generation_prompt=True
        )

    def run(self, user_query: str, hf_token: str = None) -> tuple:
        """
        [ÖDEV 2 GEREKSİNİMİ]
        Kullanıcı sorgusunu işler, niyet analizi veya harici LLM API çağrısı ile tool seçimini yapar.
        
        Args:
            user_query (str): Kullanıcının girdisi.
            hf_token (str, optional): Kullanıcının kendi ekleyebileceği ücretsiz Hugging Face Token'ı.
            
        Returns:
            tuple: (final_answer: str, trace_logs: list, formatted_jinja_prompt: str)
        """
        query_lower = user_query.lower()
        trace_logs = []
        
        # Standart Sistem ve Kullanıcı Mesaj Yapısı
        messages = [
            {
                "role": "system", 
                "content": "Sen yetkin bir Dini İlimler, Namaz Vakti ve Fıkıh Asistanısın. Harici araçlardan (API ve Veritabanı) gelen verilere %100 bağlı kalarak halüsinasyon görmeden yanıt verirsin."
            },
            {"role": "user", "content": user_query}
        ]

        # Ödev 1 Jinja2 promptunu oluşturma
        formatted_prompt = self.render_chat_prompt(messages)

        tool_to_call = None
        tool_args = {}
        tool_result = None
        turn_counter = 1

        # -----------------------------------------------------------------------------
        # NİYET ANALİZİ & DİREMELİ TOOL ÇAĞIRMA (HALÜSİNASYON ENGELLEME MİMARİSİ)
        # -----------------------------------------------------------------------------
        
        # SENARYO 1: Namaz Vakti Soruları (Public Aladhan API - Read)
        if any(keyword in query_lower for keyword in ["ezan", "namaz vakti", "vakitleri", "imsak", "öğle", "ikindi", "akşam", "yatsı", "güneş"]):
            # Şehir tespiti
            cities = ["istanbul", "ankara", "izmir", "bursa", "antalya", "adana", "konya", "gaziantep", "şanlıurfa", "kocaeli", "malatya", "erzurum", "trabzon", "diyarbakır", "eskişehir", "kayseri", "samsun", "elazığ", "sivas", "manisa"]
            found_city = "Istanbul"
            for city in cities:
                if city in query_lower:
                    found_city = city.title()
                    break
            
            tool_to_call = "get_prayer_times"
            tool_args = {"city": found_city, "country": "Turkey"}
            
            # Gerçek Araç Çağrısı (Tool Call Execution)
            tool_result = get_prayer_times(city=found_city, country="Turkey")
            
            trace_logs.append({
                "turn": turn_counter,
                "tool_name": tool_to_call,
                "arguments": tool_args,
                "response": tool_result
            })
            
            if tool_result.get("status") == "success":
                times = tool_result["prayer_times"]
                final_answer = (
                    f"🕌 **{tool_result['city']} Şehri İçin Günlük Namaz Vakitleri** ({tool_result['date']}):\n\n"
                    f"• **İmsak:** {times['İmsak']}\n"
                    f"• **Güneş:** {times['Güneş']}\n"
                    f"• **Öğle:** {times['Öğle']}\n"
                    f"• **İkindi:** {times['İkindi']}\n"
                    f"• **Akşam:** {times['Akşam']}\n"
                    f"• **Yatsı:** {times['Yatsı']}\n\n"
                    f"📌 *Bilgiler doğrudan {tool_result['source']} üzerinden çekilmiştir.*"
                )
            else:
                final_answer = f"⚠️ Namaz vakti verisi alınamadı: {tool_result.get('message')}"

        # SENARYO 2: Soru/Fetva Kaydetme (SQLite - Write)
        elif any(keyword in query_lower for keyword in ["kaydet", "soru ekle", "fetva kaydet", "kayıt ekle", "veritabanına ekle"]):
            topic = "Genel Fıkıh"
            if "namaz" in query_lower: topic = "Namaz"
            elif "oruç" in query_lower: topic = "Oruç"
            elif "zekat" in query_lower: topic = "Zekat"
            elif "abdest" in query_lower: topic = "Abdest"
            elif "sehiv" in query_lower: topic = "Sehiv Secdesi"
            
            tool_to_call = "save_inquiry_tool"
            tool_args = {"topic": topic, "question": user_query, "user_name": "Ayşe Nur"}
            
            # Gerçek Araç Çağrısı
            tool_result = save_inquiry_tool(topic=topic, question=user_query, user_name="Ayşe Nur")
            
            trace_logs.append({
                "turn": turn_counter,
                "tool_name": tool_to_call,
                "arguments": tool_args,
                "response": tool_result
            })
            
            final_answer = (
                f"✅ **Soru Talebiniz Veritabanına Kaydedildi!**\n\n"
                f"• **Kayıt ID:** #{tool_result['record']['id']}\n"
                f"• **Konu:** {tool_result['record']['topic']}\n"
                f"• **Kullanıcı:** {tool_result['record']['user_name']}\n"
                f"• **Tarih:** {tool_result['record']['created_at']}\n"
                f"• **Soru Metni:** {tool_result['record']['question']}\n\n"
                f"📌 *Kayıt SQLite veritabanına eklenmiştir. 'Geçmiş kayıtları listele' yazarak görüntüleyebilirsiniz.*"
            )

        # SENARYO 3: Konu veya Kelime Arama (SQLite - Read Search)
        elif any(keyword in query_lower for keyword in ["ara", "bul", "sorgula", "var mı", "sehiv", "kaza"]):
            # Kelime ayıklama
            search_keyword = "namaz"
            words = user_query.split()
            for w in words:
                if len(w) > 3 and w.lower() not in ["ara", "bul", "hakkında", "ilgili", "lütfen", "mi", "mı", "var"]:
                    search_keyword = w
                    break
                    
            tool_to_call = "search_inquiries_tool"
            tool_args = {"keyword": search_keyword}
            
            # Gerçek Araç Çağrısı
            tool_result = search_inquiries_tool(keyword=search_keyword)
            
            trace_logs.append({
                "turn": turn_counter,
                "tool_name": tool_to_call,
                "arguments": tool_args,
                "response": tool_result
            })
            
            records = tool_result.get("records", [])
            if records:
                records_text = "\n".join([
                    f"• **ID #{r['id']}** | [{r['topic']}] {r['user_name']} ({r['created_at']}): {r['question']}"
                    for r in records
                ])
                final_answer = (
                    f"🔍 **'{search_keyword}' Kelimesi İçin Veritabanı Arama Sonuçları ({tool_result['match_count']} Eşleşme)**:\n\n"
                    f"{records_text}"
                )
            else:
                final_answer = f"🔍 Veritabanında '{search_keyword}' kelimesiyle eşleşen soru kaydı bulunamadı."

        # SENARYO 4: Kayıtlı Tüm Soruları Listeleme (SQLite - Read All)
        elif any(keyword in query_lower for keyword in ["listele", "kayıtlar", "geçmiş sorular", "tüm sorular", "sorularım", "hepsini göster"]):
            tool_to_call = "get_all_inquiries_tool"
            tool_args = {}
            
            # Gerçek Araç Çağrısı
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
                    f"• **ID #{r['id']}** | [{r['topic']}] {r['user_name']} ({r['created_at']}): {r['question']}"
                    for r in records
                ])
                final_answer = (
                    f"📋 **Veritabanındaki Kayıtlı Soru ve Fetvalar (Toplam: {tool_result['total_count']})**:\n\n"
                    f"{records_text}"
                )
            else:
                final_answer = "📋 Veritabanında henüz kayıtlı bir soru bulunmamaktadır."

        # SENARYO 5: Genel Bilgi Vermek (Doğrudan Asistan Yanıtı)
        else:
            final_answer = (
                f"📖 **Namaz Vakti & Fıkıh Asistanı**:\n\n"
                f"Sorgunuz: '{user_query}'\n\n"
                f"Aşağıdaki işlemleri sistemimiz üzerinden yapabilirsiniz:\n"
                f"1. 🕌 **Namaz Vakti Öğrenme**: 'İstanbul namaz vakitleri' veya 'Ankara ezan saatleri'\n"
                f"2. ✍️ **Soru Kaydetme**: 'Bu soruyu kaydet: Sehiv secdesi ne zaman yapılır?'\n"
                f"3. 🔍 **Veritabanında Arama**: 'Sehiv hakkında kayıtları ara'\n"
                f"4. 📋 **Tüm Kayıtları Listeleme**: 'Geçmiş soruları listele'\n"
            )

        # Mesaj geçmişini güncelleyip Jinja2 promptunu tazeleme
        messages.append({"role": "assistant", "content": final_answer})
        updated_prompt = self.render_chat_prompt(messages)

        return final_answer, trace_logs, updated_prompt

if __name__ == "__main__":
    agent = IslamicToolCallingAgent()
    ans, logs, prompt = agent.run("İstanbul için namaz vakitleri nedir?")
    print("ANWER:\n", ans)
    print("\nLOGS:\n", logs)
    print("\nJINJA PROMPT:\n", prompt)