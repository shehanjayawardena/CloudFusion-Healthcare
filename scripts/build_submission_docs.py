"""
CloudFusion Healthcare Analytics Ltd (CHA)
Master Document and Presentation Builder: Generates Word (.docx) and PowerPoint (.pptx)
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

import pptx
from pptx.util import Inches as PInches, Pt as PPt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor as PRGBColor

# ====================================================================
# PART 1: Word Document Generator
# ====================================================================
def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def generate_word_report():
    doc = docx.Document()
    
    # Page setup (Standard A4, 1-inch margins)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    
    # Configure styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x1e, 0x29, 0x3b) # Slate 800
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)
    
    # ----------------------------------------------------
    # COVER PAGE
    # ----------------------------------------------------
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(72)
    
    p_module = doc.add_paragraph()
    r_mod = p_module.add_run("COMP60010: ENTERPRISE CLOUD AND DISTRIBUTED WEB APPLICATIONS")
    r_mod.font.size = Pt(12)
    r_mod.font.bold = True
    r_mod.font.color.rgb = RGBColor(0x02, 0x84, 0xc7) # Sky blue
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("Enterprise Cloud Architecture & Migration Strategy:\nModernising CloudFusion Healthcare Analytics Ltd (CHA)")
    r_title.font.size = Pt(24)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x0f, 0x17, 0x2a) # Slate 900
    
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("A Technical Consultancy Report and Engineering Blueprint for Cloud Transformation, Five-Nines Availability, and Continuous IoT Healthcare Monitoring on Amazon Web Services (AWS)")
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
    p_sub.paragraph_format.space_after = Pt(48)
    
    # Cover Metadata Table
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Assessment Type:", "Individual Technical Consultancy Report & Presentation (50% Module Mark)"),
        ("Scenario Client:", "CloudFusion Healthcare Analytics Ltd (CHA)"),
        ("Target Platform:", "Amazon Web Services (AWS) - ap-southeast-1 (Singapore)"),
        ("Academic Period:", "Final Year - B.Sc. (Hons) in Computing / Software Engineering"),
        ("Submission Date:", "October 2026")
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        row = meta_table.rows[row_idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.0)
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.color.rgb = RGBColor(0x0f, 0x17, 0x2a)
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        
        set_cell_background(c0, "F8FAFC")
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c0, 80, 80, 100, 100)
        set_cell_margins(c1, 80, 80, 100, 100)

    doc.add_page_break()
    
    # ----------------------------------------------------
    # Read Markdown Report Content and convert
    # ----------------------------------------------------
    md_path = r'docs\report\COMP60010_Technical_Consultancy_Report.md'
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_code_block = False
    code_lines = []
    
    # Skip frontmatter / duplicate title on first 10 lines
    start_idx = 0
    for idx, l in enumerate(lines):
        if l.startswith("## Executive Summary"):
            start_idx = idx
            break
            
    for l in lines[start_idx:]:
        line = l.rstrip()
        
        # Handle code blocks
        if line.startswith("```"):
            if in_code_block:
                in_code_block = False
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.left_indent = Inches(0.2)
                r = p.add_run("\n".join(code_lines))
                r.font.name = 'Consolas'
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(0x0f, 0x17, 0x2a)
                code_lines = []
            else:
                in_code_block = True
            continue
            
        if in_code_block:
            code_lines.append(line)
            continue
            
        # Headers
        if line.startswith("## "):
            h_text = line.replace("## ", "").strip()
            h = doc.add_heading(level=1)
            h.paragraph_format.space_before = Pt(18)
            h.paragraph_format.space_after = Pt(6)
            r = h.add_run(h_text)
            r.font.name = 'Calibri'
            r.font.size = Pt(16)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x03, 0x69, 0xa1) # Dark sky blue
            
            # Embed corresponding figure where relevant
            if "Task 1" in h_text and os.path.exists('docs/report/figures/clinical_vitals_telemetry_contrast.png'):
                doc.add_paragraph()
                doc.add_picture('docs/report/figures/clinical_vitals_telemetry_contrast.png', width=Inches(6.2))
                cap = doc.add_paragraph()
                cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                rc = cap.add_run("Figure 1: Continuous AWS IoT Telemetry vs Traditional Discrete Polling (Clinical Evidence)")
                rc.font.size = Pt(9)
                rc.font.italic = True

            elif "Task 3" in h_text and os.path.exists('docs/report/figures/aws_architecture_diagram.jpg'):
                doc.add_paragraph()
                doc.add_picture('docs/report/figures/aws_architecture_diagram.jpg', width=Inches(6.2))
                cap = doc.add_paragraph()
                cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                rc = cap.add_run("Figure 2: Comprehensive Target AWS Cloud Architecture Diagram for CloudFusion Healthcare Analytics Ltd")
                rc.font.size = Pt(9)
                rc.font.italic = True
                
            elif "Task 5" in h_text and os.path.exists('docs/report/figures/cost_comparison_tco.png'):
                doc.add_paragraph()
                doc.add_picture('docs/report/figures/cost_comparison_tco.png', width=Inches(6.0))
                cap = doc.add_paragraph()
                cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                rc = cap.add_run("Figure 3: Total Cost of Ownership (TCO) Comparison: On-Premises Baseline vs Cloud FinOps")
                rc.font.size = Pt(9)
                rc.font.italic = True
                
                if os.path.exists('docs/report/figures/aws_monthly_cost_breakdown.png'):
                    doc.add_paragraph()
                    doc.add_picture('docs/report/figures/aws_monthly_cost_breakdown.png', width=Inches(5.5))
                    cap2 = doc.add_paragraph()
                    cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    rc2 = cap2.add_run("Figure 4: Target AWS Architecture Monthly Cost Distribution ($25,176 / month)")
                    rc2.font.size = Pt(9)
                    rc2.font.italic = True
            continue

            
        if line.startswith("### "):
            h_text = line.replace("### ", "").strip()
            h = doc.add_heading(level=2)
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(4)
            r = h.add_run(h_text)
            r.font.name = 'Calibri'
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x0f, 0x17, 0x2a)
            continue

        if line.startswith("#### "):
            h_text = line.replace("#### ", "").strip()
            h = doc.add_heading(level=3)
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(2)
            r = h.add_run(h_text)
            r.font.name = 'Calibri'
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
            continue

        # Bullet points
        if line.startswith("* ") or line.startswith("- "):
            b_text = line[2:].strip()
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(b_text)
            continue

        # Normal text lines
        if line.strip():
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(6)
            p.add_run(line)
            
    doc.save(r'docs\report\COMP60010_Technical_Consultancy_Report.docx')
    print(r'[OK] Generated docs\report\COMP60010_Technical_Consultancy_Report.docx')

# ====================================================================
# PART 2: PowerPoint Presentation Generator
# ====================================================================
def generate_pptx_deck():
    prs = pptx.Presentation()
    # 16:9 Widescreen format
    prs.slide_width = PInches(13.333)
    prs.slide_height = PInches(7.5)
    
    blank_layout = prs.slide_layouts[6]
    
    slides_content = [
        {
            "num": "01",
            "title": "Enterprise Cloud Modernisation & Architecture",
            "sub": "CloudFusion Healthcare Analytics Ltd (CHA) | AWS Modernisation Strategy",
            "cards": [
                ("99.999% Availability", "Five-nines clinical reliability target with Multi-AZ redundancy."),
                ("100,000+ Users", "Massive elastic auto-scaling via ECS Fargate and Aurora Serverless v2."),
                ("82.3% TCO Savings", "Slashing $142k/mo on-premises run-rate to $25k/mo on AWS.")
            ]
        },
        {
            "num": "02",
            "title": "The Legacy Infrastructure Crisis",
            "sub": "On-Premises Single-Site Vulnerabilities & Monolithic Failure Modes",
            "cards": [
                ("Single Point of Failure", "220 VMware VMs in a single data center; power/cooling failure causes total regional blackout."),
                ("Monolithic Coupling", "Billing, EHR, and patient vitals share memory; single memory leak halts intensive care monitoring."),
                ("Operational Drag", "Manual deployments; no auto-scaling; legacy VPN bottlenecks to 22 branch hospitals.")
            ]
        },
        {
            "num": "03",
            "title": "Business Drivers & The Five Nines Imperative",
            "sub": "Contractual Mandate vs Clinical Life-Safety Realities",
            "cards": [
                ("Telco-Grade 99.999%", "99.99% permits 52.6 min/yr downtime; clinical life-safety demands 99.999% (<5.26 min/yr)."),
                ("100,000 Concurrent Scale", "Support morning clinic booking surges without database locking or server exhaustion."),
                ("FinOps Discipline", "Reduce operational expenses by at least 40% using serverless and savings plans.")
            ]
        },
        {
            "num": "04",
            "title": "Clinical Case for IoT: Discrete vs Continuous",
            "sub": "Transforming Healthcare from Reactive Guesswork to Predictive Prevention",
            "cards": [
                ("Discrete Nursing Polling", "Nurses record vitals every 4-6 hours; patient cardiac arrests between visits are completely unmonitored."),
                ("Continuous IoT Streaming", "Sensors stream SpO2 and ECG every 60s to AWS IoT Core; real-time dashboards track physiological drift."),
                ("AI Predictive Triage", "Machine learning algorithms forecast sepsis and decompensation 24 to 48 hours in advance.")
            ]
        },
        {
            "num": "05",
            "title": "Strategic Migration Framework (Well-Architected & 7 Rs)",
            "sub": "Targeted Cloud Modernisation Aligned with the 6 Well-Architected Pillars",
            "cards": [
                ("Replatform (Databases)", "Migrate MS SQL Server and MySQL to Amazon Aurora PostgreSQL Serverless v2 via AWS SCT & DMS."),
                ("Refactor (Applications)", "Decompose monolith into microservices on Amazon ECS on AWS Fargate; IoT to AWS IoT Core."),
                ("Terraform IaC Standard", "Terraform selected over CloudFormation to ensure hybrid portability across AWS and on-prem VMware.")
            ]
        },
        {
            "num": "06",
            "title": "Low-Downtime Data Migration Architecture",
            "sub": "Continuous Change Data Capture (CDC) & Cryptographic Validation",
            "cards": [
                ("AWS DMS Continuous CDC", "Multi-AZ replication instance captures ongoing transaction logs with < 2 seconds latency."),
                ("15-Minute Cutover", "Application downtime restricted to a 15-minute off-peak maintenance window."),
                ("AWS Glue PySpark Integrity", "Converts 5+ years of archives to Parquet; verifies row-level SHA-256 integrity checksums.")
            ]
        },
        {
            "num": "07",
            "title": "Target AWS Multi-AZ Network Topology",
            "sub": "VPC CIDR: 10.50.0.0/16 Spanning 3 Availability Zones in Singapore",
            "cards": [
                ("Public Subnets (.1.0, .2.0, .3.0)", "Houses Application Load Balancers and 3 redundant NAT Gateways for secure egress."),
                ("Private App Subnets (.10.0, .20.0, .30.0)", "Houses ECS Fargate tasks and Lambda functions with zero public IP addresses."),
                ("Isolated DB Subnets (.100.0, .110.0, .120.0)", "Completely isolated from internet; accepts PostgreSQL (5432) strictly from App SG.")
            ]
        },
        {
            "num": "08",
            "title": "Patient Monitoring Platform (PMP): IoT Stream",
            "sub": "Sub-Second Ingestion of Wearable Telemetry & Emergency Triage",
            "cards": [
                ("Secure mTLS Ingestion", "Medical wearables authenticate via mutual TLS (X.509 certs) publishing to AWS IoT Core."),
                ("Emergency Path (< 500ms)", "Hypoxia rule (SpO2 < 90%) routes immediately to Amazon SNS & Lambda for doctor pager alerts."),
                ("Streaming Analytics Lake", "Kinesis Data Streams writes hot records to DynamoDB and archival Parquet to Amazon S3.")
            ]
        },
        {
            "num": "09",
            "title": "Telemedicine & Patient Portal (TPP): Web App",
            "sub": "Distributed Microservices, WAF Edge Defense & Encrypted WebRTC",
            "cards": [
                ("Edge Security & CDN", "Route 53 + CloudFront CDN + AWS WAF protecting static React SPA hosted in S3 with OAC."),
                ("Elastic Fargate Microservices", "Decoupled services (EHR, Appointments, Billing) auto-scaling from 6 to 60 containers."),
                ("Amazon Chime SDK Video", "Peer-to-peer encrypted WebRTC video consultation sessions with zero backend compute load.")
            ]
        },
        {
            "num": "10",
            "title": "Multi-Layered Zero-Trust Security Architecture",
            "sub": "Defense-in-Depth Protecting Sensitive Electronic Health Records",
            "cards": [
                ("Network & Perimeter", "AWS WAF OWASP rules + strict Security Group chaining (ALB -> ECS -> Aurora DB)."),
                ("Identity & Cryptography", "Attribute-Based Access Control (ABAC), hardware MFA, and KMS Customer Managed Keys."),
                ("Continuous Auditing", "AWS CloudTrail WORM object locking, AWS Config conformance packs, and GuardDuty threat detection.")
            ]
        },
        {
            "num": "11",
            "title": "Healthcare Governance & Compliance Posture",
            "sub": "Strict Adherence to GDPR Article 17, HIPAA, and ISO 27001",
            "cards": [
                ("GDPR Right to Erasure", "Pseudonymized patient identifiers via HMAC-SHA256; cryptographic erasure of individual salt keys."),
                ("HIPAA Compliance Mode", "CloudTrail logs immutably locked using S3 Object Lock in Compliance Mode (cannot be deleted for 7 yrs)."),
                ("Zero Patient Data Leaks", "S3 Block Public Access enforced; mandatory TLS 1.3 encryption across all communication paths.")
            ]
        },
        {
            "num": "12",
            "title": "Hybrid Connectivity & Hospital Edge Integration",
            "sub": "10 Gbps Direct Connect Interconnect & AWS IoT Greengrass Ward Nodes",
            "cards": [
                ("Direct Connect + IPsec VPN", "10 Gbps dedicated link with automated BGP failover to Dual IPsec VPN in < 3 seconds via TGW."),
                ("Hybrid Route 53 DNS", "Inbound endpoints resolve AWS services from clinics; outbound endpoints resolve hospital LDAP."),
                ("Greengrass Edge Nodes", "Edge gateways in hospital wards filter vitals and buffer offline in SQLite during WAN outages.")
            ]
        },
        {
            "num": "13",
            "title": "FinOps Cost Optimization (82.3% TCO Reduction)",
            "sub": "Mathematical Proof of Slashing Operational Run-Rate Exceeding 40% Mandate",
            "cards": [
                ("On-Premises: $142,400/mo", "Baseline of 220 physical VMs, SAN storage arrays, VMware and SQL Server core licensing."),
                ("AWS On-Demand: $48,662/mo", "Immediate 65.8% reduction through serverless container and database modernization."),
                ("AWS FinOps Target: $25,176/mo", "82.3% Total TCO Savings via Fargate Spot (70% cut), 3-Yr Savings Plans, and S3 Glacier tiering.")
            ]
        },
        {
            "num": "14",
            "title": "Disaster Recovery & Business Continuity Framework",
            "sub": "Target Recovery Time Objective (RTO) and Recovery Point Objective (RPO)",
            "cards": [
                ("Single AZ Outage", "Aurora Multi-AZ storage failover in < 30 seconds with 0 seconds RPO (Zero Data Loss)."),
                ("Database Corruption", "Point-in-Time Recovery (PITR) restores database to any second within 15 minutes (< 5 min RPO)."),
                ("Catastrophic Region Outage", "Cross-region Pilot Light in Sydney (ap-southeast-2) with Route 53 automated DNS failover (< 45 min RTO).")
            ]
        },
        {
            "num": "15",
            "title": "Conclusion & Strategic Implementation Roadmap",
            "sub": "Turnkey Deliverables Ready for Immediate Staging and Production Cutover",
            "cards": [
                ("Month 1: Foundation", "Deploy Terraform stack in staging; configure DMS CDC replication; test Greengrass edge nodes."),
                ("Month 2: Load & Security Audit", "Validate 100,000 user concurrency via Locust; execute penetration testing and compliance audit."),
                ("Month 3: Production Cutover", "Execute 15-minute cutover window; repoint Route 53; decommission on-prem data center to save $1.4M/yr.")
            ]
        }
    ]
    
    for slide_data in slides_content:
        slide = prs.slides.add_slide(blank_layout)
        
        # Background fill (Deep Navy #0a0f1d)
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = PRGBColor(10, 15, 29)
        
        # Slide Header Number Tag
        tb_num = slide.shapes.add_textbox(PInches(1.0), PInches(0.6), PInches(4.0), PInches(0.4))
        p_num = tb_num.text_frame.paragraphs[0]
        p_num.text = f"SLIDE {slide_data['num']} // CLOUDFUSION AWS ARCHITECTURE"
        p_num.font.name = 'Calibri'
        p_num.font.size = PPt(10)
        p_num.font.bold = True
        p_num.font.color.rgb = PRGBColor(6, 182, 212) # Cyan
        
        # Title
        tb_title = slide.shapes.add_textbox(PInches(1.0), PInches(0.9), PInches(11.3), PInches(0.8))
        p_title = tb_title.text_frame.paragraphs[0]
        p_title.text = slide_data['title']
        p_title.font.name = 'Calibri'
        p_title.font.size = PPt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = PRGBColor(248, 250, 252) # White
        
        # Subtitle
        tb_sub = slide.shapes.add_textbox(PInches(1.0), PInches(1.6), PInches(11.3), PInches(0.5))
        p_sub = tb_sub.text_frame.paragraphs[0]
        p_sub.text = slide_data['sub']
        p_sub.font.name = 'Calibri'
        p_sub.font.size = PPt(13)
        p_sub.font.color.rgb = PRGBColor(148, 163, 184) # Muted slate
        
        # If Slide 07, embed the full-width AWS Architecture Diagram photo!
        if slide_data['num'] == '07' and os.path.exists('docs/report/figures/aws_architecture_diagram.jpg'):
            slide.shapes.add_picture('docs/report/figures/aws_architecture_diagram.jpg', PInches(1.0), PInches(2.2), width=PInches(11.333))
        else:
            # 3 Content Cards
            col_width = PInches(3.55)
            col_gap = PInches(0.35)
            top_pos = PInches(2.5)
            card_height = PInches(4.2)
            
            for idx, (card_title, card_desc) in enumerate(slide_data['cards']):
                left_pos = PInches(1.0) + idx * (col_width + col_gap)
                
                # Card background shape
                shape = slide.shapes.add_shape(
                    pptx.enum.shapes.MSO_SHAPE.ROUNDED_RECTANGLE,
                    left_pos, top_pos, col_width, card_height
                )
                shape.fill.solid()
                shape.fill.fore_color.rgb = PRGBColor(22, 30, 49) # Card slate
                shape.line.color.rgb = PRGBColor(56, 189, 248) if idx == 0 else PRGBColor(51, 65, 85)
                shape.line.width = PPt(1.2) if idx == 0 else PPt(0.8)
                
                # Card text
                tb_card = slide.shapes.add_textbox(left_pos + PInches(0.25), top_pos + PInches(0.3), col_width - PInches(0.5), card_height - PInches(0.6))
                tf = tb_card.text_frame
                tf.word_wrap = True
                
                p_ct = tf.paragraphs[0]
                p_ct.text = card_title
                p_ct.font.name = 'Calibri'
                p_ct.font.size = PPt(16)
                p_ct.font.bold = True
                p_ct.font.color.rgb = PRGBColor(6, 182, 212) if idx == 0 else PRGBColor(241, 245, 249)
                p_ct.space_after = PPt(12)
                
                p_cd = tf.add_paragraph()
                p_cd.text = card_desc
                p_cd.font.name = 'Calibri'
                p_cd.font.size = PPt(12)
                p_cd.font.color.rgb = PRGBColor(203, 213, 225)
                p_cd.line_spacing = 1.3
            
    prs.save(r'docs\presentation\executive_presentation.pptx')
    print(r'[OK] Generated docs\presentation\executive_presentation.pptx')


if __name__ == '__main__':
    generate_word_report()
    generate_pptx_deck()
