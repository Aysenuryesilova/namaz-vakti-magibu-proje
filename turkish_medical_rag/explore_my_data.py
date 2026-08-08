# ==============================================================================
# VERİ SETİNİ CANLI İNCELEME VE OKUMA ARACI
# Amacımız: İndirdiğimiz 1.000 makaleyi ve 9.946 parçayı gözümüzle görmek!
# ==============================================================================

import json

# Yerel diske kaydettiğimiz parçaları yüklüyoruz
with open("processed_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print("="*60)
print(f"📚 TOPLAM PARÇA (CHUNK) SAYINIZ: {len(chunks)}")
print("  İstediğiniz kelimeyi aratıp veritabanınızdaki metinleri okuyabilirsiniz!")
print("  Çıkmak için 'q' yazın.")
print("="*60)

while True:
    keyword = input("\n🔎 Aramak İstediğiniz Kelime (Örn: miyom, böbrek, stres, gebelik): ").strip()
    
    if keyword.lower() in ["q", "exit", "cikis"]:
        break
        
    if not keyword:
        continue
        
    # Kelimenin geçtiği parçaları buluyoruz
    matches = [c for c in chunks if keyword.lower() in c["chunk_text"].lower() or keyword.lower() in c["title"].lower()]
    
    print(f"\n🔍 '{keyword}' kelimesi geçen toplam parça sayısı: {len(matches)}")
    
    # İlk 3 eşleşmeyi ekrana basalım ki gözünle oku
    for i, m in enumerate(matches[:3]):
        print(f"\n--- EŞLEŞME #{i+1} ---")
        print("Parça ID   :", m["chunk_id"])
        print("Makale Adı :", m["title"])
        print("URL        :", m["url"])
        print("Metin Karakter Sayısı:", m["char_length"])
        print("Metin İçeriği:\n" + "-"*30)
        print(m["chunk_text"])
        print("-" * 30)