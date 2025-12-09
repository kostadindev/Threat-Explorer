#!/usr/bin/env python3
"""
Test script to demonstrate tool call logging.
Run this after starting the backend server to see tool calls in action.
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"


def test_llm_agent_query():
    """Test LLM agent with a database query"""
    print("\n" + "=" * 80)
    print("🧪 Testing LLM Agent with Database Query")
    print("=" * 80 + "\n")

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "history": [
                {
                    "role": "user",
                    "content": "How many malware attacks are in the database?"
                }
            ],
            "agent_type": "llm"
        }
    )

    print("Response:")
    print(response.text)
    print("\n")


def test_react_agent_query():
    """Test ReAct agent with a database query"""
    print("\n" + "=" * 80)
    print("🧪 Testing ReAct Agent with Database Query")
    print("=" * 80 + "\n")

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "history": [
                {
                    "role": "user",
                    "content": "What are the top 3 most common attack types in the database?"
                }
            ],
            "agent_type": "react"
        }
    )

    print("Response:")
    print(response.text)
    print("\n")


def test_direct_query():
    """Test direct database query endpoint"""
    print("\n" + "=" * 80)
    print("🧪 Testing Direct Database Query Endpoint")
    print("=" * 80 + "\n")

    response = requests.post(
        f"{BASE_URL}/query",
        json={
            "sql": "SELECT \"Attack Type\", COUNT(*) as count FROM attacks GROUP BY \"Attack Type\" ORDER BY count DESC LIMIT 5"
        }
    )

    print("Response:")
    print(json.dumps(response.json(), indent=2))
    print("\n")


def test_database_info():
    """Test database info endpoint"""
    print("\n" + "=" * 80)
    print("🧪 Testing Database Info Endpoint")
    print("=" * 80 + "\n")

    response = requests.get(f"{BASE_URL}/db/info")

    info = response.json()
    print(f"Table: {info['table_name']}")
    print(f"Total rows: {info['row_count']}")
    print(f"Columns: {len(info['columns'])}")
    print("\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🔬 THREAT EXPLORER - Tool Call Logging Tests")
    print("=" * 80)
    print("\nMake sure the backend server is running on http://localhost:8000")
    print("Check the server console to see detailed tool call logs!\n")

    try:
        # Test endpoints
        test_database_info()
        test_direct_query()
        test_llm_agent_query()
        # test_react_agent_query()  # Uncomment to test ReAct agent (takes longer)

        print("\n" + "=" * 80)
        print("✅ All tests completed!")
        print("=" * 80 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the backend is running: cd backend && python main.py\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
