using RackProvisioner.Core;
using RackProvisioner.Data;
using RackProvisioner.Domain;
using Microsoft.EntityFrameworkCore;

namespace RackProvisioner.Services;

public interface IInventoryService
{
    Task<Rack?> LoadRackBySerialAsync(string serial);
    Task SaveRackAsync(Rack rack);
    Task<IEnumerable<Rack>> GetAllRacksAsync();
    Task<Rack> CreateRackAsync(string serial, string position, string? sku = null, string? bom = null);
    Task<Rack?> GetRackBySerialAsync(string serial);
    Task AddSwitchToRackAsync(Guid rackId, Switch @switch);
    Task<(string Status, string? Role, string Reason)> VerifyIdentityAsync(string rackSerial, string? serial, string? mac);
    Task ValidateInventoryAsync(Rack rack);
}

public class InventoryService : IInventoryService
{
    private readonly RackRepository _rackRepository;
    private readonly SwitchRepository _switchRepository;
    private readonly IEventBus _eventBus;
    private readonly ISettingsService _settingsService;

    private static readonly HashSet<string> REQUIRED_ROLES = new() { "MX", "NS1", "NS2" };

    public InventoryService(
        RackRepository rackRepository,
        SwitchRepository switchRepository,
        IEventBus eventBus,
        ISettingsService settingsService)
    {
        _rackRepository = rackRepository;
        _switchRepository = switchRepository;
        _eventBus = eventBus;
        _settingsService = settingsService;
    }

    public async Task<Rack?> LoadRackBySerialAsync(string serial)
    {
        var rack = await _rackRepository.GetBySerialAsync(serial);
        if (rack != null)
        {
            _eventBus.Publish(new RackInventoryLoadedEvent(
                Guid.NewGuid(),
                rack.Serial,
                rack.Inventory?.Count ?? 0));
        }
        return rack;
    }

    public async Task SaveRackAsync(Rack rack)
    {
        rack.UpdatedAt = DateTime.UtcNow;
        await _rackRepository.UpdateAsync(rack);
        await _rackRepository.SaveAsync();
    }

    public async Task<IEnumerable<Rack>> GetAllRacksAsync()
    {
        return await _rackRepository.GetAllAsync();
    }

