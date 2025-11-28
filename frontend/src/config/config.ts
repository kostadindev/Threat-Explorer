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
  inputPlaceholder: "Ask about Threat Explorer",
  maxInputLength: 256,
  defaultPrompts: [
    "Attack type distribution",
    "Attack severity breakdown",
    "Recent malware patterns in a pie",
    "Attacks by source IP in a bar",
  ],
  chatDescription: `
## Welcome to Threat Explorer @spin[🛡️]

Your cybersecurity analysis assistant with access to real attack data. Ask me about:

* Attack statistics and patterns from our database
* Security threats and vulnerability analysis
* Attack trends by type, severity, or source
* Security best practices and recommendations

Try one of the suggested prompts below or ask me anything about cybersecurity!
  `.trim(),
  features: {
    enableParticles: true,
    enableHexagons: true,
  }
} as const satisfies Config;











// Default values for optional fields
export const DEFAULT_MAX_INPUT_LENGTH = 256;
export const DEFAULT_NAME = "AI Assistant";
export const DEFAULT_INPUT_PLACEHOLDER = "Ask me anything...";
export const DEFAULT_PROMPTS = [
  "Attack type distribution",
  "Attack severity breakdown",
  "Recent malware patterns",
  "Attacks by source IP",
]; 