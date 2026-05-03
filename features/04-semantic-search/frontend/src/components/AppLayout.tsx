import { NavLink, Outlet } from "react-router-dom";

export default function AppLayout() {
  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Feature navigation">
        <div className="sidebar-brand">AI Portfolio</div>
        <nav className="sidebar-nav">
          <NavLink
            to="/semantic-search"
            className={({ isActive }) =>
              isActive ? "sidebar-link sidebar-link--active" : "sidebar-link"
            }
          >
            Semantic Search
          </NavLink>
          <div className="sidebar-section" aria-label="Other features in this repo">
            <div className="sidebar-section-title">Other features</div>
            <ul className="sidebar-sibling-list">
              <li>01 — RAG Chat</li>
              <li>02 — Streaming (SSE)</li>
              <li>03 — Function Calling</li>
            </ul>
          </div>
        </nav>
      </aside>
      <main className="main-panel">
        <Outlet />
      </main>
    </div>
  );
}
