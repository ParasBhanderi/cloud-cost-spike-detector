from pydantic import BaseModel
from typing import List, Optional

class AnomalyPoint(BaseModel):
    date: str
    service: str
    cost: float
    anomaly_score: float
    cost_pct_change: float
    cost_rolling_mean_7: Optional[float] = None

class DetectResponse(BaseModel):
    anomalies: List[AnomalyPoint]
    total_rows: int
    total_anomalies: int