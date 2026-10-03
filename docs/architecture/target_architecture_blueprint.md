# CloudFusion Healthcare Analytics Ltd (CHA)
## Target AWS Architecture Blueprint & System Specification

---

### Executive Overview & Architectural Objectives
CloudFusion Healthcare Analytics Ltd (CHA) is migrating from a legacy, single-site on-premises VMware data center (220 virtual machines, monolithic applications, Microsoft SQL Server & MySQL) to an enterprise-grade, cloud-native Amazon Web Services (AWS) architecture. 

This target architecture is engineered to fulfill CHA’s critical business drivers:
1. **High Availability**: 99.99% uptime SLA across all clinical patient monitoring and telehealth applications.
2. **Scalability**: Seamlessly accommodate over 100,000 concurrent active users (patients, clinical staff, laboratory doctors).
3. **Cost Reduction**: Lower total cost of ownership (TCO) and infrastructure operational expenses by at least 40% using serverless, managed containers, and savings commitments.
4. **Data Protection & Compliance**: Strict adherence to healthcare compliance frameworks (GDPR, HIPAA, ISO 27001, NHS DSP Toolkit) featuring end-to-end envelope encryption, immutable audit logging, and least-privilege attribute-based access control (ABAC).
5. **Real-time IoT & AI Innovation**: Sub-second ingestion of telemetry from wearable medical devices and AI-driven clinical risk predictive modeling.
6. **Robust Business Continuity**: Disaster recovery posture with Recovery Time Objective (RTO) < 1 hour and Recovery Point Objective (RPO) < 15 minutes.

---

### 1. Multi-Tier Multi-AZ VPC Network Architecture

#### 1.1 IP Addressing and Subnet Segmentation
The infrastructure is deployed within a dedicated Virtual Private Cloud (VPC) spanning three Availability Zones (AZ-a, AZ-b, AZ-c) in the AWS Asia Pacific (Singapore) region (`ap-southeast-1`), ensuring resilience against localized data center failures.

```
VPC CIDR Block: 10.50.0.0/16 (65,536 Total IP Addresses)
├── Availability Zone 1 (ap-southeast-1a)
│   ├── Public Subnet (ALB, NAT Gateway-A):       10.50.1.0/24   (251 usable IPs)
│   ├── Private App Subnet (ECS Fargate, Lambda):  10.50.10.0/24  (251 usable IPs)
│   └── Private DB Subnet (Aurora, Cache):         10.50.100.0/24 (251 usable IPs)
├── Availability Zone 2 (ap-southeast-1b)
│   ├── Public Subnet (ALB, NAT Gateway-B):       10.50.2.0/24   (251 usable IPs)
│   ├── Private App Subnet (ECS Fargate, Lambda):  10.50.20.0/24  (251 usable IPs)
│   └── Private DB Subnet (Aurora, Cache):         10.50.110.0/24 (251 usable IPs)
└── Availability Zone 3 (ap-southeast-1c)
    ├── Public Subnet (ALB, NAT Gateway-C):       10.50.3.0/24   (251 usable IPs)
    ├── Private App Subnet (ECS Fargate, Lambda):  10.50.30.0/24  (251 usable IPs)
    └── Private DB Subnet (Aurora, Cache):         10.50.120.0/24 (251 usable IPs)
```

#### 1.2 Routing, Egress Control & Endpoints
* **Public Subnets**: Connected directly to an **Internet Gateway (IGW)** for incoming user HTTPS traffic terminated at the public Application Load Balancer.
* **Private Application Subnets**: Route all non-VPC outbound traffic through dedicated **NAT Gateways** (one per AZ) to ensure high-availability egress for third-party medical API interactions and patch management without inbound exposure.
* **Private Database Subnets**: Completely isolated with no routes to the Internet or NAT Gateways. Traffic is only permitted from the application subnets via strict Security Group ingress rules.
* **VPC Endpoints (AWS PrivateLink)**:
  * **Gateway Endpoints**: Amazon S3 and Amazon DynamoDB traffic traverses private AWS backbone routes, avoiding NAT Gateway data processing charges.
  * **Interface Endpoints**: AWS Secrets Manager, AWS KMS, CloudWatch Logs, ECR, and AWS Systems Manager (SSM) maintain end-to-end private IP communication.

---

### 2. Patient Monitoring Platform (PMP) Architecture

The Patient Monitoring Platform (PMP) processes real-time vital signs (heart rate, SpO2, ECG waveforms, blood pressure) captured by wearable IoT medical devices.

