using RackProvisioner.Core;
using RackProvisioner.Services.AI;
using System.Collections.Concurrent;

namespace RackProvisioner.UI;

public class ReadinessViewModel
{
    private readonly IEventBus _eventBus;
    private readonly IReadinessExplainer _explainer;

    public string Status { get; private set; } = "Unknown";
    public List<string> BlockedReasons { get; private set; } = new();
    public string Explanation { get; private set; } = string.Empty;
    public DateTime LastUpdated { get; private set; } = DateTime.MinValue;

    // A simple cache to avoid repeated API calls for same reasons
    private readonly ConcurrentDictionary<string, string> _explanationCache = new();

    public ReadinessViewModel(IEventBus eventBus, IReadinessExplainer explainer)
    {
        _eventBus = eventBus;
        _explainer = explainer;

        // Subscribe to readiness events
        _eventBus.Subscribe<ReadinessEvaluatedEvent>(async e =>
        {
            Status = e.Result.Status ?? "Unknown";
            BlockedReasons = e.Result.BlockedReasons ?? new List<string>();
            LastUpdated = DateTime.UtcNow;

            // Build a cache key from reasons
            var key = string.Join("|", BlockedReasons);
            if (string.IsNullOrEmpty(key) && Status == "Ready")
            {
                Explanation = "✅ Rack is ready for provisioning. All checks passed.";
            }
            else if (_explanationCache.TryGetValue(key, out var cached))
            {
                Explanation = cached;
            }
            else
            {
                // Call explainer (may be Gemini or template fallback)
                try
                {
                    var explanation = await _explainer.ExplainReadinessDecisionAsync(Status, BlockedReasons, new Dictionary<string, object>
                    {
                        ["SwitchCount"] = BlockedReasons.Count
                    });

                    Explanation = explanation ?? string.Empty;
                    _explanationCache[key] = Explanation;
                }
                catch (Exception ex)
                {
                    Explanation = $"⚠️ Failed to generate explanation: {ex.Message}";
                }
            }
        });
    }

    // Expose a manual refresh in case UI wants to re-query
    public async Task<string> RefreshExplanationAsync()
    {
        var key = string.Join("|", BlockedReasons);
        try
        {
            var explanation = await _explainer.ExplainReadinessDecisionAsync(Status, BlockedReasons);
            Explanation = explanation ?? Explanation;
            _explanationCache[key] = Explanation;
        }
        catch
        {
            // ignore, keep existing explanation
        }
        return Explanation;
    }
}
