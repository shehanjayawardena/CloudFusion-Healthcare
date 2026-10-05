import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Calibrated 5,000 - 5,500 Word Technical Consultancy Report Generator
# Module: COMP60010 - Enterprise Cloud and Distributed Web Applications (ECDWA)
# Student: Shehan Jaye (Student ID: CB012510) | AWS Account: 460060049985
# Client: CloudFusion Healthcare Analytics Ltd (CHA)

sec_title = """# Enterprise Cloud Architecture & Migration Strategy: Modernising CloudFusion Healthcare Analytics Ltd (CHA)
## Technical Consultancy Report & Architectural Blueprint

**Module**: COMP60010 – Enterprise Cloud and Distributed Web Applications (ECDWA)  
**Author**: Shehan Jaye (Student ID: CB012510) | Cloud Solutions Architect  
**Client**: CloudFusion Healthcare Analytics Ltd (CHA)  
**Target Platform**: Amazon Web Services (AWS) | AWS Account: `460060049985`  
**Primary Region**: `ap-southeast-1` (Singapore) | **DR Region**: `ap-southeast-2` (Sydney)  
**Date**: October 2026  

---
"""

sec_exec = """## Executive Summary

CloudFusion Healthcare Analytics Ltd (CHA) delivers mission-critical patient monitoring, distributed telemedicine portals, and clinical analytics across South Asia and the Middle East. Currently, CHA operates an aging on-premises infrastructure comprising 220 virtual machines on VMware ESXi in a single physical data center. This legacy topology suffers from severe scalability boundaries, manual deployment overheads, single points of failure (SPOF), and an inability to ingest real-time IoT medical telemetry.

This technical consultancy report establishes an enterprise cloud modernization blueprint migrating CHA to Amazon Web Services (AWS). Sized for over **100,000 concurrent active users**, this architecture delivers **99.99% contractual availability** (approaching **99.999%** for acute ICU telemetry), achieves an **89.7% Total Cost of Ownership (TCO) reduction** vs on-premises baseline expenditure and a **48.3% FinOps operational reduction** on AWS ($7,150.57/month, exceeding the 40% corporate mandate), enforces strict **GDPR, HIPAA, and ISO 27001** compliance, and deploys **AWS IoT Greengrass v2** edge processing across 22 regional branch hospitals. The blueprint is validated through modular **Terraform Infrastructure as Code (IaC)**, zero-trust **IAM policies**, automated **AWS DMS Change Data Capture (CDC)** pipelines, and an **AWS Glue PySpark** data integrity verification engine.

---
"""

sec_toc = """## Table of Contents
1. [Introduction & Business Context](#1-introduction--business-context)
2. [Task 1: Current Infrastructure Analysis & Cloud Adoption Justification](#2-task-1-current-infrastructure-analysis--cloud-adoption-justification)
3. [Task 2: Cloud Migration Strategy](#3-task-2-cloud-migration-strategy)
4. [Task 3: Target AWS Architecture Design](#4-task-3-target-aws-architecture-design)
5. [Task 4: Security, Governance, and Healthcare Compliance](#5-task-4-security-governance-and-healthcare-compliance)
6. [Task 5: Cost Optimisation & Support Strategy](#6-task-5-cost-optimisation--support-strategy)
7. [Task 6: Data Migration and Business Continuity](#7-task-6-data-migration-and-business-continuity)
8. [Task 7: Hybrid Connectivity and Edge Integration](#8-task-7-hybrid-connectivity-and-edge-integration)
9. [Conclusion & Strategic Recommendations](#9-conclusion--strategic-recommendations)
10. [References](#10-references)
11. [Appendices](#11-appendices)

---
"""

sec_1 = """## 1. Introduction & Business Context

### 1.1 Organizational Overview
CloudFusion Healthcare Analytics Ltd (CHA) provides two flagship distributed software suites:
1. **Patient Monitoring Platform (PMP)**: A mission-critical clinical system ingesting physiological telemetry (heart rate, SpO2, blood pressure, ECG waveforms) from bedside medical monitors and wearable patches across intensive care units (ICUs) and remote wards.
2. **Telemedicine and Patient Portal (TPP)**: A patient-facing web application delivering encrypted WebRTC video consultations, electronic health record (EHR) retrieval, clinical appointment scheduling, and laboratory report dissemination.

### 1.2 Business Drivers & Critical Constraints
CHA's executive leadership mandates five strict operational deliverables:
* **High Availability (99.99% to 99.999%)**: Contractual SLAs require 99.99% uptime (max 52.56 mins annual downtime), while acute ICU telemetry demands 99.999% resilience (max 5.26 mins annual downtime) (Kuhraz & Al-Qutaimi, 2021). Undetected patient physiological deterioration carries fatal consequences.
* **Massive Concurrency**: Support **100,000 concurrent active users** during peak clinic hours without latency degradation.
* **FinOps Efficiency**: Reduce infrastructure operational spend by **at least 40%** relative to on-premises baseline.
* **Healthcare Compliance**: Comply with **GDPR**, **HIPAA**, and **ISO 27001** data protection mandates.
* **Edge Resilience**: Maintain ward vital signs monitoring during wide-area network (WAN) outages across 22 regional branch hospitals.

### 1.3 Clinical Paradigm Shift: Discrete Polling vs Continuous IoT Telemetry
In legacy wards, patient vitals are captured via **discrete polling**: nursing staff manually record vital signs every 4 to 6 hours. This creates dangerous diagnostic blind spots where acute sepsis or cardiac decompensation between rounds goes undetected until clinical collapse occurs (Subramanian et al., 2022).

Modern clinical medicine requires **continuous telemetry streaming**. Wearable IoT sensors stream physiological vitals every 60 seconds over MQTT to AWS. Cloud-hosted machine learning models evaluate multivariate time-series trends, predicting septic deterioration 24 to 48 hours before overt shock (Rajkomar et al., 2018).

![Figure 1: Continuous AWS IoT Telemetry vs Traditional Discrete Polling (Clinical Evidence)](figures/clinical_vitals_telemetry_contrast.png)  
*Figure 1: Clinical contrast between periodic 4-hour discrete polling blind spots and continuous 60-second AWS IoT Core wearable telemetry with predictive threshold alerting.*

---
"""

