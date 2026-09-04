using Xunit;
using Moq;
using RackProvisioner.Core;
using RackProvisioner.Domain;
using RackProvisioner.Services;
using RackProvisioner.Services.AI;
using RackProvisioner.Data;
using RackProvisioner.UI;
using Microsoft.EntityFrameworkCore;

namespace RackProvisioner.Tests;

public class UIIntegrationTests : IDisposable
{
    private readonly InMemoryEventBus _eventBus;
    private readonly RackProvisionerDbContext _context;
    private readonly RackRepository _rackRepository;
    private readonly SwitchRepository _switchRepository;
    private readonly ConfigurationRepository _configurationRepository;
    private readonly Mock<ISettingsService> _mockSettingsService;

    public UIIntegrationTests()
    {
        var options = new DbContextOptionsBuilder<RackProvisionerDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        _context = new RackProvisionerDbContext(options);
        _eventBus = new InMemoryEventBus();
        _rackRepository = new RackRepository(_context);
        _switchRepository = new SwitchRepository(_context);
        _configurationRepository = new ConfigurationRepository(_context);
        _mockSettingsService = new Mock<ISettingsService>();
        _mockSettingsService.Setup(s => s.Get(It.IsAny<string>(), It.IsAny<bool>()))
            .Returns((string key, bool defaultValue) => true);
    }

    public void Dispose()
    {
        _context.Dispose();
    }

    [Fact]
    public void ReadinessViewModel_SubscribesToReadinessEvaluatedEvent()
    {
        // Arrange
        var mockExplainer = new Mock<IReadinessExplainer>();
        mockExplainer.Setup(e => e.ExplainReadinessDecisionAsync(It.IsAny<string>(), It.IsAny<List<string>>(), It.IsAny<Dictionary<string, object>>()))
            .ReturnsAsync("Test explanation");

        var mockInventoryService = new Mock<IInventoryService>();
        var mockSkuService = new Mock<ISkuService>();
        var viewModel = new ReadinessViewModel(_eventBus, mockExplainer.Object, mockInventoryService.Object, mockSkuService.Object);
        var result = new ReadinessEvaluationResult
        {
            Status = "Ready",
            BlockedReasons = new()
        };

        // Act
        _eventBus.Publish(new ReadinessEvaluatedEvent(Guid.NewGuid(), result));

        // Assert
        Assert.Equal("Ready", viewModel.Status);
        Assert.Empty(viewModel.BlockedReasons);
    }

    [Fact]
    public async Task InventoryService_CreateRackAsync_CreatesRackAndPublishesEvent()
    {
        // Arrange
        var service = new InventoryService(_rackRepository, _switchRepository, _configurationRepository, _eventBus, _mockSettingsService.Object);
        RackInventoryLoadedEvent? publishedEvent = null;

        _eventBus.Subscribe<RackInventoryLoadedEvent>(evt =>
        {
            publishedEvent = evt;
        });

        // Act
        var rack = await service.CreateRackAsync("RK001", "RK1617", "SKU123", "BOM123");

        // Assert
        Assert.NotNull(rack);
        Assert.Equal("RK001", rack.Serial);
        Assert.Equal("RK1617", rack.Position);
        Assert.NotNull(publishedEvent);
        Assert.Equal("RK001", publishedEvent.RackSerial);
        Assert.Equal(0, publishedEvent.SwitchCount);
    }

    [Fact]
    public async Task InventoryService_CreateRackAsync_ThrowsOnMissingSerial()
    {
        // Arrange
        var service = new InventoryService(_rackRepository, _switchRepository, _configurationRepository, _eventBus, _mockSettingsService.Object);

        // Act & Assert
        var ex = await Assert.ThrowsAsync<ArgumentException>(() =>
            service.CreateRackAsync("", "RK1617"));
        Assert.Contains("Rack Serial is required", ex.Message);
    }

    [Fact]
    public async Task DiscoveryService_DiscoverDeviceAsync_PublishesSwitchDiscoveredEvent()
    {
        // Arrange
        var service = new DiscoveryService(_switchRepository, _eventBus);
        SwitchDiscoveredEvent? publishedEvent = null;

        _eventBus.Subscribe<SwitchDiscoveredEvent>(evt =>
        {
            publishedEvent = evt;
        });

        var discoveryResult = new DiscoveryResult
        {
            Serial = "SW001",
            MAC = "AA:BB:CC:DD:EE:FF",
            Model = "Arista EOS"
        };

        // Act
        await service.DiscoverDeviceAsync(discoveryResult);

        // Assert
        Assert.NotNull(publishedEvent);
        Assert.Equal("Arista EOS", publishedEvent.Model);
        Assert.Equal("SW001", publishedEvent.Serial);
        Assert.Equal("AA:BB:CC:DD:EE:FF", publishedEvent.MAC);
    }

