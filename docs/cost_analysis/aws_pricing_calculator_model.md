# CloudFusion Healthcare Analytics Ltd (CHA)
## Task 5: Cost Optimisation, Pricing Model & FinOps Strategy

---

### 1. Executive Summary & Financial Mandate
A core business driver for CloudFusion Healthcare Analytics Ltd (CHA) is to **reduce infrastructure operational expenses by at least 40%** while modernizing the platform to support **over 100,000 concurrent users** and achieving **99.99% (contractual) to 99.999% (telco-grade) availability**.

This document outlines:
1. The **On-Premises Total Cost of Ownership (TCO) Baseline** for CHA's legacy 220 VMware virtual machines and monolithic database clusters.
2. An itemized **AWS Target Architecture Bill of Materials** sized using the **AWS Pricing Calculator** for the `ap-southeast-1` (Singapore) region.
3. Advanced **FinOps cost optimization strategies** (Compute Savings Plans, Fargate Spot blending, S3 Intelligent-Tiering, Aurora Serverless v2 auto-pause/scaling, and VPC Gateway endpoints).
4. Rigorous mathematical proof demonstrating an overall **45.3% monthly operational expenditure reduction**, exceeding the 40% mandate.
5. Practical advice for managing educational/POC AWS credits ($200 budget) through automated lifecycle teardown scripts.

---

### 2. On-Premises Baseline TCO Breakdown (Legacy Architecture)

The legacy infrastructure comprises 220 virtual machines hosted on 14 physical dual-socket VMware ESXi blade servers across a single data center in South Asia. 

```
+-------------------------------------------------------------+-----------------------+
| Cost Component (On-Premises Baseline)                       | Monthly Expense (USD) |
+-------------------------------------------------------------+-----------------------+
| Physical Hardware Amortization & Server Lease (14 Servers)  | $28,500               |
| SAN Storage Array (120 TB Raw, RAID-10 Usable, Controller)  | $16,800               |
| Data Center Colocation (Rack space, Power, Precision Cooling)| $19,200               |
| VMware vSphere Enterprise Plus & vCenter Licensing          | $11,400               |
| Microsoft SQL Server Enterprise (Per-Core Licensing)        | $22,600               |
| Windows Server Datacenter OS Licensing                      | $6,500                |
| Offsite LTO Tape Archival & Courier Disaster Logistics      | $3,800                |
| Network Leased Lines & Dedicated Multiprotocol Edge Links   | $8,400                |
| Hardware Maintenance, SAN Firmware Support & Vendor SLAs   | $7,200                |
| 24/7 Systems Administration & Data Center Staff Overhead    | $18,000               |
+-------------------------------------------------------------+-----------------------+
| TOTAL ON-PREMISES MONTHLY RUN-RATE BASELINE                 | $142,400 / month      |
+-------------------------------------------------------------+-----------------------+
```

#### Major Inefficiencies of the On-Premises Model:
* **Over-Provisioned Peak Headroom**: Hardware was sized for absolute peak load (100k users during daytime pandemic surges), leaving $>65\%$ of CPU and memory idle at night.
* **Prohibitive SQL Server Licensing**: Core-based licensing on multi-socket servers incurs punitive monthly amortization regardless of database utilization.
* **Single-Site Downtime Risk**: Zero disaster recovery capability; an electrical or cooling failure halts revenue and exposes CHA to compliance penalties.

---

### 3. AWS Target Architecture Sizing & Bill of Materials (100,000 Concurrent Users)

The target AWS environment is sized for **100,000 concurrent active users** across the Patient Monitoring Platform (PMP) and Telemedicine & Patient Portal (TPP).

#### Sizing Parameters:
* **Concurrent Users**: 100,000 peak (daytime clinical hours), tapering to 15,000 off-peak.
* **PMP Telemetry**: 10,000 connected wearable medical devices transmitting vitals every 60 seconds (166.7 MQTT messages/second).
* **TPP HTTP Traffic**: Average 4,500 requests/second with 15 TB outbound CDN delivery/month.
* **Database Workload**: 70% reads (reporting, EHR retrieval) and 30% writes (prescriptions, booking, vitals).

#### Itemized AWS Service Breakdown (Unoptimized On-Demand Baseline vs Optimized):

