# 📂 Namaz Vakti & Fıkıh Asistanı - Kaynak Kod Klasörü (`src/`)

Bu klasör, **1. Ödev: Custom Chat Template (Jinja2)** ve **2. Ödev: Tool-Calling Destekli Asistan** projelerinin tüm modüler kaynak kodlarını, şablonlarını ve veritabanı sürücülerini içerir.

`src/` klasörü, dış bağımlılıklardan izole edilerek modüler yazılım mimarisi ilkesine göre tasarlanmıştır.

---

## 📑 Dosya Listesi ve Sorumluluk Haritası

| Dosya Adı | Görevi / Sorumluluğu | İlgili Ödev |
| :--- | :--- | :--- |
| **`chat_template.jinja`** | Modelin sistem, kullanıcı, asistan ve araç mesajlarını ayırt etmesini sağlayan Hugging Face standartlı Jinja2 şablonu. | **1. Ödev** |
| **`database.py`** | SQLite veritabanı (`islamic_assistant.db`) bağlantısını açar, tabloları oluşturur/günceller ve Veri Yazma (INSERT), Okuma (SELECT) ve Arama (LIKE) işlevlerini sağlar. | **2. Ödev (DB)** |
| **`tools.py`** | Harici Aladhan Public REST API çağrısını (`get_prayer_times`) ve veritabanı fonksiyonlarını sarar. Model için OpenAI/HF uyumlu `TOOLS_SCHEMA` JSON tanımını barındırır. | **2. Ödev (Tools)** |
| **`agent.py`** | Jinja2 promptunu oluşturan, kullanıcının niyetini analiz ederek doğru aracı çağıran ve adım adım **Trace Log** kaydı tutan Ajan Motorudur (`IslamicToolCallingAgent`). | **2. Ödev (Engine)** |
| **`app.py`** | Gradio 5/6 uyumlu, 4 sekmeli web arayüzüdür. Sohbet ekranı, Trace Log izleyici, canlı veritabanı paneli ve istemci token ayarlarını sunar. | **2. Ödev (UI & Space)** |
| **`requirements.txt`** | Projenin ihtiyaç duyduğu bağımlılık listesi (`gradio`, `requests`, `jinja2`). | **Ortak** |
| **`islamic_assistant.db`** | Yerel SQLite veritabanı dosyası (`user_inquiries` tablosunu içerir). | **2. Ödev (DB Data)** |

---

## 🧱 Modüler Veri Akışı ve Mimari

```
                                  +-----------------------+
                                  |    app.py (Gradio)    |
                                  +-----------------------+
                                              |
                                              v
                                  +-----------------------+
                                  |   agent.py (Agent)    |
                                  +-----------------------+
                                    /                   \
                                   /                     \
                                  v                       v
               +-----------------------+     +-----------------------+
               | chat_template.jinja   |     |    tools.py (Tools)   |
               | (Prompt Formatting)   |     +-----------------------+
               +-----------------------+      /                     \
                                             /                       \
                                            v                         v
                           +------------------------+   +------------------------+
                           |  Aladhan Public API    |   |  database.py (SQLite)  |
                           | (Prayer Times Service) |   | (user_inquiries Table) |
                           +------------------------+   +------------------------+
```

---

## 🔍 Detaylı Modül Açıklamaları

### 1. `chat_template.jinja` (Ödev 1)
- **Format**: ChatML (`<|im_start|>role\ncontent<|im_end|>\n`).
- **Dinamik Şema**: Jinja2 render motoruna `tools` nesnesi verildiğinde, kullanılabilir tüm araçların JSON şemasını sistem mesajının içerisine otomatik olarak enjekte eder.
- **Generation Prompt**: `add_generation_prompt=True` seçeneği aktif olduğunda, modelin cevaba başlamasını sağlayan `<|im_start|>assistant\n` etiketini üretir.

### 2. `database.py` (Ödev 2 - Veritabanı Katmanı)
- `init_database()`: Veritabanı yoksa oluşturur. Tabloda `user_name` gibi sütunlar eksikse otomatik migrasyon (ALTER TABLE) yapar.
- `save_inquiry(topic, question, user_name)`: [WRITE] Yeni bir fıkhi soru kaydeder.
- `get_all_inquiries()`: [READ ALL] Tüm kayıtları en yeniden en eskiye sıralayarak çeker.
- `search_inquiries(keyword)`: [READ SEARCH] Konu veya soru metninde kelime bazlı arama yapar.

### 3. `tools.py` (Ödev 2 - Araçlar ve JSON Şeması)
- `get_prayer_times(city, country)`: Aladhan Public REST API'sine `https://api.aladhan.com/v1/timingsByCity` HTTP GET isteği gönderir (Method 13 - Diyanet İşleri Başkanlığı metodu).
- `TOOLS_SCHEMA`: Modelin fonksiyon isimlerini, açıklamalarını ve beklediği argüman türlerini öğrenmesini sağlayan JSON listesi.

### 4. `agent.py` (Ödev 2 - Ajan Motoru)
- `IslamicToolCallingAgent.run(user_query)`:
  1. Girdiyi alır ve `chat_template.jinja` ile ChatML promptuna dönüştürür.
  2. Niyet analizi (Intent Recognition) ile doğru fonksiyonu seçer.
  3. Araç fonksiyonunu çalıştırıp gerçek veriyi alır.
  4. Yanıtı **sadece bu verilere** dayandırarak halüsinasyonu %100 engeller.
  5. Adım adım çalıştırma izini (`trace_logs`) dizi olarak döndürür.

### 5. `app.py` (Ödev 2 - Canlı Web Arayüzü)
- Gradio `gr.Blocks` yapısı ve `type="messages"` formatı kullanılarak tasarlanmıştır.
- Sekme 1: Sohbet Arayüzü (Örnek butonlar ile hızlı test).
- Sekme 2: Tool Call & Jinja2 Trace Logları (Ödev tesliminde ekran görüntüsü alınacak alan).
- Sekme 3: Canlı Veritabanı Görüntüleyici ve Kelime Arama Paneli.
- Sekme 4: İstemci Token Ayarları (Hugging Face Spaces üzerinde sıfır maliyetle çalışmayı sağlayan esnek istemci seçeneği).

---

## ⚡ Yerel Test Talimatı

Kaynak kodları bağımsız olarak çalıştırmak için `src/` klasörüne girip `app.py` dosyasını başlatabilirsiniz:

```bash
cd src
python app.py
```
Uygulama `http://127.0.0.1:7860` adresinde yerel sunucunuzda yayına girecektir.
