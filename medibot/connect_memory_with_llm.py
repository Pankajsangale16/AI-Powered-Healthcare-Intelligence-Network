import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

HF_TOKEN = os.environ.get("HF_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
HUGGINGFACE_REPO_ID = "mistralai/Mistral-7B-Instruct-v0.3"

def load_llm(huggingface_repo_id=HUGGINGFACE_REPO_ID):
    """Load LLM using HuggingFaceEndpoint or ChatGroq fallback."""
    if HF_TOKEN:
        return HuggingFaceEndpoint(
            repo_id=huggingface_repo_id,
            temperature=1,
            huggingfacehub_api_token=HF_TOKEN,
            model_kwargs={"max_length": 512}
        )
    elif GROQ_API_KEY:
        from langchain_groq import ChatGroq
        groq_model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
        return ChatGroq(model=groq_model, temperature=0.3)
    else:
        raise ValueError("Neither HF_TOKEN nor GROQ_API_KEY found in environment or .env file.")

# Step 2: Custom Prompt for RetrievalQA
CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer user's question.
If you dont know the answer, just say that you dont know, dont try to make up an answer. 
Dont provide anything out of the given context.

Context: {context}
Question: {question}

Start the answer directly. No small talk please.
"""

def set_custom_prompt(custom_prompt_template):
    return PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])

# Step 3: Load FAISS Vector Database
DB_FAISS_PATH = "vectorstore/db_faiss"
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)

# Step 4: Create QA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=load_llm(HUGGINGFACE_REPO_ID),  # Properly Configured LLM
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={'k': 3}),
    return_source_documents=True,
    chain_type_kwargs={'prompt': set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
)

# Step 5: Accept User Query and Invoke Chain
user_query = input("Write Query Here: ")
response = qa_chain.invoke({'query': user_query})

# Step 6: Print Results
print("\n🔹 RESULT: ", response["result"])
print("\n📄 SOURCE DOCUMENTS: ", response["source_documents"])
