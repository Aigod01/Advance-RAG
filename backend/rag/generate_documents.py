"""
Generates 25+ realistic internal corporate markdown documents with tables,
quarterly breakdowns, executive memos, and operational analyses.
"""
import os

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "documents")
os.makedirs(DOCS_DIR, exist_ok=True)

DOCS = {
    "Q1_2025_Executive_Financial_Report.md": """# Apex Technologies Global - Q1 2025 Financial Performance Report
--- Page 1 ---
## Executive Summary
Apex Technologies Global delivered strong Q1 2025 financial results, driven by high demand for enterprise hardware and resilient consumer laptop shipments. Total revenue across all product lines reached $28.4M, representing a 6.2% year-over-year increase.

### Key Financial Highlights
| Metric | Q1 2024 | Q1 2025 | YoY Change |
| :--- | :--- | :--- | :--- |
| Total Revenue | $26.7M | $28.4M | +6.2% |
| Laptop Division Revenue | $13.5M | $14.1M | +4.4% |
| Desktop & Workstation Revenue | $7.8M | $8.2M | +5.1% |
| Gross Margin | 41.2% | 42.0% | +80 bps |
| Operating Profit | $5.9M | $6.4M | +8.5% |

--- Page 2 ---
## Segment Analysis
Enterprise accounts contributed 68% of laptop shipments in North America and EMEA. ApexBook Pro 16 maintained its position as the primary corporate choice for engineering and design teams.
""",

    "Q2_2025_Executive_Financial_Report.md": """# Apex Technologies Global - Q2 2025 Financial Performance Report
--- Page 1 ---
## Executive Summary
Q2 2025 marked our highest-performing quarter of the fiscal year. Record adoption of the ApexBook Pro 16 and ApexBook Air 14 drove laptop division revenue to an all-time peak of $14.2M.

### Product Category Breakdown
| Product Line | Units Sold | Average Selling Price (ASP) | Total Revenue | Gross Margin |
| :--- | :--- | :--- | :--- | :--- |
| ApexBook Pro 16 | 3,250 | $2,499 | $8.12M | 44.5% |
| ApexBook Air 14 | 3,820 | $1,299 | $4.96M | 41.0% |
| ApexBook Ultra 13 | 1,120 | $999 | $1.12M | 36.2% |
| Total Laptop Segment | 8,190 | - | $14.20M | 42.6% |
| Desktops & Accessories | - | - | $15.10M | 39.8% |
| Total Company Revenue | - | - | $29.30M | 41.2% |

--- Page 2 ---
## Regional Distribution
North America led growth with $15.4M in total revenue, followed by EMEA at $8.9M and APAC at $5.0M. Client feedback highlighted high satisfaction with thermal efficiency and battery life.
""",

    "Q3_2025_Executive_Financial_Report.md": """# Apex Technologies Global - Q3 2025 Financial Performance Report
--- Page 1 ---
## Executive Summary & Performance Discrepancy Analysis
In Q3 2025, company revenue experienced a localized contraction in our Laptop segment. Total laptop division revenue fell from $14.2M in Q2 2025 to $11.6M in Q3 2025, representing an 18.3% quarter-over-quarter decline.

### Q3 2025 Revenue Comparison
| Category | Q2 2025 Revenue | Q3 2025 Revenue | QoQ Change (%) | Status |
| :--- | :--- | :--- | :--- | :--- |
| ApexBook Pro 16 | $8.12M | $6.45M | -20.6% | Supplier Delay |
| ApexBook Air 14 | $4.96M | $4.10M | -17.3% | Procurement Pause |
| ApexBook Ultra 13 | $1.12M | $1.05M | -6.3% | Stable |
| Total Laptop Revenue | $14.20M | $11.60M | -18.3% | Decline |
| Total Company Revenue | $29.30M | $25.80M | -11.9% | Impacted |

--- Page 2 ---
## Internal Root Cause Identification
Detailed operational review identified three primary internal/partner drivers for the Q3 laptop revenue decline:
1. **Critical Component Shortage**: Our primary OLED display supplier (Shinra Micro) faced a 6-week factory retooling delay, forcing a backlog of 2,400 ApexBook Pro 16 units into late Q4.
2. **Enterprise Client Refresh Delay**: Key enterprise customers (including Wayne Enterprises and CyberDyne Systems) postponed fleet upgrades pending the announced Q4 Next-Gen processor transition.
3. **Regional APAC Logistics Bottleneck**: Typhoon disruptions in East Asian shipping lanes delayed container shipments to APAC regional distribution centers by 22 days.
""",

    "Q4_2025_Executive_Financial_Report.md": """# Apex Technologies Global - Q4 2025 Financial Performance Report
--- Page 1 ---
## Executive Summary
Q4 2025 exhibited a robust recovery across all product lines as supply chain bottlenecks were resolved. Laptop division revenue rebounded to $13.8M, supported by holiday seasonal demand and fulfillment of Q3 backorders.

### Full Year 2025 Financial Summary
| Quarter | Laptop Revenue | Total Revenue | Operating Margin |
| :--- | :--- | :--- | :--- |
| Q1 2025 | $14.1M | $28.4M | 22.5% |
| Q2 2025 | $14.2M | $29.3M | 23.8% |
| Q3 2025 | $11.6M | $25.8M | 18.1% |
| Q4 2025 | $13.8M | $28.9M | 21.9% |
| FY 2025 Total | $53.7M | $112.4M | 21.6% |
""",

    "Q1_2026_Executive_Financial_Report.md": """# Apex Technologies Global - Q1 2026 Financial Performance Report
--- Page 1 ---
## Overview
Q1 2026 demonstrated sustained momentum. Laptop revenue reached $14.5M, driven by new enterprise contract rollouts in EMEA and North America.
Gross margins improved to 43.1% following internal manufacturing cost reductions.
""",

    "Q2_2026_Executive_Financial_Report.md": """# Apex Technologies Global - Q2 2026 Financial Performance Report
--- Page 1 ---
## Overview
Q2 2026 laptop revenue totaled $14.8M. Enterprise workstation adoption grew 14% YoY. Supply chains remained fully operational with zero critical tier-1 component delays.
""",

    "Supply_Chain_Risk_Assessment_2025.md": """# Internal Audit: Supply Chain Risk & Vendor Dependencies (2025)
--- Page 1 ---
## Vendor Concentration Risks
An evaluation of our hardware manufacturing vendors revealed single-source dependency in two critical sub-assemblies:
- **Display Assemblies**: Shinra Micro provides 78% of high-refresh 16-inch panels.
- **Power Management ICs**: Tyrell BioTech / MicroDivision provides 65% of fast-charging controllers.

### Mitigation Strategies
To prevent recurring quarterly revenue dips like Q3 2025, Apex is onboarding secondary suppliers in Vietnam and India by Q1 2026.
""",

    "Laptop_Product_Line_Performance_Analysis_2025.md": """# Product Performance Review: ApexBook Family (2025)
--- Page 1 ---
## Product Lifecycle & RMA Metrics
| Model | Return Rate (RMA) | Customer Rating | Primary Defect Reported |
| :--- | :--- | :--- | :--- |
| ApexBook Pro 16 | 1.2% | 4.8 / 5.0 | Trackpad firmware latency (resolved v1.4) |
| ApexBook Air 14 | 1.8% | 4.6 / 5.0 | Port clearance |
| ApexBook Ultra 13 | 2.4% | 4.2 / 5.0 | Battery drain on standby |
| ApexStudio Max 16 | 0.9% | 4.9 / 5.0 | None reported |

Enterprise fleets exhibited low warranty defect rates of under 1.4% overall.
""",

    "ApexBook_Pro_16_Technical_Specifications_and_Pricing.md": """# ApexBook Pro 16 Specification & Tier Pricing Guide
--- Page 1 ---
## Hardware Specs
- Processor: Apex Silicon M4 Pro (14-Core CPU, 20-Core GPU)
- Memory: 32GB / 64GB Unified LPDDR5X
- Storage: 1TB / 2TB NVMe PCIe 4.0 SSD
- Display: 16.2-inch Liquid Mini-LED, 3456x2234, 120Hz ProMotion
- Retail Price: $2,499.00 USD
- Enterprise Tier Discount: 8% on volume >= 25 units; 12% on volume >= 100 units.
""",

    "ApexBook_Air_14_Customer_Feedback_and_RMA_Report.md": """# ApexBook Air 14 Quality Review and Customer Survey
--- Page 1 ---
## Summary
The ApexBook Air 14 remains the highest unit volume product in the Apex portfolio.
92% of corporate users rated portability and keyboard ergonomics as exceptional.
Minor complaints regarding external monitor dual-display support were addressed in the Q2 firmware patch.
""",

    "Regional_Market_Analysis_North_America_2025.md": """# Regional Market Review: North America Division (FY 2025)
--- Page 1 ---
## Market Share & Key Accounts
North America generated $58.2M (51.8%) of total company revenue.
Top corporate accounts: CyberDyne Systems, Wayne Enterprises, Stark Industries, Acme Corporation.
Enterprise budget freezes in August 2025 temporarily lowered Q3 sales by 19% across the East Coast territory.
""",

    "Regional_Market_Analysis_EMEA_2025.md": """# Regional Market Review: EMEA Division (FY 2025)
--- Page 1 ---
## European Enterprise Demand
EMEA division recorded $31.4M in FY 2025 revenue. Growth was driven by German and UK tech firms standardizing on Apex laptops.
Regulatory compliance for EU Ecodesign and USB-C standardization was completed ahead of schedule in Q1 2025.
""",

    "Regional_Market_Analysis_APAC_2025.md": """# Regional Market Review: APAC Division (FY 2025)
--- Page 1 ---
## APAC Expansion & Logistics
APAC generated $17.8M in revenue. Logistics disruptions in Singapore and Tokyo ports in August 2025 impacted Q3 deliveries, but fulfillment recovered fully by November 2025.
""",

    "Enterprise_Customer_Satisfaction_Survey_2025.md": """# Enterprise Customer Satisfaction & Retention Survey 2025
--- Page 1 ---
## Survey Metrics
- Overall Net Promoter Score (NPS): +68
- Hardware Reliability Score: 94 / 100
- Enterprise IT Deployment Ease: 91 / 100
- Contract Renewal Likelihood: 89%

Key feedback requested faster turnaround on customized bulk-order OS imaging.
""",

    "Competitive_Intelligence_Report_PC_and_Laptop_Market.md": """# Competitive Intelligence: PC & Laptop Hardware Sector (2025-2026)
--- Page 1 ---
## Industry Trend Overview
Across the broader PC and Laptop industry, global shipments declined by 4.2% in Q3 2025 due to macroeconomic tightening and high interest rates.
However, Apex Technologies' 18.3% decline in Q3 was significantly steeper than the general 4.2% industry contraction, proving that our drop was largely company-specific (driven by Shinra display bottlenecks and pending architecture upgrades) rather than purely macroeconomic.
""",

    "Enterprise_Hardware_Refresh_Cycle_Whitepaper.md": """# Enterprise Hardware Refresh Cycles: 3-Year vs 4-Year Depreciation
--- Page 1 ---
## Lifecycle Insights
Most Fortune 500 organizations have shifted from a 3-year refresh cycle to a 3.5-year cycle, creating periodic lulls before major chip architecture generations.
Apex recommended trade-in programs to smooth out purchase seasonality.
""",

    "Corporate_Discount_and_Pricing_Policy.md": """# Apex Global Corporate Pricing & Discount Matrix
--- Page 1 ---
## Volume Tier Guidelines
- Tier 1 (1-9 units): Standard List Price (0% discount)
- Tier 2 (10-49 units): 5% discount
- Tier 3 (50-199 units): 10% discount
- Tier 4 (200+ units): 15% discount + free docking stations
All discounts must be approved by regional sales directors.
""",

    "Apex_Warranty_and_Support_Service_Level_Agreement.md": """# Hardware Warranty and Enterprise Support SLA
--- Page 1 ---
## Standard SLA Terms
- Next-Business-Day Onsite Repair for Enterprise Tier contracts.
- 3-Year comprehensive parts and labor warranty included on all ApexBook Pro and ApexStation models.
- 24/7 dedicated IT support helpline with < 15 minute average response time.
""",

    "IT_Asset_Management_and_Depreciation_Policy.md": """# IT Asset Depreciation and Fleet Management Policy
--- Page 1 ---
## Financial Treatment
Laptops are depreciated on a straight-line basis over 36 months with a 10% residual value salvage rate.
Internal company laptops are retired after 3 years and recycled through certified e-waste partners.
""",

    "Product_Roadmap_2025_2027_Hardware_Division.md": """# Strategic Product Roadmap (2025 - 2027)
--- Page 1 ---
## Planned Releases
- Q4 2025: ApexBook Pro 16 Gen 2 (M4 Max chipset, Wi-Fi 7)
- Q2 2026: ApexBook Air 15 (Ultra-thin 1.1kg chassis)
- Q4 2026: ApexWorkstation AI Tower with dual dedicated neural accelerators
- Q2 2027: ApexFold Flexible OLED Tablet / Laptop Hybrid
""",

    "Manufacturing_Yield_and_Quality_Audit_Q3_2025.md": """# Internal Audit: Manufacturing Yield & Quality Control (Q3 2025)
--- Page 1 ---
## Production Yield Metrics
Overall factory yield for ApexBook Pro 16 dropped to 86.4% in July 2025 due to display panel alignment calibration errors at our Shenzhen facility.
Quality control protocols successfully prevented defective units from shipping to end customers.
Factory yield returned to 98.2% by September 2025 after optical sensor recalibration.
""",

    "Cybersecurity_and_Firmware_Update_Report_2025.md": """# Firmware Security & Trusted Platform Module (TPM) Compliance
--- Page 1 ---
## Security Highlights
All Apex 2025 hardware incorporates hardware-isolated Secure Enclave chips with zero known critical vulnerabilities.
Automated firmware update verification passed ISO/IEC 27001 compliance standards.
""",

    "Global_Logistics_and_Freight_Cost_Review_2025.md": """# Logistics & Air/Sea Freight Operational Report (2025)
--- Page 1 ---
## Shipping Cost Trends
Air freight rates increased 14% in Q3 2025, prompting a temporary shift to maritime shipping for accessory items.
Ocean container transit times averaged 24 days from assembly plants to Long Beach and Rotterdam.
""",

    "Semiconductor_Shortage_Impact_Analysis_2025.md": """# Special Assessment: Semiconductor & Silicon Wafer Availability
--- Page 1 ---
## Foundry Capacity
Foundry allocations for 3nm wafer production were secured through FY 2027.
Secondary silicon suppliers for power regulators and audio DACs were qualified in September 2025 to mitigate future disruptions.
""",

    "Annual_Sustainability_and_Hardware_Recycling_Report.md": """# Apex Global Sustainability & Environmental Impact Report (2025)
--- Page 1 ---
## Environmental Commitments
- 100% recycled aluminum chassis across the entire ApexBook product family.
- Packaging reduced by 35% with zero single-use plastics.
- Carbon neutral corporate operations achieved across North America and European facilities.
"""
}


def generate_all_documents():
    print(f"Generating {len(DOCS)} corporate internal documents in {DOCS_DIR}...")
    for filename, content in DOCS.items():
        filepath = os.path.join(DOCS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
    print(f"Successfully generated {len(DOCS)} documents.")


if __name__ == "__main__":
    generate_all_documents()
