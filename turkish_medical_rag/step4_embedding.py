# ==============================================================================
# ADIM 4: CHUNK METİNLERİNİ EMBEDDING VEKTÖRLERİNE DÖNÜŞTÜRME (ULTRA HIZLI CPU)
# Model: trmteb/turkish-embedding-model (768 Boyutlu Türkçe BERT Tabanlı)
# ==============================================================================

import json
import time
import os
import torch
from sentence_transformers import SentenceTransformer

# Tüm CPU çekirdeklerini aktif et
num_cores = os.cpu_count() or 4
torch.set_num_threads(num_cores)

# Ödevimizin sunduğu Türkçe BERT Tabanlı 768 Boyutlu Süper Hızlı Model
MODEL_NAME = "trmteb/turkish-embedding-model"

print(f"⏳ Hızlı Türkçe Embedding modeli yükleniyor: '{MODEL_NAME}'...")
start_time = time.time()

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🖥️ İşlem Cihazı: {device.upper()} ({num_cores} Çekirdek Aktif)")

model = SentenceTransformer(MODEL_NAME, device=device)

print(f"✅ Model başarıyla yüklendi! ({time.time() - start_time:.2f} saniye)")

# 2. Chunk verilerimizi yüklüyoruz
print("\n⏳ 'processed_chunks.json' okunuyor...")
with open("processed_chunks.json", "r", encoding="utf-8") as f:
    chunks_data = json.load(f)

total_chunks = len(chunks_data)
print(f"✅ Toplam {total_chunks} adet chunk hazır.")

texts_to_embed = [item["chunk_text"] for item in chunks_data]

print("\n🚀 İŞIK HIZINDA VEKTÖR ÜRETİMİ BAŞLIYOR...")
print("⚡ Beklenen süre: ~1-2 DAKİKA!")

encode_start = time.time()

with torch.inference_mode():
    embeddings = model.encode(
        texts_to_embed,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

encode_duration = time.time() - encode_start
print(f"\n🎉 MÜKEMMEL! Vektör üretimi tamamlandı! Toplam süre: {encode_duration:.2f} saniye ({encode_duration/60:.2f} dakika)")

# 3. Vektörleri nesnelere ekliyoruz
print("\n🛠️ Vektörler ödev veritabanı şemasına ekleniyor...")
for i, item in enumerate(chunks_data):
    item["chunk_vector"] = embeddings[i].tolist()

output_file = "embedded_chunks.json"
print(f"💾 Son veriler '{output_file}' dosyasına kaydediliyor...")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(chunks_data, f, ensure_ascii=False)

print(f"✅ BİLGI: Vektörlü veri seti başarıyla kaydedildi!")

# ==============================================================================
# 📊 DOĞRULAMA KONTROLÜ
# ==============================================================================
print("\n" + "="*50)
print("🔍 VEKTÖR DOĞRULAMA VE ŞEMA KONTROLÜ")
print("="*50)
sample = chunks_data[0]
vector = sample["chunk_vector"]

print("1. Örnek Chunk ID:", sample["chunk_id"])
print("2. Vektör Boyutu (Dimension):", len(vector), "(Beklenen: 768)")
print("3. Vektörün İlk 5 Elemanı:", vector[:5])
print("4. ÖDEVİN 3 ZORUNLU SÜTÜNU MEVCUT MU?:")
print("   - 'url' var mı?:", "url" in sample)
print("   - 'chunk_text' var mı?:", "chunk_text" in sample)
print("   - 'chunk_vector' var mı?:", "chunk_vector" in sample)
print("="*50)