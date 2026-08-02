"""
agent.py - Tool Calling, Fıkıh Bilgi Tabanı ve Jinja2 Entegrasyonlu Ajan Motoru
"""

import os
from jinja2 import Template
from database import init_database
from tools import AVAILABLE_TOOLS, TOOLS_SCHEMA, get_prayer_times, save_inquiry_tool, get_all_inquiries_tool

# Detaylı İslam Fıkhı ve İbadet Bilgi Tabanı (Halüsinasyonsuz Doğru Cevaplar İçin)
FIQH_KNOWLEDGE_BASE = {
    "sehiv secdesi": (
        "📖 **Sehiv Secdesi (Yanılma Secdesi) Hükmü ve Yapılışı**:\n\n"
        "• **Nedir?:** Namazın farzlarından birini geciktirmek veya vaciplerinden birini unutarak terk etmek ya da geciktirmek durumunda yapılan secderdir.\n"
        "• **Nasıl Yapılır?:** Son oturuşta sadece 'Tahiyyat' (Ettehiyyatü) duası okunduktan sonra sağa ve sola (veya sadece sağa) selam verilir. Ardından 'Allahu Akbar' denilerek iki defa peş peşe secdeye varılır. Secdelerden sonra tekrar oturulup Tahiyyat, Salli-Barik ve Rabbena duaları okunarak selam verilip namaz tamamlanır.\n"
        "• **Hükmü:** Vaciptir. Farzın terkinde sehiv secdesi namazı kurtarmaz, namazın yeniden kılınması gerekir."
    ),
    "abdest": (
        "🧼 **Abdestin Farzları ve Sünnetleri**:\n\n"
        "• **Farzları (4 Tane):**\n"
        "  1. Yüzü bir kere yıkamak (saç bitiminden çene altına, kulak yumuşağına kadar).\n"
        "  2. Kolları dirseklerle birlikte bir kere yıkamak.\n"
        "  3. Başın en az dörtte birini (1/4) ıslak elle meshetmek.\n"
        "  4. Ayakları topuklarla birlikte bir kere yıkamak.\n\n"
        "• **Abdesti Bozan Başlıca Durumlar:** Vücuttan kan veya irin çıkması, idrar/dışkı yollarından çıkan şeyler, ağız dolusu kusmak, yatarak veya dayanarak uyumak, namazda yakındakilerin duyacağı kadar sesli gülmek."
    ),
    "gusül": (
        "🚿 **Gusül (Boy Abdesti) Farzları**:\n\n"
        "1. Ağza su alıp boğaza kadar çalkalamak (Mazmaza).\n"
        "2. Burna su çekip temizlemek (İstinşak).\n"
        "3. Bütün bedeni kuru yer kalmayacak şekilde yıkamak."
    ),
    "namaz farzları": (
        "🕌 **Namazın Farzları (12 Tane)**:\n\n"
        "• **Dışındaki Farzlar (Şartları):**\n"
        "  1. Hadesten Taharet (Abdest/Gusül)\n"
        "  2. Necasetten Taharet (Beden/Elbise temizliği)\n"
        "  3. Setr-i Avret (Avret yerlerini örtmek)\n"
        "  4. İstikbal-i Kıble (Kıbleye yönelmek)\n"
        "  5. Vakit (Namaz vaktinin girmesi)\n"
        "  6. Niyet\n\n"
        "• **İçindeki Farzlar (Rükünleri):**\n"
        "  1. İftitah Tekbiri ('Allahu Akbar' ile başlamak)\n"
        "  2. Kıyam (Ayakta durmak)\n"
        "  3. Kıraat (Kur'an okumak)\n"
        "  4. Rükû (Eğilmek)\n"
        "  5. Secde (Yere kapanmak)\n"
        "  6. Ka'de-i Ahîre (Son oturuşta Tahiyyat okuyacak kadar oturmak)"
    ),
    "vitir": (
        "🌙 **Vitir Namazı Hükmü ve Kılınışı**:\n\n"
        "• **Hükmü:** Hanefi mezhebine göre vaciptir.\n"
        "• **Vakti:** Yatsı namazından sonra başlar, imsak vaktine kadar kılınabilir.\n"
        "• **Kılınışı:** 3 rekattır. 3. rekatta Fatiha ve zammı sure okunduktan sonra ayağa kalkar gibi tekbir alınır ('Allahu Akbar'), eller kaldırılıp tekrar bağlanır ve **Kunut Duaları** okunur, ardından rükûya gidilir."
    ),
    "seferilik": (
        "🚗 **Seferilik (Yolculuk) Namazı Kuralları**:\n\n"
        "• **Mesafe:** En az 90 km mesafeye, en az 15 gün kalmamak üzere yolculuğa çıkan kişi seferi sayılır.\n"
        "• **Kılınış:** 4 rekatlık farz namazlar (Öğle, İkindi, Yatsı) 2 rekat olarak kısaltılarak kılınır (Kasr-ı Namaz).\n"
        "• **Sünnetler:** Vakit ve imkan varsa sünnetler kılınır, aciliyet varsa terk edilebilir."
    ),
    "kerahat": (
        "⏳ **Namaz Kılmanın Mekruh Olduğu Kerahat Vakitleri**:\n\n"
        "1. **Güneş Doğarken:** Güneşin doğuşundan itibaren yaklaşık 45-50 dakika geçinceye kadar.\n"
        "2. **Güneş Tam Tepe Noktasındayken (İstiva Vakti):** Öğle ezanından yaklaşık 15-20 dakika öncesi.\n"
        "3. **Güneş Batarken:** Akşam ezanına 45 dakika kala başlar. (Sadece o günün ikindi namazının farzı gecikmişse kılınabilir)."
    ),
    "oruç": (
        "🌙 **Oruç Fıkhı ve Kuralları**:\n\n"
        "• **Orucu Bozup Sadece Kaza Gerektirenler:** Unutarak yiyip içtikten sonra orucun bozulduğunu sanarak yemeye devam etmek, ağza kaçan yağmur/kar suyunu yutmak, ilaç kullanmak.\n"
        "• **Orucu Bozmayanlar:** Unutarak yemek/içmek, göz/kulak damlası damlatmak, banyo yapmak, diş fırçalamak (macun yutmamak şartıyla), koku koklamak."
    )
}

