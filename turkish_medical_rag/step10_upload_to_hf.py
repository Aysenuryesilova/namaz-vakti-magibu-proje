# ==============================================================================
# TUM .py/.json pipeline
# dosyalari da "scripts/" klasoru altinda repoya yukleniyor. Boylece
# sonuclarin nasil uretildigi HF tarafinda da denetlenebilir/tekrarlanabilir
# oluyor.
# ==============================================================================

import json
import os
from datasets import Dataset
from huggingface_hub import HfApi

HF_TOKEN = "YOUR_HF_TOKEN_HERE"

api = HfApi(token=HF_TOKEN)

print("Hugging Face kullanicisi dogrulaniyor...")
try:
    user_info = api.whoami()
    username = user_info["name"]
    print(f"Giris yapilan kullanici: '{username}'")
except Exception as e:
    print(f"Token dogrulanirken hata olustu: {e}")
    exit()

DATASET_REPO_ID = f"{username}/turkish-medical-rag-dataset"
print(f"Hedef Repo ID: '{DATASET_REPO_ID}'")

# 1. Repo olustur (yoksa)
api.create_repo(
    repo_id=DATASET_REPO_ID,
    repo_type="dataset",
    private=False,
    exist_ok=True,
)
print(f"Repo hazir: '{DATASET_REPO_ID}'")

# 2. Vektorlu veriyi yukle (mevcut mantik korunuyor)
print("\n'embedded_chunks.json' okunuyor...")
with open("embedded_chunks.json", "r", encoding="utf-8") as f:
    chunks_data = json.load(f)

print(f"Toplam {len(chunks_data)} chunk okundu. HF formatina donusturuluyor...")
hf_dataset = Dataset.from_list(chunks_data)

print("\nHugging Face Hub'a veri seti yukleniyor...")
hf_dataset.push_to_hub(repo_id=DATASET_REPO_ID, token=HF_TOKEN)
print("Veri seti basariyla yuklendi!")

# 3. README.md yukle
print("\n'README.md' repoya ekleniyor...")
api.upload_file(
    path_or_fileobj="README.md",
    path_in_repo="README.md",
    repo_id=DATASET_REPO_ID,
    repo_type="dataset",
)
print("README.md yuklendi!")

# 4. YENI: Pipeline scriptlerini scripts/ klasoru altinda yukle
# Bu adim eksikti - odev "veri seti VE kodlar" istiyor, sadece veri seti
# yeterli degil. Asagidaki liste, HF reposunda gorunmesini istedigin
# tum pipeline dosyalarini kapsiyor.
PIPELINE_FILES = [
    "step2_fetch_data.py",
    "step3_chunking.py",
    "step4_embedding.py",
    "step5_vector_db.py",
    "step6_benchmark_dataset.py",
    "step8_threshold_search.py",
    "step9_create_readme.py",
    "benchmark_questions.json",
    "benchmark_evaluation_results.json",
]

print("\nPipeline scriptleri 'scripts/' altinda yukleniyor...")
for filename in PIPELINE_FILES:
    if not os.path.exists(filename):
        print(f"  ATLANDI (bulunamadi): {filename}")
        continue
    api.upload_file(
        path_or_fileobj=filename,
        path_in_repo=f"scripts/{filename}",
        repo_id=DATASET_REPO_ID,
        repo_type="dataset",
    )
    print(f"  Yuklendi: scripts/{filename}")

print("\n" + "=" * 70)
print("TAMAMLANDI! Veri seti + tum pipeline kodu HF reposuna yuklendi.")
print("=" * 70)
print(f"Repo: https://huggingface.co/datasets/{DATASET_REPO_ID}")
print("=" * 70)