    [Fact]
    public async Task InventoryService_VerifyIdentityAsync_FindsMatchingDeviceBySerial()
    {
        // Arrange
        var rack = new Rack { Serial = "RK001", Position = "RK1617", CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow };
        var @switch = new Switch
        {
            Model = "Arista EOS",
            Serial = "SW001",
            MAC = "AA:BB:CC:DD:EE:FF",
            Role = SwitchRole.MX,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        rack.Inventory = new() { @switch };

        await _context.Racks.AddAsync(rack);
        await _context.SaveChangesAsync();

        var service = new InventoryService(_rackRepository, _switchRepository, _configurationRepository, _eventBus, _mockSettingsService.Object);

        // Act
        var (status, role, reason) = await service.VerifyIdentityAsync("RK001", "SW001", null);

        // Assert
        Assert.Equal("OK", status);
        Assert.Equal("MX", role);
        Assert.Contains("identified", reason);
    }

    [Fact]
    public async Task InventoryService_VerifyIdentityAsync_FindsMatchingDeviceByMAC()
    {
        // Arrange
        var rack = new Rack { Serial = "RK001", Position = "RK1617", CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow };
        var @switch = new Switch
        {
            Model = "Arista EOS",
            Serial = "SW001",
            MAC = "AA:BB:CC:DD:EE:FF",
            Role = SwitchRole.NS1,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        rack.Inventory = new() { @switch };

        await _context.Racks.AddAsync(rack);
        await _context.SaveChangesAsync();

        var service = new InventoryService(_rackRepository, _switchRepository, _configurationRepository, _eventBus, _mockSettingsService.Object);

        // Act
        var (status, role, reason) = await service.VerifyIdentityAsync("RK001", null, "AA:BB:CC:DD:EE:FF");

        // Assert
        Assert.Equal("OK", status);
        Assert.Equal("NS1", role);
    }

    [Fact]
    public async Task InventoryService_ValidateInventoryAsync_SucceedsWithValidRack()
    {
        // Arrange
        var rack = new Rack { Serial = "RK001", Position = "RK1617", CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow };
        rack.Inventory = new()
        {
            new Switch { Model = "Arista1", Serial = "SW001", MAC = "AA:BB:CC:DD:EE:FF", Role = SwitchRole.MX, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow },
            new Switch { Model = "Arista2", Serial = "SW002", MAC = "AA:BB:CC:DD:EE:FE", Role = SwitchRole.NS1, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow },
            new Switch { Model = "Arista3", Serial = "SW003", MAC = "AA:BB:CC:DD:EE:FD", Role = SwitchRole.NS2, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow }
        };

        var service = new InventoryService(_rackRepository, _switchRepository, _configurationRepository, _eventBus, _mockSettingsService.Object);

        // Act & Assert
        await service.ValidateInventoryAsync(rack);
    }

    [Fact]
    public async Task InventoryService_ValidateInventoryAsync_ThrowsOnMissingRequiredRoles()
    {
        // Arrange
        var rack = new Rack { Serial = "RK001", Position = "RK1617", CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow };
        rack.Inventory = new()
        {
            new Switch { Model = "Arista1", Serial = "SW001", MAC = "AA:BB:CC:DD:EE:FF", Role = SwitchRole.MX, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow },
            new Switch { Model = "Arista2", Serial = "SW002", MAC = "AA:BB:CC:DD:EE:FE", Role = SwitchRole.NS1, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow }
        };

        var service = new InventoryService(_rackRepository, _switchRepository, _configurationRepository, _eventBus, _mockSettingsService.Object);

        // Act & Assert
        var ex = await Assert.ThrowsAsync<ArgumentException>(() =>
            service.ValidateInventoryAsync(rack));
        Assert.Contains("Missing required roles", ex.Message);
    }

    [Fact]
    public async Task InventoryService_ValidateInventoryAsync_ThrowsOnDuplicateRoles()
    {
        // Arrange
        var rack = new Rack { Serial = "RK001", Position = "RK1617", CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow };
        rack.Inventory = new()
        {
            new Switch { Model = "Arista1", Serial = "SW001", MAC = "AA:BB:CC:DD:EE:FF", Role = SwitchRole.MX, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow },
            new Switch { Model = "Arista2", Serial = "SW002", MAC = "AA:BB:CC:DD:EE:FE", Role = SwitchRole.MX, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow }
        };

        var service = new InventoryService(_rackRepository, _switchRepository, _configurationRepository, _eventBus, _mockSettingsService.Object);

        // Act & Assert
        var ex = await Assert.ThrowsAsync<ArgumentException>(() =>
            service.ValidateInventoryAsync(rack));
        Assert.Contains("Duplicate roles", ex.Message);
    }

    [Fact]
    public async Task InventoryService_ValidateInventoryAsync_ThrowsOnDuplicateSerials()
    {
        // Arrange
        var rack = new Rack { Serial = "RK001", Position = "RK1617", CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow };
        rack.Inventory = new()
        {
            new Switch { Model = "Arista1", Serial = "SW001", MAC = "AA:BB:CC:DD:EE:FF", Role = SwitchRole.MX, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow },
            new Switch { Model = "Arista2", Serial = "SW001", MAC = "AA:BB:CC:DD:EE:FE", Role = SwitchRole.NS1, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow },
            new Switch { Model = "Arista3", Serial = "SW003", MAC = "AA:BB:CC:DD:EE:FD", Role = SwitchRole.NS2, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow }
        };

        var service = new InventoryService(_rackRepository, _switchRepository, _configurationRepository, _eventBus, _mockSettingsService.Object);

        // Act & Assert
        var ex = await Assert.ThrowsAsync<ArgumentException>(() =>
            service.ValidateInventoryAsync(rack));
        Assert.Contains("Duplicate serials", ex.Message);
    }

    [Fact]
    public async Task InventoryService_AddSwitchToRackAsync_PublishesEventAndUpdatesInventory()
    {
        // Arrange
        var rack = new Rack { Serial = "RK001", Position = "RK1617", CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow };
        await _context.Racks.AddAsync(rack);
        await _context.SaveChangesAsync();

        var service = new InventoryService(_rackRepository, _switchRepository, _configurationRepository, _eventBus, _mockSettingsService.Object);
        SwitchDiscoveredEvent? publishedEvent = null;

        _eventBus.Subscribe<SwitchDiscoveredEvent>(evt =>
        {
            publishedEvent = evt;
        });

        var @switch = new Switch
        {
            Model = "Arista EOS",
            Serial = "SW001",
            MAC = "AA:BB:CC:DD:EE:FF",
            Role = SwitchRole.MX
        };

        // Act
        await service.AddSwitchToRackAsync(rack.Id, @switch);

        // Assert
        Assert.NotNull(publishedEvent);
        Assert.Equal("SW001", publishedEvent.Serial);
        
        var savedSwitch = await _switchRepository.GetByIdAsync(@switch.Id);
        Assert.NotNull(savedSwitch);
        Assert.Equal(rack.Id, savedSwitch.RackId);
    }

    [Fact]
    public async Task ReadinessViewModel_GeneratesExplanation_WhenReadinessIsBlocked()
    {
        // Arrange
        var explainer = new TemplateExplainerService();
        var mockInventoryService = new Mock<IInventoryService>();
        var mockSkuService = new Mock<ISkuService>();
        var viewModel = new ReadinessViewModel(_eventBus, explainer, mockInventoryService.Object, mockSkuService.Object);

        var result = new ReadinessEvaluationResult
        {
            Status = "Blocked",
            BlockedReasons = new() { "MAC_MISMATCH", "MISSING_INVENTORY" }
        };

        // Act
        _eventBus.Publish(new ReadinessEvaluatedEvent(Guid.NewGuid(), result));

        // Allow event handler to complete
        await Task.Delay(100);

        // Assert
        Assert.Equal("Blocked", viewModel.Status);
        Assert.Equal(2, viewModel.BlockedReasons.Count);
        Assert.NotEmpty(viewModel.Explanation);
        Assert.Contains("MAC_MISMATCH", viewModel.Explanation);
        Assert.Contains("MISSING_INVENTORY", viewModel.Explanation);
    }

    [Fact]
    public async Task ReadinessViewModel_CachesExplanations_ForSameBlockedReasons()
    {
        // Arrange
        var callCount = 0;
        var mockExplainer = new Mock<IReadinessExplainer>();
        mockExplainer.Setup(e => e.ExplainReadinessDecisionAsync(
            It.IsAny<string>(),
            It.IsAny<List<string>>(),
            It.IsAny<Dictionary<string, object>>(),
            It.IsAny<CancellationToken>()))
            .Callback(() => callCount++)
            .ReturnsAsync("Cached explanation");

        var mockInventoryService = new Mock<IInventoryService>();
        var mockSkuService = new Mock<ISkuService>();
        var viewModel = new ReadinessViewModel(_eventBus, mockExplainer.Object, mockInventoryService.Object, mockSkuService.Object);

        var result = new ReadinessEvaluationResult
        {
            Status = "Blocked",
            BlockedReasons = new() { "MAC_MISMATCH" }
        };

        // Act - Publish same event twice
        _eventBus.Publish(new ReadinessEvaluatedEvent(Guid.NewGuid(), result));
        await Task.Delay(50);
        _eventBus.Publish(new ReadinessEvaluatedEvent(Guid.NewGuid(), result));
        await Task.Delay(50);

        // Assert - Explainer should be called only once due to caching
        Assert.Equal(1, callCount);
        Assert.Equal("Cached explanation", viewModel.Explanation);
    }

    [Fact]
    public async Task ReadinessViewModel_RefreshesInventoryStatus_WhenRackLoaded()
    {
        // Arrange
        var rack = new Rack { Serial = "RK001", Position = "RK1617", CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow };
        rack.Inventory = new()
        {
            new Switch { Model = "Arista1", Serial = "SW001", MAC = "AA:BB:CC:DD:EE:FF", Role = SwitchRole.MX, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow },
            new Switch { Model = "Arista2", Serial = "SW002", MAC = "AA:BB:CC:DD:EE:FE", Role = SwitchRole.NS1, CreatedAt = DateTime.UtcNow, UpdatedAt = DateTime.UtcNow }
        };
        await _context.Racks.AddAsync(rack);
        await _context.SaveChangesAsync();

        var mockExplainer = new Mock<IReadinessExplainer>();
        var inventoryService = new InventoryService(_rackRepository, _switchRepository, _configurationRepository, _eventBus, _mockSettingsService.Object);
        var mockSkuService = new Mock<ISkuService>();
        var viewModel = new ReadinessViewModel(_eventBus, mockExplainer.Object, inventoryService, mockSkuService.Object);

        // Act - Initialize current rack to enable event-driven updates
        await viewModel.RefreshReadinessAsync("RK001");
        _eventBus.Publish(new RackInventoryLoadedEvent(rack.Id, "RK001", 2));
        await Task.Delay(100);

        // Assert
        Assert.Equal("Partial", viewModel.InventoryStatus);
        Assert.Equal(2, viewModel.DeviceCount);
    }

    [Fact]
    public async Task TemplateExplainerService_ExplainsAllBlockedReasons_WithProperFormatting()
    {
        // Arrange
        var explainer = new TemplateExplainerService();
        var allReasons = new List<string>
        {
            "MAC_MISMATCH",
            "MISSING_INVENTORY",
            "INCOMPLETE_ROLE_ASSIGNMENT",
            "LLDP_MISMATCH",
            "CONFIG_NOT_FOUND",
            "UNSUPPORTED_HARDWARE"
        };

        // Act
        var explanation = await explainer.ExplainReadinessDecisionAsync("Blocked", allReasons);

        // Assert
        Assert.NotEmpty(explanation);
        foreach (var reason in allReasons)
        {
            Assert.Contains(reason, explanation);
        }
        Assert.Contains("❌ Provisioning is blocked", explanation);
        Assert.Contains("Steps to resolve", explanation);
    }

    [Fact]
    public async Task TemplateExplainerService_ExplainsReadyStatus_SuccessMessage()
    {
        // Arrange
        var explainer = new TemplateExplainerService();

        // Act
        var explanation = await explainer.ExplainReadinessDecisionAsync("Ready", new());

        // Assert
        Assert.NotEmpty(explanation);
        Assert.Contains("✅", explanation);
        Assert.Contains("ready for provisioning", explanation);
    }

    [Fact]
    public async Task ReadinessViewModel_ProvidesMissingInventoryTemplate_WithRemediationSteps()
    {
        // Arrange
        var explainer = new TemplateExplainerService();
        var mockInventoryService = new Mock<IInventoryService>();
        var mockSkuService = new Mock<ISkuService>();
        var viewModel = new ReadinessViewModel(_eventBus, explainer, mockInventoryService.Object, mockSkuService.Object);

        var result = new ReadinessEvaluationResult
        {
            Status = "Blocked",
            BlockedReasons = new() { "MISSING_INVENTORY" }
        };

        // Act
        _eventBus.Publish(new ReadinessEvaluatedEvent(Guid.NewGuid(), result));
        await Task.Delay(100);

        // Assert
        Assert.Contains("Manually add missing device", viewModel.Explanation);
        Assert.Contains("Enter device model", viewModel.Explanation);
        Assert.Contains("Assign appropriate role", viewModel.Explanation);
    }
}
