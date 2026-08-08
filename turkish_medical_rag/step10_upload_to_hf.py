# ==============================================================================
# ADIM 8: OTOMATİK KULLANICI ALMA VE HUGGING FACE YÜKLEME
# ==============================================================================

import json
from datasets import Dataset
from huggingface_hub import HfApi

HF_TOKEN = "YOUR_HF_TOKEN_HERE" 

api = HfApi(token=HF_TOKEN)

print("⏳ Hugging Face kullanıcısı doğrulanıyor...")
try:
    user_info = api.whoami()
    username = user_info["name"]
    print(f"✅ Giriş Yapılan Gerçek Kullanıcı Adı: '{username}'")
except Exception as e:
    print(f"❌ Token doğrulanırken hata oluştu: {e}")
    exit()

# Otomatik olarak doğru kullanıcı adı ile repo_id oluşturuluyor!
DATASET_REPO_ID = f"{username}/turkish-medical-rag-dataset"
print(f"🎯 Hedef Repo ID: '{DATASET_REPO_ID}'")

# 1. Repoyu oluşturmayı deniyoruz
try:
    api.create_repo(
        repo_id=DATASET_REPO_ID,
        repo_type="dataset",
        private=False,
        exist_ok=True
    )
    print(f"✅ Repo hazırlandı: '{DATASET_REPO_ID}'")
except Exception as e:
    print(f"ℹ️ BİLGI: Repo zaten mevcut veya erişim hazır.")

# 2. Vektörlü veriyi okuyoruz
print(f"\n⏳ 'embedded_chunks.json' okunuyor...")
with open("embedded_chunks.json", "r", encoding="utf-8") as f:
    chunks_data = json.load(f)

print(f"✅ Toplam {len(chunks_data)} adet chunk okundu. Hugging Face formatına dönüştürülüyor...")

# Hugging Face Dataset objesine çeviriyoruz
hf_dataset = Dataset.from_list(chunks_data)

# 3. Veri setini yüklüyoruz
print(f"\n🚀 Hugging Face Hub'a veri seti yükleniyor...")
hf_dataset.push_to_hub(
    repo_id=DATASET_REPO_ID,
    token=HF_TOKEN
)
print("✅ Veri seti (9.946 Chunk + Vektörler + Meta Veriler) başarıyla yüklendi!")

# 4. README.md dosyasını yüklüyoruz
print(f"\n⏳ 'README.md' dosyası repoya ekleniyor...")
try:
    api.upload_file(
        path_or_fileobj="README.md",
        path_in_repo="README.md",
        repo_id=DATASET_REPO_ID,
        repo_type="dataset"
    )
    print("✅ Akademik README.md dosyası başarıyla yüklendi!")
except Exception as e:
    print(f"⚠️ README yüklenirken uyarı: {e}")

print("\n" + "="*70)
print("🎉 TEBRİKLER! ÖDEVİN HUGGING FACE REPOSUNA BAŞARIYLA YÜKLENDİ!")
print("="*70)
print(f"🔗 Hugging Face Repo Bağlantın:\nhttps://huggingface.co/datasets/{DATASET_REPO_ID}")
print("="*70)