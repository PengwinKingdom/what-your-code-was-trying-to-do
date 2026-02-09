# What Your Code Was Trying to Do

A developer-focused tool that analyzes a block of code and explains **its intended goal, hidden assumptions, potential future problems, and one high-impact recommendation**.

The application is designed to help developers quickly understand unfamiliar or legacy code beyond line-by-line syntax.

---

## Features

- Paste code (up to 150 lines) and receive:
  - Intended goal of the code
  - Hidden assumptions
  - Potential future problems (with severity)
  - One high-impact recommendation
- Automatic programming language detection
- Supports Python, JavaScript, C++, and C#
- Clean and minimal UI built with Streamlit
- FastAPI backend
- **Graceful fallback analyzer** when AI quota is unavailable

---

## Gemini API Integration

The backend integrates with the **Google Gemini API (Gemini 3)** to generate structured, high-level code analysis.

When Gemini API quota is unavailable, the system automatically falls back to a **local heuristic-based analyzer** to ensure the application remains fully functional for demos and users.

This design demonstrates:
- Robust system architecture
- Resilience to external API limits
- Clear separation between AI-driven and rule-based analysis

---

## Project Structure
```bash
├── app/ # FastAPI backend
│ ├── main.py
│ ├── gemini_client.py
│ ├── prompts.py
│ └── fallback_analyzer.py
├── frontend/ # Streamlit frontend
│ └── app.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## How to Run the Project Locally

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Create and activate a virtual environment

#### Windows
```bash
python -m venv venv
# venv\Scripts\activate    # Windows
```

#### MacOS/Linux
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a .env file using .env.example as reference:

```bash
GEMINI_API_KEY=your_api_key_here
ENABLE_FALLBACK=true
BACKEND_URL=http://127.0.0.1:8000
```

### 5. Run the backend (FastAPI)

```bash
cd app
uvicorn main:app --reload
```

Backend will run at

```bash
http://127.0.0.1:8000
```

### 6. Run the frontend (Streamlit)

```bash
cd frontend
streamlit run app.py
```

Frontend will run at

```bash
http://localhost:8501
```



