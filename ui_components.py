"""Reusable visual components for the native desktop interface."""
import math
import time
import tkinter as tk
import customtkinter as ctk
from ui_motion import color_value, mix_color

BG = ("#F5F6FB", "#0B0E17")
SURFACE = ("#FFFFFF", "#131927")
SOFT = ("#F0EDFA", "#20243B")
BORDER = ("#E1E5F0", "#283147")
TEXT = ("#1D2740", "#F0F3FC")
MUTED = ("#65708A", "#99A6C1")
ACCENT = ("#7048CF", "#B29AFF")
PRIMARY = "#8057E6"


class MotionButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        self._motion_ready = False
        kwargs.setdefault("height", 38)
        kwargs.setdefault("corner_radius", 11)
        kwargs.setdefault("font", ("Segoe UI", 13))
        kwargs.setdefault("hover_color", "#9370EF")
        super().__init__(master, **kwargs)
        self._motion_ready = True
        self._visual_bg = color_value(self, self._fg_color)

    @property
    def engine(self):
        return getattr(self.winfo_toplevel(), "motion", None)

    def _paint(self, color):
        self._visual_bg = color
        self._canvas.itemconfig("inner_parts", outline=color, fill=color)
        if self._text_label is not None:
            self._text_label.configure(bg=color)
        if self._image_label is not None:
            self._image_label.configure(bg=color)

    def _animate_background(self, target, duration=150):
        target = color_value(self, target)
        start = self._visual_bg
        if self.engine:
            self.engine.animate(self, "button-bg", lambda p: self._paint(mix_color(start, target, p)), duration)
        else:
            self._paint(target)

    def _on_enter(self, event=None):
        self._mouse_inside = True
        if self._motion_ready and self._hover and self._state == "normal":
            self._animate_background(self._hover_color or self._fg_color)

    def _on_leave(self, event=None):
        self._mouse_inside = False
        if self._motion_ready:
            self._animate_background(self._fg_color, 200)

    def _on_release(self, event=None):
        if self._mouse_inside and self._state != tk.DISABLED:
            self._paint(mix_color(color_value(self, self._fg_color), "#FFFFFF", 0.16))
            self._animate_background(self._hover_color or self._fg_color, 180)
            if self._command is not None:
                self._command()

    def configure(self, require_redraw=False, **kwargs):
        color_changed = "fg_color" in kwargs or "hover_color" in kwargs or "state" in kwargs
        super().configure(require_redraw=require_redraw, **kwargs)
        if self._motion_ready and color_changed:
            self._animate_background(self._hover_color if self._mouse_inside and self._state == "normal" else self._fg_color)

    def _set_appearance_mode(self, mode_string):
        super()._set_appearance_mode(mode_string)
        if getattr(self, "_motion_ready", False):
            if self.engine:
                self.engine.cancel(self, "button-bg")
            self._paint(color_value(self, self._fg_color))


class SurfaceFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        solid = kwargs.get("fg_color") != "transparent" and kwargs.get("corner_radius", 18) != 0
        if solid:
            kwargs.setdefault("corner_radius", 18)
            kwargs.setdefault("border_width", 1)
            kwargs.setdefault("border_color", BORDER)
            kwargs.setdefault("fg_color", SURFACE)
        super().__init__(master, **kwargs)
        if solid:
            self._rest_border = self.cget("border_color")
            self.bind("<Enter>", self._hover_card, add="+")
            self.bind("<Leave>", self._leave_card, add="+")

    def _border_to(self, target):
        engine = getattr(self.winfo_toplevel(), "motion", None)
        if engine:
            start, end = color_value(self, self.cget("border_color")), color_value(self, target)
            engine.animate(self, "card-border", lambda p: self.configure(border_color=mix_color(start, end, p)), 190)

    def _hover_card(self, event=None):
        self._border_to(("#BBA7E7", "#66518F"))

    def _leave_card(self, event=None):
        self._border_to(self._rest_border)

    def _set_appearance_mode(self, mode_string):
        super()._set_appearance_mode(mode_string)
        if hasattr(self, "_rest_border"):
            engine = getattr(self.winfo_toplevel(), "motion", None)
            if engine:
                engine.cancel(self, "card-border")
            self.configure(border_color=self._rest_border)


class CoreOrbit(tk.Canvas):
    def __init__(self, master, size=180):
        super().__init__(master, width=size, height=size, highlightthickness=0,
                         background=color_value(master, master.cget("fg_color")))
        self.size = size
        self.started = time.perf_counter()
        self._draw()
        self.winfo_toplevel().motion.periodic(self, "orbit", self._draw, 40)

    def _draw(self):
        self.delete("all")
        size = self.size
        center = size/2
        light = ctk.get_appearance_mode() == "Light"
        angle = (time.perf_counter()-self.started)*0.32
        if not self.winfo_toplevel().preferences["animations"]:
            angle = 0.5
        for radius, color in [(76, "#D6CBF3" if light else "#32284B"), (58, "#C9B8F3" if light else "#493465"), (39, "#B59AEF" if light else "#68479C")]:
            self.create_oval(center-radius, center-radius, center+radius, center+radius, outline=color, width=1)
        self.create_rectangle(center-22, center-22, center+22, center+22, fill="#8057E6", outline="#CBB7FF", width=2)
        self.create_text(center, center, text="C", fill="#FFFFFF", font=("Segoe UI", 23, "bold"))
        for index, radius in enumerate((58, 76)):
            a = angle * (1 if index == 0 else -0.7) + index*2
            x, y = center+math.cos(a)*radius, center+math.sin(a)*radius
            self.create_oval(x-4, y-4, x+4, y+4, fill="#A58AFF" if index == 0 else "#77D9BD", outline="")
