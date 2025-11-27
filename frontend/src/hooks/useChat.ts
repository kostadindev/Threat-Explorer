import { useState, useCallback, useRef, useEffect } from 'react';
import { Message } from '../types/chat';
import { chatService } from '../services/chatService';

const CHAT_HISTORY_KEY = "chat_history";

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleMessagesLoad = useCallback((loadedMessages: Message[]) => {
    setMessages(loadedMessages);
  }, []);

  const clearChat = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setMessages([]);
    setSuggestions([]);
    setIsSending(false);
    setIsTyping(false);
    localStorage.removeItem(CHAT_HISTORY_KEY);
  }, []);

  const sendMessage = useCallback(async (messageToSend: string) => {
    if (isSending || !messageToSend.trim()) return;

    const userMessage: Message = { content: messageToSend, role: "user" };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setIsSending(true);
    setSuggestions([]);

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const stream = await chatService.sendMessage(newMessages, controller.signal);
      if (!stream) return;

      setMessages((prev) => [...prev, { content: "", role: "assistant" }]);
      setIsTyping(true);

      const reader = stream.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunkValue = decoder.decode(value, { stream: true });
        setIsTyping(false);
        setMessages((prev) => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;
          updated[lastIndex] = {
            ...updated[lastIndex],
            content: updated[lastIndex].content + chunkValue,
          };
          return updated;
        });
      }

      const suggestions = await chatService.getSuggestions([
        ...newMessages,
        {
          content: messages[messages.length - 1]?.content || "Let me know how else I can help.",
          role: "assistant",
        },
      ]);
      setSuggestions(suggestions);
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        console.log("Request was aborted");
      } else {
        const errorMessage: Message = {
          content: "Error fetching response: " + (error instanceof Error ? error.message : "Unknown error"),
          role: "assistant",
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } finally {
      setIsSending(false);
      setIsTyping(false);
    }
  }, [messages, isSending]);

  useEffect(() => {
    chatService.wakeUpServer();
  }, []);

  return {
    messages,
    input,
    setInput,
    isSending,
    isTyping,
    suggestions,
    clearChat,
    sendMessage,
    onMessagesLoad: handleMessagesLoad,
  };
}; 