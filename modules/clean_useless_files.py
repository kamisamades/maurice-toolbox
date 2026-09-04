#!/usr/bin/env python3
"""Module Clean Useless Files."""

import fnmatch
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class CleanUselessFiles:
    """Outil de nettoyage des fichiers temporaires et inutiles."""

    VERSION = "1.0.0"
    AUTHOR = "Maurice"
    RELEASE_DATE = "04/09/2026"

    USELESS_FILE_PATTERNS = (
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
    USELESS_DIRECTORIES = {
        "__MACOSX",
        ".Trashes",
        ".Spotlight-V100",
        ".fseventsd",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Clean Useless Files ("+self.VERSION+" - "+self.RELEASE_DATE+")")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        self.root.configure(bg="#f0f0f0")

        self.selected_folder = tk.StringVar()
        self.paths_to_delete = []
        self._create_widgets()
        self.root.after(100, self._center_window)

    def _center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="Clean Useless Files", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=(0, 10))
        tk.Label(
            main_frame,
            text="Sélectionnez un dossier pour supprimer les fichiers temporaires et inutiles.",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666",
            wraplength=500,
        ).pack(pady=(0, 20))

        folder_frame = tk.Frame(main_frame, bg="#f0f0f0")
        folder_frame.pack(fill=tk.X, pady=10)
        tk.Label(folder_frame, text="Dossier :", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(side=tk.LEFT, padx=(0, 10))
        tk.Entry(folder_frame, textvariable=self.selected_folder, font=("Arial", 10), width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(
            folder_frame,
            text="Parcourir",
            command=self._browse_folder,
            bg="#2196F3",
            fg="black",
            font=("Arial", 9, "bold"),
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=(10, 0))

        list_frame = tk.Frame(main_frame, bg="#f0f0f0")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        tk.Label(list_frame, text="Fichiers détectés (prévisualisation) :", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor=tk.W, pady=(0, 5))

        list_container = tk.Frame(list_frame, bg="white", relief=tk.SUNKEN, bd=1)
        list_container.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox = tk.Listbox(list_container, font=("Courier", 9), bg="white", yscrollcommand=scrollbar.set)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_listbox.yview)

        action_frame = tk.Frame(main_frame, bg="#f0f0f0")
        action_frame.pack(fill=tk.X, pady=20)
        tk.Button(
            action_frame,
            text="🔍 Analyser le dossier",
            command=self._analyze_folder,
            bg="#4CAF50",
            fg="black",
            font=("Arial", 10, "bold"),
            width=18,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=(0, 10))
        self.delete_btn = tk.Button(
            action_frame,
            text="🗑️ Supprimer les fichiers",
            command=self._delete_files,
            bg="#f44336",
            fg="black",
            font=("Arial", 10, "bold"),
            width=22,
            cursor="hand2",
            state=tk.DISABLED,
        )
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(
            action_frame,
            text="❌ Fermer",
            command=self.root.destroy,
            bg="#9e9e9e",
            fg="black",
            font=("Arial", 10, "bold"),
            width=15,
            cursor="hand2",
        ).pack(side=tk.LEFT)

        self.status_label = tk.Label(
            main_frame,
            text="Prêt — sé­lectionnez un dossier puis cliquez sur Analyser le dossier.",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#666",
            anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Sélectionnez un dossier à nettoyer", mustexist=True)
        if folder:
            self.selected_folder.set(folder)
            self.status_label.config(text=f"Dossier sé­lectionné : {folder}")

    def _analyze_folder(self):
        folder = self.selected_folder.get()
        if not folder:
            messagebox.showwarning("Avertissement", "Veuillez d'abord sé­lectionner un dossier.")
            return
        if not os.path.isdir(folder):
            messagebox.showerror("Erreur", f"Le dossier « {folder} » n'existe pas.")
            return

        self.files_listbox.delete(0, tk.END)
        self.paths_to_delete = []
        self.status_label.config(text="Analyse en cours…")
        self.root.update_idletasks()

        errors = 0
        for root_dir, dirs, files in os.walk(folder, topdown=True, onerror=lambda _error: None):
            for name in list(dirs):
                if self._is_useless_directory(name):
                    path = os.path.join(root_dir, name)
                    self.paths_to_delete.append(path)
                    self.files_listbox.insert(tk.END, os.path.relpath(path, folder) + os.sep)
                    dirs.remove(name)
            for name in files:
                if self._is_useless_file(name):
                    path = os.path.join(root_dir, name)
                    self.paths_to_delete.append(path)
                    self.files_listbox.insert(tk.END, os.path.relpath(path, folder))

        count = len(self.paths_to_delete)
        if count:
            self.status_label.config(text=f"{count} é­lément(s) inutile(s) détecté(s).")
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Aucun fichier ou dossier inutile détecté.")
            self.delete_btn.config(state=tk.DISABLED)

    def _is_useless_file(self, filename):
        return any(fnmatch.fnmatch(filename.lower(), pattern.lower()) for pattern in self.USELESS_FILE_PATTERNS)

    def _is_useless_directory(self, dirname):
        return dirname.lower() in {name.lower() for name in self.USELESS_DIRECTORIES}

    def _delete_files(self):
        if not self.paths_to_delete:
            messagebox.showinfo("Information", "Aucun é­lément à supprimer.")
            return

        count = len(self.paths_to_delete)
        if not messagebox.askyesno(
            "Confirmation de suppression",
            f"Voulez-vous vraiment supprimer {count} é­lément(s) ?\n\nCette action est irré­versible.",
            icon=messagebox.WARNING,
        ):
            return

        deleted = 0
        skipped = 0
        for path in sorted(self.paths_to_delete, key=len, reverse=True):
            try:
                if os.path.isdir(path) and not os.path.islink(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                deleted += 1
            except OSError:
                skipped += 1

        messagebox.showinfo("Nettoyage terminé", f"Éléments supprimés : {deleted}\nÉléments ignorés : {skipped}")
        self.status_label.config(text=f"Nettoyage terminé — {deleted} é­lément(s) supprimé(s), {skipped} ignoré(s).")
        self.files_listbox.delete(0, tk.END)
        self.paths_to_delete = []
        self.delete_btn.config(state=tk.DISABLED)
