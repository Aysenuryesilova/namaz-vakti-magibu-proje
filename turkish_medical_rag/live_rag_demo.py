# ==============================================================================
# CANLI RAG VEKTÖR ARAMA VE TEST ORTAMI
# İstediğiniz her türlü soruyu sorabilirsiniz!
# ==============================================================================

import chromadb
from sentence_transformers import SentenceTransformer

# Ayarlar
DB_PATH = "./chroma_db_storage"
COLLECTION_NAME = "turkish_medical_collection"
MODEL_NAME = "trmteb/turkish-embedding-model"
SIMILARITY_THRESHOLD = 0.60  # Eşik Değeri

print("⏳ Sistem yükleniyor, lütfen bekleyin...")
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection(name=COLLECTION_NAME)
model = SentenceTransformer(MODEL_NAME)

print("\n" + "="*60)
print("🩺 TÜRKÇE TIBBİ RAG CANLI SORU-CEVAP SİSTEMİ")
print("   Çıkmak için 'q' veya 'exit' yazabilirsiniz.")
print("="*60 + "\n")

while True:
    user_query = input("\n❓ Sorunuzu Yazın: ").strip()
    
    if user_query.lower() in ["q", "exit", "cikis", "çıkış"]:
        print("👋 Görüşmek üzere!")
        break
        
    if not user_query:
        continue
        
    # 1. Soruyu 768 boyutlu vektöre çevir
    q_vector = model.encode(user_query, normalize_embeddings=True).tolist()
    
    # 2. ChromaDB'de ara
    results = collection.query(
        query_embeddings=[q_vector],
        n_results=1,
        include=["documents", "metadatas", "distances"]
    )
    
    distance = results["distances"][0][0]
    similarity = 1.0 - distance
    
    print(f"\n📊 Benzerlik Skoru: %{similarity*100:.1f} (Eşik: %{SIMILARITY_THRESHOLD*100:.0f})")
    
    # 3. Eşik Kontrolü
    if similarity >= SIMILARITY_THRESHOLD:
        print("🟢 DURUM: Cevap Bulundu!")
        print("📌 Makale Başlığı :", results["metadatas"][0][0]["title"])
        print("🔗 Kaynak URL     :", results["metadatas"][0][0]["url"])
        print("\n📄 BULUNAN METİN İÇERİĞİ:\n" + "-"*40)
        print(results["documents"][0][0])
        print("-" * 40)
    else:
        print("🔴 DURUM: Eşik Altında Kaldı (Filtrelendi)")
        print("💬 Sistem Çıktısı: 'Bu sorunun cevabı dokümanlarımda yer almamaktadır'")