```
[Wearable Medical Devices] 
         │ (MQTT over TLS 1.3 / X.509 Device Certs)
         ▼
[AWS IoT Core] ─────────► [IoT Rules Engine]
                             │
     ┌───────────────────────┴────────────────────────┐
     │ Urgent Vitals (Anomaly Detected)               │ Continuous Telemetry Stream
     ▼                                                ▼
[Amazon SNS / SQS]                            [Amazon Kinesis Data Streams]
     │                                                │
     ▼                                                ▼
[AWS Lambda (Emergency Triage)]               [Kinesis Data Firehose] ──► [Amazon S3 Raw Data Lake]
     │                                                │
     ├─► Push Alert to Clinician (Doctor Mobile App)  ▼
     └─► Write Critical Event to DynamoDB      [Amazon Timestream / DynamoDB]
                                                      │
                                                      ▼
                                       [PMP Real-Time Dashboard (ECS Fargate)]
```

#### 2.1 Ingestion & Message Processing Pipeline
1. **Device Authentication**: Medical wearable devices connect to **AWS IoT Core** using mutual TLS (mTLS) with individual X.509 client certificates registered in AWS IoT Device Management.
2. **IoT Rules Engine**: Evaluates incoming telemetry against clinical threshold rules (e.g., `SpO2 < 90%` or `HeartRate > 140 BPM`).
   * **Critical Vitals Pathway**: Instantly dispatches alerts to an **Amazon SNS** topic and an **Amazon SQS** Dead Letter Queue (DLQ). Dedicated serverless **AWS Lambda** microservices notify hospital on-call teams within <500ms.
   * **Telemetry Aggregation Pathway**: Telemetry streams into **Amazon Kinesis Data Streams** with 24-hour data retention, buffering up to 100,000 concurrent device payloads.
3. **Storage & Analytics**:
   * **Hot Storage**: Real-time telemetry is written to **Amazon DynamoDB** with an aggressive Time-To-Live (TTL) of 30 days and single-digit millisecond query latencies.
   * **Time-Series Analysis**: High-frequency ECG and vitals are ingested into **Amazon Timestream** for real-time trend analytics and visualization.
   * **Cold Storage / Data Lake**: **Amazon Kinesis Data Firehose** dynamically batches, compresses (Snappy), and converts payloads to columnar Apache Parquet before landing them in **Amazon S3 Medical Data Lake**.

---

### 3. Telemedicine and Patient Portal (TPP) Architecture

The Telemedicine and Patient Portal (TPP) is a distributed, containerized web platform enabling secure video consultations, medical record retrieval, appointment bookings, and lab reporting.

```
       [Patients & Doctors Web / Mobile Clients]
                          │
                          ▼
            [Amazon Route 53 (Latency & Failover)]
                          │
                          ▼
            [Amazon CloudFront CDN + AWS WAF]
             │                             │
    (Static Assets / SPA)          (Dynamic API Traffic)
             │                             │
             ▼                             ▼
   [Amazon S3 (OAC Protected)]   [Application Load Balancer]
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
        [ECS Fargate: Patient API]                    [ECS Fargate: Telehealth Engine]
                    │                                             │
      ┌─────────────┼─────────────┐                               ▼
      ▼             ▼             ▼                    [Amazon Chime SDK / WebRTC]
[Aurora PG]  [DynamoDB]  [ElastiCache Redis]             (Encrypted P2P Media Streams)
```

#### 3.1 Edge Tier & Presentation
* **DNS & Routing**: **Amazon Route 53** handles global low-latency routing, health checks, and automatic DNS failover.
* **Content Delivery & Protection**: **Amazon CloudFront** accelerates static delivery (React SPA) and dynamic API requests with TLS 1.3. CloudFront is safeguarded by **AWS WAF** configured with AWS Managed Rule Sets (Core Rule Set, SQLi protection, Known Bad Inputs, Rate Limiting).
* **Static Origin Security**: Web assets reside in an S3 bucket accessible exclusively via CloudFront using **Origin Access Control (OAC)**; direct public bucket access is prohibited.

#### 3.2 Compute & Microservices Tier (ECS Fargate)
* **Container Orchestration**: The dynamic microservices operate on **Amazon Elastic Container Service (ECS)** with the **AWS Fargate** serverless launch type, eliminating OS patching, kernel vulnerabilities, and EC2 capacity management.
* **Services Breakdown**:
  * `patient-record-service`: Manages electronic health records (EHR) with strict access control.
  * `appointment-booking-service`: Coordinates clinic schedules and physician availability.
  * `telehealth-session-service`: Manages appointment tokens, room authentication, and connects patients to clinicians via **Amazon Chime SDK** WebRTC encrypted sessions.
  * `notification-service`: Triggers automated SMS and email reminders via Amazon SNS and Amazon SES.
* **Elastic Scalability**: Configured with ECS Auto Scaling policies utilizing target tracking metrics (Target CPU 65%, Target Memory 70%, and ALB Request Count per Target), scaling between 6 and 60 container tasks across all 3 AZs.

