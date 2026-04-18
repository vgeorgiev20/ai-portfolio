namespace Api.Services;

public class MockChatService : IChatService
{
    public Task<string> GetResponseAsync(string message)
    {
        var response = $"This is a mock response for: {message}";
        return Task.FromResult(response);
    }
}
