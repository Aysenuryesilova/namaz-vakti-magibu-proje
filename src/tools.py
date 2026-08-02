"""
tools.py - Tool Calling Fonksiyonları ve Şemaları
Bu dosya, modelin dış dünya ile iletişim kurmasını sağlar. Aladhan API ve SQLite 
veritabanı işlemlerini modelin çağırabileceği fonksiyonlar haline getirir.
"""

import requests
from database import save_inquiry, get_all_inquiries

def get_prayer_times(city: str, country: str = "Turkey") -> dict:
    """
    Tool 1: Belirtilen şehir için Aladhan API'den namaz vakitlerini çeker (Veri Okuma).
    """
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=13"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 200:
            timings = data["data"]["timings"]
            return {
                "status": "success",
                "city": city,
                "prayer_times": {
                    "Imsak": timings.get("Fajr"),
                    "Gunes": timings.get("Sunrise"),
                    "Ogle": timings.get("Dhuhr"),
                    "Ikindi": timings.get("Asr"),
                    "Aksam": timings.get("Maghrib"),
                    "Yatsi": timings.get("Isha")
                },
                "source": "Aladhan API (Diyanet Metodu)"
            }
        else:
            return {"status": "error", "message": "Vakit bilgisi alınamadı."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_user_inquiry(topic: str, question: str) -> dict:
    """
    Tool 2: Kullanıcının sorduğu fıkhi soruyu veya talebi SQLite veritabanına kaydeder (Veri Yazma).
    """
    try:
        inquiry_id = save_inquiry(topic, question)
        return {
            "status": "success",
            "message": f"Talebiniz başarıyla veritabanına kaydedildi. Kayıt ID: {inquiry_id}",
            "inquiry_id": inquiry_id,
            "topic": topic,
            "question": question
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_user_inquiries() -> dict:
    """
    Tool 3: Veritabanındaki kayıtlı soru ve talepleri listeler (Veri Okuma).
    """
    try:
        inquiries = get_all_inquiries()
        return {
            "status": "success",
            "total_records": len(inquiries),
            "inquiries": inquiries,
            "source": "SQLite Yerel Veritabanı"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Modelin hangi araçları çağırabileceğini anladığı JSON Şema Tanımları (Tool Schema)
TOOLS_SCHEMA = [
    {
        "name": "get_prayer_times",
        "description": "Türkiye veya dünya şehirlerinin günlük namaz/ezan vakitlerini getirir.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Şehir adı (Örn: Ankara, Istanbul)"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "create_user_inquiry",
        "description": "Kullanıcının fıkhi sorusunu veya fetva talebini SQLite veritabanına kaydeder.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Konu başlığı (Örn: Abdest, Oruç, Namaz)"},
                "question": {"type": "string", "description": "Kullanıcının sorduğu soru veya talep metni"}
            },
            "required": ["topic", "question"]
        }
    },
    {
        "name": "list_user_inquiries",
        "description": "Veritabanında kayıtlı olan tüm soru ve talepleri listeler.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]

# Fonksiyon isimlerini gerçek python fonksiyonlarıyla eşleştiren harita (Dictionary)
AVAILABLE_TOOLS = {
    "get_prayer_times": get_prayer_times,
    "create_user_inquiry": create_user_inquiry,
    "list_user_inquiries": list_user_inquiries
}