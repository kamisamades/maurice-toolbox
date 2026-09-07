#!/usr/bin/env python3
"""Module de compression d'un dossier en archive ZIP."""

import os
import tkinter as tk
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from config import *


class ZipDir:
    """Compresse un dossier avec des filtres d'extensions optionnels."""

    VERSION = "1.0.0"
    AUTHOR = "Maurice"
    RELEASE_DATE = "07/09/2026"

    def __init__(self, root):
        self.root = root
        self.root.title(f"Compresser un dossier ({self.VERSION} - {self.RELEASE_DATE})")
        self.root.geometry("700x650")
        self.root.minsize(600, 550)
        self.root.configure(bg=WINDOW_BG_COLOR)

        self.selected_folder = tk.StringVar()
        self.selected_zipfile = tk.StringVar()
        self.include_extensions = tk.StringVar()
        self.exclude_extensions = tk.StringVar()
        self.split_archive = tk.BooleanVar(value=False)
        self.split_size_mb = tk.StringVar(value="100")
        self.files_to_zip = []

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
            text="Compresser un dossier",
            font=("Arial", 18, "bold"),
            bg=WINDOW_BG_COLOR,
        ).pack(pady=(0, 5))
        tk.Label(
            main_frame,
            text="Créez une archive ZIP en filtrant les extensions de fichiers.",
            font=("Arial", 10),
            bg=WINDOW_BG_COLOR,
            fg=DESC_TEXT_COLOR,
        ).pack(pady=(0, 15))

        self._create_path_row(main_frame, "Dossier source :", self.selected_folder, self._browse_folder)
        self._create_path_row(main_frame, "Fichier ZIP :", self.selected_zipfile, self._browse_zipfile)

        filters_frame = tk.LabelFrame(
            main_frame,
            text="Filtres d'extensions",
            bg=WINDOW_BG_COLOR,
            padx=10,
            pady=5,
        )
        filters_frame.pack(fill=tk.X, pady=10)
        self._create_entry_row(
            filters_frame,
            "Inclure :",
            self.include_extensions,
            "Ex. .py, .txt (vide = tous les fichiers)",
        )
        self._create_entry_row(
            filters_frame,
            "Exclure :",
            self.exclude_extensions,
            "Ex. .tmp, .log (prioritaire sur Inclure)",
        )

        split_frame = tk.Frame(main_frame, bg=WINDOW_BG_COLOR)
        split_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Checkbutton(
            split_frame,
            text="Scinder l'archive après création",
            variable=self.split_archive,
            command=self._toggle_split_size,
            bg=WINDOW_BG_COLOR,
            activebackground=WINDOW_BG_COLOR,
        ).pack(side=tk.LEFT)
        tk.Label(split_frame, text="Taille d'une partie (Mo) :", bg=WINDOW_BG_COLOR).pack(side=tk.LEFT, padx=(15, 5))
        self.split_size_entry = tk.Entry(split_frame, textvariable=self.split_size_mb, width=8)
        self.split_size_entry.pack(side=tk.LEFT)
        self.split_size_entry.config(state=tk.DISABLED)

        list_frame = tk.Frame(main_frame, bg=WINDOW_BG_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        tk.Label(
            list_frame,
            text="Fichiers inclus après analyse :",
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
        action_frame.pack(fill=tk.X, pady=15)
        self._create_button(action_frame, "Analyser", self._analyze_folder).pack(side=tk.LEFT, padx=(0, 8))
        self.create_btn = self._create_button(action_frame, "Créer le ZIP", self._create_zip, state=tk.DISABLED)
        self.create_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._create_button(action_frame, "Fermer", self.root.destroy).pack(side=tk.LEFT)

        self.status_label = tk.Label(
            main_frame,
            text="Prêt — sélectionnez un dossier puis cliquez sur Analyser.",
            font=("Arial", 9),
            bg=WINDOW_BG_COLOR,
            fg=DESC_TEXT_COLOR,
            anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, pady=(5, 0))

    def _create_path_row(self, parent, label, variable, command):
        frame = tk.Frame(parent, bg=WINDOW_BG_COLOR)
        frame.pack(fill=tk.X, pady=5)
        tk.Label(frame, text=label, width=16, anchor=tk.W, font=("Arial", 10, "bold"), bg=WINDOW_BG_COLOR).pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=variable, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._create_button(frame, "Parcourir", command).pack(side=tk.LEFT, padx=(8, 0))

    def _create_entry_row(self, parent, label, variable, help_text):
        frame = tk.Frame(parent, bg=WINDOW_BG_COLOR)
        frame.pack(fill=tk.X, pady=3)
        tk.Label(frame, text=label, width=12, anchor=tk.W, bg=WINDOW_BG_COLOR).pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=variable).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(frame, text=help_text, fg=DESC_TEXT_COLOR, bg=WINDOW_BG_COLOR).pack(side=tk.LEFT, padx=(8, 0))

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
        folder = filedialog.askdirectory(title="Sélectionnez le dossier à compresser", mustexist=True)
        if folder:
            self.selected_folder.set(folder)
            if not self.selected_zipfile.get():
                self.selected_zipfile.set(os.path.join(folder+"/..", f"{os.path.basename(folder)}-archive.zip"))
            self.status_label.config(text=f"Dossier sélectionné : {folder}")

    def _browse_zipfile(self):
        zip_path = filedialog.asksaveasfilename(
            title="Sélectionnez le fichier ZIP de sortie",
            defaultextension=".zip",
            filetypes=(("Archive ZIP", "*.zip"), ("Tous les fichiers", "*.*")),
        )
        if zip_path:
            self.selected_zipfile.set(zip_path)

    def _toggle_split_size(self):
        self.split_size_entry.config(state=tk.NORMAL if self.split_archive.get() else tk.DISABLED)

    @staticmethod
    def _parse_extensions(value):
        extensions = set()
        for item in value.split(","):
            extension = item.strip().lower()
            if extension:
                extensions.add(extension if extension.startswith(".") else f".{extension}")
        return extensions

    def _is_included(self, filename):
        include = self._parse_extensions(self.include_extensions.get())
        exclude = self._parse_extensions(self.exclude_extensions.get())
        suffix = Path(filename).suffix.lower()
        return (not include or suffix in include) and suffix not in exclude

    def _collect_files(self, folder):
        files = []
        for root_dir, _dirs, names in os.walk(folder):
            for name in names:
                path = os.path.join(root_dir, name)
                if os.path.isfile(path) and self._is_included(name):
                    files.append(path)
        return sorted(files)

    def _analyze_folder(self):
        folder = self.selected_folder.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier valide.")
            return

        self.files_listbox.delete(0, tk.END)
        self.files_to_zip = self._collect_files(folder)
        total_size = 0
        for path in self.files_to_zip:
            try:
                total_size += os.path.getsize(path)
                self.files_listbox.insert(tk.END, os.path.relpath(path, folder))
            except OSError:
                continue

        size_mb = total_size / (1024 * 1024)
        self.status_label.config(text=f"Analyse terminée — {len(self.files_to_zip)} fichier(s), {size_mb:.2f} Mo.")
        self.create_btn.config(state=tk.NORMAL)

    def _create_zip(self):
        folder = self.selected_folder.get()
        zip_path = self.selected_zipfile.get()
        if not self.files_to_zip:
            self._analyze_folder()
        if not self.files_to_zip:
            messagebox.showwarning("Avertissement", "Aucun fichier ne correspond aux filtres sélectionnés.")
            return
        if not zip_path:
            self._browse_zipfile()
            zip_path = self.selected_zipfile.get()
        if not zip_path:
            return

        try:
            Path(zip_path).parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
                for path in self.files_to_zip:
                    archive.write(path, os.path.relpath(path, folder))
            parts = self._split_archive(zip_path) if self.split_archive.get() else []
        except (OSError, ValueError, zipfile.BadZipFile) as error:
            messagebox.showerror("Erreur", f"La création de l'archive a échoué :\n{error}")
            return

        if parts:
            messagebox.showinfo(
                "Compression terminée",
                f"Archive créée : {zip_path}\n{len(parts)} partie(s) générée(s).\n\nRéassemblez-les dans l'ordre avant d'ouvrir le ZIP.",
            )
        else:
            messagebox.showinfo("Compression terminée", f"Archive créée :\n{zip_path}")
        self.status_label.config(text=f"Archive créée — {len(self.files_to_zip)} fichier(s).")

    def _split_archive(self, zip_path):
        try:
            size_mb = float(self.split_size_mb.get().replace(",", "."))
            if size_mb <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("La taille des parties doit être un nombre supérieur à zéro.")

        part_size = int(size_mb * 1024 * 1024)
        parts = []
        with open(zip_path, "rb") as source:
            index = 1
            while True:
                data = source.read(part_size)
                if not data:
                    break
                part_path = f"{zip_path}.part{index:03d}"
                with open(part_path, "wb") as part:
                    part.write(data)
                parts.append(part_path)
                index += 1
        os.remove(zip_path)
        return parts