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
- fine-tuning
base_model: Qwen/Qwen2.5-3B-Instruct
---

# Namaz Vakti ve Fıkıh Asistanı - Özel Benchmark ve Model Değerlendirme Raporu

Bu repository, **Qwen/Qwen2.5-3B-Instruct** modeli tabanlı geliştirilen İslam fıkhı, ibadet esasları ve namaz kuralları asistanının özel benchmark (test) süreçlerini, veri setlerini ve değerlendirme sonuçlarını barındırır.

---

## 📌 Projenin Amacı ve Senaryo
Genel amaçlı dil modellerinin (LLM) dini terminoloji, fıkıh kuralları ve ibadet detayları (örneğin sehiv secdesi, mesh hükümleri, kerahat vakitleri vb.) gibi hassas konularda halüsinasyon görmeden, kaynaklara uygun ve doğru yanıtlar verip veremediğini test etmek ve ölçmektir. Bu bağlamda yalıtılmış bir test veri seti (`benchmark`) oluşturulmuş ve model performansı Google Colab ortamında otomatize edilmiştir.

---

## 📂 Dosya Yapısı

```text
namaz_vakti_magibu_proje/
│
├── benchmark/
│   ├── namaz_vakti_benchmark.jsonl      # Eğitim dışı bırakılmış %5-%10'luk fıkhi test seti
│   ├── benchmark_results_qwen_base.json # Ham (Base) Qwen modelinin test yanıtları
│   └── run_benchmark.py                 # Otomatik benchmark koşturma script'i
│
└── README.md                            # Model kartı ve dokümantasyon
```
📊 Benchmark Veri Seti Örneği (namaz_vakti_benchmark.jsonl)
Test setimiz, sistem promptu, kullanıcı sorusu ve uzman onaylı doğru yanıt (ground_truth) üçlüsünden oluşmaktadır:
{
  "messages": [
    {"role": "system", "content": "Sen İslam dini ve ibadetler konusunda bilgili, rehber bir asistansın."},
    {"role": "user", "content": "Yolculuk esnasında tuvalet ihtiyacı için mola verildiğinde, ceket veya mont üzerine mesh edilebilir mi?"},
    {"role": "assistant", "content": "Hayır, mont, ceket veya normal giysiler üzerine mesh edilemez. Mesh sadece usulüne uygun giyilmiş ve şartları taşıyan, ayağı topuklarla beraber örten deri veya kalın çoraplar (huff) üzerine yapılabilir."}
  ]
}

🚀 Test Süreci ve Çalıştırma
Benchmark testini yerel ortamda veya Google Colab üzerinde çalıştırmak için run_benchmark.py script'i kullanılmaktadır:
python benchmark/run_benchmark.py

Teknik Parametreler:
-Model: Qwen/Qwen2.5-3B-Instruct

-Inference Ortamı: PyTorch, Hugging Face transformers & peft

-Generation Ayarları: temperature=0.1, repetition_penalty=1.2, max_new_tokens=150

📈 Sonuçlar ve Değerlendirme
Yapılan testler sonucunda ham modelin genel dil yeteneğine sahip olduğu, ancak fıkhi konularda derinlemesine adaptasyon gerektirdiği tespit edilmiştir. Bu çalışma, özelleştirilmiş alanlarda (domain adaptation) benchmark setlerinin önemini ve model başarı ölçümünün metodolojisini net bir şekilde ortaya koymaktadır.
