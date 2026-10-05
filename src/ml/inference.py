"""
CloudFusion Healthcare Analytics Ltd (CHA)
Amazon SageMaker Serverless Inference Handler
Module: COMP60010 - Enterprise Cloud and Distributed Web Applications
Author: Shehan Jaye (CB012510) | AWS Account: 460060049985
Target AWS Region: ap-southeast-1 (Singapore)

This handler is invoked by the Amazon SageMaker container runtime
during real-time / serverless endpoint invocations.
"""

import os
import json
import numpy as np

def model_fn(model_dir):
    """
    Loads the trained model parameters from the unpacked model archive.
    """
    params_path = os.path.join(model_dir, "model_params.json")
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"Model parameters file not found at {params_path}")
        
    with open(params_path, "r", encoding="utf-8") as f:
        model_payload = json.load(f)
        
    return {
        "weights": np.array(model_payload["weights"]),
        "mean": np.array(model_payload["mean"]),
        "std": np.array(model_payload["std"]),
        "features": model_payload["features"]
    }

def input_fn(request_body, request_content_type):
    """
    Parses incoming HTTP request payload (JSON).
    Expected payload format:
    {
        "patient_id": "CHA-PT-10492",
        "heart_rate": 112.0,
        "spo2": 91.5,
        "systolic_bp": 90.0,
        "diastolic_bp": 55.0,
        "temperature": 38.7,
        "respiratory_rate": 26.0
    }
    """
    if request_content_type == "application/json":
        data = json.loads(request_body)
        return data
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}. Expected application/json.")

def predict_fn(input_data, model):
    """
    Performs inference to compute Sepsis Deterioration Probability.
    """
    hr = float(input_data["heart_rate"])
    spo2 = float(input_data["spo2"])
    sbp = float(input_data["systolic_bp"])
    dbp = float(input_data["diastolic_bp"])
    temp = float(input_data["temperature"])
    rr = float(input_data["respiratory_rate"])
    shock_index = hr / sbp if sbp > 0 else 1.0
    
    raw_vector = np.array([hr, spo2, sbp, dbp, temp, rr, shock_index])
    scaled_vector = (raw_vector - model["mean"]) / model["std"]
    feature_b = np.r_[1.0, scaled_vector]
    
    # Sigmoid prediction
    z = np.dot(feature_b, model["weights"])
    prob = float(1.0 / (1.0 + np.exp(-np.clip(z, -25, 25))))
    
    triage_alert = prob >= 0.75
    alert_level = "CRITICAL_ICU_ALERT" if prob >= 0.75 else ("ELEVATED_WATCH" if prob >= 0.50 else "STABLE")
    
    return {
        "patient_id": input_data.get("patient_id", "UNKNOWN"),
        "sepsis_deterioration_probability": round(prob, 4),
        "alert_level": alert_level,
        "is_critical_triage": triage_alert,
        "calculated_shock_index": round(shock_index, 3),
        "model_runtime": "Amazon SageMaker Serverless Inference (ap-southeast-1)"
    }

def output_fn(prediction, content_type):
    """
    Serializes prediction output to JSON.
    """
    if content_type == "application/json":
        return json.dumps(prediction, indent=2)
    raise ValueError(f"Unsupported accept type: {content_type}")
