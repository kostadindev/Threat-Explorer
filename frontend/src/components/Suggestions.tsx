import React from "react";
import { Button } from "antd";

interface SuggestionsProps {
  suggestions: string[];
  isDarkMode: boolean;
  onSuggestionClick: (suggestion: string) => void;
}

export const Suggestions: React.FC<SuggestionsProps> = ({
  suggestions,
  isDarkMode,
  onSuggestionClick,
}) => {
  if (suggestions.length === 0) return null;

  return (
    <div
      className="px-4 pt-2 pb-2 flex flex-wrap gap-2"
      style={{
        backgroundColor: isDarkMode ? "#121212" : "#ffffff",
      }}
    >
      {suggestions.map((text, index) => (
        <Button
          key={index}
          onClick={() => onSuggestionClick(text)}
          size="middle"
          style={{
            backgroundColor: isDarkMode ? "#1f1f1f" : "#f5f5f5",
            borderRadius: "9999px",
            transition: "all 0.2s ease-in-out",
          }}
        >
          {text}
        </Button>
      ))}
    </div>
  );
};
