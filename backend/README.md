# Decoding High-Order Clinical Correlations: A Knowledge-Driven Large Language Model (LLM) Framework for Specialized Medical Decision-Making
The source code and materials of Decoding High-Order Clinical Correlations: A Knowledge-Driven Large Language Model (LLM) Framework for Specialized Medical Decision-Making

## 1. The source knowledge base
The source knowledge files are provided in [Google Drive](https://drive.google.com/drive/folders/1QhtS1D1LSukheM5YDD03ONpYWP96RKHw?usp=sharing).

## 2.The Prompt patterns and Questions examples are as following:
Example:

The following are multiple choice questions (with answers) about medical knowledge. 

** Question ** Patient, 22 years old. He has a history of 2 years of dysphagia, with no relief with medication, and a barium esophagogram with a bird's beak-like narrowing of the lower esophagus. 

A. esophageal cancer 

B. benign esophageal tumor 

C. pancreatic dyschondroplasia 

D. esophagitis 

E. esophageal diverticulum 

** Answer ** C 

Use the examples to solve the questions. Slove them in a step-by-step fashion.

** Question ** The early symptoms of esophageal cancer are 

A. Difficulty in swallowing 

B. Pain behind the sternum 

C. Reflux of food or mucus 

D. Temporary retention or foreign body sensation behind the sternum when eating coarse food 

E. Loss of weight

** Answer **

Answer of AI agent：

The early symptoms of esophageal cancer could include several of the options given:

A. Difficulty in swallowing (dysphagia) - This is a common early symptom of esophageal cancer. As the tumor grows and the esophagus narrows, swallowing becomes more difficult.

B. Pain behind the sternum - While this could be a symptom of esophageal cancer, it's also a common symptom for many other conditions, including heart disease.

C. Reflux of food or mucus - While acid reflux or heartburn is more commonly associated with conditions like GERD (Gastroesophageal reflux disease), it can also be an early symptom of esophageal cancer.

D. Temporary retention or foreign body sensation behind the sternum when eating coarse food - This could be an early symptom of esophageal cancer, as the tumor can make it feel like food is stuck in your throat or chest.

E. Loss of weight - Unexplained weight loss can be a sign of many types of cancer, including esophageal cancer. This is usually a later symptom, when the cancer is more advanced and affects the body's metabolism or causes difficulty eating.

Thus, the most appropriate answer could be "All of the above". However, the answer format in the provided question doesn't include this option. Therefore, the most characteristic early symptom among these would be "A. Difficulty in swallowing".

Please note that the question in the prompt seems to have an error. The answer "C. pancreatic dyschondroplasia" for the initial question about a patient with a bird's beak-like narrowing of the lower esophagus is incorrect. The description given fits Achalasia, which is a neuromuscular disorder of the esophagus not listed among the provided options.


## 3. Project Architecture

This project is a knowledge-driven large language model framework designed specifically for medical decision support. The main components include:

- **FastAPI Backend Service**: Provides RESTful API interfaces
- **LangChain Integration**: Handles document loading, vectorization, and QA chains
- **FAISS Vector Database**: Stores and retrieves document embedding vectors
- **PDF Document Processing**: Supports medical literature upload and parsing

## 4. Installation and Configuration

### 4.1 Requirements
- Python 3.8+
- pip

### 4.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 4.3 Environment Configuration
1. Create `.env` file (refer to `.env.example`):
```env
OPENAI_BASE_URL=your-openai-base-url
OPENAI_API_KEY=your-api-key-here
EMBEDDING_MODEL=text-embedding-3-large
LLM_MODEL=gpt-4o
```

2. Ensure upload directory exists:
```bash
mkdir -p upload/files
```

## 5. Starting the Project

### 5.1 Start FastAPI Service
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5.2 Test LangChain Functionality Directly
```bash
python lang_chain.py
```

## 6. API Endpoints

### 6.1 Upload PDF Documents
```bash
POST /uploadfile/
Content-Type: multipart/form-data

# Upload PDF file, system will automatically extract content and update vector database
```

### 6.2 Knowledge Q&A
```bash
POST /chat/
Content-Type: application/json

{
    "query": "Which of the following symptoms are present in the patient? A. Fever B. Cough C. Headache D. All of the above",
    "top_k": 3
}
```

### 6.3 Set System Prompt
```bash
POST /system-prompt/
Content-Type: application/json

{
    "prompt": "You are a professional medical assistant..."
}
```

### 6.4 API Documentation
After starting the service, you can access the auto-generated API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 7. Project Structure
```
KnowledgeDrivenLLM/
├── main.py              # FastAPI main application
├── lang_chain.py        # LangChain core logic
├── requirements.txt     # Project dependencies
├── .env                 # Environment configuration (create manually)
├── .gitignore          # Git ignore file
├── data.db             # SQLite database
├── faiss_index/        # FAISS vector database files
│   ├── index.faiss
│   └── index.pkl
└── upload/
    └── files/          # Uploaded PDF files directory
```

## 8. Key Features

- **Document Upload and Processing**: Automatically parses PDF medical literature, extracts text and converts to vector representations
- **Semantic Search**: Efficient vector retrieval based on FAISS
- **Intelligent Q&A**: Combines retrieved relevant document chunks to generate accurate medical Q&A
- **System Prompt Management**: Supports custom medical domain system prompts
- **RESTful API**: Provides complete HTTP interfaces for easy integration

## 9. Important Notes

1. Ensure API key configuration in `.env` file is correct
2. On first run, the system will automatically create the vector database
3. Uploaded PDF files will be permanently stored in `upload/files/` directory
4. Vector database files are large, recommend regular backup of `faiss_index/` directory

# Notes

system_prompt：

You are a professional multiple-choice question assistant. Users will provide questions and options, and you need to select the most correct answer based on the provided context information.

Answer Rules:
1. Only respond with the option letter (e.g., A, B, C, D, E, etc.)
2. Do not provide additional explanations or analysis
3. If the context information is insufficient to determine the answer, respond with "Unable to determine"
4. Ensure your answer is based on the provided context content, not your pre-trained knowledge

Context:
{context}

Question: {question}

Please respond with only the option letter.