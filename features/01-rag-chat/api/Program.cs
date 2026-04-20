using Api.Services;
using Microsoft.SemanticKernel;

var builder = WebApplication.CreateBuilder(args);

const string CorsPolicyName = "FrontendCors";

builder.Services.AddCors(options =>
{
    options.AddPolicy(CorsPolicyName, policy =>
    {
        policy
            .WithOrigins("http://localhost:5173")
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});


var config = builder.Configuration;

builder.Services.AddOpenAIChatCompletion(
    modelId: config["OpenAI:ModelId"]!,
    apiKey: config["OpenAI:ApiKey"]!
);


builder.Services.AddScoped<IChatService, OpenAIChatService>();
builder.Services.AddSingleton<DocumentChunkingService>();
builder.Services.AddSingleton<RagMemoryService>();

var app = builder.Build();

// Index the PDF on startup
using (var scope = app.Services.CreateScope())
{
    var chunker = scope.ServiceProvider.GetRequiredService<DocumentChunkingService>();
    var ragMemory = scope.ServiceProvider.GetRequiredService<RagMemoryService>();

    var pdfPath = Path.Combine(AppContext.BaseDirectory, "Documents", "tenancy.pdf");
    var chunks = chunker.ChunkPdf(pdfPath);
    await ragMemory.IndexChunksAsync(chunks);
    
    Console.WriteLine($" Indexed {chunks.Count} chunks from tenancy PDF");
}

app.UseCors(CorsPolicyName);

app.MapPost("/api/chat", async (ChatRequest request, IChatService chatService) =>
{
    if (string.IsNullOrWhiteSpace(request.Message))
    {
        return Results.BadRequest(new { error = "Message is required." });
    }

    var response = await chatService.GetResponseAsync(request.Message);
    return Results.Ok(new ChatResponse(response));
});

app.Run();

public record ChatRequest(string Message);
public record ChatResponse(string Response);