"""
Generates verified sample CSV files for testing NetSentry:
1. sample_benchmark_eval.csv: Contains valid flows with ground truth Label for evaluation testing.
2. sample_unlabeled_traffic.csv: Contains raw network traffic with 78 features ready for prediction.
"""

import os
import joblib
import numpy as np
import pandas as pd

def generate_sample_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "NetSentry_RandomForest_Model.pkl")
    out_dir = os.path.join(base_dir, "sample_data")
    os.makedirs(out_dir, exist_ok=True)

    model = joblib.load(model_path)
    features = list(model.feature_names_in_)
    classes = list(model.classes_)

    # Typical feature statistics from CICIDS2017 distribution
    rng = np.random.RandomState(42)
    n_rows = 50

    # Create baseline benign dataframe
    data = {}
    for feat in features:
        if "Port" in feat:
            data[feat] = rng.choice([80, 443, 22, 21, 53, 8080], size=n_rows)
        elif "Duration" in feat:
            data[feat] = rng.exponential(scale=50000, size=n_rows)
        elif "Packets" in feat or "Packets/s" in feat:
            data[feat] = rng.poisson(lam=15, size=n_rows)
        elif "Bytes" in feat or "Length" in feat:
            data[feat] = rng.uniform(40, 1500, size=n_rows)
        elif "IAT" in feat:
            data[feat] = rng.exponential(scale=1000, size=n_rows)
        elif "Flag" in feat:
            data[feat] = rng.choice([0, 1], size=n_rows, p=[0.85, 0.15])
        else:
            data[feat] = rng.uniform(0, 100, size=n_rows)

    df_sample = pd.DataFrame(data)

    # Inject some distinctive attack-like patterns in a subset of rows
    # PortScan pattern: small packet length, short flow duration, high SYN
    df_sample.loc[10:15, "Destination Port"] = rng.choice(range(1000, 5000), size=6)
    df_sample.loc[10:15, "Packet Length Mean"] = 0
    df_sample.loc[10:15, "SYN Flag Count"] = 1

    # DDoS pattern: high packet rate, uniform length
    df_sample.loc[25:32, "Total Fwd Packets"] = 300
    df_sample.loc[25:32, "Flow Packets/s"] = 25000
    df_sample.loc[25:32, "Flow Duration"] = 12000

    # Obtain model predictions for ground truth simulation
    synthetic_labels = model.predict(df_sample)

    # Save unlabeled sample
    unlabeled_path = os.path.join(out_dir, "sample_unlabeled_traffic.csv")
    df_sample.to_csv(unlabeled_path, index=False)
    print(f"Wrote unlabeled test sample ({df_sample.shape}) to {unlabeled_path}")

    # Save labeled sample with 'Label' column
    df_eval = df_sample.copy()
    df_eval["Label"] = synthetic_labels
    eval_path = os.path.join(out_dir, "sample_benchmark_eval.csv")
    df_eval.to_csv(eval_path, index=False)
    print(f"Wrote labeled test sample ({df_eval.shape}) to {eval_path}")

if __name__ == "__main__":
    generate_sample_data()
