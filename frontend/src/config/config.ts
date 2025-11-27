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
  name: "AI Kostadin",
  inputPlaceholder: "Ask about Kostadin's work",
  maxInputLength: 256,
  defaultPrompts: [
    "Current project?",
    "What's Recursive QA?",
    "Formal ML coursework?",
    "Explain Deep Gestures",
  ],
  chatDescription: `
## Hi! I'm AI Kostadin @spin[🤖]

I'm here to chat about my work and expertise. Feel free to ask me about:

* My projects and technical experience
* My work history and achievements

Try one of the suggested prompts below or ask me anything!
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
export const DEFAULT_PROMPTS = ["Tell me about yourself", "What can you do?"]; 