interface Config {
  /** The name displayed in the header of the chat interface */
  name?: string;

  /** Placeholder text shown in the input field when empty */
  inputPlaceholder?: string;

  /** Maximum number of characters allowed in user input messages */
  maxInputLength?: number;

  /** List of suggested prompts shown as clickable buttons below the chat */
  defaultPrompts?: string[];

  /** Welcome message shown in markdown format. Supports @spin[emoji] for animated emojis */
  chatDescription?: string;

  /** Optional UI enhancement features */
  features?: {
    /** Enable/disable interactive particle background effect */
    enableParticles?: boolean;

    /** Enable/disable hexagonal pattern overlay */
    enableHexagons?: boolean;
  };
}


export const UI_CONFIG: Config = {
  name: "Threat Explorer",
  inputPlaceholder: "Ask about attacks, threats, or security best practices...",
  maxInputLength: 512,
  defaultPrompts: [
    "Show me the top 10 attack types",
    "What protocols are most targeted?",
    "Critical severity attacks this month",
    "Compare DDoS vs Malware attack frequency",
    "Which source IPs have the most attacks?",
    "Show me attack patterns by network segment",
  ],
  chatDescription: `
## Welcome to Threat Explorer @spin[🛡️]

**AI-Powered Threat Intelligence Platform** with multi-agent analysis capabilities.

Explore real attack data through natural language queries. Our specialized AI agents analyze:

* **Attack Patterns** - Distribution by type, severity, protocol, and source
* **Threat Intelligence** - Malware indicators, anomaly scores, and signatures
* **Network Analysis** - Traffic patterns, ports, IP addresses, and geographic data
* **Security Insights** - IDS/IPS alerts, firewall logs, and incident response

**Powered by 3 specialized AI agents:**
- 🔍 SQL Builder - Translates your questions into precise database queries
- 🎯 Threat Analyst - Analyzes patterns and identifies security insights
- 📊 Report Formatter - Presents findings with interactive visualizations

Try the suggested prompts below or ask anything about cybersecurity threats!
  `.trim(),
  features: {
    enableParticles: true,
    enableHexagons: true,
  }
} as const satisfies Config;











// Default values for optional fields
export const DEFAULT_MAX_INPUT_LENGTH = 512;
export const DEFAULT_NAME = "Threat Explorer";
export const DEFAULT_INPUT_PLACEHOLDER = "Ask about attacks, threats, or security...";
export const DEFAULT_PROMPTS = [
  "Show me the top 10 attack types",
  "What protocols are most targeted?",
  "Critical severity attacks this month",
  "Compare DDoS vs Malware attack frequency",
]; 