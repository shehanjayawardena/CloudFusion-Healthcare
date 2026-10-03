# CloudFusion Healthcare Analytics Ltd (CHA)
## AWS Cloud Modernisation & Technical Consultancy Presentation

**Module**: COMP60010 – Enterprise Cloud and Distributed Web Applications (ECDWA)  
**Deliverable**: 10–15 Slide Executive Presentation  
**Target Audience**: C-Suite Executives, Chief Medical Information Officer (CMIO), Solutions Architects  

---

### Slide 1: Title & Executive Introduction
* **Title**: Enterprise Cloud Modernisation & Distributed Healthcare Architecture
* **Subtitle**: Architectural Transformation of CloudFusion Healthcare Analytics Ltd (CHA)
* **Presenter**: Lead Cloud Solutions Architect
* **Target Cloud Platform**: Amazon Web Services (AWS) | Region: `ap-southeast-1` (Singapore)
* **Key Themes**: High Availability (99.999%), 100,000+ Concurrent Scalability, $\ge$40% Cost Reduction, Continuous IoT Telemetry, Zero-Trust Healthcare Compliance.

> **Speaker Notes**:  
> "Good morning, members of the executive board and academic evaluators. Today, I present the architectural blueprint for migrating CloudFusion Healthcare Analytics from an aging on-premises data center to an enterprise-grade, highly resilient cloud architecture on AWS. This presentation details how we achieve five-nines availability, cut infrastructure operational costs by 82.3%, and unlock real-time IoT clinical monitoring."

---

### Slide 2: The Legacy Infrastructure Crisis
* **Physical Footprint**: 220 virtual machines hosted on VMware ESXi in a single on-premises data center in South Asia.
* **Architecture**: Fragile monolithic application; tight coupling between patient billing, scheduling, and clinical telemetry.
* **Database Contention**: Standalone Microsoft SQL Server and MySQL; manual backups; locking contention during reporting.
* **Single Point of Failure (SPOF)**: Zero disaster recovery environment; power or cooling failure causes total regional blackout.
* **Operational Inefficiencies**: Manual SSH/RDP deployments; no auto-scaling; legacy IPsec VPN bottleneck to 22 branch hospitals.

> **Speaker Notes**:  
> "Our current setup is reaching critical failure. Operating 220 VMs in a single facility creates an unacceptable life-safety risk. A single hardware failure or power outage knocks out patient monitoring across all hospitals. Furthermore, releasing a minor update requires midnight maintenance windows because our monolithic codebase cannot scale or deploy independently."

---

### Slide 3: Strategic Business Drivers & The "Five Nines" Imperative
* **Contractual vs Clinical Availability**:
  * Assignment Baseline: **99.99% availability** (permits 52.56 minutes downtime/year).
  * Clinical Life-Safety Target: **99.999% "Five Nines"** (permits $<5.26$ minutes downtime/year), mirroring telecommunications standards.
* **Massive Concurrency**: Dynamic auto-scaling supporting **over 100,000 concurrent users** (doctors, patients, lab techs).
* **Cost Mandate**: Reduce operational expenditure by **at least 40%** (slashing an unoptimized $142k/mo baseline).
* **Compliance**: Strict adherence to **GDPR, HIPAA, and ISO 27001**.
* **Edge Resilience**: Uninterrupted hospital ward vital sign monitoring during regional internet outages.

> **Speaker Notes**:  
> "The business mandate demands at least 40% cost reduction and 99.99% uptime. But in healthcare, downtime means lost lives. As noted in telecommunications, five nines—99.999%—is the true gold standard. Our target architecture is engineered with active-active Multi-AZ redundancy to approach near-zero unplanned downtime."

---

### Slide 4: Clinical Paradigm Shift: Discrete Polling vs Continuous IoT Telemetry
* **Traditional / Old Hospitals (Discrete Polling)**:
  * Nurses record vitals in paper charts every 4–6 hours.
  * **The Fatal Blind Spot**: If a cardiac patient suffers myocardial infarction between visits, doctors have zero visibility. Physicians can only react retrospectively after catastrophic cardiac arrest.
* **Modern Cloud Hospitals (Continuous IoT Streaming)**:
  * Wearable sensors continuously stream SpO2, heart rate, and ECG waveforms every 60 seconds to AWS IoT Core.
  * Real-time dashboards visualize subtle physiological variations.
  * Cloud AI predictive algorithms identify clinical deterioration (e.g. sepsis) **24 to 48 hours in advance**, enabling proactive intervention.

> **Speaker Notes**:  
> "Here is why cloud modernization is a clinical necessity. In the traditional ward, a nurse checks a patient every four hours. If that patient deteriorates in minute five, nobody knows until hour four—often too late. With our new AWS IoT streaming pipeline, telemetry is analyzed every minute. Subtle physiological drift is flagged instantly, allowing doctors to intervene before a crisis occurs."

