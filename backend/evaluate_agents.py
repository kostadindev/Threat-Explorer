#!/usr/bin/env python3
"""
Agent Evaluation Script for Threat Explorer

This script evaluates all three agents (LLM, ReACT, Multi-Agent) against a curated
set of multi-turn dialogue conversations to compare their performance on key metrics including:
- Query validity and pattern matching
- Visualization correctness
- Context awareness across conversation turns
- Response time and quality
- Token usage and cost analysis

The evaluation uses realistic dialogue scenarios where users progressively refine their
queries, requiring agents to maintain context across multiple turns.

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
from openai import OpenAI

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import LLMAgent, ReACTAgent, MultiAgent, Message
from db.database import db

# Load environment variables
load_dotenv()


# ============================================================================
# EVALUATION DATASET - DIALOGUE CONVERSATIONS
# ============================================================================

EVALUATION_DIALOGUES = [
    # ==================== DIALOGUE 1: BASIC ATTACK ANALYSIS ====================
    {
        "id": "d1",
        "title": "Basic Attack Type Analysis",
        "category": "basic_analysis",
        "description": "User performs simple attack counting and filtering",
        "turns": [
            {
                "turn_id": 1,
                "user_message": "Show me the top 5 attack types and how many times each occurred",
                "expected_query_pattern": r'SELECT.*"Attack Type".*COUNT.*GROUP BY.*"Attack Type".*LIMIT\s+5',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must group by attack type, count occurrences, and limit to 5",
                    "correctness": "Must return top 5 attack types by count",
                    "visualization": "Should use chart or pie for distribution"
                }
            },
            {
                "turn_id": 2,
                "user_message": "What severity levels do these attacks have?",
                "expected_query_pattern": r'SELECT.*"Severity Level".*COUNT',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must count by severity level",
                    "context_awareness": "Should reference top attack types from previous query",
                    "visualization": "Should use chart for distribution"
                }
            },
            {
                "turn_id": 3,
                "user_message": "Show me 10 examples of the most common attack type",
                "expected_query_pattern": r'SELECT.*"Attack Type".*LIMIT\s+10',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must filter by the most common attack type and limit to 10",
                    "context_awareness": "Should use the most common attack type from turn 1",
                    "visualization": "Should use table for detailed records"
                }
            }
        ]
    },

    # ==================== DIALOGUE 2: PROTOCOL INVESTIGATION ====================
    {
        "id": "d2",
        "title": "Protocol-Based Investigation",
        "category": "protocol_analysis",
        "description": "User investigates attacks by protocol type",
        "turns": [
            {
                "turn_id": 1,
                "user_message": "What protocols are being used for attacks?",
                "expected_query_pattern": r'SELECT.*Protocol.*COUNT.*GROUP BY',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must group by protocol and count occurrences",
                    "correctness": "Must return protocol distribution",
                    "visualization": "Should use chart for distribution"
                }
            },
            {
                "turn_id": 2,
                "user_message": "Show me attacks using TCP protocol",
                "expected_query_pattern": r'SELECT.*Protocol.*TCP.*LIMIT',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must filter by TCP protocol",
                    "context_awareness": "Should reference TCP from previous results",
                    "visualization": "Should use table for detailed records"
                }
            },
            {
                "turn_id": 3,
                "user_message": "What are the severity levels of these TCP attacks?",
                "expected_query_pattern": r'SELECT.*"Severity Level".*COUNT.*Protocol.*TCP',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must count severity levels for TCP attacks",
                    "context_awareness": "Must maintain TCP protocol filter from turn 2",
                    "visualization": "Should use chart for distribution"
                }
            }
        ]
    },

    # ==================== DIALOGUE 3: SEVERITY ANALYSIS ====================
    {
        "id": "d3",
        "title": "Severity Level Analysis",
        "category": "severity_analysis",
        "description": "User analyzes attacks by severity level",
        "turns": [
            {
                "turn_id": 1,
                "user_message": "Show me how many attacks there are for each severity level",
                "expected_query_pattern": r'SELECT.*"Severity Level".*COUNT.*GROUP BY',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must group by severity level and count",
                    "correctness": "Must return count per severity level",
                    "visualization": "Should use chart or pie for distribution"
                }
            },
            {
                "turn_id": 2,
                "user_message": "Give me 10 examples of Critical severity attacks",
                "expected_query_pattern": r'SELECT.*"Severity Level".*Critical.*LIMIT\s+10',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must filter by Critical severity and limit to 10",
                    "context_awareness": "Should reference Critical from previous query",
                    "visualization": "Should use table for detailed records"
                }
            },
            {
                "turn_id": 3,
                "user_message": "What actions were taken for these critical attacks?",
                "expected_query_pattern": r'SELECT.*"Action Taken".*"Severity Level".*Critical',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must show action taken for Critical severity",
                    "context_awareness": "Must maintain Critical severity filter",
                    "visualization": "Should use chart for action distribution"
                }
            }
        ]
    },

    # ==================== DIALOGUE 4: TEMPORAL ANALYSIS ====================
    {
        "id": "d4",
        "title": "Recent Attack Analysis",
        "category": "temporal_analysis",
        "description": "User analyzes recent attacks and their patterns",
        "turns": [
            {
                "turn_id": 1,
                "user_message": "Show me the 20 most recent attacks",
                "expected_query_pattern": r'SELECT.*ORDER BY.*Timestamp.*DESC.*LIMIT\s+20',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must order by Timestamp DESC and limit to 20",
                    "correctness": "Must return 20 most recent attacks",
                    "visualization": "Should use table for time-series data"
                }
            },
            {
                "turn_id": 2,
                "user_message": "What attack types appear in these recent attacks?",
                "expected_query_pattern": r'SELECT.*"Attack Type".*COUNT',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must count attack types",
                    "context_awareness": "Should consider recent attacks from previous query",
                    "visualization": "Should use chart for distribution"
                }
            },
            {
                "turn_id": 3,
                "user_message": "Show me the source IPs for the most common attack type",
                "expected_query_pattern": r'SELECT.*"Source IP Address"',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must show source IPs",
                    "context_awareness": "Should filter by most common attack type from turn 2",
                    "visualization": "Should use table for detailed IP data"
                }
            }
        ]
    },

    # ==================== DIALOGUE 5: NETWORK SEGMENT ANALYSIS ====================
    {
        "id": "d5",
        "title": "Network Segment Investigation",
        "category": "network_analysis",
        "description": "User investigates attacks across network segments",
        "turns": [
            {
                "turn_id": 1,
                "user_message": "Which network segments have the most attacks?",
                "expected_query_pattern": r'SELECT.*"Network Segment".*COUNT.*GROUP BY.*"Network Segment"',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must group by network segment and count attacks",
                    "correctness": "Must return attack counts per segment",
                    "visualization": "Should use chart for comparison"
                }
            },
            {
                "turn_id": 2,
                "user_message": "Show me details of attacks in the segment with the most attacks",
                "expected_query_pattern": r'SELECT.*"Network Segment".*LIMIT',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must filter by specific network segment",
                    "context_awareness": "Should identify and use the segment with most attacks from turn 1",
                    "visualization": "Should use table for detailed records"
                }
            },
            {
                "turn_id": 3,
                "user_message": "What are the attack types in this vulnerable segment?",
                "expected_query_pattern": r'SELECT.*"Attack Type".*"Network Segment".*COUNT',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must count attack types for specific segment",
                    "context_awareness": "Must maintain network segment filter from turn 2",
                    "visualization": "Should use chart for attack type distribution"
                }
            }
        ]
    },

    # ==================== DIALOGUE 6: SOURCE IP INVESTIGATION ====================
    {
        "id": "d6",
        "title": "Source IP Analysis",
        "category": "ip_analysis",
        "description": "User investigates attacks by source IP addresses",
        "turns": [
            {
                "turn_id": 1,
                "user_message": "Show me the top 10 source IP addresses with the most attacks",
                "expected_query_pattern": r'SELECT.*"Source IP Address".*COUNT.*GROUP BY.*LIMIT\s+10',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must group by source IP and count, limit to 10",
                    "correctness": "Must return top 10 source IPs by attack count",
                    "visualization": "Should use chart for ranking"
                }
            },
            {
                "turn_id": 2,
                "user_message": "What attack types is the top IP performing?",
                "expected_query_pattern": r'SELECT.*"Attack Type".*"Source IP Address"',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must filter by specific source IP",
                    "context_awareness": "Should use the top source IP from turn 1",
                    "visualization": "Should use chart for attack type distribution"
                }
            },
            {
                "turn_id": 3,
                "user_message": "Show me 10 attack records from this IP address",
                "expected_query_pattern": r'SELECT.*"Source IP Address".*LIMIT\s+10',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must filter by source IP and limit to 10",
                    "context_awareness": "Must maintain source IP filter from turn 2",
                    "visualization": "Should use table for detailed records"
                }
            }
        ]
    },

    # ==================== DIALOGUE 7: PORT ANALYSIS ====================
    {
        "id": "d7",
        "title": "Destination Port Analysis",
        "category": "port_analysis",
        "description": "User investigates attacks targeting specific ports",
        "turns": [
            {
                "turn_id": 1,
                "user_message": "What are the most commonly targeted destination ports?",
                "expected_query_pattern": r'SELECT.*"Destination Port".*COUNT.*GROUP BY',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must group by destination port and count",
                    "correctness": "Must return port attack counts",
                    "visualization": "Should use chart for distribution"
                }
            },
            {
                "turn_id": 2,
                "user_message": "Show me attacks targeting the most common port",
                "expected_query_pattern": r'SELECT.*"Destination Port".*LIMIT',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must filter by specific destination port",
                    "context_awareness": "Should use most common port from turn 1",
                    "visualization": "Should use table for detailed records"
                }
            },
            {
                "turn_id": 3,
                "user_message": "What protocols are used for attacks on this port?",
                "expected_query_pattern": r'SELECT.*Protocol.*"Destination Port".*COUNT',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must count protocols for specific port",
                    "context_awareness": "Must maintain destination port filter from turn 2",
                    "visualization": "Should use chart for protocol distribution"
                }
            }
        ]
    },

    # ==================== DIALOGUE 8: MALWARE INVESTIGATION ====================
    {
        "id": "d8",
        "title": "Malware Indicator Analysis",
        "category": "malware_analysis",
        "description": "User investigates malware-related attacks",
        "turns": [
            {
                "turn_id": 1,
                "user_message": "Show me attacks that have malware indicators",
                "expected_query_pattern": r'SELECT.*"Malware Indicators".*LIMIT',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must filter for non-empty malware indicators",
                    "correctness": "Must return attacks with malware indicators",
                    "visualization": "Should use table for detailed records"
                }
            },
            {
                "turn_id": 2,
                "user_message": "What are the severity levels of these malware attacks?",
                "expected_query_pattern": r'SELECT.*"Severity Level".*COUNT',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must count severity levels",
                    "context_awareness": "Should maintain malware indicator filter from turn 1",
                    "visualization": "Should use chart for severity distribution"
                }
            },
            {
                "turn_id": 3,
                "user_message": "What actions were taken against these malware attacks?",
                "expected_query_pattern": r'SELECT.*"Action Taken".*COUNT',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must count actions taken",
                    "context_awareness": "Must maintain malware context from previous turns",
                    "visualization": "Should use chart for action distribution"
                }
            }
        ]
    },

    # ==================== DIALOGUE 9: IDS/IPS ALERTS ANALYSIS ====================
    {
        "id": "d9",
        "title": "IDS/IPS Alert Investigation",
        "category": "alert_analysis",
        "description": "User investigates IDS/IPS alert patterns",
        "turns": [
            {
                "turn_id": 1,
                "user_message": "Show me attacks that triggered IDS/IPS alerts",
                "expected_query_pattern": r'SELECT.*"IDS/IPS Alerts".*LIMIT',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must filter for non-empty IDS/IPS alerts",
                    "correctness": "Must return attacks with IDS/IPS alerts",
                    "visualization": "Should use table for detailed records"
                }
            },
            {
                "turn_id": 2,
                "user_message": "What attack types generated these alerts?",
                "expected_query_pattern": r'SELECT.*"Attack Type".*COUNT',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must count attack types",
                    "context_awareness": "Should maintain IDS/IPS alert filter from turn 1",
                    "visualization": "Should use chart for attack type distribution"
                }
            },
            {
                "turn_id": 3,
                "user_message": "Show me the network segments where these alerts occurred",
                "expected_query_pattern": r'SELECT.*"Network Segment".*COUNT',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must count by network segment",
                    "context_awareness": "Must maintain IDS/IPS alert context",
                    "visualization": "Should use chart for segment distribution"
                }
            }
        ]
    },

    # ==================== DIALOGUE 10: TRAFFIC TYPE ANALYSIS ====================
    {
        "id": "d10",
        "title": "Traffic Type Investigation",
        "category": "traffic_analysis",
        "description": "User analyzes attacks by traffic type",
        "turns": [
            {
                "turn_id": 1,
                "user_message": "Show me how attacks are distributed across traffic types",
                "expected_query_pattern": r'SELECT.*"Traffic Type".*COUNT.*GROUP BY',
                "expected_visualization": "db-chart",
                "rubric": {
                    "query_validity": "Must group by traffic type and count",
                    "correctness": "Must return attack counts per traffic type",
                    "visualization": "Should use chart or pie for distribution"
                }
            },
            {
                "turn_id": 2,
                "user_message": "Give me 15 examples from the most common traffic type",
                "expected_query_pattern": r'SELECT.*"Traffic Type".*LIMIT\s+15',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must filter by specific traffic type and limit to 15",
                    "context_awareness": "Should use most common traffic type from turn 1",
                    "visualization": "Should use table for detailed records"
                }
            },
            {
                "turn_id": 3,
                "user_message": "What are the average anomaly scores for this traffic type?",
                "expected_query_pattern": r'SELECT.*(AVG|avg).*"Anomaly Scores".*"Traffic Type"',
                "expected_visualization": "db-table",
                "rubric": {
                    "query_validity": "Must calculate average anomaly scores",
                    "context_awareness": "Must maintain traffic type filter from turn 2",
                    "visualization": "Should use table or chart for numeric results"
                }
            }
        ]
    }
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


def llm_judge_rating(client: OpenAI, user_question: str, agent_response: str, database_schema: str) -> Dict[str, Any]:
    """
    Use LLM as a judge to rate agent responses on multiple dimensions.

    Args:
        client: OpenAI client instance
        user_question: The original user question
        agent_response: The agent's response to evaluate
        database_schema: Schema information for context

    Returns:
        Dictionary with ratings for Factuality, Helpfulness, and Overall Quality (1-5 scale)
    """

    judge_prompt = f"""You are an expert evaluator assessing the quality of an AI agent's response to a cybersecurity database query question.

