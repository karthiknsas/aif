"""Analysis and Summarization Tools"""
import os
from pathlib import Path
import json
import logging
from typing import List

from .base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class SummarizeFileTool(BaseTool):
    name = "summarize_file"
    description = "Summarize a text file. Input: file path"
    
    def _execute(self, path: str) -> ToolResult:
        path = path.strip()
        
        if not os.path.exists(path):
            return ToolResult(False, None, f"File not found: {path}")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return ToolResult(False, None, f"Read error: {e}")
        
        # Return content for LLM to summarize
        # The actual summarization happens in the LLM response
        word_count = len(content.split())
        char_count = len(content)
        line_count = len(content.splitlines())
        
        result = {
            "file": path,
            "stats": {
                "words": word_count,
                "characters": char_count,
                "lines": line_count
            },
            "content": content[:5000] if len(content) > 5000 else content,
            "truncated": len(content) > 5000
        }
        
        return ToolResult(True, json.dumps(result, indent=2))


class StoreInVectorDBTool(BaseTool):
    name = "store_in_vectordb"
    description = "Store document in vector database for retrieval. Input: 'filepath' or 'text|metadata_json'"
    
    def _execute(self, input_str: str) -> ToolResult:
        try:
            from vector import get_vector_store
            db = get_vector_store()
        except Exception as e:
            return ToolResult(False, None, f"Vector DB init failed: {e}")
        
        # Check if file path or text
        if os.path.exists(input_str.strip()):
            # It's a file
            path = input_str.strip()
            try:
                with open(path, "r") as f:
                    content = f.read()
                
                # Chunk the content
                chunks = self._chunk_text(content, chunk_size=500)
                ids = []
                for i, chunk in enumerate(chunks):
                    doc_id = db.add_text(
                        chunk, 
                        metadata={"source": path, "chunk": i, "total_chunks": len(chunks)}
                    )
                    ids.append(doc_id)
                
                return ToolResult(True, f"Stored {len(chunks)} chunks from {path}")
                
            except Exception as e:
                return ToolResult(False, None, f"Error: {e}")
        else:
            # It's text with optional metadata
            if "|" in input_str:
                text, meta_str = input_str.split("|", 1)
                try:
                    metadata = json.loads(meta_str)
                except:
                    metadata = {"raw_meta": meta_str}
            else:
                text = input_str
                metadata = {}
            
            try:
                doc_id = db.add_text(text.strip(), metadata)
                return ToolResult(True, f"Stored with ID: {doc_id}")
            except Exception as e:
                return ToolResult(False, None, f"Error: {e}")
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Simple chunking by characters with overlap"""
        chunks = []
        overlap = 50
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks


class SearchVectorDBTool(BaseTool):
    name = "search_vectordb"
    description = "Search vector database for relevant documents. Input: 'query' or 'query|top_k'"
    
    def _execute(self, input_str: str) -> ToolResult:
        try:
            from vector import get_vector_store
            db = get_vector_store()
        except Exception as e:
            return ToolResult(False, None, f"Vector DB init failed: {e}")
        
        if "|" in input_str:
            query, top_k_str = input_str.split("|", 1)
            try:
                top_k = int(top_k_str.strip())
            except:
                top_k = 5
        else:
            query = input_str
            top_k = 5
        
        try:
            results = db.search(query.strip(), top_k=top_k)
            
            output = []
            for r in results:
                output.append({
                    "score": round(r.score, 4),
                    "content": r.document.content[:500],
                    "metadata": r.document.metadata
                })
            
            return ToolResult(True, json.dumps(output, indent=2))
        except Exception as e:
            return ToolResult(False, None, f"Search error: {e}")


class AnalyzeCSVTool(BaseTool):
    name = "analyze_csv"
    description = "Perform statistical analysis on CSV. Input: 'filepath|analysis_type' (types: summary, correlation, distribution)"
    
    def _execute(self, input_str: str) -> ToolResult:
        import pandas as pd
        import numpy as np
        
        if "|" not in input_str:
            return ToolResult(False, None, "Format: 'filepath|analysis_type'")
        
        path, analysis = input_str.split("|", 1)
        path = path.strip()
        analysis = analysis.strip().lower()
        
        if not os.path.exists(path):
            return ToolResult(False, None, f"File not found: {path}")
        
        try:
            df = pd.read_csv(path)
        except Exception as e:
            return ToolResult(False, None, f"Load error: {e}")
        
        try:
            if analysis == "summary":
                result = {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.astype(str).to_dict(),
                    "describe": df.describe().to_dict(),
                    "nulls": df.isnull().sum().to_dict()
                }
            
            elif analysis == "correlation":
                numeric_df = df.select_dtypes(include=[np.number])
                if numeric_df.empty:
                    return ToolResult(False, None, "No numeric columns for correlation")
                corr = numeric_df.corr()
                result = {"correlation_matrix": corr.to_dict()}
            
            elif analysis == "distribution":
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                result = {}
                for col in numeric_cols:
                    result[col] = {
                        "mean": float(df[col].mean()),
                        "std": float(df[col].std()),
                        "min": float(df[col].min()),
                        "max": float(df[col].max()),
                        "median": float(df[col].median()),
                        "skew": float(df[col].skew())
                    }
            else:
                return ToolResult(False, None, f"Unknown analysis: {analysis}")
            
            return ToolResult(True, json.dumps(result, indent=2, default=str))
            
        except Exception as e:
            return ToolResult(False, None, f"Analysis error: {e}")
