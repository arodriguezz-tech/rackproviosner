using Xunit;
using RackProvisioner.Core;
using RackProvisioner.Domain;

namespace RackProvisioner.Tests;

public class EventBusTests
{
    [Fact]
    public void Publish_AndSubscribe_EventIsReceived()
    {
        // Arrange
        var eventBus = new InMemoryEventBus();
        RackInventoryLoadedEvent? receivedEvent = null;

        eventBus.Subscribe<RackInventoryLoadedEvent>(evt =>
        {
            receivedEvent = evt;
        });

        var testEvent = new RackInventoryLoadedEvent(
            Guid.NewGuid(),
            "RK001",
            2);

        // Act
        eventBus.Publish(testEvent);

        // Assert
        Assert.NotNull(receivedEvent);
        Assert.Equal("RK001", receivedEvent.RackSerial);
        Assert.Equal(2, receivedEvent.SwitchCount);
    }

    [Fact]
    public void MultipleSubscribers_ReceiveEvent()
    {
        // Arrange
        var eventBus = new InMemoryEventBus();
        int callCount = 0;

        eventBus.Subscribe<SwitchDiscoveredEvent>(evt => callCount++);
        eventBus.Subscribe<SwitchDiscoveredEvent>(evt => callCount++);

        // Act
        eventBus.Publish(new SwitchDiscoveredEvent(
            Guid.NewGuid(),
            "Model1",
            "Serial1",
            "AA:BB:CC:DD:EE:FF"));

        // Assert
        Assert.Equal(2, callCount);
    }
}

public class DomainModelTests
{
    [Fact]
    public void Rack_CanBeCreated()
    {
        // Arrange & Act
        var rack = new Rack
        {
            Serial = "RK001",
            Position = "RK1617",
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        // Assert
        Assert.NotNull(rack);
        Assert.Equal("RK001", rack.Serial);
        Assert.Equal("RK1617", rack.Position);
    }

    [Fact]
    public void Switch_WithRole()
    {
        // Arrange & Act
        var @switch = new Switch
        {
            Model = "Arista EOS",
            Serial = "SW001",
            MAC = "AA:BB:CC:DD:EE:FF",
            Role = SwitchRole.MX
        };

        // Assert
        Assert.Equal(SwitchRole.MX, @switch.Role);
        Assert.Equal("Arista EOS", @switch.Model);
    }

    [Fact]
    public void ReadinessEvaluationResult_StartsUnknown()
    {
        // Arrange & Act
        var result = new ReadinessEvaluationResult();

        // Assert
        Assert.Equal("Unknown", result.Status);
        Assert.Empty(result.BlockedReasons);
    }
}
