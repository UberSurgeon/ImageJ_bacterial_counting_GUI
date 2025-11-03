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
from include.tab4 import Tab4
from include.tab1_1 import Tab1_1
from include.ijClass import ImageJ
from include.loading import LoadingWindow
from include.SaveDialog import SaveDialog
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
import torch
import stat
from preprocess.minicpm_predict import ensure_ollama_ready
import customtkinter as ctk
from include.DirectoryCard import DirectoryCard
from include.LogDropDown import LogDropdown
from typing import Literal

if getattr(sys, 'frozen', False):
    import pyi_splash


loader = LoadingWindow("ImageJ...", spinner=True)

APP_BG= "#f1f8ff"

TEXT_COLOR = "#003366"

ACCENT_COLOR = "#0066cc"
TEXT_COLOR = "#ffffff"
ROBOTO_BOLD = ("Roboto", 18, "bold")
ROBOTO_LABEL = ("Roboto", 16)

class Prelaunch(ctk.CTkToplevel):
    def __init__(self, master=None, on_confirm=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        utils.log_message('info', "Prelaunch window initialized")
        utils.log_message('info', 'in prolaunch')
        self.protocol("WM_DELETE_WINDOW", self._exit)
        self.configure(fg_color=APP_BG)
        self.title("launcher")

        self.icon_path = ImageTk.PhotoImage(file=utils.imgPath('icon.ico'))
        self.wm_iconbitmap()
        self.after(250, lambda: self.iconphoto(False, self.icon_path))

        # Load configuration file
        with open(utils.settingPath(), 'r') as file:
            self.setting = json.load(file)
        utils.log_message('debug', f"Loaded settings: {self.setting}")
        # if self.setting['launch'] == 0:
        #     utils.log_message('info', f"first time")
        # elif self.setting['launch'] == 1:
        #     utils.log_message('info', f"not first time (launch is 1)")
        #     self._exit()
        
        self.output = self.capture_checkup_output()
        # print(self.output)
         
        style = ttk.Style()
        style.theme_use("default")

        # Notebook container
        style.configure("TNotebook",
                        background=APP_BG,
                        borderwidth=0,
                        padding=10)

        # Individual Tabs
        style.configure("TNotebook.Tab",
                        background=APP_BG,
                        foreground=TEXT_COLOR,
                        padding=[20, 10],
                        borderwidth=0,
                        font=("Segoe UI", 10, "bold"))

        # Hover/selected states
        style.map("TNotebook.Tab",
                background=[("selected", ACCENT_COLOR),
                            ("active", "#004c99")],
                foreground=[("selected", TEXT_COLOR),
                            ("active", TEXT_COLOR)])

        # frame for the directory buttons

        self.button_frame = ctk.CTkFrame(self,fg_color=APP_BG)
        self.button_frame.pack(expand=True,fill="both",padx=20,pady=20)
        self.button_frame.columnconfigure(0,weight=1)
        self.button_frame.columnconfigure(1,weight=1)



        # styles 

        roboto_bold = ("Roboto",14,"bold")

        roboto_label = ("Roboto", 10)

        self.java_card = DirectoryCard(self.button_frame,"Current Java Directory",f'{self.setting["JAVA_HOME"]}',"Change",command=self.update_JAVA_HOME)
        self.fiji_card = DirectoryCard(self.button_frame,"Current Fiji Directory",f'{self.setting["fiji_dir"]}',"Change",command=self.update_fijiDir)
        self.java_card.grid(row=0,column=0,sticky="nsew",padx=10,pady=10)
        self.fiji_card.grid(row=0,column=1,sticky="nsew",padx=10,pady=10)

        # Display current JAVA_HOME and Fiji directories
        #self.JHLb = tk.Label(self, text=f'JAVA_HOME={self.setting["JAVA_HOME"]}')
        #self.FJLb = tk.Label(self, text=f'fiji_dir={self.setting["fiji_dir"]}')
        #self.torch = tk.Label(self)
        self.torch = ctk.CTkLabel(self,font=roboto_label,text_color="#003366")

        if torch.cuda.is_available():
            self.torch.configure(text=f'GPU available, {torch.cuda.get_device_properties(0)}')
        else:
            self.torch.configure(text=f'GPU NOT available')

        self.olm = ctk.CTkLabel(self,font=roboto_label,text_color="#003366")
        self.olm.configure(text=f'Ollama status={ensure_ollama_ready()}')

        self.torch.pack()
        self.olm.pack()
        
        


        # Run ImageJ environment check
        # text_box = tk.Text(self)
        # text_box.pack()
        # text_box.insert(tk.END, self.capture_checkup_output())
        # text_box.config(state='disabled')

        log_dropdown = LogDropdown(self, self.output)
        log_dropdown.pack(pady=20,fill="x")

        # Confirm launch section
        # tk.Label(self, text="Proceed to main app?").pack(pady=10)
        # tk.Button(self, text="Yes", command=lambda: self._confirm(on_confirm)).pack(side="left", padx=30)
        # tk.Button(self, text="No", command=self._exit).pack(side="right", padx=30)
        
        if getattr(sys, 'frozen', False):
            pyi_splash.close()
        

        ctk.CTkButton(self, text="Proceed to main app", command=lambda: self._confirm(on_confirm), text_color="white",font=roboto_bold,corner_radius=12,height=40,width=180).pack(pady=20)


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
            self.java_card.change_name(name=f'JAVA_HOME={self.setting["JAVA_HOME"]}')
            self.update_setting()
            utils.log_message('info', f"Updated JAVA_HOME: {path}")

    def update_fijiDir(self):
        # Change Fiji directory
        path = filedialog.askdirectory(title='Select the fiji installation Directory')
        if path != '':
            self.setting["fiji_dir"] = path
            self.fiji_card.change_name(name=f'fiji_dir={self.setting["fiji_dir"]}')
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
        self.setting["launch"] = 1
        self.update_setting()
        utils.log_message('info', f"Updated launch: 1")
        on_confirm()
    
    def _exit(self):
        self.quit()
        self.destroy()
        sys.exit(0)
        




class Windows(ctk.CTkToplevel):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        utils.log_message('info', "Initializing main window")

        self.icon_path = ImageTk.PhotoImage(file=utils.imgPath('icon.ico'))
        self.wm_iconbitmap()
        self.after(250, lambda: self.iconphoto(False, self.icon_path))

        try:
            # Load settings
            with open(utils.settingPath(), 'r') as file:
                self.setting = json.load(file)
            utils.log_message('debug', f"Loaded settings: {self.setting}")

            loader.start()
            # Initialize ImageJ
            os.environ['JAVA_HOME'] = self.setting["JAVA_HOME"]
            self.imageJ = ImageJ(self.setting["fiji_dir"], mode='interactive')
            utils.log_message('info', "ImageJ initialized successfully")
        except Exception as e:
            utils.errorMsg(title='Init error', msg=f'fiji/JAVA_HOME dir is wrong ({e})')
            utils.log_message('error', f"Failed to initialize ImageJ: {e}")
            self.window_exit()

        # Window setup
        self.wm_title('Untitled_Project')
        self.wm_geometry('1200x800')
        self.protocol("WM_DELETE_WINDOW", self.window_exit)

        # Menu bar setup
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=False)
        self.file_menu.add_command(label='New', command=self.new)
        self.file_menu.add_command(label='Open', command=self.open)
        self.file_menu.add_command(label='Save As', command=self.save)

        self.menubar.add_cascade(label='File', menu=self.file_menu)


        # Create temporary directories
        self.setFolder()
        self.save_Dir = None
        self.project_Name = None

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


        self.notebook = ctk.CTkTabview(self, fg_color=APP_BG,anchor="nw")
        self.notebook.grid(row=0, column=0, sticky="nsew",padx=0,pady=0)

        # Add tabs
        self.notebook.add("Upload Image")
        self.notebook.add("Rename")
        self.notebook.add("Count")
        self.notebook.add("Info / Misc")

        # Apply consistent sizing
        for tab_name in self.notebook.tab("Upload Image"), self.notebook.tab("Rename"), self.notebook.tab("Count"), self.notebook.tab("Info / Misc"):
            tab_name.grid_columnconfigure(0, weight=1)
            tab_name.grid_rowconfigure(0, weight=1)

        # Embed existing tab classes inside the CTkTabview
        self.tab1 = Tab1(self.notebook.tab("Upload Image"), save_Dir=self.save_Dir, temp_dir=self.temp_dir, windows=self)
        self.tab1_1 = Tab1_1(self.notebook.tab("Rename"), save_Dir=self.save_Dir, temp_dir=self.temp_dir, windows=self)
        self.tab2 = Tab2(self.notebook.tab("Count"), imageJ=self.imageJ, setting=self.setting, temp_dir=self.temp_dir)
        self.tab4 = Tab4(self.notebook.tab("Info / Misc"))

        # Place them inside each tab frame
        self.tab1.pack(fill="both", expand=True)
        self.tab1_1.pack(fill="both", expand=True)
        self.tab2.pack(fill="both", expand=True)
        self.tab4.pack(fill="both", expand=True)

        utils.log_message('info', "Main window UI initialized")
        loader.stop()
        self.lift()

    def window_exit(self):
        # Handle window close request
        close = messagebox.askyesno("Exit?", "Are you sure you want to exit? Any unsaved project will be lost")
        if close:
            try:
                if getattr(sys, 'frozen', False):
                    BASE_DIR = sys._MEIPASS
                else:
                    BASE_DIR = sys.path[0]
                x = os.path.join('preprocess', 'yolov7', 'runs', 'detect')

                self.setting["launch"] = 0
                # Save updated settings to file
                with open(utils.settingPath(), 'w') as file:
                    json.dump(self.setting, file, indent=4)
                utils.log_message('debug', "Settings updated and saved successfully")
                utils.log_message('info', "Updated launch: 0")
                self.force_rmtree(self.temp_dir)
                self.force_rmtree(os.path.join(BASE_DIR, x))
                self.imageJ.exit()
                # shutil.rmtree(self.temp_dir, ignore_errors=True)
                self.destroy()
                utils.log_message('info', "Application closed and resources cleaned up")
                sys.exit(0)
            except Exception as e:
                utils.log_message('error', f"Error during application exit: {e}")
                
    def force_rmtree(self, path, retries=5, delay=0.5):
        """Forcefully remove a folder and all contents, handling permissions and locks."""
        if not os.path.exists(path):
            return

        def onerror(func, p, exc_info):
            # Change permissions if file is read-only
            try:
                os.chmod(p, stat.S_IWRITE)
                func(p)
            except Exception:
                pass  # Ignore errors but continue deleting

        for i in range(retries):
            try:
                shutil.rmtree(path)
                if not os.path.exists(path):
                    return
            except PermissionError:
                # Sometimes a process (like ImageJ, Pillow, etc.) still holds the file
                time.sleep(delay)
            except Exception as e:
                print(f"Warning: retry {i+1}/{retries} failed: {e}")
                time.sleep(delay)
        # Last resort
        try:
            shutil.rmtree(path, ignore_errors=True)
        except Exception as e:
            print(f"Final attempt failed to remove {path}: {e}")
    
    def setFolder(self):
        self.temp_dir = tempfile.mkdtemp(prefix="temp_")
        os.makedirs(os.path.join(self.temp_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "imageJ", "data"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "imageJ", "result"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "crop", "raw", "dishes"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "crop", "raw", "labels"), exist_ok=True)
        # os.makedirs(os.path.join(self.temp_dir, "crop", "labels"), exist_ok=True)
        utils.log_message('debug', f"Temporary directories created at {self.temp_dir}")

    def save(self):
        dialog = SaveDialog(self, title="Save Project As", initial_dir=os.getcwd())
        self.wait_window(dialog)
        save_path = dialog.result

        if not save_path:
            self.save_Dir = None
            utils.log_message('info', "Save operation cancelled by user.")
            return

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        self.save_Dir = save_path
        shutil.copytree(self.temp_dir, self.save_Dir, dirs_exist_ok=True)
        self.wm_title(self.save_Dir)
        
        # Update paths in data.json to be absolute paths in the new project directory
        data_json_path = os.path.join(self.save_Dir, 'imageJ', 'data', 'data.json')
        if os.path.exists(data_json_path):
            with open(data_json_path, 'r+') as f:
                data = json.load(f)
                for item in data:
                    for key in ['img_path', 'label_path', 'count_path']:
                        if key in item and item[key] and self.temp_dir in item[key]:
                            relative_path = os.path.relpath(item[key], self.temp_dir)
                            item[key] = os.path.join(self.save_Dir, relative_path)
                
                f.seek(0)  # Go to the beginning of the file
                json.dump(data, f, indent=4)
                f.truncate() # Remove old content if new content is shorter

        self.update_save()
        utils.log_message('info', f"Project saved to {self.save_Dir}")

    def open(self):
        # Open existing project directory
        prv_save = self.save_Dir
        self.save_Dir = filedialog.askdirectory(title='Select the project Directory')
        if self.save_Dir == '' and prv_save is None:
            self.save_Dir = None
            utils.log_message('warning', "Open cancelled: No directory selected")
            return
        else:
            self.wm_title(self.save_Dir)
            self.update_save()
            utils.log_message('info', f"Opened project from {self.save_Dir}")            
            self.change_tab('Count')
            
    def new(self):
        if messagebox.askokcancel(title='new', message='Do you want to start a new project?'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.save_Dir = None
            self.setFolder()
            self.wm_title('Untitled_Project')
            self.update_save()
            self.update_temp()
            self.update_img_dict_list([])
            utils.log_message('info', "new empty project")
            self.change_tab('Upload Image')

    def update_save(self):
        self.tab1.update_save_Dir(self.save_Dir)
        self.tab2.update_save_Dir(self.save_Dir)
        data_dir = utils.getDst(self.save_Dir, self.temp_dir, 'data')
        json_path = os.path.join(data_dir, 'data.json')
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as data_file:
                loaded_data = json.load(data_file)
                self.update_img_dict_list(loaded_data)
                self.tab2.updateTable(loaded_data)

    def update_temp(self):
        self.tab1.update_temp_Dir(self.temp_dir)
        self.tab2.update_temp_Dir(self.temp_dir)
        print(self.tab2.temp_dir)
        
    def update_img(self):
        # Display and update tab2
        self.tab2.mode = 'dish'
        self.tab2.displayImage()

    def update_img_dict_list(self, img_dict_list):
        # print(img_dict_list)
        utils.log_message('debug', f"UPDATE_IMG_DICT_LIST CONTAIN >> {img_dict_list}")
        self.tab1_1.updateImage(img_dict_list)
        self.tab2.updateImage(img_dict_list)

    def change_tab(
            self,
            name: Literal[
                'Upload Image',
                'Rename',
                'Count',
                'Info / Misc'
                ]):
        self.notebook.set(name)  


def main():
    # Initialize base Tk root and launch Prelaunch first
    root = tk.Tk()
    root.withdraw()
    utils.set_icon(root)
    ctk.set_appearance_mode("light")
    utils.log_message('info', "Application started, Prelaunch window opened")


    def launch_main():
        # Launch main app after prelaunch confirmation
        app = Windows(root)
        utils.log_message('info', "Launching main window")
        app.mainloop()


    pre = Prelaunch(root, on_confirm=launch_main)
    utils.log_message('info', 'out prelaunch')


    root.mainloop()
    utils.log_message('info', "Main event loop ended")


if __name__ == "__main__":
    utils.log_message('info', "Starting application execution")
    main()
