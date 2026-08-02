# 📊 Namaz Vakti ve Fıkıh Asistanı - Özel Benchmark Dokümantasyonu

Bu dizin, **Namaz Vakti ve Fıkıh Asistanı** dil modelinin fıkhi konularda, vakit hesaplamalarında ve dini terminolojide halüsinasyon görüp görmediğini ölçmek için hazırlanan yalıtılmış benchmark test kümesini barındırır.

---

## 📌 Benchmark Metodolojisi ve Şartları (Hafta 2.1 & 2.2)

1. **Yalıtılmış Veri Dilimi (%5-%10):** Fine-tune eğitimi aşamasında modele hiçbir şekilde verilmeyen 100 soru kenara ayrılmıştır.
2. **Manuel ve Sentetik Soru Üretimi:** Test kümesindeki 100 sorunun en az 10 adedi fıkıh kitapları ve kaynakları taranarak elle özenle hazırlanmış, kalan kısmı sentetik çeşitlendirmeyle oluşturulmuştur.
3. **5 Model Karşılaştırması:** Özel benchmark testi 5 farklı model üzerinde koşturulmuş ve başarım oranları şeffaf bir şekilde kaydedilmiştir.

---

## 🏆 5 Model Karşılaştırma Sonuçları Tablosu

| Model Adı | Doğruluk Oranı (Accuracy) | Doğru Yanıt / Toplam | Halüsinasyon Oranı | Ort. Yanıt Süresi |
| :--- | :---: | :---: | :---: | :---: |
| 🥇 **Aysenur44/namaz-vakti-lora-adaptor (Bizim Model)** | **%94.0** | **94 / 100** | **%1.0** | **1.2 sn** |
| 🥈 Mistral-7B-Instruct-v0.2 | %81.0 | 81 / 100 | %6.0 | 2.4 sn |
| 🥉 Qwen/Qwen2.5-3B-Instruct (Base Model) | %78.0 | 78 / 100 | %8.5 | 1.1 sn |
| 4️⃣ Llama-3.2-3B-Instruct | %72.0 | 72 / 100 | %12.0 | 1.3 sn |
| 5️⃣ Gemma-2-2B-it | %68.0 | 68 / 100 | %15.0 | 1.0 sn |

---

## 📂 Dosyalar

- `namaz_vakti_benchmark.jsonl`: 100 soruluk test veri kümesi.
- `benchmark_results.json`: 5 modelin ayrıntılı test sonuçlarını içeren JSON raporu.
- `2_hafta_odevım.ipynb`: Colab üzerinde testi koşturan Jupyter Notebook.
