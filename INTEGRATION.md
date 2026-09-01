# Readiness UI Integration

Create one `ReadinessPanel` and inject the application's shared EventBus:

```python
readiness_panel = ReadinessPanel(
    event_bus=services.bus,
    engineer_mode=services.settings.get_bool("general", "engineer_mode", False),
)
```

Add it to the Single Switch or dedicated Readiness page. The panel subscribes to
`readiness.evaluated`; the ReadinessService remains the only component that
calculates the final safety decision.

When Settings publishes `settings.changed`, call:

```python
readiness_panel.set_engineer_mode(new_engineer_mode)
```

The panel never displays raw switch commands. Technician Mode shows friendly
outcomes; Engineer Mode adds rule keys, block codes, and technical explanations.
