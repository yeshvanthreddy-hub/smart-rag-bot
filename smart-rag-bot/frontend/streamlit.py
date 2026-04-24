import streamlit as st
import requests
import time

st.set_page_config(page_title="RAG Bot", layout="wide")

# ---------- HEADER ----------
st.title("🤖 Smart RAG Assistant")
st.caption("AI-powered document search with real-time answers")

# ---------- STYLE ----------
st.markdown("""
<style>
button {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# ---------- SIDEBAR ----------
st.sidebar.title("📂 Document Manager")

# Show files
if st.session_state.uploaded_files:
    for file in st.session_state.uploaded_files:
        st.sidebar.markdown(f"""
        <div style='padding:8px; border-radius:8px; background:#1f2937; margin-bottom:5px'>
        📄 {file}
        </div>
        """, unsafe_allow_html=True)
else:
    st.sidebar.write("No documents uploaded")

# Upload
files = st.sidebar.file_uploader("Upload files", accept_multiple_files=True)

if st.sidebar.button("Upload Files"):
    if files:
        for file in files:
            res = requests.post(
                "http://127.0.0.1:12345/upload/",
                files={"file": (file.name, file.getvalue())}
            )

            try:
                st.sidebar.success(f"{file.name} uploaded ✅")

                if file.name not in st.session_state.uploaded_files:
                    st.session_state.uploaded_files.append(file.name)

            except:
                st.sidebar.error(f"{file.name} failed ❌")
    else:
        st.sidebar.warning("Select files first")

# ---------- CHAT ----------
st.subheader("💬 Chat")

if not st.session_state.messages:
    st.info("👋 Upload documents and start asking questions!")

# Show chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- INPUT ----------
if prompt := st.chat_input("Ask your question..."):

    st.session_state.messages.append({
        "role": "user",
        "content": f"🧑 {prompt}"
    })

    with st.chat_message("user"):
        st.markdown(f"🧑 {prompt}")

    # ---------- ASSISTANT ----------
    with st.chat_message("assistant"):

        placeholder = st.empty()

        with st.spinner("Thinking..."):
            res = requests.post(
                "http://127.0.0.1:12345/chat/",
                json={"user_message": prompt}   # ✅ FIXED
            )

        try:
            data = res.json()

            answer = data.get("response")
            sources = data.get("sources", [])

            if not answer or answer.strip() == "":
                answer = "⚠️ No answer found. Try rephrasing."

            # ---------- STREAMING ----------
            full_text = ""
            for char in answer:
                full_text += char
                placeholder.markdown(f"🤖 {full_text}")
                time.sleep(0.005)

            # ---------- SOURCES ----------
            if sources:
                st.markdown("### 📄 Sources")
                for src in sources:
                    st.markdown(f"""
                    <div style="background:#111827; padding:10px; border-radius:10px; margin-bottom:8px;">
                    📁 <b>{src['file']}</b><br>
                    {src['text']}
                    </div>
                    """, unsafe_allow_html=True)

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"🤖 {answer}"
            })

        except:
            placeholder.markdown("❌ Error")
            st.write(res.text)