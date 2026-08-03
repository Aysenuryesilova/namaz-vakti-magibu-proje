# 🕌 Namaz Vakti ve Fıkıh Asistanı (Magibu Yapay Zekâ Mimarisi)
## 📌 Ödev 1: Custom Chat Template (Jinja2) & Ödev 2: Tool-Calling Destekli Asistan

Bu proje, **Custom Jinja2 Chat Template** yapısını Hugging Face standartlarına göre tasarlayarak; bir Büyük Dil Modelinin (LLM) dış dünya ile (Public API ve yerel SQLite Veritabanı) iletişim kurabildiği, **%100 Halüsinasyon Önlemeli (Zero-Hallucination)** ve **Maliyetsiz İstemci (Zero-Cost Client)** mimarisine sahip uçtan uca bir AI Asistan sistemidir.

---

## 🎯 1. Senaryo Özeti ve Sistem Mimarisi

Asistanımız, kullanıcıların gün içerisinde ihtiyaç duyduğu dini bilgilere ve ibadet vakitlerine erişmesini sağlar:
1. **Harici Public API (Veri Okuma / Read)**: Aladhan REST API üzerinden belirttiğiniz şehir (ör: İstanbul, Ankara, Malatya) için Diyanet İşleri metoduna (Method 13) göre günlük ezan/namaz vakitlerini çeker.
2. **Yerel SQLite Veritabanı (Veri Yazma / Write)**: Kullanıcının sorduğu fıkhi soru ve fetva danışmalarını `user_inquiries` tablosuna kaydeder.
3. **Yerel SQLite Veritabanı (Veri Arama ve Listeleme / Read & Search)**: Veritabanındaki geçmiş soru kayıtlarını listeler veya istenen kelimeye göre arama yapar.

```
                  +-----------------------------------+
                  |   Kullanıcı Girdisi / UI (Gradio) |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Ödev 1: Custom Jinja2 Template   |
                  | (Role & Tools JSON Entegrasyonu)  |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |    Niyet Analizi & Tool Dispatch  |
                  +-----------------------------------+
                         /          |          \
                        /           |           \
                       v            v            v
        +------------------+ +---------------+ +------------------+
        | Aladhan Public   | | SQLite Write  | | SQLite Read/     |
        | API (Prayer Times)| | (save_inquiry)| | Search (inquiries)|
        +------------------+ +---------------+ +------------------+
                       \            |           /
                        \           |          /
                         v          v         v
                  +-----------------------------------+
                  |   Trace Log & Halüsinasyonsuz     |
                  |          Nihai Yanıt              |
                  +-----------------------------------+
```

---

## 🛠️ 2. Kullanılan Teknolojiler ve Ödev Gereksinimleri

| Bileşen | Kullanılan Teknoloji / Standart | Açıklama |
| :--- | :--- | :--- |
| **Chat Template** | Jinja2 (`src/chat_template.jinja`) | ChatML (`<|im_start|>role...`) standartında, `tools` şeması enjeksiyonlu ve `add_generation_prompt` destekli şablon. |
| **Harici API (Read)** | Aladhan REST API | Diyanet İşleri vakit hesaplama algoritmasını kullanan canlı REST servis. |
| **Veritabanı (Write/Read)** | SQLite (`src/islamic_assistant.db`) | Soruları `id`, `topic`, `question`, `user_name`, `created_at` yapısında saklayan yerel DB. |
| **Arayüz (UI)** | Gradio (`src/app.py`) | Sohbet ekranı, arka plan Trace Log izleyici ve canlı SQLite veritabanı paneli. |
| **Maliyetsiz İstemci** | Zero-Cost Client Architecture | Hugging Face Spaces üzerinde sunucu/GPU kısıtlamalarına takılmayan, %100 ücretsiz CPU uyumlu mimari. |

---

## 📜 3. Ödev 1: Custom Jinja2 Chat Template Yapısı

`src/chat_template.jinja` dosyamız, Hugging Face model standartlarıyla birebir uyumludur:

```jinja
{%- if messages[0]['role'] == 'system' -%}
    {{- "<|im_start|>system\n" + messages[0]['content'] | trim -}}
    {%- set loop_messages = messages[1:] -%}
{%- else -%}
    {{- "<|im_start|>system\nSen yetkin bir Dini İlimler ve Fıkıh Asistanısın..." -}}
    {%- set loop_messages = messages -%}
{%- endif -%}

{%- if tools is defined and tools -%}
    {{- "\n\nKullanılabilir Araçlar (Tools):\n" -}}
    {{- tools | tojson(indent=2) -}}
    {{- "\nFonksiyon çağırmak istediğinde çıktını şu formatta üret: <tool_call>{\"name\": \"fonksiyon_adi\", \"arguments\": {...}}</tool_call>" -}}
{%- endif -%}

{{- "<|im_end|>\n" -}}

{%- for message in loop_messages -%}
    {%- if message['role'] == 'user' -%}
        {{- "<|im_start|>user\n" + message['content'] | trim + "<|im_end|>\n" -}}
    {%- elif message['role'] == 'assistant' -%}
        {{- "<|im_start|>assistant\n" + message['content'] | trim + "<|im_end|>\n" -}}
    {%- elif message['role'] == 'tool_call' -%}
        {{- "<|im_start|>tool_call\n" + message['content'] | trim + "<|im_end|>\n" -}}
    {%- elif message['role'] in ['tool', 'tool_response'] -%}
        {{- "<|im_start|>tool_response\n" + message['content'] | trim + "<|im_end|>\n" -}}
    {%- endif -%}
{%- endfor -%}

{%- if add_generation_prompt -%}
    {{- "<|im_start|>assistant\n" -}}
{%- endif -%}
```

