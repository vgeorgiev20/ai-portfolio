import { FormEvent, useState } from "react";
import "./App.css";

const API_URL = "http://localhost:5001/api/stream";

export default function StreamingChat() {
  const [response, setResponse] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [input, setInput] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedInput = input.trim();

    if (!trimmedInput || isStreaming) {
      return;
    }

    setResponse("");
    setIsStreaming(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: trimmedInput })
      });

      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
      }

      if (!res.body) {
        throw new Error("Streaming response body is missing.");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let isDone = false;

      while (!isDone) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const eventChunk of events) {
          const lines = eventChunk.split("\n");

          for (const line of lines) {
            if (!line.startsWith("data: ")) {
              continue;
            }

            const text = line.slice("data: ".length);

            if (text === "[DONE]") {
              isDone = true;
              break;
            }

            setResponse((previous) => previous + text);
          }

          if (isDone) {
            break;
          }
        }
      }
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "An unknown streaming error occurred.";

      setResponse(`Unable to stream response: ${message}`);
    } finally {
      setIsStreaming(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="chat-card">
        <h1>Streaming Chat</h1>
        <p className="subtitle">Send a prompt and watch the response stream in.</p>

        <div className="response-panel">
          {response || "The assistant response will appear here as chunks arrive."}
        </div>

        <form className="input-row" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
            disabled={isStreaming}
          />
          <button type="submit" disabled={!input.trim() || isStreaming}>
            {isStreaming ? "Streaming..." : "Send"}
          </button>
        </form>
      </section>
    </main>
  );
}
