# 📂 Namaz Vakti & Fıkıh Asistanı - Proje ve Kaynak Kod Dokümantasyonu (`src/`)

Bu proje, **1. Ödev: Custom Chat Template (Jinja2)** ve **2. Ödev: Tool-Calling Destekli Asistan** çalışmalarının modüler kaynak kodlarını, şablonlarını, veritabanı sürücülerini ve canlı demo bağlantılarını içerir.

---

## 🚀 Canlı Demo ve Çalıştırma Bağlantıları

> 📌 **Önemli Not:** Hugging Face Space üzerindeki ücretsiz CPU/donanım ve kota sınırlamaları nedeniyle uygulamanın kesintisiz test edilebilmesi amacıyla **Google Colab Canlı Demo** ortamı oluşturulmuştur.

- 🟢 **Google Colab Canlı Demo (Önerilen Canlı Ortam):** [Colab Demo Notebook](https://colab.research.google.com/github/Aysenuryesilova/namaz-vakti-magibu-proje/blob/main/src/colab_demo.ipynb)
- 🟡 **Hugging Face Space:** [Aysenur44/ezan-vakti-ai-assistant](https://huggingface.co/spaces/Aysenur44/ezan-vakti-ai-assistant)
- 🔗 **GitHub Kaynak Kod Deposu:** [Aysenuryesilova/namaz-vakti-magibu-proje](https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje)

---

## 📑 Dosya Listesi ve Sorumluluk Haritası

| Dosya Adı                  | Görevi / Sorumluluğu                                                                                                                                                    | İlgili Ödev           |
| :------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------- |
| **`chat_template.jinja`**  | Modelin sistem, kullanıcı, asistan ve araç mesajlarını ayırt etmesini sağlayan ChatML standartlı Jinja2 şablonu.                                                        | **1. Ödev**           |
| **`test_template.py`**     | Jinja2 şablonunun bağımsız olarak ChatML çıktısı üretip üretmediğini doğrulayan test betiği.                                                                            | **1. Ödev**           |
| **`database.py`**          | SQLite veritabanı (`islamic_assistant.db`) bağlantısını açar, tabloları oluşturur/günceller; Veri Yazma (INSERT), Okuma (SELECT) ve Arama (LIKE) işlevlerini sağlar.    | **2. Ödev (DB)**      |
| **`tools.py`**             | Harici Aladhan Public REST API çağrısını (`get_prayer_times`) ve veritabanı fonksiyonlarını sarar. Model için OpenAI/HF uyumlu `TOOLS_SCHEMA` JSON tanımını barındırır. | **2. Ödev (Tools)**   |
| **`agent.py`**             | Jinja2 promptunu oluşturan, kullanıcının niyetini analiz ederek doğru aracı çağıran ve adım adım **Trace Log** kaydı tutan Ajan Motorudur (`IslamicToolCallingAgent`).  | **2. Ödev (Engine)**  |
| **`app.py`**               | Gradio uyumlu web arayüzüdür. Sohbet ekranı, Trace Log izleyici, canlı veritabanı paneli ve istemci ayarlarını sunar.                                                   | **2. Ödev (UI)**      |
| **`requirements.txt`**     | Projenin ihtiyaç duyduğu bağımlılık listesi (`gradio`, `requests`, `jinja2`).                                                                                           | **Ortak**             |
| **`islamic_assistant.db`** | Yerel SQLite veritabanı dosyası (`user_inquiries` tablosunu içerir).                                                                                                    | **2. Ödev (DB Data)** |

---

## 🧱 Modüler Veri Akışı ve Mimari

```text
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

## ⚙️ Arka Plan Tool-Call & Trace Log Çıktısı (Örnek Çalıştırma)

Uygulamanın test_template.py veya agent.py üzerinden çalıştırılması esnasında arka planda üretilen ham Trace Log kaydı:

=== ÖDEV 1: CUSTOM JINJA2 CHAT TEMPLATE ÇIKTISI ===
<|im_start|>system
Sen yetkin, güvenilir bir Dini İlimler, Namaz Vakti ve Fıkıh Asistanısın. Kullanılabilir araçları (tools) kullanarak halüsinasyon görmeden doğru yanıtlar üretirsin.

Kullanılabilir Araçlar (Tools):
[
{
"description": "Belirtilen şehir için namaz vakitlerini getirir.",
"name": "get_namaz_vakti",
"parameters": {
"properties": {
"sehir": {
"description": "Şehir adı (Örn: İstanbul)",
"type": "string"
}
},
"required": [
"sehir"
],
"type": "object"
}
}
]
Fonksiyon çağırmak istediğinde çıktını şu formatta üret: <tool_call>{"name": "fonksiyon_adi", "arguments": {...}}</tool_call><|im_end|>
<|im_start|>user
İstanbul için bugün akşam ezanı saat kaçta okunacak?<|im_end|>
<|im_start|>assistant
<tool_call>{"name": "get_namaz_vakti", "arguments": {"sehir": "İstanbul"}}</tool_call><|im_end|>
<|im_start|>tool_response
{"aksham": "20:15"}<|im_end|>
<|im_start|>assistant

=== ÖDEV 2: TOOL CALLING TRACE LOGS (ADIM ADIM ÇALIŞTIRMA İZİ) ===
[Döngü Adımı / Turn 1]
• Çağrılan Fonksiyon / Tool: get_prayer_times
• Gönderilen Argümanlar: {'city': 'Istanbul', 'country': 'Turkey'}
• Araçtan Dönen Gerçek Veri (Status): success
• Yanıt İçeriği: {'status': 'success', 'city': 'Istanbul', 'country': 'Turkey', 'prayer_times': {'İmsak': '04:11', 'Güneş': '05:55', 'Öğle': '13:15', 'İkindi': '17:10', 'Akşam': '20:25', 'Yatsı': '22:01'}}

## ⚡ Yerelde Çalıştırma Adımları

Kaynak kodları kendi bilgisayarınızda bağımsız olarak çalıştırmak için:

# 1. Proje dizinine geçin

cd src

# 2. Gerekli kütüphaneleri yükleyin

pip install -r requirements.txt

# 3. Jinja2 şablonunu test etmek için

python test_template.py

# 4. Gradio arayüzünü başlatmak için

python app.py

Uygulama [http://127.0.0.1:7860](http://127.0.0.1:7860) adresinde yerel sunucunuzda yayına girecektir.
