namespace RackProvisioner.Core;

public interface IEventBus
{
    void Publish<T>(T @event) where T : IDomainEvent;
    void Subscribe<T>(Action<T> handler) where T : IDomainEvent;
}

public class InMemoryEventBus : IEventBus
{
    private readonly Dictionary<Type, List<Delegate>> _subscribers = new();

    public void Publish<T>(T @event) where T : IDomainEvent
    {
        var eventType = typeof(T);
        if (_subscribers.TryGetValue(eventType, out var handlers))
        {
            foreach (var handler in handlers)
            {
                handler.DynamicInvoke(@event);
            }
        }
    }

    public void Subscribe<T>(Action<T> handler) where T : IDomainEvent
    {
        var eventType = typeof(T);
        if (!_subscribers.ContainsKey(eventType))
        {
            _subscribers[eventType] = new List<Delegate>();
        }
        _subscribers[eventType].Add(handler);
    }
}