---

### Slide 5: Strategic Migration Framework (Well-Architected & The 7 R's)
* **AWS Well-Architected Framework**: Aligned across all 6 Pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability).
* **Selected 7 R's Migration Strategies**:
  * **Replatform**: Migrate Microsoft SQL Server & MySQL to **Amazon Aurora PostgreSQL Serverless v2** via AWS SCT.
  * **Refactor**: Modernize monolithic applications into decoupled container microservices on **Amazon ECS on AWS Fargate**; refactor telemetry ingestion to **AWS IoT Core + Kinesis**.
  * **Rehost**: Selectively migrate legacy Windows utilities via **AWS Application Migration Service (MGN)**.
* **Infrastructure as Code (IaC)**: Standardized on **HashiCorp Terraform** over CloudFormation for multi-cloud and hybrid VMware portability.

> **Speaker Notes**:  
> "We structured our migration using the AWS Well-Architected Framework. We didn't attempt to force all 7 R's indiscriminately; we selected Replatform for databases to eliminate SQL Server license costs, and Refactor for our web platforms into containers. We chose Terraform as our IaC standard because it allows us to manage both our cloud stack and our on-premises hospital edge infrastructure under a single version-controlled tool."

---

### Slide 6: Low-Downtime Data Migration Architecture
* **AWS Database Migration Service (AWS DMS)**:
  * Multi-AZ `dms.r5.xlarge` replication instance deployed in private subnets.
  * **Phase 1: Full Load**: Parallel multi-threaded transfer of historic relational tables.
  * **Phase 2: Continuous CDC**: Captures ongoing transaction logs with $<2$ seconds latency.
  * **Cutover Window**: $<15$ minutes total application maintenance window.
* **Historical Data Archival (AWS Glue PySpark)**:
  * Converts 5+ years of archive data into partitioned Apache Parquet on Amazon S3.
  * Generates row-level **SHA-256 cryptographic checksums** reconciling against on-premise manifests for verifiable compliance.

> **Speaker Notes**:  
> "Migrating healthcare databases cannot tolerate data loss or days of downtime. We deploy AWS DMS with continuous Change Data Capture. While our teams test the new environment, changes from the live hospital database replicate continuously in under two seconds. Cutover takes under 15 minutes, with AWS Glue verifying cryptographic SHA-256 hashes to guarantee 100% record integrity."

---

### Slide 7: Target AWS Multi-AZ Network Topology
* **VPC Architecture**: `10.50.0.0/16` deployed across 3 Availability Zones (`ap-southeast-1a, 1b, 1c`).
* **Subnet Micro-Segmentation**:
  * **Public Subnets (`.1.0, .2.0, .3.0/24`)**: Houses ALBs and 3 high-availability NAT Gateways.
  * **Private App Subnets (`.10.0, .20.0, .30.0/24`)**: Houses ECS Fargate containers and Lambda functions (No public IPs).
  * **Private Database Subnets (`.100.0, .110.0, .120.0/24`)**: Isolated from internet; houses Aurora PostgreSQL and ElastiCache Redis.
* **VPC Gateway Endpoints**: Amazon S3 and DynamoDB traffic stays on the private AWS network, bypassing NAT Gateways and eliminating data processing charges.

> **Speaker Notes**:  
> "This slide illustrates our multi-tier VPC topology across three availability zones. Public access is restricted solely to the Application Load Balancers. Our containerized microservices and databases sit in isolated private subnets. By provisioning VPC Gateway Endpoints for S3 and DynamoDB, we keep sensitive health records off the public internet while saving thousands of dollars in NAT data transfer fees."

---

### Slide 8: Patient Monitoring Platform (PMP) Architecture
* **High-Throughput IoT Ingestion**:
  * Wearable devices connect via **MQTT over TLS 1.3 (mTLS)** with individual X.509 client certificates.
  * Ingestion handled by **AWS IoT Core**, scaling to millions of concurrent messages.
* **Dual-Path Clinical Routing**:
  * **Emergency Triage (<500ms SLA)**: IoT Topic Rule detects abnormal vitals (`SpO2 < 90%` or `HR > 140`) $\rightarrow$ Routes immediately to **Amazon SNS** & **AWS Lambda** $\rightarrow$ Triggers push notifications to doctor mobile pagers and ICU screens.
  * **Continuous Streaming Pipeline**: Telemetry streams into **Amazon Kinesis Data Streams** $\rightarrow$ Ingested into **Amazon DynamoDB** (Hot store, TTL 30 days) and **Amazon S3 Medical Lake** (Snappy Parquet via Kinesis Firehose).

