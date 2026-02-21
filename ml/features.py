import pandas as pd

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["dow"] = out["date"].dt.dayofweek
    out["dom"] = out["date"].dt.day
    out["month"] = out["date"].dt.month
    return out

def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["cost_rolling_mean_7"] = (
        out.groupby("service")["cost"].transform(lambda s: s.rolling(7, min_periods=3).mean())
    )
    out["cost_rolling_std_7"] = (
        out.groupby("service")["cost"].transform(lambda s: s.rolling(7, min_periods=3).std())
    )
    out["cost_pct_change"] = out.groupby("service")["cost"].pct_change().fillna(0.0)
    out["cost_vs_rollmean"] = (out["cost"] - out["cost_rolling_mean_7"]).fillna(0.0)
    out["roll_std_filled"] = out["cost_rolling_std_7"].fillna(0.0)
    return out

def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    x = df[[
        "cost",
        "dow",
        "dom",
        "month",
        "cost_pct_change",
        "cost_vs_rollmean",
        "roll_std_filled"
    ]].copy()
    return x.fillna(0.0)