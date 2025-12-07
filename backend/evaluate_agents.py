#!/usr/bin/env python3
"""
Agent Evaluation Script for Threat Explorer

This script evaluates all three agents (LLM, ReACT, Multi-Agent) against a curated
set of test questions to compare their performance on key metrics including:
- Query validity and pattern matching
- Visualization correctness
- Response time and quality
- Token usage and cost analysis

Usage:
    python evaluate_agents.py
    python evaluate_agents.py --agents llm react  # Test only LLM and ReACT agents
    python evaluate_agents.py --agents multi-agent # Test only Multi-Agent
    python evaluate_agents.py --html my_report.html --report my_report.md
"""

import os
import sys
import json
import time
import argparse
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import LLMAgent, ReACTAgent, MultiAgent, Message
from db.database import db

# Load environment variables
load_dotenv()


# ============================================================================
# EVALUATION DATASET
# ============================================================================

EVALUATION_QUESTIONS = [
    # ==================== SIMPLE QUERIES ====================
    {
        "id": "q1",
        "question": "Show me the top 5 attack types",
        "category": "simple_query",
        "expected_query_pattern": r"SELECT.*Attack Type.*COUNT.*GROUP BY.*LIMIT\s+5",
        "expected_data_fields": ["Attack Type"],
        "expected_visualization": "db-chart",
        "rubric": {
            "query_validity": "Must generate valid SQL with GROUP BY and LIMIT 5",
            "correctness": "Must return top 5 attack types by count",
            "visualization": "Should use bar chart (db-chart) for aggregated data"
        }
    },
    {
        "id": "q2",
        "question": "What are the severity levels in the database?",
        "category": "simple_query",
        "expected_query_pattern": r'SELECT.*"Severity Level".*GROUP BY',
        "expected_data_fields": ["Severity Level"],
        "expected_visualization": "db-pie",
        "rubric": {
            "query_validity": "Must quote 'Severity Level' with double quotes",
            "correctness": "Must return all severity levels with counts",
            "visualization": "Should use pie chart for distribution"
        }
    },
    {
        "id": "q3",
        "question": "List all unique protocols in the attacks database",
        "category": "simple_query",
        "expected_query_pattern": r'SELECT.*DISTINCT.*"Protocol"',
        "expected_data_fields": ["Protocol"],
        "expected_visualization": "db-table",
        "rubric": {
            "query_validity": "Must use DISTINCT or GROUP BY for unique values",
            "correctness": "Must return unique protocols",
            "visualization": "Should use table or chart"
        }
    },

    # # ==================== FILTERED QUERIES ====================
    # {
    #     "id": "q4",
    #     "question": "Show me recent malware attacks with their source IPs",
    #     "category": "filtered_query",
    #     "expected_query_pattern": r'SELECT.*"Attack Type".*=.*[\'"]Malware[\'"].*LIMIT',
    #     "expected_data_fields": ["Attack Type", "Source IP Address"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must filter by Attack Type = 'Malware'",
    #         "correctness": "Must return malware attacks with source IPs",
    #         "visualization": "Should use table for detailed records"
    #     }
    # },
    # {
    #     "id": "q5",
    #     "question": "Find all high severity intrusion attempts",
    #     "category": "filtered_query",
    #     "expected_query_pattern": r'SELECT.*"Severity Level".*High.*"Attack Type".*Intrusion',
    #     "expected_data_fields": ["Severity Level", "Attack Type"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must filter by both Severity Level and Attack Type",
    #         "correctness": "Must return high severity intrusion attacks",
    #         "visualization": "Should use table for detailed data"
    #     }
    # },
    # {
    #     "id": "q6",
    #     "question": "Show me attacks using TCP protocol",
    #     "category": "filtered_query",
    #     "expected_query_pattern": r'SELECT.*"Protocol".*=.*[\'"]TCP[\'"]',
    #     "expected_data_fields": ["Protocol"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must filter by Protocol = 'TCP'",
    #         "correctness": "Must return TCP protocol attacks",
    #         "visualization": "Should use table"
    #     }
    # },

    # # ==================== AGGREGATION & RANKING ====================
    # {
    #     "id": "q7",
    #     "question": "Which protocols are targeted most frequently?",
    #     "category": "aggregation",
    #     "expected_query_pattern": r'SELECT.*"Protocol".*COUNT.*GROUP BY.*ORDER BY.*DESC',
    #     "expected_data_fields": ["Protocol"],
    #     "expected_visualization": "db-chart",
    #     "rubric": {
    #         "query_validity": "Must quote Protocol, use GROUP BY and ORDER BY",
    #         "correctness": "Must return protocols ranked by frequency",
    #         "visualization": "Should use bar chart for ranking"
    #     }
    # },
    # {
    #     "id": "q8",
    #     "question": "What are the top 3 source IPs with the most attacks?",
    #     "category": "aggregation",
    #     "expected_query_pattern": r'SELECT.*"Source IP Address".*COUNT.*GROUP BY.*LIMIT\s+3',
    #     "expected_data_fields": ["Source IP Address"],
    #     "expected_visualization": "db-chart",
    #     "rubric": {
    #         "query_validity": "Must quote Source IP Address, GROUP BY, LIMIT 3",
    #         "correctness": "Must return top 3 IPs by attack count",
    #         "visualization": "Should use bar chart"
    #     }
    # },
    # {
    #     "id": "q9",
    #     "question": "Count attacks by destination port",
    #     "category": "aggregation",
    #     "expected_query_pattern": r'SELECT.*"Destination Port".*COUNT.*GROUP BY',
    #     "expected_data_fields": ["Destination Port"],
    #     "expected_visualization": "db-chart",
    #     "rubric": {
    #         "query_validity": "Must quote Destination Port and use GROUP BY",
    #         "correctness": "Must return port-based attack counts",
    #         "visualization": "Should use bar chart"
    #     }
    # },
    # {
    #     "id": "q10",
    #     "question": "What are the top 10 most targeted destination IPs?",
    #     "category": "aggregation",
    #     "expected_query_pattern": r'SELECT.*"Destination IP Address".*COUNT.*GROUP BY.*LIMIT\s+10',
    #     "expected_data_fields": ["Destination IP Address"],
    #     "expected_visualization": "db-chart",
    #     "rubric": {
    #         "query_validity": "Must use GROUP BY and LIMIT 10",
    #         "correctness": "Must return top 10 destination IPs",
    #         "visualization": "Should use bar chart"
    #     }
    # },

    # # ==================== COMPARISON QUERIES ====================
    # {
    #     "id": "q11",
    #     "question": "Compare the frequency of DDoS attacks vs Intrusion attacks",
    #     "category": "comparison",
    #     "expected_query_pattern": r'SELECT.*"Attack Type".*COUNT.*WHERE.*IN.*DDoS.*Intrusion',
    #     "expected_data_fields": ["Attack Type"],
    #     "expected_visualization": "db-chart",
    #     "rubric": {
    #         "query_validity": "Must filter for both DDoS and Intrusion",
    #         "correctness": "Must return counts for both attack types",
    #         "visualization": "Should use bar chart for comparison"
    #     }
    # },
    # {
    #     "id": "q12",
    #     "question": "Compare critical vs low severity attack volumes",
    #     "category": "comparison",
    #     "expected_query_pattern": r'SELECT.*"Severity Level".*COUNT.*WHERE.*IN.*Critical.*Low',
    #     "expected_data_fields": ["Severity Level"],
    #     "expected_visualization": "db-chart",
    #     "rubric": {
    #         "query_validity": "Must filter for Critical and Low severity",
    #         "correctness": "Must return counts for both severity levels",
    #         "visualization": "Should use bar chart or pie chart"
    #     }
    # },

    # # ==================== COMPLEX FILTERS ====================
    # {
    #     "id": "q13",
    #     "question": "Show me critical severity attacks from the last week",
    #     "category": "complex_filter",
    #     "expected_query_pattern": r'SELECT.*"Severity Level".*=.*Critical.*"Timestamp"',
    #     "expected_data_fields": ["Severity Level", "Timestamp"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must filter by Severity Level and Timestamp",
    #         "correctness": "Must return critical severity attacks with timestamps",
    #         "visualization": "Should use table for detailed time-based data"
    #     }
    # },
    # {
    #     "id": "q14",
    #     "question": "Find all malware attacks on port 443 with high severity",
    #     "category": "complex_filter",
    #     "expected_query_pattern": r'SELECT.*"Attack Type".*Malware.*"Destination Port".*443.*"Severity Level".*High',
    #     "expected_data_fields": ["Attack Type", "Destination Port", "Severity Level"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must filter by attack type, port, and severity",
    #         "correctness": "Must return matching attacks with all conditions",
    #         "visualization": "Should use table for multi-field data"
    #     }
    # },
    # {
    #     "id": "q15",
    #     "question": "Show reconnaissance attacks using ICMP protocol with medium or high severity",
    #     "category": "complex_filter",
    #     "expected_query_pattern": r'SELECT.*"Attack Type".*Reconnaissance.*"Protocol".*ICMP.*"Severity Level"',
    #     "expected_data_fields": ["Attack Type", "Protocol", "Severity Level"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must filter by attack type, protocol, and severity range",
    #         "correctness": "Must return matching attacks",
    #         "visualization": "Should use table"
    #     }
    # },

    # # ==================== TIME-BASED QUERIES ====================
    # {
    #     "id": "q16",
    #     "question": "Show me the most recent 20 attacks",
    #     "category": "time_based",
    #     "expected_query_pattern": r'SELECT.*ORDER BY.*"Timestamp".*DESC.*LIMIT\s+20',
    #     "expected_data_fields": ["Timestamp"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must ORDER BY Timestamp DESC and LIMIT 20",
    #         "correctness": "Must return 20 most recent attacks",
    #         "visualization": "Should use table for time-series data"
    #     }
    # },
    # {
    #     "id": "q17",
    #     "question": "What attacks occurred in 2023?",
    #     "category": "time_based",
    #     "expected_query_pattern": r'SELECT.*"Timestamp".*2023',
    #     "expected_data_fields": ["Timestamp"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must filter by year 2023",
    #         "correctness": "Must return attacks from 2023",
    #         "visualization": "Should use table or chart"
    #     }
    # },

    # # ==================== STATISTICAL QUERIES ====================
    # {
    #     "id": "q18",
    #     "question": "What percentage of attacks are critical severity?",
    #     "category": "statistical",
    #     "expected_query_pattern": r'SELECT.*"Severity Level".*COUNT',
    #     "expected_data_fields": ["Severity Level"],
    #     "expected_visualization": "db-pie",
    #     "rubric": {
    #         "query_validity": "Must aggregate by severity level",
    #         "correctness": "Must show distribution allowing percentage calculation",
    #         "visualization": "Should use pie chart for percentage distribution"
    #     }
    # },
    # {
    #     "id": "q19",
    #     "question": "Show the distribution of attack types",
    #     "category": "statistical",
    #     "expected_query_pattern": r'SELECT.*"Attack Type".*COUNT.*GROUP BY',
    #     "expected_data_fields": ["Attack Type"],
    #     "expected_visualization": "db-pie",
    #     "rubric": {
    #         "query_validity": "Must use GROUP BY for distribution",
    #         "correctness": "Must return all attack types with counts",
    #         "visualization": "Should use pie chart for distribution"
    #     }
    # },

    # # ==================== NETWORK ANALYSIS ====================
    # {
    #     "id": "q20",
    #     "question": "Which source IPs have attacked multiple destination IPs?",
    #     "category": "network_analysis",
    #     "expected_query_pattern": r'SELECT.*"Source IP Address".*COUNT.*DISTINCT.*"Destination IP Address"',
    #     "expected_data_fields": ["Source IP Address"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must count distinct destination IPs per source",
    #         "correctness": "Must identify sources with multiple targets",
    #         "visualization": "Should use table or chart"
    #     }
    # },
    # {
    #     "id": "q21",
    #     "question": "Show all attacks from internal network segments",
    #     "category": "network_analysis",
    #     "expected_query_pattern": r'SELECT.*"Network Segment"',
    #     "expected_data_fields": ["Network Segment"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must filter or group by Network Segment",
    #         "correctness": "Must return network segment information",
    #         "visualization": "Should use table or chart"
    #     }
    # },

    # # ==================== GENERAL KNOWLEDGE (NO DATABASE) ====================
    # {
    #     "id": "q22",
    #     "question": "What is a SQL injection attack?",
    #     "category": "general_knowledge",
    #     "expected_query_pattern": None,
    #     "expected_data_fields": [],
    #     "expected_visualization": None,
    #     "rubric": {
    #         "query_validity": "Should not query database",
    #         "correctness": "Must provide accurate definition of SQL injection",
    #         "visualization": "Should not generate visualizations"
    #     }
    # },
    # {
    #     "id": "q23",
    #     "question": "Explain what a DDoS attack is",
    #     "category": "general_knowledge",
    #     "expected_query_pattern": None,
    #     "expected_data_fields": [],
    #     "expected_visualization": None,
    #     "rubric": {
    #         "query_validity": "Should not query database",
    #         "correctness": "Must provide accurate DDoS explanation",
    #         "visualization": "Should not generate visualizations"
    #     }
    # },
    # {
    #     "id": "q24",
    #     "question": "What are the main differences between IDS and IPS?",
    #     "category": "general_knowledge",
    #     "expected_query_pattern": None,
    #     "expected_data_fields": [],
    #     "expected_visualization": None,
    #     "rubric": {
    #         "query_validity": "Should not query database",
    #         "correctness": "Must explain IDS vs IPS correctly",
    #         "visualization": "Should not generate visualizations"
    #     }
    # },
    # {
    #     "id": "q25",
    #     "question": "How can I prevent cross-site scripting (XSS) attacks?",
    #     "category": "general_knowledge",
    #     "expected_query_pattern": None,
    #     "expected_data_fields": [],
    #     "expected_visualization": None,
    #     "rubric": {
    #         "query_validity": "Should not query database",
    #         "correctness": "Must provide XSS prevention best practices",
    #         "visualization": "Should not generate visualizations"
    #     }
    # },

    # # ==================== EDGE CASES & ADVERSARIAL ====================
    # {
    #     "id": "q26",
    #     "question": "Show me attacks",
    #     "category": "ambiguous",
    #     "expected_query_pattern": r'SELECT.*FROM.*attacks.*LIMIT',
    #     "expected_data_fields": [],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must generate valid query despite vague request",
    #         "correctness": "Should return sample attacks with LIMIT clause",
    #         "visualization": "Should use table"
    #     }
    # },
    # {
    #     "id": "q27",
    #     "question": "What can you tell me about the data?",
    #     "category": "ambiguous",
    #     "expected_query_pattern": r'SELECT.*FROM.*attacks.*LIMIT',
    #     "expected_data_fields": [],
    #     "expected_visualization": None,
    #     "rubric": {
    #         "query_validity": "Should provide schema info or sample data",
    #         "correctness": "Should give overview of available data",
    #         "visualization": "May or may not visualize"
    #     }
    # },
    # {
    #     "id": "q28",
    #     "question": "Find attacks with anomaly score above 0.8",
    #     "category": "advanced_filter",
    #     "expected_query_pattern": r'SELECT.*"Anomaly Scores".*>.*0\.8',
    #     "expected_data_fields": ["Anomaly Scores"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must filter by Anomaly Scores > 0.8",
    #         "correctness": "Must return high anomaly score attacks",
    #         "visualization": "Should use table"
    #     }
    # },
    # {
    #     "id": "q29",
    #     "question": "Show attacks with malware indicators present",
    #     "category": "advanced_filter",
    #     "expected_query_pattern": r'SELECT.*"Malware Indicators"',
    #     "expected_data_fields": ["Malware Indicators"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must filter or select Malware Indicators",
    #         "correctness": "Must return attacks with malware indicators",
    #         "visualization": "Should use table"
    #     }
    # },
    # {
    #     "id": "q30",
    #     "question": "List all attacks where action taken was 'Blocked'",
    #     "category": "filtered_query",
    #     "expected_query_pattern": r'SELECT.*"Action Taken".*=.*[\'"]Blocked[\'"]',
    #     "expected_data_fields": ["Action Taken"],
    #     "expected_visualization": "db-table",
    #     "rubric": {
    #         "query_validity": "Must filter by Action Taken = 'Blocked'",
    #         "correctness": "Must return blocked attacks",
    #         "visualization": "Should use table"
    #     }
    # }
]


