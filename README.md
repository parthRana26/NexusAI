# NexusAI — Premium Intelligence Platform

NexusAI is a production-grade AI assistant platform featuring intelligent intent routing, dual-layer memory (ST/LT), and a professional SaaS UI. It enables users to interact with various AI capabilities including web search, document analysis (RAG), and long-term context retention.

## 🌟 Key Features
- **Intelligent Routing**: Automatically detects user intent (Web Search, News, Finance, RAG).
- **Dual-Layer Memory**: Remembers session context and learns long-term user facts.
- **Advanced RAG**: Upload PDF/DOCX files or images (OCR) for deep AI analysis.
- **Professional UI**: A sleek, responsive dashboard built with Streamlit.
- **Secure Auth**: Robust JWT-based authentication system.

## 💻 Tech Stack
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Pydantic.
- **Frontend**: Streamlit, Pandas, CSS Injection.
- **AI/LLM**: Groq (Llama 3), LangChain.
- **Vector DB**: Qdrant (for RAG).
- **Services**: Tavily (Search), GNews (News), Alpha Vantage (Finance).

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.10+
- PostgreSQL
- Virtual Environment (recommended)

### 2. Clone and Configure
1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Copy `.env.example` to `backend/.env`
   - Fill in your API keys (Groq, Tavily, etc.)

### 3. Database Initialization
Ensure your PostgreSQL server is running and the database specified in `.env` exists.

## 🚀 Run Instructions

### Start Backend
Run from the root directory or `backend/` folder:
```bash
cd backend
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### Start Frontend
Run from the root directory or `frontend/` folder:
```bash
cd frontend
streamlit run app.py
```
The UI will be available at `http://localhost:8501`.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
