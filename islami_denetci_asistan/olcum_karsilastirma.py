"""
==============================================================================
EMBEDDING VE RAG BAŞARI ÖLÇÜM & KARŞILAŞTIRMA SCRIPT’İ (OLCUM_KARSILASTIRMA.PY)
==============================================================================
Bu dosya ödevdeki 'olcum_karsilastirma.py' dosyasının İslami senaryomuza uyarlanmış halidir.
TF-IDF Vektör veritabanındaki aramanın (retriever) doğruluğunu ve alaka skoru ayrımını ölçer.
==============================================================================
"""

import sys
import islamic_rag

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Veritabanında olması gereken sorular ve beklenen anahtar kelimeler
IN_KB = [
    ("Sehiv secdesi nedir?", "sehiv"),
    ("İmsak vakti nasıl hesaplanır?", "imsak"),
    ("Abdestin farzları nelerdir?", "abdest"),
]

# Veritabanında olmaması gereken alakasız sorular
OUT_OF_KB = [
    "Mars kolonilerinde grip nasıl tedavi edilir?",
    "Bitcoin fiyatı ne kadar?",
]

def main():
    print("==================================================================")
    print(" İSLAMİ VEKTÖR RAG DOĞRULUK VE ÖLÇÜM KARŞILAŞTIRMA TESTİ")
    print("==================================================================")
    
    print("\n=== 1. VERİTABANI İÇİ SORGULAR (IN-KB ACCURACY TEST) ===")
    for q, expected in IN_KB:
        hits = islamic_rag.search_rag(q)
        if hits:
            top = hits[0]
            text_combo = (top["text"] + " " + top["topic"]).lower()
            correct = expected.lower() in text_combo
            print(f"  {'✅ OK ' if correct else '❌ YANLIŞ'} | Soru: '{q}' -> Eşleşen Konu: [{top['topic']}]")
        else:
            print(f"  ❌ Sonuç Bulunamadı | Soru: {q}")

    print("\n=== 2. ALAKASIZ SORGULAR FİLTRELEME TESTİ (OUT-OF-KB TEST) ===")
    for q in OUT_OF_KB:
        hits = islamic_rag.search_rag(q)
        print(f"  ℹ️ Alakasız Sorgu: '{q}' | Dönen Sonuç Sayısı: {len(hits)}")

if __name__ == "__main__":
    main()
