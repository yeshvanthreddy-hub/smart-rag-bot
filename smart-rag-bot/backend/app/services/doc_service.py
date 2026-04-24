from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import pandas as pd
from docx import Document


class DocumentService:

    @staticmethod
    def read_file(path):
        try:
            # PDF
            if path.endswith(".pdf"):
                reader = PdfReader(path)
                return " ".join([p.extract_text() or "" for p in reader.pages])

            # DOCX
            elif path.endswith(".docx"):
                doc = Document(path)
                return " ".join([p.text for p in doc.paragraphs])

            # EXCEL
            elif path.endswith(".xlsx"):
                df = pd.read_excel(path)
                return df.to_string()

            # TXT ✅ FIXED
            elif path.endswith(".txt"):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()

            return ""

        except Exception as e:
            print("READ FILE ERROR:", e)
            return ""

    @staticmethod
    def split_text(text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        return splitter.split_text(text)