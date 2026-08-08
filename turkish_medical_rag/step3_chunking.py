# ==============================================================================
# ADIM 3: CHUNKING (METİN PARÇALAMA) STRATEJİSİ
# Yöntem: Cümle/Paragraf Sınırlarına Duyarlı + Overlap (Örtüşme) Parçalama
# Girdi: selected_raw_articles.json (1.000 Makale)
# Çıktı: processed_chunks.json (Tüm Parçalar ve Meta Veriler)
# ==============================================================================

import json
import re

# Chunking Parametreleri
CHUNK_SIZE = 600      # Hedeflenen parça boyutu (Karakter bazlı)
CHUNK_OVERLAP = 120   # Parçalar arasındaki örtüşme miktarı (Karakter bazlı)

def recursive_chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Metni rastgele bir noktadan kesmek yerine önce paragraf (\n\n), 
    sonra cümle (.), en son kelime (boşluk) sınırlarından akıllıca böler.
    Ayrıca parçalar arasına overlap (örtüşme) ekler.
    """
    if not text or len(text) <= chunk_size:
        return [text]
    
    # 1. Metni önce paragraflara ve cümlelere bölelim
    # Nokta, soru işareti, ünlem veya yeni satırdan ayırıyoruz
    sentences = re.split(r'(?<=[.!?\n])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Eğer mevcut parçaya bu cümleyi eklediğimizde limit aşılmıyorsa ekle
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            # Limit aşıldı! Mevcut parçayı listeye ekle
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # OVERLAP (ÖRTÜŞME) MANTIĞI:
            # Yeni parçaya geçmeden önce eski parçanın son 'overlap' kadarlık kısmını alıyoruz
            if len(current_chunk) > overlap:
                overlap_text = current_chunk[-overlap:]
                # Overlap metnini kelime ortasından kesmemek için ilk boşluktan sonrasını alıyoruz
                first_space = overlap_text.find(" ")
                if first_space != -1:
                    overlap_text = overlap_text[first_space+1:]
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk = sentence
                
    # Son kalan parçayı da ekle
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

print("⏳ 'selected_raw_articles.json' dosyası okunuyor...")

# 1.000 Makalemizi yüklüyoruz
with open("selected_raw_articles.json", "r", encoding="utf-8") as f:
    raw_articles = json.load(f)

print(f"✅ {len(raw_articles)} adet ana makale yüklendi. Chunking işlemi başlıyor...")

all_chunks = []
total_chunk_count = 0

for article in raw_articles:
    parent_id = article["parent_id"]
    url = article["url"]
    title = article["title"]
    source = article["__source"]
    text = article["text"]
    
    # Akıllı Chunking fonksiyonumuzu çağırıyoruz
    chunks_text_list = recursive_chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    
    # Her parçayı zengin meta verilerle paketliyoruz
    for i, c_text in enumerate(chunks_text_list):
        chunk_id = f"{parent_id}_chunk_{i:03d}"  # Örn: doc_0042_chunk_001
        
        chunk_item = {
            "chunk_id": chunk_id,          # Parça benzersiz ID'si
            "parent_id": parent_id,        # Ana makale ID'si (Parent-Child ilişkisi)
            "chunk_index": i,              # Parçanın makaledeki sırası (0, 1, 2...)
            "url": url,                    # ÖDEV ZORUNLU SÜTUN 1: Kaynak Bağlantı
            "title": title,                # Ek Meta Veri: Makale Başlığı
            "__source": source,            # Ek Meta Veri: Kaynak Hastane/Kütüphane
            "chunk_text": c_text,          # ÖDEV ZORUNLU SÜTUN 2: Parçalanmış Metin
            "char_length": len(c_text),    # Ek Meta Veri: Karakter Sayısı
            "word_count": len(c_text.split()) # Ek Meta Veri: Kelime Sayısı
        }
        
        all_chunks.append(chunk_item)

print("\n" + "="*50)
print("📊 CHUNKING İSTATİSTİKLERİ VE SONUÇLARI")
print("="*50)
print(f"Toplam İşlenen Ana Makale (Parent) Sayısı: {len(raw_articles)}")
print(f"Üretilen Toplam Parça (Chunk / Child) Sayısı: {len(all_chunks)}")
print(f"Makale Başına Ortalama Parça Sayısı: {len(all_chunks) / len(raw_articles):.2f}")

# Hazırlanan tüm chunk'ları diske kaydediyoruz
output_file = "processed_chunks.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=4)

print(f"\n💾 Tüm parçalar meta verileriyle kaydedildi: '{output_file}'")

# Rastgele bir chunk örneği basıp inceleyelim
print("\n--- ÖRNEK VERİTABANI CHUNK ELEMANI (100/100 Şema) ---")
sample_chunk = all_chunks[0]
for key, val in sample_chunk.items():
    if key == "chunk_text":
        print(f"  {key}: '{val[:150]}...'")
    else:
        print(f"  {key}: {val}")
print("="*50)