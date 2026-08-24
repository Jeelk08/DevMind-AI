import ReactMarkdown from "react-markdown";

import CodeBlock from "./CodeBlock";
import "./MessageContent.css";

function MessageContent({ content }) {
  return (
    <div className="message-content">
      <ReactMarkdown
        components={{
          pre({ children }) {
            const codeElement = Array.isArray(children)
              ? children[0]
              : children;

            const className =
              codeElement?.props?.className || "";

            const match =
              /language-([\w-]+)/.exec(className);

            const language = match?.[1] || "text";

            const code =
              codeElement?.props?.children ?? "";

            return (
              <CodeBlock language={language}>
                {code}
              </CodeBlock>
            );
          },

          code({ className, children, ...props }) {
            return (
              <code
                className={className}
                {...props}
              >
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

export default MessageContent;