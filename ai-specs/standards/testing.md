# Testing

- Pytest units live under `backend/tests/unit/`.
- Playwright drives the Gradio `ChatInterface` chat UI. v1 is a slot only: no live MiniMax suite, no network E2E against the model.
- Test deps are pinned in `backend/requirements-dev.txt`, not in production `backend/requirements.txt`:

```
pytest==9.1.1
playwright==1.62.0
```

- Config: `backend/pytest.ini` (`testpaths = tests`, `pythonpath = src`). Run from `backend/`.
- Unit smoke is import-level and must not hit the network.
- E2E under `backend/tests/e2e/` may be skipped until a later change implements Gradio chat coverage.
