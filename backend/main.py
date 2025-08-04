import os
import sqlite3
from typing import Union

from fastapi import FastAPI
from fastapi import UploadFile
from pydantic import BaseModel

from lang_chain import setup_qa_chain, setup_vector_store, embeddings, llm, update_vector_store


app = FastAPI()

@app.get("/")
def read_root():
    return {"code": 2000, "message": "success", "data": {"Hello": "World"}}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"code": 2000, "message": "success", "data": {"item_id": item_id, "q": q}}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    try:
        contents = await file.read()
        # Save file to disk
        if not os.path.exists("upload/files"):
            os.makedirs("upload/files")
        file_path = os.path.join("upload", "files", file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        update_vector_store(embeddings, file_path)
        return {"code": 2000, "message": "success", "data": {"filename": file.filename}}
    except Exception as e:
        return {"code": 5000, "message": "error", "data": {"error": str(e)}}
    
class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

@app.post("/chat/")
async def handle_query(request: QueryRequest):
    try:
        vector_store = setup_vector_store(embeddings, os.path.join("upload", "files"))
        qa_chain = setup_qa_chain(vector_store, llm)
        print(f"Processing query: {request.query} with top_k={request.top_k}")
        result = qa_chain.invoke({"query": request.query, "top_k": request.top_k})
        return {"code": 2000, "message": "success", "data": {"answer": result["result"]}}
    except Exception as e:
        return {"code": 5000, "message": "error", "data": {"error": str(e)}}


class SystemPromptRequest(BaseModel):
    prompt: str

@app.post("/system-prompt/")
async def set_system_prompt(request: SystemPromptRequest):
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS system_prompt (id INTEGER PRIMARY KEY, prompt TEXT)')
        cursor.execute('DELETE FROM system_prompt')  # Clear existing prompts
        cursor.execute('INSERT INTO system_prompt (prompt) VALUES (?)', (request.prompt,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"code": 2000, "message": "success", "data": {"prompt": request.prompt}}
    except Exception as e:
        return {"code": 5000, "message": "error", "data": {"error": str(e)}}
