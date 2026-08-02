# benchmark/create_benchmark.py
"""
BENCHMARK OLUŞTURMA SÜRECİ VE YENİDEN ÜRETİLEBİLİRLİK (REPRODUCIBILITY) SCRIPT'İ
Bu script, ana eğitim veri setinden (namaz-vakti-dua-asistan-tr) %10'luk yalıtılmış 
test dilimini (hold-out) ayırır ve senaryoya özel benchmark kütüğünü üretir.
"""

import json
from datasets import load_dataset

def create_scenario_benchmark():
    print("1. Ana Eğitim Veri Seti Yükleniyor (Aysenur44/namaz-vakti-dua-asistan-tr)...")
    try:
        # Ana eğitim veri setimizi yüklüyoruz
        full_dataset = load_dataset("Aysenur44/namaz-vakti-dua-asistan-tr", split="train")
    except Exception as e:
        print(f"Veri seti yükleme hatası: {e}")
        return

    print("2. Eğitim Verisinden Bağımsız %10 Yalıtılmış (Hold-Out) Test Kümesi Ayrılıyor...")
    # Seed=42 kullanarak her çalıştırmada aynı %10'luk yalıtılmış kütüğün ayrılmasını sağlıyoruz
    split_data = full_dataset.train_test_split(test_size=0.10, seed=42)
    isolated_test_set = split_data["test"]

    print(f"   -> Toplam Ayrılan Yalıtılmış Soru Sayısı: {len(isolated_test_set)}")

    # 3. Senaryoya Özel Veri Formatlama
    benchmark_list = []
    for row in isolated_test_set:
        benchmark_list.append({
            "instruction": row.get("instruction", row.get("question", "")),
            "input": row.get("input", ""),
            "expected_output": row.get("output", row.get("answer", "")),
            "source": "holdout_split_10_percent"
        })

    # 4. Benchmark Dosyasını Oluşturma
    output_file = "benchmark/namaz_vakti_benchmark.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for item in benchmark_list:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"✅ Senaryoya Özel Benchmark Başarıyla Üretildi ve Kaydedildi: {output_file}")

if __name__ == "__main__":
    create_scenario_benchmark()