Database Schema Context:
{database_schema}

User Question: {user_question}

Agent Response to Evaluate:
{agent_response}

Please evaluate this response on the following criteria, providing a score from 1-5 for each (where 1 is poor and 5 is excellent):

1. **Factuality (1-5)**: How factually accurate and correct is the response?
   - 5: Completely accurate with correct SQL queries, proper database column usage, and accurate interpretations
   - 4: Mostly accurate with minor issues
   - 3: Some factual errors or incorrect assumptions
   - 2: Multiple factual errors or significant inaccuracies
   - 1: Largely inaccurate or misleading

2. **Helpfulness (1-5)**: How helpful and useful is the response for the user?
   - 5: Extremely helpful, provides actionable insights, proper visualizations, and clear explanations
   - 4: Very helpful with good insights and clarity
   - 3: Moderately helpful but could be more detailed or clear
   - 2: Minimally helpful, lacks important details or context
   - 1: Not helpful, confusing, or irrelevant

3. **Overall Quality (1-5)**: Overall assessment considering all factors
   - 5: Excellent response - accurate, helpful, well-formatted, and comprehensive
   - 4: Good response with minor room for improvement
   - 3: Adequate response but with notable limitations
   - 2: Below average response with significant issues
   - 1: Poor response that fails to address the question properly

