# Cloud Cost Spike Detector (FinOps ML) — API + Dashboard

End-to-end ML micro-project to detect cloud cost spikes from billing exports and surface the most impacted services.

## Features

- CSV ingestion (`date, service, cost`)
- Feature engineering (rolling stats + percent change)
- Anomaly detection using Isolation Forest
- FastAPI service with `/detect` and `/detect/summary`
- Streamlit dashboard for uploads + visualization
- Dockerized + CI + tests

## Run locally (Python)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
streamlit run ui/streamlit_app.py
```