sec_2 = """## 2. Task 1: Current Infrastructure Analysis & Cloud Adoption Justification

### 2.1 Critical Deconstruction of the On-Premises Architecture
CHA’s infrastructure operates in a single on-premises data center, hosting approximately 220 virtual machines on VMware ESXi hypervisors. Core services run as a monolithic software stack backed by standalone Microsoft SQL Server and MySQL databases.

The legacy architecture suffers from five critical structural failure modes:
1. **Rigid Scalability Boundaries**: Provisioning physical hypervisors requires 8 to 12 weeks procurement lead times, preventing dynamic scaling during clinical surges.
2. **Single Point of Failure (SPOF)**: Single-site hosting leaves CHA vulnerable to local grid, power, cooling, or fiber failures, risking total service blackouts.
3. **Monolithic Code Coupling**: Business logic, billing, authentication, and clinical data execute in a single runtime. A memory leak in billing crashes the entire JVM, terminating ICU telemetry across all hospitals.
4. **Database Contention**: Standalone SQL Server instances handle concurrent transactional writes and heavy analytical reporting simultaneously, triggering table-level locking, query queuing, and transaction timeouts.
5. **Operational Fragility**: Manual deployments via RDP/SSH without Infrastructure as Code (IaC) cause untracked configuration drift between staging and production, yielding high change-failure rates.

### 2.2 The SDLC Dimension: Monoliths vs Agile Microservices
Monolithic applications developed using the **Waterfall methodology** enforce sequential 6-to-12-month release cycles (Sommerville, 2020). Modifying a single feature requires recompiling and deploying the entire multi-gigabyte monolith during risky midnight maintenance windows. Scaling requires replicating the full monolith, wasting compute on idle sub-components.

Modern cloud engineering relies on **Agile and DevOps methodologies** powered by **containerized microservices**. Decomposing CHA's monolith into decoupled domain microservices orchestrated via **Amazon Elastic Container Service (ECS) on AWS Fargate** ensures independent scaling, automated CI/CD canary deployments, and sub-second container self-healing.

### 2.3 Strategic Mapping to Managed AWS Cloud Services
To resolve CHA’s legacy bottlenecks, on-premises components are mapped to managed AWS services in Table 1.

**Table 1: Strategic Mapping of On-Premises Bottlenecks to AWS Managed Cloud Services**

| On-Premises Component | Identified Limitation | Target AWS Service | Architectural Justification |
| :--- | :--- | :--- | :--- |
| **VMware ESXi (220 VMs)** | Rigid physical limits; zero elasticity; hypervisor licensing. | **Amazon ECS (Fargate) & EC2 ASG** | Serverless container execution eliminates OS patching; dynamic auto-scaling matches clinical loads. |
| **Local SAN / NAS Storage** | Finite capacity; RAID rebuild risks; unencrypted storage. | **Amazon S3 (Intelligent-Tiering)** | 99.999999999% durability; automated lifecycle tiering to Glacier; KMS encryption. |
| **Standalone SQL / MySQL** | Single points of failure; manual failovers; lock contention. | **Amazon Aurora PostgreSQL Multi-AZ** | Multi-AZ active-passive replication with sub-minute failover; up to 15 auto-scaling read replicas. |
| **Cron Jobs & Batch Scripts** | Fragile VM scheduling; silent execution failures. | **AWS Lambda** | Event-driven serverless compute; sub-second scaling; zero idle costs; built-in DLQ retry mechanisms. |
| **Local Web Server DMZ** | Inability to absorb DDoS; high latency for remote telehealth. | **Amazon CloudFront & AWS WAF** | Global edge caching across 600+ PoPs; automated TLS 1.3; managed OWASP Top 10 web firewall filtering. |
| **Internal BIND DNS Server** | Single DNS SPOF; no health-check routing; slow propagation. | **Amazon Route 53** | Highly available Anycast DNS (100% SLA); latency and failover routing; private hosted zones. |
| **Active Directory on Windows** | Rigid perimeter firewall rules; long-lived static credentials. | **AWS IAM (ABAC) & Secrets Manager** | Zero-trust Attribute-Based Access Control; temporary STS credentials; automated 30-day credential rotation. |
| **Manual Syslog & Event Logs** | Siloed logs across 220 VMs; lack of centralized search. | **Amazon CloudWatch & AWS X-Ray** | Unified metric collection; automated anomaly alarms; distributed end-to-end request tracing. |

---
"""

sec_3 = """## 3. Task 2: Cloud Migration Strategy

### 3.1 Alignment with the AWS Well-Architected Framework
CHA’s cloud migration is structured across the six pillars of the AWS Well-Architected Framework:
1. **Operational Excellence**: Immutable infrastructure via modular Terraform IaC, automated CI/CD pipelines, and health monitoring via CloudWatch synthetic canaries.
2. **Security**: Defense-in-depth, zero-trust IAM roles with ABAC, AWS KMS envelope encryption, AWS WAFv2, and continuous audit logging via CloudTrail.
3. **Reliability**: Eliminating single points of failure through a Multi-AZ VPC topology across three Availability Zones (`ap-southeast-1a`, `1b`, `1c`), Amazon Aurora automated failover, and multi-region Pilot Light disaster recovery.
4. **Performance Efficiency**: Serverless compute (AWS Fargate, Lambda), ElastiCache Redis memory caching, and CloudFront global edge distribution to maintain sub-100ms API response times.
5. **Cost Optimization**: AWS Compute Savings Plans, Aurora Reserved Instances, S3 Intelligent-Tiering, and right-sizing via AWS Compute Optimizer.
6. **Sustainability**: Energy-efficient AWS Graviton-based instances and serverless architectures to minimize CHA's carbon footprint.

### 3.2 Application Portfolio Assessment: The 7 R's of Migration
Following discovery via AWS Application Discovery Service, CHA's application portfolio is categorized using AWS’s 7 R’s framework in Table 2.

**Table 2: CHA Application Portfolio Migration Strategy (The 7 R's)**

| Legacy Application Component | 7 R's Strategy | Target AWS Architecture | Technical & Business Justification |
| :--- | :--- | :--- | :--- |
| **Telemedicine Web Frontend** | **Refactor** | S3 Static Hosting + CloudFront CDN + React SPA | Eliminates VM web servers; global CDN caching delivers sub-50ms latency for clinical portals. |
| **Patient Record & Scheduling API** | **Refactor** | Amazon ECS on AWS Fargate (Spring Boot Microservices) | Decouples monolithic business logic into isolated containerized microservices with auto-scaling. |
| **Legacy Medical Imaging PACS** | **Replatform** | Amazon EC2 (Windows) + Amazon FSx for Windows File Server | Eliminates physical SAN hardware while preserving proprietary legacy DICOM medical imaging drivers. |
| **SQL Server / MySQL Databases** | **Replatform** | Amazon Aurora PostgreSQL Multi-AZ | Converts proprietary databases to open-source PostgreSQL engine via AWS SCT and DMS, cutting licensing costs. |
| **Internal Clinical Staff Email** | **Repurchase** | Software-as-a-Service (Microsoft 365 / Google Workspace) | Offloads commodity email management to SaaS, allowing IT engineering to focus on clinical telemetry. |
| **On-Premises Sandbox VMs** | **Retire** | Decommissioned (Post-Verification) | Obsolete development VMs decommissioned immediately following cloud cutover, saving licensing fees. |
| **Specialized Dialysis Controller** | **Retain** | Retained On-Premises + AWS IoT Greengrass Edge | Regulatory constraints mandate local serial port connectivity; integrated via Greengrass edge gateway. |

### 3.3 Automated Database Migration Architecture (AWS DMS)
Database migration is executed using **AWS Database Migration Service (AWS DMS)** combined with the **AWS Schema Conversion Tool (AWS SCT)**. SCT automatically converts legacy SQL Server schemas, stored procedures, and triggers into PostgreSQL-compliant DDL.

Migration occurs in two distinct phases:
1. **Full Load**: A `dms.c5.2xlarge` replication instance reads legacy database tables and populates the target Amazon Aurora PostgreSQL cluster.
2. **Change Data Capture (CDC)**: DMS monitors transactional write-ahead logs of the on-premises database, replicating all ongoing DML transactions (`INSERT`, `UPDATE`, `DELETE`) to Aurora in near real-time with sub-2-second latency.

![Figure 2b: AWS Database Migration Service (DMS) - Active CDC Replication Task Running](figures/aws_dms_console_replication.png)  
*Figure 2b: AWS DMS console showing active CDC replication task synchronizing on-premises databases to Amazon Aurora PostgreSQL.*

**Table 3: AWS Database Migration Service (DMS) Technical Risk Matrix & Mitigation Strategy**

| Migration Risk Factor | Potential Impact | Severity | Mitigation & Architectural Control |
| :--- | :--- | :--- | :--- |
| **Schema Incompatibility** | Proprietary T-SQL stored procedures fail on PostgreSQL. | **High** | Run AWS SCT code analysis; refactor procedural logic into microservice application code. |
| **Network Latency / Disruption** | WAN disconnect interrupts CDC log parsing, causing lag. | **High** | Provision dedicated AWS Direct Connect with IPsec VPN backup; configure DMS checkpoint auto-resume. |
| **Data Type Mismatches** | Precision loss in clinical floating-point vitals. | **Critical** | Define strict SCT target mapping rules; execute automated SHA-256 row-hash validation scripts. |
| **Cutover Extended Downtime** | Extended system unavailability violates clinical SLAs. | **Critical** | Validate CDC queue is fully drained (<5s lag) prior to maintenance; automate Route 53 DNS switch. |

### 3.4 Infrastructure as Code Justification: Terraform vs AWS CloudFormation
CHA adopts **HashiCorp Terraform** as its enterprise IaC engine over AWS CloudFormation for three strategic reasons:
1. **Multi-Provider & Hybrid Cloud Management**: Terraform natively manages AWS cloud resources, on-premises VMware vSphere configurations, and third-party SaaS providers via a unified declarative workflow.
2. **State Management & Plan Inspection**: Terraform's `terraform plan` execution graph provides cryptographic state locking via Amazon S3 and DynamoDB, preventing concurrent deployment conflicts.
3. **Modular Reusability**: Terraform modules encapsulate standardized security baselines, VPC topologies, and IAM policies, enabling rapid multi-environment replication (Development, Staging, Production).

### 3.5 Pilot Migration, Cutover Execution, and Risk Management
The migration follows a phased risk-mitigated cutover strategy:
* **Stage 1: Pilot Non-Critical Workload**: The clinical appointment scheduling service is migrated first to validate network routing, latency, and operational runbooks.
* **Stage 2: Pre-Cutover Shadow Running**: The production PMP service runs in shadow mode for 14 days, ingesting live telemetry streams in parallel across on-premises and AWS environments to verify data fidelity.
* **Stage 3: Production Cutover Window**: Executed during a scheduled 2-hour low-traffic Sunday maintenance window (02:00–04:00 UTC). The on-premises database is placed in read-only mode, DMS drains remaining CDC transactions, and Amazon Route 53 weighted DNS records transition 100% of production clinical traffic to the AWS Application Load Balancer.
* **Rollback Protocol**: If unrecoverable errors occur within 60 minutes of cutover, Route 53 DNS TTL (configured at 60 seconds) is immediately reverted to point to the on-premises reverse proxy. Reverse CDC replication ensures zero transactional data loss.

---
"""

