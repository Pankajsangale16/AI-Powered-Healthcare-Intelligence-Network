import os
import asyncio
import nest_asyncio
import streamlit as st
from dotenv import load_dotenv, find_dotenv

# LangChain & Groq Imports
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv(find_dotenv())
nest_asyncio.apply()

st.sidebar.markdown("<h2 style='color: #ffffff;'>📌 Description</h2>", unsafe_allow_html=True)
st.sidebar.image("utils/ph2.png", use_container_width=True)
st.sidebar.markdown("<p class='sidebar-text'>The LLM Medical Chatbot is an AI-powered assistant designed to provide instant, accurate, and reliable healthcare insights.</p>", unsafe_allow_html=True)

# Ensure async loop is running
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Constants
DB_FAISS_PATH = "vectorstore/db_faiss"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY is missing. Please set it in your environment.")
    st.stop()

@st.cache_resource(show_spinner="Loading medical knowledge base...")
def load_vectorstore():
    try:
        embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        return FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    except Exception as e:
        st.error(f"Error loading vector store: {e}")
        return None

vectorstore = load_vectorstore()

def expand_query(question: str) -> str:
    """Turn short symptom queries into retrieval-friendly search text."""
    cleaned = " ".join(question.strip().split())
    return (
        f"{cleaned} {cleaned.replace(' ', '')} "
        "symptoms causes diagnosis treatment home care remedies "
        "medication tablets pain relief doctor specialist physiotherapy "
        "when to see a doctor emergency warning signs"
    )


def get_prompt_template():
    return PromptTemplate(
        template="""You are Medibot, a careful health-education assistant (not a doctor).
The user wants practical help: what the problem may be, what they can do, typical medicines, and which doctor to see.

Use the retrieved context when it is relevant. If the context is a dictionary snippet or is incomplete,
still answer using widely accepted general medical knowledge for common conditions.
Do NOT reply with only "I don't know" for everyday symptoms such as pain, fever, cough, cold, acidity, or infection.

Always include this disclaimer at the top:
"Educational information only — not a diagnosis or a personal prescription. Consult a licensed clinician before taking any medicine."

Write a clear answer with these headings:

1. **What it may be** — likely common causes (2–5), in plain language.
2. **What you can do now** — home care, rest, posture, heat/ice, diet, or first-aid steps.
3. **Typical medicines** — commonly used OTC and prescription *classes or well-known examples* (for example paracetamol, ibuprofen) with usual purpose. Say dose must be confirmed by a doctor/pharmacist. Flag who should avoid them (ulcers, kidney disease, pregnancy, children).
4. **Which doctor to see** — GP vs specialist (orthopedic, neurologist, physiotherapist, gastroenterologist, ENT, dermatologist, emergency, etc.) and when.
5. **See a doctor urgently if** — red-flag symptoms.

Keep the tone helpful and specific. Do not invent rare diagnoses. Do not claim a definite diagnosis.

**Retrieved notes (may be incomplete):**
{context}

**User question:**
{question}
        """,
        input_variables=["context", "question"]
    )

def load_llm():
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
    return ChatGroq(
        temperature=0.3,
        model=GROQ_MODEL
    )

def format_sources(source_documents):
    if not source_documents:
        return "**Sources:** No sources found."
    formatted_sources = "\n\n**Sources:**"
    for idx, doc in enumerate(source_documents, start=1):
        formatted_sources += f"\n🔹 **Source {idx}:** {doc.metadata.get('source', 'Unknown Source')}"
    return formatted_sources

def main():
    st.title("💬 Medibot - AI Health Assistant")
    st.markdown("""
        **Describe a symptom or condition** (for example `back pain`, `fever`, `acidity`).
        Medibot will suggest likely causes, home care, typical medicines, and which doctor to see.
        🤖🩺 *Educational only — not a substitute for a real clinician.*
    """)

    with st.sidebar:
        st.markdown("""
        ### 🔍 About Medibot:
        - Suggests **likely causes, home care, typical tablets, and specialists**
        - Uses Groq plus the medical knowledge base
        - Not a diagnosis or prescription — confirm with a doctor
        """)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        st.chat_message(message["role"]).markdown(message["content"])

    user_query = st.chat_input("Type your medical query...")

    if user_query:
        st.chat_message("user").markdown(f"**You:** {user_query}")
        st.session_state.messages.append({"role": "user", "content": user_query})

        with st.spinner("🤖 Medibot is thinking..."):
            try:
                if vectorstore is None:
                    st.error("❌ Error: Vector store failed to load.")
                    return

                qa_chain = RetrievalQA.from_chain_type(
                    llm=load_llm(),
                    chain_type="stuff",
                    retriever=vectorstore.as_retriever(search_kwargs={'k': 8}),
                    return_source_documents=True,
                    chain_type_kwargs={'prompt': get_prompt_template()}
                )

                response = qa_chain.invoke({'query': expand_query(user_query)})
                result = response.get("result", "⚠️ No response generated.")
                sources = response.get("source_documents", [])

                formatted_response = f"**Medibot:** {result}\n\n{format_sources(sources)}"
                st.chat_message("assistant").markdown(formatted_response)
                st.session_state.messages.append({"role": "assistant", "content": formatted_response})
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    main()