    public async Task<Rack> CreateRackAsync(string serial, string position, string? sku = null, string? bom = null)
    {
        if (string.IsNullOrWhiteSpace(serial))
            throw new ArgumentException("Rack Serial is required");

        var rack = new Rack
        {
            Serial = serial,
            Position = position,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        await _rackRepository.AddAsync(rack);
        await _rackRepository.SaveAsync();

        _eventBus.Publish(new RackInventoryLoadedEvent(
            Guid.NewGuid(),
            serial,
            0));

        return rack;
    }

    public async Task<Rack?> GetRackBySerialAsync(string serial)
    {
        return await _rackRepository.GetBySerialAsync(serial);
    }

    public async Task AddSwitchToRackAsync(Guid rackId, Switch @switch)
    {
        @switch.RackId = rackId;
        @switch.CreatedAt = DateTime.UtcNow;
        @switch.UpdatedAt = DateTime.UtcNow;

        await _switchRepository.AddAsync(@switch);
        await _switchRepository.SaveAsync();

        _eventBus.Publish(new SwitchDiscoveredEvent(
            Guid.NewGuid(),
            @switch.Model,
            @switch.Serial,
            @switch.MAC));
    }

    public async Task<(string Status, string? Role, string Reason)> VerifyIdentityAsync(string rackSerial, string? serial, string? mac)
    {
        if (!_settingsService.Get("inventory:enabled", false))
        {
            return ("DISABLED", null, "Inventory verification disabled");
        }

        var rack = await _rackRepository.GetBySerialAsync(rackSerial);
        if (rack == null)
        {
            return ("NOT_FOUND", null, "Rack not found in inventory");
        }

        if (rack.Inventory == null || !rack.Inventory.Any())
        {
            return ("EMPTY", null, "No devices in rack inventory");
        }

        var matching = rack.Inventory.FirstOrDefault(s =>
            (!string.IsNullOrEmpty(serial) && s.Serial == NormalizeSerial(serial)) ||
            (!string.IsNullOrEmpty(mac) && s.MAC == NormalizeMac(mac)));

        if (matching == null)
        {
            return ("NOT_FOUND", null, "Device not found in inventory");
        }

        return ("OK", matching.Role.ToString(), $"Device identified as {matching.Role}");
    }

    public async Task ValidateInventoryAsync(Rack rack)
    {
        if (string.IsNullOrEmpty(rack.Serial))
            throw new ArgumentException("Rack Serial is required");

        if (rack.Inventory == null || !rack.Inventory.Any())
            throw new ArgumentException("Rack must have at least 3 devices");

        var devices = rack.Inventory;

        var roleCounts = devices.GroupBy(d => d.Role).Where(g => g.Count() > 1).ToList();
        if (roleCounts.Any())
            throw new ArgumentException($"Duplicate roles found: {string.Join(", ", roleCounts.Select(g => g.Key))}");

        var assignedRoles = new HashSet<string>(devices.Select(d => d.Role.ToString()));
        var missing = REQUIRED_ROLES.Except(assignedRoles).ToList();
        if (missing.Any())
            throw new ArgumentException($"Missing required roles: {string.Join(", ", missing)}");

        foreach (var device in devices)
        {
            if (string.IsNullOrEmpty(device.Model))
                throw new ArgumentException($"{device.Role} model is required");

            if (string.IsNullOrEmpty(device.Serial) && string.IsNullOrEmpty(device.MAC))
                throw new ArgumentException($"{device.Role} serial or MAC is required");

            if (!string.IsNullOrEmpty(device.MAC) && device.MAC.Length != 17)
                throw new ArgumentException($"{device.Role} MAC is invalid (expected 17 chars with colons)");
        }

        var serials = devices.Where(d => !string.IsNullOrEmpty(d.Serial)).Select(d => d.Serial).ToList();
        var duplicateSerials = serials.GroupBy(s => s).Where(g => g.Count() > 1).Select(g => g.Key).ToList();
        if (duplicateSerials.Any())
            throw new ArgumentException($"Duplicate serials: {string.Join(", ", duplicateSerials)}");

        var macs = devices.Where(d => !string.IsNullOrEmpty(d.MAC)).Select(d => d.MAC).ToList();
        var duplicateMacs = macs.GroupBy(m => m).Where(g => g.Count() > 1).Select(g => g.Key).ToList();
        if (duplicateMacs.Any())
            throw new ArgumentException($"Duplicate MACs: {string.Join(", ", duplicateMacs)}");

        await Task.CompletedTask;
    }

    private static string NormalizeSerial(string serial) => serial?.Trim().ToUpperInvariant() ?? string.Empty;
    private static string NormalizeMac(string mac) => mac?.Trim().ToUpperInvariant() ?? string.Empty;
}

public interface ISkuService
{
    Task<Configuration> CreateConfigurationAsync(Guid rackId, string sku, string profile, string content, int majorVersion = 1, int minorVersion = 0);
    Task<Configuration?> GetLatestConfigurationAsync(Guid rackId);
    Task<Configuration?> GetConfigurationByVersionAsync(Guid rackId, int majorVersion, int minorVersion);
    Task<IEnumerable<Configuration>> GetConfigurationHistoryAsync(Guid rackId);
    Task ArchiveConfigurationAsync(int configurationId);
}

public class SkuService : ISkuService
{
    private readonly RackProvisionerDbContext _context;
    private readonly IEventBus _eventBus;

    public SkuService(RackProvisionerDbContext context, IEventBus eventBus)
    {
        _context = context;
        _eventBus = eventBus;
    }

    public async Task<Configuration> CreateConfigurationAsync(
        Guid rackId,
        string sku,
        string profile,
        string content,
        int majorVersion = 1,
        int minorVersion = 0)
    {
        if (string.IsNullOrWhiteSpace(sku))
            throw new ArgumentException("SKU is required");
        if (string.IsNullOrWhiteSpace(profile))
            throw new ArgumentException("Profile is required");
        if (string.IsNullOrWhiteSpace(content))
            throw new ArgumentException("Configuration content is required");

        var rack = await _context.Racks.FindAsync(rackId);
        if (rack == null)
            throw new ArgumentException($"Rack with ID {rackId} not found");

        var existing = await _context.Configurations
            .Where(c => c.RackId == rackId && c.SKU == sku && c.Profile == profile)
            .OrderByDescending(c => c.MajorVersion)
            .ThenByDescending(c => c.MinorVersion)
            .FirstOrDefaultAsync();

        if (existing != null && content != existing.Content)
        {
            minorVersion = existing.MinorVersion + 1;
            majorVersion = existing.MajorVersion;
        }

        var config = new Configuration
        {
            RackId = rackId,
            SKU = sku,
            Profile = profile,
            Content = content,
            MajorVersion = majorVersion,
            MinorVersion = minorVersion,
            CreatedAt = DateTime.UtcNow
        };

        await _context.Configurations.AddAsync(config);
        await _context.SaveChangesAsync();

        return config;
    }

