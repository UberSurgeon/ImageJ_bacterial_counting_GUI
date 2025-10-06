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
import json
import tempfile
import threading
import sys


class windows(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.started = False
        
        try:
            threading.Thread(target=self.pop).start()
        except Exception:
            print('loading done')
        
        try:
            # get setting
            with open(self.setting_path(), 'r') as file:
                self.setting = json.load(file)
            
            # init imageJ
            os.environ['JAVA_HOME'] = self.setting["JAVA_HOME"]
            # self.imageJ = ImageJ("C:/Users/NotEW/Desktop/Fiji", mode='interactive')
            self.imageJ = ImageJ(self.setting["fiji_dir"], mode='interactive')
        except Exception as e:
            self.error_msg(title='Init error', msg=f'somthing wrong with setting or, the fiji dir is wrong ({e})')
            
        try:
            self.iconbitmap(self.img_path('logo.ico'))
        except Exception as e:
            self.error_msg(title='icon error', msg=f'somthing wrong with icon({e})')
            
        
        
        self.wm_title('Untitled_Project')
        # self.reset()
        self.wm_geometry('800x600')
        self.protocol("WM_DELETE_WINDOW", self.window_exit)

        menubar = tk.Menu()
        self.config(menu=menubar)

        fileMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='save', command=self.save)
        menubar.add_cascade(label='open', command=self.open)
        menubar.add_cascade(label='fiji directory', command=self.update_fijiDir)
        
        #init temp file
        self.temp_dir = tempfile.mkdtemp(prefix="temp_")

        os.makedirs(os.path.join(self.temp_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "imageJ", "data"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "imageJ", "result"), exist_ok=True)
        # print(os.listdir(self.temp_dir))
        # print(os.listdir(os.path.join(self.temp_dir, "imageJ")))
        

        # button = tk.Button(text="OPEN", command=self.openFile)
        # button.grid(row=0, column=0)

        self.save_Dir = None
        self.project_Name = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        
        self.tab2 = Tab2(self.notebook, imageJ=self.imageJ, setting=self.setting, temp_dir=self.temp_dir)
        self.tab1 = Tab1(self.notebook, save_Dir=self.save_Dir, tab2=self.tab2, temp_dir=self.temp_dir)
        self.tab3 = Tab3(self.notebook)
        self.tab4 = Tab4(self.notebook)
        self.notebook.add(self.tab1, text="Tab 1")
        self.notebook.add(self.tab2, text="Tab 2")
        self.notebook.add(self.tab3, text="Tab 3")
        self.notebook.add(self.tab4, text="Tab 4")
        self.notebook.grid(row=0, column=0, sticky=tk.NSEW)
        
        self.started = True        

    def reset(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def window_exit(self):
        close = messagebox.askyesno("Exit?", "Are you sure you want to exit? Any unsaved project will be lost")
        if close:
            # ignore all crash error, forcing the java vm to close
            try:
                self.imageJ.exit()
                self.reset()
                self.destroy()
            except Exception as e:
                pass
            
    def save(self):
        if self.save_Dir is None:
            self.save_Dir = filedialog.askdirectory(title='Create a new project Directory')
            if self.save_Dir == '':
                self.save_Dir = None
                return
            # move files
            # temp = os.path.join(os.path.dirname(__file__), 'temp')
            shutil.copytree(self.temp_dir, self.save_Dir, dirs_exist_ok=True)
            self.wm_title(self.save_Dir)
            self.tab1.update_save_Dir(self.save_Dir)
            self.tab2.update_save_Dir(self.save_Dir)
        else:
            messagebox.showinfo('Information', 'project already saved')

    def open(self):
        prv_save = self.save_Dir
        if self.save_Dir is None:
            self.save_Dir = filedialog.askdirectory(title='Select the project Directory')
            if self.save_Dir == '' and prv_save is None:
                self.save_Dir = None
                return
            else:
                self.wm_title(self.save_Dir)
                self.tab1.update_save_Dir(self.save_Dir)
                self.tab2.update_save_Dir(self.save_Dir)
        else:
            messagebox.showinfo('Information', 'project already been open/ created')
    
    def update_fijiDir(self):
        path = filedialog.askdirectory(title='Select the project Directory', initialdir=self.setting["fiji_dir"])
        if path != '':
            self.setting["fiji_dir"] = path
            # print('fiji folder updated')
            self.update_setting()

    def update_setting(self):
        self.tab2.update_setting(self.setting)
        
        with open('gui/setting.json', 'w') as file:
            json.dump(self.setting, file, indent=4)

        #tell use that update complete, and need to restart for change to take effect file will be lost
        self.window_exit()
        
    def error_msg(self, title, msg):
        messagebox.showerror(title=title, message=msg)
    
    def warning_msg(self, title, msg):
        messagebox.showwarning(title=title, message=msg)
        
    def pop(self):
        new = tk.Tk()
        l = tk.Label(new, text='Loading')
        l.pack()
        def check_close():
            if self.started:
                new.destroy()
            else:
                new.after(100, check_close)  # check again after 100 ms

        check_close()
        new.mainloop()
    
    def setting_path(self):
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, 'setting', 'setting.json')
        else:
            return os.path.join(sys.path[0], 'setting', 'setting.json')
        
    def img_path(self, name):
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, 'img', name)
        else:
            return os.path.join(sys.path[0], 'img', name)

        
def main():
    testObj = windows()
    testObj.mainloop()


if __name__ == "__main__":
    # if not pyuac.isUserAdmin():
    #     print("Re-launching with admin privileges...")
    #     pyuac.runAsAdmin()
    # else:
    main()
    
