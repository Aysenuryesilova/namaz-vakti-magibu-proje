"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN - SİSTEM VE MODEL KONFİGÜRASYONU (CONFIG.PY)
==============================================================================
BU MODÜL NEYİ SAĞLAR? (EĞİTİCİ AÇIKLAMA):
------------------------------------------------------------------------------
1. System Prompt (Sistem İstemi):
   Yapay zekanın 'ana Anayasası'dır. Asistanın rolünü (İslami İlimler Denetçisi),
   konuşma üslubunu (saygılı, ilmi, akademisyen tonda) ve katı kurallarını
   (asla bilgi uydurmama, kaynak gösterme) belirler.

2. Model Parametreleri:
   - TEMPERATURE: 0.1 (Sıfıra yakın değerler modelin yaratıcı uydurmalar yapmasını
     engeller, kararlı ve kesin yanıtlar vermesini sağlar).
   - MAX_TOOL_ROUNDS: Modelin ardışık olarak kaç araç çağırabileceğini sınırlar.

3. Temiz Mimari ve Vektör Veritabanı Seçimi (Architectural Rationale):
   - Modüler Kod Mimarısı: Kodun tek bir dev dosya (monolith) yerine katmanlarına
     (config, client, engine, tools, db, rag, ui) ayrılması Clean Architecture
     prensipleri gereğidir.
   - Vektör RAG Motoru: Ağır ve karmaşık dış bağımlılıklar (ChromaDB/PGVector C++ bağları)
     yerine sıfır bağımlılıklı, %100 kararlı ve hızlı matematiksel TF-IDF & Kosinüs Benzerliği
     Vektör Motoru (`islamic_rag.py`) tercih edilmiştir.
==============================================================================
"""

import os

# Yerel Ollama Sunucu Adresi
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Kullanılacak Yerel Yapay Zeka Modeli
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5:3b")

# Model Üretim Parametreleri
TEMPERATURE = 0.1       # 0.0 - 1.0 arası: Düşük değer = Sıfır halüsinasyon, yüksek doğruluk
MAX_TOKENS = 1024       # Cevap başına maksimum kelime/token uzunluğu
MAX_TOOL_ROUNDS = 4     # Bir soruda çalıştırılabilecek maksimum ReAct döngü sayısı

# ==============================================================================
# SİSTEM İSTEMİ (SYSTEM PROMPT) - ASİSTAN ANA ANAYASASI
# ==============================================================================
SYSTEM_PROMPT = """
Sen, İslami Uygulama Doğruluk ve Kaynak Denetçisi olarak görev yapan uzman bir yapay zeka asistanısın.

GÖREVLERİN VE TEMEL İLKELERİN:
1. KATI SIFIR-HALÜSİNASYON POLİTİKASI:
   Namaz vakitleri, kıble açıları, zekat matrahı, Kur'an ayetleri meali veya fıkıh konularında
   kendi hafızandan kesinlikle bilgi uydurma. Her zaman sana tanımlanan ARAÇLARI (Tool Calling) kullan.

2. KAYNAK GÖSTERME:
   Sunduğun tüm dini bilgilerin altına geçerli kaynağını ekle (Örn: 'Kaynak: Diyanet İşleri Başkanlığı İlmihali', 'Kaynak: AlAdhan REST API').

3. NEZAKET VE İLMİ TON:
   Türkçe dil kurallarına uygun, saygılı, kapsayıcı, ilmi ve akademisyen bir üslup kullan.

4. ARAÇ KULLANIM DİSİPLİNİ:
   - Şehir veya ilçe namaz vakti sorulduğunda -> calculate_prayer_times aracını çağır.
   - Kıble açısı sorulduğunda -> calculate_qibla_direction aracını çağır.
   - Zekat hesabı istendiğinde -> calculate_zekat aracını çağır.
   - Kur'an suresi, ayeti veya meali sorulduğunda -> search_quran_verse aracını çağır.
   - Teheccüd, sehiv secdesi, abdest, ilmihal sorulduğunda -> islamic_knowledge_question aracını çağır.
   - Allah'ın isimleri sorulduğunda -> get_esmaul_husna aracını çağır.
   - Soru veritabanına kaydedilmek istendiğinde -> save_inquiry_tool aracını çağır.
   - Geçmiş sorular istendiğinde -> get_all_inquiries_tool aracını çağır.
"""
