import { useEffect, useRef, useState } from "react";
import "./ChatComposer.css";

function ChatComposer({
  onSend,
  isProcessing,
  isContextOpen,
  onToggleContext,
  onUpload,
  isUploading,
}) {
  const [value, setValue] = useState("");
  const [selectedFiles, setSelectedFiles] = useState([]);

  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const hasText = value.trim().length > 0;

  const canSend =
    hasText &&
    !isProcessing &&
    !isUploading;

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

    if (
      !trimmedValue ||
      isProcessing ||
      isUploading
    ) {
      return;
    }

    onSend(trimmedValue);

    setValue("");
  };

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      event.currentTarget.form.requestSubmit();
    }
  };

  const handleChange = (event) => {
    setValue(event.target.value);
  };

  const handleUploadClick = () => {
    if (
      isProcessing ||
      isUploading
    ) {
      return;
    }

    fileInputRef.current?.click();
  };

  const handleFileChange = (event) => {
    const files = Array.from(
      event.target.files || []
    );

    if (files.length === 0) {
      return;
    }

    setSelectedFiles((currentFiles) => {
      const existingKeys = new Set(
        currentFiles.map(
          (file) =>
            `${file.name}-${file.size}-${file.lastModified}`
        )
      );

      const newFiles = files.filter((file) => {
        const key = `${file.name}-${file.size}-${file.lastModified}`;

        return !existingKeys.has(key);
      });

      return [
        ...currentFiles,
        ...newFiles,
      ];
    });

    event.target.value = "";
  };

  const handleUpload = async () => {
    if (
      selectedFiles.length === 0 ||
      isProcessing ||
      isUploading
    ) {
      return;
    }

    try {
      await onUpload(selectedFiles);

      setSelectedFiles([]);
    } catch (error) {
      console.error(
        "Failed to upload files:",
        error
      );
    }
  };

  const handleRemoveFile = (fileToRemove) => {
    if (isUploading) {
      return;
    }

    setSelectedFiles((currentFiles) =>
      currentFiles.filter(
        (file) => file !== fileToRemove
      )
    );
  };

  const handleUploadButtonClick = () => {
    if (selectedFiles.length > 0) {
      handleUpload();
      return;
    }

    handleUploadClick();
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

        {selectedFiles.length > 0 && (
          <div
            className="chat-composer__files"
            aria-label="Selected files"
          >
            {selectedFiles.map((file) => (
              <div
                className="chat-composer__file"
                key={`${file.name}-${file.size}-${file.lastModified}`}
              >
                <span className="chat-composer__file-icon">
                  📄
                </span>

                <span
                  className="chat-composer__file-name"
                  title={file.name}
                >
                  {file.name}
                </span>

                <button
                  type="button"
                  className="chat-composer__file-remove dm-button dm-button--ghost dm-button--icon dm-button--sm"
                  onClick={() =>
                    handleRemoveFile(file)
                  }
                  aria-label={`Remove ${file.name}`}
                  disabled={
                    isProcessing ||
                    isUploading
                  }
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          multiple
          hidden
          onChange={handleFileChange}
          aria-label="Upload files"
        />

        <div className="chat-composer__footer">
          <div className="chat-composer__actions">
            <button
              type="button"
              onClick={
                selectedFiles.length > 0
                  ? handleUpload
                  : handleUploadClick
              }
              disabled={
                isProcessing ||
                isUploading
              }
            >
              {isUploading
                ? "Uploading..."
                : selectedFiles.length > 0
                ? "↑ Upload"
                : "+ Upload"}
            </button>

            <button
              type="button"
              className={`dm-button dm-button--sm ${
                isContextOpen
                  ? "chat-composer__context-button--active"
                  : "dm-button--ghost"
              }`}
              onClick={onToggleContext}
              aria-pressed={isContextOpen}
              title={
                isContextOpen
                  ? "Hide context"
                  : "Show context"
              }
            >
              🧠 Context
            </button>
          </div>

          <button
            className="dm-button dm-button--primary dm-button--icon chat-composer__send"
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