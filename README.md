# Military Asset Management System (MAMS)

## Run the backend (Python 3.10+)
    cd backend
    python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
API docs open at http://localhost:8000/docs. The SQLite DB and demo data are created on first start.

## Run the frontend (Node 18+)
    cd frontend
    npm install
    npm run dev          # http://localhost:5173
Set VITE_API_URL (e.g. https://your-api.onrender.com/api) when deploying.

## Demo logins
| Role | Username | Password |
|---|---|---|
| Admin | admin | admin123 |
| Base Commander (Alpha) | commander | cmd123 |
| Logistics Officer (Alpha) | logistics | log123 |
