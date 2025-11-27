import React from "react";
import Markdown from "markdown-to-jsx";
import { theme } from "antd";
import styles from "./spin.module.css";

// Custom components for Markdown elements
const MarkdownComponents = {
  h1: ({ children }: { children: React.ReactNode }) => (
    <h1 className="text-2xl font-bold mt-4 mb-3 text-primary">{children}</h1>
  ),
  h2: ({ children }: { children: React.ReactNode }) => (
    <h2 className="text-xl font-semibold mt-4 mb-2 text-primary">{children}</h2>
  ),
  h3: ({ children }: { children: React.ReactNode }) => (
    <h3 className="text-lg font-medium mt-3 mb-2 text-primary">{children}</h3>
  ),
  h4: ({ children }: { children: React.ReactNode }) => (
    <h4 className="text-base font-medium mt-2 mb-2 text-primary">{children}</h4>
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
    if (className) {
      return (
        <code className="px-1 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-sm font-mono">
          {children}
        </code>
      );
    }
    return (
      <code className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-sm font-mono">
        {children}
      </code>
    );
  },
  pre: ({ children }: { children: React.ReactNode }) => (
    <pre className="p-3 rounded-lg bg-gray-100 dark:bg-gray-800 overflow-x-auto my-3 text-sm font-mono">
      {children}
    </pre>
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
};

const MarkdownRenderer: React.FC<{ content: string }> = ({ content }) => {
  const { useToken } = theme;
  const { token } = useToken();

  const textColor = token.colorText; // Text color based on theme

  // Process the content to replace @spin[] tags with HTML
  const processedContent = content.replace(
    /@spin\[(.*?)\]/g,
    `<span class="${styles.spin}">$1</span>`
  );

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
