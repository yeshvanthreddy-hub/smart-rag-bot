print(" VECTOR SERVICE FILE LOADED")

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os


class VectorService:

    def __init__(self):
        # ---------- EMBEDDING MODEL ----------
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        # ---------- FAISS PATH ----------
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.index_path = os.path.join(BASE_DIR, "faiss_index")

        print("FAISS PATH:", self.index_path)

        self.vectorstore = None

        # ---------- LOAD EXISTING INDEX ----------
        if os.path.exists(self.index_path):
            try:
                self.vectorstore = FAISS.load_local(
                    self.index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(" FAISS INDEX LOADED")
            except Exception as e:
                print(" LOAD ERROR:", e)

    # ---------- CREATE / UPDATE INDEX ----------
    def create_index(self, chunks, file_name="uploaded_file"):
        print(" Updating FAISS index...")
        print("Chunks received:", len(chunks))

        if not chunks:
            print(" No chunks to index")
            return

        # Convert to Documents (IMPORTANT for metadata)
        documents = [
            Document(
                page_content=chunk,
                metadata={"source": file_name}
            )
            for chunk in chunks
        ]

        # Reload existing index (if any)
        if os.path.exists(self.index_path):
            try:
                self.vectorstore = FAISS.load_local(
                    self.index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(" Existing index loaded")
            except Exception as e:
                print(" Reload error:", e)

        # Create or update index
        if self.vectorstore is None:
            print("Creating new FAISS index")
            self.vectorstore = FAISS.from_documents(
                documents,
                self.embeddings
            )
        else:
            print(" Adding documents to existing index")
            self.vectorstore.add_documents(documents)

        # Save index
        self.vectorstore.save_local(self.index_path)

        print("FAISS INDEX UPDATED")

    # ---------- SEARCH (FIXED METHOD NAME) ----------
    def search(self, query: str, k: int = 3):

        print(" SEARCH FUNCTION CALLED")

        # Always reload latest index
        if os.path.exists(self.index_path):
            try:
                self.vectorstore = FAISS.load_local(
                    self.index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(" Index loaded for search")
            except Exception as e:
                print(" Search load error:", e)

        if self.vectorstore is None:
            print("No vectorstore available")
            return []

        results = self.vectorstore.similarity_search(query, k=k)

        print(f" Found {len(results)} results")

        return results
