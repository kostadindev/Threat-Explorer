export interface Message {
  content: string;
  role: "user" | "system" | "assistant";
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