Provide your evaluation in the following JSON format:
{{
    "factuality": <score 1-5>,
    "factuality_reasoning": "<brief explanation>",
    "helpfulness": <score 1-5>,
    "helpfulness_reasoning": "<brief explanation>",
    "overall_quality": <score 1-5>,
    "overall_reasoning": "<brief explanation>"
}}

Respond ONLY with the JSON object, no additional text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert evaluator of AI system responses. Provide objective, detailed assessments."},
                {"role": "user", "content": judge_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        # Parse the JSON response
        result_text = response.choices[0].message.content.strip()

        # Extract JSON if wrapped in code blocks
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        ratings = json.loads(result_text)

        return {
            "factuality": ratings.get("factuality", 3),
            "factuality_reasoning": ratings.get("factuality_reasoning", ""),
            "helpfulness": ratings.get("helpfulness", 3),
            "helpfulness_reasoning": ratings.get("helpfulness_reasoning", ""),
            "overall_quality": ratings.get("overall_quality", 3),
            "overall_reasoning": ratings.get("overall_reasoning", ""),
            "judge_success": True
        }

    except Exception as e:
        print(f"     ⚠ LLM Judge error: {str(e)}")
        return {
            "factuality": 0,
            "factuality_reasoning": f"Judge failed: {str(e)}",
            "helpfulness": 0,
            "helpfulness_reasoning": f"Judge failed: {str(e)}",
            "overall_quality": 0,
            "overall_reasoning": f"Judge failed: {str(e)}",
            "judge_success": False
        }


def score_response(response: str, turn_data: Dict[str, Any], usage: Dict[str, int] = None, metadata: Dict[str, Any] = None, is_followup: bool = False) -> Dict[str, Any]:
    """Score a single agent response for a conversation turn"""
    scores = {
        "query_validity": 0,
        "query_pattern_match": 0,
        "visualization_correctness": 0,
        "context_awareness": 0,  # New metric for dialogue evaluation
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

    if turn_data.get("expected_query_pattern"):
        # This turn expects a database query
        if sql_query:
            validation = validate_sql_query(sql_query)
            scores["query_validity"] = 1 if validation["valid"] else 0
            scores["query_error"] = validation.get("error")

            # Check if query matches expected pattern
            if check_query_pattern(sql_query, turn_data["expected_query_pattern"]):
                scores["query_pattern_match"] = 1
        else:
            scores["query_validity"] = 0
            scores["query_error"] = "No SQL query found in response"
    else:
        # This turn should NOT query database
        if not sql_query:
            scores["query_validity"] = 1  # Correctly didn't query
        else:
            scores["query_validity"] = 0  # Incorrectly queried database

    # Check visualization format
    viz_type = detect_visualization_type(response)
    expected_viz = turn_data.get("expected_visualization")

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

    # For follow-up turns, check if context awareness rubric exists
    if is_followup and "context_awareness" in turn_data.get("rubric", {}):
        # Simple heuristic: if the query/response is valid and follows pattern, assume context was maintained
        # In a more sophisticated evaluation, you might check for specific context references
        if scores["query_validity"] == 1 and scores["query_pattern_match"] == 1:
            scores["context_awareness"] = 1
        else:
            scores["context_awareness"] = 0
    elif not is_followup:
        # First turn always gets full context awareness score (no prior context to maintain)
        scores["context_awareness"] = 1

    return scores


def evaluate_agent(agent_name: str, agent, dialogues: List[Dict], enable_viz: bool = True, use_judge: bool = True, judge_client: OpenAI = None) -> Dict[str, Any]:
    """Evaluate a single agent on all dialogue conversations"""
    print(f"\n{'='*80}")
    print(f"Evaluating {agent_name} (Visualizations: {'ON' if enable_viz else 'OFF'}, Judge: {'ON' if use_judge else 'OFF'})")
    print(f"{'='*80}")

    # Get database schema for judge context
    database_schema = """
The database contains a table called 'attacks' with the following exact columns (case-sensitive):

Columns requiring double quotes (have spaces):
- "Source IP Address", "Destination IP Address"
- "Source Port", "Destination Port"
- "Packet Length", "Packet Type", "Traffic Type"
- "Payload Data", "Malware Indicators", "Anomaly Scores"
- "Alerts/Warnings", "Attack Type", "Attack Signature"
- "Action Taken", "Severity Level"
- "User Information", "Device Information", "Network Segment"
- "Geo-location Data", "Proxy Information"
- "Firewall Logs", "IDS/IPS Alerts", "Log Source"

Columns NOT requiring quotes (no spaces):
- Timestamp, Protocol

IMPORTANT:
- The column is "Anomaly Scores" (PLURAL), not "Anomaly Score"
- ALL column names with spaces MUST be enclosed in double quotes in SQL queries
- Column names are case-sensitive
"""

    results = {
        "agent_name": agent_name,
        "visualizations_enabled": enable_viz,
        "total_dialogues": len(dialogues),
        "total_turns": sum(len(d["turns"]) for d in dialogues),
        "dialogues": [],
        "aggregate_scores": {},
        "total_time": 0,
        "use_judge": use_judge
    }

    for dialogue_idx, dialogue_data in enumerate(dialogues, 1):
        print(f"\n{'─'*80}")
        print(f"Dialogue {dialogue_idx}/{len(dialogues)}: {dialogue_data['title']}")
        print(f"Category: {dialogue_data['category']}")
        print(f"Description: {dialogue_data['description']}")
        print(f"{'─'*80}")

        dialogue_result = {
            "dialogue_id": dialogue_data["id"],
            "title": dialogue_data["title"],
            "category": dialogue_data["category"],
            "description": dialogue_data["description"],
            "turns": [],
            "dialogue_time": 0
        }

        # Maintain conversation history across turns
        conversation_history = []

        for turn_idx, turn_data in enumerate(dialogue_data["turns"], 1):
            user_message = turn_data["user_message"]
            print(f"\n  Turn {turn_idx}/{len(dialogue_data['turns'])}: {user_message}")

            # Add user message to conversation history
            conversation_history.append(Message(role="user", content=user_message))

            # Time the response
            start_time = time.time()

            try:
                # Pass the full conversation history to the agent
                response = agent.chat(
                    messages=conversation_history,
                    temperature=0.7,
                    max_tokens=2000,
                    enable_visualizations=enable_viz
                )

                elapsed_time = time.time() - start_time
                response_text = response.message.content

                # Add assistant response to conversation history
                conversation_history.append(Message(role="assistant", content=response_text))

                # Extract token usage for display
                tokens_used = response.usage.get("total_tokens", 0) if response.usage else 0
                print(f"     ✓ Response received ({elapsed_time:.2f}s, {tokens_used} tokens)")

                # Score the response (mark as follow-up if not first turn)
                is_followup = turn_idx > 1
                scores = score_response(
                    response_text,
                    turn_data,
                    response.usage,
                    response.metadata,
                    is_followup=is_followup
                )

                # Get LLM Judge ratings if enabled
                judge_ratings = None
                if use_judge and judge_client:
                    print(f"     🔍 Getting LLM judge ratings...")
                    judge_ratings = llm_judge_rating(
                        judge_client,
                        user_message,
                        response_text,
                        database_schema
                    )
                    if judge_ratings.get("judge_success"):
                        print(f"     📊 Judge Scores - Factuality: {judge_ratings['factuality']}/5, "
                              f"Helpfulness: {judge_ratings['helpfulness']}/5, "
                              f"Quality: {judge_ratings['overall_quality']}/5")

                # Extract the SQL query from response for display
                sql_query = extract_sql_query(response_text)
                if not sql_query and response.metadata and "sql_queries" in response.metadata and response.metadata["sql_queries"]:
                    sql_query = response.metadata["sql_queries"][0]

                turn_result = {
                    "turn_id": turn_data["turn_id"],
                    "user_message": user_message,
                    "response": response_text,
                    "response_time": elapsed_time,
                    "scores": scores,
                    "judge_ratings": judge_ratings,
                    "metadata": response.metadata,
                    "is_followup": is_followup,
                    "generated_sql": sql_query,
                    "expected_query_pattern": turn_data.get("expected_query_pattern", "")
                }

                dialogue_result["turns"].append(turn_result)
                dialogue_result["dialogue_time"] += elapsed_time
                results["total_time"] += elapsed_time

            except Exception as e:
                print(f"     ✗ Error: {str(e)}")
                turn_result = {
                    "turn_id": turn_data["turn_id"],
                    "user_message": user_message,
                    "error": str(e),
                    "response_time": time.time() - start_time,
                    "is_followup": turn_idx > 1
                }
                dialogue_result["turns"].append(turn_result)
                dialogue_result["dialogue_time"] += turn_result["response_time"]
                results["total_time"] += turn_result["response_time"]

        results["dialogues"].append(dialogue_result)
        print(f"\n  Dialogue completed in {dialogue_result['dialogue_time']:.2f}s")

    # Calculate aggregate scores across all turns
    all_turns = []
    for dialogue in results["dialogues"]:
        all_turns.extend(dialogue["turns"])

    valid_turns = [t for t in all_turns if "error" not in t]

    if valid_turns:
        results["aggregate_scores"] = {
            "query_validity_rate": sum(t["scores"]["query_validity"] for t in valid_turns) / len(valid_turns),
            "query_pattern_match_rate": sum(t["scores"]["query_pattern_match"] for t in valid_turns) / len(valid_turns),
            "visualization_correctness_rate": sum(t["scores"]["visualization_correctness"] for t in valid_turns) / len(valid_turns),
            "context_awareness_rate": sum(t["scores"]["context_awareness"] for t in valid_turns) / len(valid_turns),
            "avg_response_time": results["total_time"] / len(valid_turns),
            "avg_response_length": sum(t["scores"]["response_length"] for t in valid_turns) / len(valid_turns),
            "recommendations_rate": sum(t["scores"]["has_recommendations"] for t in valid_turns) / len(valid_turns),
            "error_rate": (len(all_turns) - len(valid_turns)) / len(all_turns) if all_turns else 0,
            "total_input_tokens": sum(t["scores"]["input_tokens"] for t in valid_turns),
            "total_output_tokens": sum(t["scores"]["output_tokens"] for t in valid_turns),
            "total_tokens": sum(t["scores"]["total_tokens"] for t in valid_turns),
            "avg_input_tokens": sum(t["scores"]["input_tokens"] for t in valid_turns) / len(valid_turns),
            "avg_output_tokens": sum(t["scores"]["output_tokens"] for t in valid_turns) / len(valid_turns),
            "avg_total_tokens": sum(t["scores"]["total_tokens"] for t in valid_turns) / len(valid_turns)
        }

        # Add judge ratings if available
        if use_judge:
            turns_with_judge = [t for t in valid_turns if t.get("judge_ratings") and t["judge_ratings"].get("judge_success")]
            if turns_with_judge:
                results["aggregate_scores"]["avg_factuality"] = sum(t["judge_ratings"]["factuality"] for t in turns_with_judge) / len(turns_with_judge)
                results["aggregate_scores"]["avg_helpfulness"] = sum(t["judge_ratings"]["helpfulness"] for t in turns_with_judge) / len(turns_with_judge)
                results["aggregate_scores"]["avg_overall_quality"] = sum(t["judge_ratings"]["overall_quality"] for t in turns_with_judge) / len(turns_with_judge)
                results["aggregate_scores"]["judge_success_rate"] = len(turns_with_judge) / len(valid_turns)
            else:
                results["aggregate_scores"]["avg_factuality"] = 0
                results["aggregate_scores"]["avg_helpfulness"] = 0
                results["aggregate_scores"]["avg_overall_quality"] = 0
                results["aggregate_scores"]["judge_success_rate"] = 0

        # Print summary for this agent
        print(f"\n{'-'*80}")
        print(f"Agent Summary:")
        print(f"  Total Dialogues: {results['total_dialogues']}")
        print(f"  Total Turns: {results['total_turns']}")
        print(f"  Context Awareness: {results['aggregate_scores']['context_awareness_rate']:.1%}")
        if use_judge and results['aggregate_scores'].get('avg_factuality', 0) > 0:
            print(f"  LLM Judge Ratings:")
            print(f"    Factuality: {results['aggregate_scores']['avg_factuality']:.2f}/5")
            print(f"    Helpfulness: {results['aggregate_scores']['avg_helpfulness']:.2f}/5")
            print(f"    Overall Quality: {results['aggregate_scores']['avg_overall_quality']:.2f}/5")
        print(f"  Total Tokens: {results['aggregate_scores']['total_tokens']:,}")
        print(f"  Avg Tokens/Turn: {results['aggregate_scores']['avg_total_tokens']:.0f}")
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


def generate_html_report(output_file: str, json_file: str = "evaluation_results.json"):
    """Generate an interactive HTML report that reads from a JSON results file

    Args:
        output_file: Path to output HTML file
        json_file: Path to JSON results file (relative to HTML file location)
    """

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

        .loading-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 400px;
            padding: 40px;
        }}

        .loading-spinner {{
            width: 50px;
            height: 50px;
            border: 5px solid #e2e8f0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        .loading-text {{
            margin-top: 20px;
            color: #718096;
            font-size: 1.1rem;
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
            <!-- Loading indicator -->
            <div id="loading" class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading evaluation results...</div>
            </div>

            <!-- Content sections (hidden until loaded) -->
            <div id="report-content" style="display: none;">
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

                <div class="chart-container">
                    <h3 style="margin-bottom: 20px; color: #2d3748;">LLM Judge Ratings (1-5 Scale)</h3>
                    <div class="chart-wrapper">
                        <canvas id="judgeChart"></canvas>
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

            <!-- Individual Evaluation Results Table -->
            <div class="section">
                <h2 class="section-title">📋 Complete Evaluation Results (All Turns)</h2>
                <div id="individual-results-table"></div>
            </div>

            <!-- Per-Agent Detailed Tables -->
            <div class="section">
                <h2 class="section-title">🔍 Per-Agent Detailed Results</h2>
                <div id="per-agent-tables"></div>
            </div>
            </div><!-- End report-content -->
        </div>
    </div>

    <script>
        let evaluationData = null;

        // Load evaluation data from JSON file
        async function loadEvaluationData() {{
            try {{
                const response = await fetch('{json_file}');
                if (!response.ok) {{
                    throw new Error(`Failed to load results: ${{response.statusText}}`);
                }}
                evaluationData = await response.json();

                // Transform raw results to expected format
                transformData();

                // Hide loading indicator and show content
                document.getElementById('loading').style.display = 'none';
                document.getElementById('report-content').style.display = 'block';

                // Initialize all visualizations
                initializeVisualizations();
            }} catch (error) {{
                console.error('Error loading evaluation data:', error);
                document.getElementById('loading').innerHTML = `
                    <div style="text-align: center; max-width: 800px; margin: 0 auto;">
                        <h1 style="color: #f56565; margin-bottom: 20px;">❌ CORS Error: Cannot Load Results</h1>
                        <p style="color: #718096; font-size: 1.1rem; margin-bottom: 20px;">
                            The browser blocked loading <strong>{json_file}</strong> due to CORS restrictions when opening HTML files directly.
                        </p>

                        <div style="background: #fff5f5; border: 2px solid #f56565; border-radius: 8px; padding: 20px; margin-bottom: 20px; text-align: left;">
                            <h3 style="color: #c53030; margin-bottom: 10px;">🔧 How to Fix This:</h3>
                            <p style="color: #4a5568; margin-bottom: 15px;">You need to serve the HTML file using a local web server. Choose one of these options:</p>

                            <div style="background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
                                <p style="margin-bottom: 10px; font-weight: bold;">Option 1: Python HTTP Server (Recommended)</p>
                                <code style="display: block; background: #1a202c; padding: 10px; border-radius: 4px; font-family: monospace;">
                                    cd {os.path.dirname(os.path.abspath('{json_file}')) or '.'}
                                    <br>python -m http.server 8000
                                </code>
                                <p style="margin-top: 10px; font-size: 0.9rem;">Then open: <a href="http://localhost:8000/evaluation_results.html" style="color: #90cdf4;">http://localhost:8000/evaluation_results.html</a></p>
                            </div>

                            <div style="background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
                                <p style="margin-bottom: 10px; font-weight: bold;">Option 2: Node.js HTTP Server</p>
                                <code style="display: block; background: #1a202c; padding: 10px; border-radius: 4px; font-family: monospace;">
                                    npx http-server -p 8000
                                </code>
                            </div>

                            <div style="background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 6px;">
                                <p style="margin-bottom: 10px; font-weight: bold;">Option 3: VS Code Live Server</p>
                                <p style="font-size: 0.9rem;">Right-click the HTML file in VS Code and select "Open with Live Server"</p>
                            </div>
                        </div>

                        <details style="text-align: left; background: #f7fafc; padding: 15px; border-radius: 8px;">
                            <summary style="cursor: pointer; font-weight: bold; color: #2d3748; margin-bottom: 10px;">Show Technical Error Details</summary>
                            <pre style="background: #1a202c; color: #e2e8f0; padding: 15px; border-radius: 4px; overflow-x: auto; margin-top: 10px;">Error: ${{error.message}}</pre>
                        </details>
                    </div>
                `;
            }}
        }}

        // Transform raw evaluation results to expected format
        function transformData() {{
            const total_dialogues = evaluationData[0]?.total_dialogues || 0;
            const total_turns = evaluationData[0]?.total_turns || 0;

            const summary = {{
                total_dialogues: total_dialogues,
                total_turns: total_turns,
                total_configurations: evaluationData.length,
                evaluation_date: evaluationData[0]?.evaluation_date || new Date().toISOString()
            }};

            const formatted_results = [];
            for (const result of evaluationData) {{
                // Flatten all turns from all dialogues
                const all_turns = [];
                for (const dialogue of result.dialogues) {{
                    for (const turn of dialogue.turns) {{
                        const turn_copy = {{ ...turn }};
                        turn_copy.dialogue_id = dialogue.dialogue_id;
                        turn_copy.dialogue_title = dialogue.title;
                        turn_copy.category = dialogue.category;
                        all_turns.push(turn_copy);
                    }}
                }}

                formatted_results.push({{
                    agent_name: result.agent_name,
                    agent_type: result.agent_name.toLowerCase().replace('-', '_'),
                    visualizations_enabled: result.visualizations_enabled,
                    avg_response_time: result.aggregate_scores.avg_response_time,
                    aggregate_scores: result.aggregate_scores,
                    responses: all_turns,
                    dialogues: result.dialogues
                }});
            }}

            evaluationData = {{
                summary: summary,
                results: formatted_results
            }};
        }}

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

            const bestQuality = evaluationData.results.reduce((best, current) =>
                (current.aggregate_scores.avg_overall_quality || 0) > (best.aggregate_scores.avg_overall_quality || 0) ? current : best
            );

            container.innerHTML = `
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Total Dialogues</h3>
                        <div class="value">${{evaluationData.summary.total_dialogues}}</div>
                        <div class="label">${{evaluationData.summary.total_turns}} Total Turns</div>
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
                        <h3>Highest Quality (Judge)</h3>
                        <div class="value">${{bestQuality.agent_name}}</div>
                        <div class="label">${{(bestQuality.aggregate_scores.avg_overall_quality || 0).toFixed(2)}}/5 Rating</div>
                    </div>
                    <div class="metric-card">
                        <h3>Best Context Awareness</h3>
                        <div class="value">${{evaluationData.results.reduce((best, current) =>
                            current.aggregate_scores.context_awareness_rate > best.aggregate_scores.context_awareness_rate ? current : best
                        ).agent_name}}</div>
                        <div class="label">${{(evaluationData.results.reduce((best, current) =>
                            current.aggregate_scores.context_awareness_rate > best.aggregate_scores.context_awareness_rate ? current : best
                        ).aggregate_scores.context_awareness_rate * 100).toFixed(0)}}% Context Aware</div>
                    </div>
                    <div class="metric-card">
                        <h3>Fastest Agent</h3>
                        <div class="value">${{fastestAgent.agent_name}}</div>
                        <div class="label">${{fastestAgent.avg_response_time.toFixed(2)}}s avg</div>
                    </div>
                    <div class="metric-card">
                        <h3>Most Efficient</h3>
                        <div class="value">${{mostEfficient.agent_name}}</div>
                        <div class="label">${{Math.round(mostEfficient.aggregate_scores.avg_total_tokens)}} tokens/turn</div>
                    </div>
                </div>
            `;
        }}

        // Render comparison table
        function renderComparisonTable() {{
            const container = document.getElementById('comparison-table');
            const rows = evaluationData.results.map(result => {{
                const scores = result.aggregate_scores;
                const factuality = scores.avg_factuality || 0;
                const helpfulness = scores.avg_helpfulness || 0;
                const quality = scores.avg_overall_quality || 0;

                // Helper to get score class for judge ratings (out of 5)
                const getJudgeClass = (val) => {{
                    if (val >= 4) return 'high';
                    if (val >= 3) return 'medium';
                    return 'low';
                }};

                return `
                    <tr>
                        <td><div class="agent-label">${{result.agent_name}}</div></td>
                        <td><span class="score ${{getScoreClass(scores.query_validity_rate)}}">${{(scores.query_validity_rate * 100).toFixed(1)}}%</span></td>
                        <td><span class="score ${{getScoreClass(scores.query_pattern_match_rate)}}">${{(scores.query_pattern_match_rate * 100).toFixed(1)}}%</span></td>
                        <td><span class="score ${{getScoreClass(scores.visualization_correctness_rate)}}">${{(scores.visualization_correctness_rate * 100).toFixed(1)}}%</span></td>
                        <td><span class="score ${{getScoreClass(scores.context_awareness_rate)}}">${{(scores.context_awareness_rate * 100).toFixed(1)}}%</span></td>
                        <td><span class="score ${{getJudgeClass(factuality)}}">${{factuality > 0 ? factuality.toFixed(2) : 'N/A'}}</span></td>
                        <td><span class="score ${{getJudgeClass(helpfulness)}}">${{helpfulness > 0 ? helpfulness.toFixed(2) : 'N/A'}}</span></td>
                        <td><span class="score ${{getJudgeClass(quality)}}">${{quality > 0 ? quality.toFixed(2) : 'N/A'}}</span></td>
                        <td>${{result.avg_response_time.toFixed(2)}}s</td>
                        <td>${{Math.round(scores.avg_total_tokens).toLocaleString()}}</td>
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
                            <th>Context Aware</th>
                            <th>Factuality</th>
                            <th>Helpfulness</th>
                            <th>Quality</th>
                            <th>Avg Time</th>
                            <th>Avg Tokens</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${{rows}}
                    </tbody>
                </table>
                <p style="margin-top: 15px; color: #718096; font-size: 0.9rem;">
                    * Factuality, Helpfulness, and Quality rated by LLM Judge on 1-5 scale
                </p>
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
                        }},
                        {{
                            label: 'Context Awareness',
                            data: evaluationData.results.map(r => r.aggregate_scores.context_awareness_rate * 100),
                            backgroundColor: 'rgba(246, 211, 101, 0.8)'
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

        // Create LLM judge ratings chart
        function createJudgeChart() {{
            const ctx = document.getElementById('judgeChart').getContext('2d');
            const labels = evaluationData.results.map(r => r.agent_name);

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [
                        {{
                            label: 'Factuality',
                            data: evaluationData.results.map(r => r.aggregate_scores.avg_factuality || 0),
                            backgroundColor: 'rgba(102, 126, 234, 0.8)'
                        }},
                        {{
                            label: 'Helpfulness',
                            data: evaluationData.results.map(r => r.aggregate_scores.avg_helpfulness || 0),
                            backgroundColor: 'rgba(72, 187, 120, 0.8)'
                        }},
                        {{
                            label: 'Overall Quality',
                            data: evaluationData.results.map(r => r.aggregate_scores.avg_overall_quality || 0),
                            backgroundColor: 'rgba(246, 211, 101, 0.8)'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 5,
                            ticks: {{
                                callback: function(value) {{
                                    return value.toFixed(1);
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '/5';
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

                        // Add judge ratings if available
                        if (r.judge_ratings && r.judge_ratings.judge_success) {{
                            const factuality = r.judge_ratings.factuality;
                            const helpfulness = r.judge_ratings.helpfulness;
                            const quality = r.judge_ratings.overall_quality;

                            badges.push(`<span class="score-badge info">Factuality: ${{factuality}}/5</span>`);
                            badges.push(`<span class="score-badge info">Helpful: ${{helpfulness}}/5</span>`);
                            badges.push(`<span class="score-badge info">Quality: ${{quality}}/5</span>`);
                        }}
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
                            ${{r.generated_sql ? `
                                <div style="margin-top: 10px;">
                                    <strong style="font-size: 0.9rem;">Generated SQL Query:</strong>
                                    <pre style="background: #2d3748; color: #e2e8f0; padding: 10px; border-radius: 4px; font-size: 0.8rem; overflow-x: auto; margin-top: 5px;">${{r.generated_sql}}</pre>
                                </div>
                            ` : ''}}

                            ${{r.expected_query_pattern ? `
                                <div style="margin-top: 10px;">
                                    <strong style="font-size: 0.9rem;">Expected Pattern (Regex):</strong>
                                    <pre style="background: #edf2f7; color: #2d3748; padding: 10px; border-radius: 4px; font-size: 0.8rem; overflow-x: auto; margin-top: 5px; border: 1px solid #cbd5e0;">${{r.expected_query_pattern}}</pre>
                                </div>
                            ` : ''}}

                            <div class="response-preview" id="preview-${{qId}}-${{r.agent}}">
                                ${{hasError ? 'Error: ' + r.error : (r.response || 'No response').substring(0, 200)}}...
                            </div>
                            <button class="expand-btn" onclick="togglePreview('${{qId}}-${{r.agent}}')">Show Full Response</button>

                            ${{r.judge_ratings && r.judge_ratings.judge_success ? `
                                <div style="margin-top: 10px; padding: 10px; background: #edf2f7; border-left: 3px solid #667eea; border-radius: 4px; font-size: 0.85rem;">
                                    <strong>Judge Feedback:</strong>
                                    <div style="margin-top: 5px;">
                                        <div><strong>Factuality:</strong> ${{r.judge_ratings.factuality_reasoning}}</div>
                                        <div style="margin-top: 3px;"><strong>Helpfulness:</strong> ${{r.judge_ratings.helpfulness_reasoning}}</div>
                                        <div style="margin-top: 3px;"><strong>Overall:</strong> ${{r.judge_ratings.overall_reasoning}}</div>
                                    </div>
                                </div>
                            ` : ''}}
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

        // Toggle SQL details row
        function toggleSQLDetails(rowId) {{
            const row = document.getElementById(rowId);
            const button = event.target;

            if (row.style.display === 'none') {{
                row.style.display = 'table-row';
                button.textContent = 'Hide SQL';
            }} else {{
                row.style.display = 'none';
                button.textContent = 'Show SQL';
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

        // Render individual results table
        function renderIndividualResultsTable() {{
            const container = document.getElementById('individual-results-table');

            // Collect all turns from all agents
            const allTurns = [];
            evaluationData.results.forEach(result => {{
                result.dialogues.forEach(dialogue => {{
                    dialogue.turns.forEach(turn => {{
                        allTurns.push({{
                            agent: result.agent_name,
                            dialogue_id: dialogue.dialogue_id,
                            dialogue_title: dialogue.title,
                            category: dialogue.category,
                            turn_id: turn.turn_id,
                            user_message: turn.user_message,
                            response_time: turn.response_time,
                            scores: turn.scores,
                            judge_ratings: turn.judge_ratings,
                            error: turn.error,
                            is_followup: turn.is_followup
                        }});
                    }});
                }});
            }});

            // Create table rows
            const rows = allTurns.map((turn, index) => {{
                const hasError = turn.error ? true : false;
                const scores = turn.scores || {{}};
                const judge = turn.judge_ratings || {{}};

                const queryValid = scores.query_validity === 1;
                const patternMatch = scores.query_pattern_match === 1;
                const vizCorrect = scores.visualization_correctness === 1;
                const contextAware = scores.context_awareness === 1;

                const factuality = judge.factuality || 0;
                const helpfulness = judge.helpfulness || 0;
                const quality = judge.overall_quality || 0;

                // Truncate user message for table
                const truncatedMsg = turn.user_message.length > 80
                    ? turn.user_message.substring(0, 80) + '...'
                    : turn.user_message;

                const rowId = `all-row-${{turn.dialogue_id}}-${{turn.turn_id}}-${{turn.agent.replace(/[^a-zA-Z0-9]/g, '')}}`;

                return `
                    <tr style="${{index % 2 === 0 ? 'background: #f7fafc;' : ''}}">
                        <td style="font-weight: 600;">${{turn.agent}}</td>
                        <td><span style="font-size: 0.85rem; color: #718096;">${{turn.dialogue_id.toUpperCase()}}</span></td>
                        <td style="max-width: 300px; font-size: 0.9rem;">${{truncatedMsg}}</td>
                        <td style="text-align: center;">${{turn.turn_id}}</td>
                        <td style="text-align: center;">
                            <span class="score-badge ${{turn.is_followup ? 'info' : 'success'}}" style="font-size: 0.7rem;">
                                ${{turn.is_followup ? 'Follow-up' : 'First'}}
                            </span>
                        </td>
                        <td style="text-align: center;">
                            ${{hasError ?
                                '<span class="score-badge error" style="font-size: 0.7rem;">ERROR</span>' :
                                (queryValid ? '✅' : '❌')
                            }}
                        </td>
                        <td style="text-align: center;">${{patternMatch ? '✅' : '❌'}}</td>
                        <td style="text-align: center;">${{vizCorrect ? '✅' : '❌'}}</td>
                        <td style="text-align: center;">${{contextAware ? '✅' : '❌'}}</td>
                        <td style="text-align: center; font-weight: 600; color: ${{factuality >= 4 ? '#48bb78' : factuality >= 3 ? '#ed8936' : '#f56565'}};">
                            ${{factuality > 0 ? factuality.toFixed(1) : 'N/A'}}
                        </td>
                        <td style="text-align: center; font-weight: 600; color: ${{helpfulness >= 4 ? '#48bb78' : helpfulness >= 3 ? '#ed8936' : '#f56565'}};">
                            ${{helpfulness > 0 ? helpfulness.toFixed(1) : 'N/A'}}
                        </td>
                        <td style="text-align: center; font-weight: 600; color: ${{quality >= 4 ? '#48bb78' : quality >= 3 ? '#ed8936' : '#f56565'}};">
                            ${{quality > 0 ? quality.toFixed(1) : 'N/A'}}
                        </td>
                        <td style="text-align: center;">${{turn.response_time?.toFixed(2) || 'N/A'}}s</td>
                        <td style="text-align: center;">${{scores.total_tokens?.toLocaleString() || '0'}}</td>
                        <td style="text-align: center;">
                            <button class="expand-btn" onclick="toggleSQLDetails('${{rowId}}')" style="padding: 4px 8px; font-size: 0.75rem;">
                                Show SQL
                            </button>
                        </td>
                    </tr>
                    <tr id="${{rowId}}" style="display: none;">
                        <td colspan="15" style="background: #f7fafc; padding: 15px;">
                            ${{turn.generated_sql ? `
                                <div style="margin-bottom: 10px;">
                                    <strong>Generated SQL:</strong>
                                    <pre style="background: #2d3748; color: #e2e8f0; padding: 10px; border-radius: 4px; font-size: 0.75rem; overflow-x: auto; margin-top: 5px;">${{turn.generated_sql}}</pre>
                                </div>
                            ` : '<div><em>No SQL generated</em></div>'}}
                            ${{turn.expected_query_pattern ? `
                                <div>
                                    <strong>Expected Pattern (Regex):</strong>
                                    <pre style="background: #edf2f7; color: #2d3748; padding: 10px; border-radius: 4px; font-size: 0.75rem; overflow-x: auto; margin-top: 5px; border: 1px solid #cbd5e0;">${{turn.expected_query_pattern}}</pre>
                                </div>
                            ` : ''}}
                        </td>
                    </tr>
                `;
            }}).join('');

            container.innerHTML = `
                <div style="overflow-x: auto;">
                    <table class="comparison-table" style="font-size: 0.9rem;">
                        <thead>
                            <tr>
                                <th style="min-width: 100px;">Agent</th>
                                <th style="min-width: 60px;">Dialogue</th>
                                <th style="min-width: 300px;">User Question</th>
                                <th style="min-width: 50px;">Turn #</th>
                                <th style="min-width: 80px;">Type</th>
                                <th style="min-width: 80px;">Valid SQL</th>
                                <th style="min-width: 80px;">Pattern</th>
                                <th style="min-width: 80px;">Viz</th>
                                <th style="min-width: 80px;">Context</th>
                                <th style="min-width: 80px;">Factual</th>
                                <th style="min-width: 80px;">Helpful</th>
                                <th style="min-width: 80px;">Quality</th>
                                <th style="min-width: 80px;">Time</th>
                                <th style="min-width: 80px;">Tokens</th>
                                <th style="min-width: 80px;">SQL</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${{rows}}
                        </tbody>
                    </table>
                </div>
                <p style="margin-top: 15px; color: #718096; font-size: 0.9rem;">
                    * Factual, Helpful, and Quality columns show LLM Judge ratings (1-5 scale)
                    <br>* ✅ = Pass, ❌ = Fail for automated metrics
                    <br>* Click "Show SQL" to see generated query vs expected pattern
                </p>
            `;
        }}

        // Render per-agent detailed tables
        function renderPerAgentTables() {{
            const container = document.getElementById('per-agent-tables');

            const agentTables = evaluationData.results.map(result => {{
                // Collect all turns for this agent
                const turns = [];
                result.dialogues.forEach(dialogue => {{
                    dialogue.turns.forEach(turn => {{
                        turns.push({{
                            dialogue_id: dialogue.dialogue_id,
                            dialogue_title: dialogue.title,
                            category: dialogue.category,
                            ...turn
                        }});
                    }});
                }});

                // Create rows for this agent
                const rows = turns.map((turn, index) => {{
                    const hasError = turn.error ? true : false;
                    const scores = turn.scores || {{}};
                    const judge = turn.judge_ratings || {{}};

                    const queryValid = scores.query_validity === 1;
                    const patternMatch = scores.query_pattern_match === 1;
                    const vizCorrect = scores.visualization_correctness === 1;
                    const contextAware = scores.context_awareness === 1;

                    const factuality = judge.factuality || 0;
                    const helpfulness = judge.helpfulness || 0;
                    const quality = judge.overall_quality || 0;

                    const rowId = `agent-row-${{turn.dialogue_id}}-${{turn.turn_id}}-${{index}}`;

                    return `
                        <tr style="${{index % 2 === 0 ? 'background: #f7fafc;' : ''}}">
                            <td style="text-align: center;">${{turn.dialogue_id.toUpperCase()}}</td>
                            <td style="text-align: center;">${{turn.turn_id}}</td>
                            <td style="max-width: 400px; font-size: 0.9rem;">${{turn.user_message}}</td>
                            <td style="text-align: center;">
                                ${{hasError ?
                                    '<span class="score-badge error" style="font-size: 0.7rem;">ERROR</span>' :
                                    (queryValid ? '✅' : '❌')
                                }}
                            </td>
                            <td style="text-align: center;">${{patternMatch ? '✅' : '❌'}}</td>
                            <td style="text-align: center;">${{vizCorrect ? '✅' : '❌'}}</td>
                            <td style="text-align: center;">${{contextAware ? '✅' : '❌'}}</td>
                            <td style="text-align: center; font-weight: 600; color: ${{factuality >= 4 ? '#48bb78' : factuality >= 3 ? '#ed8936' : '#f56565'}};">
                                ${{factuality > 0 ? factuality.toFixed(1) : 'N/A'}}
                            </td>
                            <td style="text-align: center; font-weight: 600; color: ${{helpfulness >= 4 ? '#48bb78' : helpfulness >= 3 ? '#ed8936' : '#f56565'}};">
                                ${{helpfulness > 0 ? helpfulness.toFixed(1) : 'N/A'}}
                            </td>
                            <td style="text-align: center; font-weight: 600; color: ${{quality >= 4 ? '#48bb78' : quality >= 3 ? '#ed8936' : '#f56565'}};">
                                ${{quality > 0 ? quality.toFixed(1) : 'N/A'}}
                            </td>
                            <td style="text-align: center;">${{turn.response_time?.toFixed(2) || 'N/A'}}s</td>
                            <td style="text-align: center;">${{scores.total_tokens?.toLocaleString() || '0'}}</td>
                            <td style="text-align: center;">
                                <button class="expand-btn" onclick="toggleSQLDetails('${{rowId}}')" style="padding: 4px 8px; font-size: 0.75rem;">
                                    Show SQL
                                </button>
                            </td>
                        </tr>
                        <tr id="${{rowId}}" style="display: none;">
                            <td colspan="13" style="background: #f7fafc; padding: 15px;">
                                ${{turn.generated_sql ? `
                                    <div style="margin-bottom: 10px;">
                                        <strong>Generated SQL:</strong>
                                        <pre style="background: #2d3748; color: #e2e8f0; padding: 10px; border-radius: 4px; font-size: 0.75rem; overflow-x: auto; margin-top: 5px;">${{turn.generated_sql}}</pre>
                                    </div>
                                ` : '<div><em>No SQL generated</em></div>'}}
                                ${{turn.expected_query_pattern ? `
                                    <div>
                                        <strong>Expected Pattern (Regex):</strong>
                                        <pre style="background: #edf2f7; color: #2d3748; padding: 10px; border-radius: 4px; font-size: 0.75rem; overflow-x: auto; margin-top: 5px; border: 1px solid #cbd5e0;">${{turn.expected_query_pattern}}</pre>
                                    </div>
                                ` : ''}}
                            </td>
                        </tr>
                    `;
                }}).join('');

                // Calculate agent summary stats
                const validTurns = turns.filter(t => !t.error);
                const avgFactuality = validTurns.reduce((sum, t) => sum + (t.judge_ratings?.factuality || 0), 0) / validTurns.length;
                const avgHelpfulness = validTurns.reduce((sum, t) => sum + (t.judge_ratings?.helpfulness || 0), 0) / validTurns.length;
                const avgQuality = validTurns.reduce((sum, t) => sum + (t.judge_ratings?.overall_quality || 0), 0) / validTurns.length;

                return `
                    <div class="category-card">
                        <h3 style="display: flex; justify-content: space-between; align-items: center;">
                            <span>${{result.agent_name}} - Detailed Results</span>
                            <span style="font-size: 0.9rem; font-weight: normal; color: #718096;">
                                Avg Judge Scores: Factual ${{avgFactuality.toFixed(2)}}, Helpful ${{avgHelpfulness.toFixed(2)}}, Quality ${{avgQuality.toFixed(2)}}
                            </span>
                        </h3>
                        <div style="overflow-x: auto; margin-top: 15px;">
                            <table class="comparison-table" style="font-size: 0.85rem;">
                                <thead>
                                    <tr>
                                        <th>Dialogue</th>
                                        <th>Turn</th>
                                        <th style="min-width: 400px;">Question</th>
                                        <th>Valid SQL</th>
                                        <th>Pattern</th>
                                        <th>Viz</th>
                                        <th>Context</th>
                                        <th>Factual</th>
                                        <th>Helpful</th>
                                        <th>Quality</th>
                                        <th>Time</th>
                                        <th>Tokens</th>
                                        <th>SQL</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{rows}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            }}).join('');

            container.innerHTML = agentTables;
        }}

        // Initialize all visualizations
        function initializeVisualizations() {{
            renderOverview();
            renderComparisonTable();
            createValidityChart();
            createTokenChart();
            createTimeChart();
            createCostChart();
            createJudgeChart();
            renderCostTable();
            renderQuestionResults();
            renderCategoryResults();
            renderIndividualResultsTable();
            renderPerAgentTables();
        }}

        // Load data when page loads
        window.addEventListener('DOMContentLoaded', () => {{
            loadEvaluationData();
        }});
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

    # Add dialogue and turn info
    total_dialogues = all_results[0]['total_dialogues'] if all_results else 0
    total_turns = all_results[0]['total_turns'] if all_results else 0
    viz_enabled = all_results[0]['visualizations_enabled'] if all_results else True

    report.append(f"\n**Total Dialogues:** {total_dialogues}")
    report.append(f"\n**Total Conversation Turns:** {total_turns}")
    report.append(f"\n**Visualizations:** {'ENABLED' if viz_enabled else 'DISABLED'}\n")

    # Summary table
    report.append("## Performance Summary\n")
    report.append("| Agent | Query Validity | Pattern Match | Viz Correct | Context Aware | Avg Time (s) | Recommendations |\n")
    report.append("|-------|----------------|---------------|-------------|---------------|--------------|------------------|\n")

    for result in all_results:
        scores = result["aggregate_scores"]
        report.append(
            f"| {result['agent_name']} | "
            f"{scores['query_validity_rate']:.1%} | "
            f"{scores['query_pattern_match_rate']:.1%} | "
            f"{scores['visualization_correctness_rate']:.1%} | "
            f"{scores['context_awareness_rate']:.1%} | "
            f"{scores['avg_response_time']:.2f} | "
            f"{scores['recommendations_rate']:.1%} |\n"
        )

    # LLM Judge Ratings table
    if all_results and all_results[0].get("use_judge"):
        report.append("\n## LLM-as-a-Judge Ratings (1-5 Scale)\n")
        report.append("| Agent | Factuality | Helpfulness | Overall Quality | Judge Success Rate |\n")
        report.append("|-------|------------|-------------|-----------------|--------------------|\n")

        for result in all_results:
            scores = result["aggregate_scores"]
            if scores.get("avg_factuality", 0) > 0:
                report.append(
                    f"| {result['agent_name']} | "
                    f"{scores.get('avg_factuality', 0):.2f}/5 | "
                    f"{scores.get('avg_helpfulness', 0):.2f}/5 | "
                    f"{scores.get('avg_overall_quality', 0):.2f}/5 | "
                    f"{scores.get('judge_success_rate', 0):.1%} |\n"
                )

    # Token usage table
    report.append("\n## Token Usage Summary\n")
    report.append("| Agent | Total Tokens | Avg Tokens/Turn | Input Tokens | Output Tokens |\n")
    report.append("|-------|--------------|-----------------|--------------|---------------|\n")

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
    report.append("| Agent | Total Cost | Cost/Turn | Input Cost | Output Cost |\n")
    report.append("|-------|------------|-----------|------------|-------------|\n")

    for result in all_results:
        scores = result["aggregate_scores"]
        total_cost = calculate_cost(scores['total_input_tokens'], scores['total_output_tokens'])
        cost_per_turn = total_cost / result['total_turns'] if result['total_turns'] > 0 else 0
        input_cost = calculate_cost(scores['total_input_tokens'], 0)
        output_cost = calculate_cost(0, scores['total_output_tokens'])

        report.append(
            f"| {result['agent_name']} | "
            f"${total_cost:.4f} | "
            f"${cost_per_turn:.4f} | "
            f"${input_cost:.4f} | "
            f"${output_cost:.4f} |\n"
        )

    # Detailed results by dialogue category
    report.append("\n## Results by Dialogue Category\n")

    categories = set()
    for result in all_results:
        for dialogue in result["dialogues"]:
            if "category" in dialogue:
                categories.add(dialogue["category"])

    for category in sorted(categories):
        report.append(f"\n### {category.replace('_', ' ').title()}\n")

        for result in all_results:
            cat_dialogues = [d for d in result["dialogues"] if d.get("category") == category]
            if cat_dialogues:
                # Count valid turns across all dialogues in this category
                total_turns = sum(len(d["turns"]) for d in cat_dialogues)
                valid_turns = sum(
                    1 for d in cat_dialogues for t in d["turns"]
                    if "error" not in t and t.get("scores", {}).get("query_validity") == 1
                )
                report.append(
                    f"- **{result['agent_name']}**: {valid_turns}/{total_turns} valid turns "
                    f"across {len(cat_dialogues)} dialogue(s)\n"
                )

    # Winner analysis
    report.append("\n## Best Performer by Metric\n")

    metrics = ["query_validity_rate", "query_pattern_match_rate", "visualization_correctness_rate", "context_awareness_rate", "recommendations_rate"]
    metric_names = ["Query Validity", "Pattern Match", "Visualization Correctness", "Context Awareness", "Recommendations Rate"]

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
        f"{most_efficient['aggregate_scores']['avg_total_tokens']:.0f} tokens/turn avg\n"
    )

    # Most cost-effective agent (lowest cost per turn)
    def get_cost_per_turn(result):
        scores = result["aggregate_scores"]
        total_cost = calculate_cost(scores['total_input_tokens'], scores['total_output_tokens'])
        return total_cost / result['total_turns'] if result['total_turns'] > 0 else float('inf')

    most_cost_effective = min(all_results, key=get_cost_per_turn)
    cost_pt = get_cost_per_turn(most_cost_effective)
    report.append(
        f"- **Most Cost-Effective:** {most_cost_effective['agent_name']} - "
        f"${cost_pt:.4f}/turn avg\n"
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

    # Initialize OpenAI client for LLM judge
    judge_client = OpenAI(api_key=api_key)

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
            dialogues=EVALUATION_DIALOGUES,
            enable_viz=enable_viz,
            use_judge=True,
            judge_client=judge_client
        )
        # Add evaluation date to each result
        result["evaluation_date"] = datetime.now().isoformat()
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

    # Generate and save HTML report (references the JSON file)
    print(f"📊 Generating HTML report to {args.html}...")
    # Extract just the filename from the JSON path for relative reference
    json_filename = os.path.basename(args.output)
    generate_html_report(args.html, json_filename)

    # Print summary
    print("\n" + "="*80)
    print("EVALUATION COMPLETE")
    print("="*80)
    print(f"Evaluated {len(agents)} agents")
    print(f"Visualizations: {'ENABLED' if enable_viz else 'DISABLED'}")
    print(f"Total dialogues: {len(EVALUATION_DIALOGUES)}")
    total_turns = sum(len(d["turns"]) for d in EVALUATION_DIALOGUES)
    print(f"Total conversation turns: {total_turns}")
    print(f"\n📁 Files Generated:")
    print(f"  • JSON Results: {args.output}")
    print(f"  • Markdown Report: {args.report}")
    print(f"  • HTML Report: {args.html}")

    print(f"\n🌐 To View HTML Report:")
    print(f"  The HTML file loads data from {os.path.basename(args.output)}")
    print(f"  You must serve it via HTTP (CORS restriction). Run one of:")
    print(f"\n  Option 1 (Python):")
    print(f"    cd {os.path.dirname(os.path.abspath(args.output)) or '.'}")
    print(f"    python -m http.server 8000")
    print(f"    # Then open: http://localhost:8000/{os.path.basename(args.html)}")
    print(f"\n  Option 2 (npx):")
    print(f"    npx http-server -p 8000")
    print(f"\n  Option 3 (VS Code):")
    print(f"    Right-click {args.html} → 'Open with Live Server'")

    print("\nSummary:")

    for result in all_results:
        print(f"\n{result['agent_name']}:")
        print(f"  Query Validity: {result['aggregate_scores']['query_validity_rate']:.1%}")
        print(f"  Context Awareness: {result['aggregate_scores']['context_awareness_rate']:.1%}")
        if result.get("use_judge") and result['aggregate_scores'].get('avg_factuality', 0) > 0:
            print(f"  Judge Ratings:")
            print(f"    Factuality: {result['aggregate_scores']['avg_factuality']:.2f}/5")
            print(f"    Helpfulness: {result['aggregate_scores']['avg_helpfulness']:.2f}/5")
            print(f"    Overall Quality: {result['aggregate_scores']['avg_overall_quality']:.2f}/5")
        print(f"  Avg Response Time: {result['aggregate_scores']['avg_response_time']:.2f}s")
        print(f"  Error Rate: {result['aggregate_scores']['error_rate']:.1%}")
        print(f"  Total Tokens: {result['aggregate_scores']['total_tokens']:,}")
        print(f"  Avg Tokens/Turn: {result['aggregate_scores']['avg_total_tokens']:.0f}")


if __name__ == "__main__":
    main()
