"""
tools.py - Public API Entegrasyonları ve SQLite Veritabanı Araçları (Tool Call Definitions)
Bu modül; modelin çağırabileceği dış dünya API'sini (Aladhan Namaz Vakitleri API) 
ve veritabanı okuma/yazma araçlarını tanımlar.
"""

import requests

from database import save_inquiry, get_all_inquiries

def get_prayer_times(city: str, country: str = "Turkey") -> dict:
    """
    Tool 1: Diyanet metoduna göre belirtilen şehrin günlük namaz vakitlerini Aladhan Public API'sinden çeker.
    """
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=13"
        response = requests.get(url, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            timings = data["data"]["timings"]
            date_info = data["data"]["date"]["readable"]
            
            return {
                "status": "success",
                "city": city.title(),
                "country": country.title(),
                "date": date_info,
                "prayer_times": {
                    "İmsak": timings["Fajr"],
                    "Güneş": timings["Sunrise"],
                    "Öğle": timings["Dhuhr"],
                    "İkindi": timings["Asr"],
                    "Akşam": timings["Maghrib"],
                    "Yatsı": timings["Isha"]
                },
                "source": "Aladhan Public API (Diyanet Metodu)"
            }
        else:
            return {"status": "error", "message": f"API yanıt vermedi (HTTP Code: {response.status_code})"}
            
    except Exception as e:
        return {"status": "error", "message": f"Bağlantı hatası: {str(e)}"}

def save_inquiry_tool(topic: str, question: str, user_name: str = "Anonim") -> dict:
    """
    Tool 2: Kullanıcının fıkhi sorusunu SQLite veritabanına kaydeder (Veritabanı - Veri Yazma).
    """
    return save_inquiry(topic=topic, question=question, user_name=user_name)

def get_all_inquiries_tool() -> dict:
    """
    Tool 3: Veritabanındaki tüm soru ve fetva kayıtlarını listeler (Veritabanı - Veri Okuma).
    """
    return get_all_inquiries()

# Kullanılabilir araçlar sözlüğü
AVAILABLE_TOOLS = {
    "get_prayer_times": get_prayer_times,
    "save_inquiry_tool": save_inquiry_tool,
    "get_all_inquiries_tool": get_all_inquiries_tool
}

# Hafta 3.1 & 3.2 gereksinimi: Model için JSON Şeması (Tool Definitions)
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_prayer_times",
            "description": "Belirtilen şehir ve ülke için Diyanet metoduna göre günlük namaz vakitlerini çeker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Namaz vakti istenen şehir adı (ör: Istanbul, Ankara, Izmir, Malatya)"
                    },
                    "country": {
                        "type": "string",
                        "description": "Ülke adı. Varsayılan 'Turkey'.",
                        "default": "Turkey"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_inquiry_tool",
            "description": "Kullanıcının fıkhi sorusunu veya fetva danışmasını SQLite veritabanına kaydeder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Sorunun ana konusu (ör: Namaz, Oruç, Abdest, Sehiv Secdesi, Zekat)"
                    },
                    "question": {
                        "type": "string",
                        "description": "Kullanıcının sorduğu detaylı fıkhi soru"
                    },
                    "user_name": {
                        "type": "string",
                        "description": "Soruyu soran kişinin adı (Varsayılan: Anonim)",
                        "default": "Anonim"
                    }
                },
                "required": ["topic", "question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_inquiries_tool",
            "description": "Veritabanında kayıtlı tüm fıkhi soru ve fetva taleplerini listeler.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

if __name__ == "__main__":
    print("Test get_prayer_times('Istanbul'):", get_prayer_times("Istanbul"))