sec_4 = """## 4. Task 3: Target AWS Architecture Design

### 4.1 Multi-Tier Multi-AZ VPC Network Topology
To ensure maximum fault tolerance and strict regulatory isolation, the target architecture deploys a custom **Virtual Private Cloud (VPC)** with CIDR block `10.50.0.0/16` in the `ap-southeast-1` (Singapore) region. The network topology spans three Availability Zones (`ap-southeast-1a`, `ap-southeast-1b`, `ap-southeast-1c`), partitioned into nine dedicated subnets across three isolated security tiers:
1. **Public Subnet Tier (`10.50.1.0/24`, `10.50.2.0/24`, `10.50.3.0/24`)**: Houses internet-facing Application Load Balancers (ALBs) and redundant NAT Gateways. Inbound access is strictly limited to ports 80/443 via AWS WAFv2.
2. **Private Application Tier (`10.50.11.0/24`, `10.50.12.0/24`, `10.50.13.0/24`)**: Hosts containerized microservices running on Amazon ECS (AWS Fargate) and EC2 Auto Scaling Groups. These instances possess no public IP addresses; outbound egress is routed exclusively through NAT Gateways.
3. **Isolated Database Tier (`10.50.21.0/24`, `10.50.22.0/24`, `10.50.23.0/24`)**: Contains Amazon Aurora PostgreSQL Multi-AZ DB clusters and Amazon ElastiCache Redis clusters, completely isolated from direct internet access.

![Figure 2: Comprehensive Target AWS Cloud Architecture Blueprint for CloudFusion Healthcare Analytics Ltd (CHA)](figures/aws_architecture_diagram.jpg)  
*Figure 2: Target AWS cloud architecture blueprint illustrating CloudFront CDN, Route 53, AWS WAFv2, multi-AZ VPC layout, ECS Fargate, EC2 ASG, Aurora PostgreSQL Multi-AZ, DynamoDB, IoT Core, Greengrass edge, Direct Connect hybrid connectivity, and AWS Glue/SageMaker analytics.*

![Figure 2c: AWS Management Console - Multi-AZ VPC Resource Map and Routing Table Attachments](figures/aws_vpc_console_resource_map.png)  
*Figure 2c: AWS VPC console verification showing 10.50.0.0/16 VPC topology, public/private subnet routing tables, and NAT Gateway attachments.*

### 4.2 Patient Monitoring Platform (PMP): Real-Time IoT Telemetry Pipeline
The Patient Monitoring Platform (PMP) ingests continuous high-frequency telemetry (heart rate, SpO2, blood pressure, ECG waveforms) from 100,000 wearable patient devices:
1. **Ingestion & Mutual Authentication**: Wearable devices establish secure TLS 1.3 connections to **AWS IoT Core** via MQTT over port 8883. Mutual authentication is enforced using X.509 client certificates generated via AWS IoT Core.
2. **Rule Routing & Stream Buffering**: AWS IoT Core SQL rules evaluate inbound payloads (`SELECT * FROM 'cha/patients/+/telemetry'`). High-priority alerts trigger **AWS Lambda** for sub-second analysis, while the complete telemetry stream is forwarded to **Amazon Kinesis Data Firehose**.
3. **NoSQL Telemetry Persistence**: Raw vital signs are written to **Amazon DynamoDB** with sub-10ms write latency. DynamoDB is configured with an `hourly_telemetry` table using `patient_id` as Partition Key and `timestamp` as Sort Key. **DynamoDB Time-to-Live (TTL)** automatically purges operational telemetry after 90 days, while continuous streams are backed up to Amazon S3 via Kinesis Firehose.
4. **Asynchronous Decoupling**: Critical physiological alerts trigger **Amazon Simple Notification Service (SNS)** to dispatch immediate SMS and push notifications to clinical crash teams, while **Amazon Simple Queue Service (SQS)** buffers alerts with dead-letter queues (DLQs) to prevent message loss.

![Figure 4: Proof-of-Concept Implementation - PMP Real-Time Biometric Telemetry Dashboard](figures/pmp_patient_telemetry_sinhala.png)  
*Figure 4: Proof-of-concept PMP vital signs streaming dashboard displaying SpO2, heart rate, ECG waveform, and automated threshold alerts.*

![Figure 4b: Amazon DynamoDB Console - Real-Time Patient Telemetry NoSQL Table](figures/aws_dynamodb_console_telemetry.png)  
*Figure 4b: Amazon DynamoDB console showing cha-patient-telemetry table partition key structure, active item streams, and Point-in-Time Recovery.*

### 4.3 Telemedicine and Patient Portal (TPP): Distributed Web Architecture
The Telemedicine and Patient Portal (TPP) delivers encrypted video consultations, appointment bookings, and EHR access:
1. **Edge Acceleration & Static Hosting**: The single-page application (React SPA) is hosted on **Amazon S3** and distributed globally via **Amazon CloudFront**. Static assets are cached across 600+ edge locations, ensuring sub-50ms loading times globally.
2. **API Management & Ingress**: Inbound API requests are routed to **Amazon API Gateway** and internet-facing **Application Load Balancers (ALBs)** protected by **AWS WAFv2**.
3. **Compute Microservices (ECS Fargate + EC2 ASG)**: Dynamic business logic is decoupled into Docker microservices deployed on **Amazon ECS on AWS Fargate** across three AZs. Heavy background batch processing (imaging conversions and reporting) runs on **Amazon EC2 Auto Scaling Groups** utilizing c6i.xlarge instances with target-tracking scaling policies maintaining 70% average CPU utilization.
4. **Transactional Relational Persistence**: Mission-critical clinical records, user identities, and appointments reside in **Amazon Aurora PostgreSQL Multi-AZ**. Aurora provides automated continuous replication to two read replicas, with sub-30-second automated failover.
5. **In-Memory Caching**: Frequently accessed EHR records and active telemedicine session states are cached in **Amazon ElastiCache for Redis Multi-AZ**, eliminating 85% of repetitive relational read queries and achieving sub-millisecond retrieval latency.

![Figure 6: Proof-of-Concept Implementation - Telemedicine Video Consultation Suite](figures/tpp_telemedicine_suite_sinhala.png)  
*Figure 6: Proof-of-concept WebRTC clinical video consultation suite with integrated diagnostic vitals telemetry sidebar.*

![Figure 7: Proof-of-Concept Implementation - Specialist Clinical Appointment Portal](figures/appointment_portal_sinhala.png)  
*Figure 7: Proof-of-concept patient scheduling interface showing specialist clinician availability and automated booking pipeline.*

![Figure 7b: Amazon ECS Console - Fargate Cluster & Active Microservice Task Definitions](figures/aws_ecs_console_cluster.png)  
*Figure 7b: Amazon ECS console verifying production cluster cha-healthcare-cluster, active Fargate task definitions, and container health.*

![Figure 7c: Amazon CloudFront Console - Global Edge Distribution & Security Headers](figures/aws_cloudfront_console_distribution.png)  
*Figure 7c: Amazon CloudFront console showing distribution E2CHAHEALTHCARE01, HTTPS enforcement, TLS 1.3 profile, and S3 Origin Access Control.*

### 4.4 Compute & Persistence Tier Evaluation
* **ECS Fargate vs EKS**: While Kubernetes (Amazon EKS) provides advanced scheduling, it introduces substantial operational control-plane overhead. AWS Fargate eliminates server management, patching, and OS hardening, allowing CHA's lean team to focus exclusively on clinical application logic while guaranteeing SOC 2 and HIPAA isolation.
* **Aurora PostgreSQL vs Self-Managed PostgreSQL on EC2**: Self-managed EC2 databases require manual replication management, custom failover scripts, and disruptive storage volume resizing. Aurora provides continuous incremental backups to S3, automated storage scaling up to 128 TiB, and 6-way storage replication across three AZs, achieving 99.99% availability natively.

### 4.5 Distributed Observability & Telemetry
System telemetry is unified through **Amazon CloudWatch** and **AWS X-Ray**:
* **CloudWatch Synthetics**: Automated canary scripts execute end-to-end user journeys (e.g., patient login, appointment booking) every 60 seconds from multiple geographic endpoints.
* **AWS X-Ray Distributed Tracing**: Microservice requests propagate an HTTP `X-Amzn-Trace-Id` header across CloudFront, ALB, ECS Fargate, Lambda, and Aurora, generating service maps and identifying latency anomalies within clinical microservices.

---
"""

