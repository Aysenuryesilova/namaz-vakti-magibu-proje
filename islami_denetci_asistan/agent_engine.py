"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN AGENT MOTORU (AGENT_ENGINE.PY)
==============================================================================
Bu modül:
1. Ollama LLM + Tool Calling (Araç Kullanımı) ReAct Döngüsünü yönetir.
2. Araç sonuçlarını doğrudan asistana aktarır ve halüsinasyon görmeden net cevaplar verir.
3. NLU motoru ile soru tiplerini ayrıştırıp dış veritabanı ve API araçlarını çağırır.
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
        init_database()
        self.ollama_available = self.check_ollama_status()

    def check_ollama_status(self) -> bool:
        """Ollama sunucusunun çalışıp çalışmadığını anlık kontrol eder (0.1sn)."""
        try:
            res = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=0.3)
            return res.status_code == 200
        except Exception:
            return False

    def extract_city(self, text: str) -> str:
        """Kullanıcı sorgusundan il/ilçe adını ayıklar (Örn: Sivas Gemerek -> Sivas Gemerek, İzmit -> İzmit)."""
        t_clean = (
            text.lower()
            .replace("ezan", "")
            .replace("namaz", "")
            .replace("vakti", "")
            .replace("vakitleri", "")
            .replace("kıble", "")
            .replace("kıblem", "")
            .replace("yönü", "")
            .replace("yönde", "")
            .replace("kaç", "")
            .replace("derecedir", "")
            .replace("nedir", "")
            .replace("mevcut", "")
            .replace("ne", "")
            .replace("olmalı", "")
            .replace("nerede", "")
            .strip()
        )
        words = [w.strip("?,.!") for w in t_clean.split() if w.strip("?,.!") not in ["için", "mevcut", "ne", "yönde", "olmalı", "bugün", "güncel", "nerede"]]
        if words and len(" ".join(words)) >= 2:
            return " ".join(words).title()
        return "İstanbul"

    def detect_fallback_tool(self, user_query: str) -> list[dict] | None:
        """Kullanıcı sorgusuna uygun aracı tespit eder."""
        q = user_query.lower().strip()
        
        # 1. Namaz vakitleri (Sivas Gemerek, İzmit, Kadıköy vb.)
        if any(kw in q for kw in ["namaz vakit", "ezan vakit", "imsak", "sahur", "iftar", "vakitleri", "ezan"]):
            city = self.extract_city(user_query)
            return [{"function": {"name": "calculate_prayer_times", "arguments": {"city": city}}}]

        # 2. Kıble açısı
        if "kıble" in q:
            city = self.extract_city(user_query)
            return [{"function": {"name": "calculate_qibla_direction", "arguments": {"city": city}}}]

        # 3. Esmaül Hüsna (Fettah, Rahman, Rahim, Allah'ın isimleri vb.)
        esma_names = ["fettah", "rahman", "rahim", "melik", "kuddus", "selam", "mumin", "muheymin", "aziz", "cebbar", "mutekebbir", "halik", "bari", "musavvir", "gaffar", "kahhar", "vehhab", "rezzak", "alim", "esma"]
        if any(kw in q for kw in esma_names) or "allah'ın isim" in q or "el-" in q or "er-" in q:
            # Fettah kelimesini yakalayalım
            match_name = next((name for name in esma_names if name in q and name != "esma"), "fettah" if "fettah" in q else user_query)
            return [{"function": {"name": "get_esmaul_husna", "arguments": {"query": match_name}}}]

        # 4. Kur'an Ayet / Sure Arama (504. ayet, Nebe suresi, 100. sure, sure meali vb.)
        if any(kw in q for kw in ["sure", "suresi", "ayet", "ayeti", "kuran kaç", "meal"]):
            return [{"function": {"name": "search_quran_verse", "arguments": {"query_or_surah": user_query}}}]

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

        return None

    def run(self, user_query: str) -> tuple[str, list[dict], str]:
        """
        Kullanıcı mesajını işler, araçları çalıştırır, trace logları üretir ve nihai yanıtı döndürür.
        Returns: (final_answer, trace_logs, rendered_prompt)
        """
        messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]
        trace_logs = []
        final_answer = ""
        tool_outputs = []

        # 1. Ollama LLM ReAct Döngüsü
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
                        messages.append({"role": "tool", "content": str(output)})

                if tool_outputs:
                    final_answer = "\n\n".join(tool_outputs)

                if final_answer:
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

        rendered_prompt = "\n".join([f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>" for m in messages])
        return final_answer, trace_logs, rendered_prompt

if __name__ == "__main__":
    engine = IslamicAgentEngine()
    ans, logs, prompt = engine.run("fettah ne demek")
    print("YANIT:\n", ans)
