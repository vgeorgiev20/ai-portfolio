using Microsoft.SemanticKernel.Memory;
using Microsoft.SemanticKernel.Connectors.OpenAI;

namespace Api.Services;

#pragma warning disable SKEXP0001, SKEXP0010, SKEXP0050

public class RagMemoryService
{
    private readonly ISemanticTextMemory _memory;
    private const string CollectionName = "tenancy-docs";

    public RagMemoryService(IConfiguration config)
    {
        var apiKey = config["OpenAI:ApiKey"]!;

        _memory = new MemoryBuilder()
            .WithOpenAITextEmbeddingGeneration("text-embedding-ada-002", apiKey)
            .WithMemoryStore(new VolatileMemoryStore())
            .Build();
    }

    public async Task IndexChunksAsync(List<string> chunks)
    {
        for (int i = 0; i < chunks.Count; i++)
        {
            await _memory.SaveInformationAsync(
                collection: CollectionName,
                text: chunks[i],
                id: $"chunk-{i}"
            );
        }
    }

    public async Task<List<string>> SearchAsync(string query, int topK = 3)
{
    var results = new List<string>();

   await foreach (var result in _memory.SearchAsync(CollectionName, query, topK, minRelevanceScore: 0.5))
{
    Console.WriteLine($"Found chunk with score: {result.Relevance}");
    Console.WriteLine($"Chunk preview: {result.Metadata.Text.Substring(0, Math.Min(200, result.Metadata.Text.Length))}");
    results.Add(result.Metadata.Text);
}

    Console.WriteLine($"Total chunks found: {results.Count}");
    return results;
}
}