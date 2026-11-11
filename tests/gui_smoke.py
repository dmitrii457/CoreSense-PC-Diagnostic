"""Run explicitly on a desktop: python -m tests.gui_smoke is not required by CI."""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import FixAI

app = FixAI()
errors = []
app.report_callback_exception = lambda kind, value, tb: errors.append(str(value))
try:
    for page in [app.home_page, app.diagnostic_page, app.logic_page, app.frames_page,
                 app.semantic_page, app.ml_page, app.knowledge_page, app.about_page, app.ai_page]:
        page()
        app.update()
        print(page.__name__, "OK")
    app._set_prompt("Компьютер не включается, индикатор питания не горит")
    app.run_ai()
    deadline = time.monotonic() + 8
    while app._busy and time.monotonic() < deadline:
        app.update()
        time.sleep(0.02)
    assert not app._busy, "Assistant did not finish"
    assert "R5" in app.ai_result.get("1.0", "end"), "No production chain"
    app.run_ai()
    app.home_page()
    for _ in range(15):
        app.update()
        time.sleep(0.02)
    assert not errors, errors
    print("GUI_SMOKE_OK")
finally:
    app.destroy()
