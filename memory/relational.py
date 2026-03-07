"""
SQLite relational database for structured data
"""

import structlog
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

logger = structlog.get_logger(__name__)


class RelationalDB:
    """SQLite database for sessions, users, and structured logs"""
    
    def __init__(self, config):
        self.config = config
        
        db_path = config.get("memory.relational_db.path", "./data/jarvis.db")
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        logger.info("Initializing relational database", path=db_path)
        
        self._create_tables()
        
        logger.info("✓ Relational database ready")
        
    def _create_tables(self):
        """Create database schema"""
        cursor = self.conn.cursor()
        
        # Sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            start_time TEXT NOT NULL,
            end_time TEXT,
            utterance_count INTEGER DEFAULT 0,
            action_count INTEGER DEFAULT 0,
            metadata TEXT
        )
        """)
        
        # Utterances table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS utterances (
            utterance_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            source TEXT,
            text TEXT NOT NULL,
            stt_confidence REAL,
            intent TEXT,
            intent_confidence REAL,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        """)
        
        # Actions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            action_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            command_id TEXT,
            timestamp TEXT NOT NULL,
            status TEXT,
            steps_total INTEGER,
            steps_completed INTEGER,
            error TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        """)
        
        # User preferences table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            type TEXT,
            updated_at TEXT NOT NULL
        )
        """)
        
        self.conn.commit()
        
    def create_session(self, session_id: str, metadata: Optional[Dict] = None) -> bool:
        """Create new session"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO sessions (session_id, start_time, metadata)
            VALUES (?, ?, ?)
            """, (
                session_id,
                datetime.now().isoformat(),
                json.dumps(metadata) if metadata else None
            ))
            self.conn.commit()
            logger.info("Session created", session_id=session_id)
            return True
        except Exception as e:
            logger.error("Failed to create session", error=str(e))
            return False
            
    def log_utterance(self, utterance) -> bool:
        """Log utterance to database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO utterances (
                utterance_id, session_id, timestamp, source, text,
                stt_confidence, intent, intent_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                utterance.utterance_id,
                utterance.session_id,
                utterance.timestamp.isoformat(),
                utterance.source,
                utterance.text,
                utterance.stt_confidence,
                None,  # Will be updated later
                None
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("Failed to log utterance", error=str(e))
            return False
            
    def log_action(self, action_id: str, session_id: str, command_id: str,
                   steps_total: int, status: str = "pending") -> bool:
        """Log action execution"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO actions (
                action_id, session_id, command_id, timestamp,
                status, steps_total, steps_completed
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                action_id,
                session_id,
                command_id,
                datetime.now().isoformat(),
                status,
                steps_total,
                0
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("Failed to log action", error=str(e))
            return False
            
    def update_action_status(self, action_id: str, status: str, 
                           steps_completed: int = None, error: str = None) -> bool:
        """Update action status"""
        try:
            cursor = self.conn.cursor()
            if error:
                cursor.execute("""
                UPDATE actions SET status = ?, steps_completed = ?, error = ?
                WHERE action_id = ?
                """, (status, steps_completed, error, action_id))
            else:
                cursor.execute("""
                UPDATE actions SET status = ?, steps_completed = ?
                WHERE action_id = ?
                """, (status, steps_completed, action_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("Failed to update action", error=str(e))
            return False
            
    def get_recent_utterances(self, limit: int = 10) -> List[Dict]:
        """Get recent utterances"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM utterances
        ORDER BY timestamp DESC
        LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    def close(self):
        """Close database connection"""
        self.conn.close()
        logger.info("Database connection closed")
