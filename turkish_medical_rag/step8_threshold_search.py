# ==============================================================================
# ADIM 7: VEKTÖR ARAMA & EŞİK (THRESHOLD) YÖNETİMİ VE BENCHMARK EVALUATION
# Amacımız: 30 Soruyu test etmek, Eşik (Threshold = 0.60) kontrolü uygulamak
# ve Sistemin Doğruluk (Accuracy), Hassasiyet (Precision) metriklerini ölçmek.
# ==============================================================================

import json
import time
import chromadb
from sentence_transformers import SentenceTransformer

# 1. Sabitler ve Ayarlar
DB_PATH = "./chroma_db_storage"
COLLECTION_NAME = "turkish_medical_collection"
MODEL_NAME = "trmteb/turkish-embedding-model"

# ÖDEVİN EN KRİTİK DEĞERİ: BENZERLİK EŞİĞİ (THRESHOLD)
# 0.60 (%60) altındaki aramalar "Cevap Dokümanda Yok" kabul edilecek.
SIMILARITY_THRESHOLD = 0.60

print(f"⏳ ChromaDB ve '{MODEL_NAME}' modeli yükleniyor...")
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection(name=COLLECTION_NAME)
embedding_model = SentenceTransformer(MODEL_NAME)

print(f"✅ Sistem Hazır! Veritabanında {collection.count()} adet chunk mevcut.")
print(f"🎯 Belirlenen Benzerlik Eşiği (Threshold): {SIMILARITY_THRESHOLD} (%{SIMILARITY_THRESHOLD*100:.0f})")

# 2. Test Sorularını Yüklüyoruz
with open("benchmark_questions.json", "r", encoding="utf-8") as f:
    test_questions = json.load(f)

print(f"\n📋 {len(test_questions)} adet test sorusu yükledi. Test başlatılıyor...\n")

# Metrik Takip Değişkenleri (Confusion Matrix)
TP = 0  # True Positive: Cevabı olan soruyu buldu ve verdi
TN = 0  # True Negative: Cevabı olmayan soruyu elendi ("Cevap dokümanda yok" dedi)
FP = 0  # False Positive: Cevabı olmayan soruya yanlışlıkla cevap verdi (Eşik hatası)
FN = 0  # False Negative: Cevabı olan soruyu yanlışlıkla elendi (Eşik yüksek geldi)

evaluation_results = []

print("="*80)
print(f"{'ID':<10} | {'TİP':<8} | {'BENZERLİK':<10} | {'DURUM':<15} | {'ÇIKTI VE SONUÇ'}")
print("="*80)

for q in test_questions:
    q_id = q["id"]
    q_type = q["type"]
    q_text = q["question"]
    
    # 1. Soruyu kendi 768 boyutlu modelimizle vektörleştiriyoruz
    q_vector = embedding_model.encode(q_text, normalize_embeddings=True).tolist()
    
    # 2. ChromaDB'de en yakın 1 parçayı aratıyoruz
    search_res = collection.query(
        query_embeddings=[q_vector],
        n_results=1,
        include=["documents", "metadatas", "distances"]
    )
    
    # Kosinüs Uzaklığını Kosinüs Benzerliğine çeviriyoruz (Similarity = 1 - Distance)
    distance = search_res["distances"][0][0]
    similarity = 1.0 - distance
    
    retrieved_text = search_res["documents"][0][0]
    retrieved_url = search_res["metadatas"][0][0]["url"]
    retrieved_title = search_res["metadatas"][0][0]["title"]
    
    # ==========================================================================
    # 🚨 EŞİK (THRESHOLD) KONTROLÜ
    # ==========================================================================
    if similarity >= SIMILARITY_THRESHOLD:
        system_status = "ANSWER_FOUND"
        system_output = retrieved_text[:120] + "..."
        is_above_threshold = True
    else:
        system_status = "NO_ANSWER_FALLBACK"
        # ÖDEVİN ZORUNLU CÜMLESİ:
        system_output = "Bu sorunun cevabı dokümanlarımda yer almamaktadır"
        is_above_threshold = False
        
    # Metrik Analizi ve Doğruluk Değerlendirmesi
    if q_type == "positive":
        if is_above_threshold:
            TP += 1
            eval_result = "✅ BAŞARILI (TP)"
        else:
            FN += 1
            eval_result = "❌ HATALI (FN - Yanlışlıkla elendi)"
    else: # negative soru
        if not is_above_threshold:
            TN += 1
            eval_result = "✅ BAŞARILI (TN - Doğru Elendi)"
        else:
            FP += 1
            eval_result = "❌ HATALI (FP - Uydurma Cevap)"
            
    print(f"{q_id:<10} | {q_type:<8} | %{similarity*100:<8.1f} | {system_status:<15} | {eval_result}")
    
    evaluation_results.append({
        "question_id": q_id,
        "question_type": q_type,
        "question": q_text,
        "similarity_score": similarity,
        "is_above_threshold": is_above_threshold,
        "system_status": system_status,
        "system_output": system_output,
        "retrieved_url": retrieved_url if is_above_threshold else None,
        "eval_result": eval_result
    })

# ==============================================================================
# 📊 DEĞERLENDİRME RAPORU VE PERFORMANS METRİKLERİ
# ==============================================================================
total_q = len(test_questions)
accuracy = (TP + TN) / total_q * 100
precision = (TP / (TP + FP) * 100) if (TP + FP) > 0 else 0
recall = (TP / (TP + FN) * 100) if (TP + FN) > 0 else 0

print("\n" + "="*50)
print("🎯 RAG VEKTÖR ARAMA BENCHMARK SONUÇLARI")
print("="*50)
print(f"Toplam Test Sorusu Sayısı : {total_q}")
print(f"Kullanılan Eşik (Threshold): {SIMILARITY_THRESHOLD} (%{SIMILARITY_THRESHOLD*100:.0f})")
print("-"*50)
print(f"True Positives (TP)  : {TP}  (Doğru Cevaplanan Pozitif Sorular)")
print(f"True Negatives (TN)  : {TN}  (Doğru Elenen Negatif Sorular)")
print(f"False Positives (FP) : {FP}  (Uydurulan / Yanlış Cevaplar)")
print(f"False Negatives (FN) : {FN}  (Kaçırılan Pozitif Sorular)")
print("-"*50)
print(f"📈 SİSTEM DOĞRULUĞU (ACCURACY) : %{accuracy:.2f}")
print(f"📈 HASSASİYET (PRECISION)       : %{precision:.2f}")
print(f"📈 DUYARLILIK (RECALL)          : %{recall:.2f}")
print("="*50)

# Sonuçları diske kaydediyoruz
output_file = "benchmark_evaluation_results.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump({
        "threshold": SIMILARITY_THRESHOLD,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "confusion_matrix": {"TP": TP, "TN": TN, "FP": FP, "FN": FN},
        "results": evaluation_results
    }, f, ensure_ascii=False, indent=4)

print(f"\n💾 Test sonuçları detaylı rapor olarak kaydedildi: '{output_file}'")