class IslamicToolCallingAgent:
    def __init__(self):
        init_database()
        template_path = os.path.join(os.path.dirname(__file__), "chat_template.jinja")
        with open(template_path, "r", encoding="utf-8") as f:
            self.template_content = f.read()
            
    def render_chat_prompt(self, messages: list) -> str:
        template = Template(self.template_content)
        return template.render(messages=messages, add_generation_prompt=True)

    def run(self, user_query: str) -> tuple:
        query_lower = user_query.lower()
        trace_logs = []
        messages = [
            {
                "role": "system", 
                "content": "Sen yetkin bir Dini İlimler ve Fetva Takip Asistanısın. Veritabanı ve API araçlarını kullanarak halüsinasyon görmeden doğru yanıtlar üretirsin."
            },
            {"role": "user", "content": user_query}
        ]

        formatted_prompt = self.render_chat_prompt(messages)

        tool_to_call = None
        tool_args = {}
        tool_result = None
        turn_counter = 1

        # 1. Ezan / Namaz Vakitleri (Public Aladhan API - Read)
        if any(keyword in query_lower for keyword in ["ezan", "namaz vakti", "vakitleri", "imsak", "öğle", "ikindi", "akşam", "yatsı"]):
            cities = ["istanbul", "ankara", "izmir", "bursa", "antalya", "adana", "konya", "gaziantep", "şanlıurfa", "kocaeli", "malatya", "erzurum", "trabzon", "diyarbakır", "eskişehir", "kayseri", "samsun"]
            found_city = "Istanbul"
            for city in cities:
                if city in query_lower:
                    found_city = city.title()
                    break
            
            tool_to_call = "get_prayer_times"
            tool_args = {"city": found_city, "country": "Turkey"}
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

        # 2. Soru/Fetva Kaydetme (SQLite - Write)
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

        # 3. Kayıtlı Soruları Listeleme (SQLite - Read)
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

        # 4. Bilgi Tabanı Taraması ve Fıkhi Cevap Üretme
        else:
            matched_key = None
            for key in FIQH_KNOWLEDGE_BASE:
                if key in query_lower:
                    matched_key = key
                    break
            
            if matched_key:
                final_answer = FIQH_KNOWLEDGE_BASE[matched_key]
            else:
                final_answer = (
                    f"📖 **Fıkhi Bilgi Asistanı**:\n\n"
                    f"Sorgunuz: '{user_query}'\n\n"
                    f"Dini ilimler, ibadet esasları ve namaz vakitleri konusunda size yardımcı olabilirim.\n"
                    f"• Şehir bazlı vakitler için: *'İstanbul namaz vakitleri'*\n"
                    f"• Fıkhi konular için: *'Sehiv secdesi ne zaman yapılır?'* veya *'Abdestin farzları nelerdir?'*\n"
                    f"• Sorunuzu kaydetmek için: *'Bu soruyu kaydet: Orucu bozan şeyler nelerdir?'*\n"
                    f"• Kayıtları görmek için: *'Kayıtlı soruları listele'*"
                )

        messages.append({"role": "assistant", "content": final_answer})
        updated_prompt = self.render_chat_prompt(messages)

        return final_answer, trace_logs, updated_prompt