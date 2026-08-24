import { useEffect, useRef, useState } from "react";
import "./ChatComposer.css";

function ChatComposer({ onSend, isProcessing }) {
  const [value, setValue] = useState("");
  const textareaRef = useRef(null);

  const hasText = value.trim().length > 0;

  const canSend = hasText && !isProcessing;

  const resizeTextarea = () => {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";

    const maxHeight = 180;

    textarea.style.height = `${Math.min(
      textarea.scrollHeight,
      maxHeight
    )}px`;
  };

  useEffect(() => {
    resizeTextarea();
  }, [value]);

  const handleSubmit = (event) => {
    event.preventDefault();

    const trimmedValue = value.trim();

    if (!trimmedValue || isProcessing) {
      return;
    }

    onSend(trimmedValue);

    setValue("");
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      event.currentTarget.form.requestSubmit();
    }
  };

  const handleChange = (event) => {
    setValue(event.target.value);
  };

  return (
    <div className="chat-composer-area">
      <form
        className="chat-composer"
        onSubmit={handleSubmit}
      >
        <textarea
          ref={textareaRef}
          className="chat-composer__input"
          name="message"
          value={value}
          placeholder={
            isProcessing
              ? "DevMind is thinking..."
              : "Ask DevMind..."
          }
          rows="1"
          aria-label="Message DevMind"
          disabled={isProcessing}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
        />

        <div className="chat-composer__footer">
          <div className="chat-composer__actions">
            <button type="button">
              + Upload
            </button>

            <button type="button">
              🧠 Context
            </button>
          </div>

          <button
            className="chat-composer__send"
            type="submit"
            disabled={!canSend}
            aria-label="Send message"
          >
            {isProcessing ? "..." : "↑"}
          </button>
        </div>
      </form>

      <p className="chat-composer__hint">
        Enter to send · Shift + Enter for new line
      </p>
    </div>
  );
}

export default ChatComposer;