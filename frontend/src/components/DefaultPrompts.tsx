import React from "react";
import { Button } from "antd";

interface Props {
  onPromptSelect: (prompt: string) => void;
  isDarkMode: boolean;
  cardBackground: string;
  prompts: readonly string[];
}

const DefaultPrompts: React.FC<Props> = ({
  onPromptSelect,
  isDarkMode,
  prompts,
}) => {
  return (
    <div className="flex flex-col justify-end items-center text-center px-6 pb-4 max-w-3xl mx-auto h-full w-full">
      <div
        className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full"
        style={{ marginTop: "auto" }}
      >
        {prompts.map((prompt, idx) => (
          <Button
            key={idx}
            onClick={() => onPromptSelect(prompt)}
            size="large"
            style={{
              backgroundColor: isDarkMode ? "#1f1f1f" : "#f5f5f5",
              borderRadius: "9999px",
              transition: "all 0.2s ease-in-out",
            }}
            className="hover:scale-[1.01]"
          >
            {prompt}
          </Button>
        ))}
      </div>
    </div>
  );
};

export default DefaultPrompts;
