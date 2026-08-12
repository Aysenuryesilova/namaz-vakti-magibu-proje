"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN - SQLITE VERİTABANI YÖNETİMİ (DATABASE.PY)
==============================================================================
BU MODÜL NEYİ SAĞLAR? (EĞİTİCİ AÇIKLAMA):
------------------------------------------------------------------------------
1. İlişkisel Veritabanı (Relational SQLite DB):
   Kullanıcıların sorduğu dini soruları, fetva taleplerini ve asistan yanıtlarını
   kalıcı olarak `islamic_assistant.db` veritabanı dosyasında saklar. Uygulama
   kapatılıp açılsa dahi geçmiş veriler kaybolmaz.

2. CRUD İşlemleri (Create, Read, Update, Delete):
   - `save_inquiry`: Yeni soru ve fetva kaydı oluşturur (CREATE).
   - `get_all_inquiries`: Saklanan tüm soruları listeler (READ).
==============================================================================
"""

import sqlite3
import os
from datetime import datetime

# Veritabanı Dosya Yolu
DB_PATH = os.path.join(os.path.dirname(__file__), "islamic_assistant.db")

def get_connection():
    """
    SQLite Veritabanı Bağlantı Oluşturucu:
    Veritabanı dosyası yoksa otomatik oluşturur ve bağlantı nesnesini döndürür.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Sütun isimlerine sözlük mantığıyla erişmeyi sağlar
    return conn

def init_database():
    """
    Veritabanı Tablosu İlklendirici (Schema Creation):
    `user_inquiries` tablosunu otomatik oluşturur. Tablo yapısı:
    - id          : Otomatik artan birincil anahtar (Primary Key)
    - topic       : Konu kategorisi (Örn: Namaz, Zekat, Fıkıh)
    - question    : Kullanıcının sorduğu detaylı soru metni
    - user_name   : Soruyu soran kullanıcı adı
    - created_at  : Kayıt oluşturulma zaman damgası
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                user_name TEXT DEFAULT 'Anonim',
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

def save_inquiry(topic: str, question: str, user_name: str = "Anonim") -> dict:
    """
    Veritabanına Yeni Soru Kaydetme Fonksiyonu (Data Writing):
    SQL INSERT INTO sorgusuyla yeni veri ekler.
    """
    try:
        init_database()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_inquiries (topic, question, user_name, created_at)
                VALUES (?, ?, ?, ?)
            """, (topic, question, user_name, now_str))
            conn.commit()
            new_id = cursor.lastrowid
            
        return {
            "status": "success",
            "message": "Soru veritabanına başarıyla kaydedildi.",
            "record": {
                "id": new_id,
                "topic": topic,
                "question": question,
                "user_name": user_name,
                "created_at": now_str
            }
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

def get_all_inquiries() -> dict:
    """
    Veritabanındaki Tüm Soruları Listeleme Fonksiyonu (Data Reading):
    SQL SELECT * FROM sorgusuyla geçmiş verileri okur.
    """
    try:
        init_database()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_inquiries ORDER BY id DESC")
            rows = cursor.fetchall()
            
            records = [
                {
                    "id": row["id"],
                    "topic": row["topic"],
                    "question": row["question"],
                    "user_name": row["user_name"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
            return {
                "status": "success",
                "total_count": len(records),
                "records": records
            }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "records": []}

if __name__ == "__main__":
    # Veritabanı Testi
    init_database()
    save_inquiry("Namaz", "Sehiv secdesi ne zaman yapılır?", "Ayşenur")
    res = get_all_inquiries()
    print("SQLite DB Test Kayıtları Toplamı:", res["total_count"])
