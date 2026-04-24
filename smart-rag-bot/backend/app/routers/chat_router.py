from fastapi import APIRouter
from pydantic import BaseModel
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/chat")

# ---------- REQUEST MODEL ----------
class ChatRequest(BaseModel):
    user_message: str


# ---------- CHAT API ----------
@router.post("/")
def chat(request: ChatRequest):
    try:
        user_message = request.user_message.strip()

        print("🧑 USER:", user_message)

        if not user_message:
            return {
                "response": "⚠️ Please enter a valid question",
                "sources": []
            }

        # ---------- VECTOR SEARCH ----------
        vector = VectorService()
        docs = vector.search(user_message)

        print(f"📊 Docs found: {len(docs)}")

        if not docs:
            return {
                "response": "⚠️ No relevant information found in uploaded documents",
                "sources": []
            }

        # ---------- BUILD CONTEXT ----------
        context = "\n\n".join([doc.page_content for doc in docs])

        print("📄 CONTEXT LENGTH:", len(context))

        # ---------- LLM ----------
        llm = LLMService()

        try:
            # ✅ FIXED PARAM ORDER
            response = llm.generate_response(context, user_message)
        except Exception as e:
            print("❌ LLM ERROR:", e)
            return {
                "response": "⚠️ LLM failed to generate response",
                "sources": []
            }

        if not response or response.strip() == "":
            response = "⚠️ I couldn't generate a proper answer. Try rephrasing."

        # ---------- SOURCES ----------
        sources = []
        for doc in docs:
            sources.append({
                "file": doc.metadata.get("source", "Unknown"),
                "text": doc.page_content[:200]
            })

        return {
            "response": response,
            "sources": sources
        }

    except Exception as e:
        print("❌ CHAT ERROR:", e)
        return {
            "response": "❌ Internal server error",
            "sources": []
        }