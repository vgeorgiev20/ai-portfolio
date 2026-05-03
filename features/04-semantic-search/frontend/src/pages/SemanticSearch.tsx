import { FormEvent, useState } from "react";
import { postSemanticSearch } from "../api/semanticSearch";

function truncateContent(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength)}...`;
}

function similarityBadgeClass(score: number): string {
  if (score >= 0.85) {
    return "similarity-badge similarity-badge--high";
  }
  if (score >= 0.7) {
    return "similarity-badge similarity-badge--mid";
  }
  return "similarity-badge similarity-badge--low";
}

export default function SemanticSearch() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState<
    Awaited<ReturnType<typeof postSemanticSearch>>["results"] | null
  >(null);
  const [submittedQuery, setSubmittedQuery] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const runSearch = async () => {
    const trimmed = query.trim();
    if (!trimmed || isLoading) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setSubmittedQuery(trimmed);
    setHasSearched(true);

    try {
      const data = await postSemanticSearch({ query: trimmed, topK });
      setResults(data.results);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed.");
      setResults(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void runSearch();
  };

  return (
    <div className="semantic-page">
      <header className="semantic-header">
        <h1>Semantic Search</h1>
        <p className="semantic-subtitle">
          Find documents by meaning, not just keywords.
        </p>
      </header>

      <form className="semantic-controls" onSubmit={handleSubmit}>
        <div className="semantic-row">
          <input
            type="search"
            className="semantic-input"
            placeholder="Describe what you are looking for…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            aria-label="Search query"
          />
          <button
            type="submit"
            className="semantic-search-btn"
            disabled={isLoading || !query.trim()}
          >
            Search
          </button>
        </div>
        <div className="semantic-row semantic-row--meta">
          <label className="semantic-label" htmlFor="top-k">
            Results
          </label>
          <select
            id="top-k"
            className="semantic-select"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            disabled={isLoading}
          >
            <option value={3}>3</option>
            <option value={5}>5</option>
            <option value={10}>10</option>
          </select>
        </div>
      </form>

      {error && (
        <div className="semantic-banner semantic-banner--error" role="alert">
          {error}
        </div>
      )}

      <section className="semantic-results" aria-live="polite">
        {isLoading && (
          <div className="semantic-loading">
            <span className="semantic-spinner" aria-hidden />
            <span>Searching…</span>
          </div>
        )}

        {!isLoading && hasSearched && results && submittedQuery && (
          <>
            <p className="semantic-results-summary">
              Top {results.length} results for &apos;{submittedQuery}&apos;
            </p>
            {results.length === 0 ? (
              <p className="semantic-empty">
                No results found. Try different wording.
              </p>
            ) : (
              <ul className="semantic-card-list">
                {results.map((r) => (
                  <li key={r.id} className="semantic-card">
                    <span
                      className={similarityBadgeClass(r.similarityScore)}
                      title="Cosine similarity"
                    >
                      {Math.round(r.similarityScore * 100)}%
                    </span>
                    <h2 className="semantic-card-title">{r.title}</h2>
                    <p className="semantic-card-body">
                      {truncateContent(r.content, 150)}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}

        {!isLoading && !hasSearched && (
          <p className="semantic-placeholder">
            Enter a query to search documents
          </p>
        )}
      </section>
    </div>
  );
}
