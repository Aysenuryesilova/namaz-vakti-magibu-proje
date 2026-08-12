# 🕌 İslami Uygulama Doğruluk & Kaynak Denetçisi (Ezan Vakti Agent)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-orange.svg)](https://ollama.ai/)
[![Model](https://img.shields.io/badge/Model-Qwen2.5--3B--Instruct-purple.svg)](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)
[![Relational DB](https://img.shields.io/badge/DB-SQLite3-lightgrey.svg)](https://www.sqlite.org/)
[![Interface](https://img.shields.io/badge/UI-Gradio_%26_Rich_CLI-brightgreen.svg)](https://gradio.app/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Yerel (Local) LLM (Ollama / Qwen2.5:3b) tabanlı, ReAct Tool-Calling destekli; Kur'an-ı Kerim 6.236 Ayet Meali & Diyanet İlmihali Vektör RAG Motoru, Sahih Hadisler, Zekat Hesaplama Makinesi, 81 İl ve 922 İlçe Namaz Vakitleri, Allah'ın 99 İsmi (Esmaül Hüsna), SQLite Kayıt Sistemi ve Docker Desteğini Kapsayan İslami Asistan**

---

## 📋 Ödev Gereksinimleri ve Karşılık Gelen Proje Dosyaları

| Ödevde İstenen Gereksinim | Karşılık Gelen Proje Dosyası ve İçeriği |
| :--- | :--- |
| **1. Temel Kod Yapısı (4-5 Dosya)** | `config.py`, `ollama_client.py`, `tools.py`, `database.py`, `agent_engine.py`, `islamic_rag.py`, `chat.py`, `app.py` |
| **2. Yerel Model Kullanımı (Ollama / LM Studio)** | `ollama_client.py` & `agent_engine.py` (Yerel Qwen2.5:3b modelinin Ollama REST API üzerinden çalıştırılması) |
| **3. Model Seçimi ve Araç Çağrısı (Tool Calling)** | `tools.py` & `agent_engine.py` (Namaz vakitleri, kıble açısı, zekat hesabı, Esmaül Hüsna vb. 11 harici aracın çağrılması) |
| **4. Sistem İstemi (System Prompt)** | `config.py` (`SYSTEM_PROMPT`: Sıfır halüsinasyon kuralı, Diyanet kaynak zorunluluğu, ilmi Türkçe tonu) |
| **5. Arama Sağlayıcı / İnternet Araması (Search Provider)** | `tools.py` (`web_search_tool`: DuckDuckGo API ile canlı İslami haber, duyuru ve fetva araması) |
| **6. Vektör Veri Tabanı / RAG (Vector Database / RAG)** | `islamic_rag.py` (`VectorRAGEngine`: Kur'an 6.236 Ayet ve Diyanet İlmihalinin TF-IDF & Kosinüs Benzerliği ile aranması) |
| **7. Hesap Makinesi / Kod Yürütme (Calculator)** | `tools.py` (`calculate_zekat`: Altın, nakit ve borçlar üzerinden fıkhi nisab & %2.5 zekat hesaplama makinesi) |
| **8. Veri Yazma & Okuma (Relational Database)** | `database.py` & `tools.py` (`save_inquiry_tool` ile SQLite DB'ye soru yazma & `get_all_inquiries_tool` ile okuma) |
| **9. Kullanıcı Arayüzü (User Interface)** | `chat.py` (Zengin CLI Terminal Arayüzü) & `app.py` (3 Sekmeli Modern Gradio Web UI) |

---

## 🛠️ Araç Envanteri (Tool Calling Inventory)

1. **`calculate_prayer_times(city, date_str)`**: Türkiye'nin 81 ili ve **TÜM 922 ilçesi** (*Sivas Gemerek*, *Kocaeli İzmit*, *Van Edremit*, *Muş Hasköy*, *İstanbul Kadıköy*, *Trabzon Of* vb.) veya dünyadaki tüm şehirler için Diyanet vakitlerini getirir.
2. **`get_current_location_prayer_times()`**: Kullanıcının IP/GPS konumunu otomatik tespit edip vakitleri basar.
3. **`calculate_qibla_direction(city)`**: Konumdan Kabe'ye olan kıble açısını *Great-Circle Bearing* trigonometrisiyle hesaplar.
4. **`calculate_zekat(gold_grams, silver_grams, cash_try, commercial_goods_try, debts_try)`**: Diyanet fıkhi esaslarına göre (80.18 gr altın nisabı) %2.5 zekat matrahını hesaplayan fıkhi hesap makinesi.
5. **`web_search_tool(query)`**: DuckDuckGo API üzerinden güncel İslami haber, duyuru ve Diyanet fetvalarını arar.
6. **`save_inquiry_tool(topic, question, user_name)`**: Kullanıcının fıkhi sorusunu SQLite veritabanına kaydeder (*Veri Yazma*).
7. **`get_all_inquiries_tool()`**: SQLite veritabanındaki kayıtlı geçmiş soruları listeler (*Veri Okuma*).
8. **`search_quran_verse(query_or_surah)`**: Kur'an 114 Sure, 6.236 Ayet, 504. genel ayet sırası, sure anlamları ve meallerini getirir.
9. **`islamic_knowledge_question(question)`**: Teheccüd, sehiv secdesi, abdest, gusül ve ilmihal konularını Vektör RAG motorundan yanıtlar.
10. **`get_esmaul_husna(query)`**: Allah'ın 99 İsmini (`elmelik`, `melik`, `er-rahman`, `rahman`, `es-selam`, `selam` vb. takı temizleme ile) getirir.
11. **`find_islamic_event(event_name, year)`**: Ramazan başlangıcı, bitişi, süresi ve Bayram tarihlerini hesaplar.
12. **`verify_hadith_source(hadith_query)`**: Hadis metnini Sahih-i Buhari dijital veritabanında doğrular.

---

## ⚡ Kurulum ve Çalıştırma

### Option A: Yerel Python Ortamı ile Çalıştırma

#### 1. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

#### 2. Yerel Modeli Başlatın (Ollama)
```bash
ollama pull qwen2.5:3b
ollama serve
```

#### 3. Zengin CLI Terminal Arayüzünü Çalıştırın
```bash
python chat.py
```

#### 4. Gradio Web Arayüzünü Çalıştırın (3 Sekmeli)
```bash
python app.py
```
Tarayıcınızda `http://127.0.0.1:7860` adresine gidin.

#### 5. Otomatik Benchmark Testini Çalıştırın
```bash
python generate_benchmark.py
```

---

### Option B: Docker ve Docker Compose ile Çalıştırma (Tek Komut)

Tüm sistemi ve Ollama bağımlılığını konteynerize olarak tek komutla başlatmak için:

```bash
docker-compose up --build
```
Web Arayüzü: `http://localhost:7860`

---

## 📊 Benchmark Test Sonuçları

`generate_benchmark.py` ile yapılan uçtan uca test sonuçları:

- **Toplam Test Sayısı:** 10
- **Başarılı Test Sayısı:** 10 (%100.0 Başarı Oranı)
- **SQLite DB Kayıt Kontrolü:** Tam Doğrulanmış Kayıt Okuma/Yazma

---

## 📜 Lisans

Bu proje **Apache 2.0 Lisansı** ile lisanslanmıştır. Serbestçe kullanılabilir, geliştirilebilir ve dağıtılabilir.
