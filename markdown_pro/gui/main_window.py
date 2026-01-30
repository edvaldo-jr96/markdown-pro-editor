from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from markdown_pro.core.document_manager import DocumentManager
from markdown_pro.gui.editor_widget import EditorWidget
from markdown_pro.gui.line_numbers import LineNumbers
from markdown_pro.gui.find_replace_dialog import FindReplaceDialog

class MainWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Markdown Pro Editor")
        self.root.geometry("1100x700")

        self.doc = DocumentManager()

        self._setup_style()
        self._build_layout()
        self._build_menu()
        self._bind_shortcuts()

        self._load_new_document()

        # fechar com confirmação se tiver alterações
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Pronto")
        self.title_var = tk.StringVar(value="Sem título")

        header = ttk.Frame(container)
        header.pack(fill=tk.X)

        ttk.Label(header, textvariable=self.title_var, font=("Sans", 14, "bold")).pack(
            side=tk.LEFT
        )
        ttk.Label(header, textvariable=self.status_var).pack(side=tk.RIGHT)

        ttk.Separator(container).pack(fill=tk.X, pady=8)

        workspace = ttk.Frame(container)
        workspace.pack(fill=tk.BOTH, expand=True)

        self.editor = EditorWidget(workspace)
        self.editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.linenos = LineNumbers(workspace, self.editor)
        self.linenos.pack(side=tk.LEFT, fill=tk.Y)

        self.editor.set_on_change(self._on_editor_change)

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Novo", accelerator="Ctrl+N", command=self._new)
        file_menu.add_command(label="Abrir...", accelerator="Ctrl+O", command=self._open)
        file_menu.add_separator()
        file_menu.add_command(label="Salvar", accelerator="Ctrl+S", command=self._save)
        file_menu.add_command(
            label="Salvar como...", accelerator="Ctrl+Shift+S", command=self._save_as
        )

        # Recentes
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recentes", menu=self.recent_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self._on_close)

        menubar.add_cascade(label="Arquivo", menu=file_menu)

        self.root.config(menu=menubar)
        self._refresh_recents_menu()

    def _bind_shortcuts(self) -> None:
        self.root.bind_all("<Control-n>", lambda e: self._new())
        self.root.bind_all("<Control-o>", lambda e: self._open())
        self.root.bind_all("<Control-s>", lambda e: self._save())
        self.root.bind_all("<Control-Shift-S>", lambda e: self._save_as())
        self.root.bind_all("<Control-f>", lambda e: self._open_find())
        self.root.bind_all("<Control-b>", lambda e: self.editor.toggle_wrap_selection("**", "**"))
        self.root.bind_all("<Control-i>", lambda e: self.editor.toggle_wrap_selection("*", "*"))
        self.root.bind_all("<Control-k>", lambda e: self.editor.toggle_wrap_selection("`", "`"))
        self.root.bind_all("<Control-l>", lambda e: self.editor.insert_link())
        self.root.bind_all("<Control-Shift-H>", lambda e: self.editor.insert_heading(2))


    # ---------- Actions ----------
    def _load_new_document(self) -> None:
        self.doc.new_document()
        self.editor.set_content("")
        self._update_title()
        self.status_var.set("Novo documento")

    def _new(self) -> None:
        if not self._ensure_can_discard_or_save():
            return
        self._load_new_document()

    def _open(self) -> None:
        if not self._ensure_can_discard_or_save():
            return

        path_str = filedialog.askopenfilename(
            title="Abrir Markdown",
            filetypes=[("Markdown", "*.md"), ("Texto", "*.txt"), ("Todos", "*.*")],
        )
        if not path_str:
            return

        path = Path(path_str)
        try:
            content = self.doc.open_document(path)
            self.editor.set_content(content)
            self.status_var.set(f"Aberto: {path.name}")
            self._update_title()
            self._refresh_recents_menu()
        except Exception as ex:
            messagebox.showerror("Erro ao abrir", str(ex))

    def _save(self) -> None:
        try:
            content = self.editor.get_content()
            if self.doc.state.path is None:
                return self._save_as()
            saved_path = self.doc.save(content)
            self.status_var.set(f"Salvo: {saved_path.name}")
            self._update_title()
            self._refresh_recents_menu()
        except Exception as ex:
            messagebox.showerror("Erro ao salvar", str(ex))

    def _save_as(self) -> None:
        try:
            path_str = filedialog.asksaveasfilename(
                title="Salvar como",
                defaultextension=".md",
                filetypes=[("Markdown", "*.md"), ("Texto", "*.txt"), ("Todos", "*.*")],
            )
            if not path_str:
                return
            path = Path(path_str)
            content = self.editor.get_content()
            saved_path = self.doc.save_as(path, content)
            self.status_var.set(f"Salvo: {saved_path.name}")
            self._update_title()
            self._refresh_recents_menu()
        except Exception as ex:
            messagebox.showerror("Erro ao salvar", str(ex))

    def _open_recent(self, path_str: str) -> None:
        if not self._ensure_can_discard_or_save():
            return
        path = Path(path_str)
        if not path.exists():
            messagebox.showwarning("Arquivo não encontrado", f"Não existe:\n{path}")
            self._refresh_recents_menu()
            return
        try:
            content = self.doc.open_document(path)
            self.editor.set_content(content)
            self.status_var.set(f"Aberto: {path.name}")
            self._update_title()
            self._refresh_recents_menu()
        except Exception as ex:
            messagebox.showerror("Erro ao abrir", str(ex))

    # ---------- State ----------
    def _on_editor_change(self, _content: str) -> None:
        if not self.doc.state.dirty:
            self.doc.set_dirty(True)
            self._update_title()
            self.linenos.redraw()

    def _update_title(self) -> None:
        name = self.doc.state.path.name if self.doc.state.path else "Sem título"
        dirty = " *" if self.doc.state.dirty else ""
        self.title_var.set(f"{name}{dirty}")
        self.root.title(f"Markdown Pro Editor — {name}{dirty}")

    def _ensure_can_discard_or_save(self) -> bool:
        if not self.doc.state.dirty:
            return True

        choice = messagebox.askyesnocancel(
            "Alterações não salvas",
            "Você tem alterações não salvas.\nDeseja salvar antes de continuar?",
        )
        if choice is None:  # Cancel
            return False
        if choice is True:  # Yes
            self._save()
            # se ainda estiver dirty, salvamento falhou/cancelou
            return not self.doc.state.dirty
        return True  # No

    def _refresh_recents_menu(self) -> None:
        self.recent_menu.delete(0, tk.END)
        recents = self.doc.get_recents()

        if not recents:
            self.recent_menu.add_command(label="(vazio)", state=tk.DISABLED)
            return

        for path_str in recents:
            label = path_str
            self.recent_menu.add_command(
                label=label, command=lambda p=path_str: self._open_recent(p)
            )

    def _on_close(self) -> None:
        if not self._ensure_can_discard_or_save():
            return
        self.root.destroy()

    def _open_find(self) -> None:
        FindReplaceDialog(self.root, self.editor)

    def run(self) -> None:
        self.root.mainloop()
