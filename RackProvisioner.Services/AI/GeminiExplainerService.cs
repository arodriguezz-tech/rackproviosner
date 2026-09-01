using System.Net.Http.Json;
using System.Text.Json;

namespace RackProvisioner.Services.AI;

public class GeminiExplainerService : IReadinessExplainer
{
    private readonly string _apiKey;
    private readonly HttpClient _httpClient;
    private const string GeminiEndpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent";

    public GeminiExplainerService(string apiKey, HttpClient? httpClient = null)
    {
        _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));
        _httpClient = httpClient ?? new HttpClient();
    }

    public async Task<string> ExplainReadinessDecisionAsync(
        string status,
        List<string> blockedReasons,
        Dictionary<string, object>? context = null,
        CancellationToken cancellationToken = default)
    {
        if (status == "Ready")
        {
            return "✅ Rack is ready for provisioning. All checks passed. Proceed with confidence!";
        }

        var prompt = BuildPrompt(status, blockedReasons, context);

        try
        {
            var request = new
            {
                contents = new[]
                {
                    new
                    {
                        parts = new[]
                        {
                            new { text = prompt }
                        }
                    }
                }
            };

            var url = $"{GeminiEndpoint}?key={_apiKey}";
            var response = await _httpClient.PostAsJsonAsync(url, request, cancellationToken);

            if (response.IsSuccessStatusCode)
            {
                var jsonContent = await response.Content.ReadAsStringAsync(cancellationToken);
                var result = JsonSerializer.Deserialize<GeminiResponse>(jsonContent);
                return result?.Candidates?.FirstOrDefault()?.Content?.Parts?.FirstOrDefault()?.Text
                    ?? "Unable to generate explanation. Please contact support.";
            }

            // Fallback on API error
            return $"⚠️ Could not generate AI explanation (API error). Blocked reasons:\n" +
                   string.Join("\n", blockedReasons.Select(r => $"• {r}"));
        }
        catch (Exception ex)
        {
            // Fallback on any exception
            return $"⚠️ Could not generate AI explanation ({ex.Message}). Blocked reasons:\n" +
                   string.Join("\n", blockedReasons.Select(r => $"• {r}"));
        }
    }

    private string BuildPrompt(string status, List<string> blockedReasons, Dictionary<string, object>? context)
    {
        var contextInfo = context != null
            ? $"\nContext: Rack Position={context.GetValueOrDefault("Position")}, " +
              $"Switches={context.GetValueOrDefault("SwitchCount")}"
            : "";

        return $@"You are a helpful assistant for a rack provisioning system. A technician is trying to provision a network rack.

Current Status: {status}

Blocked Reasons:
{string.Join("\n", blockedReasons.Select(r => $"- {r}"))}{contextInfo}

Please provide:
1. A brief, friendly explanation of what's wrong (1-2 sentences)
2. 3-4 specific remediation steps to fix the issues

Format your response clearly with the explanation first, then list steps as bullet points.
Keep language simple and non-technical where possible.";
    }

    private class GeminiResponse
    {
        public Candidate[]? Candidates { get; set; }
    }

    private class Candidate
    {
        public Content? Content { get; set; }
    }

    private class Content
    {
        public Part[]? Parts { get; set; }
    }

    private class Part
    {
        public string? Text { get; set; }
    }
}
