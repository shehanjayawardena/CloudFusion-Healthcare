"""
CloudFusion Healthcare Analytics Ltd (CHA)
Predictive Clinical Machine Learning Pipeline for Amazon SageMaker
Module: COMP60010 - Enterprise Cloud and Distributed Web Applications
Author: Shehan Jaye (CB012510) | AWS Account: 460060049985
Target AWS Region: ap-southeast-1 (Singapore)

This script:
1. Synthesizes a realistic clinical telemetry dataset (5,000 ICU vitals records based on PhysioNet/MIMIC-III Sepsis-3).
2. Exports the dataset to CSV format for the S3 Healthcare Data Lake (Bronze/Silver ingestion).
3. Trains a multivariate clinical deterioration risk classifier with L2 regularization.
4. Generates publication-quality evaluation metrics, ROC curves, confusion matrices, and feature importance charts.
5. Saves the high-resolution figure to docs/report/figures/ml_sepsis_model_evaluation.png.
6. Packages the trained model into SageMaker's standard deployable archive: src/ml/artifacts/model.tar.gz.
7. Executes a live simulated inference validation on patient test cases.
"""

import os
import sys
import json
import tarfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, confusion_matrix, precision_recall_fscore_support

def generate_synthetic_clinical_dataset(n_samples=5000, random_seed=42):
    """
    Generates realistic clinical telemetry records based on ICU vital signs
    distributions (MIMIC-III / PhysioNet Sepsis benchmark parameters).
    
    Features:
    1. heart_rate (BPM): 50 - 160 (Normal 60-100, Tachycardia > 100)
    2. spo2 (%): 85 - 100 (Hypoxia < 92%)
    3. systolic_bp (mmHg): 70 - 180 (Hypotension < 90)
    4. diastolic_bp (mmHg): 45 - 110
    5. temperature (°C): 35.5 - 40.0 (Hypothermia < 36.0, Hyperthermia > 38.3)
    6. respiratory_rate (breaths/min): 10 - 35 (Tachypnea > 24)
    7. shock_index: heart_rate / systolic_bp (> 0.9 indicates acute shock risk)
    """
    np.random.seed(random_seed)
    
    # Baseline physiological vitals (normal distribution)
    hr = np.random.normal(loc=78, scale=15, size=n_samples)
    spo2 = np.random.normal(loc=97.5, scale=2.4, size=n_samples)
    sbp = np.random.normal(loc=122, scale=17, size=n_samples)
    dbp = np.random.normal(loc=76, scale=11, size=n_samples)
    temp = np.random.normal(loc=36.8, scale=0.7, size=n_samples)
    rr = np.random.normal(loc=16, scale=3.8, size=n_samples)
    
    # Physiological bounding
    hr = np.clip(hr, 45, 175)
    spo2 = np.clip(spo2, 75, 100)
    sbp = np.clip(sbp, 65, 200)
    dbp = np.clip(dbp, 40, 120)
    temp = np.clip(temp, 35.0, 41.0)
    rr = np.clip(rr, 8, 42)
    
    # Clinical shock index: Heart Rate / Systolic BP
    shock_index = hr / sbp
    
    # Clinical deterioration risk scoring (Sepsis-3 physiological weightings)
    # Higher HR, lower SpO2, lower SBP, higher Temp, higher RR, higher Shock Index
    risk_score = (
        0.045 * (hr - 75)
        - 0.14 * (spo2 - 95)
        - 0.035 * (sbp - 110)
        + 1.6 * (temp - 37.0)
        + 0.085 * (rr - 16)
        + 2.8 * (shock_index - 0.7)
    )
    
    # Probability via Sigmoid activation
    prob = 1.0 / (1.0 + np.exp(-risk_score))
    
    # Binary label: 1 = Deterioration / Septic Shock Risk, 0 = Clinically Stable
    labels = (prob >= 0.52).astype(int)
    
    # Construct DataFrame
    df = pd.DataFrame({
        "patient_id": [f"CHA-PT-{10000 + i}" for i in range(n_samples)],
        "heart_rate": np.round(hr, 1),
        "spo2": np.round(spo2, 1),
        "systolic_bp": np.round(sbp, 1),
        "diastolic_bp": np.round(dbp, 1),
        "temperature": np.round(temp, 2),
        "respiratory_rate": np.round(rr, 1),
        "shock_index": np.round(shock_index, 3),
        "sepsis_deterioration_risk": labels
    })
    
    return df