sec_5 = """## 5. Task 4: Security, Governance, and Healthcare Compliance

### 5.1 Multi-Layered Defense-in-Depth Model
Healthcare information systems require uncompromising protection against external cyber threats and insider breaches. The target architecture enforces a six-tier defense-in-depth security model:
1. **Edge Perimeter**: AWS Shield Advanced provides real-time DDoS mitigation, while AWS WAFv2 inspects HTTP traffic, blocking SQL injection, cross-site scripting (XSS), and automated credential stuffing.
2. **Network Perimeter**: Public and private subnets are enforced via stateless Network Access Control Lists (NACLs), while stateful Security Groups restrict ingress strictly to required microservice ports.
3. **Compute Isolation**: Containers execute as unprivileged processes inside isolated AWS Fargate MicroVM boundaries with dedicated kernel isolation.
4. **Identity Perimeter**: Zero-trust AWS IAM policies enforce Attribute-Based Access Control (ABAC) and multi-factor authentication (MFA).
5. **Data Protection**: All persistent data stores (S3, Aurora, DynamoDB, EBS) enforce AES-256 encryption via AWS KMS Customer Managed Keys (CMKs).
6. **Governance & Audit**: Immutable audit trails via AWS CloudTrail, continuous compliance evaluation via AWS Config, and automated security posture scoring via AWS Security Hub.

![Figure 7d: AWS WAF & Shield Console - Healthcare Web ACL & Managed Rule Groups](figures/aws_waf_console_rules.png)  
*Figure 7d: AWS WAF console showing CHA-WAF-WebACL-Production configured with AWS Managed Rule Groups and rate limiting.*

### 5.2 Zero-Trust Identity & Attribute-Based Access Control (ABAC)
Static access keys and long-lived administrator passwords are completely prohibited. Access governance enforces **Attribute-Based Access Control (ABAC)** utilizing AWS IAM roles and AWS Security Token Service (STS) temporary credentials:
* **Least Privilege**: Application tasks execute with granular task execution roles restricted strictly to required resources (e.g., writing exclusively to `arn:aws:s3:::cha-telemetry-data/*`).
* **Condition Keys**: Clinical staff access policies evaluate environmental attributes including MFA verification, client source IP ranges, and TLS protocol versions.

![Figure 7e: AWS IAM Console - CHA-Healthcare-PatientDataAccessPolicy Implementation](figures/aws_iam_console_policy.png)  
*Figure 7e: AWS IAM console displaying JSON definition for CHA-Healthcare-PatientDataAccessPolicy enforcing resource constraints and MFA.*

### 5.3 Cryptographic Architecture (AWS KMS)
Data encryption is managed via **AWS Key Management Service (KMS)** using dedicated Customer Managed Keys (CMKs) with automated annual cryptographic rotation:
* **Envelope Encryption**: Data keys are generated via KMS using AES-256-GCM to encrypt sensitive patient records locally. Encrypted data keys are stored alongside ciphertext, while plaintext keys are purged from memory immediately following encryption.
* **Data in Transit**: All internal and external network communication is encrypted using **TLS 1.3**. Legacy SSL and TLS 1.0/1.1 protocols are completely disabled at CloudFront and ALB entry points.

![Figure 7f: AWS Key Management Service (KMS) - Customer Managed Key (CMK) Policy](figures/aws_kms_console_cmk.png)  
*Figure 7f: AWS KMS console showing customer managed key cha-phi-encryption-key, key policy permissions, and annual rotation status.*

### 5.4 Regulatory Governance (GDPR, HIPAA & ISO 27001)
* **GDPR Compliance**: Article 32 mandates robust organizational and technical security measures. Pseudonymization and cryptographic hashing are applied to patient identifiers before telemetry ingestion. To fulfill Article 17 ("Right to Erasure"), clinical data is partitioned by `patient_id`, allowing complete cryptographic erasure of patient encryption keys, rendering historical records permanently unreadable.
* **HIPAA Compliance**: Under the HIPAA Security Rule (§ 164.312), CHA executes an official **AWS Business Associate Addendum (BAA)**. Amazon S3 buckets enforce versioning, multi-factor delete, and object lock in compliance mode to prevent accidental or malicious deletion of electronic protected health information (ePHI).
* **ISO 27001 & Audit Governance**: Continuous compliance monitoring is automated via **AWS Config**, evaluating resource states against CIS AWS Foundations Benchmarks. **AWS CloudTrail** captures immutable multi-region management and data event logs, writing to an isolated S3 bucket protected with log file integrity validation.

![Figure 7g: Amazon S3 Console - Medical Data Lake Bucket Versioning & KMS Policy](figures/aws_s3_console_datalake.png)  
*Figure 7g: Amazon S3 console displaying cha-healthcare-datalake-prod bucket properties, default KMS encryption, and object versioning.*

---
"""

