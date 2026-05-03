using api;
using api.Services;
using Microsoft.EntityFrameworkCore;
using Npgsql;
using Pgvector.EntityFrameworkCore;

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



var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? throw new InvalidOperationException("Connection string 'DefaultConnection' is not configured.");



builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(connectionString, o => o.UseVector()));

builder.Services.AddScoped<IEmbeddingService, OpenAIEmbeddingService>();
builder.Services.AddScoped<SemanticSeedService>();
builder.Services.AddScoped<SemanticSearchService>();

builder.Services.AddControllers();

var app = builder.Build();

app.UseCors(CorsPolicyName);

app.MapControllers();

await using (var scope = app.Services.CreateAsyncScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

    try
    {
        await db.Database.OpenConnectionAsync();
        Console.WriteLine("DB connection successful.");
        await db.Database.CloseConnectionAsync();
    }
    catch (Exception ex)
    {
        Console.WriteLine($"DB connection failed: {ex.GetType().Name}: {ex.Message}");
        throw;
    }

    await db.Database.MigrateAsync();

    var seeder = scope.ServiceProvider.GetRequiredService<SemanticSeedService>();
    await seeder.SeedAsync();
}

app.Run("http://0.0.0.0:5010");


