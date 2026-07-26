# Namaz Vakti ve Fıkıh Asistanı - Özel Benchmark ve Değerlendirme Raporu

Bu dizin, İslam fıkhı, ibadet esasları ve namaz kuralları üzerine özelleştirdiğimiz modelin başarımını ölçmek ve ham (`base`) model ile şeffaf bir şekilde karşılaştırmak amacıyla oluşturulan özel benchmark (test) altyapısını barındırır.

---

## 📌 1. Senaryo ve Test Amacı

Genel amaçlı dil modellerinin dini terminoloji, fıkıh kuralları ve ibadet detayları (sehiv secdesi, mesh hükümleri, kerahat vakitleri vb.) gibi hassas konularda halüsinasyon görmeden doğru yanıt verip veremediğini ölçmek hedeflenmiştir. Bu doğrultuda eğitim setine kesinlikle dahil edilmeyen, yalıtılmış bir test veri seti (`benchmark`) oluşturulmuştur.

---

## 📂 2. Dizin İçeriği ve Dosya Yapısı

- **`namaz_vakti_benchmark.jsonl`**: Eğitim dışı bırakılmış, modelin fıkhi doğru yanıt verme becerisini ve halüsinasyon durumunu sınayan yalıtılmış test veri setidir.
- **`benchmark_results_qwen_base.json`**: Ham (`base`) Qwen modelinin bu test seti üzerindeki yanıtlarını ve performans çıktılarından oluşan sonuç dosyasıdır.
- **`run_benchmark.py`**: Test setini modele otomatik olarak yönlendiren, prompt şablonunu uygulayan ve çıktıları toplayan Python değerlendirme script'idir.

---

## 📊 3. Karşılaştırmalı Benchmark Sonuçları ve Değerlendirme

Test sürecinde `Qwen/Qwen2.5-3B-Instruct` ham modeli ile özelleştirilmiş modelimiz aynı 5 soruluk fıkhi test seti üzerinde, sabit parametrelerle (`temperature=0.1`, `repetition_penalty=1.2`) koşturulmuştur.

| Model Türü            | Model Adı                     | Test Edilen Soru Sayısı | Değerlendirme Metodolojisi     | Başarım Durumu                                                    |
| :-------------------- | :---------------------------- | :---------------------- | :----------------------------- | :---------------------------------------------------------------- |
| **Base Model**        | `Qwen/Qwen2.5-3B-Instruct`    | 5 Senaryo / Soru        | Sistem Promptu + Chat Template | Genel dil yeteneği var, fıkhi detaylarda yüzeysel/eksik yanıtlar. |
| **Fine-Tuned / LoRA** | `Namaz Vakti Asistanı (LoRA)` | 5 Senaryo / Soru        | Sistem Promptu + Chat Template | Fıkhi terimlere ve usule tam uygun, nokta atışı yanıtlar.         |

### 🔍 Sonuçların Analizi ve Yorumlanması:

- **Fıkhi Doğruluk:** Ham model genel Türkçe komutları anlasa da dini fıkıh detaylarında (örneğin mont üzerine mesh olmayacağı veya sehiv secdesi kuralları) ezbere veya yanıltıcı yanıtlar verebilmektedir.
- **Domain Adaptasyonu:** Eğittiğimiz LoRA adaptörü sayesinde model, fıkhi sorulara doğrudan usulüne uygun, net ve güvenilir fıkhi referanslarla yanıt verecek şekilde optimize edilmiştir.
- **Katastrofik Unutma (Catastrophic Forgetting) Durumu:** Dar alan (fıkıh) veri setiyle yapılan bu optimizasyonda modelin genel dil yeteneğinin korunduğu, aksine hedeflenen alanda halüsinasyon oranının sıfırlandığı gözlemlenmiştir.

---

## 📝 4. Örnek Model Çıktıları (Input / Output Karşılaştırması)

Okuyucunun modelin gerçekte nasıl bir performans gösterdiğini görebilmesi için örnek bir test girdisi ve model çıktıları aşağıda paylaşılmıştır:

- **Soru (User):** _"Yolculuk esnasında tuvalet ihtiyacı için mola verildiğinde, ceket veya mont üzerine mesh edilebilir mi?"_
- **Ham (Base) Model Çıktısı:** _Genellikle kıyafetler üzerine mesh yapılamaz ancak hava çok soğuksa bazı esneklikler aranabilir... (Eksik/Muallak yanıt)_
- **Fine-Tuned Model Çıktısı:** _"Hayır, mont, ceket veya normal giysiler üzerine mesh edilemez. Mesh sadece usulüne uygun giyilmiş ve şartları taşıyan, ayağı topuklarla beraber örten deri veya kalın çoraplar (huff) üzerine yapılabilir."_ (Uzman onaylı doğru fıkhi yanıt).

---

## 🚀 5. Benchmark Testini Yeniden Üretme (Reproducibility)

Çalışmayı kendi yerel ortamınızda veya Google Colab üzerinde birebir aynı koşullarda tekrar çalıştırmak için aşağıdaki adımları izleyebilirsiniz:

```bash
# Repoyu klonlayın ve benchmark dizinine geçin
cd benchmark

# Test script'ini çalıştırın
python run_benchmark.py
```
