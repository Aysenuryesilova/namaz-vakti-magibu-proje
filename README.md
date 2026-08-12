# 🕌 Namaz Vakti ve Fıkıh Asistanı (Magibu Yapay Zekâ Mimarisi)

> **Custom Chat Template (Jinja2), Tool-Calling Destekli Asistan, HuggingFace Gradio UI ve Yerel LLM Destekli İslami Uygulama Doğruluk ve Kaynak Denetçisi Agent**

Bu proje; Custom Jinja2 Chat Template yapısını Hugging Face standartlarına göre tasarlayarak; bir Büyük Dil Modelinin (LLM) dış dünya ile (Public API, ChromaDB Vektör Veritabanı ve yerel SQLite Veritabanı) iletişim kurabildiği, **%100 Halüsinasyon Önlemeli (Zero-Hallucination)** ve **Maliyetsiz İstemci (Zero-Cost Client)** mimarisine sahip uçtan uca bir AI Asistan ve Denetçi sistemidir.

---

## 🎯 1. Senaryo Özeti ve Sistem Mimarisi

Sistem iki ana çalıştırma modundan oluşmaktadır:

### A. Web / Gradio Arayüzü & Jinja2 Template (`src/`)
1. **Harici Public API (Veri Okuma / Read)**: Aladhan REST API üzerinden belirttiğiniz şehir (ör: İstanbul, Ankara, Malatya) için Diyanet İşleri metoduna (Method 13) göre günlük ezan/namaz vakitlerini çeker.
2. **Yerel SQLite Veritabanı (Veri Yazma / Write)**: Kullanıcının sorduğu fıkhi soru ve fetva danışmalarını `user_inquiries` tablosuna kaydeder.
3. **Yerel SQLite Veritabanı (Veri Arama ve Listeleme / Read & Search)**: Veritabanındaki geçmiş soru kayıtlarını listeler veya istenen kelimeye göre arama yapar.

### B. Yerel ReAct Denetçi Agent & ChromaDB RAG (`islami_denetci_asistan/`)
1. **81 İl ve TÜM 922 İlçe Namaz Vakitleri**: Türkiye'nin 81 ili ve istisnasız tüm ilçeleri (*Van Edremit, Muş Hasköy, Sivas Şarkışla, Kadıköy, İnegöl, Of, Cizre vb.*) için canlı Diyanet vakitleri ve Kıble açısı hesabı.
2. **Otomatik IP/GPS Konum Tespiti**: Kullanıcının konumunu otomatik algılayarak en yakın ezan vakitlerini sunma.
3. **Kur'an-ı Kerim Modülü**: 114 Sure, 6.236 Ayet, surelerin Türkçe anlamları, Diyanet mealleri ve nüzul açıklamaları.
4. **Hadisler ve Raviler Modülü**: Sahih-i Buhari hadisleri, senet ve ravi doğrulaması.
5. **Esmaül Hüsna Modülü**: Allah'ın 99 İsmi ve tüm Türkçe anlamları.
6. **Kelam, Hikmet ve İman Delilleri (RAG)**: Nizam ve gaye delili (fine-tuning), Kur'an bilimsel mucizeleri (*Zariyat 47, Nebe 6-7, Enbiya 30*), Teheccüd ve Sehiv Secdesi rehberi.

```
                  +-----------------------------------+
                  | Kullanıcı Girdisi / UI & Terminal |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  | Ödev 1: Custom Jinja2 Template /  |
                  | ReAct Loop (Role & Tools JSON)    |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |   Niyet Analizi & Tool Dispatch   |
                  +-----------------------------------+
                   /         |           |          \
                  /          |           |           \
                 v           v           v            v
        +--------------+ +-----------+ +------------+ +----------------+
        | Aladhan API  | | SQLite DB | | ChromaDB   | | Open-Meteo     |
        | (Vakitler)   | | (Sorular) | | RAG (Fıkıh)| | (81 İl/İlçe)   |
        +--------------+ +-----------+ +------------+ +----------------+
                 \           |           |            /
                  \          |           |           /
                   v         v           v          v
                  +-----------------------------------+
                  | Trace Log & Halüsinasyonsuz Yanıt |
                  +-----------------------------------+
```

---

## 🛠️ 2. Kullanılan Teknolojiler ve Proje Mimarisi

