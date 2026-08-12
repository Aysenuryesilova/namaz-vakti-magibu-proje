# 🕌 İslami Uygulama Doğruluk & Kaynak Denetçisi (Ezan Vakti Agent)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-orange.svg)](https://ollama.ai/)
[![Model](https://img.shields.io/badge/Model-Qwen2.5--3B--Instruct-purple.svg)](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)
[![Vector DB](https://img.shields.io/badge/RAG-Vector_Space_Cosine_Similarity-emerald.svg)]()
[![Relational DB](https://img.shields.io/badge/DB-SQLite3-lightgrey.svg)](https://www.sqlite.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue.svg)](https://www.docker.com/)
[![Interface](https://img.shields.io/badge/UI-Gradio_%26_Rich_CLI-brightgreen.svg)](https://gradio.app/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Yerel (Local) LLM (Ollama / Qwen2.5:3b) tabanlı, ReAct Tool-Calling destekli; Kur'an-ı Kerim 6.236 Ayet Meali & Diyanet İlmihali Vektör RAG Motoru, Sahih Hadisler, Zekat Hesaplama Makinesi, 81 İl ve 922 İlçe Namaz Vakitleri, Allah'ın 99 İsmi (Esmaül Hüsna Esnek Prefix Temizleme), SQLite Kayıt Sistemi, Sohbet Bağlamı Belleği ve Docker Desteğini Kapsayan Kurumsal İslami Asistan**

Bu proje; İslami uygulamalar ve kullanıcılar için özel olarak geliştirilmiş **Seviye 5 (Eksiksiz & İleri Seviye)** bir denetçi ve rehber asistandır.

---

## 📋 Ödev Gereksinimleri ve Uygulama Tablosu

| Ödev Kriteri | Durum | Teknik Gerçekleştirim Detayı |
| :--- | :---: | :--- |
| **1. Temel Kod Yapısı (4-5 Dosya)** | ✅ %100 | `config.py`, `ollama_client.py`, `tools.py`, `database.py`, `agent_engine.py`, `islamic_rag.py`, `chat.py`, `app.py` |
| **2. Yerel Model (Ollama / LM Studio)** | ✅ %100 | `ollama_client.chat(model='qwen2.5:3b', tools=...)` Python SDK entegrasyonu + Akıllı NLU Fallback Motoru |
| **3. Sistem İstemi (System Prompt)** | ✅ %100 | `config.py`: Rol, sınırlar, sıfır halüsinasyon kuralı, Diyanet kaynak zorunluluğu, ilmi Türkçe tonu |
| **4. İnternet Araması (Search Provider)** | ✅ %100 | `web_search_tool`: DuckDuckGo API ile canlı İslami haber, diyanet duyurusu ve fetva araması |
| **5. Senaryoya Özel Araçlar (Tool Calling)** | ✅ %100 | **11 Adet Özel Araç:** Namaz Vakitleri, Kıble Açısı, Zekat Hesabı, Kur'an Meali, Hadis Doğrulama vb. |
| **6. Vektör RAG Motoru** | ✅ %100 | `islamic_rag.py`: TF-IDF ve Kosinüs Benzerliği ile Kur'an 6.236 Ayet ve Diyanet İlmihali Vektör Araması |
| **7. Kod Yürütme / Hesap Makinesi** | ✅ %100 | `calculate_zekat`: Altın, gümüş, nakit, ticari mal ve borçlar üzerinden fıkhi nisab & %2.5 zekat hesaplama |
| **8. Veri Yazma & Okuma (SQLite DB)** | ✅ %100 | `database.py`: `save_inquiry_tool` (Veri Yazma) & `get_all_inquiries_tool` (Veri Okuma) |
| **9. Sohbet Bağlam Belleği** | ✅ %100 | `agent_engine.py`: `conversation_history` ve `last_mentioned_city` ile konum hatırlama (Multi-turn Chat) |
| **10. Arayüz (UI) & Konteynerizasyon** | ✅ %100 | Zengin Terminal CLI (`chat.py`) + 3 Sekmeli Gradio Web UI (`app.py`) + `Dockerfile` & `docker-compose.yml` |
| **11. Benchmark & Test Engine** | ✅ %100 | Uçtan Uca Otomatik Benchmark Scripti (`generate_benchmark.py`) ile 10/10 (%100) test başarısı |

---

## 🛠️ Araç Envanteri (Tool Calling Inventory)

1. **`calculate_prayer_times(city, date_str)`**: Türkiye'nin 81 ili ve **TÜM 922 ilçesi** (*Sivas Gemerek*, *Kocaeli İzmit*, *Van Edremit*, *Muş Hasköy*, *İstanbul Kadıköy*, *Trabzon Of* vb.) veya dünyadaki tüm şehirler için Diyanet vakitlerini getirir.
2. **`get_current_location_prayer_times()`**: Kullanıcının IP/GPS konumunu otomatik tespit edip vakitleri basar.
3. **`calculate_qibla_direction(city)`**: Konumdan Kabe'ye olan kıble açısını *Great-Circle Bearing* trigonometrisiyle hesaplar (Sohbet belleğindeki son şehri hatırlar).
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

## 🖥️ Örnek Kullanım ve Sohbet Bağlamı Logları

```text
==================================================================
  İSLAMİ UYGULAMA DOĞRULUK & KAYNAK DENETÇİSİ (EZAN VAKTİ AGENT)
==================================================================

Kullanıcı > İstanbul için namaz vakitleri nelerdir?

  🔧 [ARAÇ ÇAĞRILDI]: calculate_prayer_times({'city': 'İstanbul'})
📍 Konum: İstanbul (41.0082, 28.9784) | Tarih: 2026-08-12
✅ Diyanet İşleri Başkanlığı Ezan Vakitleri:
   • İmsak (Sahur) : 04:22
   • Akşam (İftar) : 20:23
   • Yatsı         : 21:52

-----------------------------------------------------------------

Kullanıcı > peki kıble açısı nedir? (Şehir belirtilmedi, hafızadaki İstanbul hatırlandı)

  🔧 [ARAÇ ÇAĞRILDI]: calculate_qibla_direction({'city': 'İstanbul'})
🧭 Kıble Açısı Sonucu:
   • Konum        : İstanbul (41.0082° K, 28.9784° D)
   • Kıble Açısı  : 151.56° (Gerçek Kuzeyden Saat Yönünde)
-----------------------------------------------------------------

Kullanıcı > es-selam ne demek?

  🔧 [ARAÇ ÇAĞRILDI]: get_esmaul_husna({'query': 'selam'})
✨ **Esmaül Hüsna**: 'El-Selam'
   • Türkçe Anlamı: Kullanı selamlatan, her türlü tehlikeden selamete çıkaran, esenlik veren.
```

---

## 📊 Benchmark Test Sonuçları

`generate_benchmark.py` ile yapılan uçtan uca test sonuçları:

- **Toplam Test Sayısı:** 10
- **Başarılı Test Sayısı:** 10 (%100.0 Başarı Oranı)
- **SQLite DB Kayıt Kontrolü:** Tam Doğrulanmış Kayıt Okuma/Yazma

---

## 📜 Lisans

Bu proje **Apache 2.0 Lisansı** ile lisanslanmıştır. Serbestçe kullanılabilir, geliştirilebilir ve dağıtılabilir.
