import React, { useMemo } from "react";
import Markdown from "markdown-to-jsx";
import { theme } from "antd";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { base16AteliersulphurpoolLight, vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import styles from "./spin.module.css";

import TableRenderer from "./TableRenderer";
import BarChartRenderer from "./BarChartRenderer";
import PieChartRenderer from "./PieChartRenderer";

const MarkdownRenderer: React.FC<{ content: string }> = ({ content }) => {
  const { useToken } = theme;
  const { token } = useToken();

  const textColor = token.colorText; // Text color based on theme

  // Detect if we're in dark mode by calculating background luminance
  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  };

  const getLuminance = (hex: string) => {
    const rgb = hexToRgb(hex);
    if (!rgb) return 0;
    // Calculate relative luminance
    const { r, g, b } = rgb;
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  };

  const isDarkMode = getLuminance(token.colorBgContainer) < 0.5;
  const syntaxTheme = isDarkMode ? vscDarkPlus : base16AteliersulphurpoolLight;

  // Custom components for Markdown elements
  const MarkdownComponents = useMemo(
    () => ({
      h1: ({ children }: { children: React.ReactNode }) => (
        <h1 className="text-2xl font-bold mt-4 mb-3 text-primary">
          {children}
        </h1>
      ),
      h2: ({ children }: { children: React.ReactNode }) => (
        <h2 className="text-xl font-semibold mt-4 mb-2 text-primary">
          {children}
        </h2>
      ),
      h3: ({ children }: { children: React.ReactNode }) => (
        <h3 className="text-lg font-medium mt-3 mb-2 text-primary">
          {children}
        </h3>
      ),
      h4: ({ children }: { children: React.ReactNode }) => (
        <h4 className="text-base font-medium mt-2 mb-2 text-primary">
          {children}
        </h4>
      ),
      p: ({ children }: { children: React.ReactNode }) => (
        <p className="text-base leading-7 mb-3">{children}</p>
      ),
      ul: ({ children }: { children: React.ReactNode }) => (
        <ul className="list-disc ml-6 mb-3 space-y-1">{children}</ul>
      ),
      ol: ({ children }: { children: React.ReactNode }) => (
        <ol className="list-decimal ml-6 mb-3 space-y-1">{children}</ol>
      ),
      li: ({ children }: { children: React.ReactNode }) => (
        <li className="mb-0.5">{children}</li>
      ),
      blockquote: ({ children }: { children: React.ReactNode }) => (
        <blockquote className="border-l-4 border-primary pl-4 italic my-3 bg-opacity-10 bg-primary">
          {children}
        </blockquote>
      ),
      code: ({
        children,
        className,
      }: {
        children: React.ReactNode;
        className?: string;
      }) => {
        const match = /lang-(\w+)/.exec(className || "");
        const language = match ? match[1] : "";
        const contentStr = String(children).replace(/\n$/, "");
        const trimmed = contentStr.trim();

        const isTableData =
          language === "db-table" ||
          (trimmed.startsWith("{") && trimmed.includes('"columns"'));

        const isBarChartData =
          language === "db-chart" ||
          (trimmed.startsWith("{") && trimmed.includes('"xKey"') && trimmed.includes('"yKey"'));

        const isPieChartData =
          language === "db-pie" ||
          (trimmed.startsWith("{") && trimmed.includes('"nameKey"') && trimmed.includes('"valueKey"'));

        if (isTableData) {
          return <TableRenderer content={contentStr} />;
        }

        if (isBarChartData) {
          return <BarChartRenderer content={contentStr} />;
        }

        if (isPieChartData) {
          return <PieChartRenderer content={contentStr} />;
        }

        if (language) {
          return (
            <div className="rounded-md overflow-hidden my-3">
              <SyntaxHighlighter
                language={language}
                style={syntaxTheme}
                PreTag="div"
                customStyle={{
                  margin: 0,
                  borderRadius: "0.375rem",
                  backgroundColor: isDarkMode ? token.colorFillAlter : '#f5f5f5',
                  padding: '1rem',
                }}
              >
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            </div>
          );
        }

        return (
          <code className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-sm font-mono">
            {children}
          </code>
        );
      },
      pre: ({ children }: { children: React.ReactNode }) => (
        <div className="not-prose">{children}</div>
      ),
      hr: () => (
        <hr className="border-t my-4 border-gray-200 dark:border-gray-700" />
      ),
      a: ({ href, children }: { href: string; children: React.ReactNode }) => (
        <a
          href={href}
          className="text-primary hover:text-primary-dark underline transition-colors duration-200"
          target="_blank"
          rel="noopener noreferrer"
        >
          {children}
        </a>
      ),
      table: ({ children }: { children: React.ReactNode }) => (
        <div className="overflow-x-auto my-3">
          <table className="min-w-full border-collapse border border-gray-200 dark:border-gray-700">
            {children}
          </table>
        </div>
      ),
      th: ({ children }: { children: React.ReactNode }) => (
        <th className="border border-gray-200 dark:border-gray-700 px-4 py-2 bg-gray-50 dark:bg-gray-800 font-semibold">
          {children}
        </th>
      ),
      td: ({ children }: { children: React.ReactNode }) => (
        <td className="border border-gray-200 dark:border-gray-700 px-4 py-2">
          {children}
        </td>
      ),
      span: ({
        children,
        className,
      }: {
        children: React.ReactNode;
        className?: string;
      }) => {
        if (className === styles.spin) {
          return <span className={styles.spin}>{children}</span>;
        }
        return <span>{children}</span>;
      },
    }),
    [token.colorFillAlter, syntaxTheme, isDarkMode, token]
  );

  // Process the content to replace @spin[] tags with HTML
  let processedContent = content.replace(
    /@spin\[(.*?)\]/g,
    `<span class="${styles.spin}">$1</span>`
  );

  // Auto-close code block if unclosed to allow streaming
  // If there is an odd number of triple backticks, we are inside a code block
  if (processedContent.split("```").length % 2 === 0) {
    processedContent += "\n```";
  }

  return (
    <div
      style={{ color: textColor }}
      className="prose dark:prose-invert max-w-none"
    >
      <Markdown
        options={{
          overrides: MarkdownComponents,
          forceBlock: true,
        }}
      >
        {processedContent}
      </Markdown>
    </div>
  );
};

export default MarkdownRenderer;
