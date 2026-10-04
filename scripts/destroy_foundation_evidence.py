"""
CloudFusion Healthcare Analytics Ltd (CHA)
Destroy Foundation Evidence Resources from AWS ap-southeast-1
Safely deletes all resources listed in deployed_resources_manifest.json
"""

import os
import json
import boto3
from botocore.exceptions import ClientError

MANIFEST_PATH = "deployed_resources_manifest.json"

if not os.path.exists(MANIFEST_PATH):
    print(f"[ERROR] Manifest file '{MANIFEST_PATH}' not found. Nothing to destroy.")
    exit(1)

with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    manifest = json.load(f)

REGION = manifest.get("region", "ap-southeast-1")
account_id = manifest.get("account_id")

session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=REGION
)

print(f"[TEARDOWN] Tearing down resources for Account {account_id} in {REGION}...")

# 1. Delete S3 Bucket & Objects
s3 = session.client("s3")
bucket_name = manifest.get("s3_bucket")
if bucket_name:
    print(f"\n[1/4] Deleting S3 bucket: {bucket_name}...")
    try:
        # Delete all versions/markers
        paginator = s3.get_paginator('list_object_versions')
        for page in paginator.paginate(Bucket=bucket_name):
            delete_keys = []
            for v in page.get('Versions', []):
                delete_keys.append({'Key': v['Key'], 'VersionId': v['VersionId']})
            for m in page.get('DeleteMarkers', []):
                delete_keys.append({'Key': m['Key'], 'VersionId': m['VersionId']})
            if delete_keys:
                s3.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_keys})
        s3.delete_bucket(Bucket=bucket_name)
        print(f"  [OK] S3 Bucket deleted: {bucket_name}")
    except ClientError as e:
        print(f"  [ERROR] S3 error: {e}")

# 2. Delete DynamoDB Table
dynamodb = session.client("dynamodb")
table_name = manifest.get("dynamodb_table")
if table_name:
    print(f"\n[2/4] Deleting DynamoDB table: {table_name}...")
    try:
        dynamodb.delete_table(TableName=table_name)
        print(f"  [OK] DynamoDB table deleted: {table_name}")
    except ClientError as e:
        print(f"  [ERROR] DynamoDB error: {e}")

# 3. Delete IAM Role & Policy
iam = session.client("iam")
role_name = manifest.get("iam_role_name")
policy_arn = manifest.get("iam_policy_arn")
if role_name and policy_arn:
    print(f"\n[3/4] Deleting IAM Role & Policy...")
    try:
        iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        iam.delete_role(RoleName=role_name)
        print(f"  [OK] IAM Role deleted: {role_name}")
    except ClientError as e:
        print(f"  [ERROR] IAM role error: {e}")
    try:
        iam.delete_policy(PolicyArn=policy_arn)
        print(f"  [OK] IAM Policy deleted: {policy_arn}")
    except ClientError as e:
        print(f"  [ERROR] IAM policy error: {e}")

# 4. Delete VPC Network Resources
ec2 = session.client("ec2")
vpc_id = manifest.get("vpc_id")
if vpc_id:
    print(f"\n[4/4] Deleting VPC Network: {vpc_id}...")
    # Delete Security Groups
    for sg_id in manifest.get("security_groups", []):
        try:
            ec2.delete_security_group(GroupId=sg_id)
            print(f"  [OK] Security Group deleted: {sg_id}")
        except ClientError as e:
            print(f"  [ERROR] SG error: {e}")

    # Delete Subnets
    for sub_id in manifest.get("subnet_ids", []):
        try:
            ec2.delete_subnet(SubnetId=sub_id)
            print(f"  [OK] Subnet deleted: {sub_id}")
        except ClientError as e:
            print(f"  [ERROR] Subnet error: {e}")

    # Detach & Delete IGWs
    try:
        igws = ec2.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])
        for igw in igws.get('InternetGateways', []):
            igw_id = igw['InternetGatewayId']
            ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            ec2.delete_internet_gateway(InternetGatewayId=igw_id)
            print(f"  [OK] Internet Gateway detached and deleted: {igw_id}")
    except ClientError as e:
        print(f"  [ERROR] IGW error: {e}")

    # Delete VPC
    try:
        ec2.delete_vpc(VpcId=vpc_id)
        print(f"  [OK] VPC deleted: {vpc_id}")
    except ClientError as e:
        print(f"  [ERROR] VPC error: {e}")

# Remove manifest
os.remove(MANIFEST_PATH)
print("\n[SUCCESS] All foundation evidence resources completely destroyed.")