> **Speaker Notes**:  
> "For the Patient Monitoring Platform, wearable medical devices authenticate via mutual TLS X.509 certificates. Incoming telemetry is split into two streams: critical emergency events route in under 500 milliseconds via Lambda to alert doctors immediately, while standard continuous vitals stream through Amazon Kinesis into DynamoDB and our S3 data lake."

---

### Slide 9: Telemedicine & Patient Portal (TPP) Architecture
* **Global Edge Network**: **Amazon Route 53** latency routing $\rightarrow$ **Amazon CloudFront CDN** delivering static React SPA assets stored in S3 protected via **Origin Access Control (OAC)**.
* **Web Security**: **AWS WAF** inspects all inbound traffic at the edge, blocking SQL injection, cross-site scripting (XSS), and automated bot attacks.
* **Microservices Tier**: **Amazon ECS on AWS Fargate** auto-scales across 3 AZs from 6 to 60 containers based on target CPU (65%) and request metrics.
* **Real-Time Video Consultations**: Powered by **Amazon Chime SDK** WebRTC encrypted media pipelines, eliminating video processing burden on backend application servers.
* **Persistence Tier**: **Amazon Aurora PostgreSQL Serverless v2** + **Amazon ElastiCache Redis** for sub-millisecond session caching.

> **Speaker Notes**:  
> "The Telemedicine and Patient Portal leverages CloudFront and AWS WAF at the edge. The backend runs as containerized microservices on AWS Fargate that scale elastically to meet morning appointment surges. Video consultations run over the Amazon Chime SDK with end-to-end encrypted WebRTC streams, ensuring patient video never passes unencrypted through backend servers."

---

### Slide 10: Multi-Layered Zero-Trust Security Architecture
* **Layer 1 (Perimeter)**: AWS Shield Standard + AWS WAF managed rule groups.
* **Layer 2 (Network)**: Strict Security Group chaining: ALB SG $\rightarrow$ ECS SG $\rightarrow$ Aurora DB SG. Zero outbound internet routes from database tier.
* **Layer 3 (Identity)**: Attribute-Based Access Control (ABAC); enforced hardware MFA; temporary credentials via AWS STS.
* **Layer 4 (Cryptography)**: **AWS KMS Customer Managed Keys (CMK)** with automated annual rotation; mandatory TLS 1.3 in transit (`aws:SecureTransport: true`).
* **Layer 5 (Audit & Detection)**: **AWS CloudTrail** organization trails + **AWS Config** conformance packs + **Amazon GuardDuty** AI threat detection + **AWS Security Hub**.

> **Speaker Notes**:  
> "Security in healthcare is paramount. We implemented a Zero-Trust architecture. Security groups are strictly chained so our database only accepts connections from authorized ECS tasks. All data at rest is encrypted with Customer Managed KMS keys that rotate automatically. Every API call is logged immutably, and GuardDuty uses machine learning to detect unauthorized access anomalies."

---

### Slide 11: Healthcare Governance & Compliance Posture
* **GDPR Article 17 (Right to Erasure)**: Direct patient identifiers are salted and pseudonymized using SHA-256 hashes during ingestion. Cryptographic erasure enables instant deletion of individual patient encryption keys, rendering records irreversibly unreadable while preserving aggregated clinical analytics.
* **HIPAA Audit Controls (45 CFR § 164.312(b))**: AWS CloudTrail logs are locked in an isolated security S3 bucket using **S3 Object Lock in Compliance Mode (WORM)**, preventing log deletion or modification even by root administrators.
* **ISO 27001 Alignment**: Continuous automated posture evaluation through AWS Security Hub and AWS Config conformance packs.

> **Speaker Notes**:  
> "Compliance is codified into our architecture. Under GDPR, we support the Right to Erasure through cryptographic pseudonymization: deleting a patient's individual decryption key instantly erases their identifiable record. For HIPAA compliance, CloudTrail logs are protected with S3 Object Lock in Compliance Mode, guaranteeing a tamper-proof audit trail that cannot be deleted by anyone for seven years."

---

### Slide 12: Hybrid Connectivity & Hospital Edge Integration
* **Primary Interconnect**: Dedicated **10 Gbps AWS Direct Connect (DX)** providing sub-5ms deterministic latency for large DICOM medical scans and live telehealth video.
* **Automated Redundant Failover**: Active-standby **AWS Site-to-Site Dual IPsec VPN** with automated BGP failover in $<3$ seconds.
* **Centralized Hub**: **AWS Transit Gateway (TGW)** interconnecting central HQ, 22 branch hospitals, and production cloud VPCs.
* **Hybrid DNS**: **Amazon Route 53 Resolver** (Inbound endpoints resolve AWS domains from clinics; Outbound endpoints resolve on-premise Active Directory).
* **Edge Computing via AWS IoT Greengrass v2**: Edge appliances deployed in hospital wards filter sensor noise and maintain an **encrypted local SQLite buffer** to store vitals during network disconnects, syncing automatically upon reconnection.

