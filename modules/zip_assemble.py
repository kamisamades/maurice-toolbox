#!/usr/bin/env python3
"""Module de réassemblage d'une archive ZIP scindée."""

import os
import re
import tkinter as tk
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from config import *


class ZipAssemble:
    """Réassemble les parties d'une archive ZIP scindée."""

    VERSION = "1.0.0"
    AUTHOR = "Maurice"
    RELEASE_DATE = "07/09/2026"

    PART_PATTERN = re.compile(r"^(?P<base>.+\.zip)\.part(?P<number>\d+)$", re.IGNORECASE)

    def __init__(self, root):
        self.root = root
        self.root.title(f"Zip Assemble ({self.VERSION} - {self.RELEASE_DATE})")
        self.root.geometry("700x550")
        self.root.minsize(600, 450)
        self.root.configure(bg=WINDOW_BG_COLOR)

        self.selected_parts = []
        self.selected_zipfile = tk.StringVar()

        self._create_widgets()
        self.root.after(100, self._center_window)

    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        main_frame = tk.Frame(self.root, bg=WINDOW_BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            main_frame,
            text="Zip Assemble",
            font=("Arial", 18, "bold"),
            bg=WINDOW_BG_COLOR,
        ).pack(pady=(0, 5))
        tk.Label(
            main_frame,
            text="Réassemblez les parties d'une archive ZIP en un seul fichier.",
            font=("Arial", 10),
            bg=WINDOW_BG_COLOR,
            fg=DESC_TEXT_COLOR,
        ).pack(pady=(0, 15))

        parts_frame = tk.Frame(main_frame, bg=WINDOW_BG_COLOR)
        parts_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        tk.Label(
            parts_frame,
            text="Parties sélectionnées :",
            font=("Arial", 10, "bold"),
            bg=WINDOW_BG_COLOR,
        ).pack(anchor=tk.W, pady=(0, 5))
        list_container = tk.Frame(parts_frame, bg="white", relief=tk.SUNKEN, bd=1)
        list_container.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.parts_listbox = tk.Listbox(list_container, font=("Courier", 9), bg="white", yscrollcommand=scrollbar.set)
        self.parts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.parts_listbox.yview)

        select_frame = tk.Frame(main_frame, bg=WINDOW_BG_COLOR)
        select_frame.pack(fill=tk.X, pady=10)
        self._create_button(select_frame, "Sélectionner les parties", self._browse_parts).pack(side=tk.LEFT)

        output_frame = tk.Frame(main_frame, bg=WINDOW_BG_COLOR)
        output_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            output_frame,
            text="Fichier ZIP de sortie :",
            width=20,
            anchor=tk.W,
            font=("Arial", 10, "bold"),
            bg=WINDOW_BG_COLOR,
        ).pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.selected_zipfile, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._create_button(output_frame, "Parcourir", self._browse_output).pack(side=tk.LEFT, padx=(8, 0))

        action_frame = tk.Frame(main_frame, bg=WINDOW_BG_COLOR)
        action_frame.pack(fill=tk.X, pady=15)
        self.assemble_btn = self._create_button(action_frame, "Assembler le ZIP", self._assemble, state=tk.DISABLED)
        self.assemble_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._create_button(action_frame, "Fermer", self.root.destroy).pack(side=tk.LEFT)

        self.status_label = tk.Label(
            main_frame,
            text="Prêt — sélectionnez les parties .zip.partXXX.",
            font=("Arial", 9),
            bg=WINDOW_BG_COLOR,
            fg=DESC_TEXT_COLOR,
            anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, pady=(5, 0))

    def _create_button(self, parent, text, command, state=tk.NORMAL):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=BT_BG_COLOR,
            fg=BT_TEXT_COLOR,
            font=("Arial", 9, "bold"),
            cursor="hand2",
            state=state,
        )

    @classmethod
    def _part_info(cls, path):
        match = cls.PART_PATTERN.match(os.path.basename(path))
        if not match:
            return None
        return match.group("base"), int(match.group("number"))

    @classmethod
    def _sort_and_validate_parts(cls, paths):
        if not paths:
            raise ValueError("Sélectionnez au moins une partie de l'archive.")

        parsed = [(path, cls._part_info(path)) for path in paths]
        if any(info is None for _path, info in parsed):
            raise ValueError("Tous les fichiers doivent respecter le format .zip.partXXX.")

        base_names = {info[0].lower() for _path, info in parsed}
        if len(base_names) != 1:
            raise ValueError("Les parties sélectionnées ne proviennent pas de la même archive.")

        sorted_parts = sorted(parsed, key=lambda item: item[1][1])
        numbers = [info[1] for _path, info in sorted_parts]
        if len(numbers) != len(set(numbers)):
            raise ValueError("Une même partie a été sélectionnée plusieurs fois.")
        if numbers != list(range(numbers[0], numbers[-1] + 1)) or numbers[0] != 1:
            raise ValueError("Il manque une ou plusieurs parties de l'archive.")
        return [path for path, _info in sorted_parts]

    def _browse_parts(self):
        paths = filedialog.askopenfilenames(
            title="Sélectionnez les parties de l'archive",
            filetypes=(("Parties ZIP", "*.zip.part*"), ("Tous les fichiers", "*.*")),
        )
        if not paths:
            return

        try:
            self.selected_parts = self._sort_and_validate_parts(paths)
        except ValueError as error:
            self.selected_parts = []
            self.parts_listbox.delete(0, tk.END)
            self.assemble_btn.config(state=tk.DISABLED)
            messagebox.showerror("Sélection invalide", str(error))
            return

        self.parts_listbox.delete(0, tk.END)
        for path in self.selected_parts:
            self.parts_listbox.insert(tk.END, os.path.basename(path))

        base_name = os.path.splitext(os.path.basename(self.selected_parts[0]))[0]
        output_name = f"{os.path.splitext(base_name)[0]}-assemble.zip"
        if not self.selected_zipfile.get():
            self.selected_zipfile.set(os.path.join(os.path.dirname(self.selected_parts[0]), output_name))
        self.assemble_btn.config(state=tk.NORMAL)
        self.status_label.config(text=f"{len(self.selected_parts)} partie(s) sélectionnée(s), prêtes à être assemblées.")

    def _browse_output(self):
        zip_path = filedialog.asksaveasfilename(
            title="Sélectionnez le fichier ZIP assemblé",
            initialfile=os.path.basename(self.selected_zipfile.get()) or "archive-assemble.zip",
            defaultextension=".zip",
            filetypes=(("Archive ZIP", "*.zip"), ("Tous les fichiers", "*.*")),
        )
        if zip_path:
            self.selected_zipfile.set(zip_path)

    def _assemble(self):
        try:
            parts = self._sort_and_validate_parts(self.selected_parts)
        except ValueError as error:
            messagebox.showerror("Erreur", str(error))
            return

        output_path = self.selected_zipfile.get()
        if not output_path:
            self._browse_output()
            output_path = self.selected_zipfile.get()
        if not output_path:
            return
        if os.path.abspath(output_path) in {os.path.abspath(path) for path in parts}:
            messagebox.showerror("Erreur", "Le fichier de sortie ne peut pas être une partie source.")
            return
        if os.path.exists(output_path) and not messagebox.askyesno(
            "Confirmation",
            f"Le fichier existe déjà :\n{output_path}\n\nVoulez-vous le remplacer ?",
        ):
            return

        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as destination:
                for part in parts:
                    with open(part, "rb") as source:
                        while chunk := source.read(1024 * 1024):
                            destination.write(chunk)
            with zipfile.ZipFile(output_path, "r") as archive:
                if archive.testzip() is not None:
                    raise zipfile.BadZipFile("L'archive assemblée contient un fichier corrompu.")
        except (OSError, zipfile.BadZipFile) as error:
            if os.path.exists(output_path):
                os.remove(output_path)
            messagebox.showerror("Erreur", f"L'assemblage a échoué :\n{error}")
            return

        self.status_label.config(text=f"Assemblage terminé — {len(parts)} partie(s).")
        messagebox.showinfo("Assemblage terminé", f"Archive créée :\n{output_path}")