    public async Task<Configuration?> GetLatestConfigurationAsync(Guid rackId)
    {
        return await _context.Configurations
            .Where(c => c.RackId == rackId)
            .OrderByDescending(c => c.MajorVersion)
            .ThenByDescending(c => c.MinorVersion)
            .FirstOrDefaultAsync();
    }

    public async Task<Configuration?> GetConfigurationByVersionAsync(Guid rackId, int majorVersion, int minorVersion)
    {
        return await _context.Configurations
            .FirstOrDefaultAsync(c =>
                c.RackId == rackId &&
                c.MajorVersion == majorVersion &&
                c.MinorVersion == minorVersion);
    }

    public async Task<IEnumerable<Configuration>> GetConfigurationHistoryAsync(Guid rackId)
    {
        return await _context.Configurations
            .Where(c => c.RackId == rackId)
            .OrderByDescending(c => c.CreatedAt)
            .ToListAsync();
    }

    public async Task ArchiveConfigurationAsync(int configurationId)
    {
        var config = await _context.Configurations.FindAsync(configurationId);
        if (config == null)
            throw new ArgumentException($"Configuration with ID {configurationId} not found");

        _context.Configurations.Remove(config);
        await _context.SaveChangesAsync();
    }
}

public interface IDiscoveryService
{
    Task<Switch?> DiscoverSwitchAsync(string model, string serial, string mac);
    Task<IEnumerable<Switch>> GetDiscoveredSwitchesAsync(Guid rackId);
    Task DiscoverDeviceAsync(DiscoveryResult result);
    Task<IEnumerable<Switch>> GetDiscoveredDevicesAsync();
    Task ClearDiscoveredDevicesAsync();
}

public class DiscoveryResult
{
    public string? Serial { get; set; }
    public string? MAC { get; set; }
    public string? Model { get; set; }
    public Dictionary<string, string>? LLDPData { get; set; }
}

public class DiscoveryService : IDiscoveryService
{
    private readonly SwitchRepository _switchRepository;
    private readonly IEventBus _eventBus;
    private readonly List<Switch> _discoveredDevices = new();

    public DiscoveryService(SwitchRepository switchRepository, IEventBus eventBus)
    {
        _switchRepository = switchRepository;
        _eventBus = eventBus;
    }

    public async Task<Switch?> DiscoverSwitchAsync(string model, string serial, string mac)
    {
        var @switch = new Switch
        {
            Model = model,
            Serial = serial,
            MAC = mac,
            Role = SwitchRole.Unknown,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        await _switchRepository.AddAsync(@switch);
        await _switchRepository.SaveAsync();

        _eventBus.Publish(new SwitchDiscoveredEvent(
            Guid.NewGuid(),
            model,
            serial,
            mac));

        return @switch;
    }

    public async Task<IEnumerable<Switch>> GetDiscoveredSwitchesAsync(Guid rackId)
    {
        return await _switchRepository.GetByRackIdAsync(rackId);
    }

    public async Task DiscoverDeviceAsync(DiscoveryResult result)
    {
        if (string.IsNullOrEmpty(result.Serial) && string.IsNullOrEmpty(result.MAC))
            throw new ArgumentException("Device must have Serial or MAC");

        var @switch = new Switch
        {
            Serial = result.Serial ?? string.Empty,
            MAC = result.MAC ?? string.Empty,
            Model = result.Model ?? "Unknown",
            Role = SwitchRole.Unknown,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        _discoveredDevices.Add(@switch);

        _eventBus.Publish(new SwitchDiscoveredEvent(
            Guid.NewGuid(),
            @switch.Model,
            @switch.Serial,
            @switch.MAC));

        await Task.CompletedTask;
    }

    public async Task<IEnumerable<Switch>> GetDiscoveredDevicesAsync()
    {
        return await Task.FromResult(_discoveredDevices.AsReadOnly());
    }

    public async Task ClearDiscoveredDevicesAsync()
    {
        _discoveredDevices.Clear();
        await Task.CompletedTask;
    }
}

public interface IReadinessService
{
    Task EvaluateRackReadinessAsync(Guid rackId);
}

public class ReadinessService : IReadinessService
{
    private readonly IInventoryService _inventoryService;
    private readonly IEventBus _eventBus;

    public ReadinessService(IInventoryService inventoryService, IEventBus eventBus)
    {
        _inventoryService = inventoryService;
        _eventBus = eventBus;
    }

    public async Task EvaluateRackReadinessAsync(Guid rackId)
    {
        var result = new ReadinessEvaluationResult { Status = "Pending" };
        _eventBus.Publish(new ReadinessEvaluatedEvent(Guid.NewGuid(), result));
        await Task.CompletedTask;
    }
}
