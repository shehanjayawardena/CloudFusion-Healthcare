# Amazon SageMaker Predictive Clinical Machine Learning Pipeline
**CloudFusion Healthcare Analytics Ltd (CHA)**  
**Module**: COMP60010 – Enterprise Cloud and Distributed Web Applications (ECDWA)  
**Author**: Shehan Jaye (Student ID: `CB012510`) | AWS Account: `460060049985`  
**Primary Region**: `ap-southeast-1` (Singapore)

---

## 1. What is the ML Component in the Report?

In traditional hospital wards, vital signs are captured every 4 to 6 hours by nurses on paper charts. This creates **dangerous 4-hour clinical blind spots** where acute septic shock or sudden cardiac arrest occurs between visits without warning.

In the target **AWS Cloud Architecture**:
1. **Wearable IoT Sensors** stream real-time telemetry (Heart Rate, $\text{SpO}_2$, Blood Pressure, Temperature, Respiratory Rate) every 60 seconds to **AWS IoT Core**.
2. **AWS Glue** transforms and cleanses historical archives in the **Amazon S3 Medical Data Lake** into columnar Apache Parquet.
3. **Amazon SageMaker** trains and hosts a multivariate **early warning clinical risk model (XGBoost / Logistic Classifier)**.
4. The model continuously evaluates patient time-series vitals to predict **septic shock and acute organ failure 24 to 48 hours in advance**.
5. If the deterioration probability exceeds **75%**, **Amazon SNS** dispatches urgent alerts to ICU attending physicians, and the status updates on the clinical portal.

---

## 2. Do We Have to Deploy SageMaker Live on AWS for the Assignment?

### Academic & Assessment Perspective:
* **No, running a 24/7 live Amazon SageMaker endpoint is NOT required by the COMP60010 rubric.**
* COMP60010 focuses on **Enterprise Cloud Architecture, Migration Strategy, Multi-AZ Networking (VPC), Containerisation, Security Governance, and Cost Modeling**.
* In enterprise cloud strategy, Machine Learning model hosting is categorized under **Phase 4 (Advanced AI/ML Innovation & Optimization)** of the implementation roadmap (Months 7–8).

### Crucial Cost & Credit Warning (FinOps):
* Real-time SageMaker endpoints (e.g., `ml.m5.xlarge` or `ml.t3.medium`) run on persistent EC2 compute instances.
* A live SageMaker endpoint costs **$0.05 to $0.25+ per hour** (**$40.00 – $180.00/month**). Leaving it running on a student account or AWS Academy lab will quickly consume credits or incur unwanted personal charges.
* If deploying to AWS, always use **Amazon SageMaker Serverless Inference** ($0.00 idle cost), as implemented in `src/ml/sagemaker_deploy_endpoint.py`.

---

## 3. How the ML Component is Implemented in This Project

This repository provides full end-to-end implementation across two layers:

### A. Live Interactive Frontend Simulation
* Located in: [`src/frontend/app.js`](file:///d:/APIIT/Final%20Year/ECDWA/CloudFusion-Healthcare/src/frontend/app.js) & [`src/frontend/index.html`](file:///d:/APIIT/Final%20Year/ECDWA/CloudFusion-Healthcare/src/frontend/index.html).
* Deployed live on AWS S3: [http://cha-healthpulse-web-460060049985.s3-website-ap-southeast-1.amazonaws.com](http://cha-healthpulse-web-460060049985.s3-website-ap-southeast-1.amazonaws.com).
* Features the **AI Early Warning Deterioration Alert (AWS SageMaker Inference)** card that dynamically scores patient physiological risk and alerts clinical staff.

### B. Python Machine Learning & SageMaker Pipeline Code
* **Model Training Script**: [`src/ml/train_sepsis_model.py`](file:///d:/APIIT/Final%20Year/ECDWA/CloudFusion-Healthcare/src/ml/train_sepsis_model.py)
  * Synthesizes 5,000 multi-parameter ICU vital sign records.
  * Engineers clinical features including the **Shock Index** ($\text{HR} / \text{SBP}$).
  * Trains a multivariate classifier achieving **>90% precision and recall**.
  * Packages the model artifact into standard SageMaker format: `artifacts/model.tar.gz`.
* **SageMaker Deployment Script**: [`src/ml/sagemaker_deploy_endpoint.py`](file:///d:/APIIT/Final%20Year/ECDWA/CloudFusion-Healthcare/src/ml/sagemaker_deploy_endpoint.py)
  * Defines the official AWS XGBoost inference container.
  * Configures an **Amazon SageMaker Serverless Inference Endpoint** with 2048 MB memory and max concurrency of 20 ($0.00 idle cost).
  * Simulates sample patient telemetry payload inference.

---

## 4. Running the Model Training Script Locally

To train the model and generate the SageMaker artifact:
```bash
python src/ml/train_sepsis_model.py
```

Sample output:
```
======================================================================
CloudFusion Healthcare Analytics - Amazon SageMaker ML Training Engine
Author: Shehan Jaye (CB012510) | AWS Account: 460060049985
======================================================================
[1/5] Synthesizing 5,000 multi-parameter ICU vital sign records...
      Train Set: 4000 samples | Test Set: 1000 samples
[2/5] Training multivariate clinical deterioration classifier...
[Phase 4/5] Evaluating Classifier on Unseen Cohort (N = 1,000)...
-------------------------------------------------------
  Test Accuracy:        98.70%
  Recall (Sensitivity): 95.00% (High sensitivity avoids missed shock)
  Precision:            99.56%
  F1-Score:             97.23%
  Area Under ROC (AUC): 0.9998
-------------------------------------------------------
      [OK] High-resolution evaluation figure exported: docs/report/figures/ml_sepsis_model_evaluation.png

[Phase 5/5] Exporting Amazon SageMaker Artifacts (model.tar.gz)...
      [OK] Parameters saved: src/ml/artifacts/model_params.json
      [OK] SageMaker Archive: src/ml/artifacts/model.tar.gz

======================================================================
REAL-TIME CLINICAL INFERENCE SIMULATION (AMAZON SAGEMAKER ENDPOINT)
======================================================================
Profile: Patient 02: Mr. Kavindu Bandara (Impending Septic Deterioration)
  Vitals: HR=118.0 BPM | SpO2=90.5% | BP=88.0/54.0 mmHg | Temp=38.9°C | RR=27.0/min
  Shock Index (HR/SBP): 1.34 (Normal < 0.70)
  >> SageMaker Predicted Deterioration Probability: 100.0%
  >> TRIAGE: [CRITICAL ALERT] HIGH PROBABILITY OF SEPTIC SHOCK WITHIN 24 HOURS!
  >> DISPATCH: Amazon SNS -> Automated emergency alert sent to ICU Attending Physician.
======================================================================
```
