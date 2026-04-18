namespace Api.Services;

public interface IChatService
{
    Task<string> GetResponseAsync(string message);
}