> **Speaker Notes**:  
> "To connect our 22 branch hospitals, we deploy a 10 Gbps AWS Direct Connect circuit backed by automated BGP failover to an IPsec VPN over AWS Transit Gateway. Crucially, we deploy AWS IoT Greengrass edge gateways inside hospital wards. If an external storm severs the hospital's internet connection, local ward monitors continue to process vitals and buffer telemetry locally, syncing back to the cloud as soon as the link recovers."

---

### Slide 13: Financial Engineering & FinOps (82.3% TCO Reduction)
* **Monthly Run-Rate Comparison**:
  * On-Premises Baseline: **$142,400 / month** ($1.71M annual run rate).
  * AWS On-Demand Baseline: **$48,662 / month** (Immediate 65.8% savings).
  * **AWS FinOps Optimized Target**: **$25,176 / month** (82.3% total TCO savings).
* **Key FinOps Levers**:
  * **Fargate Spot Blending**: 75% elastic tasks dispatched to Fargate Spot $\rightarrow$ **70% compute savings**.
  * **3-Year Compute Savings Plans**: Applied to 25% baseline tasks $\rightarrow$ **52% savings**.
  * **S3 Lifecycle Tiering**: Auto-transition to Glacier Deep Archive $\rightarrow$ **65% storage savings**.
  * **Gateway VPC Endpoints**: Eliminates NAT Gateway data processing fees $\rightarrow$ **Saves $1,650/month**.
* **Corporate Mandate**: Requires $\ge 40\%$ reduction; achieved **48.3% savings within AWS** and **82.3% overall TCO reduction**.

> **Speaker Notes**:  
> "Financially, the business required a 40% cost reduction. Our on-premises run rate was $142,400 per month. By migrating to AWS On-Demand, costs immediately drop to $48,600. Through active FinOps—blending Fargate Spot, committing to a 3-Year Compute Savings Plan, and using S3 Glacier lifecycle tiering—our optimized run-rate drops to $25,176 per month. That represents an 82.3% total cost reduction, far exceeding our target."

---

### Slide 14: Disaster Recovery & Business Continuity Framework
* **SLA Performance by Disaster Scenario**:
  * **AZ Outage (Local Center Failure)**: Automatic failover in **<30 seconds** via Aurora Multi-AZ storage and ECS task rescheduling (RPO: **0 seconds / Zero data loss**).
  * **Accidental Database Corruption**: Restored in **<15 minutes** via Aurora Point-in-Time Recovery (PITR) with continuous incremental logging (RPO: **<5 minutes**).
  * **Catastrophic Regional Disaster**: Cross-region Pilot Light architecture in Sydney (`ap-southeast-2`) using S3 Cross-Region Replication and Aurora Global Database snapshots (RTO: **<45 minutes**, RPO: **<15 minutes**).

> **Speaker Notes**:  
> "Our legacy infrastructure had zero disaster recovery. In our target architecture, if an entire AWS data center goes offline, Aurora storage and ECS Fargate containers fail over automatically in under 30 seconds with zero data loss. In the event of a catastrophic regional failure, our cross-region pilot light restores full operations in under 45 minutes."

---

### Slide 15: Conclusion, Strategic Roadmap & Next Steps
* **Summary of Transformation**:
  1. **Availability**: 99.99% SLA achieved; multi-AZ design targets five-nines (99.999%).
  2. **Scalability**: Elastic support for 100,000+ concurrent healthcare users.
  3. **Cost**: 82.3% TCO reduction, saving over $1.4M annually.
  4. **Clinical Innovation**: Continuous IoT vital signs monitoring + Greengrass edge resilience.
  5. **Turnkey Implementation**: Complete Terraform IaC, IAM, DMS, and Glue codebase ready for deployment.
* **Next Steps**:
  * **Month 1**: Deploy staging environment via Terraform; execute DMS pilot database migration.
  * **Month 2**: Conduct cutover testing, load validation, and security penetration audits.
  * **Month 3**: Execute 15-minute production cutover; commence physical server decommissioning.

> **Speaker Notes**:  
> "In conclusion, this modernization blueprint successfully addresses every business driver and technical requirement. We achieve five-nines reliability, reduce costs by 82.3%, unlock real-time predictive patient care, and provide turnkey Terraform and DMS automation. The architecture is robust, fully compliant, and ready for deployment. Thank you, and I look forward to your questions."
