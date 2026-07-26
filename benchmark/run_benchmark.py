import os
import json
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

print("🚀 LoRA Adaptörlü Kesin Çözümlü Benchmark Script'i Başlatılıyor...")

current_dir = Path(__file__).resolve().parent  # benchmark klasörü
root_dir = current_dir.parent                 # ana dizin

# 1. Model ve Tokenizer Yükleme
base_model_id = "unsloth/gemma-3-1b-it-unsloth-bnb-4bit"
print("📥 Base model yükleniyor...")
tokenizer = AutoTokenizer.from_pretrained(base_model_id)
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    device_map={"": "cpu"}
)

# 2. Doğru Klasör Adıyla LoRA Adaptörünü Entegre Etme
adapter_path = root_dir / "namaz-vakti-lora-adaptor"
if (adapter_path / "adapter_config.json").exists():
    print(f"🔗 LoRA Adaptörü başarıyla bulundu ve entegre ediliyor: {adapter_path}")
    model = PeftModel.from_pretrained(model, str(adapter_path))
else:
    print(f"⚠️ UYARI: '{adapter_path}' altında 'adapter_config.json' bulunamadı! Baz model ile devam ediliyor.")

model.eval()

# 3. Benchmark Verisini Okuma
benchmark_file = current_dir / "namaz_vakti_benchmark.jsonl"
with open(benchmark_file, "r", encoding="utf-8") as f:
    test_data = [json.loads(line) for line in f]

results = []
print(f"📊 Toplam {len(test_data)} test sorusu eğitilmiş LoRA modeline yöneltiliyor...")

# 4. Test Döngüsü
for idx, item in enumerate(test_data):
    messages = item["messages"]
    
    system_prompt = messages[0]["content"]
    user_prompt = messages[1]["content"]
    
    prompt = f"System: {system_prompt}\nUser: {user_prompt}\nAssistant:"
    
    inputs = tokenizer(prompt, return_tensors="pt")
    
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
    model_response = generated_text.split("Assistant:")[-1].strip()
    
    results.append({
        "id": idx + 1,
        "expected_user": user_prompt,
        "ground_truth_assistant": messages[2]["content"] if len(messages) > 2 else messages[1]["content"],
        "model_output": model_response
    })

# 5. Sonuçları Benchmark Klasörüne Kaydetme
output_file = current_dir / "benchmark_results.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"✅ İşlem tamam! LoRA destekli fıkhi sonuçlar '{output_file}' dosyasına kaydedildi.")