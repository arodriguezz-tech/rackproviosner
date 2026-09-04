namespace RackProvisioner.Services.AI;

public class TemplateExplainerService : IReadinessExplainer
{
    private readonly Dictionary<string, (string Explanation, List<string> Steps)> _templates = new()
    {
        ["MAC_MISMATCH"] = (
            "Serial/MAC mismatch detected. The device identity does not match our inventory records.",
            new()
            {
                "Check cable connections on all ports",
                "Verify device serial numbers match the label",
                "Rescan device MAC address from console",
                "Update inventory if device was replaced"
            }),
        
        ["MISSING_INVENTORY"] = (
            "Device not found in rack inventory. Unable to provision until inventory is updated.",
            new()
            {
                "Manually add missing device to inventory",
                "Enter device model, serial, and MAC address",
                "Assign appropriate role (MX, NS1, or NS2)",
                "Save and retry readiness evaluation"
            }),
        
        ["INCOMPLETE_ROLE_ASSIGNMENT"] = (
            "Not all switch roles are assigned. All three roles (MX, NS1, NS2) are required.",
            new()
            {
                "Review discovered switches in inventory",
                "Assign each switch to correct role based on device model",
                "Verify role assignments against rack design",
                "Re-evaluate readiness when all roles assigned"
            }),
        
        ["LLDP_MISMATCH"] = (
            "LLDP neighbor discovery found unexpected connections. Cabling may be incorrect.",
            new()
            {
                "Physically verify cable connections match topology",
                "Check for misrouted or crossed cables",
                "Re-run LLDP neighbor discovery",
                "Confirm expected uplink connections"
            }),
        
        ["CONFIG_NOT_FOUND"] = (
            "Configuration profile not available for selected SKU. Check SKU manager.",
            new()
            {
                "Verify SKU selection is correct",
                "Check if configuration exists in SKU manager",
                "Create new configuration if needed",
                "Ensure profile is enabled and active"
            }),
        
        ["UNSUPPORTED_HARDWARE"] = (
            "Device model is not supported in this provisioning workflow.",
            new()
            {
                "Verify device model against supported list",
                "Check if firmware version meets minimum requirements",
                "Contact support if hardware is new or recently added",
                "Use alternative provisioning method if needed"
            })
    };

    public async Task<string> ExplainReadinessDecisionAsync(
        string status,
        List<string> blockedReasons,
        Dictionary<string, object>? context = null,
        CancellationToken cancellationToken = default)
    {
        if (status == "Ready")
        {
            return "✅ Rack is ready for provisioning. All checks passed. You may proceed with configuration application.";
        }

        var explanations = new List<string> { $"❌ Provisioning is blocked. Issues found:\n" };

        foreach (var reason in blockedReasons)
        {
            if (_templates.TryGetValue(reason, out var template))
            {
                explanations.Add($"\n**{reason}**\n{template.Explanation}");
                explanations.Add("\n**Steps to resolve:**");
                explanations.AddRange(template.Steps.Select(s => $"• {s}"));
            }
            else
            {
                explanations.Add($"\n• {reason}");
            }
        }

        return await Task.FromResult(string.Join("\n", explanations));
    }
}
