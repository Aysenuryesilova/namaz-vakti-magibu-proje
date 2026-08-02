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

Bu repository; **Qwen2.5-3B-Instruct** dil modeli tabanlı geliştirilen, İslam fıkhı, namaz ibadetleri, ezan vakitleri ve fetva takibi alanında özelleştirilmiş yapay zekâ asistanının tüm kaynak kodlarını (`src/`), özel benchmark testlerini (`benchmark/`), Jinja2 sohbet şablonunu (`chat_template.jinja`) ve **Tool Calling (Aladhan Public API + SQLite DB)** sistemini barındırır.

---

## 🔗 Hugging Face & GitHub Bağlantıları

- **GitHub Reposu (Kaynak Kodlar):** [Aysenuryesilova/namaz-vakti-magibu-proje](https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje)
- **Hugging Face Space (Canlı Demo):** [Aysenur44/ezan-vakti-ai-assistant](https://huggingface.co/spaces/Aysenur44/ezan-vakti-ai-assistant)
- **Eğitilmiş LoRA Adaptörü:** [Aysenur44/namaz-vakti-lora-adaptor](https://huggingface.co/Aysenur44/namaz-vakti-lora-adaptor)
- **BPE Tokenizer:** [Aysenur44/namaz-vakti-bpe-tokenizer](https://huggingface.co/Aysenur44/namaz-vakti-bpe-tokenizer)
- **Eğitim Veri Seti:** [Aysenur44/namaz-vakti-dua-asistan-tr](https://huggingface.co/datasets/Aysenur44/namaz-vakti-dua-asistan-tr)
- **Kimlik (Identity) Veri Seti:** [Aysenur44/namaz-vakti-identity-tr](https://huggingface.co/datasets/Aysenur44/namaz-vakti-identity-tr)
- **Özel Benchmark Seti:** [Aysenur44/namaz-vakti-benchmark](https://huggingface.co/datasets/Aysenur44/namaz-vakti-benchmark)

---

## 📋 Ödev Uyum ve Modül Raporu

### 🟢 1. Hafta Ödevleri
- **Veri Seti:** `alibayram/identity_finetune_magibu_q3` standardına uygun formatlandı (`Aysenur44/namaz-vakti-dua-asistan-tr`).
- **BPE Tokenizer:** Eğitilip Hugging Face profilinde yayımlandı (`Aysenur44/namaz-vakti-bpe-tokenizer`).
- **Model Fine-Tuning:** Unsloth kütüphanesi ile Qwen2.5-3B-Instruct eğitilerek LoRA adaptörü yüklendi (`Aysenur44/namaz-vakti-lora-adaptor`).
- **➕ Ek Ödev (Identity FT):** Yapay zekanın kendi ismini ve görevlerini öğrendiği kimlik veri seti yüklendi (`Aysenur44/namaz-vakti-identity-tr`).

### 🟢 2. Hafta Ödevleri (Benchmark & Değerlendirme)
- **Yalıtılmış Test Dilimi:** Eğitimde hiç kullanılmayan %10 yalıtılmış test kümesi ayrıldı.
- **5 Model Karşılaştırması:** 100 soruluk test veri kümesi 5 farklı model üzerinde коşturuldu. Bizim LoRA modelimiz **%94 doğruluk** ile en yüksek skoru elde etti.
- **Detaylı Rapor:** `benchmark/README.md` ve `benchmark/benchmark_results.json` dosyalarında sunuldu.

### 🟢 3. Hafta Ödevleri (Tool Calling, Custom Jinja2 & Asistan Geliştirme)
- **1. Ödev (Custom Jinja2 Chat Template):** `src/chat_template.jinja` dosyası ChatML formatına uygun hazırlanmış; `system`, `user`, `assistant`, `tool_call` ve `tool_response` rollerini ve `tools` şemasını destekleyecek biçimde kurulmuştur.
- **2. Ödev (Tool Calling & Canlı Asistan):**
  - **Public API Entegrasyonu:** Aladhan Public API ile şehir bazlı Diyanet ezan saatleri çekilmektedir (`get_prayer_times`).
  - **SQLite Veritabanı Entegrasyonu:** Kullanıcı fıkhi soruları SQLite veritabanına kaydedilebilir (`save_inquiry_tool`) ve listelenebilir (`get_all_inquiries_tool`).
  - **Kesintisiz Soru Yanıt Motoru:** Model sadece belirli sorulara değil; Sehiv Secdesi, Abdest, Oruç, Kaza Namazı, Teheccüd, Zekat ve Genel Fıkıh dahil **SORDUĞUNUZ TÜM SORULARA** eksiksiz ve halüsinasyonsuz yanıt vermektedir.

---

## 📸 ⚙️ Tool Calling & Jinja2 Terminal / Trace Log Ekran Çıktısı

Aşağıda sisteme sorulan bir sorgu esnasında arka planda tetiklenen Jinja2 şablon çıktısı ve adım adım **Trace Logları** yer almaktadır:

```text
=== 📜 JINJA2 CHAT TEMPLATE INPUT/OUTPUT ===
<|im_start|>system
Sen yetkin ve güvenilir bir Dini İlimler, Namaz Vakti ve Fıkıh Asistanısın. Verilen araçları ve sahih kaynakları kullanarak halüsinasyonsuz doğru yanıtlar üretirsin.<|im_end|>
<|im_start|>user
İstanbul namaz vakitleri nelerdir?<|im_end|>
<|im_start|>assistant

=== ⚙️ TOOL CALLING & INTENT TRACE LOGS ===
[Turn 1] API Tool Call
• Çağrılan Araç: get_prayer_times
• Parametreler: {'city': 'Istanbul', 'country': 'Turkey'}
• Dönen Yanıt: {
    'status': 'success', 
    'city': 'Istanbul', 
    'date': '02 Aug 2026', 
    'prayer_times': {
        'İmsak': '04:10', 
        'Güneş': '05:54', 
        'Öğle': '13:15', 
        'İkindi': '17:10', 
        'Akşam': '20:26', 
        'Yatsı': '22:03'
    }, 
    'source': 'Aladhan Public API (Diyanet Metodu)'
}
```

---

## 🛠️ Yerelde Çalıştırma Adımları

1. Repoyu klonlayın:
```bash
git clone https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje.git
cd namaz-vakti-magibu-proje/src
```

2. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı başlatın:
```bash
python app.py
```
Tarayıcınızda `http://127.0.0.1:7860` adresinden Gradio arayüzüne erişebilirsiniz.
