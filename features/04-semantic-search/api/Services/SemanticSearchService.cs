using System.Data;
using Microsoft.EntityFrameworkCore;
using Npgsql;
using Pgvector;

namespace api.Services;

public record SemanticSearchResultDto(
    Guid Id,
    string Title,
    string Content,
    double SimilarityScore);

public sealed class SemanticSearchService(AppDbContext db, IEmbeddingService embedding)
{
    public async Task<List<SemanticSearchResultDto>> SearchAsync(
        string query,
        int topK,
        CancellationToken ct)
    {
        float[] queryEmbedding = await embedding.GetEmbeddingAsync(query, ct);
        var queryVector = new Vector(queryEmbedding);

        var connection = db.Database.GetDbConnection();
        var openedHere = connection.State != ConnectionState.Open;
        if (openedHere)
        {
            await connection.OpenAsync(ct);
        }

        try
        {
            await using var command = connection.CreateCommand();
            command.CommandText =
                """
                SELECT "Id", "Title", "Content",
                       1 - ("Embedding" <=> @queryVector::vector) AS similarity_score
                FROM "SemanticDocuments"
                WHERE "Embedding" IS NOT NULL
                ORDER BY "Embedding" <=> @queryVector::vector
                LIMIT @topK
                """;

            var vectorParam = new NpgsqlParameter("queryVector", queryVector);
            command.Parameters.Add(vectorParam);

            var topKParam = new NpgsqlParameter("topK", topK);
            command.Parameters.Add(topKParam);

            var results = new List<SemanticSearchResultDto>();
            await using var reader = await command.ExecuteReaderAsync(ct);
            while (await reader.ReadAsync(ct))
            {
                var id = reader.GetGuid(0);
                var title = reader.GetString(1);
                var content = reader.GetString(2);
                var score = reader.GetDouble(3);
                results.Add(new SemanticSearchResultDto(id, title, content, score));
            }

            return results;
        }
        finally
        {
            if (openedHere)
            {
                await connection.CloseAsync();
            }
        }
    }
}
