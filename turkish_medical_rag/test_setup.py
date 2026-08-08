import datasets
import sentence_transformers
import chromadb
import pandas as pd
import torch

print("=== KÜTÜPHANE KONTROLÜ ===")
print(f"CUDA / GPU Kullanılabilir mi?: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Cihazı: {torch.cuda.get_device_name(0)}")
else:
    print("İşlemler CPU üzerinde çalışacak (Harika, bu proje için CPU yeterlidir).")

print("Datasets Versiyonu:", datasets.__version__)
print("SentenceTransformers Versiyonu:", sentence_transformers.__version__)
print("ChromaDB Versiyonu:", chromadb.__version__)
print("\n✅ Bütün kütüphaneler başarıyla yüklendi! Adım 1 Hazır.")