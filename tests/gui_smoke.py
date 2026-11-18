"""Run explicitly on a desktop: python -m tests.gui_smoke is not required by CI."""
import sys
import time
import os
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import CoreSense

temporary_data = tempfile.TemporaryDirectory()
os.environ['CORESENSE_DATA_DIR'] = temporary_data.name
app = CoreSense()
errors = []
app.report_callback_exception = lambda kind, value, tb: errors.append(str(value))
try:
    for page in [app.home_page, app.diagnostic_page, app.logic_page, app.frames_page,
                 app.semantic_page, app.ml_page, app.knowledge_page, app.about_page, app.history_page,
                 app.component_page, app.settings_page, app.ai_page]:
        page()
        app.update()
        print(page.__name__, "OK")
    app._set_prompt("Компьютер не включается, индикатор питания не горит")
    app.run_ai()
    deadline = time.monotonic() + 8
    while (app._busy or 'R5' not in app.ai_result.get('1.0', 'end')) and time.monotonic() < deadline:
        app.update()
        time.sleep(0.02)
    assert not app._busy, "Assistant did not finish"
    assert "R5" in app.ai_result.get("1.0", "end"), "No production chain"
    session_id = app.current_session.id
    app.advance_plan('not_helped')
    assert app.current_session.current_step() == 1
    app.history_page()
    app.open_history_session(session_id)
    assert app.current_session.current_step() == 1
    app.component_page()
    for name in app._component_nodes:
        app.select_component(name)
        assert name.upper() in app.component_details.get('1.0', 'end')
    for theme in ['light', 'dark', 'system']:
        app.change_theme(theme)
        app.settings_page()
        app.update()
    app.animation_value.set(False)
    app.change_animations()
    app.ai_page()
    app.run_ai()
    pending_id = app.current_session.id
    app.home_page()
    deadline = time.monotonic() + 8
    while app._busy and time.monotonic() < deadline:
        app.update()
        time.sleep(0.02)
    assert not app._busy
    assert app.store.load_session(pending_id)['answer'], 'Background result was lost after navigation'
    assert not errors, errors
    print("GUI_SMOKE_OK")
finally:
    app.destroy()
    temporary_data.cleanup()