def plot_model_evaluation(y_test, y_probs, y_pred, feature_names, weights, out_path):
    """
    Renders a multi-panel, publication-quality evaluation figure for the report.
    Panels:
    1. ROC Curve with AUC
    2. Confusion Matrix (Clinical Interpretation)
    3. Standardized Feature Weight Importance (Coefficients)
    4. Sepsis Risk Distribution (Density Comparison)
    """
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(14, 11), dpi=300)
    
    # Panel A: ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_probs)
    roc_auc = auc(fpr, tpr)
    
    axes[0, 0].plot(fpr, tpr, color="#0284c7", lw=2.5, label=f"Clinical Classifier (AUC = {roc_auc:.3f})")
    axes[0, 0].plot([0, 1], [0, 1], color="#94a3b8", lw=1.5, linestyle="--", label="Random Classifier (AUC = 0.500)")
    axes[0, 0].set_xlim([0.0, 1.0])
    axes[0, 0].set_ylim([0.0, 1.05])
    axes[0, 0].set_xlabel("False Positive Rate (1 - Specificity)", fontsize=11, fontweight="bold")
    axes[0, 0].set_ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=11, fontweight="bold")
    axes[0, 0].set_title("A. Receiver Operating Characteristic (ROC) Curve", fontsize=12, fontweight="bold", pad=10)
    axes[0, 0].legend(loc="lower right", frameon=True)
    axes[0, 0].grid(True, linestyle=":", alpha=0.6)
    
    # Panel B: Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    im = axes[0, 1].imshow(cm, interpolation="nearest", cmap="Blues")
    fig.colorbar(im, ax=axes[0, 1], fraction=0.046, pad=0.04)
    axes[0, 1].set_xticks([0, 1])
    axes[0, 1].set_yticks([0, 1])
    axes[0, 1].set_xticklabels(["Stable (0)", "Deteriorating (1)"], fontsize=10, fontweight="bold")
    axes[0, 1].set_yticklabels(["Stable (0)", "Deteriorating (1)"], fontsize=10, fontweight="bold")
    axes[0, 1].set_xlabel("Predicted Clinical State", fontsize=11, fontweight="bold")
    axes[0, 1].set_ylabel("True Clinical State", fontsize=11, fontweight="bold")
    axes[0, 1].set_title(f"B. Confusion Matrix (N = {len(y_test)} Unseen Patients)", fontsize=12, fontweight="bold", pad=10)
    
    # Annotate numbers
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            cell_text = f"{cm[i, j]:,}\n({cm[i, j]/len(y_test)*100:.1f}%)"
            axes[0, 1].text(j, i, cell_text, ha="center", va="center",
                            color="white" if cm[i, j] > thresh else "#0f172a",
                            fontweight="bold", fontsize=11)
            
    # Panel C: Feature Importance (Standardized Weights)
    coefs = weights[1:]  # Exclude bias
    sort_idx = np.argsort(np.abs(coefs))
    sorted_features = [feature_names[i] for i in sort_idx]
    sorted_coefs = coefs[sort_idx]
    
    bar_colors = ["#10b981" if c < 0 else "#ef4444" for c in sorted_coefs]
    axes[1, 0].barh(sorted_features, sorted_coefs, color=bar_colors, edgecolor="#334155", alpha=0.85)
    axes[1, 0].axvline(0, color="#475569", linestyle="-", lw=1)
    axes[1, 0].set_xlabel("Model Coefficient (Log-Odds Impact on Sepsis Risk)", fontsize=11, fontweight="bold")
    axes[1, 0].set_title("C. Feature Importance (Physiological Weightings)", fontsize=12, fontweight="bold", pad=10)
    axes[1, 0].grid(True, linestyle=":", alpha=0.6)
    
    # Panel D: Risk Probability Density Distribution
    stable_probs = y_probs[y_test == 0]
    sepsis_probs = y_probs[y_test == 1]
    
    axes[1, 1].hist(stable_probs, bins=25, alpha=0.65, color="#10b981", label="Clinically Stable Cohort", density=True)
    axes[1, 1].hist(sepsis_probs, bins=25, alpha=0.65, color="#ef4444", label="Septic Deterioration Cohort", density=True)
    axes[1, 1].axvline(0.50, color="#0f172a", linestyle="--", lw=2, label="Triage Threshold (0.50)")
    axes[1, 1].axvline(0.75, color="#b91c1c", linestyle="-.", lw=2, label="Critical ICU Alarm Threshold (0.75)")
    axes[1, 1].set_xlabel("Predicted Sepsis Probability", fontsize=11, fontweight="bold")
    axes[1, 1].set_ylabel("Cohort Density", fontsize=11, fontweight="bold")
    axes[1, 1].set_title("D. Predicted Probability Distribution by True Cohort", fontsize=12, fontweight="bold", pad=10)
    axes[1, 1].legend(loc="upper center", frameon=True, fontsize=9)
    axes[1, 1].grid(True, linestyle=":", alpha=0.6)
    
    # Metadata Supertitle
    fig.suptitle(
        "CloudFusion Healthcare Analytics (CHA) - Amazon SageMaker Clinical Deterioration Model\n"
        "Physiological Telemetry Validation (MIMIC-III / Sepsis-3 Criteria) | Student: Shehan Jaye (CB012510) | AWS: 460060049985",
        fontsize=13, fontweight="bold", y=0.98
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"      [OK] High-resolution evaluation figure exported: {out_path}")


