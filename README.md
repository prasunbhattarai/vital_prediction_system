# Vital Prediction System

Real-time system metrics monitoring and anomaly detection. Collects CPU, memory, disk, GPU, network, and battery vitals from a local machine, runs ML-based anomaly detection (Isolation Forest), and visualizes results in a live browser dashboard.

## Tech Stack

- **Backend:** Django 6 + Django REST Framework (Python 3.12)
- **Frontend:** React 19 + Vite 8 (JavaScript, Chart.js)
- **ML:** scikit-learn (Isolation Forest), pandas, NumPy, joblib
- **Database:** SQLite
- **System Metrics:** psutil, pynvml (NVIDIA GPU)

## Project Structure

```
backend/
  config/          -- Django settings, URLs, ASGI/WSGI
  vitals/          -- Vitals model & REST API (CRUD + recent)
  anomaly/         -- ML anomaly detection engine & API (predict + history)
  collector/       -- Management command: collect_vitals (daemon)
  model_files/     -- Pre-trained scaler.pkl & isolation_forest_model.pkl
frontend/
  src/
    component/graph.jsx  -- Live dashboard with Chart.js line charts
    App.jsx, main.jsx    -- React entrypoint
```

## Features

- Real-time polling of CPU, memory, disk, network I/O, battery, GPU (if NVIDIA)
- Session-aware feature engineering with rolling windows and spike detection
- Isolation Forest anomaly detection on live data stream
- Dual Chart.js line charts (CPU + Memory) with anomaly overlay markers
- CSV export of collected metrics
- Django admin interface for manual inspection

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install django djangorestframework django-cors-headers psutil pandas numpy scikit-learn joblib pynvml
python manage.py migrate
python manage.py createsuperuser
python manage.py collect_vitals    # start data collection daemon
python manage.py runserver         # separate terminal
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173/` to view the live dashboard.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/vitals/` | List last 100 vitals records |
| `POST /api/vitals/` | Create a vitals record |
| `GET /api/vitals/recent/` | Get most recent vitals record |
| `GET /api/anomaly/predict/` | Run anomaly prediction on latest data |
| `GET /api/anomaly/history/` | Last 50 anomaly results |
| `GET /admin/` | Django admin interface |
