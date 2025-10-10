import os
import sys
from tkinter import messagebox
from typing import Literal, Union
import logging
from typing import Literal

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

def log_message(level: Literal['debug', 'info', 'warning', 'error', 'critical'], message):
    """
    Log a message at a given level.
    
    Parameters:
        level (str): One of "debug", "info", "warning", "error", "critical"
        message (str): The message to log
    """
    level = level.lower()
    if level == "debug":
        logging.debug(message)
    elif level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "critical":
        logging.critical(message)
    else:
        logging.warning(f"Unknown log level '{level}': {message}")

# info box
def errorMsg(title, msg):
    messagebox.showerror(title=title, message=msg)
    log_message('error', f'{title} - {msg}')

def warningMsg(title, msg):
    messagebox.showwarning(title=title, message=msg)
    log_message('warning', f'{title} - {msg}')

def infoMsg(title, msg):
    messagebox.showinfo(title=title, message=msg)
    log_message('info', f'{title} - {msg}')

# path
def getDst(save_Dir: Union[str, None], temp_dir: str, dst: Literal['raw', 'count', 'data']):
        if save_Dir is None:
            if dst == 'raw':
                x = os.path.join(temp_dir, 'raw')
            elif dst == 'count':
                x = os.path.join(temp_dir, 'imageJ', 'result')
            elif dst == 'data':
                x = os.path.join(temp_dir, 'imageJ', 'data')
        elif save_Dir is not None:
            if dst == 'raw':
                x = os.path.join(save_Dir, 'raw')
            elif dst == 'count':
                x = os.path.join(save_Dir, 'imageJ', 'result')
            elif dst == 'data':
                x = os.path.join(save_Dir, 'imageJ', 'data')
        else:
            warningMsg(title='getDst', msg=f'dst in getDst not accounted -> {dst}')
        return os.path.normpath(x)

def imgPath(name):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'img', name)
    else:
        return os.path.join(sys.path[0], 'img', name)

def settingPath():
    """Return the path to setting.json located next to the executable."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller EXE
        base_path = os.path.dirname(sys.executable)
    else:
        # Running from source
        base_path = sys.path[0]

    return os.path.join(base_path, "setting", "setting.json")
    
def set_icon(parent, ico_name='icon.ico'):
    import os
    from PIL import ImageTk
    ico_path = imgPath(ico_name)

    if os.path.exists(ico_path):
        icon_img = ImageTk.PhotoImage(file=ico_path)
        parent.wm_iconphoto(True, icon_img)
        parent.icon_img_ref = icon_img
        
def best_fit(oldsize, picsize):
    new_width, new_height = picsize
    old_width, old_height = oldsize
    if new_width * old_height < new_height * old_width:
        # reduce height to keep original aspect ratio
        new_height = max(1, old_height * new_width // old_width)
    else:
        # reduce width to keep original aspect ratio
        new_width = max(1, old_width * new_height // old_height)
    
    log_message(
        'debug',
        f'Change thumbnail size {
            old_width, old_height} -> {
                new_width, new_height}')
    
    return (new_width, new_height)

