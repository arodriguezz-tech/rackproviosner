namespace RackProvisioner.Services.AI;

public interface IReadinessExplainer
{
    Task<string> ExplainReadinessDecisionAsync(
        string status,
        List<string> blockedReasons,
        Dictionary<string, object>? context = null,
        CancellationToken cancellationToken = default);
}

public class ReadinessExplanation
{
    public string Explanation { get; set; } = string.Empty;
    public List<string> RemediationSteps { get; set; } = new();
    public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
}
