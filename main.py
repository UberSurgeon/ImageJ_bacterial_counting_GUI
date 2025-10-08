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


class Windows(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        utils.set_icon(self)
        
        try:
            # get setting
            with open(utils.settingPath(), 'r') as file:
                self.setting = json.load(file)

            # init imageJ
            os.environ['JAVA_HOME'] = self.setting["JAVA_HOME"]
            self.imageJ = ImageJ(self.setting["fiji_dir"], mode='interactive')
        except Exception as e:
            utils.errorMsg(title='Init error',
                           msg=f'fiji/JAVA_HOME dir is wrong ({e})')

        self.wm_title('Untitled_Project')
        self.wm_geometry('800x600')
        self.protocol("WM_DELETE_WINDOW", self.window_exit)

        menubar = tk.Menu()
        self.config(menu=menubar)

        fileMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='save',
                            command=self.save)
        menubar.add_cascade(label='open',
                            command=self.open)

        # init temp file
        self.temp_dir = tempfile.mkdtemp(prefix="temp_")

        os.makedirs(os.path.join(self.temp_dir, "raw"),
                    exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "imageJ", "data"),
                    exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "imageJ", "result"),
                    exist_ok=True)

        self.save_Dir = None
        self.project_Name = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)

        self.tab2 = Tab2(self.notebook,
                         imageJ=self.imageJ,
                         setting=self.setting,
                         temp_dir=self.temp_dir)
        self.tab1 = Tab1(self.notebook,
                         save_Dir=self.save_Dir,
                         tab2=self.tab2,
                         temp_dir=self.temp_dir)
        self.tab3 = Tab3(self.notebook)
        self.tab4 = Tab4(self.notebook)
        self.notebook.add(self.tab1, text="Upload Image")
        self.notebook.add(self.tab2, text="Count")
        self.notebook.add(self.tab3, text="Table Manager")
        self.notebook.add(self.tab4, text="Info/ Misc")
        self.notebook.grid(row=0, column=0, sticky=tk.NSEW)

    def window_exit(self):
        close = messagebox.askyesno(
            "Exit?",
            "Are you sure you want to exit? Any unsaved project will be lost"
            )
        if close:
            # ignore all crash error, forcing the java vm to close
            try:
                self.imageJ.exit()
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                self.destroy()
            except Exception as e:
                print(f'error exit: {e}')

    def save(self):
        if self.save_Dir is None:
            self.save_Dir = filedialog.askdirectory(
                title='Create a new project Directory'
                )
            if self.save_Dir == '':
                self.save_Dir = None
                return
            shutil.copytree(self.temp_dir, self.save_Dir, dirs_exist_ok=True)
            self.wm_title(self.save_Dir)
            self.tab1.update_save_Dir(self.save_Dir)
            self.tab2.update_save_Dir(self.save_Dir)
        else:
            utils.infoMsg('Information', 'project already saved')

    def open(self):
        prv_save = self.save_Dir
        if self.save_Dir is None:
            self.save_Dir = filedialog.askdirectory(
                title='Select the project Directory'
                )
            if self.save_Dir == '' and prv_save is None:
                self.save_Dir = None
                return
            else:
                self.wm_title(self.save_Dir)
                self.tab1.update_save_Dir(self.save_Dir)
                self.tab2.update_save_Dir(self.save_Dir)
        else:
            utils.infoMsg('Information',
                          'project already been open/ created'
                          )




def main():
    app = Windows()
    app.mainloop()



if __name__ == "__main__":
    # if not pyuac.isUserAdmin():
    #     print("Re-launching with admin privileges...")
    #     pyuac.runAsAdmin()
    # else:
    main()
    
