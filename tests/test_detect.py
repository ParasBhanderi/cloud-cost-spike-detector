import pandas as pd
from ml.cost_io import load_cost_csv
from ml.detect import detect_spikes

def test_detect_runs():
    df = pd.DataFrame({
        "date": ["2025-01-01","2025-01-02","2025-01-03","2025-01-04","2025-01-05","2025-01-06","2025-01-07","2025-01-08"],
        "service": ["EC2"]*8,
        "cost": [10,10,10,10,10,10,10,40],
    })
    df = load_cost_csv(df)
    scored = detect_spikes(df)
    assert "anomaly" in scored.columns
    assert len(scored) == 8