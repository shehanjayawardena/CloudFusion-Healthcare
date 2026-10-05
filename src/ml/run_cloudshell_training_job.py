"""
CloudFusion Healthcare Analytics Ltd (CHA)
AWS CloudShell One-Shot SageMaker Training Job Launcher
Module: COMP60010 - Enterprise Cloud and Distributed Web Applications
Author: Shehan Jaye (CB012510) | AWS Account: 460060049985
Target AWS Region: ap-southeast-1 (Singapore)

Run this script directly in AWS CloudShell (terminal inside AWS Console).
It will:
1. Ensure the IAM execution role exists.
2. Upload the synthetic ICU vitals dataset to S3.
3. Launch a short (~2 min) Amazon SageMaker Training Job.
4. Display the Training Job in your SageMaker Console ready for screenshots.
"""

import os
import sys
import time
import json
import boto3

REGION = "ap-southeast-1"
ACCOUNT_ID = "460060049985"
BUCKET_NAME = f"cha-healthcare-prod-lake-{ACCOUNT_ID}"
JOB_NAME = f"cha-sepsis-training-{int(time.time())}"

def main():
    print("=" * 75)
    print("CLOUDFUSION HEALTHCARE - AWS SAGEMAKER TRAINING JOB LAUNCHER")
    print(f"Account: {ACCOUNT_ID} | Region: {REGION} | Bucket: {BUCKET_NAME}")
    print("=" * 75)

    s3 = boto3.client("s3", region_name=REGION)
    iam = boto3.client("iam", region_name=REGION)
    sm = boto3.client("sagemaker", region_name=REGION)

    # 1. Setup IAM Execution Role for SageMaker
    role_name = "CHA-SageMaker-ExecutionRole"
    print(f"\n[1/4] Verifying IAM Role: {role_name}...")
    try:
        role_resp = iam.get_role(RoleName=role_name)
        role_arn = role_resp["Role"]["Arn"]
        print(f"      [OK] Found existing role: {role_arn}")
    except iam.exceptions.NoSuchEntityException:
        print("      Creating new SageMaker Execution Role...")
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "sagemaker.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        role_resp = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Execution role for CHA SageMaker Sepsis Training Jobs"
        )
        role_arn = role_resp["Role"]["Arn"]
        iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonSageMakerFullAccess")
        iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess")
        print(f"      [OK] Created and configured role: {role_arn}")
        time.sleep(10) # Wait for IAM propagation

    # 2. Upload Training Dataset to S3
    print(f"\n[2/4] Generating and uploading clinical dataset to s3://{BUCKET_NAME}/ml-training/...")
    
    # Generate 5,000 synthetic patient records (XGBoost CSV format: target in 1st col, no header)
    import numpy as np
    np.random.seed(42)
    n_samples = 5000
    hr = np.clip(np.random.normal(78, 15, n_samples), 45, 175)
    spo2 = np.clip(np.random.normal(97.5, 2.4, n_samples), 75, 100)
    sbp = np.clip(np.random.normal(122, 17, n_samples), 65, 200)
    dbp = np.clip(np.random.normal(76, 11, n_samples), 40, 120)
    temp = np.clip(np.random.normal(36.8, 0.7, n_samples), 35.0, 41.0)
    rr = np.clip(np.random.normal(16, 3.8, n_samples), 8, 42)
    shock_index = hr / sbp
    
    risk_score = 0.045*(hr - 75) - 0.14*(spo2 - 95) - 0.035*(sbp - 110) + 1.6*(temp - 37.0) + 0.085*(rr - 16) + 2.8*(shock_index - 0.7)
    labels = (1.0 / (1.0 + np.exp(-risk_score)) >= 0.52).astype(int)
    
    lines = []
    for i in range(n_samples):
        lines.append(f"{labels[i]},{hr[i]:.1f},{spo2[i]:.1f},{sbp[i]:.1f},{dbp[i]:.1f},{temp[i]:.2f},{rr[i]:.1f},{shock_index[i]:.3f}\n")
        
    csv_payload = "".join(lines).encode("utf-8")
    s3_train_key = "ml-training/train_vitals.csv"
    s3.put_object(Bucket=BUCKET_NAME, Key=s3_train_key, Body=csv_payload)
    print(f"      [OK] Uploaded {n_samples} records to s3://{BUCKET_NAME}/{s3_train_key}")

    # 3. Built-in XGBoost Algorithm Image URI for ap-southeast-1
    # Official AWS SageMaker XGBoost ECR container registry for Singapore
    xgboost_image = "475088407865.dkr.ecr.ap-southeast-1.amazonaws.com/sagemaker-xgboost:1.5-1"
    
    # 4. Launch SageMaker Training Job
    print(f"\n[3/4] Launching Amazon SageMaker Training Job: {JOB_NAME}...")
    training_params = {
        "TrainingJobName": JOB_NAME,
        "AlgorithmSpecification": {
            "TrainingImage": xgboost_image,
            "TrainingInputMode": "File"
        },
        "RoleArn": role_arn,
        "InputDataConfig": [
            {
                "ChannelName": "train",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": f"s3://{BUCKET_NAME}/ml-training/",
                        "S3DataDistributionType": "FullyReplicated"
                    }
                },
                "ContentType": "text/csv",
                "CompressionType": "None"
            }
        ],
        "OutputDataConfig": {
            "S3OutputPath": f"s3://{BUCKET_NAME}/ml-models/output/"
        },
        "ResourceConfig": {
            "InstanceType": "ml.m5.xlarge",
            "InstanceCount": 1,
            "VolumeSizeInGB": 5
        },
        "StoppingCondition": {
            "MaxRuntimeInSeconds": 600
        },
        "HyperParameters": {
            "max_depth": "5",
            "eta": "0.1",
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "num_round": "50"
        }
    }
    
    resp = sm.create_training_job(**training_params)
    print(f"      [OK] Training Job successfully created!")
    print(f"      Job ARN: {resp['TrainingJobArn']}")
    
    # 5. Monitor Status
    print("\n[4/4] Monitoring Training Job Status in AWS Console...")
    print("      (You can open Amazon SageMaker AI -> Training -> Training jobs in your browser now!)")
    
    while True:
        desc = sm.describe_training_job(TrainingJobName=JOB_NAME)
        status = desc["TrainingJobStatus"]
        print(f"      Status: [{status}] ...", flush=True)
        if status in ["Completed", "Failed", "Stopped"]:
            break
        time.sleep(15)
        
    print("=" * 75)
    if status == "Completed":
        print("SUCCESS! Training job COMPLETED successfully on AWS.")
        print(f"Output model artifact saved to: {desc['ModelArtifacts']['S3ModelArtifacts']}")
        print("\n>> TAKE YOUR SCREENSHOT NOW:")
        print("   Go to: Amazon SageMaker AI -> Training -> Training jobs -> " + JOB_NAME)
    else:
        print(f"Job ended with status: {status}")
        if "FailureReason" in desc:
            print(f"Reason: {desc['FailureReason']}")
    print("=" * 75)

if __name__ == "__main__":
    main()
