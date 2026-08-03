import os
from jinja2 import Template

# Dosyanın bulunduğu klasörün tam yolunu alıyoruz (Böylece nereden çalıştırırsan çalıştır hata vermez)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JINJA_PATH = os.path.join(BASE_DIR, "chat_template.jinja")

# 1. Şablon dosyamızı okuyoruz
with open(JINJA_PATH, "r", encoding="utf-8") as f:
    template_str = f.read()

jinja_template = Template(template_str)

# 2. Örnek Araç (Tool) Tanımı (Namaz Vakti API'si için)
tools = [
    {
        "name": "get_namaz_vakti",
        "description": "Belirtilen şehir için namaz vakitlerini getirir.",
        "parameters": {
            "type": "object",
            "properties": {
                "sehir": {"type": "string", "description": "Şehir adı (Örn: İstanbul)"}
            },
            "required": ["sehir"]
        }
    }
]

# 3. Örnek Sohbet Geçmişi
messages = [
    {"role": "user", "content": "İstanbul için bugün akşam ezanı saat kaçta okunacak?"},
    {"role": "assistant", "content": "<tool_call>{\"name\": \"get_namaz_vakti\", \"arguments\": {\"sehir\": \"İstanbul\"}}</tool_call>"},
    {"role": "tool_response", "content": "{\"aksham\": \"20:15\"}"}
]

# 4. Şablonu Render Et (Çalıştır)
rendered_output = jinja_template.render(
    messages=messages,
    tools=tools,
    add_generation_prompt=True
)

print("="*60)
print("MODELİN GÖRECEĞİ HAM METİN (RAW PROMPT):")
print("="*60)
print(rendered_output)