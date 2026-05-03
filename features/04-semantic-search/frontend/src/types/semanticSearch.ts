export interface SemanticSearchRequest {
  query: string;
  topK: number;
}

export interface SemanticSearchResult {
  id: string;
  title: string;
  content: string;
  similarityScore: number;
}

export interface SemanticSearchResponse {
  results: SemanticSearchResult[];
}
