# 🚀 NexusAI Deployment Guide

This document provides instructions for setting up and deploying the NexusAI platform.

## 🛠️ Local Development Setup

### 1. Backend Setup (FastAPI)
1. Navigate to the `backend` directory.
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r ../requirements.txt`
5. Configure `.env` (use `.env.example` as a template).
6. Run migrations: `alembic upgrade head` (if applicable).
7. Start the server: `uvicorn app.main:app --reload`

### 2. Frontend Setup (Streamlit)
1. Navigate to the `frontend` directory.
2. Install dependencies: `pip install -r ../requirements.txt`
3. Configure `BACKEND_URL` in your environment or `.env`.
4. Run the app: `streamlit run app.py`

---

## ☁️ Streamlit Cloud Deployment

1. **GitHub Repository**: Push your code to a GitHub repository. Ensure `requirements.txt` is in the root directory.
2. **Streamlit Cloud**:
   - Connect your GitHub account to Streamlit Cloud.
   - Select your repository and the `frontend/app.py` as the main file path.
3. **Secrets Management**:
   - In the Streamlit Cloud dashboard, go to **Settings > Secrets**.
   - Paste the contents of your `.env` file into the secrets editor.
   - **Crucial**: Ensure `BACKEND_URL` is set to the URL of your deployed FastAPI backend.
4. **Deploy**: Click **Deploy**.

---

## 🏗️ Production Best Practices
- **Security**: Always use a strong `SECRET_KEY` in production.
- **Database**: Use a managed PostgreSQL instance (e.g., Supabase, Neon, AWS RDS) instead of local SQLite.
- **AI Keys**: Never commit your API keys to version control. Use Streamlit Secrets or Environment Variables.
