import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import pickle
import os
from app.core.config import get_settings

settings = get_settings()

class VectorStore:
    """
    FAISS Vector Database - RAG এর জন্য
    
    Features:
    - Embedding generation (Sentence Transformers)
    - Similarity search
    - Metadata storage
    - Persistence (save/load)
    
    Use cases:
    - PDF content search
    - Semantic search
    - Document retrieval
    """
    
    def __init__(self, embedding_model: str = None):
        # Embedding model load করবে
        self.model_name = embedding_model or settings.EMBEDDING_MODEL
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # FAISS index তৈরি করবে
        # IndexFlatL2 = Exact search (slower but accurate)
        # For production: IndexIVFFlat for faster approximate search
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Metadata store করবে (FAISS শুধু vectors store করে)
        self.metadata = []  # List of dicts
        self.id_to_idx = {}  # Document ID to index mapping
    
    def add_texts(
        self, 
        texts: List[str], 
        metadatas: List[Dict] = None,
        ids: List[str] = None
    ) -> List[int]:
        """
        Texts কে embed করে vector DB তে add করবে
        
        Args:
            texts: List of text chunks
            metadatas: Optional metadata for each chunk
            ids: Optional custom IDs
        
        Returns: List of vector IDs
        """
        # Embeddings generate করবে
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # FAISS index এ add করবে
        start_idx = self.index.ntotal  # Current total vectors
        self.index.add(embeddings.astype('float32'))
        
        # Metadata store করবে
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        vector_ids = []
        for i, (text, metadata) in enumerate(zip(texts, metadatas)):
            idx = start_idx + i
            vector_ids.append(idx)
            
            # Store metadata with text
            self.metadata.append({
                "text": text,
                "id": ids[i] if ids else idx,
                **metadata
            })
            
            if ids:
                self.id_to_idx[ids[i]] = idx
        
        return vector_ids
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5,
        filter_metadata: Dict = None
    ) -> List[Tuple[str, float, Dict]]:
        """
        Semantic similarity search করবে
        
        Args:
            query: Search query
            k: Number of results
            filter_metadata: Optional metadata filter
        
        Returns: [(text, score, metadata), ...]
        """
        # Query embedding generate করবে
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search করবে
        # distances: L2 distances (lower = more similar)
        # indices: Vector indices
        distances, indices = self.index.search(
            query_embedding.astype('float32'), 
            k
        )
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                
                # Metadata filter apply করবে
                if filter_metadata:
                    if not all(meta.get(k) == v for k, v in filter_metadata.items()):
                        continue
                
                # Score: Convert L2 distance to similarity (0-1)
                # Lower distance = higher similarity
                similarity = 1 / (1 + dist)
                
                results.append((
                    meta["text"],
                    float(similarity),
                    meta
                ))
        
        return results
    
    def delete_by_ids(self, ids: List[str]):
        """
        IDs দিয়ে vectors delete করবে
        FAISS deletion support করে না directly, তাই rebuild করতে হবে
        """
        # Keep করার indices বের করবো
        indices_to_keep = [
            i for i, meta in enumerate(self.metadata)
            if meta.get("id") not in ids
        ]
        
        if not indices_to_keep:
            # All deleted, reset
            self.index.reset()
            self.metadata = []
            self.id_to_idx = {}
            return
        
        # Old vectors বের করবো
        old_vectors = self.index.reconstruct_n(0, self.index.ntotal)
        
        # Keep করার vectors filter করবো
        new_vectors = old_vectors[indices_to_keep]
        new_metadata = [self.metadata[i] for i in indices_to_keep]
        
        # Index rebuild করবো
        self.index.reset()
        self.index.add(new_vectors.astype('float32'))
        self.metadata = new_metadata
        
        # ID mapping rebuild করবো
        self.id_to_idx = {
            meta["id"]: i 
            for i, meta in enumerate(self.metadata)
            if "id" in meta
        }
    
    def save(self, path: str):
        """Vector store save করবে"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # FAISS index save করবে
        faiss.write_index(self.index, f"{path}.index")
        
        # Metadata save করবে
        with open(f"{path}.meta", "wb") as f:
            pickle.dump({
                "metadata": self.metadata,
                "id_to_idx": self.id_to_idx,
                "model_name": self.model_name
            }, f)
    
    def load(self, path: str):
        """Vector store load করবে"""
        # FAISS index load করবে
        self.index = faiss.read_index(f"{path}.index")
        
        # Metadata load করবে
        with open(f"{path}.meta", "rb") as f:
            data = pickle.load(f)
            self.metadata = data["metadata"]
            self.id_to_idx = data["id_to_idx"]
            
            # Model mismatch check করবে
            if data["model_name"] != self.model_name:
                print(f"Warning: Model mismatch. Saved: {data['model_name']}, Current: {self.model_name}")

# Singleton instance
vector_store = VectorStore()