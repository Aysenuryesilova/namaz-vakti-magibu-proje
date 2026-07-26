import json

with open("benchmark_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

print(f"🔍 Toplam {len(results)} test sonucu inceleniyor:\n" + "="*50)

for res in results:
    print(f"Soru ID: {res['id']}")
    print(f"Kullanıcı Sorusu: {res['expected_user']}")
    print(f"Modelin Cevabı:   {res['model_output']}")
    print("-" * 50)