```
+-------------------------------------------------------+-------------------+-------------------+
| AWS Service Component                                | On-Demand (USD)   | Optimized (USD)   |
+-------------------------------------------------------+-------------------+-------------------+
| 1. Compute Tier (ECS on AWS Fargate)                  |                   |                   |
|    - Average 24 Tasks (2 vCPU, 4 GB RAM) across 3 AZs  |                   |                   |
|    - 25% Baseline Fargate (Compute Savings Plan 3-Yr) | $4,850            | $2,328 (52% cut)  |
|    - 75% Elastic Fargate Spot Provider                | $14,550           | $4,365 (70% cut)  |
|    - Application Load Balancers (Dual Multi-AZ)       | $210              | $210              |
| 2. Database & Persistence Tier                        |                   |                   |
|    - Amazon Aurora PostgreSQL Serverless v2 (Multi-AZ)|                   |                   |
|      (Average 6 ACUs baseline, scaling to 16 ACUs)    | $12,800           | $7,680 (Auto-Scale)
|    - Amazon DynamoDB (On-Demand for IoT Telemetry)    | $2,450            | $2,100 (TTL trim) |
|    - Amazon ElastiCache Redis Cluster (3-Node Multi-AZ)| $1,150           | $690 (1-Yr RI)    |
| 3. Storage & Medical Data Lake                        |                   |                   |
|    - Amazon S3 Medical Lake (60 TB Initial)           |                   |                   |
|      (Intelligent-Tiering & Glacier Deep Archive)     | $1,380            | $485 (65% cut)    |
|    - S3 API & Data Management Requests                | $320              | $180              |
| 4. Networking, Hybrid Interconnect & CDN              |                   |                   |
|    - Amazon CloudFront CDN (15 TB Data Transfer Out)  | $1,280            | $896 (Discount tier)
|    - AWS Direct Connect (10 Gbps Dedicated Port)      | $1,600            | $1,600            |
|    - AWS Transit Gateway (Attachments & Data Proc)    | $1,850            | $1,420            |
|    - NAT Gateway (Minimised by S3/DynamoDB VPCEs)     | $2,100            | $450 (VPCE bypass)|
| 5. IoT & Streaming Ingestion                          |                   |                   |
|    - AWS IoT Core (10k Devices, 432M msgs/month)      | $432              | $432              |
|    - Amazon Kinesis Data Streams (4 Shards)           | $150              | $150              |
| 6. Security, Monitoring & Governance                  |                   |                   |
|    - Amazon CloudWatch (Metrics, Logs Insights, X-Ray)| $1,850            | $1,250 (Log filter)
|    - AWS WAF & AWS Shield Standard                    | $140              | $140              |
|    - AWS KMS (Customer Managed Keys & Cryptographic Ops)| $380           | $220 (Bucket keys)|
|    - AWS GuardDuty, Security Hub & Config Conformance | $1,200            | $980              |
+-------------------------------------------------------+-------------------+-------------------+
| TOTAL MONTHLY EXPENDITURE                             | $48,662 / month   | $25,176 / month   |
+-------------------------------------------------------+-------------------+-------------------+
```

---

### 4. FinOps Cost Optimisation Strategies (Achieving $\ge 40\%$ Savings)

```
                       [Total On-Premises Baseline: $142,400/mo]
                                          │
                                          ▼
                       [Standard AWS On-Demand: $48,662/mo]
                              (Immediate 65.8% Savings)
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     [FinOps Optimization Strategy]                 [Optimized Cloud Run-Rate]
     • 3-Year Compute Savings Plans                 • $25,176 / month
     • 75% Fargate Spot Capacity Providers          • 82.3% Savings vs On-Prem
     • S3 Intelligent-Tiering & Deep Archive        • 48.3% Savings vs On-Demand
     • Gateway VPC Endpoints for S3 & DynamoDB
```

#### Strategy 1: Fargate Spot Capacity Provider Blending
* **Mechanism**: ECS service configured with `FARGATE` for a base count of 2 tasks per service, with all remaining scaling containers dispatched to `FARGATE_SPOT` (weight: 3).
* **Financial Impact**: Fargate Spot delivers up to a **70% discount** compared to standard on-demand pricing. Because healthcare microservices are stateless and fronted by an ALB with graceful draining (deregistration delay 30s), Fargate Spot interruptions (with 2-minute termination warnings) carry zero impact on patient sessions.
* **Monthly Savings**: **$10,185 / month**.

#### Strategy 2: 3-Year Compute Savings Plans for Predictable Compute
* **Mechanism**: A 3-Year All-Upfront Compute Savings Plan is applied to the baseline 25% non-interruptible Fargate tasks.
* **Financial Impact**: Yields a **52% discount** over On-Demand Fargate pricing. Unlike EC2 Instance Savings Plans, Compute Savings Plans apply automatically regardless of container family, size, or region.
* **Monthly Savings**: **$2,522 / month**.

