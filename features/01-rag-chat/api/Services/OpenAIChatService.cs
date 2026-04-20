using Microsoft.SemanticKernel.ChatCompletion;

namespace Api.Services;

public class OpenAIChatService : IChatService
{
    private readonly IChatCompletionService _chat;
    private readonly RagMemoryService _memory;

    public OpenAIChatService(IChatCompletionService chat, RagMemoryService memory)
    {
        _chat = chat;
        _memory = memory;
    }

    public async Task<string> GetResponseAsync(string message)
    {
        // 1. Retrieve relevant chunks
        var relevantChunks = await _memory.SearchAsync(message, topK: 5);

        // 2. Build grounded prompt
        var context = relevantChunks.Any()
            ? string.Join("\n\n", relevantChunks)
            : "No relevant context found.";

        var groundedPrompt = $"""
    You are a helpful NSW tenancy law assistant.
    Answer the user's question based on the context below.
    If the context is partially relevant, use it to give the best answer you can.
    Only if the context has absolutely nothing relevant, say "I don't have enough information to answer that."

    Context:
    {context}

    Question: {message}
    """;

        // 3. Send grounded prompt to GPT
        var result = await _chat.GetChatMessageContentAsync(groundedPrompt);
        return result.Content ?? string.Empty;
    }
}