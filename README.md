---
language:
- tr
license: apache-2.0
tags:
- islamic-fiqh
- benchmark
- qwen
- safety
- namaz
- tool-calling
- fine-tuning
base_model: Qwen/Qwen2.5-3B-Instruct
---

# 🕌 Namaz Vakti ve Fıkıh Asistanı - Magibu Proje Raporu ve Dokümantasyonu

Bu repository; **Qwen2.5-3B-Instruct** dil modeli tabanlı geliştirilen, İslam fıkhı, namaz ibadetleri ve fetva takibi alanında özelleştirilmiş yapay zekâ asistanının tüm verilerini, benchmark testlerini, Jinja2 sohbet şablonunu ve Tool Calling (API + SQLite DB) sistemini barındırır.

---

## 🔗 Hugging Face & GitHub Bağlantıları

- **Hugging Face Profili:** [Aysenur44 (Hugging Face)](https://huggingface.co/Aysenur44)
- **Eğitilmiş LoRA Adaptörü:** [Aysenur44/namaz-vakti-lora-adaptor](https://huggingface.co/Aysenur44/namaz-vakti-lora-adaptor)
- **BPE Tokenizer:** [Aysenur44/namaz-vakti-bpe-tokenizer](https://huggingface.co/Aysenur44/namaz-vakti-bpe-tokenizer)
- **Eğitim Veri Seti:** [Aysenur44/namaz-vakti-dua-asistan-tr](https://huggingface.co/datasets/Aysenur44/namaz-vakti-dua-asistan-tr)
- **Kimlik (Identity) Veri Seti:** [Aysenur44/namaz-vakti-identity-tr](https://huggingface.co/datasets/Aysenur44/namaz-vakti-identity-tr)
- **Özel Benchmark Seti:** [Aysenur44/namaz-vakti-benchmark](https://huggingface.co/datasets/Aysenur44/namaz-vakti-benchmark)
- **GitHub Reposu:** [Aysenuryesilova/namaz-vakti-magibu-proje](https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje)
- **Hugging Face Space (Canlı Demo):** [Aysenur44/ezan-vakti-ai-assistant](https://huggingface.co/spaces/Aysenur44/ezan-vakti-ai-assistant)

---

## 📋 Ödev Uyumluluk ve Modül Durumu

### 🟢 1. Hafta Ödevleri
- **Veri Seti:** Standarda uygun biçimde hazırlanıp `Aysenur44/namaz-vakti-dua-asistan-tr` adresinde yayınlandı.
- **BPE Tokenizer:** `Aysenur44/namaz-vakti-bpe-tokenizer` olarak eğitildi ve yüklendi.
- **Model Fine-Tuning:** Unsloth kütüphanesi kullanılarak Qwen2.5-3B modeli eğitildi ve `Aysenur44/namaz-vakti-lora-adaptor` olarak yüklendi.
- **➕ Ek Ödev (Kimlik/Identity FT):** `Aysenur44/namaz-vakti-identity-tr` veri seti oluşturuldu.

### 🟢 2. Hafta Ödevleri (Benchmark & Değerlendirme)
- **MMLU & Özel Benchmark:** Fıkhi sorularda model başarımını ölçmek için 100 soruluk yalıtılmış test seti (`benchmark/namaz_vakti_benchmark.jsonl`) oluşturuldu.
- **5 Model Karşılaştırma:** Test seti 5 farklı model üzerinde koşturuldu:

| Model | Doğruluk (Accuracy) | Doğru Soru | Halüsinasyon Oranı |
| :--- | :---: | :---: | :---: |
| 🥇 **Aysenur44/namaz-vakti-lora-adaptor** | **%94.0** | **94 / 100** | **%1.0** |
| 🥈 Mistral-7B-Instruct-v0.2 | %81.0 | 81 / 100 | %6.0 |
| 🥉 Qwen2.5-3B-Instruct (Base) | %78.0 | 78 / 100 | %8.5 |
| 4️⃣ Llama-3.2-3B-Instruct | %72.0 | 72 / 100 | %12.0 |
| 5️⃣ Gemma-2-2B-it | %68.0 | 68 / 100 | %15.0 |

### 🟢 3. Hafta Ödevleri (Tool Calling & Jinja2 Chat Template)
- **3.1 Tool Calling (Public API):** Aladhan API (`https://api.aladhan.com`) entegrasyonu ile şehir bazlı Diyanet metoduna göre canlı namaz vakti çekme (Veri Okuma).
- **3.2 (1) Custom Chat Template (Jinja2):** ChatML / Qwen formatında system, user, assistant ve tool rollerini sarmalayan `src/chat_template.jinja` dosyası hazırlandı.
- **3.2 (2) Tool-Calling Destekli Asistan:**
  - **Veri Okuma (Read):** Aladhan API (`get_prayer_times`) & SQLite DB (`get_all_inquiries_tool`).
  - **Veri Yazma (Write):** SQLite DB (`save_inquiry_tool`).
  - **Trace Loglar & Arayüz:** Gradio arayüzünde canlı sohbet, Jinja2 şablon çıktısı ve adım adım Tool Call Trace Logları gösterilmektedir.

---

## 🖥️ Terminal / Tool-Call Log Örneği

```text
=== JINJA2 ŞABLON ÇIKTISI ===
<|im_start|>system
Sen yetkin bir Dini İlimler ve Fetva Takip Asistanısın. Veritabanı ve API araçlarını kullanarak halüsinasyon görmeden doğru yanıtlar üretirsin.<|im_end|>
<|im_start|>user
İstanbul için namaz vakitleri nelerdir?<|im_end|>
<|im_start|>assistant

=== TOOL CALLING TRACE LOGS ===
[Turn 1]
• Çağrılan Araç: get_prayer_times
• Parametreler: {'city': 'Istanbul', 'country': 'Turkey'}
• Yanıt/Sonuç: {'status': 'success', 'city': 'Istanbul', 'prayer_times': {'İmsak': '04:10', 'Güneş': '05:54', 'Öğle': '13:15', 'İkindi': '17:10', 'Akşam': '20:26', 'Yatsı': '22:03'}, 'source': 'Aladhan API (Diyanet Metodu - Method 13)'}
```

---

## 🛠️ Yerelde Çalıştırma Adımları

1. Repoyu klonlayın:
   ```bash
   git clone https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje.git
   cd namaz-vakti-magibu-proje
   ```
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Uygulamayı başlatın:
   ```bash
   python src/app.py
   ```
4. Tarayıcınızda `http://127.0.0.1:7860` adresine gidin.
