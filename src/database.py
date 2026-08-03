"""
====================================================================================
ÖDEV 2: VERİTABANI YÖNETİM MODÜLÜ (database.py)
====================================================================================
Bu dosya, asistanımızın dış dünya (yerel SQLite veritabanı) ile güvenli bir şekilde 
iletişim kurmasını sağlar.

Hugging Face Spaces Uyumlu Dayanıklılık:
- HF Spaces ortamlarında varsayılan dizin yazma korumalı olabilir.
- get_db_path() fonksiyonu önce yerel dizine yazmayı dener, korumalı ise geçici sistem 
  dizinine (tempfile) geçerek HİÇBİR ZAMAN ÇÖKME YAŞANMAZ.
====================================================================================
"""

import sqlite3
import os
import tempfile
from datetime import datetime

def get_db_path():
    """Hugging Face Space ve yerel ortamda yazma izinlerini kontrol ederek güvenli DB yolu döner."""
    local_path = os.path.join(os.path.dirname(__file__), "islamic_assistant.db")
    try:
        test_path = local_path + ".test"
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("test")
        if os.path.exists(test_path):
            os.remove(test_path)
        return local_path
    except Exception:
        # Yazma korumalı HF Space ortamlarında geçici klasöre geç
        return os.path.join(tempfile.gettempdir(), "islamic_assistant.db")

DB_PATH = get_db_path()

def get_db_connection():
    """Veritabanına güvenli bağlantı ve sqlite3.Row sözlük fabrikasını başlatır."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Uygulama açıldığında çalışır, yoksa tabloyu oluşturur ve eksik sütunları günceller."""
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
    
    cursor.execute("PRAGMA table_info(user_inquiries)")
    columns = [row['name'] for row in cursor.fetchall()]
    
    if "user_name" not in columns:
        cursor.execute("ALTER TABLE user_inquiries ADD COLUMN user_name TEXT DEFAULT 'Anonim'")
        
    conn.commit()
    conn.close()

def save_inquiry(topic: str, question: str, user_name: str = "Anonim") -> dict:
    """[TOOL CALL: VERİ YAZMA / WRITE] Soru/Fetva kaydını SQLite veritabanına ekler."""
    try:
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
            "message": f"Kayıt veritabanına başarıyla eklendi (Kayıt ID: #{record_id}).",
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
    """[TOOL CALL: VERİ OKUMA / READ ALL] Tüm soru ve fetva kayıtlarını çeker."""
    try:
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
        return {"status": "error", "message": f"Kayıtlar çekilirken hata oluştu: {str(e)}", "records": []}

def search_inquiries(keyword: str) -> dict:
    """[TOOL CALL: VERİ ARAMA / READ SEARCH] Kelimeye göre veritabanında arama yapar."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query_str = "%" + keyword + "%"
        cursor.execute(
            "SELECT id, topic, question, user_name, created_at FROM user_inquiries WHERE topic LIKE ? OR question LIKE ? ORDER BY id DESC",
            (query_str, query_str)
        )
        rows = cursor.fetchall()
        conn.close()
        
        records = [dict(row) for row in rows]
        return {
            "status": "success",
            "keyword": keyword,
            "match_count": len(records),
            "records": records
        }
    except Exception as e:
        return {"status": "error", "message": f"Arama yapılırken hata oluştu: {str(e)}", "records": []}

def delete_inquiry(record_id: int) -> dict:
    """[TOOL CALL: VERİ SİLME / DELETE] Belirli bir kaydı siler."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_inquiries WHERE id = ?", (record_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected > 0:
            return {"status": "success", "message": f"Kayıt #{record_id} veritabanından silindi."}
        else:
            return {"status": "error", "message": f"Kayıt #{record_id} bulunamadı."}
    except Exception as e:
        return {"status": "error", "message": f"Silme işleminde hata: {str(e)}"}

if __name__ == "__main__":
    init_database()
    print("Veritabanı yolu:", DB_PATH)
    print("Veritabanı başlatıldı.")