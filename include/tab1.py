import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
from tkinter import ttk
from include.imageViewer import CanvasImage
from typing import Literal
from include.tab2 import Tab2


class Tab1(tk.Frame):
    def __init__(self, parent, save_Dir, tab2: Tab2, temp_dir):
        super().__init__(parent)
        ttk.Frame.__init__(self, master=parent)
        
        self.tab2 = tab2
        self.temp_dir = temp_dir
        
        self.save_Dir = save_Dir
        

        
        self.img_list = []
        self.img_index = 0
        
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.img_canvas = tk.Canvas(self, width=500, height=500)
        self.init_text_id = self.img_canvas.create_text(100, 50, text="No Image Selected", fill="black", font=('Helvetica 15 bold'))
        self.img_canvas.bind("<Button-1>", self.callback)
        self.img_canvas.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)
        
        
        self.canvas_img_id = None
        
        button_back = tk.Button(self, text="<<", command=self.img_idx_back)
        button_fwd = tk.Button(self, text=">>", command=self.img_idx_fwd)
        button_upload = tk.Button(self, text="Upload", command=self.openFile)
        button_del = tk.Button(self, text='remove image', command=self.delImage)
        button_back.grid(row=2, column=0, sticky=tk.NSEW)
        button_upload.grid(row=2, column=1, sticky=tk.NSEW)
        button_fwd.grid(row=2, column=2, sticky=tk.NSEW)
        button_del.grid(row=3, column=1, sticky=tk.NSEW)
        
        

    def updateImage(self):
        if self.save_Dir != None:
            # dst = os.path.join(self.save_Dir, 'raw')
            try:
                self.img_list = []
                path = os.path.dirname(__file__)
                dst = self.getDst(path=path, dst='raw')
                for filename in os.listdir(dst):
                    path = os.path.normpath(os.path.join(dst, filename))
                    self.img_list.append(path)

                self.displayImage()
            except Exception as e:
                self.error_msg(title='updateImgae', msg=f'error in updateImage {e}')

    def openFile(self):
        path = os.path.dirname(__file__)
        dst = self.getDst(path=path, dst='raw')
        # if self.save_Dir != None:
        #     dst = os.path.join(self.save_Dir, 'raw')
        #     # filepath = os.listdir(dst)
        # else:
        #     dst = os.path.join(os.path.dirname(__file__), 'temp', 'raw')

        try:
            filepath = filedialog.askopenfiles(initialdir='gui',
                            title='select images',
                            filetypes=(('png files', '*.png'),
                                        ("all files", "*.*")))

            for file in filepath:
                print(file.name)
                shutil.copy2(str(file.name), dst)
            # print(dst)
            self.img_list = []
            for filename in os.listdir(dst):
                path = os.path.normpath(os.path.join(dst, filename))
                self.img_list.append(path)

            self.displayImage()
            self.tab2.mode = 'raw'
            self.tab2.displayImage()

        except Exception as e:
            self.error_msg(title='openFile', msg=f'error during openFile {e}')

    def delImage(self):
        imgPath = self.img_list[self.img_index]
        if os.path.exists(imgPath):
            if messagebox.askokcancel(title='delImage', message='are you sure you wanna remove this image? T-T'):
                os.remove(imgPath)
                del self.img_list[self.img_index]
                self.img_index = max(0, self.img_index - 1)
                messagebox.showinfo(title='delImage', message='image removed')

                self.displayImage()
                self.tab2.img_index = self.img_index
                self.tab2.displayImage()
            else:
                print('四不像等一下诶嗯啊！')
        else:
            self.error_msg('delImage', 'Image dont exist')

    def displayImage(self):
        if not self.img_list:
            self.img_canvas.delete(self.canvas_img_id)
            self.canvas_img_id = None
            self.init_text_id = self.img_canvas.create_text(100, 50, text="No Image Selected", fill="black", font=('Helvetica 15 bold'))
            return None
        try:
            imgPath = self.img_list[self.img_index]
            self.img = Image.open(imgPath)
            picsize = 500, 500
            size = self.img.size
            self.img = self.img.resize(self.best_fit(size, picsize), Image.Resampling.LANCZOS)
            self.photoImg = ImageTk.PhotoImage(self.img)
            
            if self.canvas_img_id is None:
                self.img_canvas.delete(self.init_text_id)
                self.canvas_img_id = self.img_canvas.create_image(
                    250, 250, image=self.photoImg, anchor="center"
                )
            else:
                self.img_canvas.itemconfig(self.canvas_img_id, image=self.photoImg)
        except Exception as e:
            self.error_msg(title='displayImage', msg=f'error in displayImage {e}')
            
    def best_fit(self, oldsize, picsize):
        new_width, new_height = picsize
        old_width, old_height = oldsize
        # if new_width/old_width < new_height/old_height is mathematically the same as
        if new_width * old_height < new_height * old_width:
            # reduce height to keep original aspect ratio
            new_height = max(1, old_height * new_width // old_width)
        else:
            # reduce width to keep original aspect ratio
            new_width = max(1, old_width * new_height // old_height)
        return (new_width, new_height)


    def img_idx_fwd(self):
        if self.img_index < len(self.img_list) - 1:
            self.img_index += 1
            # print(self.img_index)
            self.displayImage()

    def img_idx_back(self):
        if self.img_index > 0:
            self.img_index -= 1
            # print(self.img_index)
            self.displayImage()

    def callback(self, event):
        print('clicked')
        self.create_window()

    def create_window(self):
        if not self.img_list:
            return None
        imgPath = self.img_list[self.img_index]

        new_window = tk.Toplevel()
        new_window.geometry('800x600')
        new_window.rowconfigure(0, weight=1)  # make the CanvasImage widget expandable
        new_window.columnconfigure(0, weight=1)
        canvas = CanvasImage(new_window, imgPath)  # create widget
        canvas.grid(row=0, column=0)
        
    def update_save_Dir(self, save_Dir):
        
        self.save_Dir = save_Dir
        if self.save_Dir is not None:
            self.updateImage()
    
    def getDst(self, path, dst: Literal['raw']):
        if self.save_Dir is None:
            if dst == 'raw':
                # print(os.path.normpath(os.path.join(path, 'temp', 'raw')))
                return os.path.normpath(os.path.join(self.temp_dir, 'raw'))
        elif self.save_Dir is not None:
            if dst == 'raw':
                # print('here')
                # print(os.path.join(self.save_Dir, 'raw'))
                return os.path.normpath(os.path.join(self.save_Dir, 'raw'))
    
    def error_msg(self, title, msg):
        messagebox.showerror(title=title, message=msg)
    
    def warning_msg(self, title, msg):
        messagebox.showwarning(title=title, message=msg)
