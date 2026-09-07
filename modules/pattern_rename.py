#!/usr/bin/env python3
"""Module de renommage séquentiel de fichiers par pattern."""

import fnmatch
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from config import *


class PatternRename:
    """Renomme les fichiers d'un dossier selon un pattern séquentiel."""

    VERSION = "1.0.0"
    AUTHOR = "Maurice"
    RELEASE_DATE = "07/09/2026"
    SYSTEM_FILE_PATTERNS = (
        "._*",
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
        ".DS_Store?",
        ".documentRevisions-V100",
        ".TemporaryItems",
        "~$*.doc*",
        "~$*.xls*",
        "~$*.ppt*",
        ".~lock.*",
        "*.tmp",
        "*.bak",
        "*.swp",
        "*.swo",
        "*~",
    )

    def __init__(self, root):
        self.root = root
        self.root.title(f"Pattern Rename ({self.VERSION} - {self.RELEASE_DATE})")
        self.root.geometry("750x600")
        self.root.minsize(650, 500)
        self.root.configure(bg=WINDOW_BG_COLOR)

        self.selected_folder = tk.StringVar()
        self.pattern = tk.StringVar()
        self.rename_plan = []

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
            text="Pattern Rename",
            font=("Arial", 18, "bold"),
            bg=WINDOW_BG_COLOR,
        ).pack(pady=(0, 5))
        tk.Label(
            main_frame,
            text="Renommez les fichiers d'un dossier avec un indice séquentiel.",
            font=("Arial", 10),
            bg=WINDOW_BG_COLOR,
            fg=DESC_TEXT_COLOR,
        ).pack(pady=(0, 15))

        folder_frame = tk.Frame(main_frame, bg=WINDOW_BG_COLOR)
        folder_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            folder_frame,
            text="Dossier :",
            width=16,
            anchor=tk.W,
            font=("Arial", 10, "bold"),
            bg=WINDOW_BG_COLOR,
        ).pack(side=tk.LEFT)
        tk.Entry(folder_frame, textvariable=self.selected_folder, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._create_button(folder_frame, "Parcourir", self._browse_folder).pack(side=tk.LEFT, padx=(8, 0))

        pattern_frame = tk.Frame(main_frame, bg=WINDOW_BG_COLOR)
        pattern_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            pattern_frame,
            text="Pattern :",
            width=16,
            anchor=tk.W,
            font=("Arial", 10, "bold"),
            bg=WINDOW_BG_COLOR,
        ).pack(side=tk.LEFT)
        tk.Entry(pattern_frame, textvariable=self.pattern, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(pattern_frame, text="Résultat : pattern-00001.ext", fg=DESC_TEXT_COLOR, bg=WINDOW_BG_COLOR).pack(side=tk.LEFT, padx=(8, 0))

        list_frame = tk.Frame(main_frame, bg=WINDOW_BG_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        tk.Label(
            list_frame,
            text="Prévisualisation du renommage :",
            font=("Arial", 10, "bold"),
            bg=WINDOW_BG_COLOR,
        ).pack(anchor=tk.W, pady=(0, 5))
        list_container = tk.Frame(list_frame, bg="white", relief=tk.SUNKEN, bd=1)
        list_container.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox = tk.Listbox(list_container, font=("Courier", 9), bg="white", yscrollcommand=scrollbar.set)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_listbox.yview)

        action_frame = tk.Frame(main_frame, bg=WINDOW_BG_COLOR)
        action_frame.pack(fill=tk.X, pady=10)
        self.preview_btn = self._create_button(action_frame, "Analyser", self._analyze_folder)
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.rename_btn = self._create_button(action_frame, "Renommer les fichiers", self._rename_files, state=tk.DISABLED)
        self.rename_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._create_button(action_frame, "Fermer", self.root.destroy).pack(side=tk.LEFT)

        self.status_label = tk.Label(
            main_frame,
            text="Prêt — sélectionnez un dossier et définissez un pattern.",
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

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Sélectionnez le dossier à traiter", mustexist=True)
        if folder:
            self.selected_folder.set(folder)
            self._clear_plan()
            self.status_label.config(text=f"Dossier sélectionné : {folder}")

    def _clear_plan(self):
        self.rename_plan = []
        self.files_listbox.delete(0, tk.END)
        self.rename_btn.config(state=tk.DISABLED)

    def _build_plan(self):
        folder = self.selected_folder.get()
        pattern = self.pattern.get().strip()
        if not os.path.isdir(folder):
            raise ValueError("Veuillez sélectionner un dossier valide.")
        if not pattern:
            raise ValueError("Veuillez définir un pattern.")
        if any(separator in pattern for separator in (os.sep, os.altsep) if separator):
            raise ValueError("Le pattern ne doit pas contenir de séparateur de chemin.")

        files = sorted(
            (
                path
                for path in Path(folder).iterdir()
                if path.is_file() and not self._is_system_file(path.name)
            ),
            key=lambda path: path.name.lower(),
        )
        plan = []
        for index, source in enumerate(files, 1):
            target = source.with_name(f"{pattern}-{index:05d}{source.suffix}")
            plan.append((source, target))
        return plan

    @classmethod
    def _is_system_file(cls, filename):
        return any(fnmatch.fnmatch(filename.lower(), pattern.lower()) for pattern in cls.SYSTEM_FILE_PATTERNS)

    def _analyze_folder(self):
        try:
            plan = self._build_plan()
        except ValueError as error:
            self._clear_plan()
            messagebox.showerror("Erreur", str(error))
            return

        target_paths = [target for _source, target in plan]
        if len(target_paths) != len(set(target_paths)):
            self._clear_plan()
            messagebox.showerror("Erreur", "Le pattern génère des noms de fichiers en doublon.")
            return

        self.rename_plan = plan
        self.files_listbox.delete(0, tk.END)
        for source, target in plan:
            self.files_listbox.insert(tk.END, f"{source.name}  ->  {target.name}")

        self.rename_btn.config(state=tk.NORMAL if plan else tk.DISABLED)
        self.status_label.config(text=f"Analyse terminée — {len(plan)} fichier(s) prêt(s) à être renommé(s).")
        if not plan:
            self.status_label.config(text="Aucun fichier à renommer dans ce dossier.")

    def _rename_files(self):
        try:
            plan = self._build_plan()
        except ValueError as error:
            messagebox.showerror("Erreur", str(error))
            return
        if not plan:
            messagebox.showinfo("Information", "Aucun fichier à renommer dans ce dossier.")
            return

        source_paths = {source.resolve() for source, _target in plan}
        target_paths = [target.resolve() for _source, target in plan]
        if len(target_paths) != len(set(target_paths)):
            messagebox.showerror("Erreur", "Le pattern génère des noms de fichiers en doublon.")
            return
        if any(target.exists() and target.resolve() not in source_paths for target in target_paths):
            messagebox.showerror("Erreur", "Au moins un nom cible existe déjà dans le dossier.")
            return
        if not messagebox.askyesno(
            "Confirmation de renommage",
            f"Voulez-vous renommer {len(plan)} fichier(s) selon le pattern « {self.pattern.get().strip()} » ?",
        ):
            return

        temporary_paths = []
        try:
            for index, (source, _target) in enumerate(plan):
                temporary = source.with_name(f".pattern-rename-{os.getpid()}-{index:05d}")
                source.rename(temporary)
                temporary_paths.append(temporary)
            for temporary, (_source, target) in zip(temporary_paths, plan):
                temporary.rename(target)
        except OSError as error:
            for temporary, (source, _target) in zip(temporary_paths, plan):
                if temporary.exists() and not source.exists():
                    temporary.rename(source)
            messagebox.showerror("Erreur", f"Le renommage a échoué :\n{error}")
            return

        self._clear_plan()
        self.status_label.config(text=f"Renommage terminé — {len(plan)} fichier(s) renommé(s).")
        messagebox.showinfo("Renommage terminé", f"{len(plan)} fichier(s) renommé(s) avec succès.")