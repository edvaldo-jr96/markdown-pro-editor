import tkinter as tk
from tkinter import ttk


class MainWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Markdown Pro Editor")
        self.root.geometry("1100x700")

        self._setup_style()
        self._build_layout()

    def _setup_style(self) -> None:
        style = ttk.Style()
        # usa tema padrão disponível no sistema (Mint geralmente tem "clam" e outros)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(
            container,
            text="Markdown Pro Editor — Semana 1 (Base)",
            font=("Sans", 14, "bold"),
        )
        header.pack(anchor="w", pady=(0, 10))

        info = ttk.Label(
            container,
            text="Projeto inicial com arquitetura modular. Próximo passo: DocumentManager (Semana 2).",
        )
        info.pack(anchor="w")

        # placeholder: futuro layout editor/preview
        placeholder = ttk.LabelFrame(container, text="Workspace")
        placeholder.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        ttk.Label(
            placeholder,
            text="Aqui entra o editor e preview nas próximas semanas.",
        ).pack(anchor="center", pady=20)

    def run(self) -> None:
        self.root.mainloop()
