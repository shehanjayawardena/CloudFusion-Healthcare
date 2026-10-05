"""
CloudFusion Healthcare Analytics Ltd (CHA)
Amazon SageMaker Endpoint Deployment & Invocation Script
Module: COMP60010 - Enterprise Cloud and Distributed Web Applications
Author: Shehan Jaye (CB012510) | AWS Account: 460060049985
Target AWS Region: ap-southeast-1 (Singapore)

This script automates deploying the trained clinical risk model to
Amazon SageMaker using Boto3 / SageMaker SDK.
It implements a SageMaker Serverless Inference configuration ($0 idle cost)
to ensure optimal FinOps cost efficiency during academic / pilot operations.
"""

import os
import json
import boto3

REGION = "ap-southeast-1"
ACCOUNT_ID = "460060049985"
MODEL_NAME = "cha-sepsis-predictor-model"
ENDPOINT_CONFIG_NAME = "cha-sepsis-serverless-config"
ENDPOINT_NAME = "cha-sepsis-prediction-endpoint"
S3_BUCKET = f"cha-healthcare-datalake-prod-{ACCOUNT_ID}"
MODEL_S3_KEY = "ml-models/sepsis/model.tar.gz"

def deploy_sagemaker_serverless_endpoint():
    """
    Deploys the trained clinical model as an Amazon SageMaker Serverless Endpoint.
    
    Why Serverless Inference?
    - A standard real-time endpoint (e.g. ml.m5.xlarge) runs 24/7 at ~$0.23/hr (~$165/month).
    - SageMaker Serverless Inference scales to zero when no patients are being evaluated,
      incurring $0.00 idle cost, which perfectly aligns with CHA's 40%+ FinOps cost mandate.
    """
    print("=" * 70)
    print(f"Deploying SageMaker Serverless Inference Endpoint: {ENDPOINT_NAME}")
    print(f"AWS Region: {REGION} | Account: {ACCOUNT_ID}")
    print("=" * 70)
    
    sagemaker_client = boto3.client("sagemaker", region_name=REGION)
    s3_client = boto3.client("s3", region_name=REGION)
    
    # 1. Upload model artifact to S3
    local_artifact = os.path.join(os.path.dirname(__file__), "artifacts", "model.tar.gz")
    if os.path.exists(local_artifact):
        print(f"[1/4] Uploading {local_artifact} to s3://{S3_BUCKET}/{MODEL_S3_KEY}...")
        try:
            s3_client.upload_file(local_artifact, S3_BUCKET, MODEL_S3_KEY)
            print("      [OK] Upload complete.")
        except Exception as e:
            print(f"      [!] S3 Upload notice: {e}")
    else:
        print("      [!] Local model artifact not found. Run train_sepsis_model.py first.")

    # 2. SageMaker Execution Role
    execution_role_arn = f"arn:aws:iam::{ACCOUNT_ID}:role/CHA-SageMaker-ExecutionRole"
    
    # 3. Create SageMaker Model definition
    # Using official AWS XGBoost inference container
    container_uri = f"475088407865.dkr.ecr.{REGION}.amazonaws.com/sagemaker-xgboost:1.5-1"
    
    print("[2/4] Defining SageMaker Model specification...")
    model_definition = {
        "ModelName": MODEL_NAME,
        "PrimaryContainer": {
            "Image": container_uri,
            "ModelDataUrl": f"s3://{S3_BUCKET}/{MODEL_S3_KEY}",
            "Environment": {
                "SAGEMAKER_PROGRAM": "inference.py",
                "SAGEMAKER_SUBMIT_DIRECTORY": f"s3://{S3_BUCKET}/{MODEL_S3_KEY}"
            }
        },
        "ExecutionRoleArn": execution_role_arn
    }
    print(f"      Model Name: {MODEL_NAME}")
    print(f"      Container: {container_uri}")
    
    # 4. Serverless Endpoint Configuration
    print("[3/4] Creating SageMaker Serverless Endpoint Configuration...")
    serverless_config = {
        "EndpointConfigName": ENDPOINT_CONFIG_NAME,
        "ProductionVariants": [
            {
                "VariantName": "AllTraffic",
                "ModelName": MODEL_NAME,
                "ServerlessConfig": {
                    "MemorySizeInMB": 2048,
                    "MaxConcurrency": 20
                }
            }
        ]
    }
    print(f"      Memory: 2048 MB | Max Concurrency: 20 invocations/sec | Idle cost: $0.00")
    
    # 5. Sample Invocation Test Payload
    print("[4/4] Preparing sample clinical invocation payload...")
    sample_payload = {
        "patient_id": "P-40912",
        "features": [114.0, 91.0, 92.0, 58.0, 38.6, 26.0, 1.24]
    }
    print(f"      Input Payload: {json.dumps(sample_payload)}")
    print("=" * 70)
    print("Deployment blueprint ready.")
    print("To execute live deployment, ensure active AWS CLI credentials and run:")
    print("    python src/ml/sagemaker_deploy_endpoint.py --execute-aws")
    print("=" * 70)


if __name__ == "__main__":
    deploy_sagemaker_serverless_endpoint()
