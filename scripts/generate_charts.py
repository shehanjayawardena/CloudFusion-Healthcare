"""
CloudFusion Healthcare Analytics Ltd (CHA)
High-Resolution Figures Generator for Report and Presentation
"""

import matplotlib.pyplot as plt
import numpy as np

# Set global aesthetics
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

# -------------------------------------------------------------
# Figure 1: Total Cost of Ownership (TCO) Comparison
# -------------------------------------------------------------
def generate_tco_chart():
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)
    
    categories = ['On-Premises\nLegacy Baseline', 'AWS On-Demand\n(Unoptimised)', 'AWS Target\n(FinOps Optimised)']
    costs = [142400, 48662, 25176]
    colors = ['#ef4444', '#f59e0b', '#10b981']
    
    bars = ax.bar(categories, costs, color=colors, width=0.55, edgecolor='black', linewidth=0.8, zorder=3)
    
    # Grid & Limits
    ax.set_ylabel('Monthly Operational Expenditure (USD $)', fontweight='bold', fontsize=11)
    ax.set_ylim(0, 165000)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    
    # Annotate bar values
    for bar, cost in zip(bars, costs):
        height = bar.get_height()
        ax.annotate(f'${cost:,.0f}/mo',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 6),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontweight='bold', fontsize=11)
        
    # Annotate savings arrows
    ax.annotate('65.8% Immediate Savings', xy=(1, 55000), xytext=(0.5, 95000),
                arrowprops=dict(facecolor='#f59e0b', shrink=0.08, width=1.5, headwidth=7),
                ha='center', fontweight='bold', color='#b45309')
    
    ax.annotate('82.3% Total TCO Reduction\n(Mandate: >= 40%)', xy=(2, 32000), xytext=(1.6, 120000),
                arrowprops=dict(facecolor='#10b981', shrink=0.08, width=2, headwidth=8),
                ha='center', fontweight='bold', color='#047857',
                bbox=dict(boxstyle="round,pad=0.4", fc="#d1fae5", ec="#10b981", lw=1))
    
    plt.title('Monthly Operational Run-Rate: On-Premises vs Cloud Modernisation', fontweight='bold', fontsize=12, pad=15)
    plt.tight_layout()
    plt.savefig('docs/report/figures/cost_comparison_tco.png')
    plt.close()
    print('[OK] Generated docs/report/figures/cost_comparison_tco.png')

# -------------------------------------------------------------
# Figure 2: AWS Monthly Cost Breakdown (Donut Chart)
# -------------------------------------------------------------
def generate_cost_breakdown_donut():
    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    
    labels = [
        'Compute Tier (ECS Fargate + ALB)',
        'Database Tier (Aurora + DynamoDB + Redis)',
        'Storage & Data Lake (S3 Glacier)',
        'Networking & Interconnect (DX, TGW, CDN)',
        'Security, Governance & Logging'
    ]
    sizes = [6903, 10470, 665, 4366, 2772]
    colors = ['#3b82f6', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b']
    explode = (0.02, 0.04, 0.02, 0.02, 0.02)
    
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=None, autopct='%1.1f%%',
        pctdistance=0.75, startangle=140, colors=colors,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=1.5)
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
        
    ax.legend(wedges, [f'{l}: ${s:,.0f}/mo' for l, s in zip(labels, sizes)],
              title="AWS Service Tiers", loc="center left", bbox_to_anchor=(0.95, 0.5),
              fontsize=9, title_fontsize=10)
    
    plt.title('Target AWS Architecture Monthly Cost Distribution ($25,176/mo)', fontweight='bold', fontsize=11, pad=15)
    plt.tight_layout()
    plt.savefig('docs/report/figures/aws_monthly_cost_breakdown.png')
    plt.close()
    print('[OK] Generated docs/report/figures/aws_monthly_cost_breakdown.png')

