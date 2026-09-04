#!/usr/bin/env python3
"""
Module: Clean Useless Files
Permet de supprimer les fichiers inutiles (._* , .DS_Store, thumbs.db, etc.)
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path


class CleanUselessFiles:
    """Classe pour l'outil de nettoyage des fichiers inutiles"""

    VERSION = "1.0.0"
    RELEASE_DATE = "2026-09-04"
    
    # Liste des motifs de fichiers à supprimer
    USELESS_PATTERNS = [
        "._*",
        ".DS_Store",
        "Thumbs.db",
        "thumbs.db",
        "._*",
        "desktop.ini",
        "Desktop.ini",
        ".Trashes",
        ".Spotlight-V100",
        ".fseventsd",
        "__MACOSX",
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
    ]
    
    def __init__(self, root):
        """Initialisation de la fenêtre de l'outil"""
        self.root = root
        self.root.title("Clean Useless Files")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        
        # Variables
        self.selected_folder = tk.StringVar()
        self.files_to_delete = []
        self.deleted_count = 0
        self.skipped_count = 0
        
        # Configuration du style
        self.root.configure(bg="#f0f0f0")
        
        # Création de l'interface
        self._create_widgets()
        
    def _create_widgets(self):
        """Création des widgets de l'interface"""
        # Frame principale
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        title_label = tk.Label(
            main_frame,
            text="Nettoyage des fichiers inutiles ("+self.VERSION+" - "+self.RELEASE_DATE+")",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = tk.Label(
            main_frame,
            text="Sélectionnez un dossier pour supprimer les fichiers temporaires et inutile (Analyse récursive)",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666",
            wraplength=500
        )
        desc_label.pack(pady=(0, 20))
        
        # Frame de sé­lection du dossier
        folder_frame = tk.Frame(main_frame, bg="#f0f0f0")
        folder_frame.pack(fill=tk.X, pady=10)
        
        # Label du dossier
        folder_label = tk.Label(
            folder_frame,
            text="Dossier:",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0"
        )
        folder_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Entré¬©e du dossier
        folder_entry = tk.Entry(
            folder_frame,
            textvariable=self.selected_folder,
            font=("Arial", 10),
            fg="#000000",
            width=50
        )
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bouton de parcourir
        browse_btn = tk.Button(
            folder_frame,
            text="Parcourir",
            command=self._browse_folder,
            bg="#2196F3",
            fg="#000000",
            font=("Arial", 9, "bold"),
            relief=tk.RAISED,
            cursor="hand2"
        )
        browse_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame de liste des fichiers
        list_frame = tk.Frame(main_frame, bg="#f0f0f0")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Titre de la liste
        list_title = tk.Label(
            list_frame,
            text="Fichiers détectés (prévisualisation):",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0"
        )
        list_title.pack(anchor=tk.W, pady=(0, 5))
        
        # Liste avec scrollbar
        list_container = tk.Frame(list_frame, bg="white", relief=tk.SUNKEN, bd=1)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.files_listbox = tk.Listbox(
            list_container,
            font=("Courier", 9),
            bg="white",
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar.set
        )
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_listbox.yview)
        
        # Frame des boutons d'action
        action_frame = tk.Frame(main_frame, bg="#f0f0f0")
        action_frame.pack(fill=tk.X, pady=20)
        
        # Bouton analyser
        analyze_btn = tk.Button(
            action_frame,
            text="Analyser le dossier",
            command=self._analyze_folder,
            bg="#4CAF50",
            fg="#000000",
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            cursor="hand2",
            width=15
        )
        analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton supprimer
        delete_btn = tk.Button(
            action_frame,
            text="Supprimer les fichiers",
            command=self._delete_files,
            bg="#f44336",
            fg="#000000",
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            cursor="hand2",
            width=20,
            state=tk.DISABLED
        )
        self.delete_btn = delete_btn
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton fermer
        close_btn = tk.Button(
            action_frame,
            text="Fermer",
            command=self._close_window,
            bg="#9e9e9e",
            fg="#000000",
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            cursor="hand2",
            width=15
        )
        close_btn.pack(side=tk.LEFT)
        
        # Frame de statut
        status_frame = tk.Frame(main_frame, bg="#f0f0f0")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Label de statut
        self.status_label = tk.Label(
            status_frame,
            text="Prêt - Sé­lectionnez un dossier et cliquez sur Analyser",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#666",
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X)
        
    def _browse_folder(self):
        """Ouvre une boîte de dialogue pour sé­lectionner un dossier"""
        folder = filedialog.askdirectory(
            title="Sélectionnez un dossier à nettoyer",
            mustexist=True
        )
        if folder:
            self.selected_folder.set(folder)
            self.status_label.config(
                text=f"Dossier sé­lectionné: {folder}"
            )
            
    def _analyze_folder(self):
        """Analyse le dossier et trouve les fichiers inutiles"""
        folder = self.selected_folder.get()
        
        if not folder:
            messagebox.showwarning(
                "Avertissement",
                "Veuillez sé­lectionner un dossier d'abord."
            )
            return
        
        if not os.path.isdir(folder):
            messagebox.showerror(
                "Erreur",
                f"Le dossier '{folder}' n'existe pas."
            )
            return
        
        # Vider la liste
        self.files_listbox.delete(0, tk.END)
        self.files_to_delete = []
        
        # Mettre à jour le statut
        self.status_label.config(text="Analyse en cours...")
        self.root.update()
        
        # Parcourir le dossier
        try:
            for root_dir, dirs, files in os.walk(folder):
                # Vérifier les fichiers
                for file in files:
                    if self._is_useless_file(file):
                        full_path = os.path.join(root_dir, file)
                        self.files_to_delete.append(full_path)
                        relative_path = os.path.relpath(full_path, folder)
                        self.files_listbox.insert(tk.END, relative_path)
                
                # Vérifier les dossiers (pour __MACOSX, .Trashes, etc.)
                for dir_name in dirs[:]:  # Copie pour pouvoir modifier
                    if self._is_useless_directory(dir_name):
                        full_path = os.path.join(root_dir, dir_name)
                        self.files_to_delete.append(full_path + "/")
                        relative_path = os.path.relpath(full_path, folder)
                        self.files_listbox.insert(tk.END, relative_path + "/")
                        
        except PermissionError:
            messagebox.showerror(
                "Erreur",
                "Permission refusée. Impossible de lire certains dossiers."
            )
            self.status_label.config(text="Erreur lors de l'analyse")
            return
        
        # Mettre à jour le statut
        count = len(self.files_to_delete)
        if count > 0:
            self.status_label.config(
                text=f"{count} fichier(s) inutile(s) détecté(s)"
            )
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.status_label.config(
                text="Aucun fichier inutile détecté"
            )
            self.delete_btn.config(state=tk.DISABLED)
            
    def _is_useless_file(self, filename):
        """Vérifie si un fichier est dans la liste des fichiers inutiles"""
        filename_lower = filename.lower()
        
        # Vérification des motifs
        for pattern in self.USELESS_PATTERNS:
            pattern_lower = pattern.lower()
            
            # Motif avec wildcard
            if pattern_lower.startswith("*"):
                if filename_lower.endswith(pattern_lower[1:]):
                    return True
            # Motif exact
            elif pattern_lower == filename_lower:
                return True
            # Motif commenç¬§ant par .
            elif pattern_lower.startswith(".") and filename_lower.startswith("."):
                if pattern_lower[1:] == filename_lower[1:]:
                    return True
                # Vérifier les motifs de type ._*
                if "*" in pattern_lower:
                    pattern_base = pattern_lower.replace("*", "")
                    if filename_lower.startswith(pattern_base):
                        return True
        
        return False
    
    def _is_useless_directory(self, dirname):
        """Vérifie si un dossier est dans la liste des dossiers inutiles"""
        useless_dirs = ["__MACOSX", ".Trashes", ".Spotlight-V100", ".fseventsd"]
        return dirname in useless_dirs
    
    def _delete_files(self):
        """Supprime les fichiers détectés avec confirmation"""
        if not self.files_to_delete:
            messagebox.showinfo(
                "Information",
                "Aucun fichier à supprimer."
            )
            return
        
        # Confirmation
        confirm_msg = (
            f"Voulez-vous vraiment supprimer {len(self.files_to_delete)} fichier(s) ?\n\n"
            f"Cette action est irré­versible."
        )
        
        if not messagebox.askyesno(
            "Confirmation de suppression",
            confirm_msg,
            icon=messagebox.WARNING
        ):
            return
        
        # Suppression des fichiers
        self.deleted_count = 0
        self.skipped_count = 0
        
        for file_path in self.files_to_delete:
            try:
                if file_path.endswith("/"):
                    # C'est un dossier
                    os.rmdir(file_path[:-1])
                else:
                    # C'est un fichier
                    os.remove(file_path)
                self.deleted_count += 1
            except PermissionError:
                self.skipped_count += 1
            except OSError as e:
                self.skipped_count += 1
                print(f"Erreur lors de la suppression de {file_path}: {e}")
        
        # Résultat
        result_msg = (
            f"Nettoyage terminé !\n\n"
            f"Fichiers supprimés: {self.deleted_count}\n"
            f"Fichiers ignorés: {self.skipped_count}"
        )
        
        messagebox.showinfo("Nettoyage terminé", result_msg)
        self.status_label.config(
            text=f"Nettoyage terminé - {self.deleted_count} fichier(s) supprimé(s)"
        )
        
        # Vider la liste
        self.files_listbox.delete(0, tk.END)
        self.files_to_delete = []
        self.delete_btn.config(state=tk.DISABLED)
        
    def _close_window(self):
        """Ferme la fenêtre de l'outil"""
        self.root.destroy()
