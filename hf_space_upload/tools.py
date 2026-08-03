"""
====================================================================================
ÖDEV 2: ARAÇ DÜZEYİ (TOOLS.PY) VE JSON ŞEMASI TANIMLARI
====================================================================================
Bu modül, modelin dış dünya ile iletişim kurabildiği köprüdür.
Burada hem gerçek API bağlantıları (Aladhan Public API) hem de SQLite veritabanı 
işlemleri (Veri Yazma, Okuma, Arama) Python fonksiyonları olarak sarılır (wrap edilir).

Ayrıca modelin bu fonksiyonların adlarını, ne işe yaradıklarını ve hangi parametreleri 
aldıklarını anlayabilmesi için OpenAI / Hugging Face uyumlu `TOOLS_SCHEMA` JSON şeması 
tanımlanmıştır.
====================================================================================
"""

import requests
from database import save_inquiry, get_all_inquiries, search_inquiries, delete_inquiry

# ----------------------------------------------------------------------------------
# 1. HARİCİ PUBLIC API ARACI: ALADHAN NAMAZ VAKİTLERİ (READ)
# ----------------------------------------------------------------------------------
def get_prayer_times(city: str, country: str = "Turkey") -> dict:
    """
    Tool 1: Belirtilen şehir ve ülke için Aladhan API üzerinden Diyanet metoduna (Method 13) 
    göre anlık namaz vakitlerini çeker.
    
    Args:
        city (str): Şehir adı (ör: Istanbul, Ankara, Malatya)
        country (str): Ülke adı (varsayılan: Turkey)
    """
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=13"
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
                    "İmsak": timings["Fajr"],
                    "Güneş": timings["Sunrise"],
                    "Öğle": timings["Dhuhr"],
                    "İkindi": timings["Asr"],
                    "Akşam": timings["Maghrib"],
                    "Yatsı": timings["Isha"]
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
    """
    Tool 2: Fıkhi soru veya fetva danışma kaydını veritabanına ekler (WRITE).
    """
    return save_inquiry(topic=topic, question=question, user_name=user_name)

def get_all_inquiries_tool() -> dict:
    """
    Tool 3: Veritabanında saklanan tüm geçmiş soru ve fetva kayıtlarını listeler (READ ALL).
    """
    return get_all_inquiries()

def search_inquiries_tool(keyword: str) -> dict:
    """
    Tool 4: Veritabanında belirtilen kelimeye göre arama yapar (READ SEARCH).
    """
    return search_inquiries(keyword=keyword)

# ----------------------------------------------------------------------------------
# ARAÇ HARİTASI (AVAILABLE_TOOLS DICTIONARY)
# ----------------------------------------------------------------------------------
# Model bir fonksiyon adını döndürdüğünde Python'da o fonksiyonu ismiyle bulup tetiklememizi sağlar.
AVAILABLE_TOOLS = {
    "get_prayer_times": get_prayer_times,
    "save_inquiry_tool": save_inquiry_tool,
    "get_all_inquiries_tool": get_all_inquiries_tool,
    "search_inquiries_tool": search_inquiries_tool
}

# ----------------------------------------------------------------------------------
# MODEL İÇİN JSON ŞEMASI (TOOLS SCHEMA)
# ----------------------------------------------------------------------------------
# Modelin fonksiyon isimlerini, amaçlarını ve beklediği argüman türlerini öğrenmesini sağlar.
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_prayer_times",
            "description": "Belirtilen şehir için Diyanet İşleri metoduna göre günlük imsak, güneş, öğle, ikindi, akşam ve yatsı namaz vakitlerini çeker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Namaz vakti öğrenilmek istenen şehir adı (ör: Istanbul, Ankara, Izmir, Malatya, Bursa)"
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
    print("Test API Call (Istanbul):", get_prayer_times("Istanbul"))
    print("Test Search Tool ('namaz'):", search_inquiries_tool("namaz"))