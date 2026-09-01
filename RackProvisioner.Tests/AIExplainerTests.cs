using Xunit;
using RackProvisioner.Services.AI;

namespace RackProvisioner.Tests;

public class TemplateExplainerServiceTests
{
    [Fact]
    public async Task ExplainReadinessDecisionAsync_Ready_ReturnsSuccess()
    {
        // Arrange
        var explainer = new TemplateExplainerService();

        // Act
        var result = await explainer.ExplainReadinessDecisionAsync("Ready", new());

        // Assert
        Assert.Contains("✅", result);
        Assert.Contains("ready", result, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task ExplainReadinessDecisionAsync_BlockedWithMACMismatch_ReturnsExplanation()
    {
        // Arrange
        var explainer = new TemplateExplainerService();
        var blockedReasons = new List<string> { "MAC_MISMATCH" };

        // Act
        var result = await explainer.ExplainReadinessDecisionAsync("Blocked", blockedReasons);

        // Assert
        Assert.Contains("MAC", result);
        Assert.Contains("inventory", result, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("•", result);
    }

    [Fact]
    public async Task ExplainReadinessDecisionAsync_MultipleBlockedReasons_IncludesAll()
    {
        // Arrange
        var explainer = new TemplateExplainerService();
        var blockedReasons = new List<string> { "MAC_MISMATCH", "INCOMPLETE_ROLE_ASSIGNMENT" };

        // Act
        var result = await explainer.ExplainReadinessDecisionAsync("Blocked", blockedReasons);

        // Assert
        Assert.Contains("MAC_MISMATCH", result);
        Assert.Contains("INCOMPLETE_ROLE_ASSIGNMENT", result);
    }

    [Fact]
    public async Task ExplainReadinessDecisionAsync_UnknownReason_StillIncludedInOutput()
    {
        // Arrange
        var explainer = new TemplateExplainerService();
        var blockedReasons = new List<string> { "UNKNOWN_REASON" };

        // Act
        var result = await explainer.ExplainReadinessDecisionAsync("Blocked", blockedReasons);

        // Assert
        Assert.Contains("UNKNOWN_REASON", result);
    }
}

public class GeminiExplainerServiceTests
{
    [Fact]
    public async Task ExplainReadinessDecisionAsync_Ready_ReturnsFallback()
    {
        // Arrange
        var explainer = new GeminiExplainerService("dummy-key");

        // Act
        var result = await explainer.ExplainReadinessDecisionAsync("Ready", new());

        // Assert
        Assert.Contains("✅", result);
    }

    [Fact]
    public async Task ExplainReadinessDecisionAsync_APIFailure_ReturnsFallback()
    {
        // Arrange - use invalid key to trigger API failure
        var explainer = new GeminiExplainerService("invalid-key-12345");
        var blockedReasons = new List<string> { "TEST_REASON" };

        // Act
        var result = await explainer.ExplainReadinessDecisionAsync("Blocked", blockedReasons);

        // Assert - should fallback gracefully
        Assert.Contains("blocked", result, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("TEST_REASON", result);
    }
}
