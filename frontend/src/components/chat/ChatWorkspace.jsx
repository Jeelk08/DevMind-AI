import { useEffect, useRef, useState } from "react";
import "./ChatWorkspace.css";

import MessageList from "./message/MessageList";
import ChatComposer from "./composer/ChatComposer";
import { useDevMindContext } from "../../context/DevMindContext";
import ProjectSwitcher from "./project/ProjectSwitcher";
import EmptyConversation from "./EmptyConversation";
import OperationCenter from "../operation/OperationCenter";

const BOTTOM_THRESHOLD = 80;

const FOLDER_IGNORED_DIRS = new Set([
  ".git", ".devmind", ".idea", ".vscode", "__pycache__",
  ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox",
  "venv", ".venv", "env", "node_modules", "dist", "build",
]);

const FOLDER_IGNORED_FILES = new Set([
  ".venv", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
  "bun.lock", "bun.lockb",
]);

const FOLDER_SUPPORTED_EXTENSIONS = new Set([
  ".py", ".js", ".jsx", ".ts", ".tsx", ".c", ".h", ".cc",
  ".cpp", ".cxx", ".hpp", ".hh", ".hxx", ".java", ".html",
  ".css", ".scss", ".json", ".xml", ".yml", ".yaml", ".md",
]);

const isSupportedFolderFile = (relativePath) => {
  const parts = relativePath.replace(/\\/g, "/").split("/");
  if (parts.some((part) => FOLDER_IGNORED_DIRS.has(part))) return false;

  const filename = parts[parts.length - 1];
  if (FOLDER_IGNORED_FILES.has(filename)) return false;
  if (
    filename === ".env" ||
    filename.startsWith(".env.") ||
    filename.endsWith(".pem") ||
    filename.endsWith(".key") ||
    filename.startsWith("credentials.") ||
    filename.startsWith("secrets.")
  ) return false;

  const dot = filename.lastIndexOf(".");
  const extension = dot >= 0 ? filename.slice(dot).toLowerCase() : "";
  return FOLDER_SUPPORTED_EXTENSIONS.has(extension);
};

async function collectDirectoryFiles(directoryHandle, prefix = "", onProgress = () => {}) {
  const collected = [];
  for await (const entry of directoryHandle.values()) {
    const relativePath = prefix ? `${prefix}/${entry.name}` : entry.name;

    if (entry.kind === "directory") {
      if (FOLDER_IGNORED_DIRS.has(entry.name)) continue;
      collected.push(...await collectDirectoryFiles(entry, relativePath, onProgress));
      continue;
    }

    if (entry.kind !== "file") continue;
    onProgress();
    if (!isSupportedFolderFile(relativePath)) continue;
    const file = await entry.getFile();
    if (file.size <= 10 * 1024 * 1024) {
      collected.push({ file, relativePath });
    }
  }
  return collected;
}