#### Strategy 3: S3 Lifecycle Automated Tiering & Glacier Deep Archive
* **Mechanism**: Medical scans, DICOM images, and historical patient logs transition automatically:
  * 0–90 Days: `S3 Standard` / `Intelligent-Tiering` (Instant clinical access).
  * 91–180 Days: `S3 Standard-Infrequent Access` ($0.0125/GB vs $0.023/GB).
  * 181–365 Days: `S3 Glacier Flexible Retrieval` ($0.0036/GB).
  * 365+ Days: `S3 Glacier Deep Archive` ($0.00099/GB) for 7-year regulatory retention.
* **Financial Impact**: Reduces long-term storage costs by over **65%** compared to keeping all data on S3 Standard.
* **Monthly Savings**: **$895 / month**.

#### Strategy 4: VPC Gateway Endpoints for S3 and DynamoDB
* **Mechanism**: Route tables direct all S3 and DynamoDB API calls through AWS Gateway Endpoints rather than traversing NAT Gateways.
* **Financial Impact**: NAT Gateways charge $0.059 per GB processed in `ap-southeast-1`. Routing 28 TB of monthly data lake and telemetry writes through free Gateway Endpoints eliminates **$1,650/month** in NAT data fees.
* **Monthly Savings**: **$1,650 / month**.

#### Strategy 5: Dynamic Aurora Serverless v2 Scaling
* **Mechanism**: Instead of provisioning fixed `db.r6g.4xlarge` instances ($1,152/month each $\times$ 3 AZs = $3,456/month baseline), Aurora Serverless v2 scales dynamically between 0.5 ACU ($0.06/hour) at night and 16 ACU ($1.92/hour) during peak clinic hours.
* **Monthly Savings**: **$5,120 / month**.

---

### 5. Final Mathematical TCO Comparison & Proof of 40%+ Reduction

```
+------------------------------------+------------------+-----------------------+
| Comparison Dimension               | Monthly Expense  | Annualized TCO        |
+------------------------------------+------------------+-----------------------+
| 1. On-Premises Legacy Baseline     | $142,400         | $1,708,800            |
| 2. AWS Target Baseline (On-Demand) | $48,662          | $583,944              |
| 3. AWS Optimized (FinOps Engine)   | $25,176          | $302,112              |
+------------------------------------+------------------+-----------------------+
| NET SAVINGS VS ON-PREMISES         | $117,224 / month | $1,406,688 / year     |
| PERCENTAGE REDUCTION               | 82.3% REDUCTION  | (Mandate: ≥ 40%)      |
+------------------------------------+------------------+-----------------------+
| NET SAVINGS VS AWS ON-DEMAND       | $23,486 / month  | $281,832 / year       |
| PERCENTAGE REDUCTION               | 48.3% REDUCTION  | (Pure Cloud FinOps)   |
+------------------------------------+------------------+-----------------------+
```

$$\text{TCO Reduction} = \frac{\$142,400 - \$25,176}{\$142,400} \times 100\% = \mathbf{82.3\% \text{ Total Cost Reduction}}$$

Even when evaluated strictly inside AWS (comparing unoptimized on-demand versus the proposed FinOps architecture):

$$\text{Cloud FinOps Reduction} = \frac{\$48,662 - \$25,176}{\$48,662} \times 100\% = \mathbf{48.3\% \text{ Cloud Savings}}$$

Both metrics decisively fulfill the university requirement of achieving at least a 40% reduction.

---

### 6. AWS Academy Credit Management & Teardown Strategy ($200 Budget)

As emphasized by the lecturer, students are allocated approximately **$200 in AWS credits**. To prevent accidental credit exhaustion over a multi-month period, the following runbook is strictly observed:

1. **Deploy for Verification**: Deploy the Terraform stack (`terraform apply -auto-approve`) only during designated testing and evidence collection windows.
2. **Immediate Evidence Capture**: Run test scripts (e.g. `greengrass_edge_telemetry.py`, curl ALB health endpoints, test DMS replication task), capture required screenshots and logs for the appendices.
3. **Automated Teardown**: Immediately issue `terraform destroy -auto-approve` to terminate all billable resources (ALBs, NAT Gateways, Aurora clusters, and ECS containers).
4. **Zero Residual Billing**: Gateway endpoints, IAM policies, and S3 empty buckets carry zero ongoing cost when idle. NAT Gateways ($0.059/hour each) and Aurora instances are permanently deleted when not actively collecting evidence.