| Bileşen | Kullanılan Teknoloji / Standart | Açıklama |
| :--- | :--- | :--- |
| **Chat Template** | Jinja2 (`src/chat_template.jinja`) | ChatML (`<|im_start|>role...`) standartında, `tools` şeması enjeksiyonlu ve `add_generation_prompt` destekli şablon. |
| **Denetçi Agent** | Ollama ReAct (`islami_denetci_asistan/chat.py`) | `qwen2.5:3b` yerel sohbet modeli ve `embeddinggemma:latest` ile desteklenen denetçi. |
| **Harici API (Read)** | Aladhan REST API & Open-Meteo | Diyanet İşleri vakit hesaplama algoritması ve tüm 922 ilçe geocoding servisi. |
| **Vektör Veritabanı (RAG)**| ChromaDB (`islami_denetci_asistan/islamic_rag.py`) | Diyanet İlmihali, Tefsirler, Akaid, Sehiv Secdesi ve Kelam delillerini barındıran RAG katmanı. |
| **SQLite Veritabanı** | SQLite (`src/islamic_assistant.db`) | Soruları `id`, `topic`, `question`, `user_name`, `created_at` yapısında saklayan DB. |
| **Arayüz (UI)** | Gradio (`src/app.py`) | Sohbet ekranı, arka plan Trace Log izleyici ve canlı SQLite veritabanı paneli. |

---

## 📂 3. Klasör ve Proje Yapısı

```
namaz-vakti-magibu-proje/
│
├── islami_denetci_asistan/           # 🕌 Yerel LLM ReAct Denetçi Asistan Modülü
│   ├── config.py                     # Sistem İstemi (System Prompt), model ayarları ve güncel yıl
│   ├── ollama_client.py              # Ollama REST API (/api/chat, /api/embed) sarmalayıcısı
│   ├── tools.py                      # 8 Adet Doğrulama Aracı (81 il + 922 ilçe, Kur'an, Hadis, Esmaül Hüsna)
│   ├── islamic_rag.py                # ChromaDB Vektör Veritabanı ve RAG arama katmanı
│   ├── index_islamic.py              # İlmihal metinleri ve kitapları veritabanına yükleyici script
│   ├── olcum_karsilastirma.py        # Retriever ve Embedding başarı ölçüm testi
│   ├── chat.py                       # ReAct Terminal sohbet döngüsü
│   ├── diyanet_ilmihali.txt          # Kapsamlı Akaid, Taharet, Namaz, Oruç, Zekat ve Kelam dokümanı
│   └── requirements.txt              # Python kütüphaneleri (adhanpy, hijri-converter, chromadb, requests)
│
├── src/                              # 🌐 Gradio UI, Jinja2 Template & SQLite Modülü
│   ├── app.py                        # Gradio Web Arayüzü
│   ├── chat_template.jinja           # Ödev 1: Custom Jinja2 Chat Template
│   ├── islamic_assistant.db          # SQLite Soru-Cevap veritabanı
│   └── requirements.txt              # Gradio web bağımlılıkları
│
└── README.md                         # Proje Dokümantasyonu
```

---

## 📜 4. Ödev 1: Custom Jinja2 Chat Template Yapısı

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

## 🚀 5. Projeyi Çalıştırma Adımları

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje.git
cd namaz-vakti-magibu-proje
```

### 2. Gradio Web Arayüzünü Çalıştırma
```bash
pip install -r src/requirements.txt
python src/app.py
```
Tarayıcınızda `http://127.0.0.1:7860` adresinden Gradio arayüzüne erişebilirsiniz.

### 3. Yerel İslami Denetçi Terminal Agent'ını Çalıştırma
```bash
cd islami_denetci_asistan
pip install -r requirements.txt
ollama pull qwen2.5:3b
python chat.py
```

### 4. Kendi Kitap veya Dokümanlarınızı ChromaDB'ye İndeksleme
```bash
python index_islamic.py --file diyanet_ilmihali.txt
```

---

## 🌐 6. Canlı Demo & Bağlantılar

- **Hugging Face Space Live Demo**: [https://huggingface.co/spaces/Aysenur44/ezan-vakti-ai-assistant](https://huggingface.co/spaces/Aysenur44/ezan-vakti-ai-assistant)
- **GitHub Kaynak Kodu**: [https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje](https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje)
- **Hugging Face Profili**: [https://huggingface.co/Aysenur44](https://huggingface.co/Aysenur44)
- **Google Colab Canlı Demo**: [https://colab.research.google.com/github/Aysenuryesilova/namaz-vakti-magibu-proje/blob/main/src/colab_demo.ipynb](https://colab.research.google.com/github/Aysenuryesilova/namaz-vakti-magibu-proje/blob/main/src/colab_demo.ipynb)

---

## 🛡️ 7. Halüsinasyon Engelleme ve Sıfır Maliyet Yaklaşımı

- **Halüsinasyon Engelleme**: Asistan; namaz vakitleri, kıble açısı, Kur'an mealleri veya ilmihal sorularında kendi zihninden uydurma yapmaz. Yanıtlar strictly API ve ChromaDB RAG nesnelerinden formatlanır.
- **Maliyetsiz İstemci Mimarisi**: Hugging Face Spaces üzerinde GPU/CPU kısıtlamalarına takılmadan Aladhan REST API ve SQLite/ChromaDB motoruyla kesintisiz ve %100 ücretsiz çalışır.

---
*Geliştirici: Ayşe Nur Yeşilova | Magibu Yapay Zekâ Mimarisi Projesi*
