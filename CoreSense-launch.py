"""Windows package entry point with a smoke check for the frozen application."""
import sys

from app import CoreSense


app = CoreSense()
if "--smoke-test" in sys.argv:
    try:
        assert app.ai_assistant.classifier is not None
        assert app.ai_assistant.neural_network is not None
        assert "R5:" in app.ai_assistant.ask("Компьютер не включается, индикатор питания не горит")
        app.defense_page()
        app.answer_demo(True)
        app.update()
        assert any(step["rule"] == "R5" for step in app.ai_assistant.production.forward_chain(app.demo_session.facts)[1])
    finally:
        app.destroy()
else:
    app.mainloop()
