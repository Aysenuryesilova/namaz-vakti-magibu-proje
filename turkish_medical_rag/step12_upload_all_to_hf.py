# ==============================================================================
# TÜM PROJE KODLARINI VE TESTLERİ HUGGING FACE REPOSUNA YÜKLEME SCRIPT'İ
# ==============================================================================

import os
from huggingface_hub import HfApi, login

# 🔴 Gerçek Hugging Face Token'ın:
HF_TOKEN = "YOUR_HF_TOKEN_HERE"
DATASET_REPO_ID = "Aysenur44/turkish-medical-rag-dataset"

# Hugging Face oturumunu doğruluyoruz
try:
    login(token=HF_TOKEN)
except Exception as e:
    print("⚠️ Oturum açılırken hata oluştu, lütfen token'ınızı kontrol edin:", e)

api = HfApi()

# Hugging Face'e yüklenecek dosya listesi
files_to_upload = [
    "README.md",
    "step2_fetch_data.py",
    "step3_chunking.py",
    "step4_embedding.py",
    "step5_vector_db.py",
    "step6_benchmark_dataset.py",
    "step8_threshold_search.py",
    "step9_create_readme.py",
    "explore_my_data.py",
    "live_rag_demo.py",
    "benchmark_questions.json",
    "threshold_sensitivity.json"
]

print(f"⏳ Hugging Face reposuna ('{DATASET_REPO_ID}') tüm dosyalar yükleniyor...\n")

for file_name in files_to_upload:
    if os.path.exists(file_name):
        print(f"📤 Yükleniyor: {file_name} ...")
        api.upload_file(
            path_or_fileobj=file_name,
            path_in_repo=file_name,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset"
        )
    else:
        print(f"⚠️ Atlandı (Dosya bulunamadı): {file_name}")

print("\n🎉 TEBRİKLER! Tüm dosyalar Hugging Face'e başarıyla yüklendi!")
print(f"🔗 Kontrol Linki:\nhttps://huggingface.co/datasets/{DATASET_REPO_ID}/tree/main")