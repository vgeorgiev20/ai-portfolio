using System.ComponentModel;
using System.Data;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;

var builder = WebApplication.CreateBuilder(args);

const string CorsPolicyName = "FrontendCors";

builder.Services.AddCors(options =>
{
    options.AddPolicy(CorsPolicyName, policy =>
    {
        policy.WithOrigins("http://localhost:5173")
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
    apiKey: openAiApiKey);

builder.Services.AddSingleton(_ =>
{
    var kernelBuilder = Kernel.CreateBuilder();
    var kernel = kernelBuilder.Build();
    kernel.Plugins.AddFromType<WeatherTools>("weather");
    kernel.Plugins.AddFromType<TimeTools>("time");
    kernel.Plugins.AddFromType<MathTools>("math");
    return kernel;
});

var app = builder.Build();

app.UseCors(CorsPolicyName);

app.MapPost("/api/chat", async (
    ChatRequest request,
    IChatCompletionService chatCompletionService,
    Kernel kernel,
    CancellationToken cancellationToken) =>
{
    if (string.IsNullOrWhiteSpace(request.Message))
    {
        return Results.BadRequest(new { error = "Message is required." });
    }

    var chatHistory = new ChatHistory();
    chatHistory.AddUserMessage(request.Message);

    var executionSettings = new OpenAIPromptExecutionSettings
    {
        ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions // the magic 
    };

    var result = await chatCompletionService.GetChatMessageContentAsync(
        chatHistory,
        executionSettings,
        kernel,
        cancellationToken);

    return Results.Ok(new { response = result.Content ?? string.Empty });
});

app.Run("http://0.0.0.0:5001");

public record ChatRequest(string Message);

public sealed class WeatherTools
{
    [KernelFunction("getWeather")]
    [Description("Get the current weather for a location.")]
    public string GetWeather([Description("City or location name")] string location)
    {
        var normalized = string.IsNullOrWhiteSpace(location) ? "unknown location" : location.Trim();
        return $"Mock weather for {normalized}: 24C, clear skies.";
    }
}

public sealed class TimeTools
{
    [KernelFunction("getTime")]
    [Description("Get the current time for a timezone.")]
    public string GetTime([Description("Timezone ID such as Australia/Sydney or UTC")] string timezone)
    {
        if (string.IsNullOrWhiteSpace(timezone))
        {
            return $"Current UTC time: {DateTime.UtcNow:O}";
        }

        try
        {
            var tz = TimeZoneInfo.FindSystemTimeZoneById(timezone.Trim());
            var now = TimeZoneInfo.ConvertTime(DateTimeOffset.UtcNow, tz);
            return $"Current time in {tz.Id}: {now:yyyy-MM-dd HH:mm:ss zzz}";
        }
        catch (TimeZoneNotFoundException)
        {
            return $"Timezone '{timezone}' was not found. Current UTC time: {DateTime.UtcNow:O}";
        }
        catch (InvalidTimeZoneException)
        {
            return $"Timezone '{timezone}' is invalid. Current UTC time: {DateTime.UtcNow:O}";
        }
    }
}

public sealed class MathTools
{
    [KernelFunction("calculate")]
    [Description("Evaluate a basic math expression.")]
    public string Calculate([Description("Math expression such as 10 * (5 + 2)")] string expression)
    {
        if (string.IsNullOrWhiteSpace(expression))
        {
            return "Expression cannot be empty.";
        }

        try
        {
            var table = new DataTable();
            var result = table.Compute(expression, string.Empty);
            return $"{expression} = {result}";
        }
        catch (Exception ex)
        {
            return $"Could not calculate expression '{expression}': {ex.Message}";
        }
    }
}
