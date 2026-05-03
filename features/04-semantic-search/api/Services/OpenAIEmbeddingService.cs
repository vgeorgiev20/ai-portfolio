using OpenAI;
using OpenAI.Embeddings;

namespace api.Services;

public sealed class OpenAIEmbeddingService : IEmbeddingService
{
    private readonly EmbeddingClient _embeddings;

    public OpenAIEmbeddingService(IConfiguration configuration)
    {
        var apiKey = configuration["OpenAI:ApiKey"]
            ?? throw new InvalidOperationException("OpenAI:ApiKey is missing from configuration.");

        var client = new OpenAIClient(apiKey);
        _embeddings = client.GetEmbeddingClient("text-embedding-3-small");
    }

    public async Task<float[]> GetEmbeddingAsync(string text, CancellationToken ct = default)
    {
        var options = new EmbeddingGenerationOptions
        {
            Dimensions = 1536
        };

        OpenAIEmbedding embedding = await _embeddings.GenerateEmbeddingAsync(text, options, ct);
        ReadOnlyMemory<float> floats = embedding.ToFloats();
        return floats.ToArray();
    }
}
