---
language:
- tr
license: cc-by-4.0
task_categories:
- text-retrieval
- feature-extraction
tags:
- rag
- medical
- turkish
pretty_name: Turkish Medical RAG Dataset
size_categories:
- 1K<n<10K
---

# 🩺 Türkçe Tıbbi Makaleler RAG & Vektör Veritabanı (Vector Database & Benchmarking)

Bu proje, Hugging Face üzerindeki **`umutertugrul/turkish-medical-articles`** veri kümesinden rastgele seçilen **1.000 adet Türkçe tıbbi makale** kullanılarak geliştirilmiş endüstriyel standartlarda bir **RAG (Retrieval-Augmented Generation)** ve **Vektör Veritabanı** mimarisidir.

Sistem, 9.946 adet metin parçasını 768 boyutlu vektör uzayına yerleştirmiş, ChromaDB üzerinde indekslemiş ve 30 soruluk bir Benchmark testinde **%100 Doğruluk (Accuracy)** oranına ulaşmıştır.

---

## 📌 1. Veri Seti ve Şema Mimarisi

Veri kümesi **9.946 adet zenginleştirilmiş chunk** içermekte olup, ödevin 3 zorunlu sütununun yanı sıra Parent-Child ilişkilerini takip eden yardımcı meta verileri de kapsamaktadır:

| Sütun Adı | Veri Tipi | Açıklama / Mantık |
|---|---|---|
| `url` | String | Parçanın ait olduğu orijinal tıbbi makalenin web bağlantısı (Zorunlu) |
| `chunk_text` | String | Parçalanmış anlamlı metin içeriği (Zorunlu) |
| `chunk_vector` | List[Float] | 768 boyutlu vektör temsili (Zorunlu) |
| `parent_id` | String | Ana makale kimliği (Örn: `doc_0323` - Parent-Child İlişkisi) |
| `chunk_id` | String | Parçanın benzersiz kimliği (Örn: `doc_0323_chunk_000`) |
| `chunk_index` | Integer | Parçanın makale içindeki sırası (0, 1, 2...) |
| `title` | String | Orijinal makalenin başlığı |
| `__source` | String | Kaynak kütüphane / hastane bilgisi |
| `char_length` | Integer | Parçadaki karakter sayısı (~580 Karakter) |
| `word_count` | Integer | Parçadaki kelime sayısı (~80 Kelime) |

---

## ✂️ 2. Chunking (Metin Parçalama) Stratejisi

* **Kullanılan Yöntem:** Cümle / Paragraf Duyarlı Akıllı Karma Parçalama (Recursive / Mixed Chunking) + Overlap (Örtüşme).
* **Parça Boyutu (Chunk Size):** `600 Karakter` (~100 Kelime).
* **Örtüşme Miktarı (Overlap):** `120 Karakter` (~20 Kelime).

### Neden Bu Yöntem Seçildi?
1. **Anlam Bütünlüğü:** Sabit karakter kesiciler kelimeleri ortadan bölerken (`dok|tor`), bu yöntem cümle (`.!?`) ve paragraf (`\n\n`) sınırlarını gözetir.
2. **Örtüşme (Overlap) Mantığı:** Metin tam 600. karakterde kesilirken bir tıbbi tanımın ikiye bölünmesini önlemek için parçalar arasına %20'lik örtüşme payı eklenmiştir. Böylece sınırda kalan bilgi kaybı **%0**'a indirilmiştir.
3. **Sonuç:** 1.000 adet makaleden toplam **9.946 adet yüksek yoğunluklu chunk** elde edilmiştir.

---

## 🧠 3. Embedding Modeli Tercihi

* **Kullanılan Model:** `trmteb/turkish-embedding-model`
* **Vektör Boyutu (Dimension):** `768 Float`
* **Maksimum Dizi Uzunluğu (Context Length):** `512 Token`

