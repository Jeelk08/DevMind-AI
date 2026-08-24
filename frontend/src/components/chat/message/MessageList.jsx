import "./MessageList.css";

import Message from "./Message";

function MessageList({ messages, isProcessing }) {
  return (
    <div className="message-list">
      {messages.map((message, index) => {
        const isStreaming =
          isProcessing &&
          index === messages.length - 1 &&
          message.role === "assistant";

        return (
          <Message
            key={message.id}
            role={message.role}
            content={message.content}
            isStreaming={isStreaming}
          />
        );
      })}
    </div>
  );
}

export default MessageList;