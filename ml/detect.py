from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd
from sklearn.ensemble import IsolationForest

from .features import add_time_features, add_rolling_features, build_feature_matrix

@dataclass
class DetectConfig:
    contamination: float = 0.05
    random_state: int = 42

def detect_spikes(df: pd.DataFrame, cfg: DetectConfig = DetectConfig()) -> pd.DataFrame:
    work = add_time_features(df)
    work = add_rolling_features(work)
    X = build_feature_matrix(work)

    model = IsolationForest(
        n_estimators=200,
        contamination=cfg.contamination,
        random_state=cfg.random_state,
    )
    model.fit(X)

    pred = model.predict(X)              # -1 outlier, 1 inlier
    score = model.decision_function(X)   # higher = more normal

    work["anomaly"] = (pred == -1)
    work["anomaly_score"] = (-score)     # higher = more anomalous

    # keep only spike-like anomalies (avoid "drops")
    work["is_spike_like"] = (work["cost_vs_rollmean"] > 0) & (work["cost_pct_change"] > 0)
    work["anomaly"] = work["anomaly"] & work["is_spike_like"]

    return work.drop(columns=["is_spike_like"])

def explain_anomalies(df_scored: pd.DataFrame) -> Dict[str, Any]:
    anomalies = df_scored[df_scored["anomaly"]].copy()
    if anomalies.empty:
        return {"top_services": [], "total_anomalous_cost": 0.0}

    by_service = anomalies.groupby("service")["cost"].sum().sort_values(ascending=False).reset_index()
    total = float(anomalies["cost"].sum())
    top = [{"service": r["service"], "anomalous_cost": float(r["cost"])} for _, r in by_service.head(5).iterrows()]
    return {"top_services": top, "total_anomalous_cost": total}