#!/usr/bin/env python3
"""Module de redimensionnement et conversion d'images en masse."""

import fnmatch
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageOps

from config import *


class ImageResize:
    """Redimensionne et convertit des images d'un dossier en masse."""

    VERSION = "1.0.0"
    AUTHOR = "Maurice"
    RELEASE_DATE = "07/09/2026"
    FILTER_PATTERNS = {
        "JPG": "*.jp*g",
        "PNG": "*.png",
        "GIF": "*.gif",
        "WEBP": "*.webp",
    }
    OUTPUT_EXTENSIONS = {
        "JPG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
    }

    def __init__(self, root):
        self.root = root
        self.root.title(f"Image Resize ({self.VERSION} - {self.RELEASE_DATE})")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        self.root.configure(bg=WINDOW_BG_COLOR)

        self.selected_input_dir = tk.StringVar()
        self.selected_output_dir = tk.StringVar()
        self.max_width = tk.StringVar()
        self.max_height = tk.StringVar()
        self.keep_proportions = tk.BooleanVar(value=True)
        self.output_format = tk.StringVar(value="Format d'origine")
        self.filter_vars = {name: tk.BooleanVar(value=True) for name in self.FILTER_PATTERNS}
        self.files_to_process = []

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
            text="Image Resize",
            font=("Arial", 18, "bold"),
            bg=WINDOW_BG_COLOR,
        ).pack(pady=(0, 5))
        tk.Label(
            main_frame,
            text="Redimensionnez et convertissez vos images en masse.",
            font=("Arial", 10),
            bg=WINDOW_BG_COLOR,
            fg=DESC_TEXT_COLOR,
        ).pack(pady=(0, 15))

        self._create_path_row(main_frame, "Dossier d'entrée :", self.selected_input_dir, self._browse_input_dir)
        self._create_path_row(main_frame, "Dossier de sortie :", self.selected_output_dir, self._browse_output_dir)

        filters_frame = tk.LabelFrame(
            main_frame,
            text="Types d'images à traiter",
            bg=WINDOW_BG_COLOR,
            padx=10,
            pady=5,
        )
        filters_frame.pack(fill=tk.X, pady=10)
        for name, variable in self.filter_vars.items():
            tk.Checkbutton(
                filters_frame,
                text=name,
                variable=variable,
                bg=WINDOW_BG_COLOR,
                activebackground=WINDOW_BG_COLOR,
            ).pack(side=tk.LEFT, padx=(0, 15))

        options_frame = tk.LabelFrame(
            main_frame,
            text="Options de redimensionnement",
            bg=WINDOW_BG_COLOR,
            padx=10,
            pady=5,
        )
        options_frame.pack(fill=tk.X, pady=5)
        dimensions_frame = tk.Frame(options_frame, bg=WINDOW_BG_COLOR)
        dimensions_frame.pack(fill=tk.X, pady=3)
        tk.Label(dimensions_frame, text="Largeur max (px) :", bg=WINDOW_BG_COLOR).pack(side=tk.LEFT)
        tk.Entry(dimensions_frame, textvariable=self.max_width, width=10).pack(side=tk.LEFT, padx=(5, 15))
        tk.Label(dimensions_frame, text="Hauteur max (px) :", bg=WINDOW_BG_COLOR).pack(side=tk.LEFT)
        tk.Entry(dimensions_frame, textvariable=self.max_height, width=10).pack(side=tk.LEFT, padx=(5, 15))
        tk.Checkbutton(
            dimensions_frame,
            text="Conserver les proportions",
            variable=self.keep_proportions,
            bg=WINDOW_BG_COLOR,
            activebackground=WINDOW_BG_COLOR,
        ).pack(side=tk.LEFT)

        format_frame = tk.Frame(options_frame, bg=WINDOW_BG_COLOR)
        format_frame.pack(fill=tk.X, pady=3)
        tk.Label(format_frame, text="Format de sortie :", bg=WINDOW_BG_COLOR).pack(side=tk.LEFT)
        for value in ("Format d'origine", "JPG", "PNG", "WEBP"):
            tk.Radiobutton(
                format_frame,
                text=value,
                value=value,
                variable=self.output_format,
                bg=WINDOW_BG_COLOR,
                activebackground=WINDOW_BG_COLOR,
            ).pack(side=tk.LEFT, padx=(10, 0))

        list_frame = tk.Frame(main_frame, bg=WINDOW_BG_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        tk.Label(
            list_frame,
            text="Images détectées :",
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
        self._create_button(action_frame, "Analyser", self._analyze).pack(side=tk.LEFT, padx=(0, 8))
        self.process_btn = self._create_button(action_frame, "Redimensionner", self._process_images, state=tk.DISABLED)
        self.process_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._create_button(action_frame, "Fermer", self.root.destroy).pack(side=tk.LEFT)

        self.status_label = tk.Label(
            main_frame,
            text="Prêt — sélectionnez les dossiers, les formats puis cliquez sur Analyser.",
            font=("Arial", 9),
            bg=WINDOW_BG_COLOR,
            fg=DESC_TEXT_COLOR,
            anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, pady=(5, 0))

    def _create_path_row(self, parent, label, variable, command):
        frame = tk.Frame(parent, bg=WINDOW_BG_COLOR)
        frame.pack(fill=tk.X, pady=5)
        tk.Label(frame, text=label, width=20, anchor=tk.W, font=("Arial", 10, "bold"), bg=WINDOW_BG_COLOR).pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=variable, font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._create_button(frame, "Parcourir", command).pack(side=tk.LEFT, padx=(8, 0))

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

    def _browse_input_dir(self):
        folder = filedialog.askdirectory(title="Sélectionnez le dossier d'entrée", mustexist=True)
        if folder:
            self.selected_input_dir.set(folder)
            self._clear_analysis()

    def _browse_output_dir(self):
        folder = filedialog.askdirectory(title="Sélectionnez le dossier de sortie", mustexist=True)
        if folder:
            self.selected_output_dir.set(folder)

    def _clear_analysis(self):
        self.files_to_process = []
        self.files_listbox.delete(0, tk.END)
        self.process_btn.config(state=tk.DISABLED)

    def _same_directory(self):
        input_dir = self.selected_input_dir.get()
        output_dir = self.selected_output_dir.get()
        return bool(input_dir and output_dir and Path(input_dir).expanduser().resolve() == Path(output_dir).expanduser().resolve())

    def _selected_patterns(self):
        return [self.FILTER_PATTERNS[name] for name, variable in self.filter_vars.items() if variable.get()]

    def _collect_files(self):
        input_dir = Path(self.selected_input_dir.get())
        patterns = self._selected_patterns()
        return sorted(
            (
                path for path in input_dir.iterdir()
                if path.is_file() and any(fnmatch.fnmatch(path.name.lower(), pattern) for pattern in patterns)
            ),
            key=lambda path: path.name.lower(),
        )

    def _parse_dimensions(self):
        dimensions = {}
        for label, variable in (("largeur", self.max_width), ("hauteur", self.max_height)):
            value = variable.get().strip()
            if not value:
                dimensions[label] = None
                continue
            try:
                number = int(value)
            except ValueError as error:
                raise ValueError(f"La {label} maximale doit être un nombre entier.") from error
            if number <= 0:
                raise ValueError(f"La {label} maximale doit être supérieure à zéro.")
            dimensions[label] = number
        if dimensions["largeur"] is None and dimensions["hauteur"] is None:
            raise ValueError("Saisissez au moins une dimension maximale.")
        if not self.keep_proportions.get() and (dimensions["largeur"] is None or dimensions["hauteur"] is None):
            raise ValueError("Pour déformer l'image, saisissez la largeur et la hauteur.")
        return dimensions["largeur"], dimensions["hauteur"]

    def _analyze(self):
        input_dir = self.selected_input_dir.get()
        output_dir = self.selected_output_dir.get()
        if not os.path.isdir(input_dir) or not os.path.isdir(output_dir):
            messagebox.showerror("Erreur", "Veuillez sélectionner deux dossiers valides.")
            return
        if self._same_directory():
            self._clear_analysis()
            messagebox.showerror("Dossiers identiques", "Les dossiers d'entrée et de sortie doivent être différents.")
            return
        if not self._selected_patterns():
            self._clear_analysis()
            messagebox.showerror("Erreur", "Sélectionnez au moins un filtre d'image.")
            return
        try:
            self._parse_dimensions()
        except ValueError as error:
            self._clear_analysis()
            messagebox.showerror("Erreur", str(error))
            return

        self.files_to_process = self._collect_files()
        self.files_listbox.delete(0, tk.END)
        for path in self.files_to_process:
            self.files_listbox.insert(tk.END, path.name)
        self.process_btn.config(state=tk.NORMAL if self.files_to_process else tk.DISABLED)
        self.status_label.config(text=f"Analyse terminée — {len(self.files_to_process)} image(s) détectée(s).")
        if not self.files_to_process:
            self.status_label.config(text="Aucune image ne correspond aux filtres sélectionnés.")

    @staticmethod
    def _resize_dimensions(image_size, max_width, max_height, keep_proportions):
        width, height = image_size
        if not keep_proportions:
            return max_width, max_height
        scale = min(
            (max_width / width) if max_width else float("inf"),
            (max_height / height) if max_height else float("inf"),
            1,
        )
        return max(1, round(width * scale)), max(1, round(height * scale))

    def _output_path(self, source):
        output_format = self.output_format.get()
        if output_format == "Format d'origine":
            return Path(self.selected_output_dir.get()) / source.name
        return Path(self.selected_output_dir.get()) / f"{source.stem}{self.OUTPUT_EXTENSIONS[output_format]}"

    @staticmethod
    def _save_image(image, output_path, output_format):
        if output_format == "JPG" or (output_format == "Format d'origine" and output_path.suffix.lower() in (".jpg", ".jpeg")):
            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, "white")
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.getchannel("A"))
                image = background
            else:
                image = image.convert("RGB")
            image.save(output_path, format="JPEG", quality=95)
        else:
            format_name = output_format if output_format != "Format d'origine" else output_path.suffix[1:].upper()
            image.save(output_path, format=format_name)

    def _process_images(self):
        if self._same_directory():
            messagebox.showerror("Dossiers identiques", "Les dossiers d'entrée et de sortie doivent être différents.")
            return
        try:
            max_width, max_height = self._parse_dimensions()
        except ValueError as error:
            messagebox.showerror("Erreur", str(error))
            return
        if not self.files_to_process:
            self._analyze()
        if not self.files_to_process:
            return

        output_dir = Path(self.selected_output_dir.get())
        output_dir.mkdir(parents=True, exist_ok=True)
        output_format = self.output_format.get()
        processed = 0
        errors = []
        for source in self.files_to_process:
            try:
                with Image.open(source) as opened_image:
                    image = ImageOps.exif_transpose(opened_image)
                    new_size = self._resize_dimensions(image.size, max_width, max_height, self.keep_proportions.get())
                    if new_size != image.size:
                        image = image.resize(new_size, Image.Resampling.LANCZOS)
                    self._save_image(image, self._output_path(source), output_format)
                    processed += 1
            except (OSError, ValueError, KeyError) as error:
                errors.append(f"{source.name} : {error}")

        if errors:
            messagebox.showwarning(
                "Traitement terminé avec erreurs",
                f"Images traitées : {processed}\nImages en erreur : {len(errors)}\n\n" + "\n".join(errors[:5]),
            )
        else:
            messagebox.showinfo("Traitement terminé", f"{processed} image(s) enregistrée(s) dans :\n{output_dir}")
        self.status_label.config(text=f"Traitement terminé — {processed} image(s) traitée(s), {len(errors)} erreur(s).")