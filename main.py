import importlib.metadata
import sys

_original_version = importlib.metadata.version

def safe_version(name, default="1.0.0"):
    try:
        return _original_version(name)
    except importlib.metadata.PackageNotFoundError:
        return default

sys.modules["importlib.metadata"].version = safe_version

import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import os
import shutil
from include.tab1 import Tab1
from include.tab2 import Tab2
from include.tab3 import Tab3
from include.tab4 import Tab4
from include.ijClass import ImageJ
import include.utils as utils
import json
import tempfile
from PIL import ImageTk
import imagej.doctor
import io
from contextlib import redirect_stdout
import itertools
import threading
import time
import sys


class Prelaunch(tk.Toplevel):
    def __init__(self, master=None, on_confirm=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        utils.log_message('info', "Prelaunch window initialized")

        # Load configuration file
        with open(utils.settingPath(), 'r') as file:
            self.setting = json.load(file)
        utils.log_message('debug', f"Loaded settings: {self.setting}")

        # Display current JAVA_HOME and Fiji directories
        self.JHLb = tk.Label(self, text=f'JAVA_HOME={self.setting["JAVA_HOME"]}')
        self.FJLb = tk.Label(self, text=f'fiji_dir={self.setting["fiji_dir"]}')

        self.JHLb.pack()
        tk.Button(self, text='Change JAVA_HOME', command=self.update_JAVA_HOME).pack()
        self.FJLb.pack()
        tk.Button(self, text='Change fiji_dir', command=self.update_fijiDir).pack()

        # Run ImageJ environment check
        text_box = tk.Text(self)
        text_box.pack()
        text_box.insert(tk.END, self.capture_checkup_output())
        text_box.config(state='disabled')

        # Confirm launch section
        tk.Label(self, text="Proceed to main app?").pack(pady=10)
        tk.Button(self, text="Yes", command=lambda: self._confirm(on_confirm)).pack(side="left", padx=30)
        tk.Button(self, text="No", command=self.destroy).pack(side="right", padx=30)

    def capture_checkup_output(self):
        # Perform ImageJ environment check and capture the output
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            imagej.doctor.checkup()
        output = buffer.getvalue()
        buffer.close()
        utils.log_message('info', "ImageJ doctor checkup completed")
        return output

    def update_JAVA_HOME(self):
        # Change JAVA_HOME directory
        path = filedialog.askdirectory(title='Select the JAVA_HOME Directory')
        if path != '':
            self.setting["JAVA_HOME"] = path
            self.JHLb.config(text=f'JAVA_HOME={self.setting["JAVA_HOME"]}')
            self.update_setting()
            utils.log_message('info', f"Updated JAVA_HOME: {path}")

    def update_fijiDir(self):
        # Change Fiji directory
        path = filedialog.askdirectory(title='Select the fiji installation Directory')
        if path != '':
            self.setting["fiji_dir"] = path
            self.FJLb.config(text=f'fiji_dir={self.setting["fiji_dir"]}')
            self.update_setting()
            utils.log_message('info', f"Updated Fiji directory: {path}")

    def update_setting(self):
        # Save updated settings to file
        with open(utils.settingPath(), 'w') as file:
            json.dump(self.setting, file, indent=4)
        utils.log_message('debug', "Settings updated and saved successfully")

    def _confirm(self, on_confirm):
        # User confirmed to launch main window
        utils.log_message('info', "User confirmed to launch main window")
        self.destroy()
        on_confirm()


class Windows(tk.Toplevel):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        utils.log_message('info', "Initializing main window")

        try:
            # Load settings
            with open(utils.settingPath(), 'r') as file:
                self.setting = json.load(file)
            utils.log_message('debug', f"Loaded settings: {self.setting}")

            # Initialize ImageJ
            os.environ['JAVA_HOME'] = self.setting["JAVA_HOME"]
            self.imageJ = ImageJ(self.setting["fiji_dir"], mode='interactive')
            utils.log_message('info', "ImageJ initialized successfully")
        except Exception as e:
            utils.errorMsg(title='Init error', msg=f'fiji/JAVA_HOME dir is wrong ({e})')
            utils.log_message('error', f"Failed to initialize ImageJ: {e}")

        # Window setup
        self.wm_title('Untitled_Project')
        self.wm_geometry('800x600')
        self.protocol("WM_DELETE_WINDOW", self.window_exit)

        # Menu bar setup
        menubar = tk.Menu()
        self.config(menu=menubar)

        fileMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='save', command=self.save)
        menubar.add_cascade(label='open', command=self.open)

        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp(prefix="temp_")
        os.makedirs(os.path.join(self.temp_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "imageJ", "data"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "imageJ", "result"), exist_ok=True)
        utils.log_message('debug', f"Temporary directories created at {self.temp_dir}")

        self.save_Dir = None
        self.project_Name = None

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Tabs setup
        self.notebook = ttk.Notebook(self)
        self.tab2 = Tab2(self.notebook, imageJ=self.imageJ, setting=self.setting, temp_dir=self.temp_dir)
        self.tab1 = Tab1(self.notebook, save_Dir=self.save_Dir, tab2=self.tab2, temp_dir=self.temp_dir)
        self.tab3 = Tab3(self.notebook)
        self.tab4 = Tab4(self.notebook)
        self.notebook.add(self.tab1, text="Upload Image")
        self.notebook.add(self.tab2, text="Count")
        self.notebook.add(self.tab3, text="Table Manager")
        self.notebook.add(self.tab4, text="Info/ Misc")
        self.notebook.grid(row=0, column=0, sticky=tk.NSEW)
        utils.log_message('info', "Main window UI initialized")

    def window_exit(self):
        # Handle window close request
        close = messagebox.askyesno("Exit?", "Are you sure you want to exit? Any unsaved project will be lost")
        if close:
            try:
                self.imageJ.exit()
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                self.destroy()
                utils.log_message('info', "Application closed and resources cleaned up")
            except Exception as e:
                utils.log_message('error', f"Error during application exit: {e}")

    def save(self):
        # Save project data
        if self.save_Dir is None:
            self.save_Dir = filedialog.askdirectory(title='Create a new project Directory')
            if self.save_Dir == '':
                self.save_Dir = None
                return
            shutil.copytree(self.temp_dir, self.save_Dir, dirs_exist_ok=True)
            self.wm_title(self.save_Dir)
            self.tab1.update_save_Dir(self.save_Dir)
            self.tab2.update_save_Dir(self.save_Dir)
            utils.log_message('info', f"Project saved to {self.save_Dir}")
        else:
            utils.infoMsg('Information', 'project already saved')
            utils.log_message('warning', "Save attempted but project already saved")

    def open(self):
        # Open existing project directory
        prv_save = self.save_Dir
        if self.save_Dir is None:
            self.save_Dir = filedialog.askdirectory(title='Select the project Directory')
            if self.save_Dir == '' and prv_save is None:
                self.save_Dir = None
                utils.log_message('warning', "Open cancelled: No directory selected")
                return
            else:
                self.wm_title(self.save_Dir)
                self.tab1.update_save_Dir(self.save_Dir)
                self.tab2.update_save_Dir(self.save_Dir)
                utils.log_message('info', f"Opened project from {self.save_Dir}")
        else:
            utils.infoMsg('Information', 'project already been open/ created')
            utils.log_message('warning', "Open attempted but project already open")


def main():
    # Initialize base Tk root and launch Prelaunch first
    root = tk.Tk()
    root.withdraw()
    utils.set_icon(root)
    utils.log_message('info', "Application started, Prelaunch window opened")

    def launch_main():
        # Launch main app after prelaunch confirmation
        app = Windows(root)
        utils.log_message('info', "Launching main window")
        app.mainloop()

    pre = Prelaunch(root, on_confirm=launch_main)
    root.mainloop()
    utils.log_message('info', "Main event loop ended")


if __name__ == "__main__":
    utils.log_message('info', "Starting application execution")
    main()
