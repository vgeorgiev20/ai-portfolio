# Architecture

This repository is organized as a set of **incremental, composable AI features** with a shared “platform” layer. The goal is to keep each feature readable and runnable while still modeling production-grade concerns.

## Design goals

- **End-to-end**: Each feature demonstrates API + UX + infra (where applicable).
- **Production-minded**: Tracing, redaction, evaluation, security checks, and CI are treated as first-class.
- **Composable**: Shared code lives in `shared/` and is used across features.
- **Scaffold friendly**: Placeholders exist early; CI and docs should remain useful even before everything is implemented.

## Repository layout

```
.
├─ shared/
│  ├─ AzureOpenAIConfig.cs
│  └─ SemanticKernelBuilder.cs
├─ features/
│  ├─ 01-rag-chat/
│  │  ├─ api/
│  │  │  ├─ Program.cs
│  │  │  └─ appsettings.json
│  │  ├─ frontend/
│  │  │  └─ App.tsx
│  │  ├─ docker-compose.yml
│  │  └─ README.md
│  ├─ 02-streaming/README.md
│  ├─ 03-function-calling/README.md
│  ├─ 04-semantic-search/README.md
│  ├─ 05-data-extraction/README.md
│  ├─ 06-memory/README.md
│  ├─ 07-agent/README.md
│  ├─ 08-code-review/README.md
│  ├─ 09-guardrails/README.md
│  └─ 10-observability/README.md
└─ .github/workflows/ci.yml
```

## Shared layer (`shared/`)

The shared layer is intentionally small:

- **Configuration**: typed configuration objects for common AI providers (Azure OpenAI first).
- **Kernel wiring**: one place to construct a Semantic Kernel instance in a consistent way.

As features mature, shared components can expand to include:

- HTTP client policies (timeouts, retries)
- structured logging and OpenTelemetry helpers
- request/response redaction utilities
- evaluation harness utilities

## Feature folders (`features/`)

Each feature folder should follow a simple contract:

- **`README.md`**: goal, architecture, local dev instructions, test plan
- **`api/`**: minimal API surface that demonstrates the feature
- **`frontend/`**: minimal UX that exercises the API
- **`docker-compose.yml`**: local dependencies (e.g., vector DB) when needed

Features are expected to evolve from placeholder scaffolding → runnable skeleton → production-grade patterns.

## CI philosophy

CI should:

- validate what exists now (markdown / formatting / basic sanity)
- **only build** projects when a project file exists
- not block early scaffolding (no “red build” due to placeholder features)
