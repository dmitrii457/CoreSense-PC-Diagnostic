"""Native desktop motion/layout checks. Does not capture or record the screen."""
import os
from pathlib import Path
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import CoreSense
from ui_components import MotionButton


def pump(app, seconds=0.3):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.update()
        time.sleep(0.008)


with tempfile.TemporaryDirectory() as folder:
    os.environ['CORESENSE_DATA_DIR'] = folder
    app = CoreSense()
    errors = []
    layout_issues = []
    app.report_callback_exception = lambda kind, value, tb: errors.append(str(value))
    pages = [app.home_page, app.ai_page, app.history_page, app.diagnostic_page, app.logic_page,
             app.frames_page, app.semantic_page, app.ml_page, app.knowledge_page,
             app.component_page, app.about_page, app.settings_page]
    try:
        for size in ['1100x760', '1220x820']:
            app.geometry(size)
            for page in pages:
                page()
                pump(app)
                assert abs(app.content.winfo_x()) <= 1 and abs(app.content.winfo_y()) <= 1
                height = app.content.winfo_height()
                for child in app.content.winfo_children():
                    if child.winfo_manager() == 'pack' and (not child.winfo_ismapped() or child.winfo_y() + child.winfo_height() > height + 1):
                        layout_issues.append((size, page.__name__, str(child), child.winfo_y(), child.winfo_height(), height))
        for _ in range(5):
            for page in [app.home_page, app.ai_page, app.component_page]:
                page()
                app.update()
        pump(app, 0.4)
        calls = []
        button = MotionButton(app.content, text='Check', command=lambda: calls.append(True))
        button.pack()
        button._on_enter()
        pump(app, 0.04)
        button._on_release()
        button._on_leave()
        button.configure(state='disabled')
        button._on_enter()
        button._on_release()
        assert len(calls) == 1, 'Button command invoked while disabled or duplicated'
        button.destroy()
        pump(app)
        for theme in ['light', 'dark']:
            app.change_theme(theme)
            app.home_page()
            pump(app, 0.15)
            app.settings_page()
            app.update()
            app.animation_value.set(False)
            app.change_animations()
            pump(app, 0.05)
            assert not app.motion.jobs, 'Animations continued after disabling motion'
            app.animation_value.set(True)
            app.change_animations()
        assert not errors, errors
        assert not layout_issues, layout_issues
        print('VISUAL_MOTION_SMOKE_OK: 12 pages, two sizes, both themes, rapid navigation, reduced motion')
    finally:
        app.destroy()
