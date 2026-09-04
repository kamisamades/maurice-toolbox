#!/usr/bin/env python3
"""
Maurice Toolbox - Boite à outils Python avec interface Tkinter
Auteur: Maurice
Web: lebrun.dev
"""

import tkinter as tk
from tkinter import messagebox, filedialog, Menu
from modules.clean_useless_files import CleanUselessFiles


class MauriceToolbox:
    """Classe principale de l'application Maurice Toolbox"""
    
    VERSION = "1.0.0"
    AUTHOR = "Maurice"
    WEBSITE = "lebrun.dev"
    
    def __init__(self, root):
        """Initialisation de l'interface principale"""
        self.root = root
        self.root.title("Maurice Toolbox")
        self.root.geometry("600x400")
        self.root.minsize(400, 300)
        
        # Configuration du style
        self.root.configure(bg="#f0f0f0")
        
        # Création du menu
        self._create_menu()
        
        # Création de la zone d'outils
        self._create_tools_area()
        
    def _create_menu(self):
        """Cré¬¬ation du menu principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Quitter", command=self._quit_app)
        
        # Menu Outils (vide pour l'instant)
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        
        # Menu Aide
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À· propos", command=self._show_about)
        
    def _create_tools_area(self):
        """Cré¬¬ation de la zone contenant les icô¬¥·nes des outils"""
        # Frame principale pour les outils
        tools_frame = tk.Frame(self.root, bg="#f0f0f0")
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        title_label = tk.Label(
            tools_frame,
            text="Outils disponibles",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=(0, 20))
        
        # Frame pour les icô¬¥·nes (grille)
        icons_frame = tk.Frame(tools_frame, bg="#f0f0f0")
        icons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Premier outil: Clean Useless Files
        self._create_tool_icon(
            icons_frame,
            "Clean Useless Files",
            "Supprime les fichiers inutiles",
            "🗑️",
            self._launch_clean_useless_files,
            0, 0
        )
        
    def _create_tool_icon(self, parent, title, description, emoji, command, row, col):
        """Cré¬¬ation d'une icô¬¥·ne d'outil carré¬©e"""
        # Frame pour l'icô¬¥·ne
        icon_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=2)
        icon_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configuration de l'expansion
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        # Frame interne pour centrer le contenu
        inner_frame = tk.Frame(icon_frame, bg="white")
        inner_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)
        
        # Emoji/icô¬¥·ne
        emoji_label = tk.Label(
            inner_frame,
            text=emoji,
            font=("Arial", 32),
            bg="white"
        )
        emoji_label.pack(pady=(10, 5))
        
        # Titre de l'outil
        title_label = tk.Label(
            inner_frame,
            text=title,
            font=("Arial", 11, "bold"),
            bg="white"
        )
        title_label.pack(pady=2)
        
        # Description
        desc_label = tk.Label(
            inner_frame,
            text=description,
            font=("Arial", 9),
            bg="white",
            fg="#666"
        )
        desc_label.pack(pady=2)
        
        # Bouton pour lancer l'outil
        launch_btn = tk.Button(
            inner_frame,
            text="Lancer",
            command=command,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            relief=tk.RAISED,
            cursor="hand2"
        )
        launch_btn.pack(pady=(10, 0))
        
    def _launch_clean_useless_files(self):
        """Lance l'outil Clean Useless Files dans une fenêtre séparé¬©e"""
        tool_window = tk.Toplevel(self.root)
        CleanUselessFiles(tool_window)
        
    def _show_about(self):
        """Affiche la boî¬¥te de dialogue À propos"""
        about_text = (
            f"Maurice Toolbox\n"
            f"Version: {self.VERSION}\n\n"
            f"Auteur: {self.AUTHOR}\n"
            f"Web: {self.WEBSITE}\n\n"
            f"Boite à outils Python avec interface Tkinter"
        )
        messagebox.showinfo("À· propos", about_text)
        
    def _quit_app(self):
        """Quitte l'application"""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter Maurice Toolbox ?"):
            self.root.quit()
            self.root.destroy()


def main():
    """Fonction principale"""
    root = tk.Tk()
    app = MauriceToolbox(root)
    root.mainloop()


if __name__ == "__main__":
    main()
