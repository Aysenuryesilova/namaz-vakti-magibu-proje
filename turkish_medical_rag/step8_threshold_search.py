# ==============================================================================
# ADIM 8b (EK): THRESHOLD DUYARLILIK (SENSITIVITY) ANALIZI
# Amac: benchmark_evaluation_results.json icindeki gercek similarity skorlarini
# kullanarak, FARKLI esik degerlerinde (0.55, 0.60, 0.65, 0.70...) confusion
# matrix'in nasil degistigini gostermek. Bu, 0.60 esiginin neden secildigini
# sayisal olarak savunmani sagliyor.
#
# Girdi: benchmark_evaluation_results.json (step8_threshold_search.py ciktisi)
# Cikti: konsola tablo + threshold_sensitivity.json
# ==============================================================================

import json

INPUT_FILE = "benchmark_evaluation_results.json"
OUTPUT_FILE = "threshold_sensitivity.json"
CANDIDATE_THRESHOLDS = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

results = data["results"]

sensitivity_report = []

print("=" * 90)
print("THRESHOLD DUYARLILIK ANALIZI")
print("=" * 90)
print(f"{'Threshold':<10} {'TP':<5}{'TN':<5}{'FP':<5}{'FN':<5} {'Accuracy':<10}{'Precision':<11}{'Recall':<10}")
print("-" * 90)

for threshold in CANDIDATE_THRESHOLDS:
    tp = tn = fp = fn = 0
    for r in results:
        score = r["similarity_score"]
        is_positive_type = r["question_type"] == "positive"
        system_answers = score >= threshold

        if is_positive_type and system_answers:
            tp += 1
        elif is_positive_type and not system_answers:
            fn += 1
        elif not is_positive_type and not system_answers:
            tn += 1
        else:
            fp += 1

    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")

    print(f"{threshold:<10} {tp:<5}{tn:<5}{fp:<5}{fn:<5} "
          f"{accuracy:.2%}      {precision:.2%}      {recall:.2%}")

    sensitivity_report.append({
        "threshold": threshold,
        "TP": tp, "TN": tn, "FP": fp, "FN": fn,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
    })

print("=" * 90)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(sensitivity_report, f, ensure_ascii=False, indent=2)

print(f"\nDetayli rapor kaydedildi: {OUTPUT_FILE}")
print("\nYORUM ICIN NOT:")
print("- Esik yukseltilirse (orn. 0.65-0.70): FP sayisi azalir ama bazi")
print("  pozitif sorular (Q_POS_19: %64.0 gibi) da FN'e donusme riski tasir.")
print("- Esik dusurulurse: Recall artabilir ama daha fazla uydurma (FP) riski")
print("  ortaya cikar - bu RAG sistemlerinde en tehlikeli hata turudur.")
print("- 0.60 secimi, recall'u (%100) hic feda etmeden makul bir precision")
print("  sunuyor - bu RAG sistemlerinde 'hicbir dogru cevabi kacirmama'")
print("  onceligiyle uyumlu bir tasarim tercihidir.")