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

## 🎯 5. Eşik (Threshold) Analizi ve Benchmark Sonuçları

Sistemin doğruluk ve uydurma yapmama (hallucination prevention) başarımını ölçmek için **30 soruluk test seti** hazırlanmıştır:
* **20 Pozitif Soru:** Cevabı veritabanındaki dokümanlarda yer alan tıbbi sorular.
* **10 Negatif Soru:** Cevabı veri kümesinde bulunmayan alakasız / farklı konulardaki sorular.

### 🛡️ Eşik (Threshold) Yönetimi Mantığı:
* **Belirlenen Eşik Değeri:** **`0.60` (%60 Kosinüs Benzerliği)**
* **Filtreleme Mantığı:** Arama sonucunda elde edilen benzerlik skoru `0.60`'ın altında kaldığında sistem yanıt üretmez ve doğrudan şu çıktıyı verir:
  > **`"Bu sorunun cevabı dokümanlarımda yer almamaktadır"`**

### 📊 Benchmark Test Sonuçları:

| Metrik | Skor | Açıklama |
|---|---|---|
| **True Positives (TP)** | `20 / 20` | Cevabı olan soruların tamamı %64.0 - %89.4 benzerlikle doğru bulundu. |
| **True Negatives (TN)** | `10 / 10` | Cevabı olmayan soruların tamamı %13.3 - %46.2 skor alarak doğru şekilde elendi. |
| **False Positives (FP)** | `0` | Yanlış cevap / uydurma (Hallucination) **%0**. |
| **False Negatives (FN)** | `0` | Kaçırılan doğru cevap **%0**. |
| **Sistem Doğruluğu (Accuracy)** | **%100.00** | TP + TN / Toplam Soru |
| **Hassasiyet (Precision)** | **%100.00** | TP / (TP + FP) |
| **Duyarlılık (Recall)** | **%100.00** | TP / (TP + FN) |

### 📈 Benzerlik Skoru Dağılım İncelemesi:
* **Pozitif Soruların Benzerlik Aralığı:** `%64.0` - `%89.4` (Ortalama: ~%77)
* **Negatif Soruların Benzerlik Aralığı:** `%13.3` - `%46.2` (Ortalama: ~%27)
* **Sonuç:** `0.60` katsayısı pozitif ve negatif soruları kusursuz bir şekilde ikiye ayıran ideal karar sınırıdır.