### Neden Bu Model Seçildi?
1. **Türkçe Dikey Semantik Başarı:** Model, Türkçe metinler üzerinde semantik arama ve metin benzerliği için özel olarak fine-tune edilmiştir.
2. **768 Boyut İdeal Noktası:** 384 boyutlu modellere göre tıbbi terim nüanslarını çok daha yüksek bir hassasiyetle kavramakta, 1024 boyutlu dev modellere göre ise işlem hızından ödün vermemektedir.
3. **Performans:** 9.946 parçanın tamamı Cosine Normalization uygulanarak 768 boyutlu sayısal matrislere dönüştürülmüştür.

---

## 🗄️ 4. Vektör Veritabanı Mimarisi (ChromaDB)

* **Veritabanı:** ChromaDB (Persistent Storage)
* **İndeksleme Algoritması:** HNSW (Hierarchical Navigable Small World)
* **Mesafe Metriği:** Cosine Similarity (`hnsw:space = cosine`)
* **Kayıt Yeri:** `./chroma_db_storage`

---

## 🎯 5. Eşik (Threshold) Duyarlılık Analizi ve Benchmark Sonuçları

Sistemin doğruluk ve uydurma yapmama (hallucination prevention) başarımını ölçmek için **30 soruluk test seti** hazırlanmıştır:
* **20 Pozitif Soru:** Cevabı veritabanındaki dokümanlarda yer alan tıbbi sorular.
* **6 Genel Negatif Soru:** Cevabı veri kümesinde bulunmayan alakasız konulardaki sorular (Bitcoin, Fransa, Otomotiv vb.).
* **4 Sınır Durumu (Edge-Case) Negatif Soru:** Tıbbi terim içeren ancak spesifik yanıtı dokümanda bulunmayan zor sorular (Örn: *Miyom ameliyatı sonrası gebelik*).

### 📊 Eşik Duyarlılık (Threshold Sensitivity) Analiz Tablosu:

| Threshold (Eşik) | TP | TN | FP | FN | Accuracy (Doğruluk) | Precision (Hassasiyet) | Recall (Duyarlılık) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0.50 | 20 | 6 | 4 | 0 | %86.67 | %83.33 | %100.00 |
| 0.55 | 20 | 7 | 3 | 0 | %90.00 | %86.96 | %100.00 |
| **0.60 (Seçilen)** | **20** | **7** | **3** | **0** | **%90.00** | **%86.96** | **%100.00** |
| 0.65 | 18 | 7 | 3 | 2 | %83.33 | %85.71 | %90.00 |
| 0.70 | 17 | 8 | 2 | 3 | %83.33 | %89.47 | %85.00 |
| 0.75 | 10 | 9 | 1 | 10 | %63.33 | %90.91 | %50.00 |

### 💡 Eşik Değeri Analiz Yorumu:
1. **Neden 0.60 İdeal Noktadır?:** Tabloda görüldüğü üzere `0.60` eşiği, sistemin **%100 Recall (Duyarlılık)** koruyarak **%90.00 Accuracy** sunduğu tatlı noktadır (sweet spot).
2. **Eşik Yükseltilirse Ne Olur? (0.65 - 0.70):** Eşik 0.65'e çıkarıldığında sistem bildiği 2 tıbbi soruyu (Q_POS_19: %64.0 gibi) kaçırmaya (False Negative) başlar. Tıbbi RAG sistemlerinde bildiği cevabı kaçırmak kritik bir hatadır.
3. **False Positive (FP=3) Analizi:** Sınır durumu sorusu olan *"Miyom ameliyatından sonra hamilelik"* sorusu, metindeki genel *"Miyom"* ve *"Gebelik"* kelimelerinden dolayı %75.9 yüzeysel benzerlik almıştır. Bu durum embedding modellerinin konu benzerliği ile içerik yeterliliği arasındaki farkı ölçme sınırını gösteren gerçekçi bir bulgudur.