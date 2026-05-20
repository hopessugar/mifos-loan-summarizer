$env:PYTHONPATH = "C:\Users\vyass\Documents\mifos-loan-summarizer"
backend\venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000