import { Message, SuggestionResponse } from '../types/chat';

// Use relative URL in production, or VITE_API_URL if set, or localhost for dev
const API_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.PROD ? "" : "http://localhost:8000");

export type AgentType = "llm" | "react" | "multi";

export const chatService = {
  async sendMessage(history: Message[], agentType: AgentType, enableVisualizations: boolean = true, conversationId: string, signal?: AbortSignal): Promise<ReadableStream<Uint8Array> | null> {
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        history,
        agent_type: agentType,
        enable_visualizations: enableVisualizations,
        conversation_id: conversationId
      }),
      signal,
    });

    if (!response.ok) {
      throw new Error(`Network error: ${response.statusText}`);
    }

    return response.body;
  },

  async getSuggestions(history: Message[]): Promise<string[]> {
    const response = await fetch(`${API_URL}/suggest-followups`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history }),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch suggestions');
    }

    const data: SuggestionResponse = await response.json();
    return data.suggestions || [];
  },

  async wakeUpServer(): Promise<void> {
    try {
      await fetch(`${API_URL}/ping`, { method: "GET" });
    } catch (err) {
      console.warn("Server wake-up failed:", err);
    }
  }
}; 