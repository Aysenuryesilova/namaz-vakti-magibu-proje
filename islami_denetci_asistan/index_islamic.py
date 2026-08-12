"""
==============================================================================
İSLÂMİ DOKÜMAN VE KİTAP İNDEKSLEYİCİ (INDEX_ISLAMIC.PY)
==============================================================================
Bu dosya ödevdeki 'index_medical.py' dosyasının birebir karşılığıdır.
İstediğiniz bir metin dosyasını (.txt veya .json), Diyanet İlmihalini veya Tefsir
kitaplarını ChromaDB veritabanına sınırsız olarak yüklemenizi sağlar.
"""

import argparse
import os
import islamic_rag
import ollama_client

def index_file(filepath: str):
    """Verilen metin dosyasını okur, parçaları ayırır ve ChromaDB'ye yükler."""
    if not os.path.exists(filepath):
        print(f"Hata: '{filepath}' dosyası bulunamadı.")
        return
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    chunks = islamic_rag.chunk_text(content)
    metadatas = [{"baslik": os.path.basename(filepath), "kaynak": "Harici Yüklenen Kitap"} for _ in chunks]
    
    islamic_rag.add_custom_documents(chunks, metadatas)
    print(f"[OK] '{filepath}' dosyasindan {len(chunks)} parca basariyla veritabanina eklendi.")

def main():
    parser = argparse.ArgumentParser(description="İslami ilmihal ve kitapları ChromaDB veritabanına indeksler.")
    parser.add_argument("--file", type=str, help="Yüklenecek .txt metin dosyasının yolu")
    parser.add_argument("--reset", action="store_true", help="Koleksiyonu sıfırdan oluştur")
    args = parser.parse_args()

    if args.file:
        index_file(args.file)
    else:
        print("[1/2] Başlangıç İslami Esaslar Hazırlanıyor...")
        islamic_rag.seed_knowledge_base()
        print("[2/2] Başarıyla Tamamlandı! Kendi kitaplarınızı yüklemek için: python index_islamic.py --file kitap.txt")

if __name__ == "__main__":
    main()
