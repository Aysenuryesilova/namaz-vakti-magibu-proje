# ==============================================================================
# ADIM 5: CHROMADB VEKTÖR VERİTABANINA YÜKLEME VE DOĞRU SORGU ARAMASI
# ==============================================================================

import json
import time
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "./chroma_db_storage"
COLLECTION_NAME = "turkish_medical_collection"
MODEL_NAME = "trmteb/turkish-embedding-model"

print(f"⏳ ChromaDB veritabanı ilklendiriliyor ('{DB_PATH}' klasörüne kaydedilecek)...")
client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"} # Kosinüs uzaklığı
)

print(f"✅ ChromaDB Koleksiyonu Hazır: '{COLLECTION_NAME}'")

stored_count = collection.count()

# Eğer veriler henüz yüklenmediyse yükle (Daha önce 8 saniyede yüklediğimiz için tekrar yüklemeyecek)
if stored_count < 9946:
    print("\n⏳ 'embedded_chunks.json' verisi okunuyor ve yükleniyor...")
    with open("embedded_chunks.json", "r", encoding="utf-8") as f:
        chunks_data = json.load(f)

    ids = [item["chunk_id"] for item in chunks_data]
    embeddings = [item["chunk_vector"] for item in chunks_data]
    documents = [item["chunk_text"] for item in chunks_data]
    metadatas = [{
        "parent_id": item["parent_id"],
        "chunk_index": item["chunk_index"],
        "url": item["url"],
        "title": item["title"],
        "__source": item["__source"],
        "char_length": item["char_length"],
        "word_count": item["word_count"]
    } for item in chunks_data]

    BATCH_SIZE = 1000
    total_items = len(ids)

    for i in range(0, total_items, BATCH_SIZE):
        end_i = min(i + BATCH_SIZE, total_items)
        collection.upsert(
            ids=ids[i:end_i],
            embeddings=embeddings[i:end_i],
            documents=documents[i:end_i],
            metadatas=metadatas[i:end_i]
        )
        print(f"  └─► {end_i} / {total_items} chunk indekslendi...")

print(f"\n✅ Veritabanında İndekslenmiş Eleman Sayısı: {collection.count()}")

# ==============================================================================
# 📊 DOĞRU SORGU ARAMA TESTİ (768 BOYUTLU MODELİMİZ İLE)
# ==============================================================================
print("\n" + "="*50)
print("🔍 CANLI TIBBİ SORGU ARAMA TESTİ")
print("="*50)

print(f"⏳ Sorgu için '{MODEL_NAME}' modeli yükleniyor...")
embedding_model = SentenceTransformer(MODEL_NAME)

test_query = "Miyom belirtileri nelerdir?"
print(f"\n❓ Sorulan Soru: '{test_query}'")

# 1. Soruyu da KENDİ 768 boyutlu modelimizle vektörleştiriyoruz!
query_vector = embedding_model.encode(test_query, normalize_embeddings=True).tolist()

# 2. Ürettiğimiz 768 boyutlu vektörü query_embeddings olarak soruyoruz
results = collection.query(
    query_embeddings=[query_vector],
    n_results=1,
    include=["documents", "metadatas", "distances"]
)

# Kosinüs Uzaklığını (Cosine Distance) Kosinüs Benzerliğine (Cosine Similarity) çeviriyoruz
# Formula: Cosine Similarity = 1 - Cosine Distance
cosine_distance = results["distances"][0][0]
cosine_similarity = 1.0 - cosine_distance

print("\n🎯 ARAMA SONUCU VE BENZERLİK SKORU:")
print("  └─► Bulunan Parça ID:", results["ids"][0][0])
print(f"  └─► Kosinüs Benzerlik Skoru (Similarity): {cosine_similarity:.4f} (%{cosine_similarity*100:.1f})")
print("  └─► Kaynak URL:", results["metadatas"][0][0]["url"])
print("  └─► Makale Başlığı:", results["metadatas"][0][0]["title"])
print("\n📄 BULUNAN METİN PARÇASI:\n", results["documents"][0][0][:300], "...")
print("="*50)