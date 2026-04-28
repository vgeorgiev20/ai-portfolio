using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;

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

var openAiApiKey = builder.Configuration["OpenAI:ApiKey"]
    ?? throw new InvalidOperationException("OpenAI:ApiKey is missing from configuration.");
var openAiModelId = builder.Configuration["OpenAI:ModelId"]
    ?? throw new InvalidOperationException("OpenAI:ModelId is missing from configuration.");

builder.Services.AddOpenAIChatCompletion(
    modelId: openAiModelId,
    apiKey: openAiApiKey
);

var app = builder.Build();

app.UseCors(CorsPolicyName);

app.MapPost("/api/stream", async (
    StreamRequest request,
    IChatCompletionService chatCompletionService,
    HttpContext httpContext,
    CancellationToken cancellationToken) =>
{
    if (string.IsNullOrWhiteSpace(request.Message))
    {
        httpContext.Response.StatusCode = StatusCodes.Status400BadRequest;
        await httpContext.Response.WriteAsJsonAsync(
            new { error = "Message is required." },
            cancellationToken);
        return;
    }

    httpContext.Response.Headers.CacheControl = "no-cache";
    httpContext.Response.Headers.Append("X-Accel-Buffering", "no");
    httpContext.Response.ContentType = "text/event-stream";

    var chatHistory = new ChatHistory();
    chatHistory.AddUserMessage(request.Message);

    await foreach (var chunk in chatCompletionService.GetStreamingChatMessageContentsAsync(
        chatHistory,
        cancellationToken: cancellationToken))
    {
        if (string.IsNullOrEmpty(chunk.Content))
        {
            continue;
        }

        await httpContext.Response.WriteAsync($"data: {chunk.Content}\n\n", cancellationToken);
        await httpContext.Response.Body.FlushAsync(cancellationToken);
    }

    await httpContext.Response.WriteAsync("data: [DONE]\n\n", cancellationToken);
    await httpContext.Response.Body.FlushAsync(cancellationToken);
});

app.Run();

public record StreamRequest(string Message);
