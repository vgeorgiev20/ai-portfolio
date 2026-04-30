import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

createRoot(document.querySelector<HTMLDivElement>("#app")!).render(
  React.createElement(StrictMode, null, React.createElement(App))
);
