import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
from tkinter import ttk
from include.imageViewer import CanvasImage
import include.utils as utils
import regex as re
from collections import Counter
import customtkinter as ctk
from include.Secondary_Button import SecondaryButton


APP_BG= "#f1f8ff"

TEXT_COLOR = "#003366"

class Tab1_1(ctk.CTkFrame):
    def __init__(self, parent, save_Dir, temp_dir, windows):
        super().__init__(parent)
        ctk.CTkFrame.__init__(self, master=parent)
        self.configure(fg_color=APP_BG)

        self.windows = windows
        self.temp_dir = temp_dir
        self.save_Dir = save_Dir


        self.img_dict_list = []
        self.img_list = []
        self.img_index = 0

        self.canvas_img_id = None
        self.canvas_label_id = None
        # Configure layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=4)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)


        #canvas container
        self.canvas_frame = ctk.CTkFrame(self, fg_color=APP_BG)
        self.canvas_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(1, weight=1)
        
        # Canvas for image display
        self.img_canvas = tk.Canvas(self.canvas_frame)
        self.init_text_id = self.img_canvas.create_text(
            100, 50,
            text="No Image Selected",
            fill="black", font=('Roboto 15 bold')
        )
        
        #self.img_canvas.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)
        self.img_canvas.update_idletasks()

        self.img_canvas.grid(
            row=0, column=0, columnspan=3,
            sticky="nsew", 
            padx=(0, 0), pady=(10, 10)
        )

        self.img_canvas.bind("<Configure>", self.on_canvas_resize)
        self.img_canvas.bind("<Button-1>", self.create_window_img)


        self.label_canvas = tk.Canvas(self.canvas_frame, width=500, height=500)
        self.init_text_id2 = self.label_canvas.create_text(
            100, 50,
            text="No Image Selected",
            fill="black", font=('Roboto 15 bold')
        )
        self.label_canvas.grid(
            row=1, column=0, columnspan=3,
            sticky="nsew",
            padx=(10, 10), pady=(10, 10)
        )

        self.label_canvas.bind("<Button-1>", self.create_window_label)
        self.label_canvas.bind("<Configure>", self.on_canvas_resize)
        self.label_canvas.grid(row=1, column=0, columnspan=3, sticky="nsew")

        # Buttons
        button_back = SecondaryButton(self, "<<", command=self.img_idx_back)
        button_fwd = SecondaryButton(self, ">>", command=self.img_idx_fwd)
        button_del = SecondaryButton(self, "Remove image", command=self.delImage)

        button_back.grid(row=2, column=0, sticky="ew",padx=5,pady=5)
        button_fwd.grid(row=2, column=2, sticky="ew",padx=5,pady=5)
        button_del.grid(row=2, column=1, sticky="ew",padx=5,pady=5)


        self.fileNameLabel = ctk.CTkLabel(self, text='no image select',font=("Roboto",18))


        self.nameText = ctk.CTkTextbox(
            self,
            height=25,  
            width=200,
            border_color=TEXT_COLOR,
            border_width=2,
            fg_color="#FFFFFF",
            text_color="gray",  # placeholder color
            corner_radius=6,
        )

        self.nameText.grid(row=3, column=0, sticky="nsew", padx=10,pady=5)

        # Placeholder text
        self.placeholder = "Enter your name..."
        self.nameText.insert("1.0", self.placeholder)

        # self.nameText.bind("<KeyRelease>", self.on_key_release)
        self.nameText.bind("<FocusIn>", self.on_focus_in)
        self.nameText.bind("<FocusOut>", self.on_focus_out)
        self.nameText.bind("<KeyRelease>", self.on_key_release)

        self.confidenceLabel = ctk.CTkLabel(self, text='',font=("Roboto",18))

        self.confirm = ctk.CTkButton(self, text="Done", command=self.on_confirm,height=40,font=("Roboto",16,"bold"))

        #self.nameLabel.grid(row=3, column=0, sticky=tk.NSEW)
        self.nameText.grid(row=3, column=1, sticky="ew",padx=10,pady=5)
        self.fileNameLabel.grid(row=3, column=0, sticky="ew",padx=10,pady=5)
        self.confirm.grid(row=4, column=1, sticky="ew",padx=10,pady=5)
        self.confidenceLabel.grid(row=3, column=2, sticky="ew",pady=5,padx=10)

        # self.displayImage()
        self.keeptrack = ctk.CTkLabel(self, text='X/X',fg_color=APP_BG,font=("Roboto",16))
        self.keeptrack.grid(row=1, column=1, sticky="ew",padx=5,pady=5)

        utils.log_message('info', "Tab1_1 initialized successfully")

    def on_canvas_resize(self, event):
        canvas = event.widget
        width, height = event.width, event.height

        # Resize main image
        if canvas == self.img_canvas and hasattr(self, 'img') and self.canvas_img_id:
            resized_img = self.img.resize(utils.best_fit(self.img.size, (width, height)), Image.Resampling.LANCZOS)
            self.photoImg = ImageTk.PhotoImage(resized_img)
            self.img_canvas.itemconfig(self.canvas_img_id, image=self.photoImg)
            self.img_canvas.coords(self.canvas_img_id, width // 2, height // 2)

        # Resize label image (smaller than main image)
        elif canvas == self.label_canvas and hasattr(self, 'label') and self.canvas_label_id:
            label_w = int(width * 0.8)
            label_h = int(height * 0.8)
            resized_label = self.label.resize(utils.best_fit(self.label.size, (label_w, label_h)), Image.Resampling.LANCZOS)
            self.photoLabel = ImageTk.PhotoImage(resized_label)
            self.label_canvas.itemconfig(self.canvas_label_id, image=self.photoLabel)
            self.label_canvas.coords(self.canvas_label_id, width // 2, height // 2)

        # Center placeholder text if no image
        elif canvas == self.img_canvas and not self.canvas_img_id:
            canvas.coords(self.init_text_id, width // 2, height // 2)
        elif canvas == self.label_canvas and not self.canvas_label_id:
            canvas.coords(self.init_text_id2, width // 2, height // 2)

    def _resize_and_center(self, canvas, original_img, canvas_id, width, height, is_label=False):
        """Resize image proportionally to fit canvas and center it."""
        # Compute new size with aspect ratio
        target_size = (width, height)
        new_size = utils.best_fit(original_img.size, target_size)
        resized_img = original_img.resize(new_size, Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(resized_img)

        if not is_label:
            self.photoImg = tk_img
        else:
            self.photoLabel = tk_img

        # Update canvas image
        canvas.itemconfig(canvas_id, image=tk_img)
        canvas.coords(canvas_id, width // 2, height // 2)

    def on_focus_in(self,event):
        current = self.nameText.get("1.0", "end-1c")
        if current == self.placeholder:
            self.nameText.delete("1.0", "end")
            self.nameText.configure(text_color=TEXT_COLOR)

    def on_focus_out(self,event):
        current = self.nameText.get("1.0", "end-1c").strip()
        if not current:
            self.nameText.insert("1.0", self.placeholder)
            self.nameText.configure(text_color="gray")

    def on_key_release(self,event):
        print("Typed:", self.nameText.get("1.0", "end-1c"))
        
    def updateTrackingLabel(self):
        if self.img_dict_list:
            self.keeptrack.configure(text=f"{self.img_index + 1}/{len(self.img_dict_list)}")
        else:
            self.keeptrack.configure(text="X/X")
    def center_placeholder(self, event):
        """Center the placeholder text in the label canvas."""

        self.canvas = event.widget
        self.canvas.delete("all")

        self.canvas.create_text(
            event.width // 2,
            event.height // 2,
            text="No Image Selected",
            fill="black",
            font=('Roboto 15 bold')
        )

    def updateImage(self, img_dict_list):
        """Refresh image list and display current image"""
        if not img_dict_list:
            self.img_dict_list = []
        else:
            self.img_dict_list = img_dict_list
        # else:
        #     self.img_dict_list.append(img_dict_list)
        self.img_index = 0
        # print(self.img_dict_list)
        self.after(200, self.displayImage)
        self.after(200, self.on_img_change)



    def delImage(self):
        """Delete currently displayed image"""
        if not self.img_dict_list:
            utils.log_message('warning', "Delete image attempted with empty list")
            return

        imgPath = self.img_dict_list[self.img_index]['img_path']
        labelPath = self.img_dict_list[self.img_index]['label_path']

        if os.path.exists(imgPath):
            if messagebox.askokcancel(
                title='delImage',
                message='Are you sure you want to remove this image? T-T'
            ):
                try:
                    # os.remove(imgPath)
                    # os.remove(labelPath)
                    utils.log_message('info', f"Deleted image: {imgPath}")
                    del self.img_dict_list[self.img_index]
                    self.img_index = max(0, self.img_index - 1)
                    os.remove(imgPath)
                    os.remove(labelPath)
                    messagebox.showinfo(title='delImage', message='image removed')

                    # Refresh views
                    self.displayImage()
                    self.windows.update_img()
                    # self.tab2.img_index = self.img_index
                    # self.tab2.displayImage()
                except Exception as e:
                    utils.errorMsg('delImage', f'Failed to delete {imgPath}: {e}')
                    utils.log_message('error', f"Failed to delete image {imgPath}: {e}")
        else:
            utils.errorMsg('delImage', 'Image does not exist')
            utils.log_message('warning', f"Tried to delete non-existent image: {imgPath}")

    def on_img_change(self):
        self.nameText.delete("1.0", tk.END)
        #test
        if not self.img_dict_list:
            return
        if self.img_dict_list[self.img_index]['name'] == "":
            text = self.img_dict_list[self.img_index]['prediction']
            self.img_dict_list[self.img_index]['name'] = self.img_dict_list[self.img_index]['prediction']
        else:
            text = self.img_dict_list[self.img_index]['name']
        self.confidenceLabel.configure(text=f'confidence={self.img_dict_list[self.img_index]["confidence"]}')
        self.nameText.insert(tk.END, text)

    def on_confirm(self):
        if not self.img_dict_list:
            utils.infoMsg('confirm', 'there no image loaded')
            return
        if messagebox.askokcancel(title='done?', message='Do you want to rename?'):
            print(self.img_dict_list)
            try:
                dupeCheck = Counter([i['name'] for i in self.img_dict_list]).most_common()[0]
                if dupeCheck[1] > 1 and dupeCheck[0] != '':
                    raise ValueError(f"no dupe allow name: {dupeCheck[0]} amount: {dupeCheck[1]}")
                else:
                    for img_dict in self.img_dict_list:
                        oldPathM = img_dict['img_path']
                        oldPathL = img_dict['label_path']
                        if os.path.exists(oldPathM):
                            if img_dict['name'] != '':
                                dirNameM = os.path.dirname(oldPathM)
                                dirNameL = os.path.dirname(oldPathL)
                                extM = os.path.splitext(oldPathM)[1]
                                extL = os.path.splitext(oldPathL)[1]
                                newPathM = os.path.join(dirNameM, img_dict['name'] + extM)
                                newPathL = os.path.join(dirNameL, img_dict['name'] + extL)
                                os.rename(oldPathM, newPathM)
                                os.rename(oldPathL, newPathL)
                                img_dict['img_path'] = newPathM
                                img_dict['label_path'] = newPathL
                                print(f'changing {oldPathM} to {newPathM}')
                                print(f'changing {oldPathL} to {newPathM}')
                    self.windows.update_img()
                    self.windows.change_tab('Count')
            except Exception as e:
                utils.errorMsg('rename', f'error - {e}')
                
                        
            # print(self.img_dict_list)


    def on_key_release(self, event):
        """Automatically update name on every key release."""
        text = self.nameText.get("1.0", "end-1c")  # get text without trailing newline
        pattern = r"^[a-zA-Z0-9]*$"  # allow only alphanumeric

        # If invalid char typed, remove it
        if not re.fullmatch(pattern, text):
            # remove last invalid character
            self.nameText.delete("1.0", "end")
            cleaned = re.sub(r"[^a-zA-Z0-9]", "", text)
            self.nameText.insert("1.0", cleaned)
            text = cleaned

        # Update the name in your image dictionary
        self.img_dict_list[self.img_index]["name"] = text
    

    def displayImage(self):
        """Display image on canvas"""

        # If no images, show placeholder
        if not self.img_dict_list:
            self.updateTrackingLabel()
            self.img_canvas.delete("all")
            self.label_canvas.delete("all")
            self.canvas_img_id = None
            self.canvas_label_id = None
            self.init_text_id = self.img_canvas.create_text(
                self.img_canvas.winfo_width() / 2,
                self.img_canvas.winfo_height() / 2,
                text="No image selected",
                fill="Black",
                font=("Roboto", 16, "bold")
            )
            self.init_text_id2 = self.label_canvas.create_text(
                self.label_canvas.winfo_width() / 2,
                self.label_canvas.winfo_height() / 2,
                text="No image selected",
                fill="Black",
                font=("Roboto", 16, "bold")
            )
            return

        # Remove placeholder text before showing new image
        self.img_canvas.delete("all")
        self.label_canvas.delete("all")

        # Get canvas sizes
        canvas_width = self.img_canvas.winfo_width()
        canvas_height = self.img_canvas.winfo_height()
        label_width = self.label_canvas.winfo_width()
        label_height = self.label_canvas.winfo_height()

        # Retry if canvas sizes not ready
        if (canvas_width < 100 or canvas_height < 100 or label_width < 100 or label_height < 100):
            self.after(100, self.displayImage)
            return

        # Load images
        img_dict = self.img_dict_list[self.img_index]
        self.img = Image.open(img_dict["img_path"])

        # Resize and convert to Tkinter image
        self.img = self.img.resize(utils.best_fit(self.img.size, (canvas_width, canvas_height)), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas_img_id = self.img_canvas.create_image(
            canvas_width / 2, canvas_height / 2, image=self.tk_img
        )

        # Display label if available
        try:
            if "label_path" in img_dict:
                if img_dict["label_path"] == "":
                    self.label = Image.open(utils.imgPath('300px-Debugempty.png'))
                else:
                    self.label = Image.open(img_dict["label_path"])
                self.label = self.label.resize(
                    utils.best_fit(self.label.size, (max(int(label_width * 0.8), 1), max(int(label_height * 0.8), 1))),
                    Image.Resampling.LANCZOS
                )
                self.tk_label = ImageTk.PhotoImage(self.label)
                self.canvas_label_id = self.label_canvas.create_image(
                    label_width / 2, label_height / 2, image=self.tk_label
                )
        except Exception as e:
            print(f'width {int(label_width * 0.8)}')
            print(f'height {int(label_height * 0.8)}')
            print(f'exception  {e}')

        # Update filename + tracking info
        self.fileNameLabel.configure(text=os.path.basename(img_dict["img_path"]))
        self.updateTrackingLabel()


    def img_idx_fwd(self, event=None):
        """Go to next image in list"""
        if self.img_index < len(self.img_dict_list) - 1:
            self.img_index += 1
            utils.log_message('debug', f"Switched to next image index: {self.img_index}")
            self.on_img_change()
            self.displayImage()

    def img_idx_back(self, event=None):
        """Go to previous image in list"""
        if self.img_index > 0:
            self.img_index -= 1
            utils.log_message('debug', f"Switched to previous image index: {self.img_index}")
            self.on_img_change()
            self.displayImage()

    def create_window_img(self, event):
        """Open image in separate preview window"""
        if not self.img_dict_list:
            utils.log_message('warning', "Preview requested but image list empty")
            return None

        imgPath = self.img_dict_list[self.img_index]['img_path']
        new_window = tk.Toplevel()
        new_window.geometry('800x600')
        new_window.rowconfigure(0, weight=1)
        new_window.columnconfigure(0, weight=1)
        canvas = CanvasImage(new_window, imgPath)
        canvas.grid(row=0, column=0)
        utils.log_message('info', f"Opened new window for image: {imgPath}")

    def create_window_label(self, event):
        """Open image in separate preview window"""
        if not self.img_dict_list:
            utils.log_message('warning', "Preview requested but image list empty")
            return None

        labelPath = self.img_dict_list[self.img_index]['label_path']
        new_window = tk.Toplevel()
        new_window.geometry('800x600')
        new_window.rowconfigure(0, weight=1)
        new_window.columnconfigure(0, weight=1)
        canvas = CanvasImage(new_window, labelPath)
        canvas.grid(row=0, column=0)
        utils.log_message('info', f"Opened new window for image: {labelPath}")

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
