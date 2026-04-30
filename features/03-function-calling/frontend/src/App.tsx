import { useState } from "react";
import type { FormEvent } from "react";
import "./style.css";

function FunctionCallingChat() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!input.trim()) {
      setResponse("Please enter a message.");
      return;
    }

    setIsLoading(true);
    setResponse("");

    try {
      const res = await fetch("http://localhost:5001/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: input }),
      });

      if (!res.ok) {
        const errorPayload = (await res.json().catch(() => null)) as { error?: string } | null;
        setResponse(errorPayload?.error ?? `Request failed with status ${res.status}.`);
        return;
      }

      const payload = (await res.json()) as { response?: string };
      setResponse(payload.response ?? "No response received.");
    } catch {
      setResponse("Could not reach API. Make sure it is running on http://localhost:5001.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="container">
      <h1>Function Calling Chat</h1>
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask for weather, time, or a calculation..."
          className="chat-input"
        />
        <button type="submit" disabled={isLoading} className="chat-button">
          {isLoading ? "Loading..." : "Send"}
        </button>
      </form>

      <section className="response-box">
        <h2>Response</h2>
        <p>{response || "The assistant response will appear here."}</p>
      </section>
    </main>
  );
}

export default FunctionCallingChat;
