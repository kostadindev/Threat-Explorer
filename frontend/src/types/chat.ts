export interface Message {
  content: string;
  role: "user" | "system" | "assistant";
  agentType?: "llm" | "react" | "multi";
}

export interface ChatError extends Error {
  name: string;
  message: string;
}

export interface ChatResponse {
  history: Message[];
}

export interface SuggestionResponse {
  suggestions: string[];
} 