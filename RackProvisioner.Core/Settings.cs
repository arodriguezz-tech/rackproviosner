namespace RackProvisioner.Core;

public interface ISettingsService
{
    T Get<T>(string key, T defaultValue);
    void Set<T>(string key, T value);
}

public class SettingsService : ISettingsService
{
    private readonly Dictionary<string, object> _settings = new();

    public T Get<T>(string key, T defaultValue)
    {
        if (_settings.TryGetValue(key, out var value) && value is T typedValue)
        {
            return typedValue;
        }
        return defaultValue;
    }

    public void Set<T>(string key, T value)
    {
        _settings[key] = value ?? throw new ArgumentNullException(nameof(value));
    }
}
