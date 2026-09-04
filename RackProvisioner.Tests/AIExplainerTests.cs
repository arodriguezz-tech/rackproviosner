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

    [Fact]
    public async Task ExplainReadinessDecisionAsync_MissingInventory_ReturnsMissingInventoryExplanation()
    {
        // Arrange
        var explainer = new TemplateExplainerService();
        var blockedReasons = new List<string> { "MISSING_INVENTORY" };

        // Act
        var result = await explainer.ExplainReadinessDecisionAsync("Blocked", blockedReasons);

        // Assert
        Assert.Contains("MISSING_INVENTORY", result);
        Assert.Contains("inventory", result, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("Manually add", result);
    }

    [Fact]
    public async Task ExplainReadinessDecisionAsync_Blocked_IncludesRemediationSteps()
    {
        // Arrange
        var explainer = new TemplateExplainerService();
        var blockedReasons = new List<string> { "CONFIG_NOT_FOUND" };

        // Act
        var result = await explainer.ExplainReadinessDecisionAsync("Blocked", blockedReasons);

        // Assert
        Assert.Contains("CONFIG_NOT_FOUND", result);
        Assert.Contains("Steps to resolve", result);
        Assert.Contains("•", result); // bullet points for steps
    }
}
