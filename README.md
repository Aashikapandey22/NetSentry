# NetSentry — Network Intrusion Detection System 🛡️

NetSentry is a production-ready, machine learning-powered Network Intrusion Detection System (NIDS) dashboard built with Streamlit and scikit-learn. It connects directly to your trained **Random Forest Classifier** (`NetSentry_RandomForest_Model.pkl`) trained on the comprehensive **CICIDS2017** benchmark corpus.

---

## 🌟 Key Features

- **Direct PKL Connection:** Loads `NetSentry_RandomForest_Model.pkl` via `joblib`, strictly preserving `feature_names_in_`, `classes_`, and the exact 78 feature input ordering.
- **Robust Pipeline Validation:** Automatically strips whitespace/BOM from headers, detects and isolates optional `Label` columns, checks for missing features, and safely handles missing or infinite values.
- **Real-Time Traffic Analysis:** Upload network traffic CSVs to receive instant multi-class classification across 14 network vectors (BENIGN, DDoS, PortScan, Bot, DoS, Web Attacks, etc.).
- **Interactive Visualizations:**
  1. *Network Traffic Label Distribution* (Ground-truth benchmark)
  2. *Flow Duration Distribution* (Symlog-scaled frequency distribution)
  3. *Feature Correlation Heatmap* (Top 12 high-variance indicators)
  4. *Confusion Matrix* (Multiclass ground-truth verification)
  5. *Top 15 Feature Importances* (Real Gini impurity reduction from model trees)
- **Detailed Export Reports:** Download prediction batches with model confidence scores and alert levels.
- **Enterprise UI Design:** Clean off-white canvas, dark navy navigation sidebar, corporate blue buttons, clear status badges (green for BENIGN, red for detected attacks), and high-contrast typography.

---

## 📁 Project Structure

```text
NetSentry/
├── app.py                                  # Main application entry point & overview dashboard
├── NetSentry_Network_Intrusion_Detection.ipynb  # Original research notebook (preserved unchanged)
├── NetSentry_RandomForest_Model.pkl       # Original trained model (preserved unchanged)
├── requirements.txt                       # Project dependencies
├── README.md                              # Full setup and editing guide
├── utils/
│   ├── model_utils.py                     # Model loading, validation, and inference engine
│   └── generate_samples.py                # Test dataset generator for evaluation and demo
├── pages/
│   ├── 1_Intrusion_Detection.py           # CSV upload, analysis, and report export
│   ├── 2_Model_Evaluation.py              # Authentic confusion matrix and evaluation metrics
│   ├── 3_Feature_Importance.py            # Top feature importances inspection
│   └── 4_About_Project.py                 # Dataset details and architecture notes
├── assets/
│   └── styles.css                         # Clean cybersecurity dashboard theme
└── sample_data/
    ├── sample_unlabeled_traffic.csv       # 50 rows of raw traffic for testing predictions
    └── sample_benchmark_eval.csv          # 50 rows of labeled flows for testing evaluation
```

---

## 🚀 How to Run the Application

### 1. Prerequisites
Ensure Python 3.9+ is installed on your system.

### 2. Set Up Virtual Environment (Recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch NetSentry
Run the Streamlit server:
```bash
streamlit run app.py
```
Then open your browser at `http://localhost:8501`.

---

## 🧪 Testing the Prediction Workflow

1. Navigate to **Intrusion Detection** in the sidebar.
2. Click **Load Pre-verified Test CSV** (or upload `sample_data/sample_unlabeled_traffic.csv`).
3. Click **⚡ Analyze Network Traffic**.
4. View the KPI metrics, traffic category breakdown donut chart, attack vectors, and flow tables.
5. Click **📥 Download Full Prediction Report (CSV)** to save the results.
6. Navigate to **Model Evaluation** to inspect the multiclass confusion matrix and feature correlation heatmap.

---

## 🎨 How to Edit and Customize the UI

- **Color Palette & Typography:** Edit `assets/styles.css`.
  - Background color: Modify `.stApp` background (`#F8F9FA`).
  - Sidebar color: Modify `section[data-testid="stSidebar"]` background (`#0F172A`).
  - Action buttons: Modify `.stButton > button` background (`#2563EB`).
  - Status badges: Modify `.metric-badge-benign` and `.metric-badge-attack`.
- **Navigation & Dashboard View:** Edit `app.py`.
- **Pages & Functionality:** Modify or add pages inside `pages/`. Streamlit automatically organizes pages by their numeric prefix.
- **Model Inference Logic:** Edit `utils/model_utils.py` to customize validation thresholds, missing value imputation, or confidence scoring.