---

## ⚙️ 4. Ödev 2: Tool-Calling Trace Log Çıktısı Örneği

Uygulamanın çalıştırılması esnasında terminalde veya Gradio **⚙️ Tool Call & Jinja2 Trace Logları** sekmesinde üretilen gerçek iz kaydı:

```text
=== ÖDEV 1: CUSTOM JINJA2 CHAT TEMPLATE ÇIKTISI ===
<|im_start|>system
Sen yetkin bir Dini İlimler, Namaz Vakti ve Fıkıh Asistanısın. Harici araçlardan (API ve Veritabanı) gelen verilere %100 bağlı kalarak halüsinasyon görmeden yanıt verirsin.

Kullanılabilir Araçlar (Tools):
[
  {
    "function": {
      "description": "Belirtilen şehir için Diyanet İşleri metoduna göre günlük imsak, güneş, öğle, ikindi, akşam ve yatsı namaz vakitlerini çeker.",
      "name": "get_prayer_times",
      "parameters": {
        "properties": {
          "city": { "type": "string", "description": "Şehir adı (ör: Istanbul, Ankara, Malatya)" },
          "country": { "type": "string", "default": "Turkey", "description": "Ülke adı." }
        },
        "required": ["city"],
        "type": "object"
      }
    },
    "type": "function"
  }
]
Fonksiyon çağırmak istediğinde çıktını şu formatta üret: <tool_call>{"name": "fonksiyon_adi", "arguments": {...}}</tool_call><|im_end|>
<|im_start|>user
İstanbul için namaz vakitleri nedir?<|im_end|>
<|im_start|>assistant

=== ÖDEV 2: TOOL CALLING TRACE LOGS (ADIM ADIM ÇALIŞTIRMA İZİ) ===
[Döngü Adımı / Turn 1]
• Çağrılan Fonksiyon / Tool: get_prayer_times
• Gönderilen Argümanlar: {'city': 'Istanbul', 'country': 'Turkey'}
• Araçtan Dönen Gerçek Veri (Status): success
• Yanıt İçeriği: {'status': 'success', 'city': 'Istanbul', 'country': 'Turkey', 'date': '03 Aug 2026', 'prayer_times': {'İmsak': '04:11', 'Güneş': '05:55', 'Öğle': '13:15', 'İkindi': '17:10', 'Akşam': '20:25', 'Yatsı': '22:01'}, 'source': 'Aladhan Public API (Diyanet Metodu - Method 13)'}
```

---

## 🚀 5. Projeyi Yerelde Çalıştırma Adımları

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje.git
cd namaz-vakti-magibu-proje
```

### 2. Gerekli Bağımlılıkları Yükleyin
```bash
pip install -r src/requirements.txt
```

### 3. Uygulamayı Başlatın
```bash
python src/app.py
```
Tarayıcınızda `http://127.0.0.1:7860` adresine giderek Gradio arayüzüne erişebilirsiniz.

---

## 🌐 6. Canlı Demo & Bağlantılar

- **Hugging Face Space Live Demo**: [https://huggingface.co/spaces/Aysenur44/ezan-vakti-ai-assistant](https://huggingface.co/spaces/Aysenur44/ezan-vakti-ai-assistant)
- **GitHub Kaynak Kodu**: [https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje](https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje)
- **Hugging Face Profili**: [https://huggingface.co/Aysenur44](https://huggingface.co/Aysenur44)

---

## 🛡️ 7. Halüsinasyon Engelleme ve Maliyetsiz İstemci Yaklaşımı

- **Halüsinasyon Engelleme**: Asistan, kullanıcının namaz vakti veya kayıt sorularına asla kendi bilgisinden tahmin yürütmez. Yanıt metni strictly API'den veya SQLite tablosundan dönen Python nesnesinden formatlanır.
- **Sunucu Kısıtlamalarına Karşı Esneklik**: Hugging Face Spaces'in GPU/CPU uyku moduna takılmaması için Aladhan REST API ve SQLite motoru kullanılmıştır. Bu sayede canlı Space uygulaması 7/24 kesintisiz ve sıfır maliyetle çalışır.

---
*Geliştirici: Ayşe Nur Yeşilova | Magibu Yapay Zekâ Mimarisi Projesi*
