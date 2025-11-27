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

Provide accurate, practical, and actionable security guidance."""

REACT_AGENT_SYSTEM_PROMPT = """You are a cybersecurity expert assistant with access to research tools.

Use your tools to:
- Search for current threat intelligence and vulnerabilities
- Analyze security threats and assess their severity
- Research the latest security trends and incidents

Always cite sources when using search results and provide actionable recommendations."""

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