# ============================================================================
# EVALUATION FUNCTIONS
# ============================================================================

def extract_sql_query(response: str) -> str:
    """Extract SQL query from agent response"""
    import re

    # Look for SQL code blocks
    sql_pattern = r'```sql\s*(.*?)\s*```'
    matches = re.findall(sql_pattern, response, re.DOTALL | re.IGNORECASE)

    if matches:
        return matches[0].strip()

    # Fallback: look for SELECT statements
    select_pattern = r'(SELECT\s+.*?(?:;|$))'
    matches = re.findall(select_pattern, response, re.DOTALL | re.IGNORECASE)

    if matches:
        return matches[0].strip()

    return ""


def validate_sql_query(query: str) -> Dict[str, Any]:
    """Validate if SQL query is syntactically correct"""
    if not query:
        return {"valid": False, "error": "No query found"}

    # Try to execute the query
    try:
        db.query(query)
        return {"valid": True, "error": None}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def check_query_pattern(query: str, expected_pattern: str) -> bool:
    """Check if query matches expected pattern"""
    if not expected_pattern:
        return True

    import re
    return bool(re.search(expected_pattern, query, re.IGNORECASE | re.DOTALL))


def detect_visualization_type(response: str) -> str:
    """Detect which visualization format is used"""
    if "```db-table" in response or '"columns"' in response:
        return "db-table"
    elif "```db-chart" in response or ('"xKey"' in response and '"yKey"' in response):
        return "db-chart"
    elif "```db-pie" in response or ('"nameKey"' in response and '"valueKey"' in response):
        return "db-pie"
    return "none"


