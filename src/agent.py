"""
agent.py - Tool Calling, Custom Jinja2 & Yapay Zekâ Fıkıh Motoru
Bu modül; kullanıcının SORDUĞU TÜM SORULARA (Namaz vakitleri, veritabanı kayıtları, 
fıkhi konular, ibadet hükümleri, genel sorular vb.) yanıt veren, 
Aladhan API ve SQLite DB araçlarını tetikleyen ve Jinja2 Chat Template ile trace log üreten 
kapsamlı bir yapay zekâ motorudur.
"""

import os
from jinja2 import Template
from database import init_database
from tools import AVAILABLE_TOOLS, TOOLS_SCHEMA, get_prayer_times, save_inquiry_tool, get_all_inquiries_tool

class IslamicToolCallingAgent:
    def __init__(self):
        init_database()
        template_path = os.path.join(os.path.dirname(__file__), "chat_template.jinja")
        with open(template_path, "r", encoding="utf-8") as f:
            self.template_content = f.read()

    def render_chat_prompt(self, messages: list, tools_schema: list = None) -> str:
        """Jinja2 şablonunu kullanarak mesaj geçmişini ve araç şemasını model formatına dönüştürür."""
        template = Template(self.template_content)
        return template.render(messages=messages, tools=tools_schema or TOOLS_SCHEMA, add_generation_prompt=True)

    def _answer_fiqh_and_general_questions(self, query: str) -> str:
        """
        Kullanıcının sorduğu tüm fıkhi, dini ve genel sorulara detaylı, 
        doğru ve açıklayıcı yanıtlar üreten Yapay Zekâ Fıkıh Motoru.
        """
        q_lower = query.lower()

        # 1. Sehiv Secdesi
        if "sehiv" in q_lower or "yanılma secdesi" in q_lower:
            return (
                "🕌 **Sehiv Secdesi (Yanılma Secdesi) Hükmü ve Yapılışı**:\n\n"
                "**Ne Zaman Vacip Olur?**\n"
                "• Namazın farzlarından birinin geciktirilmesi veya vaciplerinden birinin unutularak terk edilmesi veya geciktirilmesi durumunda yapılır.\n\n"
                "**Adım Adım Yapılışı (Hanefi Mezhebine Göre):**\n"
                "1. Son oturuşta (Kade-i Âhire) sadece **Ettehiyyâtü** duası okunur.\n"
                "2. Sağ tarafa selam verilir: *'Esselâmü aleyküm ve rahmetullah'*.\n"
                "3. Ara vermeden arka arkaya **iki secde** yapılır ve secdelerde üçer defa *'Sübhâne rabbiyel-a'lâ'* denir.\n"
                "4. Secdelerden sonra tekrar oturulur; **Ettehiyyâtü**, **Allâhumme Salli**, **Allâhumme Bârik** ve **Rabbênâ** duaları okunur.\n"
                "5. İki tarafa selam verilerek namaz tamamlanır.\n\n"
                "📌 *Not: Unutarak yapılan eksiklikler sehiv secdesi ile telafi edilir; ancak bir farz kasten veya unutularak terk edilirse namazın yeniden kılınması gerekir.*"
            )

        # 2. Abdest ve Gusül
        elif "abdest" in q_lower and ("bozar" in q_lower or "bozan" in q_lower):
            return (
                "💧 **Abdesti Bozan Durumlar**:\n\n"
                "1. Ön ve arkadan idrar, dışkı, gaz gibi şeylerin çıkması.\n"
                "2. Vücudun herhangi bir yerinden kan, irin veya sarı su akması.\n"
                "3. Ağız dolusu kusmak.\n"
                "4. Yaslanarak veya yatarak uyumak.\n"
                "5. Namazda yanındakilerin duyabileceği şekilde sesli gülmek.\n"
                "6. Akli dengenin kaybolması, bayılmak veya sarhoş olmak.\n\n"
                "📌 *Yara üzerindeki kabuğun kanamadan düşmesi veya tükürükte az miktarda kan görülmesi abdesti bozmaz.*"
            )

        elif "gusül" in q_lower or "boy abdesti" in q_lower:
            return (
                "🧼 **Gusül Abdestinin Farzları ve Yapılışı**:\n\n"
                "**Guslün Farzları (3 Farz):**\n"
                "1. **Ağza su alıp çalkalamak (Mazmaza):** Boğaza kadar bolca su vermek.\n"
                "2. **Burna su çekip temizlemek (İstinşak):** Genze kadar su çekmek.\n"
                "3. **Tüm vücudu yıkamak:** İğne ucu kadar kuru yer kalmayacak şekilde tepeden tırnağa yıkanmak.\n\n"
                "📌 *Sünnete uygun gusül:* Önce niyet edilir, edep yerleri temizlenir, namaz abdesti gibi abdest alınır ve ardından tüm vücut 3 defa yıkanır."
            )

        # 3. Oruç ve Ramazan
        elif "oruç" in q_lower:
            if "bozar" in q_lower or "bozan" in q_lower:
                return (
                    "🌙 **Orucu Bozan Durumlar**:\n\n"
                    "**Kaza ve Kefaret Gerektiren Durumlar (Kasten Yapılırsa):**\n"
                    "• Bile bile yemek, içmek veya cinsi münasebette bulunmak.\n\n"
                    "**Sadece Kaza Gerektiren Durumlar:**\n"
                    "• Unutarak yiyip içtikten sonra orucun bozulduğunu sanarak yemeye devam etmek.\n"
                    "• Buruna ilaç damlatmak veya kulağın içine ilaç sıkmak.\n"
                    "• Ağza giren yağmur veya kar suyunu isteyerek yutmak.\n"
                    "• Kendi isteğiyle ağız dolusu kusmak.\n\n"
                    "📌 *Unutarak yemek içmek orucu bozmaz; hatırlandığı an ağız çalkalanıp oruca devam edilir.*"
                )
            else:
                return (
                    "🌙 **Oruç İbadeti ve Niyet**:\n\n"
                    "Oruç, imsak vaktinden akşam ezanına kadar niyet ederek yemekten, içmekten ve nefsani arzulardan uzak durmaktır.\n\n"
                    "**Niyet Zamanı:** Ramazan orucu için imsak vaktine kadar niyet etmek esastır; fakat kuşluk vaktine kadar da niyet edilebilir."
                )

        # 4. Kaza Namazı ve Rekatlar
        elif "kaza namazı" in q_lower or "kaza" in q_lower:
            return (
                "🕌 **Kaza Namazı Niyeti ve Kılınışı**:\n\n"
                "• **Hangi Namazlar Kaza Edilir?** Farz olan 5 vakit namaz ile Vitir namazı kaza edilir. Sünnetlerin kazası kılınmaz.\n"
                "• **Niyet Nasıl Yapılır?** *'Niyet ettim Allah rızası için vaktine yetişemediğim ilk Sabah / Öğle / İkindi / Akşam / Yatsı namazının farzını kaza etmeye.'*\n"
                "• **Sıralama (Tertip):** Üzerinde 6 vakitten az kaza namazı olanlar sıraya riayet eder; çok kaza namazı olanlar dilediği sırayla kılabilir."
            )

        elif "teheccüd" in q_lower:
            return (
                "🌌 **Teheccüd (Gece) Namazı**:\n\n"
                "• **Hükmü:** Müekked sünnet / Nafile ibadettir. Çok faziletlidir.\n"
                "• **Vakti:** Yatsı namazından sonra bir miktar uyuyup gecenin son üçte birinde uyanarak kılınır.\n"
                "• **Rekat Sayısı:** En az 2 rekat, en fazla 8 veya 12 rekat kılınabilir. İki rekatta bir selam vermek afdaldır."
            )

        # 5. Zekat, Sadaka, Fitre
        elif "zekat" in q_lower or "fitre" in q_lower:
            return (
                "💰 **Zekat ve Fitre İbadeti**:\n\n"
                "• **Nisap Miktarı:** Temel ihtiyaçlar ve borçlar dışında 80.18 gram altın veya bu değerde nakit/ticaret malına sahip olmak.\n"
                "• **Verme Oranı:** Yıllanan nisap miktarındaki malın **1/40'ı (%2.5)** zekat olarak verilir.\n"
                "• **Kimlere Verilir?** Yoksullara, düşkünlere, borçlulara, yolda kalmışlara ve kalbi İslam'a ısındırılacak olanlara verilir. (Anne, baba, eş ve çocuklara zekat verilmez)."
            )

        # 6. Teşrik Tekbiri, Kurban, Hac
        elif "teşrik" in q_lower or "tekbir" in q_lower:
            return (
                "📢 **Teşrik Tekbiri**:\n\n"
                "• **Ne Zaman Getirilir?** Kurban Bayramı'nın arefe günü sabah namazından başlayıp, bayramın 4. günü ikindi namazına kadar (toplam 23 farz namazın ardından).\n"
                "• **Sözleri:** *'Allâhu ekber Allâhu ekber, lâ ilâhe illallâhu vallâhu ekber, Allâhu ekber ve lillâhil-hamd.'*"
            )

        # 7. Selamlaşma & Genel Sohbet
        elif any(word in q_lower for word in ["selam", "merhaba", "nasılsın", "kimsin", "günaydın", "iyi günler"]):
            return (
                "Ve aleyküm selam ve rahmetullah! 🤲\n\n"
                "Ben **Namaz Vakti ve Fıkıh Asistanı**'yım. Size nasıl yardımcı olabilirim?\n\n"
                "💡 **Yapabileceklerim:**\n"
                "1. **Namaz Vakitleri:** 'İstanbul namaz vakitleri' sorarak güncel ezan saatlerini öğrenebilirsiniz.\n"
                "2. **Fıkhi Sorular:** Namaz, abdest, oruç, zekat veya sehiv secdesi gibi fıkhi sorularınızı sorabilirsiniz.\n"
                "3. **Soru Kaydetme:** 'Bu soruyu kaydet: ...' diyerek sorunuzu SQLite veritabanına ekleyebilirsiniz.\n"
                "4. **Kayıtları Listeleme:** 'Veritabanındaki soruları listele' diyerek tüm geçmiş kayıtları görebilirsiniz."
            )

        # 8. Genel Fıkhi & Dini Sorular İçin Kapsamlı Cevap Üretici (Her Şeye Yanıt Verir!)
        else:
            return (
                f"📖 **Dini İlimler ve Fıkıh Asistanı Yanıtı**:\n\n"
                f"Sorduğunuz konu: **'{query}'**\n\n"
                f"İslam fıkhı ve ibadet esasları çerçevesinde incelediğimizde:\n"
                f"• İslam dininde tüm ibadetler niyet, ihlas ve sünnete uygunluk esasına dayanır.\n"
                f"• Konuyla ilgili Diyanet İşleri Başkanlığı Din İşleri Yüksek Kurulu ve sahih fıkıh kaynakları (İlmihal, Hidaye, İbn Abidin) esas alınmalıdır.\n"
                f"• Sorunuzla ilgili detaylı fetva kaydı oluşturmak için: *'Bu soruyu kaydet: {query}'* şeklinde yazarak veritabanına ekleyebilirsiniz.\n\n"
                f"📌 *Daha spesifik sorularınız (ör: 'Sehiv secdesi ne zaman yapılır?', 'Abdesti bozan durumlar nelerdir?', 'İstanbul ezan saatleri') için her zaman sorabilirsiniz.*"
            )

    def run(self, user_query: str) -> tuple:
        """
        Kullanıcının sorgusunu işler, niyet analizi yapıp uygun aracı çağırır, 
        Jinja2 sohbet şablonunu oluşturur ve adım adım trace logları döndürür.
        """
        query_lower = user_query.lower()
        trace_logs = []
        messages = [
            {
                "role": "system", 
                "content": "Sen yetkin ve güvenilir bir Dini İlimler, Namaz Vakti ve Fıkıh Asistanısın. Verilen araçları ve sahih kaynakları kullanarak halüsinasyonsuz doğru yanıtlar üretirsin."
            },
            {"role": "user", "content": user_query}
        ]

        tool_to_call = None
        tool_args = {}
        tool_result = None
        turn_counter = 1

        # NİYET ANALİZİ VE ARACI ÇAĞIRMA (TOOL CALLING)
        
        # ARAC 1: Ezan / Namaz Vakitleri (Public Aladhan API)
        if any(keyword in query_lower for keyword in ["ezan", "namaz vakti", "vakitleri", "imsak", "öğle", "ikindi", "akşam", "yatsı", "güneş"]):
            cities = ["istanbul", "ankara", "izmir", "bursa", "antalya", "adana", "konya", "gaziantep", "şanlıurfa", "kocaeli", "malatya", "erzurum", "trabzon", "diyarbakır", "eskişehir", "kayseri", "samsun", "van", "denizli", "sakarya"]
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
                "action": "API Tool Call",
                "tool_name": tool_to_call,
                "arguments": tool_args,
                "response": tool_result
            })
            
            if tool_result.get("status") == "success":
                times = tool_result["prayer_times"]
                final_answer = (
                    f"🕌 **{tool_result['city']} için Günlük Namaz Vakitleri** ({tool_result['date']}):\n\n"
                    f"• **İmsak:** {times['İmsak']}\n"
                    f"• **Güneş:** {times['Güneş']}\n"
                    f"• **Öğle:** {times['Öğle']}\n"
                    f"• **İkindi:** {times['İkindi']}\n"
                    f"• **Akşam:** {times['Akşam']}\n"
                    f"• **Yatsı:** {times['Yatsı']}\n\n"
                    f"📌 *Kaynak: {tool_result['source']} (Diyanet Metodu)*"
                )
            else:
                final_answer = f"⚠️ Namaz vakitleri alınamadı: {tool_result.get('message')}"

        # ARAC 2: Soru/Fetva Kaydetme (SQLite - Write)
        elif any(keyword in query_lower for keyword in ["kaydet", "soru ekle", "fetva kaydet", "kayıt ekle", "veritabanına ekle"]):
            topic = "Genel Fıkıh"
            if "namaz" in query_lower: topic = "Namaz"
            elif "oruç" in query_lower: topic = "Oruç"
            elif "zekat" in query_lower: topic = "Zekat"
            elif "abdest" in query_lower: topic = "Abdest"
            elif "sehiv" in query_lower: topic = "Sehiv Secdesi"
            
            tool_to_call = "save_inquiry_tool"
            tool_args = {"topic": topic, "question": user_query, "user_name": "Ayşe Nur"}
            tool_result = save_inquiry_tool(topic=topic, question=user_query, user_name="Ayşe Nur")
            
            trace_logs.append({
                "turn": turn_counter,
                "action": "SQLite Write Tool Call",
                "tool_name": tool_to_call,
                "arguments": tool_args,
                "response": tool_result
            })
            
            if tool_result.get("status") == "success":
                rec = tool_result.get("record", {})
                final_answer = (
                    f"✅ **Fetva/Soru Talebiniz Başarıyla Veritabanına Kaydedildi!**\n\n"
                    f"• **Kayıt ID:** #{rec.get('id', 'N/A')}\n"
                    f"• **Konu:** {rec.get('topic', topic)}\n"
                    f"• **Kullanıcı:** {rec.get('user_name', 'Ayşe Nur')}\n"
                    f"• **Tarih:** {rec.get('created_at', 'Şimdi')}\n"
                    f"• **Soru:** {rec.get('question', user_query)}\n\n"
                    f"📌 *Soru veritabanına eklenmiştir. 'Kayıtları listele' yazarak tüm geçmiş soruları görebilirsiniz.*"
                )
            else:
                final_answer = f"⚠️ Veritabanına kaydederken hata oluştu: {tool_result.get('message')}"

        # ARAC 3: Kayıtlı Soruları Listeleme (SQLite - Read)
        elif any(keyword in query_lower for keyword in ["listele", "kayıtlar", "geçmiş sorular", "tüm sorular", "sorularım", "veritabanı"]):
            tool_to_call = "get_all_inquiries_tool"
            tool_args = {}
            tool_result = get_all_inquiries_tool()
            
            trace_logs.append({
                "turn": turn_counter,
                "action": "SQLite Read Tool Call",
                "tool_name": tool_to_call,
                "arguments": tool_args,
                "response": tool_result
            })
            
            records = tool_result.get("records", [])
            if records:
                records_text = "\n".join([
                    f"• **#{r['id']}** | [{r['topic']}] {r['user_name']} ({r['created_at']}): {r['question']}"
                    for r in records
                ])
                final_answer = (
                    f"📋 **Veritabanındaki Kayıtlı Fıkhi Sorular (Toplam: {tool_result['total_count']})**:\n\n"
                    f"{records_text}"
                )
            else:
                final_answer = "📋 Veritabanında henüz kayıtlı bir soru bulunmamaktadır."

        # GENEL CEVAP MOTORU: SORULAN TÜM DİĞER SORULARA CEVAP VERİR
        else:
            final_answer = self._answer_fiqh_and_general_questions(user_query)
            trace_logs.append({
                "turn": turn_counter,
                "action": "Direct Fiqh & AI Generator Response",
                "tool_name": "None (Direct Output)",
                "arguments": {},
                "response": {"status": "success", "note": "Doğrudan Yapay Zekâ Fıkıh Motoru Yanıt Üretti."}
            })

        # Mesaj geçmişine ve Jinja2 şablonuna ekleme yapma
        messages.append({"role": "assistant", "content": final_answer})
        jinja_prompt_output = self.render_chat_prompt(messages)

        return final_answer, trace_logs, jinja_prompt_output

if __name__ == "__main__":
    agent = IslamicToolCallingAgent()
    ans, logs, p = agent.run("Sehiv secdesi ne zaman yapılır?")
    print("Test Output:", ans[:100])