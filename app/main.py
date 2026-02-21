from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd

from app.schemas import DetectResponse, AnomalyPoint
from ml.cost_io import load_cost_csv
from ml.detect import detect_spikes, explain_anomalies

app = FastAPI(title="Cloud Cost Spike Detector", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/detect", response_model=DetectResponse)
async def detect(file: UploadFile = File(...)):
    try:
        raw = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(raw))
        df = load_cost_csv(df)
        scored = detect_spikes(df)
        anomalies = scored[scored["anomaly"]].copy()

        points = []
        for _, r in anomalies.iterrows():
            points.append(AnomalyPoint(
                date=r["date"].date().isoformat(),
                service=r["service"],
                cost=float(r["cost"]),
                anomaly_score=float(r["anomaly_score"]),
                cost_pct_change=float(r.get("cost_pct_change", 0.0)),
                cost_rolling_mean_7=float(r.get("cost_rolling_mean_7")) if pd.notna(r.get("cost_rolling_mean_7")) else None,
            ))
        return DetectResponse(
            anomalies=points,
            total_rows=int(len(scored)),
            total_anomalies=int(len(points)),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/detect/summary")
async def detect_summary(file: UploadFile = File(...)):
    try:
        raw = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(raw))
        df = load_cost_csv(df)
        scored = detect_spikes(df)
        expl = explain_anomalies(scored)
        return {
            "total_rows": int(len(scored)),
            "total_anomalies": int(scored["anomaly"].sum()),
            "explanation": expl,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))