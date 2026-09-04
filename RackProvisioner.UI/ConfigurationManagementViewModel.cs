using RackProvisioner.Domain;
using RackProvisioner.Services;

namespace RackProvisioner.UI;

public class ConfigurationManagementViewModel
{
    private readonly IInventoryService _inventoryService;
    
    public List<Configuration> ActiveConfigs { get; set; } = new();
    public List<Configuration> ArchivedConfigs { get; set; } = new();
    public List<(Guid ConfigId, string Name, DateTime CreatedAt)> VersionHistory { get; set; } = new();
    public Configuration? SelectedConfig { get; set; }
    public bool IsLoading { get; set; }
    public string? ErrorMessage { get; set; }
    public string ActiveTab { get; set; } = "active";

    public ConfigurationManagementViewModel(IInventoryService inventoryService)
    {
        _inventoryService = inventoryService;
    }

    public async Task LoadConfigsAsync()
    {
        try
        {
            IsLoading = true;
            ErrorMessage = null;
            
            var allConfigs = await _inventoryService.GetAllConfigurationsAsync();
            ActiveConfigs = allConfigs.Where(c => c.IsActive).ToList();
            ArchivedConfigs = allConfigs.Where(c => !c.IsActive).ToList();
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to load configurations: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }

    public async Task LoadVersionHistoryAsync()
    {
        try
        {
            ErrorMessage = null;
            var allConfigs = await _inventoryService.GetAllConfigurationsAsync();
            VersionHistory = allConfigs
                .Where(c => c.IsActive)
                .OrderByDescending(c => c.CreatedAt)
                .Select(c => (c.Id, c.Name, c.CreatedAt))
                .ToList();
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to load version history: {ex.Message}";
        }
    }

    public async Task LoadVersionHistoryAsync(Guid configId)
    {
        try
        {
            ErrorMessage = null;
            var config = await _inventoryService.GetConfigurationByIdAsync(configId);
            if (config != null)
            {
                SelectedConfig = config;
                // Simulate version history - in a real system, this would come from audit/event logs
                VersionHistory = new List<(Guid, string, DateTime)> { (config.Id, config.Name, config.CreatedAt) };
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to load version history: {ex.Message}";
        }
    }

    public async Task SaveConfigAsync(Configuration config)
    {
        try
        {
            ErrorMessage = null;
            
            if (string.IsNullOrWhiteSpace(config.Name))
                throw new ArgumentException("Configuration name is required");
            
            if (string.IsNullOrWhiteSpace(config.Content))
                throw new ArgumentException("Configuration content is required");

            config.Id = Guid.NewGuid();
            config.IsActive = true;
            config.CreatedAt = DateTime.UtcNow;

            await _inventoryService.CreateConfigurationAsync(config);
            await LoadConfigsAsync();
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to save configuration: {ex.Message}";
        }
    }

    public async Task UpdateConfigAsync(Configuration config)
    {
        try
        {
            ErrorMessage = null;
            
            if (string.IsNullOrWhiteSpace(config.Name))
                throw new ArgumentException("Configuration name is required");
            
            if (string.IsNullOrWhiteSpace(config.Content))
                throw new ArgumentException("Configuration content is required");

            var existing = await _inventoryService.GetConfigurationByIdAsync(config.Id);
            if (existing == null)
                throw new InvalidOperationException("Configuration not found");

            config.UpdatedAt = DateTime.UtcNow;
            await _inventoryService.UpdateConfigurationAsync(config);
            await LoadConfigsAsync();
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to update configuration: {ex.Message}";
        }
    }

    public async Task ArchiveConfigAsync(Guid configId)
    {
        try
        {
            ErrorMessage = null;
            var config = await _inventoryService.GetConfigurationByIdAsync(configId);
            if (config != null)
            {
                config.IsActive = false;
                await _inventoryService.UpdateConfigurationAsync(config);
                await LoadConfigsAsync();
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to archive configuration: {ex.Message}";
        }
    }

    public async Task RestoreConfigAsync(Guid configId)
    {
        try
        {
            ErrorMessage = null;
            var config = await _inventoryService.GetConfigurationByIdAsync(configId);
            if (config != null)
            {
                config.IsActive = true;
                await _inventoryService.UpdateConfigurationAsync(config);
                await LoadConfigsAsync();
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to restore configuration: {ex.Message}";
        }
    }

    public async Task DeleteConfigAsync(Guid configId)
    {
        try
        {
            ErrorMessage = null;
            await _inventoryService.DeleteConfigurationAsync(configId);
            await LoadConfigsAsync();
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to delete configuration: {ex.Message}";
        }
    }

    public string GetFormattedDate(DateTime? date) 
        => date?.ToString("yyyy-MM-dd HH:mm:ss") ?? "N/A";
}
