# Frontend Dashboard (Layer-2)

This frontend visualizes the required 6 panels from `docs/dashboard-spec.md` using the backend time-series endpoint:

- `GET /dashboard/series?window_minutes=60&bucket_seconds=60`

## Run

### 1) Start backend

From repo root:

```bash
uvicorn app.main:app --reload
```

### 2) Start frontend

```bash
cd frontend-dashboard
npm install
npm run dev
```

Open `http://localhost:5173`.

## Notes

- Default window is **last 1 hour** and auto-refresh is **15s**.
- Data comes from `data/logs.jsonl` (bucketed aggregation).
- If your backend isn’t on `127.0.0.1:8000`, set:

```bash
set VITE_API_BASE_URL=http://127.0.0.1:8000
```

