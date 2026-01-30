import tkinter as tk
from tkinter import scrolledtext


class EditorWidget(scrolledtext.ScrolledText):
    def __init__(self, master: tk.Widget) -> None:
        super().__init__(
            master,
            wrap=tk.WORD,
            font=("Monospace", 11),
            undo=True,
            maxundo=2000,
        )
        # evento de modificação do Tkinter
        self.bind("<<Modified>>", self._on_modified)

        self._on_change_callback = None

    def set_on_change(self, callback):
        """callback(content: str) -> None"""
        self._on_change_callback = callback

    def set_content(self, text: str) -> None:
        self.delete("1.0", tk.END)
        self.insert("1.0", text)
        self.edit_reset()
        self.edit_modified(False)

    def get_content(self) -> str:
        return self.get("1.0", tk.END).rstrip("\n")

    def _on_modified(self, _event=None) -> None:
        if self.edit_modified():
            self.edit_modified(False)
            if self._on_change_callback:
                self._on_change_callback(self.get_content())
