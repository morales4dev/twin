"""Import-level smoke. No network."""


def test_import_src_modules():
    import app
    import context
    import styles
    import tools

    assert callable(app.chat)
    assert context.TWIN_SYSTEM_PROMPT
    assert tools.tools
    assert styles.CSS is not None
