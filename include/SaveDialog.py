from PIL import ImageTk
import include.utils as utils
import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk


APP_BG= "#f1f8ff"

TEXT_COLOR = "#003366"

ACCENT_COLOR = "#0066cc"
TEXT_COLOR = "#ffffff"
ROBOTO_BOLD = ("Roboto", 18, "bold")
ROBOTO_LABEL = ("Roboto", 16)

class SaveDialog(ctk.CTkToplevel):
    def __init__(self, master=None, title="Save Project", initial_dir=None):
        super().__init__(master)
        self.title(title)
        self.icon_path = ImageTk.PhotoImage(file=utils.imgPath('icon.ico'))
        self.wm_iconbitmap()
        self.after(250, lambda: self.iconphoto(False, self.icon_path))
        self.geometry("450x250")
        self.configure(fg_color=APP_BG)
        self.result = None
        self.name = None
        self.protocol("WM_DELETE_WINDOW", self.update)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.path_label = ctk.CTkLabel(self, text="Project Location:")
        self.path_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")

        self.path_entry = ctk.CTkEntry(self, width=300)
        if initial_dir:
            self.path_entry.insert(0, initial_dir)
        self.path_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.name_label = ctk.CTkLabel(self, text="Project Name:")
        self.name_label.grid(row=2, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")
        
        self.project_name_entry = ctk.CTkEntry(self, width=300)
        self.project_name_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.project_name_entry.insert(0, "Untitled_Project")
        
        self.browse_button = ctk.CTkButton(self, text="Browse...", command=self.browse_directory)
        self.browse_button.grid(row=1, column=1, padx=10, pady=5)

        self.button_frame = ctk.CTkFrame(self, fg_color=APP_BG)
        self.button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.save_button = ctk.CTkButton(self.button_frame, text="Save", command=self.save)
        self.save_button.pack(side="left", padx=10)

        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel", command=self.cancel, fg_color="gray")
        self.cancel_button.pack(side="left", padx=10)

        self.transient(master)
        self.grab_set()

    def browse_directory(self):
        dir_path = filedialog.askdirectory(parent=self, title="Select Project Location")
        if dir_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, dir_path)

    def save(self):
        path = os.path.join(self.path_entry.get(), self.project_name_entry.get())
        try:
            os.mkdir(path)
            utils.log_message('debug', f'saving-created a dir named {self.project_name_entry.get()} at {self.path_entry.get()}')
        except FileExistsError:
            utils.log_message('error', 'saving-dir already exists')
            utils.infoMsg('project name', f'project with the same name {self.project_name_entry.get()} already exist')
            return
            
        self.result = path
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()