function collectInputFolderFiles(fileList) {
  return Array.from(fileList || [])
    .map((file) => {
      const browserPath = file.webkitRelativePath || file.name;
      const parts = browserPath.replace(/\\/g, "/").split("/");
      return {
        file,
        relativePath: parts.length > 1 ? parts.slice(1).join("/") : parts[0],
      };
    })
    .filter((item) => isSupportedFolderFile(item.relativePath))
    .filter((item) => item.file.size <= 10 * 1024 * 1024);
}


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
    importProjectFromFolder,
  } = useDevMindContext();

  const conversationRef = useRef(null);
  const folderInputRef = useRef(null);
  const [isImportingFolder, setIsImportingFolder] = useState(false);
  const [folderOperation, setFolderOperation] = useState(null);

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


  const handleFolderImport = async (selectedFiles, folderName) => {
    if (!selectedFiles.length) {
      setFolderOperation({ active: true, error: true, title: "No supported files found", message: "Choose a folder containing supported source files." });
      setIsImportingFolder(false);
      return;
    }
    if (selectedFiles.length > 1000) {
      setFolderOperation({ active: true, error: true, title: "Folder is too large", message: "The current import limit is 1,000 files." });
      setIsImportingFolder(false);
      return;
    }

    const totalBytes = selectedFiles.reduce((sum, item) => sum + item.file.size, 0);
    if (totalBytes > 100 * 1024 * 1024) {
      setFolderOperation({ active: true, error: true, title: "Folder is too large", message: "The current import limit is 100 MB." });
      setIsImportingFolder(false);
      return;
    }

    setIsImportingFolder(true);
    setFolderOperation({
      active: true,
      title: `Uploading ${folderName}`,
      message: `Preparing ${selectedFiles.length.toLocaleString()} files for DevMind...`,
      phase: "uploading",
      progress: 0,
      filesTotal: selectedFiles.length,
    });

    try {
      const result = await importProjectFromFolder(folderName, selectedFiles, (progress) => {
        if (progress.phase === "indexing") {
          setFolderOperation((current) => ({
            ...current, active: true, title: `Indexing ${folderName}`,
            message: "Files uploaded. Building repository knowledge...",
            phase: "indexing", progress: null,
          }));
          return;
        }
        setFolderOperation((current) => ({
          ...current, active: true, title: `Uploading ${folderName}`,
          message: `${(progress.loaded / 1024 / 1024).toFixed(1)} MB of ${(progress.total / 1024 / 1024).toFixed(1)} MB uploaded`,
          phase: "uploading", progress: progress.percent,
        }));
      });
      const count = result?.files_saved ?? selectedFiles.length;
      setFolderOperation({
        active: true, complete: true, title: `${folderName} is ready`,
        message: `${count.toLocaleString()} files imported and indexed successfully.`,
        phase: "complete", filesTotal: selectedFiles.length,
      });
      window.setTimeout(() => {
        setFolderOperation(null);
      }, 4500);
    } catch (error) {
      setFolderOperation({
        active: true, error: true, title: "Folder import failed",
        message: error?.message || "Something went wrong while importing this folder.",
        phase: "failed",
      });
    } finally {
      setIsImportingFolder(false);
    }
  };

  const handleSelectFolder = async () => {
    if (isImportingFolder || isProcessing || isUploading) return;
    setFolderOperation(null);

    if (typeof window.showDirectoryPicker === "function") {
      try {
        const directoryHandle = await window.showDirectoryPicker({ mode: "read" });
        const folderName = directoryHandle.name || "Imported Project";
        setIsImportingFolder(true);
        let scanned = 0;
        setFolderOperation({
          active: true, title: `Scanning ${folderName}`,
          message: "Reading the selected folder and filtering supported files...",
          phase: "scanning", filesFound: 0,
        });
        const selectedFiles = await collectDirectoryFiles(directoryHandle, "", () => {
          scanned += 1;
          setFolderOperation((current) => ({
            ...current, active: true, filesFound: scanned,
            message: `Checking files in ${folderName}...`,
          }));
        });
        setFolderOperation((current) => ({
          ...current, active: true, title: `Preparing ${folderName}`,
          message: `${selectedFiles.length.toLocaleString()} supported files found.`,
          phase: "preparing", filesFound: scanned, filesTotal: selectedFiles.length,
        }));
        await handleFolderImport(selectedFiles, folderName);
      } catch (error) {
        if (error?.name !== "AbortError") {
          setFolderOperation({
            active: true, error: true, title: "Couldn't read folder",
            message: error?.message || "Unable to read the selected folder.",
            phase: "failed",
          });
        } else {
          setFolderOperation(null);
        }
        setIsImportingFolder(false);
      }
      return;
    }
    folderInputRef.current?.click();
  };

  const handleFolderInputChange = async (event) => {
    const files = Array.from(event.target.files || []);
    const firstPath = files[0]?.webkitRelativePath || "";
    const folderName = firstPath.split("/")[0] || "Imported Project";
    const selectedFiles = collectInputFolderFiles(files);
    event.target.value = "";
    setFolderOperation({
      active: true, title: `Preparing ${folderName}`,
      message: `${selectedFiles.length.toLocaleString()} supported files found.`,
      phase: "preparing", filesFound: files.length, filesTotal: selectedFiles.length,
    });
    await handleFolderImport(selectedFiles, folderName);
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

        <div className="chat-workspace__header-actions">
          <input
            ref={folderInputRef}
            type="file"
            hidden
            multiple
            webkitdirectory=""
            directory=""
            onChange={handleFolderInputChange}
            aria-label="Select project folder"
          />
          <button
            type="button"
            className="chat-workspace__folder-button"
            onClick={handleSelectFolder}
            disabled={isImportingFolder || isProcessing || isUploading}
            title="Select a local project folder"
          >
            {isImportingFolder ? "Importing folder..." : "＋ Select Folder"}
          </button>
        </div>
      </header>

      <OperationCenter folderOperation={folderOperation} />

      {/* Conversation */}
      <main
        ref={conversationRef}
        className="chat-workspace__conversation"
        onScroll={checkScrollPosition}
      >
        {isImportingFolder ? (
          <div className="repository-import-stage" role="status" aria-live="polite">
            <div className="repository-import-stage__visual">
              <span className="repository-import-stage__orbit repository-import-stage__orbit--outer" />
              <span className="repository-import-stage__orbit repository-import-stage__orbit--inner" />
              <span className="repository-import-stage__core">D</span>
            </div>
            <p className="repository-import-stage__eyebrow">REPOSITORY INITIALIZATION</p>
            <h2 className="repository-import-stage__title">{folderOperation?.title || "Preparing your project"}</h2>
            <p className="repository-import-stage__message">{folderOperation?.message || "DevMind is preparing your repository..."}</p>
            <div className="repository-import-stage__steps">
              {["scanning", "preparing", "uploading", "indexing"].map((step, index) => {
                const order = ["scanning", "preparing", "uploading", "indexing"];
                const currentIndex = order.indexOf(folderOperation?.phase);
                const isComplete = currentIndex > index;
                const isActive = folderOperation?.phase === step;
                return (
                  <div className={`repository-import-stage__step ${isComplete ? "is-complete" : ""} ${isActive ? "is-active" : ""}`} key={step}>
                    <span className="repository-import-stage__step-dot">{isComplete ? "✓" : index + 1}</span>
                    <span>{step === "preparing" ? "Prepare" : step[0].toUpperCase() + step.slice(1)}</span>
                  </div>
                );
              })}
            </div>
            {folderOperation?.filesFound != null && (
              <span className="repository-import-stage__meta">
                {folderOperation.filesFound.toLocaleString()} files scanned
                {folderOperation.filesTotal != null ? ` · ${folderOperation.filesTotal.toLocaleString()} supported` : ""}
              </span>
            )}
            {folderOperation?.progress != null && (
              <div className="repository-import-stage__progress">
                <span style={{ width: `${Math.max(0, Math.min(100, folderOperation.progress))}%` }} />
              </div>
            )}
          </div>
        ) : isConversationLoading ? (
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