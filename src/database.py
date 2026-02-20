"""Database setup and operations for the AI pipeline."""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class Database:
    """Handles all database operations."""
    
    def __init__(self, db_path: str = "data/pipeline.db"):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    source VARCHAR(255),
                    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    word_count INTEGER,
                    char_count INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    sentiment VARCHAR(20),
                    sentiment_confidence REAL,
                    summary TEXT,
                    topics TEXT,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ai_model VARCHAR(50),
                    FOREIGN KEY (document_id) REFERENCES documents(id)
                );
                
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    entity_text VARCHAR(255),
                    entity_type VARCHAR(50),
                    FOREIGN KEY (document_id) REFERENCES documents(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_sentiment ON analyses(sentiment);
                CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(entity_type);
                CREATE INDEX IF NOT EXISTS idx_ingested_at ON documents(ingested_at);
            """)
    
    def insert_document(self, content: str, source: str) -> int:
        """Insert a new document and return its ID."""
        word_count = len(content.split())
        char_count = len(content)
        
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO documents (content, source, word_count, char_count) VALUES (?, ?, ?, ?)",
                (content, source, word_count, char_count)
            )
            return cursor.lastrowid
    
    def insert_analysis(self, document_id: int, sentiment: str, confidence: float,
                       summary: str, topics: str, ai_model: str) -> int:
        """Insert analysis results."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO analyses 
                   (document_id, sentiment, sentiment_confidence, summary, topics, ai_model)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (document_id, sentiment, confidence, summary, topics, ai_model)
            )
            return cursor.lastrowid
    
    def insert_entities(self, document_id: int, entities: List[Dict[str, str]]):
        """Insert extracted entities."""
        with self.get_connection() as conn:
            conn.executemany(
                "INSERT INTO entities (document_id, entity_text, entity_type) VALUES (?, ?, ?)",
                [(document_id, e['text'], e['type']) for e in entities]
            )
    
    def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve document with analysis and entities."""
        with self.get_connection() as conn:
            doc = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
            
            if not doc:
                return None
            
            analysis = conn.execute(
                "SELECT * FROM analyses WHERE document_id = ?", (document_id,)
            ).fetchone()
            
            entities = conn.execute(
                "SELECT entity_text, entity_type FROM entities WHERE document_id = ?",
                (document_id,)
            ).fetchall()
            
            return {
                "document": dict(doc),
                "analysis": dict(analysis) if analysis else None,
                "entities": [dict(e) for e in entities]
            }
    
    def list_documents(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List all documents with basic info."""
        with self.get_connection() as conn:
            docs = conn.execute(
                """SELECT d.id, d.source, d.ingested_at, d.word_count,
                          a.sentiment, a.sentiment_confidence
                   FROM documents d
                   LEFT JOIN analyses a ON d.id = a.document_id
                   ORDER BY d.ingested_at DESC
                   LIMIT ? OFFSET ?""",
                (limit, offset)
            ).fetchall()
            return [dict(doc) for doc in docs]
    
    def search_documents(self, sentiment: Optional[str] = None,
                        entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search documents by filters."""
        query = """
            SELECT DISTINCT d.id, d.source, d.ingested_at, a.sentiment
            FROM documents d
            LEFT JOIN analyses a ON d.id = a.document_id
            LEFT JOIN entities e ON d.id = e.document_id
            WHERE 1=1
        """
        params = []
        
        if sentiment:
            query += " AND a.sentiment = ?"
            params.append(sentiment)
        
        if entity_type:
            query += " AND e.entity_type = ?"
            params.append(entity_type)
        
        query += " ORDER BY d.ingested_at DESC"
        
        with self.get_connection() as conn:
            results = conn.execute(query, params).fetchall()
            return [dict(r) for r in results]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        with self.get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) as count FROM documents").fetchone()['count']
            
            sentiment_breakdown = conn.execute("""
                SELECT sentiment, COUNT(*) as count
                FROM analyses
                GROUP BY sentiment
            """).fetchall()
            
            return {
                "total_documents": total,
                "sentiment_breakdown": {row['sentiment']: row['count'] for row in sentiment_breakdown}
            }
