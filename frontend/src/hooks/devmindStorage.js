const CONVERSATIONS_STORAGE_KEY = "devmind-conversations";
const ACTIVE_CONVERSATION_STORAGE_KEY = "devmind-active-conversation";
const initialConversations = [];

export function loadConversations() {
  try {
    if (typeof localStorage === "undefined") return initialConversations;
    const saved = localStorage.getItem(CONVERSATIONS_STORAGE_KEY);
    if (!saved) return initialConversations;
    const parsed = JSON.parse(saved);
    return Array.isArray(parsed) ? parsed : initialConversations;
  } catch {
    return initialConversations;
  }
}

export function saveConversations(conversations) {
  try {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(
        CONVERSATIONS_STORAGE_KEY,
        JSON.stringify(conversations)
      );
    }
  } catch (error) {
    console.error("Failed to save conversations:", error);
  }
}

export function loadActiveConversationId() {
  try {
    return typeof localStorage === "undefined"
      ? null
      : localStorage.getItem(ACTIVE_CONVERSATION_STORAGE_KEY);
  } catch {
    return null;
  }
}

export function saveActiveConversationId(conversationId) {
  try {
    if (typeof localStorage === "undefined") return;
    if (conversationId) {
      localStorage.setItem(ACTIVE_CONVERSATION_STORAGE_KEY, conversationId);
    } else {
      localStorage.removeItem(ACTIVE_CONVERSATION_STORAGE_KEY);
    }
  } catch (error) {
    console.error("Failed to save active conversation:", error);
  }
}
