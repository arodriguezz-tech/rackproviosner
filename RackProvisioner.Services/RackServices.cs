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
}

public class InventoryService : IInventoryService
{
    private readonly RackRepository _rackRepository;
    private readonly IEventBus _eventBus;

    public InventoryService(RackRepository rackRepository, IEventBus eventBus)
    {
        _rackRepository = rackRepository;
        _eventBus = eventBus;
    }

    public async Task<Rack?> LoadRackBySerialAsync(string serial)
    {
        var rack = await _rackRepository.GetBySerialAsync(serial);
        if (rack != null)
        {
            _eventBus.Publish(new RackInventoryLoadedEvent(
                Guid.NewGuid(),
                rack.Serial,
                rack.Inventory.Count));
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
}

public interface IDiscoveryService
{
    Task<Switch?> DiscoverSwitchAsync(string model, string serial, string mac);
    Task<IEnumerable<Switch>> GetDiscoveredSwitchesAsync(int rackId);
}

public class DiscoveryService : IDiscoveryService
{
    private readonly SwitchRepository _switchRepository;
    private readonly IEventBus _eventBus;

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

    public async Task<IEnumerable<Switch>> GetDiscoveredSwitchesAsync(int rackId)
    {
        return await _switchRepository.GetByRackIdAsync(rackId);
    }
}

public interface IReadinessService
{
    Task<ReadinessEvaluationResult> EvaluateReadinessAsync(int rackId);
}

public class ReadinessService : IReadinessService
{
    private readonly RackProvisionerDbContext _context;
    private readonly IEventBus _eventBus;

    public ReadinessService(RackProvisionerDbContext context, IEventBus eventBus)
    {
        _context = context;
        _eventBus = eventBus;
    }

    public async Task<ReadinessEvaluationResult> EvaluateReadinessAsync(int rackId)
    {
        var rack = await _context.Racks.Include(r => r.Inventory).FirstOrDefaultAsync(r => r.Id == rackId);
        
        var result = new ReadinessEvaluationResult();
        
        if (rack == null)
        {
            result.Status = "Blocked";
            result.BlockedReasons.Add("Rack not found");
            return result;
        }

        if (!rack.Inventory.Any())
        {
            result.Status = "Blocked";
            result.BlockedReasons.Add("No switches discovered in inventory");
            return result;
        }

        var roleCount = rack.Inventory.Where(s => s.Role != SwitchRole.Unknown).GroupBy(s => s.Role).Count();
        if (roleCount != 3)
        {
            result.Status = "Blocked";
            result.BlockedReasons.Add("Not all switch roles assigned (MX, NS1, NS2 required)");
            return result;
        }

        result.Status = "Ready";
        
        _eventBus.Publish(new ReadinessEvaluatedEvent(
            Guid.NewGuid(),
            result));

        return result;
    }
}
