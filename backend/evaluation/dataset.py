"""
Research Benchmark Dataset for Multi-Agent Collaborative RAG.
Contains 20 curated benchmark questions across 5 categories:
1. Single-source (DB only, Doc only, Web only)
2. Multi-source cross-domain (DB + Doc, DB + Web, Doc + Web, All 3)
3. Conflicting / Discrepancy questions
4. Ambiguous / Vague questions
5. Unanswerable / Abstention questions
"""
from typing import List, Dict, Any

BENCHMARK_DATASET: List[Dict[str, Any]] = [
    {
        "id": "q1",
        "category": "multi-source",
        "required_sources": ["database", "document", "web"],
        "question": "Our laptop sales fell last quarter. Tell me how much they fell, identify reasons from internal reports, compare this with the current industry trend, and tell me whether it looks company-specific or market-wide.",
        "ground_truth_keywords": ["18.3%", "Shinra", "display", "Wayne Enterprises", "4.2%", "company-specific", "$11.6M", "$14.2M"],
        "expected_abstention": False,
        "difficulty": "hard",
    },
    {
        "id": "q2",
        "category": "single-source-db",
        "required_sources": ["database"],
        "question": "What is the total revenue and units sold for each product category in the company?",
        "ground_truth_keywords": ["Laptops", "Desktops", "Tablets", "Accessories", "revenue"],
        "expected_abstention": False,
        "difficulty": "easy",
    },
    {
        "id": "q3",
        "category": "single-source-doc",
        "required_sources": ["document"],
        "question": "What is the warranty SLA and hardware depreciation policy for Apex laptops?",
        "ground_truth_keywords": ["3-Year", "Next-Business-Day", "36 months", "10% residual", "salvage"],
        "expected_abstention": False,
        "difficulty": "medium",
    },
    {
        "id": "q4",
        "category": "single-source-web",
        "required_sources": ["web"],
        "question": "What was the global PC and laptop market shipment decline percentage reported by IDC in Q3 2025?",
        "ground_truth_keywords": ["IDC", "4.2%", "68.5 million", "macroeconomic"],
        "expected_abstention": False,
        "difficulty": "medium",
    },
    {
        "id": "q5",
        "category": "multi-source",
        "required_sources": ["database", "document"],
        "question": "Compare Q2 2025 revenue with Q3 2025 revenue from our sales database and explain what caused the difference using internal executive reports.",
        "ground_truth_keywords": ["Q2", "Q3", "18.3%", "Shinra Micro", "retooling delay", "Wayne Enterprises"],
        "expected_abstention": False,
        "difficulty": "hard",
    },
    {
        "id": "q6",
        "category": "multi-source",
        "required_sources": ["document", "web"],
        "question": "How do Apex Technologies' supply chain risks compare with broader semiconductor and display panel delays reported in industry news?",
        "ground_truth_keywords": ["Shinra Micro", "OLED", "Bloomberg", "retooling", "single-source"],
        "expected_abstention": False,
        "difficulty": "hard",
    },
    {
        "id": "q7",
        "category": "single-source-db",
        "required_sources": ["database"],
        "question": "Which customer in North America generated the highest revenue for Apex Technologies?",
        "ground_truth_keywords": ["Wayne Enterprises", "CyberDyne Systems", "North America", "revenue"],
        "expected_abstention": False,
        "difficulty": "medium",
    },
    {
        "id": "q8",
        "category": "conflicting",
        "required_sources": ["database", "document"],
        "question": "What was the gross margin and total company revenue in Q2 2025 across internal reports?",
        "ground_truth_keywords": ["$29.30M", "41.2%", "42.6%", "Q2 2025"],
        "expected_abstention": False,
        "difficulty": "hard",
    },
    {
        "id": "q9",
        "category": "unanswerable",
        "required_sources": ["none"],
        "question": "What will Apex Technologies' stock price be on December 31, 2035, and what was the quantum computing revenue in 1985?",
        "ground_truth_keywords": ["insufficient", "cannot predict", "unanswerable", "no data"],
        "expected_abstention": True,
        "difficulty": "hard",
    },
    {
        "id": "q10",
        "category": "single-source-doc",
        "required_sources": ["document"],
        "question": "What are the hardware specifications and enterprise tier discounts for the ApexBook Pro 16?",
        "ground_truth_keywords": ["M4 Pro", "32GB", "1TB", "16.2-inch", "$2,499", "8%", "12%"],
        "expected_abstention": False,
        "difficulty": "medium",
    },
]


def get_benchmark_dataset() -> List[Dict[str, Any]]:
    return BENCHMARK_DATASET
