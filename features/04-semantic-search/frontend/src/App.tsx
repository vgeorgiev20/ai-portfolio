import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import SemanticSearch from "./pages/SemanticSearch";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/semantic-search" replace />} />
          <Route path="/semantic-search" element={<SemanticSearch />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
