# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from typing import List, Dict
# import os

# class VectorStore:
#     def __init__(self):
#         self.embeddings = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/all-MiniLM-L6-v2"
#         )
#         self.vector_store = None
#         self.index_path = "./vector_db/faiss_index"
        
#         # Load existing index if available
#         if os.path.exists(self.index_path):
#             self.vector_store = FAISS.load_local(
#                 self.index_path, 
#                 self.embeddings,
#                 allow_dangerous_deserialization=True
#             )
    
#     def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
#         """Add documents to vector store with chunking"""
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200,
#             length_function=len
#         )
        
#         chunks = text_splitter.create_documents(texts, metadatas=metadatas)
        
#         if self.vector_store is None:
#             self.vector_store = FAISS.from_documents(chunks, self.embeddings)
#         else:
#             self.vector_store.add_documents(chunks)
        
#         # Save index
#         os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
#         self.vector_store.save_local(self.index_path)
        
#         return len(chunks)
    
#     def similarity_search(self, query: str, k: int = 4, filter: Dict = None):
#         """Search similar documents"""
#         if self.vector_store is None:
#             return []
        
#         results = self.vector_store.similarity_search_with_score(query, k=k)
#         return [
#             {
#                 "content": doc.page_content,
#                 "metadata": doc.metadata,
#                 "score": float(score)
#             }
#             for doc, score in results
#         ]

# # Singleton instance
# vector_store = VectorStore()





# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from typing import List, Dict
# import os

# class VectorStore:
#     def __init__(self):
#         self.embeddings = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/all-MiniLM-L6-v2"
#         )
#         self.vector_store = None
#         self.index_path = "./vector_db/faiss_index"
        
#         # Load existing index if available
#         if os.path.exists(self.index_path):
#             try:
#                 self.vector_store = FAISS.load_local(
#                     self.index_path, 
#                     self.embeddings,
#                     allow_dangerous_deserialization=True
#                 )
#             except Exception as e:
#                 print(f"Could not load existing index: {e}")
    
#     def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
#         """Add documents to vector store with chunking"""
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200,
#             length_function=len
#         )
        
#         chunks = text_splitter.create_documents(texts, metadatas=metadatas)
        
#         if self.vector_store is None:
#             self.vector_store = FAISS.from_documents(chunks, self.embeddings)
#         else:
#             self.vector_store.add_documents(chunks)
        
#         # Save index
#         os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
#         self.vector_store.save_local(self.index_path)
        
#         return len(chunks)
    
#     def similarity_search(self, query: str, k: int = 4, filter: Dict = None):
#         """Search similar documents"""
#         if self.vector_store is None:
#             return []
        
#         results = self.vector_store.similarity_search_with_score(query, k=k)
#         return [
#             {
#                 "content": doc.page_content,
#                 "metadata": doc.metadata,
#                 "score": float(score)
#             }
#             for doc, score in results
#         ]

# # Singleton instance
# vector_store = VectorStore()




from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import os

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

class VectorStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None
        self.index_path = "./vector_db/faiss_index"
        
        # Load existing index if available
        if os.path.exists(self.index_path):
            try:
                self.vector_store = FAISS.load_local(
                    self.index_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Could not load existing index: {e}")
    
    def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
        """Add documents to vector store with chunking"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        chunks = text_splitter.create_documents(texts, metadatas=metadatas)
        
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vector_store.add_documents(chunks)
        
        # Save index
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self.vector_store.save_local(self.index_path)
        
        return len(chunks)
    
    def similarity_search(self, query: str, k: int = 4, filter: Dict = None):
        """Search similar documents"""
        if self.vector_store is None:
            return []
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            }
            for doc, score in results
        ]

# Singleton instance
vector_store = VectorStore()