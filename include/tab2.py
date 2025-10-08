import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from tkinter import ttk
from include.imageViewer import CanvasImage
from include.ijClass import ImageJ
from typing import Literal
import json
import include.utils as utils


class Tab2(tk.Frame):
    def __init__(self, parent, imageJ: ImageJ, setting, temp_dir):
        super().__init__(parent)
        self.temp_dir = temp_dir

        self.save_Dir = None

        self.setting = setting
        self.settingPath = utils.settingPath()

        self.imageJ = imageJ
        self.left_frame = tk.Frame(self, width=200, height=400)
        self.left_frame.grid(row=0, column=0)

        self.right_frame = tk.Frame(self, width=200, height=400)
        self.right_frame.grid(row=0, column=1)

        self.img_list = []
        self.img_metadata = []
        self.img_index = 0
        self.canvas_img_id = None
        self.mode: Literal['raw', 'count'] = 'raw'

        self.results = None

        self.img_canvas = tk.Canvas(self.left_frame, width=200, height=200)
        self.init_text_id = self.img_canvas.create_text(100, 50, text="No Image Selected", fill="black", font=('Helvetica 15 bold'))
        self.img_canvas.grid(row=0, column=0, columnspan=3)
        self.img_canvas.bind("<Button-1>", self.callback)
        tk.Button(self.left_frame, text="<<", command=self.img_idx_back).grid(row=1, column=0)
        tk.Button(self.left_frame, text=">>", command=self.img_idx_fwd).grid(row=1, column=1)
        
        
        self.tool_bar = tk.Frame(self.left_frame, width=180, height=185, bg='grey')
        self.tool_bar.grid(row=2, column=0)

        tk.Label(self.tool_bar, text='Tools', relief='raised').grid(row=0, column=0)
        
        tk.Button(self.tool_bar,  text="raw", command=self.getRawImage, width=10).grid(row=2,  column=0,  padx=5,  pady=5,  sticky='w'+'e'+'n'+'s')
        tk.Button(self.tool_bar,  text="count", command=self.askReCount, width=8).grid(row=3,  column=0,  padx=5,  pady=5,  sticky='w'+'e'+'n'+'s')
        tk.Button(self.tool_bar,  text=":", width=2, command=self.countSetting).grid(row=3,  column=1,  padx=5,  pady=5,  sticky='w'+'e'+'n'+'s')


        # meta data
        self.text_box = tk.Text(self.right_frame, height=10, width=70)
        self.text_box.grid(row=0, column=0, columnspan=5)
        self.text_box.config(state='disabled')
        
        
        self.table = ttk.Treeview(self.right_frame)
        self.table['columns'] = ('row', 'count', 'path')

        # Format the columns
        self.table.column('#0', width=0, stretch=tk.NO)
        self.table.column('row', anchor=tk.W, width=150)
        self.table.column('count', anchor=tk.W, width=200)
        self.table.column('path', anchor=tk.W, width=150)
        
        self.table.heading('#0', text='', anchor=tk.W)
        self.table.heading('row', text='row', anchor=tk.W)
        self.table.heading('count', text='count', anchor=tk.W)
        self.table.heading('path', text='path', anchor=tk.W)            
        # Place widgets with sticky
        self.table.grid(row=1, column=0, sticky='nsew')

        # Scrollbars
        vsb = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.table.yview)
        vsb.grid(row=1, column=1, sticky='ns')

        hsb = ttk.Scrollbar(self.right_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        hsb.grid(row=2, column=0, columnspan=2, sticky='ew')

        self.table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        
    def getRawImage(self):
        try:
            dst = self.getDst(dst='raw')
            self.img_list = []
            # get raw
            for filename in os.listdir(dst):
                path = os.path.normpath(os.path.join(dst, filename))
                self.img_list.append(path)
            if self.img_list:
                self.mode = 'raw'
                self.results = []
                self.createTable()
                self.displayImage()
            else:
                self.warning_msg('no image loaded', 'no image loaded to temp')
        except Exception as e:
            self.error_msg(title='getRawImage', msg=f'error getRawImage {e}')
        

    def askReCount(self):
        imgDir = self.getDst(dst='count')
        dataDir = self.getDst(dst='data')
        # print(self.mode)
        if os.listdir(imgDir) != [] and os.listdir(dataDir) != []:
            result = messagebox.askyesnocancel(title='ReCount?', message='Do you want to recount(yes) or just display the counted image?(no)')
            if result is True:
                self.getCountImage()
            elif result is False:
                with open(os.path.join(dataDir, 'data.json'), 'r') as file:
                    self.results = json.load(file)
                self.createTable()
                self.mode = 'count'
                self.displayImage()
            else:
                print('canceled')
        else:
            self.getCountImage()

    def getCountImage(self):
        try:
            dst = os.path.join(os.path.dirname(__file__), 'temp', 'raw')
            dst = self.getDst(dst='raw')
            imgDir = self.getDst(dst='count')
            dataDir = self.getDst(dst='data')
            self.img_list = []
            for filename in os.listdir(dst):
                path = os.path.normpath(os.path.join(dst, filename))
                self.img_list.append(path)
            
            if self.img_list:
                results = self.imageJ.laskePesakeLuvut(img_list=self.img_list, setting=self.setting, imgDir=imgDir, dataDir=dataDir)
                self.results = results
                # print(self.results)
                self.createTable()
                print('DONE COUNTING')
                self.mode = 'count'
                self.displayImage()
            else:
                self.warning_msg('no image loaded', 'no image loaded')
        except Exception as e:
            self.error_msg(title='getCountImage', msg=f'error getCountImage {e}')

    def getMetaData(self, img_list):
        try:
            # print(self.img_list)
            self.img_metadata = []
            for imgPath in img_list:
                image = Image.open(imgPath)
                info_dict = {
                        "Filename": image.filename,
                        "Image Size": image.size,
                        "Image Height": image.height,
                        "Image Width": image.width,
                        "Image Format": image.format,
                        "Image Mode": image.mode,
                        "Image is Animated": getattr(image, "is_animated", False),
                        "Frames in Image": getattr(image, "n_frames", 1)
                }
                # print(info_dict)
                self.img_metadata.append(info_dict)
        except Exception as e:
            self.error_msg(title='getMetaData', msg=f'error getMetaData {e}')

    def displayImage(self):
        try:
            dst = self.getDst(dst=self.mode)
            self.img_list = []
            # get img from mode
            for filename in os.listdir(dst):
                
                path = os.path.normpath(os.path.join(dst, filename))
                self.img_list.append(path)
            
            if not self.img_list:
                self.img_canvas.delete(self.canvas_img_id)
                self.canvas_img_id = None
                self.init_text_id = self.img_canvas.create_text(100, 50, text="No Image Selected", fill="black", font=('Helvetica 15 bold'))
                return None
            
            self.getMetaData(self.img_list)
            
            if not self.img_list:
                return None
            imgPath = self.img_list[self.img_index]
            self.img = Image.open(imgPath)
            picsize = 200, 200
            size = self.img.size
            self.img = self.img.resize(self.best_fit(size, picsize), Image.Resampling.LANCZOS)
            self.photoImg = ImageTk.PhotoImage(self.img)

            if self.canvas_img_id is None:
                self.img_canvas.delete(self.init_text_id)
                self.canvas_img_id = self.img_canvas.create_image(
                    100, 100, image=self.photoImg, anchor="center"
                )
                
            else:
                self.img_canvas.itemconfig(self.canvas_img_id, image=self.photoImg)
            # set meta data
            self.text_box.config(state='normal')
            self.text_box.delete("1.0", tk.END)
            self.text = "\n".join(f"{k}: {v}" for k, v in self.img_metadata[self.img_index].items())
            self.text_box.insert(tk.END, self.text)
            self.text_box.config(state='disabled')
        except Exception as e:
            self.error_msg(title='displayImage', msg=f'error displayImage {e}')
        
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
        # print('clicked')
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
    
    def createTable(self):
        self.table.tag_configure('oddrow', background='#E8E8E8')
        self.table.tag_configure('evenrow', background='#FFFFFF')
        
        for item in self.table.get_children():
            self.table.delete(item)
        
        for i in range(len(self.results)):
            value = (self.results[i]['row'], self.results[i]['count'], self.results[i]['img'])
            if i % 2 == 0:
                self.table.insert(parent='', index=i, values=value, tags=('evenrow',))
            else:
                self.table.insert(parent='', index=i, values=value, tags=('oddrow',))
            self.table.grid(row=1, column=0)
            
    def updateImage(self):
        if self.save_Dir != None:
            self.img_list = []
            dst = os.path.join(self.save_Dir, 'raw')
            for filename in os.listdir(dst):
                path = os.path.normpath(os.path.join(dst, filename))
                self.img_list.append(path)

            self.displayImage()

    def update_save_Dir(self, save_Dir):
        self.save_Dir = save_Dir
        if self.save_Dir is not None:
            self.updateImage()
            
    def getDst(self, dst: Literal['raw', 'count', 'data']):
        if self.save_Dir is None:
            if dst == 'raw':
                x = os.path.join(self.temp_dir, 'raw')
            elif dst == 'count':
                x = os.path.join(self.temp_dir, 'imageJ', 'result')
            elif dst == 'data':
                x = os.path.join(self.temp_dir, 'imageJ', 'data')
        elif self.save_Dir is not None:
            if dst == 'raw':
                x = os.path.join(self.save_Dir, 'raw')
            elif dst == 'count':
                x = os.path.join(self.save_Dir, 'imageJ', 'result')
            elif dst == 'data':
                x = os.path.join(self.save_Dir, 'imageJ', 'data')
        else:
            self.warning_msg(title='getDst', msg=f'dst in getDst not accounted -> {dst}')
        return os.path.normpath(x)
    
    def update_setting(self, setting):
        self.setting = setting
        
        try:
            with open(self.settingPath, 'w') as file:
                json.dump(self.setting, file, indent=4)
        except Exception as e:
            self.error_msg(title='update_setting', msg=f'error update_setting {e}')
    
    def countSetting(self):
        new_window = tk.Toplevel()
        new_window.geometry('200x250')
        modes = list(self.setting['preset'].keys())
        
        def on_key_press(event):
            if event.char.isdigit() or event.keysym == "BackSpace":
                return
            return "break"
        
        def show(event):
            result = opt.get()
            lbl.config(text=result)
            lbl_addlightness.config(text=f'addlightness = {self.setting['preset'][result]['addlightness']}')
            lbl_prominence.config(text=f'prominence = {self.setting['preset'][result]['prominence']}')
            
            if result == 'custom':
                in_lightL.pack()
                in_light.pack()
                in_promL.pack()
                in_prom.pack()
                in_light.bind("<KeyPress>", on_key_press)
                in_prom.bind("<KeyPress>", on_key_press)
            else:
                in_light.pack_forget()
                in_prom.pack_forget()
                in_lightL.pack_forget()
                in_promL.pack_forget()
        
        def confirm():
            result = opt.get()
            if result == 'custom':
                if in_light.get("1.0", "end-1c") == '':
                    light = 0
                else:
                    light = in_light.get("1.0", "end-1c")
                
                if in_prom.get("1.0", "end-1c") == '':
                    prom = 0
                else:
                    prom = in_prom.get("1.0", "end-1c")
                
                self.setting['preset'][result]['addlightness'] = light
                self.setting['preset'][result]['prominence'] = prom
                in_light.delete("1.0", "end")
                in_prom.delete("1.0", "end")
            lbl.config(text=result)
            check.config(text='saved*')
            lbl_addlightness.config(text=f'addlightness = {self.setting['preset'][result]['addlightness']}')
            lbl_prominence.config(text=f'prominence = {self.setting['preset'][result]['prominence']}')
            print(self.setting['preset'][result])
            self.setting["env"] = result
            self.update_setting(self.setting)
        
        opt = tk.StringVar(value=self.setting["env"])

        
        
        tk.Label(new_window, text='Select mode').pack()
        
        tk.OptionMenu(new_window, opt, *modes, command=show).pack()

        lbl = tk.Label(new_window, text=" ")
        lbl_addlightness = tk.Label(new_window, text=" ")
        lbl_prominence = tk.Label(new_window, text=" ")
        
        lbl.config(text=self.setting["env"])
        lbl_addlightness.config(text=f'addlightness = {self.setting['preset'][self.setting["env"]]['addlightness']}')
        lbl_prominence.config(text=f'prominence = {self.setting['preset'][self.setting["env"]]['prominence']}')

        lbl.pack()
        lbl_addlightness.pack()
        lbl_prominence.pack()
        
        in_lightL = tk.Label(new_window, text='Edit addlightness value')
        in_light = tk.Text(new_window, height=1, width=3)
        in_promL = tk.Label(new_window, text='Edit prominence value')
        in_prom = tk.Text(new_window, height=1, width=3)
        
        if self.setting["env"] == 'custom':
            in_lightL.pack()
            in_light.pack()
            in_promL.pack()
            in_prom.pack()
            in_light.bind("<KeyPress>", on_key_press)
            in_prom.bind("<KeyPress>", on_key_press)

        tk.Button(new_window, text='Confirm', command=confirm).pack()
        check = tk.Label(new_window, text=" ")
        check.pack()
        
    def error_msg(self, title, msg):
        messagebox.showerror(title=title, message=msg)
    
    def warning_msg(self, title, msg):
        messagebox.showwarning(title=title, message=msg)
