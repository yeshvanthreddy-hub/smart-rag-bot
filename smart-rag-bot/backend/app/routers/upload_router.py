from fastapi import APIRouter, UploadFile, File
import shutil
from app.services.doc_service import DocumentService
from app.services.vector_service import VectorService
from app.config import STORAGE_PATH

router = APIRouter(prefix="/upload")


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        print("\n===== UPLOAD STARTED =====")

        # Initialize vector service
        vector = VectorService()

        # Save file
        path = STORAGE_PATH / file.filename

        with path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(" File saved at:", path)

        # Read file content
        text = DocumentService.read_file(str(path))

        if text:
            print("📄 TEXT LENGTH:", len(text))
        else:
            print(" TEXT IS EMPTY")

        # Validate text
        if not text or text.strip() == "":
            return {"error": "File is empty or text could not be extracted"}

        # Split text
        chunks = DocumentService.split_text(text)

        if chunks:
            print(" CHUNKS CREATED:", len(chunks))
        else:
            print(" NO CHUNKS CREATED")

        if not chunks:
            return {"error": "No chunks created from document"}

        # Create FAISS index
        print(" Calling create_index() NOW")

        vector.create_index(chunks, file.filename)

        print(" create_index() COMPLETED")

        print(" ===== UPLOAD FINISHED =====\n")

        return {
            "message": f"{file.filename} uploaded and processed successfully",
            "chunks": len(chunks)
        }

    except Exception as e:
        print(" UPLOAD ERROR:", e)
        return {"error": str(e)}
