import sqlite3
import os
from typing import Optional
from datetime import datetime

class DedupStore:
    """
    Menyimpan event_id yang sudah diproses ke SQLite
    Tujuan: deteksi duplikasi dan tahan restart
    """
    
    def __init__(self, db_path: str = "data/dedup.db"):
        self.db_path = db_path
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Buat tabel jika belum ada
        self._init_db()
    
    def _init_db(self):
        """Inisialisasi database dan tabel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_events (
                topic TEXT NOT NULL,
                event_id TEXT NOT NULL,
                processed_at TEXT NOT NULL,
                PRIMARY KEY (topic, event_id)
            )
        """)
        
        # Index untuk query cepat
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_id 
            ON processed_events(event_id)
        """)
        
        conn.commit()
        conn.close()
    
    def is_duplicate(self, topic: str, event_id: str) -> bool:
        """
        Cek apakah event sudah pernah diproses
        Return: True jika duplikat, False jika baru
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM processed_events WHERE topic = ? AND event_id = ? LIMIT 1",
            (topic, event_id)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def mark_processed(self, topic: str, event_id: str) -> bool:
        """
        Tandai event sebagai sudah diproses
        Return: True jika berhasil, False jika sudah ada (race condition)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO processed_events (topic, event_id, processed_at)
                VALUES (?, ?, ?)
                """,
                (topic, event_id, datetime.utcnow().isoformat())
            )
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            # Sudah ada (PRIMARY KEY conflict)
            return False
    
    def get_total_processed(self) -> int:
        """Hitung total event unik yang sudah diproses"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM processed_events")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_topics(self) -> dict:
        """Hitung jumlah event per topic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT topic, COUNT(*) as count 
            FROM processed_events 
            GROUP BY topic
        """)
        
        topics = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        return topics
