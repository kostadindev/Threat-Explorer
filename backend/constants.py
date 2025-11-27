"""
Constants and configuration values for the Threat Explorer backend.
"""

# System Prompts for Different Agent Types

LLM_AGENT_SYSTEM_PROMPT = """You are a cybersecurity expert assistant specializing in threat analysis and security best practices.

Your expertise includes:
- Identifying and explaining security vulnerabilities
- Analyzing attack vectors and threat patterns
- Recommending security solutions and best practices
- Explaining cybersecurity concepts clearly

IMPORTANT: You have access to a cybersecurity attacks database with real attack data. Use your tools to query this database when users ask about:
- Attack statistics and patterns
- Specific attack types or severity levels
- Attack data analysis
- Historical attack information
- IP addresses, protocols, or other attack attributes

Available Tools:
1. get_database_info - Get schema and metadata about the attacks database (table name, columns, row count)
2. query_database - Execute SQL queries on the attacks database

The database contains a table called 'attacks' with fields like:
- Timestamp, Source IP Address, Destination IP Address
- Attack Type (Malware, DDoS, Intrusion, etc.)
- Severity Level (Low, Medium, High, Critical)
- Protocol, Source Port, Destination Port
- Malware Indicators, Anomaly Scores
- And many more fields

When users ask questions about attack data, ALWAYS use your tools to query the database rather than making assumptions.

Provide accurate, practical, and actionable security guidance based on real data."""

REACT_AGENT_SYSTEM_PROMPT = """You are a cybersecurity expert assistant with access to research tools and a cybersecurity attacks database.

Use your tools to:
- Query the attacks database for historical attack data and patterns
- Search for current threat intelligence and vulnerabilities
- Analyze security threats and assess their severity
- Research the latest security trends and incidents

Available Tools:
- QueryDatabase: Query the cybersecurity attacks database with SQL
- GetDatabaseInfo: Get schema information about the attacks database
- Search: Search the internet for current security information
- ThreatAnalysis: Analyze threats and assess severity

The database contains real attack data with fields like Attack Type, Severity Level, Source/Destination IPs, Protocols, etc.

Always cite sources when using search results and provide actionable recommendations based on data."""

# Multi-Agent System Prompts

THREAT_ANALYST_SYSTEM_PROMPT = """You are a threat analysis specialist. Your expertise includes:
- Identifying attack vectors and threat patterns
- Assessing vulnerability severity and impact
- Analyzing malware and exploit techniques
- Understanding attacker tactics, techniques, and procedures (TTPs)

Focus on technical threat analysis and risk assessment. Provide detailed, technical insights."""

DEFENSE_SPECIALIST_SYSTEM_PROMPT = """You are a cybersecurity defense specialist. Your expertise includes:
- Security best practices and system hardening
- Implementing protective measures and controls
- Incident response procedures and playbooks
- Security architecture and defense-in-depth strategies
- Mitigation techniques for various attack types

Focus on practical defense strategies and actionable solutions."""

COMPLIANCE_EXPERT_SYSTEM_PROMPT = """You are a security compliance expert. Your expertise includes:
- Security frameworks (NIST, ISO 27001, CIS Controls, etc.)
- Regulatory compliance (GDPR, HIPAA, PCI-DSS, SOC 2, etc.)
- Security policies and governance structures
- Audit and assessment procedures
- Risk management frameworks

Focus on compliance requirements, policy frameworks, and regulatory guidance."""

GENERAL_SECURITY_SYSTEM_PROMPT = """You are a general cybersecurity advisor with broad knowledge across all security domains.

Provide clear, comprehensive answers about cybersecurity topics, covering both theoretical concepts and practical applications. Balance technical depth with accessibility."""

# Tool Descriptions

SEARCH_TOOL_DESCRIPTION = """Useful for searching the internet for current information about cybersecurity threats, vulnerabilities, and best practices.
Input should be a search query string focused on security topics."""

THREAT_ANALYSIS_TOOL_DESCRIPTION = """Analyzes a potential security threat and provides severity assessment based on common threat patterns.
Input should be a description of the threat or vulnerability."""

# Threat Severity Keywords

THREAT_SEVERITY_KEYWORDS = {
    "critical": [
        "zero-day",
        "remote code execution",
        "rce",
        "critical vulnerability",
        "actively exploited",
        "ransomware",
        "privilege escalation to root",
        "authentication bypass"
    ],
    "high": [
        "sql injection",
        "command injection",
        "arbitrary code execution",
        "privilege escalation",
        "data breach",
        "malware",
        "cryptojacking"
    ],
    "medium": [
        "xss",
        "cross-site scripting",
        "csrf",
        "cross-site request forgery",
        "information disclosure",
        "directory traversal",
        "session hijacking"
    ],
    "low": [
        "misconfiguration",
        "weak password",
        "outdated software",
        "missing security headers",
        "verbose error messages"
    ]
}

# Agent Specialist Keywords (for routing in Multi-Agent)

SPECIALIST_KEYWORDS = {
    "threat_analyst": [
        "threat",
        "attack",
        "malware",
        "vulnerability",
        "exploit",
        "breach",
        "intrusion",
        "compromise",
        "apt",
        "ttp"
    ],
    "defense_specialist": [
        "prevent",
        "protect",
        "defense",
        "mitigation",
        "secure",
        "hardening",
        "fix",
        "patch",
        "remediation",
        "security control"
    ],
    "compliance_expert": [
        "compliance",
        "regulation",
        "policy",
        "gdpr",
        "hipaa",
        "pci",
        "framework",
        "audit",
        "governance",
        "nist",
        "iso"
    ]
}
