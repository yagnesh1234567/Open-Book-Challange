"""Main pipeline orchestrator."""

import json
from typing import Dict, Any
from .database import Database
from .ai_analyzer import AIAnalyzer


class Pipeline:
    """Orchestrates the complete text processing pipeline."""
    
    def __init__(self, db_path: str = "data/pipeline.db", 
                 ai_provider: str = "openai", ai_model: str = None):
        self.db = Database(db_path)
        self.analyzer = AIAnalyzer(provider=ai_provider, model=ai_model)
    
    def ingest(self, text: str, source: str = "api") -> Dict[str, Any]:
        """
        Complete ingestion pipeline: validate -> store -> analyze -> save results.
        
        Args:
            text: Document text to process
            source: Source identifier (e.g., "api", "file", "manual")
        
        Returns:
            {
                "document_id": int,
                "status": "success" | "error",
                "analysis": {...},
                "message": str
            }
        """
        # Validation
        if not text or not text.strip():
            return {"status": "error", "message": "Empty text provided"}
        
        if len(text) > 100000:  # 100k char limit
            return {"status": "error", "message": "Text too large (max 100k characters)"}
        
        try:
            # Store document
            doc_id = self.db.insert_document(text, source)
            
            # AI analysis
            analysis = self.analyzer.analyze(text)
            
            # Store analysis results
            self.db.insert_analysis(
                document_id=doc_id,
                sentiment=analysis["sentiment"],
                confidence=analysis["sentiment_confidence"],
                summary=analysis["summary"],
                topics=json.dumps(analysis["topics"]),
                ai_model=analysis["model"]
            )
            
            # Store entities
            if analysis["entities"]:
                self.db.insert_entities(doc_id, analysis["entities"])
            
            return {
                "document_id": doc_id,
                "status": "success",
                "analysis": analysis,
                "message": "Document processed successfully"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Processing failed: {str(e)}"
            }
    
    def retrieve(self, document_id: int) -> Dict[str, Any]:
        """Retrieve document with full analysis."""
        result = self.db.get_document(document_id)
        if not result:
            return {"status": "error", "message": "Document not found"}
        
        # Parse topics JSON
        if result["analysis"] and result["analysis"]["topics"]:
            result["analysis"]["topics"] = json.loads(result["analysis"]["topics"])
        
        return {"status": "success", "data": result}
    
    def list_all(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List all documents."""
        docs = self.db.list_documents(limit, offset)
        return {"status": "success", "documents": docs, "count": len(docs)}
    
    def search(self, sentiment: str = None, entity_type: str = None) -> Dict[str, Any]:
        """Search documents by filters."""
        results = self.db.search_documents(sentiment, entity_type)
        return {"status": "success", "results": results, "count": len(results)}
    
    def stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        stats = self.db.get_stats()
        return {"status": "success", "stats": stats}
