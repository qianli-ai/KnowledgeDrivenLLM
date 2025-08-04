import os
import re
import sqlite3
from typing import List
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Load environment variables
load_dotenv()


@dataclass
class Config:
    BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")
    API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    VECTOR_DB_PATH: str = "faiss_index"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200


def load_pdf_document(file_path: str) -> List[Document]:
    """Load and split PDF document into chunks."""
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"Loaded {len(documents)} pages from PDF.")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=lambda x: len(re.sub(r"\s+", "", x)),
        )
        return text_splitter.split_documents(documents)
    except Exception as e:
        print(f"Error loading PDF document: {e}")
        return []


def setup_vector_store(embeddings: OpenAIEmbeddings, pdf_dir: str) -> FAISS:
    """Initialize or load FAISS vector store."""
    try:
        return FAISS.load_local(
            Config.VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True
        )
    except Exception as e:
        print(f"Error loading vector store: {e}")
        print("Creating new vector store from PDF files...")
        # Get all PDF files from directory
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
        if not pdf_files:
            print(f"No PDF files found in directory: {pdf_dir}")
            raise ValueError("No PDF files found. Please check directory path.")

        # Load all documents from PDF files
        all_documents = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_dir, pdf_file)
            documents = load_pdf_document(pdf_path)
            if documents:
                all_documents.extend(documents)
                print(f"Loaded {len(documents)} chunks from {pdf_file}")

        if not all_documents:
            raise ValueError("No documents loaded. Please check PDF contents.")

        # Create and save vector store
        vector_store = FAISS.from_documents(all_documents, embeddings)
        vector_store.save_local(Config.VECTOR_DB_PATH)
        print(f"Vector database saved to {Config.VECTOR_DB_PATH}.")
        return vector_store


def update_vector_store(embeddings: OpenAIEmbeddings, file_path: str) -> None:
    """Update existing vector store with new documents."""
    try:
        documents = load_pdf_document(file_path)
        if not documents:
            raise ValueError("No documents loaded from new file")

        try:
            # Try to load existing vector store
            vector_store = FAISS.load_local(
                Config.VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True
            )
            # Add new documents
            vector_store.add_documents(documents)
            print(f"Vector store updated with {len(documents)} new chunks")
        except Exception as load_error:
            # If loading fails, create new vector store
            print(f"Failed to load existing vector store: {load_error}")
            print("Creating new vector store...")
            vector_store = FAISS.from_documents(documents, embeddings)
            print(f"New vector store created with {len(documents)} chunks")

        # Save vector store
        vector_store.save_local(Config.VECTOR_DB_PATH)
        print(f"Vector store saved to {Config.VECTOR_DB_PATH}")
    except Exception as e:
        print(f"Error updating vector store: {e}")
        raise e


def get_system_prompt() -> str:
    """Get the system prompt for the LLM."""
    conn = sqlite3.connect("data.db")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS system_prompt (id INTEGER PRIMARY KEY, prompt TEXT)"
        )
        cursor.execute("SELECT * FROM system_prompt")
        row = cursor.fetchone()
    except Exception as e:
        pass
    finally:
        cursor.close()
        conn.close()

    if row:
        return (
            f"Based on the prompt: {row[1]}\n\n"
            "Context:\n{context}\n\n"
            "Answer the question: {question}\n\n"
        )
    else:
        return (
            "Context:\n{context}\n\n"
            "Please answer the question: {question}\n\n"
            "If unable to answer, please reply 'I don't know'.\n\n"
        )


def setup_qa_chain(
    vector_store: FAISS,
    llm: ChatOpenAI,
    chain_type: str = "stuff",
    verbose: bool = False,
) -> RetrievalQA:
    """
    Setup QA chain with vector store and language model.

    Args:
        vector_store: FAISS vector store containing document embeddings
        llm: Language model for question answering
        chain_type: Type of QA chain ("stuff", "map_reduce", "refine")
        verbose: Whether to print debug information

    Returns:
        RetrievalQA chain instance

    Raises:
        ValueError: If vector_store or llm is None
    """
    if not vector_store or not llm:
        raise ValueError("Vector store and LLM must be provided")

    try:
        # Get system prompt template
        prompt = get_system_prompt()
        # print(f"Using system prompt: {prompt}")

        # Configure chain settings
        chain_type_kwargs = {
            "prompt": PromptTemplate.from_template(prompt),
            "verbose": verbose,
        }

        # Initialize retriever with search parameters
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3},  # Return top 3 most relevant chunks
        )

        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type=chain_type,
            retriever=retriever,
            chain_type_kwargs=chain_type_kwargs,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to setup QA chain: {str(e)}")


embeddings = OpenAIEmbeddings(
    model=Config.EMBEDDING_MODEL,
    base_url=Config.BASE_URL,
    api_key=Config.API_KEY,
)

llm = ChatOpenAI(
    model_name=Config.LLM_MODEL,
    openai_api_base=Config.BASE_URL,
    api_key=Config.API_KEY,
    temperature=0.2,
)


def main():
    vector_store = setup_vector_store(embeddings, "upload/files/")
    qa_chain = setup_qa_chain(vector_store, llm)
    result = qa_chain.invoke({"query": "onedriver?"})
    print(result["result"])


if __name__ == "__main__":
    main()
