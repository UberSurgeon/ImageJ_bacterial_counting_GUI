import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
from tkinter import ttk
from include.imageViewer import CanvasImage
from include.tab2 import Tab2
import include.utils as utils


class Tab1(tk.Frame):
    def __init__(self, parent, save_Dir, tab2: Tab2, temp_dir):
        super().__init__(parent)
        ttk.Frame.__init__(self, master=parent)

        self.tab2 = tab2
        self.temp_dir = temp_dir
        self.save_Dir = save_Dir

        self.img_list = []
        self.img_index = 0

        # Configure layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Canvas for image display
        self.img_canvas = tk.Canvas(self, width=500, height=500)
        self.init_text_id = self.img_canvas.create_text(
            100, 50,
            text="No Image Selected",
            fill="black", font=('Helvetica 15 bold')
        )
        self.img_canvas.bind("<Button-1>", self.callback)
        self.img_canvas.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

        self.canvas_img_id = None

        # Buttons
        button_back = tk.Button(self, text="<<", command=self.img_idx_back)
        button_fwd = tk.Button(self, text=">>", command=self.img_idx_fwd)
        button_upload = tk.Button(self, text="Upload", command=self.openFile)
        button_del = tk.Button(self, text='remove image', command=self.delImage)

        button_back.grid(row=2, column=0, sticky=tk.NSEW)
        button_upload.grid(row=2, column=1, sticky=tk.NSEW)
        button_fwd.grid(row=2, column=2, sticky=tk.NSEW)
        button_del.grid(row=3, column=1, sticky=tk.NSEW)
        
        self.bind_all("<Left>", lambda event: self.img_idx_back())
        self.bind_all("<Right>", lambda event: self.img_idx_fwd())

        utils.log_message('info', "Tab1 initialized successfully")

    def updateImage(self):
        """Refresh image list and display current image"""
        if self.save_Dir is not None:
            try:
                self.img_list = []
                dst = utils.getDst(self.save_Dir, self.temp_dir, 'raw')
                for filename in os.listdir(dst):
                    path = os.path.normpath(os.path.join(dst, filename))
                    self.img_list.append(path)
                utils.log_message('debug', f"Updated image list: {self.img_list}")
                self.displayImage()
            except Exception as e:
                utils.errorMsg(title='updateImage', msg=f'error in updateImage {e}')
                utils.log_message('error', f"Failed to update images: {e}")

    def openFile(self):
        """Open file dialog and upload selected images"""
        dst = utils.getDst(self.save_Dir, self.temp_dir, 'raw')
        try:
            filepath = filedialog.askopenfiles(
                initialdir='gui',
                title='select images',
                filetypes=[("all files", "*.*")]
            )
            for file in filepath:
                shutil.copy2(str(file.name), dst)
                utils.log_message('info', f"Copied image: {file.name} to {dst}")

            # Refresh image list
            self.img_list = []
            for filename in os.listdir(dst):
                path = os.path.normpath(os.path.join(dst, filename))
                self.img_list.append(path)

            utils.log_message('debug', f"Loaded image list: {self.img_list}")

            # Display and update tab2
            self.displayImage()
            self.tab2.mode = 'raw'
            self.tab2.displayImage()
            utils.log_message('info', "Displayed uploaded images successfully")

        except Exception as e:
            utils.errorMsg(title='openFile', msg=f'error during openFile {e}')
            utils.log_message('error', f"Error opening or copying files: {e}")

    def delImage(self):
        """Delete currently displayed image"""
        if not self.img_list:
            utils.log_message('warning', "Delete image attempted with empty list")
            return

        imgPath = self.img_list[self.img_index]

        if os.path.exists(imgPath):
            if messagebox.askokcancel(
                title='delImage',
                message='Are you sure you want to remove this image? T-T'
            ):
                try:
                    os.remove(imgPath)
                    utils.log_message('info', f"Deleted image: {imgPath}")
                    del self.img_list[self.img_index]
                    self.img_index = max(0, self.img_index - 1)
                    messagebox.showinfo(title='delImage', message='image removed')

                    # Refresh views
                    self.displayImage()
                    self.tab2.img_index = self.img_index
                    self.tab2.displayImage()
                except Exception as e:
                    utils.errorMsg('delImage', f'Failed to delete {imgPath}: {e}')
                    utils.log_message('error', f"Failed to delete image {imgPath}: {e}")
        else:
            utils.errorMsg('delImage', 'Image does not exist')
            utils.log_message('warning', f"Tried to delete non-existent image: {imgPath}")

    def displayImage(self):
        """Display image on canvas"""
        if not self.img_list:
            self.img_canvas.delete(self.canvas_img_id)
            self.canvas_img_id = None
            self.init_text_id = self.img_canvas.create_text(
                100, 50, text="No Image Selected", fill="black", font=('Helvetica 15 bold')
            )
            utils.log_message('debug', "No image selected — showing default text")
            return None

        try:
            imgPath = self.img_list[self.img_index]
            self.img = Image.open(imgPath)
            picsize = 500, 500
            size = self.img.size
            self.img = self.img.resize(utils.best_fit(size, picsize), Image.Resampling.LANCZOS)
            self.photoImg = ImageTk.PhotoImage(self.img)

            if self.canvas_img_id is None:
                self.img_canvas.delete(self.init_text_id)
                self.canvas_img_id = self.img_canvas.create_image(
                    250, 250, image=self.photoImg, anchor="center"
                )
            else:
                self.img_canvas.itemconfig(self.canvas_img_id, image=self.photoImg)

            utils.log_message('info', f"Displayed image: {imgPath}")

        except Exception as e:
            utils.errorMsg(title='displayImage', msg=f'error in displayImage {e}')
            utils.log_message('error', f"Error displaying image: {e}")

    def img_idx_fwd(self):
        """Go to next image in list"""
        if self.img_index < len(self.img_list) - 1:
            self.img_index += 1
            utils.log_message('debug', f"Switched to next image index: {self.img_index}")
            self.displayImage()

    def img_idx_back(self):
        """Go to previous image in list"""
        if self.img_index > 0:
            self.img_index -= 1
            utils.log_message('debug', f"Switched to previous image index: {self.img_index}")
            self.displayImage()

    def callback(self, event):
        """Handle image click — open preview window"""
        utils.log_message('info', "Canvas clicked — opening image viewer")
        self.create_window()

    def create_window(self):
        """Open image in separate preview window"""
        if not self.img_list:
            utils.log_message('warning', "Preview requested but image list empty")
            return None

        imgPath = self.img_list[self.img_index]
        new_window = tk.Toplevel()
        new_window.geometry('800x600')
        new_window.rowconfigure(0, weight=1)
        new_window.columnconfigure(0, weight=1)
        canvas = CanvasImage(new_window, imgPath)
        canvas.grid(row=0, column=0)
        utils.log_message('info', f"Opened new window for image: {imgPath}")

    def update_save_Dir(self, save_Dir):
        """Update save directory and refresh images"""
        self.save_Dir = save_Dir
        utils.log_message('debug', f"Updated save directory: {self.save_Dir}")
        if self.save_Dir is not None:
            self.updateImage()
   
    def update_temp_Dir(self, temp_dir):
        """Update save directory and refresh images"""
        self.temp_dir = temp_dir
        utils.log_message('debug', f"Updated temp directory: {self.temp_dir}")
        if self.temp_dir is not None:
            self.updateImage()
            self.img_list = []
            self.displayImage()