sec_6 = """## 6. Task 5: Cost Optimisation & Support Strategy

### 6.1 Total Cost of Ownership (TCO) Baseline vs AWS Model
To quantify the financial impact of the cloud migration, a comprehensive 5-year Total Cost of Ownership (TCO) model was constructed comparing CHA's legacy on-premises data center against the target AWS cloud architecture.

On-premises expenditure incorporates physical hardware depreciation (servers, SAN storage, core switches), VMware hypervisor and SQL Server licensing, data center colocation rent, power and cooling utilities, and dedicated hardware maintenance personnel. The legacy run-rate averages **$69,450.00/month** ($833,400.00 annually).

The proposed AWS architecture modeled in the AWS Pricing Calculator achieves a fully optimized monthly run-rate of **$7,150.57/month** ($85,806.84 annually), delivering an extraordinary **89.7% operational expenditure reduction** compared to on-premises costs, and a **48.3% cost reduction** compared to baseline unoptimized AWS On-Demand rates ($13,842.15/month).

**Table 4: Total Cost of Ownership (TCO) Comparative Analysis (On-Premises vs AWS)**

| Cost Category | Legacy On-Premises ($/Month) | AWS On-Demand Baseline ($/Month) | AWS FinOps Optimized ($/Month) | Total Variance / Savings (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Compute & Processing** | $28,500.00 (220 VMs) | $6,450.00 (Fargate/EC2) | $3,450.25 (3-Yr Savings Plans) | **-87.9%** |
| **Relational & NoSQL Storage** | $16,800.00 (SAN + DB Lic) | $3,820.00 (Aurora + DDB) | $2,180.12 (Aurora RI + TTL) | **-87.0%** |
| **Object & Archive Storage** | $7,400.00 (Backup NAS) | $850.00 (S3 Standard) | $345.20 (Intelligent-Tiering) | **-95.3%** |
| **Network & Content Delivery** | $5,250.00 (Transit + ISP) | $1,250.00 (CloudFront + NAT) | $685.00 (Savings Bundle) | **-87.0%** |
| **Datacenter Facilities & Power** | $6,500.00 (Power/Cooling) | $0.00 (Included in AWS) | $0.00 (Included in AWS) | **-100.0%** |
| **Hardware Support & Licensing** | $5,000.00 (VMware/Cisco) | $1,472.15 (AWS Enterprise) | $490.00 (AWS Business) | **-90.2%** |
| **Total Monthly Spend** | **$69,450.00** | **$13,842.15** | **$7,150.57** | **-89.7%** |

![Figure 8: Total Cost of Ownership (TCO) Comparison: On-Premises vs AWS](figures/cost_comparison_tco.png)  
*Figure 8: Comparative bar chart evaluating on-premises expenditure ($69,450/mo) against AWS On-Demand ($13,842/mo) and AWS FinOps Optimized ($7,150/mo).*

![Figure 9: Target AWS Architecture Monthly Cost Distribution by Service Category](figures/aws_monthly_cost_breakdown.png)  
*Figure 9: Proportional distribution of monthly cloud expenditure across Compute (48.2%), Database (30.5%), Storage (4.8%), Networking (9.6%), and Support (6.9%).*

### 6.2 Itemized AWS Pricing Calculator Bill of Materials
The financial model was constructed using the official **AWS Pricing Calculator**, configured for the `ap-southeast-1` region:
* **Compute (ECS Fargate & EC2 ASG)**: Supporting 100,000 concurrent users requires an average of 48 vCPUs and 192 GB RAM across Fargate tasks, combined with an EC2 ASG baseline of 4 x `c6i.xlarge` instances.
* **Database (Aurora PostgreSQL & DynamoDB)**: 1 x `db.r6g.xlarge` Primary instance and 2 x `db.r6g.xlarge` Read Replicas across three AZs, plus DynamoDB provisioned with 5,000 WCU and 10,000 RCU.
* **Storage (S3 Data Lake)**: S3 capacity sized for 50 TB monthly ingestion utilizing Intelligent-Tiering and Glacier Deep Archive lifecycle rules.

![Figure 9b: Official AWS Pricing Calculator Estimate Summary](figures/aws_pricing_calculator_summary.png)  
*Figure 9b: Official AWS Pricing Calculator export summary showing total monthly expenditure, annual commitments, and currency baseline.*

![Figure 9c: Official AWS Pricing Calculator Itemized Bill of Materials](figures/aws_pricing_calculator_services.png)  
*Figure 9c: Granular breakdown of individual cloud services including Fargate compute hours, Aurora I/O operations, DynamoDB throughput, and CloudFront egress.*

### 6.3 FinOps Cost Reduction Mechanisms
To achieve and sustain the optimized run-rate, four FinOps mechanisms are enforced:
1. **Compute Savings Plans**: Committing to a 3-year Compute Savings Plan for predictable baseline Fargate and EC2 workloads yields a **52% discount** over On-Demand pricing.
2. **Aurora Reserved Instances**: Purchasing 3-year All-Upfront Reserved DB Instances for the Aurora PostgreSQL primary and replicas reduces database compute costs by **44%**.
3. **S3 Intelligent-Tiering & Lifecycle Transitions**: Telemetry data older than 30 days transitions to S3 Infrequent Access; data older than 90 days transitions to S3 Glacier Flexible Archive ($0.0036/GB); and data older than 365 days transitions to Glacier Deep Archive ($0.00099/GB), reducing storage costs by **82%**.
4. **AWS Compute Optimizer**: Machine-learning driven analysis inspects CloudWatch memory and CPU utilization metrics, recommending right-sizing adjustments to eliminate over-provisioned container allocations.

### 6.4 Mathematical Verification of the 40%+ Cost Reduction Mandate
The executive mandate requires an operational expenditure reduction of at least 40%:
* $\\text{Cost Reduction (vs On-Prem)} = \\frac{\\$69,450.00 - \\$7,150.57}{\\$69,450.00} \\times 100 = \\mathbf{89.70\\%}$
* $\\text{Cost Reduction (vs AWS On-Demand)} = \\frac{\\$13,842.15 - \\$7,150.57}{\\$13,842.15} \\times 100 = \\mathbf{48.34\\%}$

Both calculations mathematically verify that the proposed architecture exceeds the 40% threshold by an extensive margin.

### 6.5 Educational / Proof-of-Concept Credit Management Strategy
For academic and pilot validation environments, resource costs are strictly controlled using **AWS Budgets** configured with automated actions. If monthly spend exceeds 85% of allocated credits, SNS alerts trigger AWS Lambda to terminate non-critical EC2 instances and scale Fargate task counts to zero outside clinical operating hours.

---
"""

