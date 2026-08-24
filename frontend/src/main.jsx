import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App";

import "./styles/variables.css";
import "./styles/globals.css";
import "./styles/animations.css";

import { DevMindProvider } from "./context/DevMindContext";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <DevMindProvider>
      <App />
    </DevMindProvider>
  </StrictMode>,
);