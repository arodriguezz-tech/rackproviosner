using RackProvisioner.Core;
using RackProvisioner.Services;
using RackProvisioner.Services.AI;
using System.Collections.Concurrent;

namespace RackProvisioner.UI;

public class ReadinessViewModel
{
    private readonly IEventBus _eventBus;
    private readonly IReadinessExplainer _explainer;
    private readonly IInventoryService _inventoryService;
    private readonly ISkuService _skuService;

    public string Status { get; private set; } = "Unknown";
    public List<string> BlockedReasons { get; private set; } = new();
    public string Explanation { get; private set; } = string.Empty;
    public DateTime LastUpdated { get; private set; } = DateTime.MinValue;

    // Inventory status
    public string InventoryStatus { get; private set; } = "Unknown";
    public int DeviceCount { get; private set; } = 0;
    public List<(string Role, string Model, string Serial)> Devices { get; private set; } = new();

    // Configuration status
    public string ConfigurationStatus { get; private set; } = "Unknown";
    public string? LatestVersion { get; private set; } = null;
    public List<(Guid ConfigId, string Name, DateTime CreatedAt)> ConfigurationHistory { get; private set; } = new();

    // UI state
    public bool IsEvaluating { get; private set; } = false;
    public string? ErrorMessage { get; private set; } = null;
    public string? CurrentRackSerial { get; private set; } = null;

    // A simple cache to avoid repeated API calls for same reasons
    private readonly ConcurrentDictionary<string, string> _explanationCache = new();

    public ReadinessViewModel(
        IEventBus eventBus,
        IReadinessExplainer explainer,
        IInventoryService inventoryService,
        ISkuService skuService)
    {
        _eventBus = eventBus;
        _explainer = explainer;
        _inventoryService = inventoryService;
        _skuService = skuService;

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

        _eventBus.Subscribe<RackInventoryLoadedEvent>(async e =>
        {
            if (CurrentRackSerial == e.RackSerial)
            {
                await RefreshInventoryStatusAsync(e.RackSerial);
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

    public async Task RefreshReadinessAsync(string rackSerial)
    {
        try
        {
            IsEvaluating = true;
            ErrorMessage = null;
            CurrentRackSerial = rackSerial;

            var rack = await _inventoryService.LoadRackBySerialAsync(rackSerial);
            await RefreshInventoryStatusAsync(rackSerial);
            await RefreshConfigurationStatusAsync(rack?.Id ?? Guid.Empty);
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to refresh readiness: {ex.Message}";
        }
        finally
        {
            IsEvaluating = false;
        }
    }

    private async Task RefreshInventoryStatusAsync(string rackSerial)
    {
        try
        {
            var rack = await _inventoryService.GetRackBySerialAsync(rackSerial);
            if (rack == null)
            {
                InventoryStatus = "Empty";
                DeviceCount = 0;
                Devices.Clear();
                return;
            }

            DeviceCount = rack.Inventory?.Count ?? 0;
            Devices = rack.Inventory?
                .Select(d => (d.Role.ToString(), d.Model, d.Serial))
                .ToList() ?? new();

            if (DeviceCount == 0)
            {
                InventoryStatus = "Empty";
            }
            else if (DeviceCount < 3)
            {
                InventoryStatus = "Partial";
            }
            else
            {
                InventoryStatus = "Complete";
            }
        }
        catch (Exception ex)
        {
            InventoryStatus = "Error";
            ErrorMessage = $"Failed to load inventory: {ex.Message}";
        }
    }

    private async Task RefreshConfigurationStatusAsync(Guid rackId)
    {
        try
        {
            if (rackId == Guid.Empty)
            {
                ConfigurationStatus = "Missing";
                LatestVersion = null;
                ConfigurationHistory.Clear();
                return;
            }

            var latestConfig = await _skuService.GetLatestConfigurationAsync(rackId);
            var history = (await _skuService.GetConfigurationHistoryAsync(rackId)).ToList();

            if (latestConfig == null)
            {
                ConfigurationStatus = "Missing";
                LatestVersion = null;
            }
            else
            {
                LatestVersion = latestConfig.Name;
                ConfigurationStatus = "Latest";
            }

            ConfigurationHistory = history
                .Select(c => (c.Id, c.Name, c.CreatedAt))
                .ToList();
        }
        catch (Exception ex)
        {
            ConfigurationStatus = "Error";
            ErrorMessage = $"Failed to load configuration: {ex.Message}";
        }
    }
}
