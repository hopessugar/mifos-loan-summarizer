backend\venv\Scripts\activate
$env:PYTHONPATH = "C:\Users\vyass\Documents\mifos-loan-summarizer"
backend\venv\Scripts\uvicorn backend.main:app --reload --port 8000