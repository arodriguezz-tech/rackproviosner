namespace RackProvisioner.Domain;

public class Rack
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Serial { get; set; } = string.Empty;
    public string Position { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public List<Switch> Inventory { get; set; } = new();
}

public class Switch
{
    public int Id { get; set; }
    public Guid RackId { get; set; }
    public string Model { get; set; } = string.Empty;
    public string Serial { get; set; } = string.Empty;
    public string MAC { get; set; } = string.Empty;
    public SwitchRole Role { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public Rack? Rack { get; set; }
}

public class Configuration
{
    public int Id { get; set; }
    public Guid RackId { get; set; }
    public string SKU { get; set; } = string.Empty;
    public string Profile { get; set; } = string.Empty;
    public int MajorVersion { get; set; }
    public int MinorVersion { get; set; }
    public string Content { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public Rack? Rack { get; set; }
}

public class ReadinessState
{
    public int Id { get; set; }
    public Guid RackId { get; set; }
    public ReadinessStatus Status { get; set; }
    public List<string> BlockedReasons { get; set; } = new();
    public DateTime EvaluatedAt { get; set; }
    public Rack? Rack { get; set; }
}

public enum SwitchRole
{
    Unknown,
    MX,
    NS1,
    NS2
}

public enum ReadinessStatus
{
    Unknown,
    Ready,
    Blocked,
    Pending
}