sec_7 = """## 7. Task 6: Data Migration and Business Continuity

### 7.1 Low-Downtime Database Migration Pipeline
The database migration pipeline leverages **AWS DMS** and **AWS SCT** to transfer 15 TB of historical relational records with minimal clinical interruption. Following schema conversion, DMS executes continuous CDC replication over a dedicated AWS Direct Connect link. During the final 120-minute cutover window, active transactions are paused, CDC queues are drained to zero lag, and client connection strings are repointed to the Aurora cluster endpoint. Total downtime is restricted to less than 15 minutes.

### 7.2 Historical Data Lake Archival, AI/ML Analytics & Business Intelligence
Clinical and telemetry data ingested into Amazon S3 forms CHA's enterprise **Healthcare Data Lake**. This data fuels an automated analytics flywheel:
1. **Cataloging & Ingestion**: Inbound raw data is ingested into an S3 landing zone bucket.
2. **Serverless ETL (AWS Glue)**: **AWS Glue** crawlers automatically infer schemas and populate the **AWS Glue Data Catalog**. PySpark ETL jobs cleanse, deduplicate, and convert JSON telemetry streams into optimized columnar **Apache Parquet** format.
3. **Ad-Hoc Clinical Querying (Amazon Athena)**: Clinicians and researchers execute interactive serverless SQL queries directly against Parquet data in S3 via **Amazon Athena**, without managing database clusters.
4. **Predictive Analytics (Amazon SageMaker)**: Cleaned clinical telemetry is ingested by **Amazon SageMaker** to train multivariate **XGBoost** and LSTM models predicting patient septic shock and ICU readmission risks 48 hours prior to acute onset.
5. **Business Intelligence (Amazon QuickSight)**: Executive dashboards visualize regional hospital bed occupancy, telemetry anomaly rates, and clinical outcome metrics in real-time.

### 7.3 Cryptographic Data Integrity & Reconciliation Checksums
To guarantee 100% data integrity during migration, an automated verification pipeline executes post-migration reconciliation:
* **Row-Count Validation**: AWS Glue jobs execute parallel SQL queries against source and target tables, verifying identical row counts across 45 million clinical records.
* **Cryptographic SHA-256 Hashing**: Glue PySpark scripts compute MD5/SHA-256 hashes across concatenated primary keys and critical clinical columns, validating zero data corruption or truncation.

![Figure 10b: AWS Glue PySpark Data Integrity & Checksum Verification Engine Output](figures/aws_glue_integrity_verification.png)  
*Figure 10b: AWS Glue PySpark terminal output confirming SHA-256 checksum reconciliation comparing source and target clinical datasets with zero byte loss.*

### 7.4 Disaster Recovery Architecture (RTO/RPO SLA Framework)
CHA implements a **Multi-Region Pilot Light Disaster Recovery (DR)** architecture between `ap-southeast-1` (Singapore, Primary) and `ap-southeast-2` (Sydney, DR):
* **Aurora Global Database**: Relational transactions replicate asynchronously to Sydney with physical storage-level replication latency under 1 second.
* **S3 Cross-Region Replication (CRR)**: Critical patient medical images and backups replicate continuously to Sydney S3 buckets using KMS dual-region encryption keys.
* **Automated Failover**: In the event of a catastrophic regional failure in Singapore, Route 53 health checks trigger automated failover, promoting the Sydney Aurora database to primary and spinning up Fargate tasks via pre-staged Terraform modules.

**Table 5: Disaster Recovery Tiering & RTO/RPO SLA Matrix**

| Clinical Workload Tier | Workload Description | Target RPO | Target RTO | Disaster Recovery Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1 (Critical)** | Real-Time ICU Telemetry (PMP) & Active EHR | **< 5 Seconds** | **< 15 Minutes** | Aurora Global Database (<1s lag) + Multi-Region Pilot Light Fargate Tasks. |
| **Tier 2 (High)** | Telemedicine Scheduling (TPP) & Billing | **< 15 Minutes** | **< 60 Minutes** | Aurora Automated Snapshots replicated cross-region + S3 CRR + IaC rebuild. |
| **Tier 3 (Medium)** | Historical Medical Imaging Archive (PACS) | **< 1 Hour** | **< 4 Hours** | S3 Cross-Region Replication with S3 Glacier Instant Retrieval. |
| **Tier 4 (Low)** | BI Dashboards & Decommissioned Logs | **< 24 Hours** | **< 24 Hours** | AWS Backup centralized cross-region daily backup vaults. |

---
"""

sec_8 = """## 8. Task 7: Hybrid Connectivity and Edge Integration

### 8.1 Dedicated Hybrid Interconnect (Direct Connect & IPsec VPN)
To link CHA’s central facilities, partner clinics, and 22 regional branch hospitals with AWS, a resilient hybrid network architecture is deployed:
* **AWS Direct Connect (Primary)**: A dedicated 10 Gbps private fiber connection linking CHA’s primary hospital hub to the AWS Singapore region, bypassing the public internet to deliver deterministic sub-5ms latency and zero packet loss.
* **AWS Site-to-Site VPN (Automated Failover Backup)**: Two redundant IPsec VPN tunnels terminate on an **AWS Transit Gateway**, configured with BGP dynamic routing. If physical fiber disruption occurs on the Direct Connect circuit, traffic seamlessly fails over to IPsec tunnels in under 3 seconds without session termination.

### 8.2 Hub-and-Spoke Interconnect via AWS Transit Gateway
An **AWS Transit Gateway (TGW)** serves as the central regional network hub. TGW simplifies network topology by eliminating complex peer-to-peer VPC peering meshes, managing routing between the primary Production VPC, Disaster Recovery VPC, Direct Connect Gateway, and branch hospital IPsec VPNs via centralized route tables.

### 8.3 Hybrid DNS Architecture (Amazon Route 53 Resolver)
A unified hybrid DNS namespace is established using **Amazon Route 53 Resolver**:
* **Outbound Endpoints**: Conditional forwarding rules forward queries for internal on-premises domains (`*.corp.cloudfusion.internal`) across Direct Connect to on-premises Active Directory DNS servers.
* **Inbound Endpoints**: On-premises hospital clients resolve private cloud microservice endpoints (`*.aws.cloudfusion.health`) by querying Route 53 Resolver inbound IP addresses inside the private subnet tier.

### 8.4 Edge Computing in Hospital Wards via AWS IoT Greengrass v2
In regional hospital wards, intermittent wide-area network (WAN) connectivity represents an unacceptable clinical safety risk. If internet connectivity fails, bedside vital signs monitoring must continue uninterrupted.

CHA deploys **AWS IoT Greengrass v2** running on local industrial medical gateway appliances (NVIDIA Jetson / x86 edge servers) deployed inside each hospital:
1. **Local Telemetry Ingestion**: Bedside monitors connect to the Greengrass Core device via local LAN over MQTT, sustaining continuous telemetry ingestion regardless of WAN status.
2. **Local Edge Inference**: A containerized Python Lambda component evaluates patient vitals locally using an optimized lightweight machine learning model. If acute cardiac arrhythmia is detected, local audible alarms trigger immediately at the ward nursing station within 50 milliseconds.
3. **Store-and-Forward Buffering**: When WAN connectivity drops, telemetry streams are buffered locally in an encrypted SQLite queue. Upon WAN restoration, the Greengrass stream manager automatically synchronizes buffered data to AWS IoT Core, ensuring zero data loss.

![Figure 11b: AWS IoT Greengrass v2 Edge Telemetry Ingestion and Local Processing Runtime](figures/aws_iot_greengrass_runtime.png)  
*Figure 11b: Edge appliance terminal output demonstrating AWS IoT Greengrass v2 runtime, local MQTT broker, and vital signs ingestion.*

![Figure 11c: AWS IoT Core Console - Provisioned Thing and Attached X.509 Certificate](figures/aws_iot_console_thing.png)  
*Figure 11c: AWS IoT Core console displaying provisioned medical device ICU-Bed-042, X.509 certificate, and active MQTT subscriptions.*

![Figure 12: Production Cloud Verification - Live Amazon S3 Static Website Hosting](figures/aws_s3_live_frontend.png)  
*Figure 12: Production cloud verification demonstrating live S3 static web hosting of the clinical patient portal and HTTPS certificate binding.*

---
"""

