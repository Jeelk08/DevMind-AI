import { useState } from "react";
import "./AppShell.css";

import Sidebar from "../sidebar/Sidebar";
import ChatWorkspace from "../chat/ChatWorkspace";
import ContextPanel from "../context/ContextPanel";
import OperationCenter from "../operation/OperationCenter";
function AppShell() {
  const [isContextOpen, setIsContextOpen] =
    useState(true);

  const toggleContext = () => {
    setIsContextOpen((current) => !current);
  };

  return (
    <div
      className={`app-shell ${
        isContextOpen
          ? ""
          : "app-shell--context-hidden"
      }`}
    >
      {/* Sidebar */}
      <aside className="app-shell__sidebar">
        <Sidebar />
      </aside>

      {/* Main workspace */}
      <main className="app-shell__main">
        <ChatWorkspace
          isContextOpen={isContextOpen}
          onToggleContext={toggleContext}
        />
      </main>

      {/* Context panel */}
      {isContextOpen && (
        <aside className="app-shell__context">
          <ContextPanel />
        </aside>
      )}

      {/* Operation center */}
      <OperationCenter />
    </div>
  );
}

export default AppShell;