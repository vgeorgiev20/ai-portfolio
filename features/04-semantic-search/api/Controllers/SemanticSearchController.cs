using api.Services;
using Microsoft.AspNetCore.Mvc;

namespace api.Controllers;

[ApiController]
[Route("api/semantic")]
public class SemanticSearchController : ControllerBase
{
    private readonly SemanticSearchService _service;

    public SemanticSearchController(SemanticSearchService service)
    {
        _service = service;
    }

    [HttpPost("search")]
    public async Task<IActionResult> Search(
        [FromBody] SemanticSearchRequest request,
        CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(request.Query))
        {
            return BadRequest("Query cannot be empty.");
        }

        var topK = request.TopK;
        if (topK < 1 || topK > 20)
        {
            return BadRequest("TopK must be between 1 and 20.");
        }

        var results = await _service.SearchAsync(request.Query, topK, ct);
        return Ok(new { results });
    }
}

public record SemanticSearchRequest
{
    public string Query { get; init; } = string.Empty;
    public int TopK { get; init; } = 5;
}
