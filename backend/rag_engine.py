import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from groq import Groq

# REMOVE the hardcoded key string and replace it with this:
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Quick safeguard check
if not GROQ_API_KEY:
    # Fallback for your local development if you haven't set the system environment variable yet
    GROQ_API_KEY = "YOUR_GSK_KEY_HERE"

base_dir = os.path.dirname(os.path.abspath(__file__))
DB_FAISS_PATH = os.path.join(base_dir, '../data/vectorstore/db_faiss')
KNOWLEDGE_BASE_DIR = os.path.join(base_dir, '../data/knowledge_base/')

def build_vector_store():
    """Reads text files from the knowledge base, converts them to vectors, and saves them locally."""
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        os.makedirs(KNOWLEDGE_BASE_DIR)
        print("Knowledge base directory created. Please add text documents to it.")
        return None

    all_documents = []
    # Read every text file inside your knowledge base folder
    for file in os.listdir(KNOWLEDGE_BASE_DIR):
        if file.endswith(".txt"):
            file_path = os.path.join(KNOWLEDGE_BASE_DIR, file)
            loader = TextLoader(file_path)
            all_documents.extend(loader.load())

    if not all_documents:
        print("No text documents found in the knowledge base.")
        return None

    # Split deep text walls into smaller 500-character chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(all_documents)    

    # Use a lightweight embedding model to convert characters into math coordinates
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

    # Compile and store the database locally in a file format
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(DB_FAISS_PATH)
    print("Vector database successfully built and stored locally!")
    return db


#rag_system
def query_rag_system(user_question):
    """Searches the FAISS vector store and uses Groq to generate a context-aware response."""
    try:
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        
        # Build the vector store if it's missing
        if not os.path.exists(DB_FAISS_PATH):
            db = build_vector_store()
            if not db:
                return "The chatbot knowledge base is currently empty."
        else:
            db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)

        # 1. Similarity Search: Fetch the top 2 matching paragraphs from your text documents
        search_results = db.similarity_search(user_question, k=2)
        context = "\n".join([doc.page_content for doc in search_results])

        # 2. Dynamic Grounding Prompt
        system_prompt = (
            "You are an expert corporate insurance assistant for the Xceedance analytics dashboard.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. If the user's question relates to Xceedance company policies, guidelines, or stipends, "
            "you MUST rely strictly on the provided Context below. If the answer cannot be found in the Context "
            "for a company-specific query, state cleanly that you don't have that corporate data.\n"
            "2. If the user asks a general question, definition, greeting, or concept (e.g., 'What is expenditure?', "
            "'Hi', 'What is inflation?'), you are allowed to use your own broad general knowledge to answer "
            "professionally.\n"
            "3. Keep all responses concise, polite, and under 3 sentences max.\n\n"
            f"--- Context ---\n{context}"
        )

        # 3. Stream back a response using Groq Cloud Engine
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2, # Low temperature keeps it strictly factual to your files
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Error routing RAG query: {str(e)}"

if __name__ == "__main__":
    # If run directly from terminal, compile the database
    build_vector_store()