import "./AppShell.css";
import Sidebar from "../sidebar/Sidebar";
import ChatWorkspace from "../chat/ChatWorkspace";
import ContextPanel from "../context/ContextPanel";

function AppShell() {
  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="app-shell__sidebar">
        <Sidebar />
      </aside>

      {/* Main workspace */}
      <main className="app-shell__main">
        <ChatWorkspace />
      </main>

      {/* Context panel */}
      <aside className="app-shell__context">
        <ContextPanel />
      </aside>
    </div>
  );
}

export default AppShell;