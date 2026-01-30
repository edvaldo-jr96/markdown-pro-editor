from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox


class FindReplaceDialog(tk.Toplevel):
    def __init__(self, master: tk.Widget, text_widget: tk.Text) -> None:
        super().__init__(master)
        self.title("Buscar e Substituir")
        self.resizable(False, False)
        self.text_widget = text_widget

        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.case_var = tk.BooleanVar(value=False)

        self._build()
        self._bind()

        self.transient(master)
        self.grab_set()
        self.find_entry.focus_set()

    def _build(self) -> None:
        pad = {"padx": 10, "pady": 6}

        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True, **pad)

        ttk.Label(frm, text="Buscar:").grid(row=0, column=0, sticky="w")
        self.find_entry = ttk.Entry(frm, textvariable=self.find_var, width=40)
        self.find_entry.grid(row=0, column=1, sticky="we")

        ttk.Label(frm, text="Substituir:").grid(row=1, column=0, sticky="w")
        self.replace_entry = ttk.Entry(frm, textvariable=self.replace_var, width=40)
        self.replace_entry.grid(row=1, column=1, sticky="we")

        ttk.Checkbutton(frm, text="Diferenciar maiúsculas", variable=self.case_var)\
            .grid(row=2, column=1, sticky="w")

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=2, sticky="e", pady=(10, 0))

        ttk.Button(btns, text="Buscar próximo", command=self.find_next).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btns, text="Substituir", command=self.replace_one).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btns, text="Substituir tudo", command=self.replace_all).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btns, text="Fechar", command=self.destroy).pack(side=tk.LEFT)

        frm.columnconfigure(1, weight=1)

    def _bind(self) -> None:
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self.find_next())

    def _search_opts(self):
        needle = self.find_var.get()
        if not needle:
            messagebox.showinfo("Buscar", "Informe o texto para buscar.")
            return None, None
        nocase = 0 if self.case_var.get() else 1
        return needle, nocase

    def find_next(self) -> None:
        needle, nocase = self._search_opts()
        if needle is None:
            return

        self.text_widget.tag_remove("find_match", "1.0", tk.END)

        start = self.text_widget.index(tk.INSERT)
        idx = self.text_widget.search(
            needle, start, stopindex=tk.END, nocase=nocase
        )
        if not idx:
            # volta ao início
            idx = self.text_widget.search(
                needle, "1.0", stopindex=start, nocase=nocase
            )
            if not idx:
                messagebox.showinfo("Buscar", "Nenhuma ocorrência encontrada.")
                return

        end = f"{idx}+{len(needle)}c"
        self.text_widget.tag_add("find_match", idx, end)
        self.text_widget.tag_config("find_match", underline=True)
        self.text_widget.mark_set(tk.INSERT, end)
        self.text_widget.see(idx)

    def replace_one(self) -> None:
        needle, nocase = self._search_opts()
        if needle is None:
            return
        # se já tem seleção de match, substitui; senão busca
        ranges = self.text_widget.tag_ranges("find_match")
        if not ranges:
            self.find_next()
            ranges = self.text_widget.tag_ranges("find_match")
            if not ranges:
                return

        start, end = ranges[0], ranges[1]
        self.text_widget.delete(start, end)
        self.text_widget.insert(start, self.replace_var.get())
        self.text_widget.tag_remove("find_match", "1.0", tk.END)

    def replace_all(self) -> None:
        needle, nocase = self._search_opts()
        if needle is None:
            return

        self.text_widget.tag_remove("find_match", "1.0", tk.END)
        count = 0
        start = "1.0"
        while True:
            idx = self.text_widget.search(needle, start, stopindex=tk.END, nocase=nocase)
            if not idx:
                break
            end = f"{idx}+{len(needle)}c"
            self.text_widget.delete(idx, end)
            self.text_widget.insert(idx, self.replace_var.get())
            start = f"{idx}+1c"
            count += 1

        messagebox.showinfo("Substituir tudo", f"Substituições realizadas: {count}")
