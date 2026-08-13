# 🕌 İslami Uygulama Doğruluk & Kaynak Denetçisi (Ezan Vakti Agent)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-orange.svg)](https://ollama.ai/)
[![Model](https://img.shields.io/badge/Model-Qwen2.5--3B--Instruct-purple.svg)](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)
[![TF-IDF RAG](https://img.shields.io/badge/RAG-Math_TF--IDF_%26_Cosine-emerald.svg)]()
[![Relational DB](https://img.shields.io/badge/DB-SQLite3-lightgrey.svg)](https://www.sqlite.org/)
[![Interface](https://img.shields.io/badge/UI-Gradio_%26_Rich_CLI-brightgreen.svg)](https://gradio.app/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Yerel (Local) LLM (Ollama / Qwen2.5:3b) tabanlı, ReAct Tool-Calling destekli; Matematiksel TF-IDF & Kosinüs Benzerliği (Cosine Similarity) Vektör RAG Motoru (Kur'an 6.236 Ayet Meali & Diyanet İlmihali 200+ Vektör Dokümanı), Sahih Hadisler, Zekat Hesaplama Makinesi, 81 İl ve 922 İlçe Namaz Vakitleri, Allah'ın 99 İsmi (Esmaül Hüsna), SQLite Kayıt Sistemi ve Docker Desteğini Kapsayan Kurumsal İslami Asistan**

---

## 📋 Ödev Gereksinimleri ve Karşılık Gelen Proje Dosyaları

| Ödevde İstenen Gereksinim | Karşılık Gelen Proje Dosyası ve İçeriği |
| :--- | :--- |
| **1. Temel Kod Yapısı (4-5 Dosya)** | `config.py`, `ollama_client.py`, `tools.py`, `database.py`, `agent_engine.py`, `islamic_rag.py`, `chat.py`, `app.py` |
| **2. Yerel Model Kullanımı (Ollama / LM Studio)** | `ollama_client.py` & `agent_engine.py` (Yerel Qwen2.5:3b modelinin Ollama REST API üzerinden çalıştırılması) |
| **3. Model Seçimi ve Araç Çağrısı (Tool Calling)** | `tools.py` & `agent_engine.py` (Namaz vakitleri, kıble açısı, zekat hesabı, Esmaül Hüsna vb. 11 harici aracın çağrılması) |
| **4. Sistem İstemi (System Prompt)** | `config.py` (`SYSTEM_PROMPT`: Sıfır halüsinasyon kuralı, Diyanet kaynak zorunluluğu, ilmi Türkçe tonu) |
| **5. Arama Sağlayıcı / İnternet Araması (Search Provider)** | `tools.py` (`web_search_tool`: DuckDuckGo API ile canlı İslami haber, duyuru ve fetva araması) |
| **6. Vektör Veri Tabanı / RAG (Vector Database / RAG)** | `islamic_rag.py` (`VectorRAGEngine`: Kur'an 6.236 Ayet ve Diyanet İlmihalinin matematiksel TF-IDF & Kosinüs Benzerliği ile 201+ dokümanda aranması) |
| **7. Hesap Makinesi / Kod Yürütme (Calculator)** | `tools.py` (`calculate_zekat`: Altın, nakit ve borçlar üzerinden fıkhi nisab & %2.5 zekat hesaplama makinesi) |
| **8. Veri Yazma & Okuma (Relational Database)** | `database.py` & `tools.py` (`save_inquiry_tool` ile SQLite DB'ye soru yazma & `get_all_inquiries_tool` ile okuma) |
| **9. Kullanıcı Arayüzü (User Interface)** | `chat.py` (Zengin CLI Terminal Arayüzü) & `app.py` (3 Sekmeli Modern Gradio Web UI) |

---

## 🏛️ Mimari Tasarım ve Temiz Kod Prensipleri (Clean Architecture)

Projede `ollama_asistan` şablonundaki temel mantık korunmuş; ancak kod okunabilirliğini ve sürdürülebilirliğini artırmak adına **Clean Architecture (Single Responsibility Principle)** uygulanarak modülerleştirilmiştir:

- **`config.py`**: Model parametreleri, zamanaşımı ve System Prompt anayasası.
- **`ollama_client.py`**: 30 sn timeout ve 2x retry mekanizması ile güçlendirilmiş Ollama REST API istemcisi.
- **`agent_engine.py`**: ReAct döngüsü, araç yürütme ve NLU Fallback mantığı.
- **`tools.py`**: 11 işlevsel aracın (Namaz, Kıble, Zekat, Hadis, Esma vb.) mantıksal motoru.
- **`islamic_rag.py`**: TF-IDF & Kosinüs Benzerliği vektör arama motoru.
- **`database.py`**: SQLite3 ilişkisel veritabanı CRUD katmanı.
- **`chat.py` & `app.py`**: Rich CLI Terminal ve Gradio Web UI sunum katmanları.

---

## 🔬 Matematiksel TF-IDF & Kosinüs Benzerlikli RAG Mimarisi (ChromaDB / PGVector Karşılaştırması)

Sistemdeki RAG mimarisi (`islamic_rag.py`) ChromaDB veya PGVector gibi C++ derleyici bağımlılığı olan harici vektör veritabanlarına ihtiyaç duymadan yerel ortamda anında çalışan **Matematiksel TF-IDF Vektör Uzayı** kullanır:

1. **Neden Saf Python TF-IDF RAG?**
   - **Sıfır Bağımlılık (Zero-Dependency):** Yerel sistemde SQLite/ChromaDB sürücü uyumsuzluğu veya C++ derleyici hatası yaşanmasını engeller.
   - **%100 Deterministik:** Kelime frekansı ve kosinüs açısı üzerinden matematiksel olarak doğrulanabilir sonuç verir.
   - **ChromaDB / PGVector Uyumluluğu:** `search_rag(query)` arabirimi standardize edildiği için istendiğinde arkasına ChromaDB / PGVector sürücüsü saniyeler içinde takılabilir.

2. **Formülasyon:**
   - **Terim Frekansı (Term Frequency - TF):**
     $$TF(w, d) = \frac{\text{Kelime } w \text{'nin Doküman } d \text{ İçindeki Frekansı}}{\text{Dokümandaki Toplam Kelime Sayısı}}$$

   - **Ters Doküman Frekansı (Inverse Document Frequency - IDF):**
     $$IDF(w) = \log\left(1.0 + \frac{N}{1.0 + DF(w)}\right)$$
     *(N: Toplam doküman sayısı (201+), DF(w): Kelimenin geçtiği doküman sayısı)*

   - **TF-IDF Ağırlık Çarpımı & Vektörleşme:**
     $$V(w, d) = TF(w, d) \times IDF(w)$$

   - **Kosinüs Benzerliği Açısı (Cosine Similarity) & Eşik Filtresi:**
     $$\text{Cosine Similarity}(\vec{q}, \vec{d}) = \frac{\vec{q} \cdot \vec{d}}{\|\vec{q}\| \|\vec{d}\|}$$
     *(Eşik Değeri: Similarity $\ge 0.05$ altındaki alakasız sonuçlar kesinlikle elenir).*

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
9. **`islamic_knowledge_question(question)`**: Teheccüd, sehiv secdesi, abdest, gusül ve ilmihal konularını TF-IDF Vektör RAG motorundan yanıtlar.
10. **`get_esmaul_husna(query)`**: Allah'ın 99 İsmini (`elmelik`, `melik`, `er-rahman`, `rahman`, `es-selam`, `selam` vb. takı temizleme ile) getirir.
11. **`find_islamic_event(event_name, year)`**: Ramazan başlangıcı, bitişi, süresi ve Bayram tarihlerini hesaplar.
12. **`verify_hadith_source(hadith_query)`**: Hadis metnini Sahih-i Buhari dijital veritabanında doğrular.

---

## 🖥️ Detaylı Adım Adım Tool Call Trace Logları

### 1. Vektör RAG Arama Adımı (TF-IDF & Cosine Similarity)
```text
Kullanıcı > Abdestin farzları nelerdir?

  🔧 [ARAÇ ÇAĞRILDI]: islamic_knowledge_question({'question': 'Abdestin farzları nelerdir?'})
  📥 [ARAÇ ÇIKTISI]:
📖 **Diyanet İlmihali Vektör Bilgi Deposu Yanıtı**:

• 1. Abdestin Farzları (4 Farz): - Yüzü bir kere yıkamak (Saç bitiminden çene altına, kulak yumuşağına kadar). - Kolları dirseklerle birlikte bir kere yıkamak. - Başın en az dörtte birini ıslak elle meshetmek. - Ayakları topuklarla birlikte bir kere yıkamak.
  🔗 Kaynak: Diyanet İşleri Başkanlığı İlmihali (Bölüm 2: TAHARET VE TEMİZLİK FIKHI)
```

---

### 2. Zekat Fıkhi Hesaplama Adımı (Hesap Makinesi)
```text
Kullanıcı > 100 gram altınım ve 50000 TL nakdim var zekat düşer mi?

  🔧 [ARAÇ ÇAĞRILDI]: calculate_zekat({'gold_grams': 100.0, 'cash_try': 50000.0})
  📥 [ARAÇ ÇIKTISI]:
💰 **Diyanet Fıkhi Zekat & Nisab Hesaplama Raporu**
  • Toplam Varlık (Brüt)  : 350,000.00 TL
    - Altın (100.0 gr)     : 300,000.00 TL
    - Nakit Varlık       : 50,000.00 TL
  • Net Zekat Matrahı     : 350,000.00 TL
  • Asgari Nisab Miktarı  : 240,540.00 TL (80.18 gr Altın X 3000 TL)
--------------------------------------------------
✅ **DURUM: ZEKAT VERMEK FARZDIR.**
💵 **Ödenmesi Gereken Zekat Tutarı (%2.5 / 40'ta 1): 8,750.00 TL**

🔗 Kaynak: Diyanet İşleri Başkanlığı Din İşleri Yüksek Kurulu Zekat Rehberi
```

---

### 3. Namaz Vakti API (İlçe Geocoding Adımı)
```text
Kullanıcı > Sivas Gemerek için namaz vakitleri nelerdir?

  🔧 [ARAÇ ÇAĞRILDI]: calculate_prayer_times({'city': 'Sivas Gemerek'})
  📥 [ARAÇ ÇIKTISI]:
📍 Konum: Gemerek, Sivas (39.1834, 36.0719) | Tarih: 2026-08-12
✅ Diyanet İşleri Başkanlığı Ezan Vakitleri:
   • İmsak (Sahur) : 04:12
   • Güneş        : 05:46
   • Öğle          : 12:58
   • İkindi        : 16:47
   • Akşam (İftar) : 19:59
   • Yatsı         : 21:26

🔗 Kaynak: Diyanet Takvimi (AlAdhan REST API)
```

---

### 4. Esmaül Hüsna (Esnek Ön Takı Temizleme Adımı)
```text
Kullanıcı > es-selam ne demek?

  🔧 [ARAÇ ÇAĞRILDI]: get_esmaul_husna({'query': 'selam'})
  📥 [ARAÇ ÇIKTISI]:
✨ **Esmaül Hüsna**: 'El-Selam'
   • Türkçe Anlamı: Kullanı selamlatan, her türlü tehlikeden selamete çıkaran, esenlik veren.
```

---

### 5. SQLite Veritabanı Soru Kaydetme Adımı (Veri Yazma)
```text
Kullanıcı > Bu soruyu veritabanına kaydet: Sehiv secdesi hangi durumlarda yapılır?

  🔧 [ARAÇ ÇAĞRILDI]: save_inquiry_tool({'topic': 'Namaz', 'question': 'Sehiv secdesi hangi durumlarda yapılır?'})
  📥 [ARAÇ ÇIKTISI]:
💾 **SQLite Veritabanı Kayıt Başarılı**: Soru '#1' ID ile 'Namaz' konusuna eklendi.
```

---

## 📊 Sıkı Benchmark Test Metodolojisi & Sonuçları

`generate_benchmark.py` scriptindeki test kriterleri tamamen sıkılaştırılmış ve çift doğrulamalı hale getirilmiştir:

- **Başarı Kriteri 1:** Beklenen araç `test["expected_tool"] in called_tools` şeklinde **gerçekten çağrılmış olmalıdır**.
- **Başarı Kriteri 2:** Üretilen yanıt içinde beklenen doğrusal fıkhi kelime (`'İmsak'`, `'151.56'`, `'FARZDIR'`, `'El-Melik'`, `'114'`) **kesinlikle bulunmalıdır**.

```text
==================================================================
 SIKI BENCHMARK SONUÇLARI:
  • Toplam Test Sayısı   : 10
  • Kesin Başarılı       : 10
  • Gerçek Başarı Oranı  : %100.0
==================================================================
```

---

## ⚡ Kurulum ve Çalıştırma

### 1. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 2. Yerel Modeli Başlatın (Ollama)
```bash
ollama pull qwen2.5:3b
ollama serve
```

### 3. Zengin CLI Terminal Arayüzünü Çalıştırın
```bash
python chat.py
```

### 4. Gradio Web Arayüzünü Çalıştırın (3 Sekmeli)
```bash
python app.py
```
Tarayıcınızda `http://127.0.0.1:7860` adresine gidin.

### 5. Sıkı Benchmark Testini Çalıştırın
```bash
python generate_benchmark.py
```

---

## 📜 Lisans

Bu proje **Apache 2.0 Lisansı** ile lisanslanmıştır. Serbestçe kullanılabilir, geliştirilebilir ve dağıtılabilir.
