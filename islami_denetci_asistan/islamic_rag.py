"""
==============================================================================
VEKTÖR VERİTABANI VE İLMİHAL / KİTAP İNDEKSLEME KATMANI (ISLAMIC_RAG.PY)
==============================================================================
Bu dosya:
1. ChromaDB Vektör Veritabanına dinamik olarak sınırsız sayıda kitap, PDF veya TXT metin yüklenmesini sağlar.
2. Sabit cümlelerle sınırlı değildir; 'add_custom_documents()' fonksiyonu ile Diyanet İlmihali,
   Tefsirler ve Kelam kitaplarının tamamı veritabanına aktarılabilir.
"""

import os
import chromadb
import ollama_client
from config import DEFAULT_EMBED

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")

def get_collection(embed_key: str = DEFAULT_EMBED):
    """ChromaDB koleksiyonunu açar veya oluşturur."""
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(
        name=f"islami_referanslar_{embed_key}",
        metadata={"hnsw:space": "cosine"},
        embedding_function=None,
    )

def chunk_text(text: str, chunk_size: int = 250, overlap: int = 40) -> list[str]:
    """Uzun kitap metinlerini (Örn: Diyanet İlmihali) çakışmalı pencerelerle parçalara böler."""
    words = text.split()
    if not words:
        return []
    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(words), step):
        window = words[start : start + chunk_size]
        if window:
            chunks.append(" ".join(window))
        if start + chunk_size >= len(words):
            break
    return chunks

def add_custom_documents(texts: list[str], metadatas: list[dict]):
    """
    Sınırsız sayıda yeni dokümanı, ilmihal kitabını veya ayet tefsirini ChromaDB'ye ekler.
    """
    try:
        collection = get_collection()
        start_id = collection.count()
        ids = [f"doc-{start_id + i}" for i in range(len(texts))]
        embeddings = ollama_client.embed(texts, kind="doc")
        collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
        print(f"[RAG] Veritabanına {len(texts)} adet yeni ilmihal/tefsir parçası başarıyla eklendi.")
    except Exception as exc:
        print(f"[RAG Ekleme Hatası]: {exc}")

def seed_knowledge_base():
    """Örnek başlangıç bilgi tabanını yükler (Eğer veritabanı boşsa)."""
    try:
        collection = get_collection()
        if collection.count() > 0:
            return
        
        initial_docs = [
            "Nizam ve Gaye Delili (Teleological Argument): Evrendeki fiziksel sabitler bir tesadüfle açıklanamayacak kadar hassas ayarlanmıştır. Bilgi ancak bilinçli bir Yaratıcı (Allah) ile açıklanabilir.",
            "Vicdan ve Ahlak Delili: İnsandaki evrensel adalet arzusu ve merhamet duygusu maddesel değildir. İnsanın soyut bir ruha sahip olduğunu gösterir.",
            "Evrenin Genişlemesi Mucizesi (Zariyat 47): 'Göğü gücümüzle biz kurduk ve şüphesiz biz onu genişletmekteyiz.' 1400 yıl önce evrenin genişlediği bildirilmiştir.",
            "Suyun Hayat Kaynağı Olması (Enbiya 30): 'Her canlı şeyi sudan yarattığımızı görmediler mi?' Biyolojik olarak tüm canlı hücrelerinin temeli sudur.",
            "Dağların Kazık Şeklinde Olması (Nebe 6-7): Dağların yer kabuğu altında derin kökleri (isostasy) olduğu jeolojik bir gerçektir.",
            "Teheccüd Namazı: Yatsı namazından sonra gece uykudan uyanılarak İmsak (Sahur) vaktine kadar kılınan çok faziletli nafile namazdır.",
            "Sehiv Secdesi: Namazda unutarak bir rüknün geciktirilmesi veya bir vacibin terk edilmesi durumunda yapılan düzeltme secdesidir.",
            "Namazın Hikmeti: Günde 5 vakit namaz, insanı kainatın karmaşasından söküp alır ve ruhsal dinginlik sunar.",
            "Diyanet İmsak Hesabı: Diyanet imsak vaktini hesaplarken Güneş'in ufkun 18 derece altında olduğu anı esas alır.",
            "Kıble Trigonometrisi: Kıble açısı hesaplamalarında küresel dünya yüzeyi üzerindeki Büyük Daire (Great Circle) formülü kullanılır.",
            "Hicri Takvim Esasları: Hicri takvim hesaplamalarında Umm al-Qura astronomik hesabı ile rüyet-i hilal kararı arasında 1 gün fark oluşabilir."
        ]
        
        metadatas = [
            {"baslik": "Nizam Delili", "kaynak": "Kelam"},
            {"baslik": "Ahlak Delili", "kaynak": "Felsefe"},
            {"baslik": "Zariyat 47", "kaynak": "Mucize"},
            {"baslik": "Enbiya 30", "kaynak": "Mucize"},
            {"baslik": "Nebe 6-7", "kaynak": "Mucize"},
            {"baslik": "Teheccüd", "kaynak": "İlmihal"},
            {"baslik": "Sehiv Secdesi", "kaynak": "İlmihal"},
            {"baslik": "Namaz Hikmeti", "kaynak": "İlmihal"},
            {"baslik": "İmsak", "kaynak": "Diyanet"},
            {"baslik": "Kıble", "kaynak": "Trigonometri"},
            {"baslik": "Hicri Takvim", "kaynak": "Astronomı"}
        ]
        add_custom_documents(initial_docs, metadatas)
    except Exception as exc:
        print(f"[RAG Seed Hatası]: {exc}")

def search_rag(question: str, embed_key: str = DEFAULT_EMBED, k: int = 3) -> list[dict]:
    """Soruyu vektöre çevirip ChromaDB'den en alakalı dokümanları getirir."""
    try:
        collection = get_collection(embed_key)
        if collection.count() == 0:
            seed_knowledge_base()
            collection = get_collection(embed_key)
            
        query_vec = ollama_client.embed([question], embed_key, kind="query")[0]
        res = collection.query(
            query_embeddings=[query_vec],
            n_results=min(k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        
        hits = []
        if res and res["documents"]:
            for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
                hits.append({
                    "text": doc,
                    "baslik": meta.get("baslik", ""),
                    "kaynak": meta.get("kaynak", ""),
                    "benzerlik": round(1.0 - dist, 3)
                })
        return hits
    except Exception:
        return []
