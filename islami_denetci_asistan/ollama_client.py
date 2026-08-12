"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN - OLLAMA İLETİŞİM KATMANI (OLLAMA_CLIENT.PY)
==============================================================================
BU MODÜL NEYİ SAĞLAR? (EĞİTİCİ AÇIKLAMA):
------------------------------------------------------------------------------
1. Ollama REST API İletişimi:
   Yerel bilgisayarınızda (localhost:11434) çalışan Ollama yapay zeka sunucusuyla
   HTTP POST istekleri üzerinden haberleşir.

2. Tool Calling (Araç Kullanımı) Şema İletimi:
   `tools` parametresiyle Python araçlarının JSON şemalarını Ollama modeline
   iletir. Model cevabında eğer bir araç çalıştırmak isterse JSON çıktısı üretir.

3. Hızlı Zaman Aşımı (Fast Timeout):
   Ollama kapalıysa veya yanıt veremiyorsa uygulamanın donmasını engeller ve
   kontrolü hızlıca Fallback NLU engine katmanına devreder.
==============================================================================
"""

import json
import requests
import config

def chat(messages: list[dict], model: str = config.CHAT_MODEL, tools: list[dict] = None) -> dict:
    """
    Yerel Ollama LLM modeline HTTP POST isteği gönderen ana fonksiyon.
    
    Parametreler:
    - messages : Sohbet geçmişi ve sistem istemi (System, User, Assistant, Tool)
    - model    : Kullanılacak yerel model adı (Örn: qwen2.5:3b)
    - tools    : Modeli bilgilendiren araç JSON şemaları kümesi
    
    Döndürür:
    - Ollama'dan gelen yanıt mesajı nesnesi (Role, Content, Tool Calls)
    """
    url = f"{config.OLLAMA_HOST}/api/chat"
    
    # HTTP İstek Gövdesi (Payload) Oluşturma
    payload = {
        "model": model,
        "messages": messages,
        "stream": False, # Yanıtı parça parça değil, tek seferde almak için False
        "options": {
            "temperature": config.TEMPERATURE, # Yaratıcılık/Doğruluk dengesi (0.1 = Çok kararlı)
            "num_predict": config.MAX_TOKENS    # Üretilecek maksimum token sayısı
        }
    }
    
    # Eğer araç şemaları tanımlanmışsa isteğe ekle
    if tools:
        payload["tools"] = tools

    try:
        # Ollama sunucusuna 15 saniyelik zaman aşımı ile HTTP POST gönder
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            res_json = response.json()
            return res_json.get("message", {"role": "assistant", "content": ""})
        else:
            raise RuntimeError(f"Ollama API hatası: HTTP Status {response.status_code}")
    except Exception as exc:
        raise RuntimeError(f"Ollama sunucusuna ulaşılamadı veya zaman aşımı: {exc}")

if __name__ == "__main__":
    # Basit Bağlantı ve Test Fonksiyonu
    try:
        test_msg = [{"role": "user", "content": "Merhaba"}]
        res = chat(test_msg)
        print("Ollama Test Yanıtı:", res)
    except Exception as e:
        print("Test Hatası:", e)
