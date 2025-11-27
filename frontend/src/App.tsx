import { useState, useEffect } from "react";
import Chat from "./components/chat";
import { ConfigProvider, theme } from "antd";

// Theme configuration constants
const THEME_CONFIG = {
  light: {
    algorithm: theme.defaultAlgorithm,
    layout: {
      headerBg: "#f0f2f5",
      headerColor: "#000000",
      bodyBg: "#f0f2f5",
      siderBg: "#ffffff",
    },
    card: {
      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.05)",
      colorBorderSecondary: "#d9d9d9",
    },
  },
  dark: {
    algorithm: theme.darkAlgorithm,
    layout: {
      headerBg: "#1f1f1f",
      headerColor: "#ffffff",
      bodyBg: "#121212",
      siderBg: "#1f1f1f",
    },
    card: {
      boxShadow: "0 4px 12px rgba(255, 255, 255, 0.05)",
      colorBorderSecondary: "rgba(255, 255, 255, 0.1)",
    },
  },
};

export const DEFAULT_THEME = "light";

const App = () => {
  const [currentTheme, setCurrentTheme] = useState<string>(
    localStorage.getItem("theme") || DEFAULT_THEME
  );

  useEffect(() => {
    const handleThemeChange = () => {
      setCurrentTheme(localStorage.getItem("theme") || DEFAULT_THEME);
    };
    window.addEventListener("themeChanged", handleThemeChange);
    return () => window.removeEventListener("themeChanged", handleThemeChange);
  }, []);

  const themeConfig = THEME_CONFIG[currentTheme as keyof typeof THEME_CONFIG];

  return (
    <ConfigProvider
      theme={{
        algorithm: themeConfig.algorithm,
        token: {
          colorPrimary: "#e89a3c",
          borderRadius: 4,
        },
        components: {
          Layout: themeConfig.layout,
          Card: {
            borderRadius: 16,
            ...themeConfig.card,
          },
        },
      }}
    >
      <div className="App w-screen h-screen">
        <Chat />
      </div>
    </ConfigProvider>
  );
};

export default App;