#### 3.3 Persistence Tier
* **Relational Database**: **Amazon Aurora PostgreSQL Serverless v2 (Multi-AZ)**. Stores structured clinical records, user accounts, and billing transactions. Features automated multi-AZ failover (<30 seconds) and read replicas to offload reporting queries.
* **NoSQL Database**: **Amazon DynamoDB** stores session tokens, chat history, and audit trails with On-Demand capacity and global secondary indexes (GSIs).
* **In-Memory Caching**: **Amazon ElastiCache for Redis (Cluster Mode Enabled)** caches frequently queried physician directories, authorization tokens, and appointment slots to preserve database performance under peak traffic.

---

### 4. Security, Governance, and Compliance Framework

```
+-----------------------------------------------------------------------------------+
|                            AWS WAF & AWS Shield Advanced                          |
+-----------------------------------------------------------------------------------+
|                                 Network Boundaries                                |
|        Public ALB SG  ──►  ECS Fargate SG  ──►  Aurora DB / Cache SG              |
|        (Port 443 only)      (Port 8080/8443)    (Port 5432 / 6379)                |
+-----------------------------------------------------------------------------------+
|                             Identity & Access (IAM)                               |
|        - Least Privilege ABAC Roles (Doctor, Nurse, Admin)                        |
|        - Enforced Hardware MFA for Administrative Consoles                        |
|        - Temporary Credentials via AWS STS & AWS IAM Identity Center              |
+-----------------------------------------------------------------------------------+
|                             Data Protection & Cryptography                        |
|        - Encryption at Rest: AWS KMS Customer Managed Keys (CMK) with Rotation   |
|        - Encryption in Transit: Mandatory TLS 1.3 (Strict cipher suites)          |
|        - AWS Secrets Manager: Automatic 30-day credential rotation for DB         |
+-----------------------------------------------------------------------------------+
|                             Auditing, Detection & Compliance                      |
|        - AWS CloudTrail (Organization-wide, S3 object-level auditing, WORM)       |
|        - AWS Config (Continuous compliance conformance packs for HIPAA/GDPR)      |
|        - Amazon GuardDuty (Intelligent threat detection & anomaly monitoring)     |
|        - AWS Security Hub (Centralized posture score & CIS AWS Benchmark alerts)  |
+-----------------------------------------------------------------------------------+
```

#### 4.1 Cryptographic Controls (AWS KMS)
* Dedicated **Customer Managed Keys (CMKs)** with automated annual key rotation for:
  * Database Volumes (`arn:aws:kms:...:key/cha-aurora-key`)
  * Object Storage (`arn:aws:kms:...:key/cha-s3-medical-key`)
  * IoT Telemetry Streaming (`arn:aws:kms:...:key/cha-kinesis-key`)
* All S3 buckets enforce default KMS envelope encryption and reject any `s3:PutObject` request missing server-side encryption or utilizing unencrypted HTTP (`aws:SecureTransport: false`).

#### 4.2 Healthcare Compliance Posture (GDPR & HIPAA)
* **Data Sovereignty & Localization**: All clinical databases and backups reside strictly in compliant regions with cross-region replication restricted to sovereign jurisdictions.
* **Right to Erasure (GDPR Article 17)**: Patient identifiers are pseudonymized in analytics datasets. Cryptographic erasure techniques are implemented where individual encryption sub-keys can be revoked.
* **Immutable Audit Trail**: AWS CloudTrail logs are delivered to an isolated Security Account S3 bucket protected with **S3 Object Lock (Compliance Mode)**, preventing alteration or deletion even by root administrators.

---

### 5. Hybrid Connectivity and Edge Integration Architecture

To seamlessly integrate CHA's 22 branch hospitals, clinics, and laboratories with AWS:

```
[Branch Hospital 1] ────┐
[Branch Hospital 2] ────┼──► [AWS Direct Connect (10 Gbps Dedicated)] ──┐
[Central Clinic HQ] ────┘                                               │
                                                                        ▼
[Backup Dual IPsec VPN] ──────────────────────────────────────────► [AWS Transit Gateway]
                                                                        │
                         ┌──────────────────────────────────────────────┴──────────────┐
                         ▼                                                             ▼
                 [Production VPC]                                               [Shared Services VPC]
              (10.50.0.0/16 - PMP/TPP)                                          (Route 53 Resolver)
```

#### 5.1 Hybrid Connectivity & Failover
* **Primary Link**: **AWS Direct Connect (DX)** with a 10 Gbps dedicated fiber circuit providing sub-5ms deterministic latency for transmitting large DICOM medical imaging files and real-time telehealth video feeds.
* **Secondary Link**: Automated BGP failover to **AWS Site-to-Site IPsec VPN** running dual active-active tunnels across redundant customer gateways (CGWs).
* **Interconnect Hub**: **AWS Transit Gateway (TGW)** aggregates connections from all 22 branch locations, providing centralized routing, segment isolation, and inspection through a central firewall VPC.

