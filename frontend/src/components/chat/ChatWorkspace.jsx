import { useEffect, useRef, useState } from "react";
import "./ChatWorkspace.css";

import MessageList from "./message/MessageList";
import ChatComposer from "./composer/ChatComposer";
import { useDevMindContext } from "../../context/DevMindContext";
import ProjectSwitcher from "./project/ProjectSwitcher";
import EmptyConversation from "./EmptyConversation";

const BOTTOM_THRESHOLD = 80;

function ChatWorkspace({
  isContextOpen,
  onToggleContext,
}) {
  const {
    activeProject,
    projects,
    switchProject,
    messages,
    isProcessing,
    isConversationLoading,
    conversationError,
    retryConversation,
    chatError,
    clearChatError,
    retryMessage,
    sendMessage,
    disconnectProject,
    reconnectProject,
    removeProject,
    uploadFiles,
    isUploading,
  } = useDevMindContext();

  const conversationRef = useRef(null);

  const isNearBottomRef = useRef(true);

  const [isNearBottom, setIsNearBottom] =
    useState(true);

  const checkScrollPosition = () => {
    const container = conversationRef.current;

    if (!container) {
      return;
    }

    const distanceFromBottom =
      container.scrollHeight -
      container.scrollTop -
      container.clientHeight;

    const nearBottom =
      distanceFromBottom <= BOTTOM_THRESHOLD;

    isNearBottomRef.current = nearBottom;
    setIsNearBottom(nearBottom);
  };

  useEffect(() => {
    const container = conversationRef.current;

    if (
      !container ||
      !isNearBottomRef.current
    ) {
      return;
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "auto",
    });
  }, [messages]);

  const scrollToLatest = () => {
    const container = conversationRef.current;

    if (!container) {
      return;
    }

    isNearBottomRef.current = true;
    setIsNearBottom(true);

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  };

  return (
    <div className="chat-workspace">
      {/* Header */}
      <header className="chat-workspace__header">
        <ProjectSwitcher
          projects={projects}
          activeProject={activeProject}
          onProjectChange={switchProject}
          onDisconnect={disconnectProject}
          onReconnect={reconnectProject}
          onRemove={removeProject}
        />
      </header>

      {/* Conversation */}
      <main
        ref={conversationRef}
        className="chat-workspace__conversation"
        onScroll={checkScrollPosition}
      >
        {isConversationLoading ? (
          <div className="chat-workspace__loading">
            <div className="chat-workspace__loading-spinner" />

            <p className="chat-workspace__loading-text">
              Loading conversation...
            </p>
          </div>
        ) : conversationError ? (
          <div className="chat-workspace__error">
            <div className="chat-workspace__error-icon">
              !
            </div>

            <h2 className="chat-workspace__error-title">
              Couldn't load conversation
            </h2>

            <p className="chat-workspace__error-text">
              Something went wrong while restoring
              this conversation.
            </p>

            <button
              type="button"
              className="chat-workspace__retry"
              onClick={retryConversation}
            >
              Try again
            </button>
          </div>
        ) : (
          <>
            {/* Chat API error */}
            {chatError && (
              <div className="chat-workspace__chat-error">
                <div className="chat-workspace__chat-error-content">
                  <span className="chat-workspace__chat-error-icon">
                    !
                  </span>

                  <span className="chat-workspace__chat-error-message">
                    {chatError}
                  </span>
                </div>

                <div className="chat-workspace__chat-error-actions">
                  <button
                    type="button"
                    className="chat-workspace__chat-error-retry"
                    onClick={retryMessage}
                    disabled={isProcessing}
                  >
                    {isProcessing
                      ? "Retrying..."
                      : "Retry"}
                  </button>

                  <button
                    type="button"
                    className="chat-workspace__chat-error-dismiss"
                    onClick={clearChatError}
                    aria-label="Dismiss error"
                  >
                    ×
                  </button>
                </div>
              </div>
            )}

            {messages.length > 0 ? (
              <MessageList
                messages={messages}
                isProcessing={isProcessing}
              />
            ) : (
              <EmptyConversation />
            )}
          </>
        )}

        {!isNearBottom &&
          !isConversationLoading &&
          !conversationError && (
            <button
              className="chat-workspace__jump-latest"
              type="button"
              onClick={scrollToLatest}
            >
              ↓ New messages
            </button>
          )}
      </main>

      {/* Composer */}
      <ChatComposer
        onSend={sendMessage}
        onUpload={uploadFiles}
        isProcessing={
          isProcessing ||
          isConversationLoading ||
          Boolean(conversationError)
        }
        isContextOpen={isContextOpen}
        onToggleContext={onToggleContext}
        isUploading={isUploading}
      />
    </div>
  );
}

export default ChatWorkspace;