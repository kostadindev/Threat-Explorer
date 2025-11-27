export const UI_CONFIG = {
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
# Hi! I'm AI Kostadin @spin[🤖]

I'm here to chat about my work and expertise. Feel free to ask me about:

* My projects and technical experience
* My work history and achievements

Try one of the suggested prompts below or ask me anything!
  `.trim(),
} as const; 