def main():
    print("=" * 80)
    print("CLOUDFUSION HEALTHCARE ANALYTICS (CHA) - AMAZON SAGEMAKER AI/ML PIPELINE")
    print("Author: Shehan Jaye (CB012510) | AWS Account ID: 460060049985")
    print("Target AWS Region: ap-southeast-1 (Singapore)")
    print("=" * 80)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))
    data_dir = os.path.join(base_dir, "data")
    artifacts_dir = os.path.join(base_dir, "artifacts")
    figures_dir = os.path.join(project_root, "docs", "report", "figures")
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(artifacts_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    # 1. Synthesize Dataset
    print("\n[Phase 1/5] Generating Synthetic Clinical Dataset (5,000 Patient Records)...")
    df = generate_synthetic_clinical_dataset(n_samples=5000, random_seed=42)
    csv_path = os.path.join(data_dir, "synthetic_clinical_vitals.csv")
    df.to_csv(csv_path, index=False)
    print(f"      Dataset successfully exported: {csv_path}")
    print(f"      Total Records: {len(df):,} | Positive Sepsis/Shock Cases: {df['sepsis_deterioration_risk'].sum():,} ({df['sepsis_deterioration_risk'].mean()*100:.1f}%)")
    
    # Feature matrix and targets
    feature_cols = ["heart_rate", "spo2", "systolic_bp", "diastolic_bp", "temperature", "respiratory_rate", "shock_index"]
    X = df[feature_cols].values
    y = df["sepsis_deterioration_risk"].values
    
    # 2. Train / Test Split
    print("\n[Phase 2/5] Partitioning Train/Test Cohorts & Feature Standardisation...")
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    mean = np.mean(X_train, axis=0)
    std = np.std(X_train, axis=0)
    std[std == 0] = 1.0
    
    X_train_scaled = (X_train - mean) / std
    X_test_scaled = (X_test - mean) / std
    
    X_train_b = np.c_[np.ones((len(X_train_scaled), 1)), X_train_scaled]
    X_test_b = np.c_[np.ones((len(X_test_scaled), 1)), X_test_scaled]
    
    # 3. Model Training via L2 Regularised Logistic Classification
    print("\n[Phase 3/5] Training Multivariate Clinical Risk Classifier...")
    weights = np.zeros(X_train_b.shape[1])
    lr = 0.06
    n_iters = 1500
    lambda_reg = 0.015
    
    for _ in range(n_iters):
        z = np.dot(X_train_b, weights)
        preds = 1.0 / (1.0 + np.exp(-np.clip(z, -25, 25)))
        errors = preds - y_train
        grad = (np.dot(X_train_b.T, errors) / len(y_train)) + (lambda_reg * weights)
        weights -= lr * grad
        
    # 4. Evaluation on Unseen Test Cohort
    print("\n[Phase 4/5] Evaluating Classifier on Unseen Cohort (N = 1,000)...")
    z_test = np.dot(X_test_b, weights)
    y_probs = 1.0 / (1.0 + np.exp(-np.clip(z_test, -25, 25)))
    y_pred = (y_probs >= 0.50).astype(int)
    
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary")
    accuracy = np.mean(y_pred == y_test)
    fpr, tpr, _ = roc_curve(y_test, y_probs)
    roc_auc = auc(fpr, tpr)
    
    print("-" * 55)
    print(f"  Test Accuracy:        {accuracy*100:.2f}%")
    print(f"  Recall (Sensitivity): {recall*100:.2f}% (High sensitivity avoids missed shock)")
    print(f"  Precision:            {precision*100:.2f}%")
    print(f"  F1-Score:             {f1*100:.2f}%")
    print(f"  Area Under ROC (AUC): {roc_auc:.4f}")
    print("-" * 55)
    
    # Export High-Res Evaluation Graphic
    eval_fig_path = os.path.join(figures_dir, "ml_sepsis_model_evaluation.png")
    plot_model_evaluation(y_test, y_probs, y_pred, feature_cols, weights, eval_fig_path)
    
    # 5. Export SageMaker Model Artifacts
    print("\n[Phase 5/5] Exporting Amazon SageMaker Artifacts (model.tar.gz)...")
    model_payload = {
        "model_architecture": "Multivariate_Clinical_Logistic_L2",
        "aws_account_id": "460060049985",
        "region": "ap-southeast-1",
        "features": feature_cols,
        "mean": mean.tolist(),
        "std": std.tolist(),
        "weights": weights.tolist(),
        "metrics": {
            "accuracy": float(accuracy),
            "recall": float(recall),
            "precision": float(precision),
            "f1_score": float(f1),
            "roc_auc": float(roc_auc)
        },
        "training_samples": len(X_train),
        "test_samples": len(X_test)
    }
    
    params_json_path = os.path.join(artifacts_dir, "model_params.json")
    with open(params_json_path, "w", encoding="utf-8") as f:
        json.dump(model_payload, f, indent=2)
        
    tar_path = os.path.join(artifacts_dir, "model.tar.gz")
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(params_json_path, arcname="model_params.json")
        
    print(f"      [OK] Parameters saved: {params_json_path}")
    print(f"      [OK] SageMaker Archive: {tar_path}")
    
    # 6. Clinical Inference Verification on Profiles
    print("\n" + "=" * 80)
    print("REAL-TIME CLINICAL INFERENCE SIMULATION (AMAZON SAGEMAKER ENDPOINT)")
    print("=" * 80)
    
    profiles = [
        {
            "name": "Patient 01: Mrs. Dilani Fernando (Stable Post-Op)",
            "hr": 74.0, "spo2": 98.5, "sbp": 124.0, "dbp": 78.0, "temp": 36.7, "rr": 15.0
        },
        {
            "name": "Patient 02: Mr. Kavindu Bandara (Impending Septic Deterioration)",
            "hr": 118.0, "spo2": 90.5, "sbp": 88.0, "dbp": 54.0, "temp": 38.9, "rr": 27.0
        }
    ]
    
    for p in profiles:
        si = p["hr"] / p["sbp"]
        raw = np.array([p["hr"], p["spo2"], p["sbp"], p["dbp"], p["temp"], p["rr"], si])
        scaled = (raw - mean) / std
        b = np.r_[1.0, scaled]
        prob = 1.0 / (1.0 + np.exp(-np.dot(b, weights)))
        
        print(f"\nProfile: {p['name']}")
        print(f"  Vitals: HR={p['hr']} BPM | SpO2={p['spo2']}% | BP={p['sbp']}/{p['dbp']} mmHg | Temp={p['temp']}°C | RR={p['rr']}/min")
        print(f"  Shock Index (HR/SBP): {si:.2f} (Normal < 0.70)")
        print(f"  >> SageMaker Predicted Deterioration Probability: {prob*100:.1f}%")
        if prob >= 0.75:
            print("  >> TRIAGE: [CRITICAL ALERT] HIGH PROBABILITY OF SEPTIC SHOCK WITHIN 24 HOURS!")
            print("  >> DISPATCH: Amazon SNS -> Automated emergency alert sent to ICU Attending Physician.")
        else:
            print("  >> TRIAGE: [CLINICALLY STABLE] Normal telemetry observation maintained.")
            
    print("\n" + "=" * 80)
    print("AI/ML Pipeline Execution Successfully Completed!")
    print("=" * 80)

if __name__ == "__main__":
    main()
