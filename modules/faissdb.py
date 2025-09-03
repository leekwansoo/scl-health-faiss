# Initialize FAISS index (change dim to match your embedding size)
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv()

# Global variables for lazy initialization
embeddings = None
dimension_size = None
db = None

def get_embeddings():
    """Lazy initialization of embeddings"""
    global embeddings, dimension_size
    if embeddings is None:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is required")
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        dimension_size = len(embeddings.embed_query("hello world"))
        print(f"Embeddings initialized with dimension: {dimension_size}")
    return embeddings

def get_db():
    """Lazy initialization of FAISS database"""
    global db
    if db is None:
        embeddings = get_embeddings()
        faiss_path = "faiss_db"
        if not os.path.exists(faiss_path):
            db = FAISS(
                embedding_function=embeddings,
                index=faiss.IndexFlatL2(dimension_size),
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            )
        else:
            # 저장된 데이터를 로드
            db = FAISS.load_local(
                folder_path="faiss_db",
                index_name="faiss_index",
                embeddings=embeddings,
                allow_dangerous_deserialization=True,
            )
    return db
# Vector 저장소 생성 (FAISS.from_documents)
def store_pdf_documents(documents):
    # add documents to existing db
    db = get_db()
    db.add_documents(documents=documents)
    # 로컬 Disk 에 저장
    db.save_local(folder_path="faiss_db", index_name="faiss_index")
    response = "documents are stored in faiss"
    #print(db.index_to_docstore_id)
    return response
   
   

def search_documents(query, k):
    # return as documents
    db = get_db()
    results = db.similarity_search(query, k=k)
    #print(results)
    return results