#### 5.2 Hybrid DNS Resolution (Route 53 Resolver)
* **Outbound Resolver Endpoints**: Allow AWS workloads in the VPC to resolve internal on-premises clinical domains (`*.hospital.internal`) over the Direct Connect link.
* **Inbound Resolver Endpoints**: Allow hospital workstation browsers and medical diagnostic hardware on-prem to seamlessly resolve private AWS service domains (`*.cloudfusion.internal`).

#### 5.3 Edge Computing with AWS IoT Greengrass v2
* Industrial medical edge appliances deployed at each hospital branch run **AWS IoT Greengrass v2**.
* **Edge Processing**: High-frequency medical sensor streams are processed locally using containerized Python components. Greengrass performs noise filtering, deduplication, and immediate anomaly detection.
* **Store-and-Forward**: If the hybrid network link is temporarily interrupted, the edge device safely buffers vital signs in an encrypted local database and synchronizes all records upon reconnection, preventing telemetry loss.

---

### 6. Data Migration & Business Continuity Blueprint

```
[On-Premises Microsoft SQL & MySQL]
               │
               ▼
[AWS DMS Replication Instance (Multi-AZ)]
   ├── CDC (Change Data Capture) ─────────► [Amazon Aurora PostgreSQL (Target)]
   └── Full Initial Export (Historical) ──► [Amazon S3 Staging Bucket]
                                                   │
                                                   ▼
                                         [AWS Glue PySpark Job]
                                         (Transform, Hash, Verify)
                                                   │
                                                   ▼
                                         [Amazon S3 Analytics Lake (Parquet)]
                                         (SHA-256 Checksum Validation)
```

#### 6.1 Database Migration via AWS DMS
* **Replication Strategy**: Uses **AWS Database Migration Service (AWS DMS)** configured with Multi-AZ high availability.
* **Phase 1: Full Load**: Migrates initial bulk tables from legacy SQL Server and MySQL to target Aurora PostgreSQL schemas (with schema transformation handled by AWS Schema Conversion Tool - SCT).
* **Phase 2: Continuous CDC**: Captures ongoing database transaction logs (MS SQL Transaction Logs and MySQL binlog) to replicate changes with <2 seconds latency.
* **Cutover**: Minimal maintenance window (<15 minutes) during off-peak hours where DNS is repointed and final CDC transactions are validated.

#### 6.2 Historical Data Migration & Integrity Verification (AWS Glue)
* 5+ years of historical patient records and diagnostic logs are exported directly into an S3 staging area.
* An **AWS Glue (PySpark)** job parses, validates, and converts the datasets into partitioned Snappy-compressed Parquet tables in the Health Data Lake.
* **Data Integrity**: The ETL job computes SHA-256 cryptographic hashes row-by-row and verifies checksums against source database manifests before signing off migration validity.

---

### 7. Architectural Component & Specification Summary

| Domain | On-Premises Baseline (Legacy) | Proposed AWS Cloud Architecture | Strategic Justification |
| :--- | :--- | :--- | :--- |
| **Compute** | 220 VMware Virtual Machines | **Amazon ECS on AWS Fargate** | Eliminates server maintenance; sub-minute auto-scaling for 100k users. |
| **Databases** | Standalone MS SQL Server & MySQL | **Amazon Aurora Multi-AZ + DynamoDB** | Automated 6-way storage replication across 3 AZs; 99.99% availability. |
| **IoT Ingestion** | Legacy socket server (Single point of failure) | **AWS IoT Core + Kinesis Data Streams** | Scales to millions of MQTT messages; native cloud security integration. |
| **Edge Compute** | Unmanaged local PCs in clinics | **AWS IoT Greengrass v2** | Edge inference, local data caching, resilience against WAN outage. |
| **Storage** | On-premises SAN arrays | **Amazon S3 (Intelligent-Tiering & Glacier)** | 99.999999999% (11 9s) durability; automated lifecycle cost reduction. |
| **Security** | Static perimeter firewalls & LDAP | **AWS WAF + KMS + IAM ABAC + GuardDuty** | Defense-in-depth, envelope encryption, automated threat detection. |
| **Networking** | Legacy site-to-site IPsec VPN | **Direct Connect (10 Gbps) + Transit Gateway** | Low-latency DICOM/telehealth throughput with redundant failover. |
| **Disaster Recovery**| None (Single data center) | **Multi-AZ Active/Active + Cross-Region DR** | Eliminates single points of failure; RTO < 1 hour, RPO < 15 minutes. |
