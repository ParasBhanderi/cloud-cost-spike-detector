import pandas as pd
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_detect_endpoint():
    df = pd.DataFrame({
        "date": ["2025-01-01","2025-01-02","2025-01-03","2025-01-04","2025-01-05","2025-01-06","2025-01-07","2025-01-08"],
        "service": ["EC2"]*8,
        "cost": [10,10,10,10,10,10,10,40],
    })
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    r = client.post("/detect", files={"file": ("costs.csv", csv_bytes, "text/csv")})
    assert r.status_code == 200
    body = r.json()
    assert "anomalies" in body