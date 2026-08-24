import { createContext, useContext } from "react";
import useDevMind from "../hooks/useDevMind";

const DevMindContext = createContext(null);

function DevMindProvider({ children }) {
  const devMind = useDevMind();

  return (
    <DevMindContext.Provider value={devMind}>
      {children}
    </DevMindContext.Provider>
  );
}

function useDevMindContext() {
  const context = useContext(DevMindContext);

  if (!context) {
    throw new Error(
      "useDevMindContext must be used inside DevMindProvider"
    );
  }

  return context;
}

export {
  DevMindProvider,
  useDevMindContext,
};