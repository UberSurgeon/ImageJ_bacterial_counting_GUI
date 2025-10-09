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

        # Left and right frames
        self.left_frame = tk.Frame(self, width=200, height=400)
        self.left_frame.grid(row=0, column=0)
        self.right_frame = tk.Frame(self, width=200, height=400)
        self.right_frame.grid(row=0, column=1)

        # Image handling variables
        self.img_list = []
        self.img_metadata = []
        self.img_index = 0
        self.canvas_img_id = None
        self.mode: Literal['raw', 'count'] = 'raw'
        self.results = None

        # Canvas for displaying thumbnails
        self.img_canvas = tk.Canvas(self.left_frame, width=200, height=200)
        self.init_text_id = self.img_canvas.create_text(
            100, 50,
            text="No Image Selected",
            fill="black", font=('Helvetica 15 bold')
        )
        self.img_canvas.grid(row=0, column=0, columnspan=3)
        self.img_canvas.bind("<Button-1>", self.callback)

        # Navigation buttons
        tk.Button(self.left_frame, text="<<", command=self.img_idx_back).grid(row=1, column=0)
        tk.Button(self.left_frame, text=">>", command=self.img_idx_fwd).grid(row=1, column=1)
        
        self.bind_all("<Left>", lambda event: self.img_idx_back())
        self.bind_all("<Right>", lambda event: self.img_idx_fwd())

        # Toolbar with tools
        self.tool_bar = tk.Frame(self.left_frame, width=180, height=185, bg='grey')
        self.tool_bar.grid(row=2, column=0)
        tk.Label(self.tool_bar, text='Tools', relief='raised').grid(row=0, column=0)
        tk.Button(self.tool_bar, text="raw", command=self.getRawImage, width=10).grid(row=2, column=0, padx=5, pady=5, sticky=tk.NSEW)
        tk.Button(self.tool_bar, text="count", command=self.askReCount, width=8).grid(row=3, column=0, padx=5, pady=5, sticky=tk.NSEW)
        tk.Button(self.tool_bar, text=":", width=2, command=self.countSetting).grid(row=3, column=1, padx=5, pady=5, sticky=tk.NSEW)

        # Metadata text area
        self.text_box = tk.Text(self.right_frame, height=10, width=70)
        self.text_box.grid(row=0, column=0, columnspan=5)
        self.text_box.config(state='disabled')

        # Table for image data
        self.table = ttk.Treeview(self.right_frame)
        self.table['columns'] = ('row', 'count', 'path')

        # Configure columns
        self.table.column('#0', width=0, stretch=tk.NO)
        self.table.column('row', anchor=tk.W, width=150)
        self.table.column('count', anchor=tk.W, width=200)
        self.table.column('path', anchor=tk.W, width=150)
        self.table.heading('#0', text='', anchor=tk.W)
        self.table.heading('row', text='row', anchor=tk.W)
        self.table.heading('count', text='count', anchor=tk.W)
        self.table.heading('path', text='path', anchor=tk.W)
        self.table.grid(row=1, column=0, sticky='nsew')

        # Scrollbars
        vsb = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.table.yview)
        vsb.grid(row=1, column=1, sticky='ns')
        hsb = ttk.Scrollbar(self.right_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        hsb.grid(row=2, column=0, columnspan=2, sticky='ew')
        self.table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        

        utils.log_message('info', "Tab2 initialized successfully")

    def getRawImage(self):
        """Load raw images from directory and display them."""
        try:
            dst = utils.getDst(self.save_Dir, self.temp_dir, 'raw')
            self.img_list = [os.path.normpath(os.path.join(dst, f)) for f in os.listdir(dst)]
            if self.img_list:
                self.mode = 'raw'
                self.results = []
                self.createTable()
                self.displayImage()
                utils.log_message('info', f"Loaded raw images: {len(self.img_list)} found")
            else:
                utils.warningMsg('no image loaded', 'no image loaded to temp')
                utils.log_message('warning', "No raw images found in directory")
        except Exception as e:
            utils.errorMsg(title='getRawImage', msg=f'error getRawImage {e}')
            utils.log_message('error', f"Error loading raw images: {e}")

    def askReCount(self):
        """Ask user if they want to recount or display previous results."""
        imgDir = utils.getDst(self.save_Dir, self.temp_dir, 'count')
        dataDir = utils.getDst(self.save_Dir, self.temp_dir, 'data')
        if os.listdir(imgDir) != [] and os.listdir(dataDir) != []:
            result = messagebox.askyesnocancel(title='ReCount?', message='Recount(y) or Display image?(n)')
            if result is True:
                utils.log_message('info', "User chose to re-run counting process")
                self.getCountImage()
            elif result is False:
                with open(os.path.join(dataDir, 'data.json'), 'r') as file:
                    self.results = json.load(file)
                self.createTable()
                self.mode = 'count'
                self.displayImage()
                utils.log_message('info', "Displayed previous count results")
        else:
            utils.log_message('debug', "No existing count data found, starting new count")
            self.getCountImage()

    def getCountImage(self):
        """Run ImageJ counting and display results."""
        try:
            dst = utils.getDst(self.save_Dir, self.temp_dir, 'raw')
            imgDir = utils.getDst(self.save_Dir, self.temp_dir, 'count')
            dataDir = utils.getDst(self.save_Dir, self.temp_dir, 'data')

            self.img_list = [os.path.normpath(os.path.join(dst, f)) for f in os.listdir(dst)]
            if self.img_list:
                utils.log_message('info', "Starting counting process using ImageJ")
                results = self.imageJ.laskePesakeLuvut(
                    img_list=self.img_list,
                    setting=self.setting,
                    imgDir=imgDir,
                    dataDir=dataDir
                )
                self.results = results
                self.createTable()
                utils.log_message('info', f"Counting completed successfully — {len(results)} results")
                self.mode = 'count'
                self.displayImage()
            else:
                utils.warningMsg('no image loaded', 'no image loaded')
                utils.log_message('warning', "Count operation failed — no images loaded")
        except Exception as e:
            utils.errorMsg(title='getCountImage', msg=f'error getCountImage {e}')
            utils.log_message('error', f"Error in getCountImage: {e}")

    def getMetaData(self, img_list):
        """Extract metadata from images."""
        try:
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
                self.img_metadata.append(info_dict)
            utils.log_message('debug', f"Extracted metadata for {len(self.img_metadata)} images")
        except Exception as e:
            utils.errorMsg(title='getMetaData', msg=f'error getMetaData {e}')
            utils.log_message('error', f"Error extracting metadata: {e}")

    def displayImage(self):
        """Display the current image and metadata."""
        try:
            dst = utils.getDst(self.save_Dir, self.temp_dir, self.mode)
            self.img_list = [os.path.normpath(os.path.join(dst, f)) for f in os.listdir(dst)]
            if not self.img_list:
                self.img_canvas.delete(self.canvas_img_id)
                self.canvas_img_id = None
                self.init_text_id = self.img_canvas.create_text(
                    100, 50, text="No Image Selected", fill="black", font=('Helvetica 15 bold')
                )
                utils.log_message('debug', "No images found — showing default message")
                return None

            self.getMetaData(self.img_list)
            imgPath = self.img_list[self.img_index]
            self.img = Image.open(imgPath)
            picsize = 200, 200
            size = self.img.size
            self.img = self.img.resize(utils.best_fit(size, picsize), Image.Resampling.LANCZOS)
            self.photoImg = ImageTk.PhotoImage(self.img)

            if self.canvas_img_id is None:
                self.img_canvas.delete(self.init_text_id)
                self.canvas_img_id = self.img_canvas.create_image(100, 100, image=self.photoImg, anchor="center")
            else:
                self.img_canvas.itemconfig(self.canvas_img_id, image=self.photoImg)

            # Display metadata
            self.text_box.config(state='normal')
            self.text_box.delete("1.0", tk.END)
            self.text = "\n".join(f"{k}: {v}" for k, v in self.img_metadata[self.img_index].items())
            self.text_box.insert(tk.END, self.text)
            self.text_box.config(state='disabled')

            utils.log_message('info', f"Displayed image: {imgPath}")
        except Exception as e:
            utils.errorMsg(title='displayImage', msg=f'error displayImage {e}')
            utils.log_message('error', f"Error displaying image: {e}")

    def img_idx_fwd(self):
        """Navigate to the next image."""
        if self.img_index < len(self.img_list) - 1:
            self.img_index += 1
            utils.log_message('debug', f"Switched to next image index: {self.img_index}")
            self.displayImage()

    def img_idx_back(self):
        """Navigate to the previous image."""
        if self.img_index > 0:
            self.img_index -= 1
            utils.log_message('debug', f"Switched to previous image index: {self.img_index}")
            self.displayImage()

    def callback(self, event):
        """Handle image click to open in a new window."""
        utils.log_message('info', "Image canvas clicked — opening viewer")
        self.create_window()

    def create_window(self):
        """Open the current image in a new preview window."""
        if not self.img_list:
            utils.log_message('warning', "Preview requested but no image loaded")
            return None
        imgPath = self.img_list[self.img_index]
        new_window = tk.Toplevel()
        new_window.geometry('800x600')
        new_window.rowconfigure(0, weight=1)
        new_window.columnconfigure(0, weight=1)
        canvas = CanvasImage(new_window, imgPath)
        canvas.grid(row=0, column=0)
        utils.log_message('info', f"Opened new preview window for {imgPath}")

    def createTable(self):
        """Create or refresh table of count results."""
        self.table.tag_configure('oddrow', background='#E8E8E8')
        self.table.tag_configure('evenrow', background='#FFFFFF')
        for item in self.table.get_children():
            self.table.delete(item)
        for i, result in enumerate(self.results):
            value = (result['row'], result['count'], result['img'])
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.table.insert(parent='', index=i, values=value, tags=(tag,))
        utils.log_message('info', f"Table updated with {len(self.results)} entries")

    def updateImage(self):
        """Refresh image list based on save directory."""
        if self.save_Dir is not None:
            self.img_list = []
            dst = os.path.join(self.save_Dir, 'raw')
            for filename in os.listdir(dst):
                path = os.path.normpath(os.path.join(dst, filename))
                self.img_list.append(path)
            self.displayImage()
            utils.log_message('debug', f"Updated image list from {dst}")

    def update_save_Dir(self, save_Dir):
        """Update save directory and refresh image view."""
        self.save_Dir = save_Dir
        utils.log_message('debug', f"Updated save directory: {self.save_Dir}")
        if self.save_Dir is not None:
            self.updateImage()

    def update_setting(self, setting):
        """Save new settings to file."""
        self.setting = setting
        try:
            with open(self.settingPath, 'w') as file:
                json.dump(self.setting, file, indent=4)
            utils.log_message('info', "Settings file updated successfully")
        except Exception as e:
            utils.errorMsg(title='update_setting', msg=f'error update_setting {e}')
            utils.log_message('error', f"Failed to update setting file: {e}")

    def countSetting(self):
        """Open configuration window for counting settings."""
        new_window = tk.Toplevel()
        new_window.geometry('200x250')
        modes = list(self.setting['preset'].keys())
        utils.log_message('info', "Opened count settings window")

        def on_key_press(event):
            if event.char.isdigit() or event.keysym == "BackSpace":
                return
            return "break"

        def show(event):
            result = opt.get()
            lbl.config(text=result)
            lbl_addlightness.config(text=f"addlightness = {self.setting['preset'][result]['addlightness']}")
            lbl_prominence.config(text=f"prominence = {self.setting['preset'][result]['prominence']}")
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
                light = in_light.get("1.0", "end-1c") or 0
                prom = in_prom.get("1.0", "end-1c") or 0
                self.setting['preset'][result]['addlightness'] = light
                self.setting['preset'][result]['prominence'] = prom
                in_light.delete("1.0", "end")
                in_prom.delete("1.0", "end")
            lbl.config(text=result)
            check.config(text='saved*')
            lbl_addlightness.config(text=f"addlightness = {self.setting['preset'][result]['addlightness']}")
            lbl_prominence.config(text=f"prominence = {self.setting['preset'][result]['prominence']}")
            self.setting["env"] = result
            self.update_setting(self.setting)
            utils.log_message('info', f"Updated counting preset: {result}")

        opt = tk.StringVar(value=self.setting["env"])
        tk.Label(new_window, text='Select mode').pack()
        tk.OptionMenu(new_window, opt, *modes, command=show).pack()

        lbl = tk.Label(new_window, text=" ")
        lbl_addlightness = tk.Label(new_window, text=" ")
        lbl_prominence = tk.Label(new_window, text=" ")
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
