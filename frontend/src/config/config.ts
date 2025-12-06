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
  llm: {
    withViz: `
## Welcome to Threat Explorer @spin[🛡️]

**LLM Agent with Function Calling** • **Visualizations: ON** 📊

Query our cybersecurity database using natural language. The LLM agent uses function calling to automatically retrieve data and generate interactive visualizations.

**Capabilities:** Attack analysis • Threat patterns • Interactive tables & charts • Security insights

Try the suggested prompts below!
    `.trim(),
    withoutViz: `
## Welcome to Threat Explorer @spin[🛡️]

**LLM Agent with Function Calling** • **Visualizations: OFF** 📝

Query our cybersecurity database using natural language. The LLM agent uses function calling to automatically retrieve data and present it as clear, readable text.

**Capabilities:** Attack analysis • Threat patterns • Text-based reports • Security insights

Try the suggested prompts below!
    `.trim(),
  },

  react: {
    withViz: `
## Welcome to Threat Explorer @spin[🛡️]

**ReACT Agent** • **Visualizations: ON** 📊

Iterative reasoning with autonomous tool use for deep analysis. Watch the agent reason through multiple steps, querying data and building comprehensive visualized answers.

**Capabilities:** Multi-step analysis • Iterative reasoning • Interactive charts • Detailed insights

Try the suggested prompts below!
    `.trim(),
    withoutViz: `
## Welcome to Threat Explorer @spin[🛡️]

**ReACT Agent** • **Visualizations: OFF** 📝

Iterative reasoning with autonomous tool use for deep analysis. Watch the agent reason through multiple steps, querying data and building comprehensive text-based answers.

**Capabilities:** Multi-step analysis • Iterative reasoning • Text-based reports • Detailed insights

Try the suggested prompts below!
    `.trim(),
  },

  multi: {
    withViz: `
## Welcome to Threat Explorer @spin[🛡️]

**Multi-Agent System** • **Visualizations: ON** 📊

Collaborative AI powered by 3 specialized agents working together.

**Agent Pipeline:**
🔍 **SQL Builder** → Translates questions into database queries
🎯 **Threat Analyst** → Analyzes patterns and security implications
📊 **Report Formatter** → Creates interactive visualizations and insights

**Capabilities:** Comprehensive analysis • Expert insights • Interactive charts & tables • Professional reports

Try the suggested prompts below!
    `.trim(),
    withoutViz: `
## Welcome to Threat Explorer @spin[🛡️]

**Multi-Agent System** • **Visualizations: OFF** 📝

Collaborative AI powered by 3 specialized agents working together.

**Agent Pipeline:**
🔍 **SQL Builder** → Translates questions into database queries
🎯 **Threat Analyst** → Analyzes patterns and security implications
📝 **Report Formatter** → Creates clear text-based reports and insights

**Capabilities:** Comprehensive analysis • Expert insights • Text-based reports • Professional summaries

Try the suggested prompts below!
    `.trim(),
  },
} as const;

/**
 * Get the appropriate chat description based on the selected agent type and visualization setting
 */
export function getChatDescription(agentType?: string, showVisualizations: boolean = true): string {
  if (!agentType || !(agentType in AGENT_DESCRIPTIONS)) {
    return UI_CONFIG.chatDescription || '';
  }
  const agentDesc = AGENT_DESCRIPTIONS[agentType as keyof typeof AGENT_DESCRIPTIONS];
  return showVisualizations ? agentDesc.withViz : agentDesc.withoutViz;
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
