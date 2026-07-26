# 📌 Namaz Vakti & İslami Asistanlık - Özel Benchmark (Evaluation) Kiti

Bu dizin, fine-tune ettiğimiz **Gemma 3 1B 4-bit (LoRA)** İslami Asistan modelimizin fıkhi doğruluğunu, bilgi tutarlılığını ve halüsinasyon oranını test etmek amacıyla oluşturulmuş özel bir benchmark (test seti) projesidir.

## 📂 Dosya Yapısı

- `namaz_vakti_benchmark.jsonl`: Eğitim sürecinden tamamen bağımsız olarak ayrılmış %5 - %10'luk yalıtılmış test ver seti.
- `run_benchmark.py`: Modeli bu test seti üzerinde otomatik olarak koşturan değerlendirme script'i.
- `benchmark_results.json`: Modelin test sorularına verdiği yanıtların kaydedildiği çıktı dosyası.

## 🚀 Nasıl Çalıştırılır?

1. Model ve LoRA adaptör yollarınızın doğru olduğundan emin olun.
2. Test script'ini çalıştırın:
   ```bash
   python run_benchmark.py
   ```
