"""
==============================================================================
SQLİTE VERİTABANI KULLANICI FETVA VE SORU KAYIT MODÜLÜ (DATABASE.PY)
==============================================================================
Bu dosya; kullanıcıların dini soru kayıtlarını, fetva taleplerini ve ibadet
notlarını yerel SQLite veritabanında (`islamic_assistant.db`) saklar.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "islamic_assistant.db")

def get_db_connection():
    """SQLite veritabanına bağlantı açar."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Veritabanı tablolarını oluşturur ve ilk durumu hazırlar."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            question TEXT NOT NULL,
            user_name TEXT DEFAULT 'Anonim',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_inquiry(topic: str, question: str, user_name: str = "Anonim") -> dict:
    """Yeni bir dini soru/fetva talebini veritabanına kaydeder (Veri Yazma)."""
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
            "message": f"Dini soru/fetva kaydı veritabanına başarıyla eklendi (Kayıt ID: #{record_id}).",
            "record": {
                "id": record_id,
                "topic": topic,
                "question": question,
                "user_name": user_name,
                "created_at": now_str
            }
        }
    except Exception as e:
        return {"status": "error", "message": f"Veritabanı kayıt hatası: {str(e)}"}

def get_all_inquiries() -> dict:
    """Veritabanındaki tüm soruları ve fetva taleplerini listeler (Veri Okuma)."""
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
        return {"status": "error", "message": f"Veritabanı okuma hatası: {str(e)}", "records": []}

if __name__ == "__main__":
    init_database()
    print("Database testi yapılıyor...")
    res = save_inquiry("Namaz", "Sehiv secdesi hangi durumlarda vacip olur?", "Ayşe Nur")
    print("Kayıt sonucu:", res)
    print("Tüm kayıtlar:", get_all_inquiries())
