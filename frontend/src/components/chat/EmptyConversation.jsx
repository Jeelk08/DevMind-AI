import "./EmptyConversation.css";

function EmptyConversation() {
  return (
    <div className="empty-conversation">
      <div className="empty-conversation__icon">
        🧠
      </div>

      <h2 className="empty-conversation__title">
        Start a new conversation
      </h2>

      <p className="empty-conversation__description">
        Ask DevMind about your project, code,
        architecture, or anything you're working on.
      </p>
    </div>
  );
}

export default EmptyConversation;