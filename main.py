#!/usr/bin/env python3
"""
Maurice Toolbox - Boite à outils Python avec interface Tkinter
Auteur: Maurice
Web: lebrun.dev
"""

import tkinter as tk
from tkinter import messagebox, Menu
from modules.clean_useless_files import CleanUselessFiles
from modules.image_resize import ImageResize
from modules.pattern_rename import PatternRename
from modules.zip_assemble import ZipAssemble
from modules.zip_dir import ZipDir
from pathlib import Path
from PIL import Image, ImageTk
from config import *

class MauriceToolbox:
    """Classe principale de l'application Maurice Toolbox."""

    VERSION = "1.4.0"
    AUTHOR = "Maurice"
    WEBSITE = "lebrun.dev"
    RELEASE_DATE = "07/09/2026"

    def __init__(self, root):
        self.root = root
        self.root.title("Maurice Toolbox - Boite à outils ("+self.VERSION+" - "+self.RELEASE_DATE+")")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)
        self.root.configure(bg=WINDOW_BG_COLOR)

        self._create_menu()
        self._create_tools_area()
        self._create_status_bar()
        self.root.after(100, self._center_window)

        icon_path = Path(__file__).parent / "assets" / "maurice-toolbox-logo-v2-sm.png"
        if icon_path.exists():
            icon_image = Image.open(icon_path)
            self.app_icon = ImageTk.PhotoImage(icon_image)
            self.root.iconphoto(False, self.app_icon)


    def _center_window(self):
        """Centre la fenêtre sur l'é±·cran."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Quitter", command=self._quit_app)

        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Nettoyer les fichiers inutiles", command=self._launch_clean_useless_files)
        tools_menu.add_command(label="Redimensionner des images", command=self._launch_image_resize)
        tools_menu.add_command(label="Renommer par pattern", command=self._launch_pattern_rename)
        tools_menu.add_command(label="Compresser un dossier", command=self._launch_zip_dir)
        tools_menu.add_command(label="Assembler un ZIP", command=self._launch_zip_assemble)

        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À· propos", command=self._show_about)

    def _create_tools_area(self):
        tools_frame = tk.Frame(self.root, bg=WINDOW_BG_COLOR)
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            tools_frame,
            text="Maurice Toolbox - Boite à outils",
            font=("Arial", 16, "bold"),
            bg=WINDOW_BG_COLOR,
        ).pack(pady=(0, 20))

        icons_frame = tk.Frame(tools_frame, bg=WINDOW_BG_COLOR)
        icons_frame.pack(fill=tk.BOTH, expand=True)

        self._create_tool_icon(
            icons_frame,
            "Clean Useless Files",
            "Supprime les fichiers inutiles",
            "🗑️",
            self._launch_clean_useless_files,
            0,
            0,
        )
        self._create_tool_icon(
            icons_frame,
            "Image Resize",
            "Redimensionne des images en masse",
            "🖼️",
            self._launch_image_resize,
            0,
            1,
        )
        self._create_tool_icon(
            icons_frame,
            "Pattern Rename",
            "Renomme les fichiers séquentiellement",
            "✏️",
            self._launch_pattern_rename,
            0,
            2,
        )
        self._create_tool_icon(
            icons_frame,
            "Zip Directory",
            "Crée une archive ZIP d'un dossier",
            "📦",
            self._launch_zip_dir,
            1,
            0,
        )
        self._create_tool_icon(
            icons_frame,
            "Zip Assemble",
            "Réassemble les parties d'un ZIP",
            "🧩",
            self._launch_zip_assemble,
            1,
            1,
        )

    def _create_status_bar(self):
        status_frame = tk.Frame(self.root, bg=WINDOW_BG_COLOR, relief=tk.SUNKEN, bd=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        text = (
            f"Maurice Toolbox — {self.AUTHOR} — "
            f"Version : {self.VERSION} — Release : {self.RELEASE_DATE}"
        )
        tk.Label(
            status_frame,
            text=text,
            font=("Arial", 9),
            bg=WINDOW_BG_COLOR,
            fg=STATUS_TEXT_COLOR,
            anchor=tk.W,
            padx=10,
            pady=3,
        ).pack(fill=tk.X,side=tk.RIGHT)

    def _launch_clean_useless_files(self):
        tool_window = tk.Toplevel(self.root)
        CleanUselessFiles(tool_window)

    def _launch_image_resize(self):
        tool_window = tk.Toplevel(self.root)
        ImageResize(tool_window)

    def _launch_pattern_rename(self):
        tool_window = tk.Toplevel(self.root)
        PatternRename(tool_window)

    def _launch_zip_dir(self):
        tool_window = tk.Toplevel(self.root)
        ZipDir(tool_window)

    def _launch_zip_assemble(self):
        tool_window = tk.Toplevel(self.root)
        ZipAssemble(tool_window)

    def _show_about(self):
        about_text = (
            f"Maurice Toolbox\n"
            f"Version : {self.VERSION}\n"
            f"Release : {self.RELEASE_DATE}\n\n"
            f"Auteur : {self.AUTHOR}\n"
            f"Web : {self.WEBSITE}\n\n"
            f"Boite à outils"
        )
        messagebox.showinfo("À propos", about_text)

    def _quit_app(self):
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter Maurice Toolbox ?"):
            self.root.destroy()

    def _create_tool_icon(self, parent, title, description, emoji, command, row, col):
        """Création d'une icône d'outil carrée cliquable."""
        # Frame pour l'icône
        icon_frame = tk.Frame(parent, bg=CARD_BG_COLOR, relief=tk.RAISED, bd=2)
        icon_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Configuration de l'expansion
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)

        # Frame interne pour centrer le contenu
        inner_frame = tk.Frame(icon_frame, bg=CARD_BG_COLOR)
        inner_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)

        # Emoji/icône
        emoji_label = tk.Label(
            inner_frame,
            text=emoji,
            font=("Arial", 32),
            bg=BT_BG_COLOR,
            fg=BT_TEXT_COLOR,
            cursor="hand2"
        )
        emoji_label.pack(pady=(10, 5))

        # Titre de l'outil
        title_label = tk.Label(
            inner_frame,
            text=title,
            font=("Arial", 11, "bold"),
            bg=BT_BG_COLOR,
            fg=BT_TEXT_COLOR,
            cursor="hand2"
        )
        title_label.pack(pady=2)

        # Description
        desc_label = tk.Label(
            inner_frame,
            text=description,
            font=("Arial", 9),
            bg=BT_BG_COLOR,
            fg=DESC_TEXT_COLOR,
            cursor="hand2"
        )
        desc_label.pack(pady=2)

        # Bouton pour lancer l'outil
        launch_btn = tk.Button(
            inner_frame,
            text="Lancer",
            command=command,
            bg=BT_BG_COLOR,
            fg=BT_TEXT_COLOR,
            font=("Arial", 9, "bold"),
            relief=tk.RAISED,
            cursor="hand2"
        )
        #launch_btn.pack(pady=(10, 0))

        # Rendre toute la zone cliquable
        for widget in (icon_frame, inner_frame, emoji_label, title_label, desc_label, launch_btn):
            widget.bind("<Button-1>", lambda event: command())
            widget.config(cursor="hand2")


def main():
    root = tk.Tk()
    MauriceToolbox(root)
    root.mainloop()


if __name__ == "__main__":
    main()
