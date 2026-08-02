"""
database.py - SQLite Veritabanı ve Tablo Yönetimi
Bu dosya, kullanıcıların fetva taleplerini, fıkhi soru kayıtlarını ve ibadet 
notlarını güvenle saklayacağımız yerel SQLite veritabanını (`islamic_assistant.db`) kurar.
"""

import sqlite3
import os

DB_NAME = "islamic_assistant.db"

def get_db_connection():
    """Veritabanına güvenli bir bağlantı açar."""
    conn = sqlite3.connect(DB_NAME)
    # Veri satırlarını sözlük (dictionary) şeklinde alabilmek için satır fabrikası ayarlanır
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """
    Uygulama ilk açıldığında çalışır. Eğer yoksa veritabanı tablosunu oluşturur.
    Bu sayede veri yazma (INSERT) ve okuma (SELECT) işlemlerini yapabileceğimiz bir alanımız olur.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Kullanıcı soru ve fetva talepleri için tablo oluşturuyoruz
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            question TEXT NOT NULL,
            status TEXT DEFAULT 'Beklemede',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Başlangıç için örnek bir veri yazalım (Veri Yazma Testi)
    cursor.execute("SELECT COUNT(*) FROM user_inquiries")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("""
            INSERT INTO user_inquiries (topic, question, status) 
            VALUES ('Abdest', 'Yaraya sürülen merhem abdest geçtirir mi?', 'Cevaplandı')
        """)
        conn.commit()
        
    conn.close()

def save_inquiry(topic: str, question: str) -> int:
    """
    Veri Yazma (INSERT): Kullanıcının sorduğu yeni bir soruyu veya talebi veritabanına kaydeder.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_inquiries (topic, question, status)
        VALUES (?, ?, 'Beklemede')
    """, (topic, question))
    conn.commit()
    inquiry_id = cursor.lastrowid
    conn.close()
    return inquiry_id

def get_all_inquiries() -> list:
    """
    Veri Okuma (SELECT): Veritabanındaki tüm kayıtları listeler.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_inquiries ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]