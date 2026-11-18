"""Small Tk animation scheduler: cancellable, time based, main-thread only."""
import time
import tkinter as tk


def color_value(widget, value):
    if isinstance(value, (tuple, list)):
        import customtkinter as ctk
        value = value[1 if ctk.get_appearance_mode() == "Dark" else 0]
    if value == "transparent":
        parent = widget.master
        while parent is not None:
            try:
                value = parent.cget("fg_color")
                if value != "transparent":
                    return color_value(parent, value)
            except (ValueError, tk.TclError):
                pass
            parent = parent.master
        return "#10131E"
    channels = widget.winfo_rgb(value)
    return "#" + "".join(f"{channel // 257:02x}" for channel in channels)


def mix_color(start, end, progress):
    progress = max(0.0, min(1.0, progress))
    a = [int(start[i:i+2], 16) for i in (1, 3, 5)]
    b = [int(end[i:i+2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x+(y-x)*progress):02x}" for x, y in zip(a, b))


class MotionEngine:
    def __init__(self, root, enabled):
        self.root = root
        self.enabled = enabled
        self.jobs = {}
        self.closed = False
        root.bind("<Destroy>", self._root_destroyed, add="+")

    def _root_destroyed(self, event):
        if event.widget is self.root:
            self.closed = True
            self.cancel_all()

    def cancel(self, owner, key):
        record = self.jobs.pop((owner, key), None)
        if record:
            try:
                self.root.after_cancel(record[0])
            except tk.TclError:
                pass

    def cancel_tree(self, parent):
        prefix = str(parent) + "."
        for owner, key in list(self.jobs):
            if owner is parent or str(owner).startswith(prefix):
                self.cancel(owner, key)

    def cancel_all(self, finish=False):
        records = list(self.jobs.items())
        for (owner, key), (_, final) in records:
            self.cancel(owner, key)
            if finish and final and owner.winfo_exists():
                final()

    def animate(self, owner, key, update, duration=200, done=None, delay=0):
        self.cancel(owner, key)
        if self.closed or not owner.winfo_exists():
            return

        def finish():
            update(1.0)
            if done:
                done()

        if not self.enabled():
            finish()
            return
        started = time.perf_counter() + delay / 1000

        def tick():
            if self.closed or not owner.winfo_exists():
                self.jobs.pop((owner, key), None)
                return
            progress = max(0, min(1, (time.perf_counter() - started) * 1000 / max(1, duration)))
            if not self.enabled():
                progress = 1
            update(1 - (1-progress)**3)
            if progress < 1:
                self.jobs[(owner, key)] = (self.root.after(16, tick), finish)
            else:
                self.jobs.pop((owner, key), None)
                if done:
                    done()

        self.jobs[(owner, key)] = (self.root.after(max(0, delay), tick), finish)

    def periodic(self, owner, key, update, interval=40):
        self.cancel(owner, key)
        if not self.enabled():
            update()
            return

        def tick():
            if self.closed or not owner.winfo_exists() or not self.enabled():
                self.jobs.pop((owner, key), None)
                return
            update()
            self.jobs[(owner, key)] = (self.root.after(interval, tick), None)

        self.jobs[(owner, key)] = (self.root.after(interval, tick), None)

    def defer(self, owner, key, callback, delay=0):
        self.cancel(owner, key)

        def run():
            self.jobs.pop((owner, key), None)
            if not self.closed and owner.winfo_exists():
                callback()

        self.jobs[(owner, key)] = (self.root.after(delay, run), None)
