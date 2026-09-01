# Alpha v3 Readiness UI Starter

Included:

- User-friendly PySide6 `ReadinessPanel`
- Technician and Engineer Mode rendering
- Readiness event subscription
- Provisioning-button safety gate
- Headless presenter tests
- pytest-qt widget tests
- Integration notes

## Install and run tests

```bash
pip install -e ".[test]"
export QT_QPA_PLATFORM=offscreen   # Linux CI
python -m pytest -q
```

The current execution environment did not contain PySide6 or pytest-qt, so the
headless presenter tests were executed here while widget tests were collected as
conditional UI tests for a Qt-enabled environment.
