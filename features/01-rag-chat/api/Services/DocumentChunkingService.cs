using UglyToad.PdfPig;
using UglyToad.PdfPig.Content;

namespace Api.Services;

public class DocumentChunkingService
{
    private const int ChunkSize = 500;
    private const int ChunkOverlap = 50;

    public List<string> ChunkPdf(string filePath)
    {
        var chunks = new List<string>();
        var fullText = ExtractText(filePath);
        
        var words = fullText.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        
        for (int i = 0; i < words.Length; i += ChunkSize - ChunkOverlap)
        {
            var chunk = string.Join(" ", words.Skip(i).Take(ChunkSize));
            if (!string.IsNullOrWhiteSpace(chunk))
                chunks.Add(chunk);
        }

        return chunks;
    }

    private string ExtractText(string filePath)
    {
        using var pdf = PdfDocument.Open(filePath);
        var pages = pdf.GetPages()
            .Select(p => p.Text);
        return string.Join(" ", pages);
    }
}