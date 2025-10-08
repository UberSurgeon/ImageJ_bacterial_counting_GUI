import imagej.doctor
import os
import sys
from tkinter import filedialog
import json
from tkinter import messagebox
from typing import Literal, Union

# info box
def errorMsg(self, title, msg):
    messagebox.showerror(title=title, message=msg)

def warningMsg(self, title, msg):
    messagebox.showwarning(title=title, message=msg)
    
def infoMsg(self, title, msg):
    messagebox.showinfo(title=title, message=msg)

# path
def getDst(save_Dir: Union[str, None], temp_dir: str, dst: Literal['raw', 'count', 'data']):
        if save_Dir is None:
            if dst == 'raw':
                x = os.path.join(temp_dir, 'raw')
            elif dst == 'count':
                x = os.path.join(temp_dir, 'imageJ', 'result')
            elif dst == 'data':
                x = os.path.join(temp_dir, 'imageJ', 'data')
        elif self.save_Dir is not None:
            if dst == 'raw':
                x = os.path.join(save_Dir, 'raw')
            elif dst == 'count':
                x = os.path.join(save_Dir, 'imageJ', 'result')
            elif dst == 'data':
                x = os.path.join(self.save_Dir, 'imageJ', 'data')
        else:
            self.warning_msg(title='getDst', msg=f'dst in getDst not accounted -> {dst}')
        return os.path.normpath(x)

def imgPath(name):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'img', name)
    else:
        return os.path.join(sys.path[0], 'img', name)

def settingPath():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'setting', 'setting.json')
    else:
        return os.path.join(sys.path[0], 'setting', 'setting.json')
    
def set_icon(parent, ico_name='icon.ico'):
    import os
    from PIL import ImageTk
    ico_path = imgPath(ico_name)

    if os.path.exists(ico_path):
        icon_img = ImageTk.PhotoImage(file=ico_path)
        parent.wm_iconphoto(True, icon_img)
        parent.icon_img_ref = icon_img
