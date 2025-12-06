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
    "Compare DDoS vs Malware attack frequency",
    "Which source IPs have the most attacks?",
    "Show me attack patterns by network segment",
  ],
  chatDescription: `
## Welcome to Threat Explorer @spin[🛡️]

Analyze real cybersecurity attack data through natural language queries.

**What you can explore:**
* Attack patterns by type, severity, protocol, and source
* Threat intelligence with malware indicators and anomaly scores
* Network analysis across IPs, ports, and geographic locations
* Security insights from IDS/IPS alerts and firewall logs

Try the suggested prompts below or ask anything about cybersecurity threats!
  `.trim(),
  features: {
    enableParticles: true,
    enableHexagons: true,
  }
} as const satisfies Config;

// Agent-specific descriptions
export const AGENT_DESCRIPTIONS = {
  llm: `
## Welcome to Threat Explorer @spin[🛡️]

**LLM Agent with Function Calling** - Analyzes attack data using AI-powered database queries.

Query our cybersecurity database using natural language. The LLM agent uses function calling to automatically retrieve and visualize data.

**Capabilities:** Attack analysis • Threat patterns • Security insights • Interactive visualizations

Try the suggested prompts below!
  `.trim(),

  react: `
## Welcome to Threat Explorer @spin[🛡️]

**ReACT Agent** - Iterative reasoning with autonomous tool use for deep analysis.

Ask complex questions and watch the agent reason through multiple steps, querying data and building comprehensive answers.

**Capabilities:** Multi-step analysis • Iterative reasoning • Autonomous data retrieval • Detailed insights

Try the suggested prompts below!
  `.trim(),

  multi: `
## Welcome to Threat Explorer @spin[🛡️]

**Multi-Agent System** - Collaborative AI powered by 3 specialized agents.

**Agent Pipeline:**
🔍 **SQL Builder** → Translates questions into database queries
🎯 **Threat Analyst** → Analyzes patterns and security implications
📊 **Report Formatter** → Creates visualizations and actionable insights

**Capabilities:** Comprehensive analysis • Expert insights • Professional reports • Interactive charts

Try the suggested prompts below!
  `.trim(),
} as const;

/**
 * Get the appropriate chat description based on the selected agent type
 */
export function getChatDescription(agentType?: string): string {
  if (!agentType || !(agentType in AGENT_DESCRIPTIONS)) {
    return UI_CONFIG.chatDescription || '';
  }
  return AGENT_DESCRIPTIONS[agentType as keyof typeof AGENT_DESCRIPTIONS];
}

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
