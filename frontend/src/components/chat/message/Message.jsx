import "./Message.css";

import MessageContent from "./MessageContent";
import StreamingCursor from "./StreamingCursor";

function Message({ role, content, isStreaming = false }) {
  const isUser = role === "user";

  return (
    <article
      className={`message ${
        isUser ? "message--user" : "message--assistant"
      }`}
    >
      <div className="message__header">
        <div className="message__avatar">
          {isUser ? "You" : "D"}
        </div>

        <span className="message__role">
          {isUser ? "You" : "DevMind"}
        </span>
      </div>

      <div className="message__content">
        <MessageContent content={content} />

        {isStreaming && <StreamingCursor />}
      </div>
    </article>
  );
}

export default Message;