def score_response(response: str, question: Dict[str, Any], usage: Dict[str, int] = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Score a single agent response"""
    scores = {
        "query_validity": 0,
        "query_pattern_match": 0,
        "visualization_correctness": 0,
        "response_length": len(response),
        "has_recommendations": 0,
        "input_tokens": usage.get("prompt_tokens", 0) if usage else 0,
        "output_tokens": usage.get("completion_tokens", 0) if usage else 0,
        "total_tokens": usage.get("total_tokens", 0) if usage else 0
    }

    # Extract and validate SQL query
    sql_query = extract_sql_query(response)

    # If no SQL found in response text, check metadata (for tool-using agents like ReACT)
    if not sql_query and metadata and "sql_queries" in metadata and metadata["sql_queries"]:
        # Use the first SQL query from the metadata
        sql_query = metadata["sql_queries"][0]

    if question["expected_query_pattern"]:
        # This question expects a database query
        if sql_query:
            validation = validate_sql_query(sql_query)
            scores["query_validity"] = 1 if validation["valid"] else 0
            scores["query_error"] = validation.get("error")

            # Check if query matches expected pattern
            if check_query_pattern(sql_query, question["expected_query_pattern"]):
                scores["query_pattern_match"] = 1
        else:
            scores["query_validity"] = 0
            scores["query_error"] = "No SQL query found in response"
    else:
        # This question should NOT query database
        if not sql_query:
            scores["query_validity"] = 1  # Correctly didn't query
        else:
            scores["query_validity"] = 0  # Incorrectly queried database

    # Check visualization format
    viz_type = detect_visualization_type(response)
    expected_viz = question.get("expected_visualization")

    if expected_viz:
        scores["visualization_correctness"] = 1 if viz_type == expected_viz else 0
        scores["visualization_type"] = viz_type
    else:
        # No visualization expected
        scores["visualization_correctness"] = 1 if viz_type == "none" else 0
        scores["visualization_type"] = viz_type

    # Check for recommendations
    if any(keyword in response.lower() for keyword in ["recommend", "should", "consider", "best practice"]):
        scores["has_recommendations"] = 1

    return scores


def evaluate_agent(agent_name: str, agent, questions: List[Dict], enable_viz: bool = True) -> Dict[str, Any]:
    """Evaluate a single agent on all questions"""
    print(f"\n{'='*80}")
    print(f"Evaluating {agent_name} (Visualizations: {'ON' if enable_viz else 'OFF'})")
    print(f"{'='*80}")

    results = {
        "agent_name": agent_name,
        "visualizations_enabled": enable_viz,
        "total_questions": len(questions),
        "responses": [],
        "aggregate_scores": {},
        "total_time": 0
    }

    for i, question_data in enumerate(questions, 1):
        question = question_data["question"]
        print(f"\n[{i}/{len(questions)}] {question}")

        # Prepare messages
        messages = [Message(role="user", content=question)]

        # Time the response
        start_time = time.time()

        try:
            response = agent.chat(
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                enable_visualizations=enable_viz
            )

            elapsed_time = time.time() - start_time
            response_text = response.message.content

            # Extract token usage for display
            tokens_used = response.usage.get("total_tokens", 0) if response.usage else 0
            print(f"   ✓ Response received ({elapsed_time:.2f}s, {tokens_used} tokens)")

            # Score the response
            scores = score_response(response_text, question_data, response.usage, response.metadata)

            result = {
                "question_id": question_data["id"],
                "question": question,
                "category": question_data["category"],
                "response": response_text,
                "response_time": elapsed_time,
                "scores": scores,
                "metadata": response.metadata
            }

            results["responses"].append(result)
            results["total_time"] += elapsed_time

        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            results["responses"].append({
                "question_id": question_data["id"],
                "question": question,
                "category": question_data["category"],
                "error": str(e),
                "response_time": time.time() - start_time
            })

    # Calculate aggregate scores
    valid_responses = [r for r in results["responses"] if "error" not in r]

    if valid_responses:
        results["aggregate_scores"] = {
            "query_validity_rate": sum(r["scores"]["query_validity"] for r in valid_responses) / len(valid_responses),
            "query_pattern_match_rate": sum(r["scores"]["query_pattern_match"] for r in valid_responses) / len(valid_responses),
            "visualization_correctness_rate": sum(r["scores"]["visualization_correctness"] for r in valid_responses) / len(valid_responses),
            "avg_response_time": results["total_time"] / len(valid_responses),
            "avg_response_length": sum(r["scores"]["response_length"] for r in valid_responses) / len(valid_responses),
            "recommendations_rate": sum(r["scores"]["has_recommendations"] for r in valid_responses) / len(valid_responses),
            "error_rate": (len(results["responses"]) - len(valid_responses)) / len(results["responses"]),
            "total_input_tokens": sum(r["scores"]["input_tokens"] for r in valid_responses),
            "total_output_tokens": sum(r["scores"]["output_tokens"] for r in valid_responses),
            "total_tokens": sum(r["scores"]["total_tokens"] for r in valid_responses),
            "avg_input_tokens": sum(r["scores"]["input_tokens"] for r in valid_responses) / len(valid_responses),
            "avg_output_tokens": sum(r["scores"]["output_tokens"] for r in valid_responses) / len(valid_responses),
            "avg_total_tokens": sum(r["scores"]["total_tokens"] for r in valid_responses) / len(valid_responses)
        }

        # Print summary for this agent
        print(f"\n{'-'*80}")
        print(f"Agent Summary:")
        print(f"  Total Tokens: {results['aggregate_scores']['total_tokens']:,}")
        print(f"  Avg Tokens/Query: {results['aggregate_scores']['avg_total_tokens']:.0f}")
        print(f"  Total Time: {results['total_time']:.2f}s")
        print(f"{'-'*80}")

    return results


def calculate_cost(input_tokens: int, output_tokens: int, model: str = "gpt-4o-mini") -> float:
    """Calculate estimated cost based on token usage"""
    # Pricing per 1M tokens (as of 2024)
    pricing = {
        "gpt-4o-mini": {"input": 0.150, "output": 0.600},  # per 1M tokens
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50}
    }

    model_pricing = pricing.get(model, pricing["gpt-4o-mini"])
    input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (output_tokens / 1_000_000) * model_pricing["output"]
    return input_cost + output_cost


def generate_html_report(all_results: List[Dict], output_file: str):
    """Generate an interactive HTML report with charts"""

    # Prepare summary data
    total_questions = all_results[0]['total_questions'] if all_results else 0
    summary = {
        "total_questions": total_questions,
        "total_configurations": len(all_results),
        "evaluation_date": datetime.now().isoformat()
    }

    # Transform results to match expected format
    formatted_results = []
    for result in all_results:
        formatted_results.append({
            "agent_name": result["agent_name"],
            "agent_type": result["agent_name"].lower().replace("-", "_"),
            "visualizations_enabled": result["visualizations_enabled"],
            "avg_response_time": result["aggregate_scores"]["avg_response_time"],
            "aggregate_scores": result["aggregate_scores"],
            "responses": result["responses"]
        })

    evaluation_data = {
        "summary": summary,
        "results": formatted_results
    }

    # HTML template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Evaluation Results - Threat Explorer</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header p {{
            font-size: 1.1rem;
            opacity: 0.95;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 50px;
        }}

        .section-title {{
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 25px;
            color: #2d3748;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
        }}

        .metric-card h3 {{
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            opacity: 0.9;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }}

        .metric-card .value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .metric-card .label {{
            font-size: 0.85rem;
            opacity: 0.8;
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }}

        .comparison-table thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        .comparison-table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .comparison-table td {{
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
        }}

        .comparison-table tbody tr:hover {{
            background: #f7fafc;
        }}

        .agent-label {{
            font-weight: 600;
            color: #2d3748;
        }}

        .score {{
            font-weight: 600;
            font-size: 1.1rem;
        }}

        .score.high {{
            color: #48bb78;
        }}

        .score.medium {{
            color: #ed8936;
        }}

        .score.low {{
            color: #f56565;
        }}

        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }}

        .chart-wrapper {{
            position: relative;
            height: 400px;
        }}

        .question-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
        }}

        .question-card h3 {{
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.1rem;
        }}

        .question-card .question-text {{
            color: #4a5568;
            font-style: italic;
            margin-bottom: 15px;
            padding: 10px;
            background: #f7fafc;
            border-radius: 4px;
        }}

        .agent-response {{
            margin-bottom: 15px;
            padding: 15px;
            background: #f7fafc;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        }}

        .agent-response-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }}

        .agent-response-header h4 {{
            color: #2d3748;
            margin: 0;
            font-size: 1rem;
        }}

        .score-badges {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .score-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .score-badge.success {{
            background: #48bb78;
            color: white;
        }}

        .score-badge.warning {{
            background: #ed8936;
            color: white;
        }}

        .score-badge.error {{
            background: #f56565;
            color: white;
        }}

        .score-badge.info {{
            background: #667eea;
            color: white;
        }}

        .metrics-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}

        .metric-item {{
            display: flex;
            flex-direction: column;
        }}

        .metric-item .label {{
            font-size: 0.75rem;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .metric-item .value {{
            font-size: 1.1rem;
            color: #2d3748;
            font-weight: 600;
        }}

        .category-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}

        .category-card h3 {{
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.2rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}

        .category-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .stat-box {{
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 6px;
        }}

        .stat-box h4 {{
            font-size: 0.85rem;
            opacity: 0.9;
            margin-bottom: 8px;
        }}

        .stat-box .value {{
            font-size: 1.8rem;
            font-weight: 700;
        }}

        .response-preview {{
            margin-top: 10px;
            padding: 10px;
            background: white;
            border-radius: 4px;
            font-size: 0.9rem;
            color: #4a5568;
            max-height: 100px;
            overflow: hidden;
            position: relative;
        }}

        .response-preview::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 30px;
            background: linear-gradient(transparent, white);
        }}

        .expand-btn {{
            margin-top: 5px;
            padding: 6px 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: background 0.2s;
        }}

        .expand-btn:hover {{
            background: #5568d3;
        }}

        .response-preview.expanded {{
            max-height: none;
        }}

        .response-preview.expanded::after {{
            display: none;
        }}

        .winner-badge {{
            background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
            color: white;
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Threat Explorer Agent Evaluation</h1>
            <p>Comprehensive Performance Analysis & Comparison</p>
        </div>

        <div class="content">
            <!-- Overview Metrics -->
            <div class="section">
                <h2 class="section-title">📊 Overview</h2>
                <div id="overview-metrics"></div>
            </div>

            <!-- Performance Comparison Table -->
            <div class="section">
                <h2 class="section-title">📈 Performance Comparison</h2>
                <div id="comparison-table"></div>
            </div>

            <!-- Charts -->
            <div class="section">
                <h2 class="section-title">📉 Performance Metrics</h2>
                <div class="chart-container">
                    <h3 style="margin-bottom: 20px; color: #2d3748;">Query Validity & Pattern Match Rates</h3>
                    <div class="chart-wrapper">
                        <canvas id="validityChart"></canvas>
                    </div>
                </div>

                <div class="chart-container">
                    <h3 style="margin-bottom: 20px; color: #2d3748;">Token Usage Comparison</h3>
                    <div class="chart-wrapper">
                        <canvas id="tokenChart"></canvas>
                    </div>
                </div>

                <div class="chart-container">
                    <h3 style="margin-bottom: 20px; color: #2d3748;">Response Time Analysis</h3>
                    <div class="chart-wrapper">
                        <canvas id="timeChart"></canvas>
                    </div>
                </div>

                <div class="chart-container">
                    <h3 style="margin-bottom: 20px; color: #2d3748;">Cost Analysis</h3>
                    <div class="chart-wrapper">
                        <canvas id="costChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Cost Analysis Table -->
            <div class="section">
                <h2 class="section-title">💰 Cost Analysis</h2>
                <div id="cost-table"></div>
            </div>

            <!-- Question-by-Question Results -->
            <div class="section">
                <h2 class="section-title">📋 Detailed Results by Question</h2>
                <div id="question-results"></div>
            </div>

            <!-- Performance by Category -->
            <div class="section">
                <h2 class="section-title">📂 Performance by Category</h2>
                <div id="category-results"></div>
            </div>
        </div>
    </div>

    <script>
        const evaluationData = {json.dumps(evaluation_data, indent=2)};

        // Helper function to get score class
        function getScoreClass(value) {{
            if (value >= 0.8) return 'high';
            if (value >= 0.5) return 'medium';
            return 'low';
        }}

        // Render overview metrics
        function renderOverview() {{
            const container = document.getElementById('overview-metrics');
            const bestOverall = evaluationData.results.reduce((best, current) => {{
                const bestScore = best.aggregate_scores.query_validity_rate;
                const currentScore = current.aggregate_scores.query_validity_rate;
                return currentScore > bestScore ? current : best;
            }});

            const fastestAgent = evaluationData.results.reduce((fastest, current) =>
                current.avg_response_time < fastest.avg_response_time ? current : fastest
            );

            const mostEfficient = evaluationData.results.reduce((best, current) =>
                current.aggregate_scores.avg_total_tokens < best.aggregate_scores.avg_total_tokens ? current : best
            );

            container.innerHTML = `
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Total Questions</h3>
                        <div class="value">${{evaluationData.summary.total_questions}}</div>
                        <div class="label">Test Questions</div>
                    </div>
                    <div class="metric-card">
                        <h3>Agents Tested</h3>
                        <div class="value">${{evaluationData.results.length}}</div>
                        <div class="label">Configurations</div>
                    </div>
                    <div class="metric-card">
                        <h3>Best Performer</h3>
                        <div class="value">${{bestOverall.agent_name}}</div>
                        <div class="label">${{(bestOverall.aggregate_scores.query_validity_rate * 100).toFixed(0)}}% Valid</div>
                    </div>
                    <div class="metric-card">
                        <h3>Fastest Agent</h3>
                        <div class="value">${{fastestAgent.agent_name}}</div>
                        <div class="label">${{fastestAgent.avg_response_time.toFixed(2)}}s avg</div>
                    </div>
                    <div class="metric-card">
                        <h3>Most Efficient</h3>
                        <div class="value">${{mostEfficient.agent_name}}</div>
                        <div class="label">${{Math.round(mostEfficient.aggregate_scores.avg_total_tokens)}} tokens/query</div>
                    </div>
                </div>
            `;
        }}

        // Render comparison table
        function renderComparisonTable() {{
            const container = document.getElementById('comparison-table');
            const rows = evaluationData.results.map(result => {{
                const scores = result.aggregate_scores;
                return `
                    <tr>
                        <td><div class="agent-label">${{result.agent_name}}</div></td>
                        <td><span class="score ${{getScoreClass(scores.query_validity_rate)}}">${{(scores.query_validity_rate * 100).toFixed(1)}}%</span></td>
                        <td><span class="score ${{getScoreClass(scores.query_pattern_match_rate)}}">${{(scores.query_pattern_match_rate * 100).toFixed(1)}}%</span></td>
                        <td><span class="score ${{getScoreClass(scores.visualization_correctness_rate)}}">${{(scores.visualization_correctness_rate * 100).toFixed(1)}}%</span></td>
                        <td>${{result.avg_response_time.toFixed(2)}}s</td>
                        <td>${{Math.round(scores.avg_total_tokens).toLocaleString()}}</td>
                        <td><span class="score ${{getScoreClass(scores.recommendations_rate)}}">${{(scores.recommendations_rate * 100).toFixed(1)}}%</span></td>
                    </tr>
                `;
            }}).join('');

            container.innerHTML = `
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Agent</th>
                            <th>Query Validity</th>
                            <th>Pattern Match</th>
                            <th>Viz Correct</th>
                            <th>Avg Time</th>
                            <th>Avg Tokens</th>
                            <th>Recommendations</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${{rows}}
                    </tbody>
                </table>
            `;
        }}

        // Create validity chart
        function createValidityChart() {{
            const ctx = document.getElementById('validityChart').getContext('2d');
            const labels = evaluationData.results.map(r => r.agent_name);

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [
                        {{
                            label: 'Query Validity',
                            data: evaluationData.results.map(r => r.aggregate_scores.query_validity_rate * 100),
                            backgroundColor: 'rgba(102, 126, 234, 0.8)'
                        }},
                        {{
                            label: 'Pattern Match',
                            data: evaluationData.results.map(r => r.aggregate_scores.query_pattern_match_rate * 100),
                            backgroundColor: 'rgba(118, 75, 162, 0.8)'
                        }},
                        {{
                            label: 'Visualization Correct',
                            data: evaluationData.results.map(r => r.aggregate_scores.visualization_correctness_rate * 100),
                            backgroundColor: 'rgba(72, 187, 120, 0.8)'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}

        // Create token usage chart
        function createTokenChart() {{
            const ctx = document.getElementById('tokenChart').getContext('2d');
            const labels = evaluationData.results.map(r => r.agent_name);

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [
                        {{
                            label: 'Input Tokens',
                            data: evaluationData.results.map(r => r.aggregate_scores.avg_input_tokens),
                            backgroundColor: 'rgba(102, 126, 234, 0.8)'
                        }},
                        {{
                            label: 'Output Tokens',
                            data: evaluationData.results.map(r => r.aggregate_scores.avg_output_tokens),
                            backgroundColor: 'rgba(237, 137, 54, 0.8)'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            stacked: true
                        }},
                        x: {{
                            stacked: true
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}

        // Create response time chart
        function createTimeChart() {{
            const ctx = document.getElementById('timeChart').getContext('2d');
            const labels = evaluationData.results.map(r => r.agent_name);

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Average Response Time (seconds)',
                        data: evaluationData.results.map(r => r.avg_response_time),
                        borderColor: 'rgba(102, 126, 234, 1)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}

        // Create cost chart
        function createCostChart() {{
            const ctx = document.getElementById('costChart').getContext('2d');
            const labels = evaluationData.results.map(r => r.agent_name);

            // Calculate costs (GPT-4o-mini pricing: $0.150 per 1M input, $0.600 per 1M output)
            const inputCosts = evaluationData.results.map(r =>
                (r.aggregate_scores.total_input_tokens / 1000000) * 0.150
            );
            const outputCosts = evaluationData.results.map(r =>
                (r.aggregate_scores.total_output_tokens / 1000000) * 0.600
            );

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [
                        {{
                            label: 'Input Cost ($)',
                            data: inputCosts,
                            backgroundColor: 'rgba(102, 126, 234, 0.8)'
                        }},
                        {{
                            label: 'Output Cost ($)',
                            data: outputCosts,
                            backgroundColor: 'rgba(237, 137, 54, 0.8)'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            stacked: true,
                            ticks: {{
                                callback: function(value) {{
                                    return '$' + value.toFixed(4);
                                }}
                            }}
                        }},
                        x: {{
                            stacked: true
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.dataset.label + ': $' + context.parsed.y.toFixed(4);
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}

        // Render cost table
        function renderCostTable() {{
            const container = document.getElementById('cost-table');
            const rows = evaluationData.results.map(result => {{
                const scores = result.aggregate_scores;
                const inputCost = (scores.total_input_tokens / 1000000) * 0.150;
                const outputCost = (scores.total_output_tokens / 1000000) * 0.600;
                const totalCost = inputCost + outputCost;
                const costPerQuery = totalCost / evaluationData.summary.total_questions;

                return `
                    <tr>
                        <td><div class="agent-label">${{result.agent_name}}</div></td>
                        <td>${{scores.total_input_tokens.toLocaleString()}}</td>
                        <td>${{scores.total_output_tokens.toLocaleString()}}</td>
                        <td>${{scores.total_tokens.toLocaleString()}}</td>
                        <td>$${{inputCost.toFixed(4)}}</td>
                        <td>$${{outputCost.toFixed(4)}}</td>
                        <td><strong>$${{totalCost.toFixed(4)}}</strong></td>
                        <td>$${{costPerQuery.toFixed(4)}}</td>
                    </tr>
                `;
            }}).join('');

            container.innerHTML = `
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Agent</th>
                            <th>Input Tokens</th>
                            <th>Output Tokens</th>
                            <th>Total Tokens</th>
                            <th>Input Cost</th>
                            <th>Output Cost</th>
                            <th>Total Cost</th>
                            <th>Cost/Query</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${{rows}}
                    </tbody>
                </table>
                <p style="margin-top: 15px; color: #718096; font-size: 0.9rem;">
                    * Pricing based on GPT-4o-mini: $0.150 per 1M input tokens, $0.600 per 1M output tokens
                </p>
            `;
        }}

        // Render question-by-question results
        function renderQuestionResults() {{
            const container = document.getElementById('question-results');

            // Group responses by question
            const questionMap = {{}};
            evaluationData.results.forEach(result => {{
                result.responses.forEach(response => {{
                    if (!questionMap[response.question_id]) {{
                        questionMap[response.question_id] = {{
                            question: response.question,
                            category: response.category,
                            responses: []
                        }};
                    }}
                    questionMap[response.question_id].responses.push({{
                        agent: result.agent_name,
                        ...response
                    }});
                }});
            }});

            const questionsHtml = Object.entries(questionMap).map(([qId, qData]) => {{
                const responsesHtml = qData.responses.map(r => {{
                    const queryValid = r.scores?.query_validity === 1;
                    const patternMatch = r.scores?.query_pattern_match === 1;
                    const vizCorrect = r.scores?.visualization_correctness === 1;
                    const hasError = r.error ? true : false;

                    const badges = [];
                    if (hasError) {{
                        badges.push('<span class="score-badge error">Error</span>');
                    }} else {{
                        badges.push(queryValid ?
                            '<span class="score-badge success">Valid SQL</span>' :
                            '<span class="score-badge error">Invalid SQL</span>');
                        badges.push(patternMatch ?
                            '<span class="score-badge success">Pattern Match</span>' :
                            '<span class="score-badge warning">No Pattern</span>');
                        badges.push(vizCorrect ?
                            '<span class="score-badge success">Correct Viz</span>' :
                            '<span class="score-badge warning">Wrong Viz</span>');
                    }}

                    return `
                        <div class="agent-response">
                            <div class="agent-response-header">
                                <h4>${{r.agent}}</h4>
                                <div class="score-badges">${{badges.join('')}}</div>
                            </div>
                            <div class="metrics-row">
                                <div class="metric-item">
                                    <span class="label">Response Time</span>
                                    <span class="value">${{r.response_time?.toFixed(2) || 'N/A'}}s</span>
                                </div>
                                <div class="metric-item">
                                    <span class="label">Tokens</span>
                                    <span class="value">${{r.scores?.total_tokens?.toLocaleString() || '0'}}</span>
                                </div>
                                <div class="metric-item">
                                    <span class="label">Visualization</span>
                                    <span class="value">${{r.scores?.visualization_type || 'none'}}</span>
                                </div>
                            </div>
                            <div class="response-preview" id="preview-${{qId}}-${{r.agent}}">
                                ${{hasError ? 'Error: ' + r.error : (r.response || 'No response').substring(0, 200)}}...
                            </div>
                            <button class="expand-btn" onclick="togglePreview('${{qId}}-${{r.agent}}')">Show Full Response</button>
                        </div>
                    `;
                }}).join('');

                return `
                    <div class="question-card">
                        <h3>${{qId.toUpperCase()}}: ${{qData.question}}</h3>
                        <div class="question-text">
                            Category: <strong>${{qData.category.replace('_', ' ')}}</strong>
                        </div>
                        ${{responsesHtml}}
                    </div>
                `;
            }}).join('');

            container.innerHTML = questionsHtml;
        }}

        // Toggle response preview
        function togglePreview(id) {{
            const preview = document.getElementById('preview-' + id);
            const isExpanded = preview.classList.contains('expanded');

            if (isExpanded) {{
                preview.classList.remove('expanded');
                event.target.textContent = 'Show Full Response';
            }} else {{
                // Get full response text
                const [qId, agent] = id.split('-');
                const questionData = Object.values(evaluationData.results)
                    .flatMap(r => r.responses)
                    .find(resp => resp.question_id === qId);

                if (questionData) {{
                    const response = evaluationData.results
                        .find(r => r.agent_name === agent)
                        ?.responses.find(resp => resp.question_id === qId);

                    if (response) {{
                        preview.textContent = response.error || response.response || 'No response';
                        preview.classList.add('expanded');
                        event.target.textContent = 'Hide Full Response';
                    }}
                }}
            }}
        }}

        // Render category performance
        function renderCategoryResults() {{
            const container = document.getElementById('category-results');

            // Group by category
            const categories = {{}};
            evaluationData.results.forEach(result => {{
                result.responses.forEach(response => {{
                    const cat = response.category;
                    if (!categories[cat]) {{
                        categories[cat] = {{}};
                    }}
                    if (!categories[cat][result.agent_name]) {{
                        categories[cat][result.agent_name] = {{
                            total: 0,
                            valid: 0,
                            pattern_match: 0,
                            viz_correct: 0
                        }};
                    }}
                    const stats = categories[cat][result.agent_name];
                    stats.total++;
                    if (response.scores?.query_validity === 1) stats.valid++;
                    if (response.scores?.query_pattern_match === 1) stats.pattern_match++;
                    if (response.scores?.visualization_correctness === 1) stats.viz_correct++;
                }});
            }});

            const categoriesHtml = Object.entries(categories).map(([category, agentStats]) => {{
                const statsHtml = Object.entries(agentStats).map(([agent, stats]) => {{
                    const validRate = (stats.valid / stats.total * 100).toFixed(0);
                    const patternRate = (stats.pattern_match / stats.total * 100).toFixed(0);
                    const vizRate = (stats.viz_correct / stats.total * 100).toFixed(0);

                    return `
                        <div class="stat-box">
                            <h4>${{agent}}</h4>
                            <div class="value">${{validRate}}%</div>
                            <div style="font-size: 0.85rem; margin-top: 5px;">
                                Valid: ${{validRate}}% | Pattern: ${{patternRate}}% | Viz: ${{vizRate}}%
                            </div>
                        </div>
                    `;
                }}).join('');

                return `
                    <div class="category-card">
                        <h3>${{category.replace('_', ' ').toUpperCase()}}</h3>
                        <div class="category-stats">
                            ${{statsHtml}}
                        </div>
                    </div>
                `;
            }}).join('');

            container.innerHTML = categoriesHtml;
        }}

        // Initialize all visualizations
        renderOverview();
        renderComparisonTable();
        createValidityChart();
        createTokenChart();
        createTimeChart();
        createCostChart();
        renderCostTable();
        renderQuestionResults();
        renderCategoryResults();
    </script>
</body>
</html>"""

    # Write HTML file
    with open(output_file, 'w') as f:
        f.write(html_content)


def generate_comparison_report(all_results: List[Dict]) -> str:
    """Generate a markdown comparison report"""
    report = []

    report.append("# Threat Explorer Agent Evaluation Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Add visualization mode info
    viz_enabled = all_results[0]['visualizations_enabled'] if all_results else True
    report.append(f"\n**Visualizations:** {'ENABLED' if viz_enabled else 'DISABLED'}\n")

    # Summary table
    report.append("## Performance Summary\n")
    report.append("| Agent | Query Validity | Pattern Match | Viz Correct | Avg Time (s) | Recommendations |\n")
    report.append("|-------|----------------|---------------|-------------|--------------|------------------|\n")

    for result in all_results:
        scores = result["aggregate_scores"]
        report.append(
            f"| {result['agent_name']} | "
            f"{scores['query_validity_rate']:.1%} | "
            f"{scores['query_pattern_match_rate']:.1%} | "
            f"{scores['visualization_correctness_rate']:.1%} | "
            f"{scores['avg_response_time']:.2f} | "
            f"{scores['recommendations_rate']:.1%} |\n"
        )

    # Token usage table
    report.append("\n## Token Usage Summary\n")
    report.append("| Agent | Total Tokens | Avg Tokens/Query | Input Tokens | Output Tokens |\n")
    report.append("|-------|--------------|------------------|--------------|---------------|\n")

    for result in all_results:
        scores = result["aggregate_scores"]
        report.append(
            f"| {result['agent_name']} | "
            f"{scores['total_tokens']:,} | "
            f"{scores['avg_total_tokens']:.0f} | "
            f"{scores['total_input_tokens']:,} | "
            f"{scores['total_output_tokens']:,} |\n"
        )

    # Cost analysis table
    report.append("\n## Estimated Cost Analysis (GPT-4o-mini pricing)\n")
    report.append("| Agent | Total Cost | Cost/Query | Input Cost | Output Cost |\n")
    report.append("|-------|------------|------------|------------|-------------|\n")

    for result in all_results:
        scores = result["aggregate_scores"]
        total_cost = calculate_cost(scores['total_input_tokens'], scores['total_output_tokens'])
        cost_per_query = total_cost / result['total_questions'] if result['total_questions'] > 0 else 0
        input_cost = calculate_cost(scores['total_input_tokens'], 0)
        output_cost = calculate_cost(0, scores['total_output_tokens'])

        report.append(
            f"| {result['agent_name']} | "
            f"${total_cost:.4f} | "
            f"${cost_per_query:.4f} | "
            f"${input_cost:.4f} | "
            f"${output_cost:.4f} |\n"
        )

    # Detailed results by category
    report.append("\n## Results by Question Category\n")

    categories = set()
    for result in all_results:
        for response in result["responses"]:
            if "category" in response:
                categories.add(response["category"])

    for category in sorted(categories):
        report.append(f"\n### {category.replace('_', ' ').title()}\n")

        for result in all_results:
            cat_responses = [r for r in result["responses"] if r.get("category") == category]
            if cat_responses:
                valid = sum(1 for r in cat_responses if "error" not in r and r["scores"]["query_validity"] == 1)
                report.append(f"- **{result['agent_name']}**: {valid}/{len(cat_responses)} valid queries\n")

    # Winner analysis
    report.append("\n## Best Performer by Metric\n")

    metrics = ["query_validity_rate", "query_pattern_match_rate", "visualization_correctness_rate", "recommendations_rate"]
    metric_names = ["Query Validity", "Pattern Match", "Visualization Correctness", "Recommendations Rate"]

    for metric, name in zip(metrics, metric_names):
        best = max(all_results, key=lambda x: x["aggregate_scores"][metric])
        report.append(
            f"- **{name}:** {best['agent_name']} - "
            f"{best['aggregate_scores'][metric]:.1%}\n"
        )

    # Fastest agent
    fastest = min(all_results, key=lambda x: x["aggregate_scores"]["avg_response_time"])
    report.append(
        f"- **Fastest:** {fastest['agent_name']} - "
        f"{fastest['aggregate_scores']['avg_response_time']:.2f}s avg\n"
    )

    # Most token-efficient agent
    most_efficient = min(all_results, key=lambda x: x["aggregate_scores"]["avg_total_tokens"])
    report.append(
        f"- **Most Token-Efficient:** {most_efficient['agent_name']} - "
        f"{most_efficient['aggregate_scores']['avg_total_tokens']:.0f} tokens/query avg\n"
    )

    # Most cost-effective agent (lowest cost per query)
    def get_cost_per_query(result):
        scores = result["aggregate_scores"]
        total_cost = calculate_cost(scores['total_input_tokens'], scores['total_output_tokens'])
        return total_cost / result['total_questions'] if result['total_questions'] > 0 else float('inf')

    most_cost_effective = min(all_results, key=get_cost_per_query)
    cost_pq = get_cost_per_query(most_cost_effective)
    report.append(
        f"- **Most Cost-Effective:** {most_cost_effective['agent_name']} - "
        f"${cost_pq:.4f}/query avg\n"
    )

    return "\n".join(report)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Evaluate Threat Explorer agents")
    parser.add_argument("--output", "-o", default="evaluation_results.json", help="Output JSON file")
    parser.add_argument("--report", "-r", default="evaluation_report.md", help="Output markdown report")
    parser.add_argument("--html", default="evaluation_results.html", help="Output HTML report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--agents", "-a", nargs="+",
                        choices=["llm", "react", "multi-agent", "all"],
                        default=["all"],
                        help="Agents to evaluate (default: all). Options: llm, react, multi-agent, all")

    args = parser.parse_args()

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment")
        sys.exit(1)

    # Initialize database
    print("🔧 Initializing database...")
    db.initialize()

    # Determine which agents to test
    selected_agents = args.agents
    if "all" in selected_agents:
        selected_agents = ["llm", "react", "multi-agent"]

    # Initialize agents
    print(f"🤖 Initializing agents: {', '.join(selected_agents)}...")
    agents = {}

    agent_map = {
        "llm": ("LLM", LLMAgent),
        "react": ("ReACT", ReACTAgent),
        "multi-agent": ("Multi-Agent", MultiAgent)
    }

    for agent_key in selected_agents:
        agent_name, agent_class = agent_map[agent_key]
        agents[agent_name] = agent_class(api_key=api_key)

    # Visualizations are always enabled
    enable_viz = True

    # Run evaluations
    all_results = []

    for agent_name, agent in agents.items():
        result = evaluate_agent(
            agent_name=agent_name,
            agent=agent,
            questions=EVALUATION_QUESTIONS,
            enable_viz=enable_viz
        )
        all_results.append(result)

    # Save detailed results
    print(f"\n💾 Saving detailed results to {args.output}...")
    with open(args.output, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    # Generate and save markdown report
    print(f"📊 Generating markdown report to {args.report}...")
    report = generate_comparison_report(all_results)
    with open(args.report, 'w') as f:
        f.write(report)

    # Generate and save HTML report
    print(f"📊 Generating HTML report to {args.html}...")
    generate_html_report(all_results, args.html)

    # Print summary
    print("\n" + "="*80)
    print("EVALUATION COMPLETE")
    print("="*80)
    print(f"Evaluated {len(agents)} agents")
    print(f"Visualizations: {'ENABLED' if enable_viz else 'DISABLED'}")
    print(f"Total questions: {len(EVALUATION_QUESTIONS)}")
    print(f"Results saved to: {args.output}")
    print(f"Markdown report saved to: {args.report}")
    print(f"HTML report saved to: {args.html}")
    print("\nSummary:")

    for result in all_results:
        print(f"\n{result['agent_name']}:")
        print(f"  Query Validity: {result['aggregate_scores']['query_validity_rate']:.1%}")
        print(f"  Avg Response Time: {result['aggregate_scores']['avg_response_time']:.2f}s")
        print(f"  Error Rate: {result['aggregate_scores']['error_rate']:.1%}")
        print(f"  Total Tokens: {result['aggregate_scores']['total_tokens']:,}")
        print(f"  Avg Tokens/Query: {result['aggregate_scores']['avg_total_tokens']:.0f}")


if __name__ == "__main__":
    main()
