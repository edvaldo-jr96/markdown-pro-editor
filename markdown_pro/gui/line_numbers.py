from __future__ import annotations
import tkinter as tk


class LineNumbers(tk.Canvas):
    def __init__(self, master: tk.Widget, text_widget: tk.Text, **kwargs) -> None:
        super().__init__(master, width=48, highlightthickness=0, **kwargs)
        self.text_widget = text_widget

        self.text_widget.bind("<KeyRelease>", lambda e: self.redraw())
        self.text_widget.bind("<MouseWheel>", lambda e: self.redraw())
        self.text_widget.bind("<ButtonRelease-1>", lambda e: self.redraw())
        self.text_widget.bind("<Configure>", lambda e: self.redraw())

        # Linux scroll (algumas distros)
        self.text_widget.bind("<Button-4>", lambda e: self.redraw())
        self.text_widget.bind("<Button-5>", lambda e: self.redraw())

    def redraw(self) -> None:
        self.delete("all")

        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            line = str(i).split(".")[0]
            self.create_text(40, y, anchor="ne", text=line)
            i = self.text_widget.index(f"{i}+1line")
