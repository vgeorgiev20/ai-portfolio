using Api.Services;

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

builder.Services.AddScoped<IChatService, MockChatService>();

var app = builder.Build();

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