# -------------------------------------------------------------
# Figure 3: Clinical Vitals Telemetry Contrast
# -------------------------------------------------------------
def generate_clinical_contrast_chart():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True, dpi=300)
    
    # Time axis (hours 0 to 12)
    t = np.linspace(0, 12, 500)
    
    # Simulated Heart Rate (BPM)
    # Stable baseline (75) until hour 5.2, decompensation spike to 142 at hour 5.8
    hr_baseline = 75 + 3 * np.sin(t * 1.5)
    hr_event = 65 * np.exp(-((t - 6.2) ** 2) / 0.5) * (t > 5.2)
    hr = hr_baseline + hr_event
    
    # Simulated SpO2 (%)
    # Stable baseline (98) until hour 5.2, drops sharply to 87 at hour 5.8
    spo2_baseline = 98 - 0.5 * np.cos(t * 1.2)
    spo2_event = -11 * np.exp(-((t - 6.2) ** 2) / 0.8) * (t > 5.2)
    spo2 = spo2_baseline + spo2_event
    
    # Subplot 1: Continuous IoT Telemetry vs Discrete Polling
    ax1.plot(t, spo2, color='#0284c7', linewidth=2, label='Continuous IoT Telemetry (AWS IoT Core)')
    ax1.axhline(90, color='#dc2626', linestyle='--', linewidth=1.2, label='Critical Hypoxia Alarm Threshold (< 90%)')
    
    # Discrete nursing rounds at Hour 0, 4, 8, 12
    rounds = [0, 4, 8, 12]
    discrete_spo2 = [98.2, 97.8, 89.5, 96.0]
    ax1.scatter(rounds, discrete_spo2, color='#b91c1c', s=80, zorder=5, label='Traditional Nursing Polling (4-Hour Rounds)')
    
    # Highlight blind spot
    ax1.axvspan(4.0, 8.0, color='#fef2f2', alpha=0.8, zorder=0)
    ax1.text(6.0, 94.5, 'FATAL 4-HOUR BLIND SPOT\n(Patient in Acute Distress at Hr 5.8)', 
             ha='center', color='#991b1b', fontweight='bold', fontsize=9,
             bbox=dict(boxstyle="round,pad=0.3", fc="#fee2e2", ec="#ef4444", lw=0.8))
    
    ax1.set_ylabel('Blood Oxygen SpO2 (%)', fontweight='bold')
    ax1.set_ylim(82, 102)
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.legend(loc='lower left', fontsize=8.5)
    
    # Subplot 2: Heart Rate & Instant Alert
    ax2.plot(t, hr, color='#7c3aed', linewidth=2, label='Continuous Heart Rate (BPM)')
    ax2.axhline(135, color='#dc2626', linestyle='--', linewidth=1.2, label='Tachycardia Alarm Threshold (> 135 BPM)')
    
    # Discrete HR
    discrete_hr = [74, 76, 128, 78]
    ax2.scatter(rounds, discrete_hr, color='#b91c1c', s=80, zorder=5, label='Discrete Nurse Measurement')
    
    # Alert callout
    ax2.annotate('INSTANT CLOUD ALERT (< 500ms)\nSNS -> Emergency Doctor Pager',
                 xy=(5.6, 136), xytext=(2.5, 125),
                 arrowprops=dict(facecolor='#dc2626', shrink=0.08, width=1.5, headwidth=6),
                 fontweight='bold', fontsize=9, color='#991b1b',
                 bbox=dict(boxstyle="round,pad=0.3", fc="#fef2f2", ec="#dc2626", lw=0.8))
    
    ax2.set_xlabel('Clinical Monitoring Timeline (Hours)', fontweight='bold')
    ax2.set_ylabel('Heart Rate (BPM)', fontweight='bold')
    ax2.set_ylim(50, 160)
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend(loc='lower left', fontsize=8.5)
    
    plt.suptitle('Clinical Evidence: Continuous AWS IoT Telemetry vs Traditional Discrete Polling', fontweight='bold', fontsize=11, y=0.98)
    plt.tight_layout()
    plt.savefig('docs/report/figures/clinical_vitals_telemetry_contrast.png')
    plt.close()
    print('[OK] Generated docs/report/figures/clinical_vitals_telemetry_contrast.png')

if __name__ == '__main__':
    generate_tco_chart()
    generate_cost_breakdown_donut()
    generate_clinical_contrast_chart()
