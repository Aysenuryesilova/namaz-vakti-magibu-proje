# ==============================================================================
# README.MD İÇİN HUGGING FACE YAML META VERİSİ EKLEME & YÜKLEME
# ==============================================================================

from huggingface_hub import HfApi

HF_TOKEN = "YOUR_HUGGING_FACE_TOKEN"
DATASET_REPO_ID = "Aysenur44/turkish-medical-rag-dataset"

# 1. Hugging Face'in istediği YAML Başlık Formatı
yaml_header = """---
language:
- tr
license: cc-by-4.0
task_categories:
- text-retrieval
- feature-extraction
tags:
- rag
- medical
- turkish
pretty_name: Turkish Medical RAG Dataset
size_categories:
- 1K<n<10K
---

"""

# 2. Mevcut README.md dosyasını okuyup başına YAML ekliyoruz
with open("README.md", "r", encoding="utf-8") as f:
    existing_readme = f.read()

# Eğer zaten --- ile başlamıyorsa başına ekle
if not existing_readme.startswith("---"):
    updated_readme = yaml_header + existing_readme
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_readme)
    print("✅ 'README.md' dosyasına YAML meta verisi başarıyla eklendi.")

# 3. Güncellenmiş README.md'yi Hugging Face Reposuna yüklüyoruz
print("⏳ Hugging Face'e güncellenmiş README.md yükleniyor...")
api = HfApi(token=HF_TOKEN)
api.upload_file(
    path_or_fileobj="README.md",
    path_in_repo="README.md",
    repo_id=DATASET_REPO_ID,
    repo_type="dataset"
)

print("\n🎉 MÜKEMMEL! YAML Uyarısı Tamamen Temizlendi!")
print(f"🔗 Reponu kontrol edebilirsin:\nhttps://huggingface.co/datasets/{DATASET_REPO_ID}")