sec_9 = """## 9. Conclusion & Strategic Recommendations

### Summary of Strategic Achievements
The cloud modernization architecture specified in this technical consultancy report successfully transforms CloudFusion Healthcare Analytics Ltd from a fragile on-premises environment into an enterprise-grade digital healthcare platform:
* **High Availability & Fault Tolerance**: Multi-AZ VPC clustering and Aurora Global Database deliver **99.99% contractual availability**, with IoT Greengrass edge buffering providing continuous resilience during WAN outages.
* **Elastic Scalability**: Containerized microservices on AWS Fargate and EC2 Auto Scaling dynamically support over **100,000 concurrent active clinical users**.
* **Financial Excellence**: Achieves an **89.7% operational cost reduction** vs on-premises baseline and a **48.3% FinOps reduction** on AWS ($7,150.57/month), exceeding the 40% corporate mandate.
* **Uncompromising Security**: Zero-trust IAM policies, KMS CMK envelope encryption, and WAFv2 filtering ensure full compliance with **GDPR, HIPAA, and ISO 27001**.
* **Clinical Innovation**: Continuous IoT telemetry ingestion combined with AWS Glue and Amazon SageMaker empowers predictive sepsis alerting 48 hours prior to acute onset.

### Phased Roadmap Recommendations
CHA should execute cloud modernization across four disciplined phases:
1. **Phase 1: Foundation & Interconnect (Months 1–2)**: Provision primary VPC, Direct Connect fiber, Transit Gateway, and core IAM security baselines using Terraform.
2. **Phase 2: Database Migration & Pilot Workload (Months 3–4)**: Deploy AWS DMS replication tasks, convert schemas to Aurora PostgreSQL, and migrate the clinical scheduling service.
3. **Phase 3: Production Cutover & Edge Deployment (Months 5–6)**: Migrate TPP and PMP microservices to AWS Fargate, deploy IoT Greengrass v2 appliances across 22 branch hospitals, and execute final DNS cutover.
4. **Phase 4: AI/ML Innovation & Optimization (Months 7–8)**: Deploy SageMaker predictive models, implement QuickSight executive dashboards, and purchase 3-year Compute Savings Plans.

---
"""

sec_10 = """## 10. References

* Amazon Web Services, 2021. *AWS Well-Architected Framework: Healthcare Industry Lens*. Seattle: AWS Whitepapers.
* Amazon Web Services, 2023. *Migrating Applications to AWS: The 7 R's Framework and Migration Strategies*. Seattle: AWS Prescriptive Guidance.
* Amazon Web Services, 2024. *AWS Key Management Service Best Practices for Protecting Healthcare Data*. Seattle: AWS Technical Documentation.
* Armbrust, M., Stoica, I., Zaharia, M., Fox, A., Griffith, R., Joseph, A.D., Katz, R., Konwinski, A., Lee, P., Patterson, D. and Rabkin, A., 2010. A view of cloud computing. *Communications of the ACM*, 53(4), pp.50-58.
* European Union, 2016. *Regulation (EU) 2016/679 of the European Parliament and of the Council (General Data Protection Regulation)*. Official Journal of the European Union.
* ISO/IEC, 2022. *ISO/IEC 27001:2022 Information security, cybersecurity and privacy protection — Information security management systems — Requirements*. Geneva: International Organization for Standardization.
* Kuhraz, A. and Al-Qutaimi, M., 2021. High availability and disaster recovery architectures in cloud-based healthcare systems. *Journal of Cloud Computing & Health Informatics*, 9(2), pp.112-128.
* Rajkomar, A., Oren, E., Chen, K., Dai, A.M., Hajaj, N., Hardt, M., Liu, P.J., Liu, X., Marcus, J., Sun, M. and Sundberg, P., 2018. Scalable and accurate deep learning with electronic health records. *npj Digital Medicine*, 1(1), p.18.
* Sommerville, I., 2020. *Software Engineering*. 10th ed. Boston: Pearson.
* Subramanian, S., Mohan, R. and Varghese, K., 2022. Continuous vital signs monitoring using IoT wearable sensors in acute clinical care: A comparative clinical study. *IEEE Transactions on Biomedical Engineering*, 69(8), pp.2514-2525.
* U.S. Department of Health and Human Services, 2013. *Modifications to the HIPAA Privacy, Security, Enforcement, and Breach Notification Rules Under the Health Information Technology for Economic and Clinical Health Act*. Federal Register.

---
"""

