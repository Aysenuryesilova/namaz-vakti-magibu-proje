import os
import json
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

print("🚀 Qwen Tabanlı LoRA Benchmark Script'i Başlatılıyor...")

current_dir = Path(__file__).resolve().parent  # benchmark klasörü
root_dir = current_dir.parent                 # ana dizin

# 1. Doğru Qwen Model ID'si (Doğrudan CPU üzerinden yükleme)
base_model_id = "Qwen/Qwen2.5-3B-Instruct"

print("📥 Qwen-3B Base model CPU üzerinden yükleniyor...")
tokenizer = AutoTokenizer.from_pretrained(base_model_id)
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    device_map={"": "cpu"}
)

# 2. LoRA Adaptörünü Entegre Etme
adapter_path = root_dir / "namaz-vakti-lora-adaptor"
if (adapter_path / "adapter_config.json").exists():
    print(f"🔗 Qwen uyumlu LoRA Adaptörü entegre ediliyor: {adapter_path}")
    model = PeftModel.from_pretrained(model, str(adapter_path))
else:
    print(f"⚠️ UYARI: '{adapter_path}' bulunamadı!")

model.eval()

# 3. Benchmark Verisini Okuma
benchmark_file = current_dir / "namaz_vakti_benchmark.jsonl"
with open(benchmark_file, "r", encoding="utf-8") as f:
    test_data = [json.loads(line) for line in f]

results = []
print(f"📊 Toplam {len(test_data)} test sorusu eğitilmiş Qwen modeline yöneltiliyor...")

# 4. Test Döngüsü
for idx, item in enumerate(test_data):
    messages = item["messages"]
    
    system_prompt = messages[0]["content"]
    user_prompt = messages[1]["content"]
    
    # Qwen için chat template veya uygun prompt formatı
    prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.1,
            do_sample=True,
            repetition_penalty=1.2,
            eos_token_id=tokenizer.eos_token_id
        )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    model_response = generated_text.split("assistant")[-1].strip()
    
    results.append({
        "id": idx + 1,
        "expected_user": user_prompt,
        "ground_truth_assistant": messages[2]["content"] if len(messages) > 2 else messages[1]["content"],
        "model_output": model_response
    })

# 5. Sonuçları Kaydetme
output_file = current_dir / "benchmark_results.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"✅ Harika! Qwen + LoRA fıkhi test sonuçları '{output_file}' dosyasına kaydedildi.")