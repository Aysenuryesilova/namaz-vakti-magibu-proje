"""
database.py - SQLite Veritabanı ve Tablo Yönetimi
Bu dosya, kullanıcıların fetva taleplerini, fıkhi soru kayıtlarını ve ibadet 
notlarını güvenle saklayacağımız yerel SQLite veritabanını (`islamic_assistant.db`) kurar.
"""

import sqlite3
import os
from datetime import datetime

# Veritabanı dosya yolu (src klasörü içinde saklanır)
DB_PATH = os.path.join(os.path.dirname(__file__), "islamic_assistant.db")

def get_db_connection():
    """Veritabanına güvenli bir bağlantı açar."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """
    Uygulama ilk açıldığında çalışır. Tablo şemasının doğru olduğundan emin olur.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Var olan tablo yapısını denetle, yoksa veya eski ise yeniden oluştur
    cursor.execute("PRAGMA table_info(user_inquiries)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if not columns or "user_name" not in columns:
        cursor.execute("DROP TABLE IF EXISTS user_inquiries")
        cursor.execute("""
            CREATE TABLE user_inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                user_name TEXT DEFAULT 'Anonim',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Örnek başlangıç verileri
        sample_records = [
            ("Namaz", "Sehiv secdesi hangi durumlarda vacip olur?", "Ayşe Nur", "2026-07-26 14:30:00"),
            ("Oruç", "Unutarak bir şey yemek veya içmek orucu bozar mı?", "Mehmet", "2026-07-28 10:15:00"),
            ("Abdest", "Abdest alırken sırayı karıştırmak abdesti geçersiz kılar mı?", "Fatma", "2026-08-01 09:00:00")
        ]
        cursor.executemany(
            "INSERT INTO user_inquiries (topic, question, user_name, created_at) VALUES (?, ?, ?, ?)",
            sample_records
        )
        conn.commit()
        
    conn.close()

def save_inquiry(topic: str, question: str, user_name: str = "Anonim") -> dict:
    """
    Tool Call: Veri Yazma (Write) İşlemi.
    Kullanıcının fıkhi sorusunu veya fetva kaydını SQLite veritabanına ekler.
    """
    try:
        init_database()
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO user_inquiries (topic, question, user_name, created_at) VALUES (?, ?, ?, ?)",
            (topic, question, user_name, now_str)
        )
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return {
            "status": "success",
            "message": f"Soru/Fetva kaydı veritabanına başarıyla eklendi (Kayıt ID: #{record_id}).",
            "record": {
                "id": record_id,
                "topic": topic,
                "question": question,
                "user_name": user_name,
                "created_at": now_str
            }
        }
    except Exception as e:
        return {"status": "error", "message": f"Veritabanına kaydederken hata oluştu: {str(e)}"}

def get_all_inquiries() -> dict:
    """
    Tool Call: Veri Okuma (Read) İşlemi.
    Veritabanındaki tüm soru ve fetva kayıtlarını çekip liste halinde döndürür.
    """
    try:
        init_database()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, topic, question, user_name, created_at FROM user_inquiries ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        records = [dict(row) for row in rows]
        return {
            "status": "success",
            "total_count": len(records),
            "records": records
        }
    except Exception as e:
        return {"status": "error", "message": f"Kayıtları okurken hata oluştu: {str(e)}", "records": []}

if __name__ == "__main__":
    init_database()
    print("Database test başlatılıyor...")
    res = save_inquiry("Namaz", "Teheccüd namazı kaç rekat kılınır?", "Ayşe Nur")
    print("Kaydedildi:", res)
    print("Tüm Kayıtlar:", get_all_inquiries())