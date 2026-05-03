import type { SemanticSearchRequest, SemanticSearchResponse } from "../types/semanticSearch";

export async function postSemanticSearch(
  body: SemanticSearchRequest
): Promise<SemanticSearchResponse> {
  const response = await fetch("/api/semantic/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const text = await response.text();
    let message = `Request failed with status ${response.status}.`;
    try {
      const json = JSON.parse(text) as { title?: string; detail?: string };
      message = json.title ?? json.detail ?? message;
    } catch {
      if (text) {
        message = text;
      }
    }
    throw new Error(message);
  }

  return (await response.json()) as SemanticSearchResponse;
}
