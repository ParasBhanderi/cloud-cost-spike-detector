import pandas as pd

REQUIRED_COLS = {"date", "service", "cost"}

def load_cost_csv(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower().strip(): c for c in df.columns}
    if "date" not in cols or "service" not in cols or "cost" not in cols:
        raise ValueError("CSV must contain columns: date, service, cost (case-insensitive).")

    df = df.rename(columns={cols["date"]: "date", cols["service"]: "service", cols["cost"]: "cost"}).copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        raise ValueError("Some 'date' values could not be parsed.")

    df["service"] = df["service"].astype(str).str.strip()
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    if df["cost"].isna().any():
        raise ValueError("Some 'cost' values could not be parsed as numbers.")

    return df.sort_values(["service", "date"]).reset_index(drop=True)