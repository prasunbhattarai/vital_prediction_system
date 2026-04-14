import pandas as pd
from joblib import load
from collections import deque

scaler = load("ml_engine/scaler.pkl")
model = load("ml_engine/isolation_forest_model.pkl")


def feature_engineering(df):
    df = df.drop(columns=["id"])
    featured_columns = ["cpu_usage", "memory_usage","top5_processes_cpu_average","top5_processes_cpu_std"]
    WINDOW = 3

    df["timestamp"] = pd.to_datetime(df["date"] + " " + df["current_time"])
    df["time_window"] = df["timestamp"].dt.floor("1min")  
    df = df.sort_values("timestamp")
    df["time_diff"] = df["timestamp"].diff().dt.total_seconds()
    df["new_session"] = (df["time_diff"]>60).astype(int)
    df["session_id"] = df["new_session"].cumsum()

    for feature in featured_columns:
        df[f"{feature}_sess_mean"] = (
            df.groupby("session_id")[feature]
            .rolling(window=WINDOW)
            .mean()
            .reset_index(level=0,drop=True)   
        )

    for feature in featured_columns:
        df[f"{feature}_sess_std"] = (
            df.groupby("session_id")[feature]
            .rolling(window=WINDOW)
            .std()
            .reset_index(level=0,drop=True)
        )

    df["cpu_spike_diff"] = df.groupby("session_id")["cpu_usage"].diff()
    df["memory_spike_diff"] = df.groupby("session_id")["memory_usage"].diff()
    df = df.drop(columns=["date","current_time","time_window","timestamp","new_session","new_session","session_id"])


    df = df.dropna()
    scaled = scaler.transform(df)

    df["anomaly"] = model.predict(scaled)
    print(df)
    return df