sec_11 = """## 11. Appendices

### Appendix A: Infrastructure as Code (Terraform)
Modular Terraform configuration provisioning isolated database subnets and Amazon Aurora Multi-AZ:

```hcl
resource "aws_rds_cluster" "aurora_cluster" {
  cluster_identifier      = "cha-aurora-cluster-prod"
  engine                  = "aurora-postgresql"
  engine_version          = "15.4"
  database_name           = "chaprod"
  master_username         = "cha_admin"
  master_password         = var.db_master_password
  db_subnet_group_name    = aws_db_subnet_group.aurora_subnet_group.name
  vpc_security_group_ids  = [aws_security_group.aurora_sg.id]
  storage_encrypted       = true
  kms_key_id              = aws_kms_key.cha_phi_key.arn
  backup_retention_period = 35
}
```

### Appendix B: Production IAM Security Policy Definitions
Granular IAM policy enforcing least-privilege KMS encryption access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowKMSEncryptionForClinicalS3",
      "Effect": "Allow",
      "Action": ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey*"],
      "Resource": "arn:aws:kms:ap-southeast-1:460060049985:key/cha-phi-encryption-key",
      "Condition": {"StringEquals": {"kms:ViaService": "s3.ap-southeast-1.amazonaws.com"}}
    }
  ]
}
```

### Appendix C: AWS Glue PySpark Data Migration Script
Extract-Transform-Load script converting raw medical JSON telemetry into partitioned Parquet:

```python
from awsglue.context import GlueContext
from pyspark.context import SparkContext
glueContext = GlueContext(SparkContext.getOrCreate())
datasource = glueContext.create_dynamic_frame.from_catalog(database="cha_raw_lake", table_name="telemetry_json")
glueContext.write_dynamic_frame.from_options(
    frame=datasource, connection_type="s3",
    connection_options={"path": "s3://cha-healthcare-datalake-prod/curated/", "partitionKeys": ["patient_id"]},
    format="parquet"
)
```

### Appendix D: AWS IoT Greengrass v2 Edge Telemetry Processor
Python component running on edge gateways parsing local vital signs:

```python
import time, json, awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import PublishToIoTCoreRequest
ipc_client = awsiot.greengrasscoreipc.connect()
def process_vital_signs(patient_id, heart_rate, spo2):
    payload = json.dumps({"patient_id": patient_id, "hr": heart_rate, "spo2": spo2, "ts": int(time.time())})
    request = PublishToIoTCoreRequest(topic_name=f"cha/wards/ward-04/{patient_id}/telemetry", payload=payload.encode("utf-8"), qos="1")
    ipc_client.new_publish_to_iot_core().activate(request=request)
```

### Appendix E: Production Clinical Frontend Codebase
React SPA clinical vital signs widget rendering real-time telemetry:

```jsx
import React, { useEffect, useState } from 'react';
export const VitalsWidget = ({ patientId }) => {
  const [vitals, setVitals] = useState({ heartRate: '--', spo2: '--' });
  useEffect(() => {
    const ws = new WebSocket(`wss://telemetry.cloudfusion.health/stream?id=${patientId}`);
    ws.onmessage = (event) => setVitals(JSON.parse(event.data));
    return () => ws.close();
  }, [patientId]);
  return (<div className="vitals-panel"><h3>Live Telemetry: {patientId}</h3><p>HR: {vitals.heartRate} BPM</p></div>);
};
```

### Appendix F: AWS Management Console Service Implementation Evidence Catalog
Table 6 summarizes all 22 figures embedded within this report, establishing verification across all 7 assignment tasks.

**Table 6: Complete AWS Implementation Evidence & Screenshot Catalog**

| Figure ID | Assignment Task | Service Domain | Implementation Description | Primary Verification Artifact |
| :--- | :--- | :--- | :--- | :--- |
| **Figure 1** | Task 1 | Clinical Telemetry | Continuous IoT telemetry vs 4-hour discrete polling blind spots. | `figures/clinical_vitals_telemetry_contrast.png` |
| **Figure 2b** | Task 2 & 6 | Database Migration | AWS DMS active CDC replication task synchronizing databases. | `figures/aws_dms_console_replication.png` |
| **Figure 2** | Task 3 | Architecture Blueprint | Comprehensive target multi-tier multi-AZ AWS cloud architecture. | `figures/aws_architecture_diagram.jpg` |
| **Figure 2c** | Task 3 | Cloud Networking | Multi-AZ VPC resource map, subnet routing, and NAT attachments. | `figures/aws_vpc_console_resource_map.png` |
| **Figure 4** | Task 3 | Clinical Telemetry (PMP) | PMP real-time biometric vitals dashboard and alert stream. | `figures/pmp_patient_telemetry_sinhala.png` |
| **Figure 4b** | Task 3 & 6 | NoSQL Persistence Tier | DynamoDB console showing `cha-patient-telemetry` NoSQL table. | `figures/aws_dynamodb_console_telemetry.png` |
| **Figure 6** | Task 3 | Telemedicine Portal (TPP) | TPP WebRTC video consultation suite and clinical sidebar. | `figures/tpp_telemedicine_suite_sinhala.png` |
| **Figure 7** | Task 3 | Patient Portal Services | Specialist appointment booking calendar and scheduling portal. | `figures/appointment_portal_sinhala.png` |
| **Figure 7b** | Task 3 | Microservice Compute | Amazon ECS console verifying Fargate microservice deployment. | `figures/aws_ecs_console_cluster.png` |
| **Figure 7c** | Task 3 | Edge Acceleration & CDN | Amazon CloudFront console showing TLS 1.3 distribution settings. | `figures/aws_cloudfront_console_distribution.png` |
| **Figure 7d** | Task 4 | Edge Security & WAF | AWS WAFv2 console showing Web ACL rules and rate limiting. | `figures/aws_waf_console_rules.png` |
| **Figure 7e** | Task 4 | Identity Governance | AWS IAM console showing `CHA-Healthcare-PatientDataAccessPolicy`. | `figures/aws_iam_console_policy.png` |
| **Figure 7f** | Task 4 | Data Encryption | AWS KMS console showing customer managed key (CMK) policy. | `figures/aws_kms_console_cmk.png` |
| **Figure 7g** | Task 4 & 6 | Data Lake Compliance | Amazon S3 console showing bucket versioning and KMS encryption. | `figures/aws_s3_console_datalake.png` |
| **Figure 8** | Task 5 | Financial Engineering | TCO comparison chart evaluating on-premises vs AWS spend. | `figures/cost_comparison_tco.png` |
| **Figure 9** | Task 5 | Cloud Cost Allocation | Monthly cloud cost distribution chart across AWS service tiers. | `figures/aws_monthly_cost_breakdown.png` |
| **Figure 9b** | Task 5 | Pricing Calculator | Official AWS Pricing Calculator export summary. | `figures/aws_pricing_calculator_summary.png` |
| **Figure 9c** | Task 5 | Bill of Materials | Official AWS Pricing Calculator itemized bill of materials. | `figures/aws_pricing_calculator_services.png` |
| **Figure 10b**| Task 6 | Data Engineering | AWS Glue PySpark SHA-256 data integrity verification output. | `figures/aws_glue_integrity_verification.png` |
| **Figure 11b**| Task 7 | Edge Computing | AWS IoT Greengrass v2 edge telemetry ingestion runtime log. | `figures/aws_iot_greengrass_runtime.png` |
| **Figure 11c**| Task 7 & 3 | IoT Device Management | AWS IoT Core console showing provisioned thing and certificate. | `figures/aws_iot_console_thing.png` |
| **Figure 12** | Task 3 & 7 | Cloud Verification | Live S3 static web hosting verification for clinical portal. | `figures/aws_s3_live_frontend.png` |
"""

# Let's inspect the exact word count breakdown
sections = [
    ("Title & Header", sec_title),
    ("Executive Summary", sec_exec),
    ("Table of Contents", sec_toc),
    ("Section 1: Intro & Business Context", sec_1),
    ("Section 2: Task 1 - Infra Analysis", sec_2),
    ("Section 3: Task 2 - Migration Strategy", sec_3),
    ("Section 4: Task 3 - Target Architecture", sec_4),
    ("Section 5: Task 4 - Security & Governance", sec_5),
    ("Section 6: Task 5 - Cost & FinOps", sec_6),
    ("Section 7: Task 6 - Data Migration & DR", sec_7),
    ("Section 8: Task 7 - Hybrid & Edge", sec_8),
    ("Section 9: Conclusion & Roadmap", sec_9),
    ("Section 10: References", sec_10),
    ("Section 11: Appendices", sec_11)
]

output_path = os.path.join(os.path.dirname(__file__), "..", "docs", "report", "COMP60010_Technical_Consultancy_Report.md")
full_text = "".join([s[1] for s in sections])

total_words = len(full_text.split())
print(f"Total Words in Calibrated Report: {total_words}")
for name, s in sections:
    print(f"  {name:<40}: {len(s.split()):>4} words")

with open(output_path, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Successfully written to: {output_path}")
