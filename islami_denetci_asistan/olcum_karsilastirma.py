"""
==============================================================================
EMBEDDING VE RAG BAŞARI ÖLÇÜM & KARŞILAŞTIRMA SCRIPT’İ (OLCUM_KARSILASTIRMA.PY)
==============================================================================
Bu dosya ödevdeki 'olcum_karsilastirma.py' dosyasının İslami senaryomuza uyarlanmış halidir.
Vektör veritabanındaki aramanın (retriever) doğruluğunu ve alaka skoru ayrımını ölçer.
"""

import argparse
import islamic_rag
import ollama_client

# Veritabanında olması gereken sorular ve beklenen anahtar kelimeler
IN_KB = [
    ("Sehiv secdesi nedir?", "sehiv"),
    ("İmsak vakti nasıl hesaplanır?", "imsak"),
    ("Kıble açısı nasıl hesaplanır?", "kıble"),
]

# Veritabanında olmaması gereken alakasız sorular
OUT_OF_KB = [
    "Mars kolonilerinde grip nasıl tedavi edilir?",
    "Bitcoin fiyatı ne kadar?",
]

def main():
    parser = argparse.ArgumentParser(description="Embedding modellerinin doğruluğunu ölçer.")
    parser.add_argument("--model", nargs="+", default=list(ollama_client.EMBED_MODELS), help="Ölçülecek modeller")
    args = parser.parse_args()

    for embed_key in args.model:
        print(f"\n=== {embed_key} ({ollama_client.EMBED_MODELS[embed_key]['name']}) Ölçüm Testi ===")
        for q, expected in IN_KB:
            hits = islamic_rag.search_rag(q, embed_key=embed_key, k=1)
            if hits:
                top = hits[0]
                correct = expected.lower() in top["text"].lower()
                print(f"  {'✅ OK ' if correct else '❌ YANLIŞ'} Skor: {top['benzerlik']} | Soru: {q}")
            else:
                print(f"  ❌ Sonuç Bulunamadı | Soru: {q}")

if __name__ == "__main__":
    main()
