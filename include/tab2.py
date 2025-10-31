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
import customtkinter as ctk
from include.Secondary_Button import SecondaryButton


APP_BG= "#f1f8ff"

TEXT_COLOR = "#003366"

class Tab2(ctk.CTkFrame):
    def __init__(self, parent, imageJ: ImageJ, setting, temp_dir):
        super().__init__(parent)
        self.configure(fg_color=APP_BG)

        self.temp_dir = temp_dir
        self.save_Dir = None
        self.setting = setting
        self.settingPath = utils.settingPath()
        self.imageJ = imageJ


        # main container
        self.main_container = ctk.CTkFrame(self,fg_color=APP_BG)
        self.main_container.grid_columnconfigure(0, weight=1, uniform="equal")
        self.main_container.grid_columnconfigure(1, weight=1, uniform="equal")
        self.main_container.grid_rowconfigure(0, weight=0)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(2, weight=1)
        self.main_container.pack(fill="both", expand=True)

        # Left frame layout
        self.left_frame = ctk.CTkFrame(self.main_container, fg_color=APP_BG)
        self.left_frame.grid(row=1, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1)   # image area 
        self.left_frame.grid_rowconfigure(1, weight=0)   # navigation buttons
        self.left_frame.grid_rowconfigure(2, weight=0)   # view original
        self.left_frame.grid_rowconfigure(3, weight=0)   # view counted
        self.left_frame.grid_rowconfigure(3, weight=0)   # count colonies
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.right_frame = ctk.CTkFrame(self.main_container, fg_color="#f1f8ff")
        self.right_frame.grid(row=1, column=1, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)


        # Button frame (centered)
        self.button_frame = ctk.CTkFrame(self.left_frame, fg_color="#f1f8ff")
        #self.button_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="n")
        self.button_frame.grid(row=1, column=0, pady=(0, 10))
        self.button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Image handling variables
        self.img_metadata = []
        self.img_index = 0
        self.canvas_img_id = None
        self.mode: Literal['count', 'dish'] = 'dish'
        self.results = None
        self.init_text_id = None
        self.img_dict_list = None

        self.img_canvas = tk.Canvas(self.left_frame,bg=APP_BG)

        self.img_canvas.grid(row=0, column=0,padx=10, pady=10)
        #self.img_canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.img_canvas.bind("<Configure>", lambda e: self.displayImage())
        self.img_canvas.bind("<Button-1>", self.callback)

        # Image Navigation buttons
        SecondaryButton(self.button_frame, "<<", self.img_idx_back).grid(row=0, column=0, sticky="e", padx=5)
        SecondaryButton(self.button_frame, ">>", self.img_idx_fwd).grid(row=0, column=2, sticky="w", padx=5)


        # Buttons inside
        self.get_img_btn = SecondaryButton(self.left_frame, "View Original Image", self.toggle_image_view)
        self.get_img_btn.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(self.left_frame,font=("Roboto",16,"bold") ,text="Count Colonies", command=self.askReCount,height=40,text_color="white").grid(
            row=4, column=0, padx=10, pady=10, sticky="ew"
        )
        ctk.CTkButton(self.main_container, text="Settings", font=("Roboto",16),width=2, command=self.countSetting,fg_color=APP_BG,hover_color=APP_BG,text_color=TEXT_COLOR).grid(row=0, column=0, sticky="nw")

        # Metadata text area
        self.text_box = ctk.CTkTextbox(self.right_frame,font=("Roboto", 16))
        self.text_box.grid(row=0, column=0, columnspan=5, sticky="nsew")
        self.text_box.configure(state='disabled')

        # Table style
        style = ttk.Style()

        # General row styling
        style.configure(
            "Treeview",
            background="#f1f8ff",
            fieldbackground="#f1f8ff",
            foreground=TEXT_COLOR,
            rowheight=34,              
            font=('Roboto', 14),
            padding=(0, 6)            
        )

        # Header styling
        style.configure(
            "Treeview.Heading",
            background="#82b8fe",
            foreground=TEXT_COLOR,
            font=('Roboto', 12, 'bold'),
            padding=(0, 6)
        )


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

        self.keeptrack = ctk.CTkLabel(self.button_frame, text='X/X')
        self.keeptrack.grid(row=0, column=1, pady=5, padx=5)

        utils.log_message('info', "Tab2 initialized successfully")

    def clear_placeholder(self):
        self.img_canvas.delete("all")
        self.canvas_img_id = None
        self.init_text_id = None
    

    def updateTrackingLabel(self):
        if self.img_dict_list:
            self.keeptrack.configure(text=f"{self.img_index + 1}/{len(self.img_dict_list)}")
        else:
            self.keeptrack.configure(text="X/X")

    def toggle_image_view(self):
        """Toggles between showing the original dish image and the counted image."""
        if self.mode == 'dish':
            if self.img_dict_list and 'count_path' in self.img_dict_list[0] and self.img_dict_list[0]['count_path']:
                self.mode = 'count'
                self.get_img_btn.change_text("View Original Image")
                utils.log_message('info', "Switched to count view.")
            else:
                utils.infoMsg('Info', 'No counted images available. Please run "Count Colonies" first.')
                return
        else:
            self.mode = 'dish'
            self.get_img_btn.change_text("View Counted Image")
            utils.log_message('info', "Switched to original dish view.")
        self.displayImage()


    def askReCount(self):
        """recount"""
        imgDir = utils.getDst(self.save_Dir, self.temp_dir, 'count')
        dataDir = utils.getDst(self.save_Dir, self.temp_dir, 'data')
        if os.listdir(imgDir) != [] and os.listdir(dataDir) != []:
            result = messagebox.askyesnocancel(title='ReCount?', message='Recount(y) no(n)')
            if result is True:
                utils.log_message('info', "User chose to re-run counting process")
                self.getCountImage()
            elif result is False:
                return
        else:
            utils.log_message('debug', "No existing count data found, starting new count")
            self.getCountImage()

    def getCountImage(self):
        """Run ImageJ counting and display results."""
        try:
            if not self.img_dict_list:
                utils.warningMsg('No Images', 'Please upload and process images in Tab 1 first.')
                utils.log_message('warning', "Count operation failed — img_dict_list is empty")
                return

            image_paths_to_count = [d['img_path'] for d in self.img_dict_list]

            imgDir = utils.getDst(self.save_Dir, self.temp_dir, 'count')
            dataDir = utils.getDst(self.save_Dir, self.temp_dir, 'data')

            if image_paths_to_count:
                utils.log_message('info', "Starting counting process using ImageJ")
                results = self.imageJ.laskePesakeLuvut(
                    img_list=image_paths_to_count,
                    setting=self.setting,
                    imgDir=imgDir,
                    dataDir=dataDir
                )
                self.results = results
                self.update_count_paths(imgDir)
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

    def update_count_paths(self, count_dir):
        """Adds the path of the counted image to each dictionary in img_dict_list."""
        for img_dict in self.img_dict_list:
            base_name = os.path.basename(img_dict['img_path'])
            name, ext = os.path.splitext(base_name)
            count_path = os.path.join(count_dir, f"{name}_point_selection.png")
            img_dict['count_path'] = count_path
            
    def updateImage(self, img_dict_list):
        """Refresh image list and display current image"""
        if not img_dict_list:
            self.img_dict_list = []
        else:
            self.img_dict_list = img_dict_list
        # else:
        self.img_index = 0
        self.mode = 'dish' # Default to original view
        self.get_img_btn.change_text("View Counted Image")
        self.after(200, self.displayImage)
   
    def updateTable(self, img_dict_list):
        if not img_dict_list:
            return
        else:
            self.results = []
            for i, n in enumerate(img_dict_list):
                obj = {
                    'row': i,
                    'count': img_dict_list[i]['count'],
                    'img': img_dict_list[i]['img_path']
                    }
                
                self.results.append(obj)
            self.createTable()
            
    

    def getMetaData(self, img_list):
        """Extract metadata from images."""
        try:
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
            self.updateTrackingLabel()

            if not self.img_dict_list:
                self.clear_placeholder()
                self.init_text_id = self.img_canvas.create_text(
                    self.img_canvas.winfo_width() / 2,
                    self.img_canvas.winfo_height() / 2,
                    text="No Image Selected",
                    fill="black",
                    font=('Helvetica 15 bold'),
                    tags="placeholder"
                )
                utils.log_message('debug', "No images found — showing default message")
                return

            # Get current canvas dimensions
            canvas_width = self.img_canvas.winfo_width()
            canvas_height = self.img_canvas.winfo_height()

            # Calculate center coordinates
            center_x = canvas_width / 2
            center_y = canvas_height / 2

            current_dict = self.img_dict_list[self.img_index]

            if self.mode == 'dish':
                imgPath = current_dict['img_path']
            elif self.mode == 'count':
                imgPath = current_dict.get('count_path')
                if not imgPath or not os.path.exists(imgPath):
                    utils.warningMsg("Not Found", "Counted image not found. Please run counting first.")
                    self.mode = 'dish' # Revert to dish mode
                    self.get_img_btn.change_text("View Counted Image")
                    imgPath = current_dict['img_path']

            self.getMetaData([imgPath]) # Pass as a list
            self.img = Image.open(imgPath)
            picsize = canvas_height, canvas_height
            size = self.img.size
            self.img = self.img.resize(utils.best_fit(size, picsize), Image.Resampling.LANCZOS)
            self.photoImg = ImageTk.PhotoImage(self.img)

            
            # Remove "No Image Selected" text if present
            self.img_canvas.delete(self.init_text_id)

            # If first time, create image; otherwise, update position and image
            if self.canvas_img_id is None:
                self.canvas_img_id = self.img_canvas.create_image(center_x, center_y, image=self.photoImg, anchor="center")
                self.init_text_id = None

            else:
                self.img_canvas.coords(self.canvas_img_id, center_x, center_y)
                self.img_canvas.itemconfig(self.canvas_img_id, image=self.photoImg)


            # Display metadata
            self.text_box.configure(state='normal')
            self.text_box.delete("1.0", tk.END)
            self.text = "\n".join(f"{k}: {v}" for k, v in self.img_metadata[self.img_index].items())
            self.text_box.insert(tk.END, self.text)
            self.text_box.configure(state='disabled')
            
            self.updateTrackingLabel()

            utils.log_message('info', f"Displayed image: {imgPath}")
        except Exception as e:
            utils.errorMsg(title='displayImage', msg=f'error displayImage {e}')
            utils.log_message('error', f"Error displaying image: {e}")

    def img_idx_fwd(self):
        """Navigate to the next image."""
        if self.img_dict_list and self.img_index < len(self.img_dict_list) - 1:
            self.img_index += 1
            utils.log_message('debug', f"Switched to next image index: {self.img_index}")
            self.displayImage()

    def img_idx_back(self):
        """Navigate to the previous image."""
        if self.img_dict_list and self.img_index > 0:
            self.img_index -= 1
            utils.log_message('debug', f"Switched to previous image index: {self.img_index}")
            self.displayImage()

    def callback(self, event):
        """Handle image click to open in a new window."""
        utils.log_message('info', "Image canvas clicked — opening viewer")
        self.create_window()

    def create_window(self):
        """Open the current image in a new preview window."""
        if not self.img_dict_list:
            utils.log_message('warning', "Preview requested but no image loaded")
            return None

        current_dict = self.img_dict_list[self.img_index]
        if self.mode == 'dish':
            imgPath = current_dict['img_path']
        else: # 'count'
            imgPath = current_dict.get('count_path', current_dict['img_path'])


        new_window = tk.Toplevel()
        new_window.geometry('800x600')
        new_window.rowconfigure(0, weight=1)
        new_window.columnconfigure(0, weight=1)
        canvas = CanvasImage(new_window, imgPath)
        canvas.grid(row=0, column=0)
        utils.log_message('info', f"Opened new preview window for {imgPath}")

    def createTable(self):
        """Create or refresh table of count results."""
        for item in self.table.get_children():
            self.table.delete(item)

        if not self.results:
            utils.log_message('debug', "createTable called with no results.")
            return

        self.table.tag_configure('oddrow', background='#E8E8E8')
        self.table.tag_configure('evenrow', background='#FFFFFF')
        for i, result in enumerate(self.results):
            value = (result['row'], result['count'], result['img'])
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.table.insert(parent='', index=i, values=value, tags=(tag,))
            self.img_dict_list[i]['count'] = result['count']
        dataDir = utils.getDst(self.save_Dir, self.temp_dir, 'data')
        dst = os.path.join(dataDir, "data.json")
        with open(dst, 'w', encoding='utf-8') as file:
            json.dump(self.img_dict_list, file, ensure_ascii=False, indent=4)
        utils.log_message('info', f"Table updated with {len(self.results)} entries")


    def _update_image_from_dir(self):
        """Refresh image list based on save directory."""
        if self.save_Dir is not None:
            self.displayImage()
            utils.log_message('debug', f"Updated image list from {dst}")

    def update_save_Dir(self, save_Dir):
        """Update save directory and refresh image view."""
        self.save_Dir = save_Dir
        utils.log_message('debug', f"Updated save directory: {self.save_Dir}")
        if self.save_Dir is not None:
            self.displayImage()
  
    def update_temp_Dir(self, temp_dir):
        """Update save directory and refresh images"""
        self.temp_dir = temp_dir
        utils.log_message('debug', f"Updated temp directory: {self.temp_dir}")
        if self.temp_dir is not None:
            self.img_dict_list = []
            self.results = []
            self.createTable()
            self.displayImage()
            # empty meta
            self.text_box.configure(state='normal')
            self.text_box.delete("1.0", tk.END)
            self.text_box.configure(state='disabled')

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
            lbl.configure(text=result)
            lbl_addlightness.configure(text=f"addlightness = {self.setting['preset'][result]['addlightness']}")
            lbl_prominence.configure(text=f"prominence = {self.setting['preset'][result]['prominence']}")
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
            lbl.configure(text=result)
            check.configure(text='saved*')
            lbl_addlightness.configure(text=f"addlightness = {self.setting['preset'][result]['addlightness']}")
            lbl_prominence.configure(text=f"prominence = {self.setting['preset'][result]['prominence']}")
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
