import re
import tkinter as tk
from tkinter import scrolledtext

from markdown_pro.utils.text_ops import wrap, make_link


class EditorWidget(scrolledtext.ScrolledText):
    def __init__(self, master: tk.Widget) -> None:
        super().__init__(
            master,
            wrap=tk.WORD,
            font=("Monospace", 11),
            undo=True,
            maxundo=2000,
        )

        self._on_change_callback = None
        self._highlight_after_id = None

        # modified callback
        self.bind("<<Modified>>", self._on_modified)

        # indent / tab
        self.bind("<Tab>", self._indent)
        self.bind("<Shift-Tab>", self._outdent)
        self.bind("<Return>", self._newline_with_indent)

        # tags (linha ativa + markdown simples)
        self.tag_config("active_line", background="#f0f2f5")

        self.tag_config("md_header", font=("Monospace", 11, "bold"))
        self.tag_config("md_codefence", font=("Monospace", 11, "bold"))
        self.tag_config("md_bold", font=("Monospace", 11, "bold"))
        self.tag_config("md_italic", font=("Monospace", 11, "italic"))

        # um único handler de KeyRelease (evita override de bind)
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<ButtonRelease-1>", lambda e: self._highlight_active_line())

    def set_on_change(self, callback):
        self._on_change_callback = callback

    def set_content(self, text: str) -> None:
        self.delete("1.0", tk.END)
        self.insert("1.0", text)
        self.edit_reset()
        self.edit_modified(False)
        self._highlight_active_line()
        self._apply_markdown_highlight()

    def get_content(self) -> str:
        return self.get("1.0", tk.END).rstrip("\n")

    # ---------- events ----------
    def _on_modified(self, _event=None) -> None:
        if self.edit_modified():
            self.edit_modified(False)
            if self._on_change_callback:
                self._on_change_callback(self.get_content())

    def _on_key_release(self, _event=None) -> None:
        self._highlight_active_line()
        self._debounced_highlight()

    # ---------- indentation ----------
    def _indent(self, _event=None):
        try:
            start = self.index("sel.first")
            end = self.index("sel.last")
        except tk.TclError:
            self.insert(tk.INSERT, "    ")
            return "break"

        start_line = int(start.split(".")[0])
        end_line = int(end.split(".")[0])

        for line in range(start_line, end_line + 1):
            self.insert(f"{line}.0", "    ")
        return "break"

    def _outdent(self, _event=None):
        try:
            start = self.index("sel.first")
            end = self.index("sel.last")
        except tk.TclError:
            return "break"

        start_line = int(start.split(".")[0])
        end_line = int(end.split(".")[0])

        for line in range(start_line, end_line + 1):
            line_start = f"{line}.0"
            chunk = self.get(line_start, f"{line}.4")
            if chunk == "    ":
                self.delete(line_start, f"{line}.4")
            elif chunk.startswith("\t"):
                self.delete(line_start, f"{line}.1")
        return "break"

    def _newline_with_indent(self, _event=None):
        line_start = self.index("insert linestart")
        line_text = self.get(line_start, self.index("insert lineend"))
        indent = re.match(r"[ \t]*", line_text).group(0)

        self.insert(tk.INSERT, "\n" + indent)
        return "break"

    # ---------- formatting ----------
    def toggle_wrap_selection(self, left: str, right: str):
        try:
            start = self.index("sel.first")
            end = self.index("sel.last")
            selected = self.get(start, end)
            self.delete(start, end)
            self.insert(start, wrap(selected, left, right))
        except tk.TclError:
            self.insert(tk.INSERT, left + right)
            self.mark_set(tk.INSERT, f"{tk.INSERT}-{len(right)}c")

    def insert_link(self):
        # se tiver seleção, transforma seleção em link
        try:
            start = self.index("sel.first")
            end = self.index("sel.last")
            selected = self.get(start, end) or "texto"
            snippet = make_link(selected, "https://")
            self.delete(start, end)
            self.insert(start, snippet)
            return
        except tk.TclError:
            pass

        # sem seleção: insere no cursor
        snippet = make_link("texto", "https://")
        self.insert(tk.INSERT, snippet)

    def insert_heading(self, level: int = 1):
        level = max(1, min(level, 6))
        prefix = "#" * level + " "
        line_start = self.index("insert linestart")
        self.insert(line_start, prefix)

    # ---------- highlights ----------
    def _highlight_active_line(self):
        self.tag_remove("active_line", "1.0", tk.END)
        line = self.index("insert").split(".")[0]
        self.tag_add("active_line", f"{line}.0", f"{line}.end")

    def _debounced_highlight(self):
        if self._highlight_after_id:
            self.after_cancel(self._highlight_after_id)
        self._highlight_after_id = self.after(200, self._apply_markdown_highlight)

    def _apply_markdown_highlight(self):
        for tag in ("md_header", "md_codefence", "md_bold", "md_italic"):
            self.tag_remove(tag, "1.0", tk.END)

        text = self.get("1.0", tk.END)

        # headers
        for m in re.finditer(r"(?m)^(#{1,6})\s+(.+)$", text):
            self.tag_add("md_header", self._index_from_pos(m.start()), self._index_from_pos(m.end()))

        # code fences
        for m in re.finditer(r"(?m)^```.*$", text):
            self.tag_add("md_codefence", self._index_from_pos(m.start()), self._index_from_pos(m.end()))

        # bold **text**
        for m in re.finditer(r"\*\*(.+?)\*\*", text):
            self.tag_add("md_bold", self._index_from_pos(m.start()), self._index_from_pos(m.end()))

        # italic *text* (bem simples)
        for m in re.finditer(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", text):
            self.tag_add("md_italic", self._index_from_pos(m.start()), self._index_from_pos(m.end()))

    def _index_from_pos(self, pos: int) -> str:
        return f"1.0+{pos}c"
