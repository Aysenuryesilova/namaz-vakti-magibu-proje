"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN AGENT MOTORU (AGENT_ENGINE.PY)
==============================================================================
BU MODÜL NEYİ SAĞLAR? (EĞİTİCİ VE TEKNİK DÜZELTME):
------------------------------------------------------------------------------
1. Gerçek ReAct & LLM Tool Result Sentez Döngüsü (LLM Synthesis):
   Model bir aracı (tool) çağırdıktan sonra, araç çıktısı `role: tool` mesajı
   olarak yerel modele (Qwen2.5:3b) geri beslenir. Yerel LLM, araç çıktısını
   Sistem İstemi (System Prompt) kuralları ve Diyanet üslubu çerçevesinde
   yorumlayarak nihai doğal dil cevabını üretir.

2. Sohbet Geçmişi ve Oturum Belleği (Conversational State & Memory):
   `conversation_history` değişkeni kullanıcının sohbet boyunca sorduğu önceki
   soruları ve konumları hatırlar.

3. Kesin NLU Sözcük Sınırı (Word Boundary Regex Matching):
   'ali', 'hak', 'nur' gibi kısa Esmaül Hüsna isimlerinin çakışması önlenmiştir.
==============================================================================
"""

import sys
import re
import json
import requests
import config
import ollama_client
import tools
from database import init_database

class IslamicAgentEngine:
    def __init__(self):
        """
        Agent Engine Başlatıcı:
        - Veritabanı bağlantılarını ilkler (init_database).
        - Yerel Ollama sunucu durumunu kontrol eder.
        - Çoklu konuşma turları için sohbet belleğini (conversation_history) başlatır.
        """
        init_database()
        self.ollama_available = self.check_ollama_status()
        self.conversation_history = []  # Sohbet geçmişi belleği (Multi-turn Chat State)
        self.last_mentioned_city = None # Hatırlanan son konum/şehir bağlamı

    def check_ollama_status(self) -> bool:
        """
        Ollama daemon sunucusunun çalışıp çalışmadığını 0.3 saniyelik hızlı
        ping (health check) ile kontrol eder. Çevrimdışı ise hemen fallback moduna geçer.
        """
        try:
            res = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=0.3)
            return res.status_code == 200
        except Exception:
            return False

    def clear_memory(self):
        """Sohbet belleğini ve hatırlanan şehir bağlamını sıfırlar."""
        self.conversation_history = []
        self.last_mentioned_city = None

    def extract_city(self, text: str) -> str:
        """
        Kullanıcı sorgusundan il/ilçe adını ayıklar. Eğer kullanıcı yeni bir şehir
        belirtmemişse sohbet belleğindeki son konumu (last_mentioned_city) hatırlar!
        """
        stop_words = [
            "ezan", "namaz", "vakti", "vakitleri", "kıble", "kıblem", "yönü", "yönde",
            "kaç", "derecedir", "derece", "nedir", "mevcut", "ne", "olmalı", "nerede",
            "peki", "açısı", "açı", "miktarı", "bilgisi", "sonucu", "için", "bugün", "güncel"
        ]
        t_clean = text.lower()
        for sw in stop_words:
            t_clean = t_clean.replace(sw, "")
            
        words = [w.strip("?,.!") for w in t_clean.split() if w.strip("?,.!") and w.strip("?,.!") not in stop_words]
        
        if words and len(" ".join(words)) >= 2:
            extracted = " ".join(words).title()
            self.last_mentioned_city = extracted # Belleğe kaydet
            return extracted
            
        # Eğer yeni şehir bulunamadıysa sohbet belleğindeki son şehri döndür
        if self.last_mentioned_city:
            return self.last_mentioned_city
            
        return "İstanbul"

    def detect_fallback_tool(self, user_query: str) -> list[dict] | None:
        """
        Kullanıcının doğal dil sorgusunu NLU ile analiz ederek tetiklenmesi
        gereken 11 harici araçtan hangisinin çağrılacağını tespit eder.
        """
        q = user_query.lower().strip()
        
        # 1. Namaz vakitleri (Sivas Gemerek, İzmit, Kadıköy vb.)
        if any(kw in q for kw in ["namaz vakit", "ezan vakit", "imsak", "sahur", "iftar", "vakitleri", "ezan"]):
            city = self.extract_city(user_query)
            return [{"function": {"name": "calculate_prayer_times", "arguments": {"city": city}}}]

        # 2. Kıble açısı
        if "kıble" in q:
            city = self.extract_city(user_query)
            return [{"function": {"name": "calculate_qibla_direction", "arguments": {"city": city}}}]

        # 3. Kur'an Ayet / Sure Arama (Öncelikli: 504. ayet, kaç sure, Nebe suresi, 100. sure vb.)
        if any(kw in q for kw in ["sure", "suresi", "ayet", "ayeti", "kuran kaç", "meal"]):
            return [{"function": {"name": "search_quran_verse", "arguments": {"query_or_surah": user_query}}}]

        # 4. Esmaül Hüsna (ALLAH'IN 99 İSMİNİN TAMAMI - KELİME SINIRI ILE KESİN EŞLEŞTİRME)
        all_99_esma = list(tools.ESMAUL_HUSNA.keys())
        q_norm = (
            q.replace("i̇", "i").replace("ı", "i").replace("â", "a").replace("î", "i").replace("û", "u")
            .replace("anlamı", "").replace("ne demek", "").replace("nedir", "").replace("isminin", "").replace("ismi", "")
            .strip()
        )
        for p in ["el-", "er-", "es-", "ez-", "ef-", "et-", "ed-", "el", "er", "es", "ez", "ef", "et", "ed"]:
            if q_norm.startswith(p) and len(q_norm) > len(p) + 2:
                candidate = q_norm[len(p):].strip("- ")
                if candidate in all_99_esma:
                    q_norm = candidate
                    break

        matched_esma = None
        for name in all_99_esma:
            if len(name) <= 4:
                if re.search(r'\b' + re.escape(name) + r'\b', q_norm) or re.search(r'\b' + re.escape(name) + r'\b', q):
                    matched_esma = name
                    break
            else:
                if name == q_norm or name in q or name in q_norm:
                    matched_esma = name
                    break

        if matched_esma or "esma" in q or "allah'ın isim" in q:
            target_name = matched_esma if matched_esma else user_query
            return [{"function": {"name": "get_esmaul_husna", "arguments": {"query": target_name}}}]

        # 5. Zekat hesabı (SADECE zekat veya nisab kelimesi geçiyorsa)
        if "zekat" in q or "nisab" in q:
            numbers = [float(n) for n in re.findall(r'\d+', q)]
            gold = numbers[0] if len(numbers) > 0 else 100.0
            cash = numbers[1] if len(numbers) > 1 else 0.0
            return [{"function": {"name": "calculate_zekat", "arguments": {"gold_grams": gold, "cash_try": cash}}}]

        # 6. Veritabanına Soru Kaydetme
        if any(kw in q for kw in ["kaydet", "ekle", "veritabanına"]):
            topic = "Fıkıh"
            if "namaz" in q: topic = "Namaz"
            elif "zekat" in q: topic = "Zekat"
            elif "oruç" in q: topic = "Oruç"
            return [{"function": {"name": "save_inquiry_tool", "arguments": {"topic": topic, "question": user_query, "user_name": "Kullanıcı"}}}]

        # 7. Veritabanı Sorularını Listeleme
        if any(kw in q for kw in ["listele", "kayıtlı", "geçmiş sorular", "tüm sorular"]):
            return [{"function": {"name": "get_all_inquiries_tool", "arguments": {}}}]

        # 8. Hadis ve Buhari Doğrulama
        if "hadis" in q or "buhari" in q:
            return [{"function": {"name": "verify_hadith_source", "arguments": {"hadith_query": user_query}}}]

        # 9. Ramazan / İslami Takvim
        if "ramazan" in q or "bayram" in q or "hicri" in q:
            return [{"function": {"name": "find_islamic_event", "arguments": {"event_name": "ramazan"}}}]

        # 10. Döviz / Dolar / Güncel Haber / Web Araması
        if any(kw in q for kw in ["dolar", "euro", "güncel", "haber", "duyuru", "hac", "umre", "diyanet"]):
            return [{"function": {"name": "web_search_tool", "arguments": {"query": user_query}}}]

        # 11. Fıkıh RAG (Teheccüd, Sehiv Secdesi vb.)
        if any(kw in q for kw in ["sehiv", "teheccüd", "abdest", "bozar mı", "vacip", "farz"]):
            return [{"function": {"name": "islamic_knowledge_question", "arguments": {"question": user_query}}}]

        # 12. Genel Dini Soru Yanıtlama (Web Araması Fallback)
        return [{"function": {"name": "web_search_tool", "arguments": {"query": user_query}}}]

    def run(self, user_query: str) -> tuple[str, list[dict], str]:
        """
        Kullanıcı mesajını işleyen ana fonksiyon:
        1. Mesajı sohbet geçmişi (conversation_history) belleğine ekler.
        2. Ollama LLM ReAct döngüsüyle aracı çağırır ve çıktıyı LLM'e geri verip sentezletir.
        3. Yanıtı belleğe kaydeder ve kullanıcıya sunar.
        """
        self.conversation_history.append({"role": "user", "content": user_query})
        
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}] + self.conversation_history
        trace_logs = []
        final_answer = ""
        tool_outputs = []

        # 1. Ollama LLM ReAct & Tool Output Sentez Döngüsü
        if self.ollama_available:
            try:
                for turn in range(1, config.MAX_TOOL_ROUNDS + 1):
                    response_msg = ollama_client.chat(
                        messages=messages,
                        model=config.CHAT_MODEL,
                        tools=tools.TOOL_SCHEMAS
                    )
                    messages.append(response_msg)

                    tool_calls = response_msg.get("tool_calls")
                    if not tool_calls:
                        content = (response_msg.get("content") or "").strip()
                        if content and not content.startswith("Sorgunuz:"):
                            final_answer = content
                        break

                    for call in tool_calls:
                        name = call["function"]["name"]
                        arguments = call["function"].get("arguments") or {}
                        fn = tools.TOOLS.get(name)
                        output = fn(**arguments) if fn else f"'{name}' aracı bulunamadı."
                        
                        tool_outputs.append(str(output))
                        trace_logs.append({
                            "turn": turn,
                            "tool_name": name,
                            "arguments": arguments,
                            "response": output
                        })
                        # Araç çıktısı modele 'tool' rolünde geri iletilir (LLM Synthesis)
                        messages.append({"role": "tool", "content": str(output)})

                # Yerel LLM sentezlenmiş içerik üretmediyse doğrudan araç çıktısına düş
                if not final_answer and tool_outputs:
                    final_answer = "\n\n".join(tool_outputs)

                if final_answer:
                    self.conversation_history.append({"role": "assistant", "content": final_answer})
                    rendered_prompt = "\n".join([f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>" for m in messages])
                    return final_answer, trace_logs, rendered_prompt
            except Exception:
                pass

        # 2. Akıllı NLU Motoru (Kesintisiz Dış Araç Çağrısı)
        fallback_calls = self.detect_fallback_tool(user_query)
        if fallback_calls:
            for call in fallback_calls:
                name = call["function"]["name"]
                arguments = call["function"].get("arguments") or {}
                fn = tools.TOOLS.get(name)
                output = fn(**arguments) if fn else f"'{name}' aracı bulunamadı."

                tool_outputs.append(str(output))
                trace_logs.append({
                    "turn": 1,
                    "tool_name": name,
                    "arguments": arguments,
                    "response": output
                })
                messages.append({"role": "assistant", "content": f"[Tool Call: {name}]"})
                messages.append({"role": "tool", "content": str(output)})
            
            final_answer = "\n\n".join(tool_outputs)
        else:
            final_answer = (
                f"🕌 **İslami İlimler ve Doğruluk Denetçisi**:\n\n"
                f"Sorgunuz: '{user_query}'\n\n"
                f"Sorunuz ilmi kaynaklar ve fıkıh rehberi çerçevesinde değerlendirilmiştir. "
                f"Namaz vakitleri, kıble açısı, zekat hesabı, Kur'an mealleri veya fıkıh soruları "
                f"için özel araçlarımız aktiftir."
            )
            messages.append({"role": "assistant", "content": final_answer})

        self.conversation_history.append({"role": "assistant", "content": final_answer})
        rendered_prompt = "\n".join([f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>" for m in messages])
        return final_answer, trace_logs, rendered_prompt

if __name__ == "__main__":
    engine = IslamicAgentEngine()
    ans, logs, _ = engine.run("İstanbul ezan vakitleri")
    print("ENGINE SYNTHESIS RESULT:\n", ans)
