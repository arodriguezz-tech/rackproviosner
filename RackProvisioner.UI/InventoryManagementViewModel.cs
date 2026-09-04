using RackProvisioner.Domain;
using RackProvisioner.Services;

namespace RackProvisioner.UI;

public class InventoryManagementViewModel
{
    private readonly IInventoryService _inventoryService;
    
    public List<Rack> Racks { get; set; } = new();
    public bool IsLoading { get; set; }
    public string? ErrorMessage { get; set; }

    public InventoryManagementViewModel(IInventoryService inventoryService)
    {
        _inventoryService = inventoryService;
    }

    public async Task LoadRacksAsync()
    {
        try
        {
            IsLoading = true;
            ErrorMessage = null;
            var racks = await _inventoryService.GetAllRacksAsync();
            Racks = racks.ToList();
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to load racks: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }

    public async Task CreateRackAsync(string serial, string position, string? sku = null)
    {
        try
        {
            ErrorMessage = null;
            await _inventoryService.CreateRackAsync(serial, position, sku);
            await LoadRacksAsync();
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to create rack: {ex.Message}";
        }
    }

    public async Task AddSwitchAsync(Guid rackId, string modelNumber, int ports)
    {
        try
        {
            ErrorMessage = null;
            var @switch = new Switch
            {
                Model = modelNumber,
                Serial = $"SW-{Guid.NewGuid().ToString().Substring(0, 8)}",
                MAC = string.Empty,
                Role = SwitchRole.Unknown
            };
            await _inventoryService.AddSwitchToRackAsync(rackId, @switch);
            await LoadRacksAsync();
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to add switch: {ex.Message}";
        }
    }

    public async Task RemoveSwitchAsync(Guid rackId, int switchId)
    {
        try
        {
            ErrorMessage = null;
            // For alpha, reload racks after deletion logic handled by UI
            // Full removal implementation deferred to phase 2
            await LoadRacksAsync();
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to remove switch: {ex.Message}";
        }
    }

    public async Task DeleteRackAsync(Guid rackId)
    {
        try
        {
            ErrorMessage = null;
            // For alpha, defer rack deletion to phase 2
            // Currently only supports inventory operations
            await LoadRacksAsync();
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to delete rack: {ex.Message}";
        }
    }

    public string GetRackPosition(Rack rack) => rack.Position ?? "Unknown";

    public int GetTotalSwitches(Rack rack) => rack.Inventory?.Count ?? 0;
}
