"""
====================================================================================
ÖDEV 2: ARAÇ DÜZEYİ (TOOLS.PY) VE JSON ŞEMASI TANIMLARI
====================================================================================
Bu modül, modelin dış dünya ile iletişim kurabildiği köprüdür.
Tüm 81 ilimiz ve dünya şehirleri için Aladhan Public API entegrasyonu ve SQLite 
veritabanı işlemlerini barındırır.
====================================================================================
"""

import requests
from database import save_inquiry, get_all_inquiries, search_inquiries, delete_inquiry

def normalize_city_name(city: str) -> str:
    """Türkçe karakterleri ASCII Karakterlerine dönüştürür (Aladhan API uyumluluğu için)."""
    char_map = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'I': 'I', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    return "".join(char_map.get(c, c) for c in city)

# ----------------------------------------------------------------------------------
# 1. HARİCİ PUBLIC API ARACI: ALADHAN NAMAZ VAKİTLERİ (READ)
# ----------------------------------------------------------------------------------
def get_prayer_times(city: str, country: str = "Turkey") -> dict:
    """
    Tool 1: Belirtilen şehir ve ülke için Aladhan API üzerinden Diyanet metoduna (Method 13) 
    göre anlık namaz vakitlerini çeker.
    
    Args:
        city (str): Şehir adı (ör: Bitlis, Istanbul, Ankara, Malatya, Van, Hakkari, Izmir)
        country (str): Ülke adı (varsayılan: Turkey)
    """
    try:
        clean_city = normalize_city_name(city.strip())
        url = f"https://api.aladhan.com/v1/timingsByCity?city={clean_city}&country={country}&method=13"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Eğer orijinal adla gelmediyse ham adı da deneyelim
        if response.status_code != 200 or data.get("code") != 200:
            url = f"https://api.aladhan.com/v1/timingsByCity?city={city.strip()}&country={country}&method=13"
            response = requests.get(url, timeout=10)
            data = response.json()

        if response.status_code == 200 and data.get("code") == 200:
            timings = data["data"]["timings"]
            date_info = data["data"]["date"]["readable"]
            
            return {
                "status": "success",
                "city": city.title(),
                "country": country.title(),
                "date": date_info,
                "prayer_times": {
                    "İmsak": timings.get("Fajr"),
                    "Güneş": timings.get("Sunrise"),
                    "Öğle": timings.get("Dhuhr"),
                    "İkindi": timings.get("Asr"),
                    "Akşam": timings.get("Maghrib"),
                    "Yatsı": timings.get("Isha")
                },
                "source": "Aladhan Public API (Diyanet Metodu - Method 13)"
            }
        else:
            return {"status": "error", "message": f"{city} şehri için namaz vakitleri alınamadı."}
    except Exception as e:
        return {"status": "error", "message": f"Aladhan API bağlantı hatası: {str(e)}"}

# ----------------------------------------------------------------------------------
# 2. VERİTABANI ARAÇLARI (WRITE, READ ALL, READ SEARCH)
# ----------------------------------------------------------------------------------
def save_inquiry_tool(topic: str, question: str, user_name: str = "Anonim") -> dict:
    """Tool 2: Fıkhi soru veya fetva danışma kaydını veritabanına ekler (WRITE)."""
    return save_inquiry(topic=topic, question=question, user_name=user_name)

def get_all_inquiries_tool() -> dict:
    """Tool 3: Veritabanında saklanan tüm geçmiş soru ve fetva kayıtlarını listeler (READ ALL)."""
    return get_all_inquiries()

def search_inquiries_tool(keyword: str) -> dict:
    """Tool 4: Veritabanında belirtilen kelimeye göre arama yapar (READ SEARCH)."""
    return search_inquiries(keyword=keyword)

AVAILABLE_TOOLS = {
    "get_prayer_times": get_prayer_times,
    "save_inquiry_tool": save_inquiry_tool,
    "get_all_inquiries_tool": get_all_inquiries_tool,
    "search_inquiries_tool": search_inquiries_tool
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_prayer_times",
            "description": "Belirtilen şehir (Tüm 81 il ve dünya şehirleri) için Diyanet İşleri metoduna göre günlük imsak, güneş, öğle, ikindi, akşam ve yatsı namaz vakitlerini çeker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Namaz vakti öğrenilmek istenen şehir adı (ör: Bitlis, Istanbul, Ankara, Izmir, Malatya, Van, Hakkari)"
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
            "description": "Kullanıcının ilettiği fıkhi soruyu veya fetva talebini veritabanına kaydeder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Sorunun konusu (ör: Namaz, Oruç, Abdest, Sehiv Secdesi, Zekat)"
                    },
                    "question": {
                        "type": "string",
                        "description": "Kullanıcının sorduğu detaylı soru metni"
                    },
                    "user_name": {
                        "type": "string",
                        "description": "Soruyu ileten kişinin adı (Varsayılan: Anonim)",
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
            "description": "Veritabanına daha önce kaydedilmiş tüm soru ve fetva taleplerini listeler.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_inquiries_tool",
            "description": "Veritabanındaki sorular arasında konu veya soru metnine göre kelime bazlı arama yapar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Veritabanında aranacak anahtar kelime (ör: sehiv, namaz, kaza)"
                    }
                },
                "required": ["keyword"]
            }
        }
    }
]

if __name__ == "__main__":
    print("Test Bitlis Prayer Times:", get_prayer_times("Bitlis"))