namespace RackProvisioner.Core;

public interface IDomainEvent
{
    Guid AggregateId { get; }
    DateTime OccurredAt { get; }
}

public record RackInventoryLoadedEvent(
    Guid AggregateId,
    string RackSerial,
    int SwitchCount) : IDomainEvent
{
    public DateTime OccurredAt { get; } = DateTime.UtcNow;
}

public record SwitchDiscoveredEvent(
    Guid AggregateId,
    string Model,
    string Serial,
    string MAC) : IDomainEvent
{
    public DateTime OccurredAt { get; } = DateTime.UtcNow;
}

public record ReadinessEvaluatedEvent(
    Guid AggregateId,
    ReadinessEvaluationResult Result) : IDomainEvent
{
    public DateTime OccurredAt { get; } = DateTime.UtcNow;
}

public class ReadinessEvaluationResult
{
    public string Status { get; set; } = "Unknown";
    public List<string> BlockedReasons { get; set; } = new();
    public DateTime EvaluatedAt { get; set; } = DateTime.UtcNow;
}
