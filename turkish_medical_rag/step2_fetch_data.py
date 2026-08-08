# ==============================================================================
# ADIM 2: HUGGING FACE VERİ SETİ İNDİRME VE TOKEN İLE KİMLİK DOĞRULAMA
# ==============================================================================

import json
import random
from datasets import load_dataset
import pandas as pd

HF_TOKEN = "YOUR_HF_TOKEN_HERE"

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

print("⏳ Hugging Face Token ile kimlik doğrulaması yapılıyor ve veri seti indiriliyor...")

try:
    # token parametresi ile erişim izni alıyoruz
    dataset = load_dataset(
        "umutertugrul/turkish-medical-articles",
        split="train",
        token=HF_TOKEN
    )
    print(f"✅ BİLGI: Veri seti başarıyla çekildi! Toplam makale sayısı: {len(dataset)}")
except Exception as e:
    print(f"\n❌ Veri indirilirken bir hata oluştu:\n{e}")
    print("\n👉 Lütfen HF_TOKEN değişkenine geçerli bir 'hf_...' tokeni yazdığından ve web sitesinde erişim butonuna tıkladığından emin ol.")
    exit()

df = pd.DataFrame(dataset)

# ==============================================================================
# 📊 VERİ İNCELEME VE ANALİZİ
# ==============================================================================
print("\n" + "="*50)
print("🔍 VERİ SETİ RÖNTGENİ VE ANALİZİ")
print("="*50)

print("\n1. Sütun İsimleri ve Yapısı:")
print(df.columns.tolist())

print("\n2. İlk 2 Satır Örneği:")
print(df.head(2))

# Temizlik: Metni boş olan satırları eliyoruz
df_clean = df.dropna(subset=["text"]).copy()
df_clean = df_clean[df_clean["text"].str.strip() != ""].copy()
print(f"\n3. Temizlik Sonrası Geçerli Makale Sayısı: {len(df_clean)}")

# Metin uzunlukları istatistiği (Karakter bazında)
df_clean["char_count"] = df_clean["text"].str.len()
print("\n4. Makale Karakter Uzunluğu İstatistikleri:")
print(df_clean["char_count"].describe())

# ==============================================================================
# 🎯 1.000 ADET MAKALE SEÇİMİ
# ==============================================================================
TARGET_COUNT = 1000

if len(df_clean) >= TARGET_COUNT:
    df_selected = df_clean.sample(n=TARGET_COUNT, random_state=RANDOM_SEED).reset_index(drop=True)
else:
    print(f"⚠️ Veri setinde {len(df_clean)} makale var, tümü kullanılıyor.")
    df_selected = df_clean.reset_index(drop=True)

print(f"\n✅ Hedeflenen {len(df_selected)} adet makale başarıyla seçildi!")

# ==============================================================================
# 🛠️ META VERİLERİ YAPILANDIRMA
# ==============================================================================
processed_articles = []

for idx, row in df_selected.iterrows():
    parent_id = f"doc_{idx:04d}"
    
    url = row.get("url") if "url" in row and pd.notna(row["url"]) else f"https://turkish-medical-journal.org/article/{parent_id}"
    title = row.get("title") if "title" in row and pd.notna(row["title"]) else f"Tıbbi İnceleme Makalesi #{idx+1}"
    text = str(row["text"]).strip()
    source = row.get("source") or row.get("category") or "Türk Tıp Kütüphanesi"
    
    processed_articles.append({
        "parent_id": parent_id,
        "url": str(url),
        "title": str(title),
        "text": text,
        "__source": str(source),
        "char_count": len(text)
    })

# JSON formatında yerel diske kaydediyoruz
output_file = "selected_raw_articles.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(processed_articles, f, ensure_ascii=False, indent=4)

print(f"\n💾 1.000 Makale başarıyla yerel dosyaya kaydedildi: '{output_file}'")

# İnceleme için 1 örnek gösterelim
print("\n--- ÖRNEK SEÇİLEN MAKALE (parent_id: doc_0000) ---")
print("Ana Kimlik (parent_id):", processed_articles[0]["parent_id"])
print("Başlık:", processed_articles[0]["title"])
print("URL:", processed_articles[0]["url"])
print("Kaynak:", processed_articles[0]["__source"])
print("Karakter Sayısı:", processed_articles[0]["char_count"])
print("Metin Başlangıcı (İlk 250 Karakter):\n", processed_articles[0]["text"][:250], "...")
print("="*50)