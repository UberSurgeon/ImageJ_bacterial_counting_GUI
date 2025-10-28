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


class Tab1_1(tk.Frame):
    def __init__(self, parent, save_Dir, temp_dir, windows):
        super().__init__(parent)
        ttk.Frame.__init__(self, master=parent)

        self.windows = windows
        self.temp_dir = temp_dir
        self.save_Dir = save_Dir


        self.img_dict_list = []
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
        self.img_canvas.bind("<Button-1>", self.create_window_img)
        self.img_canvas.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)
        
        self.label_canvas = tk.Canvas(self, width=500, height=500)
        self.init_text_id2 = self.label_canvas.create_text(
            100, 50,
            text="No Image Selected",
            fill="black", font=('Helvetica 15 bold')
        )
        self.label_canvas.bind("<Button-1>", self.create_window_label)
        self.label_canvas.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)

        self.canvas_img_id = None
        self.canvas_label_id = None

        # Buttons
        button_back = tk.Button(self, text="<<", command=self.img_idx_back)
        button_fwd = tk.Button(self, text=">>", command=self.img_idx_fwd)
        button_del = tk.Button(self, text='remove image', command=self.delImage)

        button_back.grid(row=2, column=0, sticky=tk.NSEW)
        button_fwd.grid(row=2, column=2, sticky=tk.NSEW)
        button_del.grid(row=2, column=1, sticky=tk.NSEW)

        self.bind_all("<Left>", self.img_idx_back)
        self.bind_all("<Right>", self.img_idx_fwd)

        self.fileNameLabel = tk.Label(self, text='no image select')

        self.nameLabel = tk.Label(self, text='Write Label')
        self.nameText = tk.Text(self, height=1, width=10)
        self.nameText.bind("<KeyRelease>", self.on_key_release)
        
        self.confidenceLabel = tk.Label(self, text='')
        
        self.confirm = tk.Button(self, text="done", command=self.on_confirm)
        
        self.nameLabel.grid(row=3, column=0, sticky=tk.NSEW)
        self.nameText.grid(row=3, column=1, sticky=tk.NSEW)
        self.fileNameLabel.grid(row=4, column=0, sticky=tk.NSEW)
        self.confirm.grid(row=4, column=1, sticky=tk.NSEW)
        self.confidenceLabel.grid(row=5, column=0, sticky=tk.NSEW)

        # self.displayImage()

        utils.log_message('info', "Tab1_1 initialized successfully")

    def updateImage(self, img_dict_list):
        """Refresh image list and display current image"""
        self.img_dict_list = img_dict_list
        self.img_index = 0
        print(self.img_dict_list)
        self.displayImage()
        self.on_img_change()
        # if self.save_Dir is not None:
        #     try:
        #         self.img_list = []
        #         dst = utils.getDst(self.save_Dir, self.temp_dir, 'raw')
        #         for filename in os.listdir(dst):
        #             path = os.path.normpath(os.path.join(dst, filename))
        #             self.img_list.append(path)
        #         utils.log_message('debug', f"Updated image list: {self.img_list}")
        #         self.displayImage()
        #     except Exception as e:
        #         utils.errorMsg(title='updateImage', msg=f'error in updateImage {e}')
        #         utils.log_message('error', f"Failed to update images: {e}")

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
        if self.img_dict_list[self.img_index]['name'] == "":
            text = self.img_dict_list[self.img_index]['prediction']
            self.img_dict_list[self.img_index]['name'] = self.img_dict_list[self.img_index]['prediction']
        else:
            text = self.img_dict_list[self.img_index]['name']
        self.confidenceLabel.config(text=f'confidence={self.img_dict_list[self.img_index]['confidence']}')
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
                    self.windows.change_tab(2)
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
    
    # def on_key_press(self, event):
    #     pattern = r'^[a-zA-Z0-9]+$'
    #     if re.match(pattern, event.char):
    #         self.img_dict_list[self.img_index]['name'] = self.img_dict_list[self.img_index]['name'] + event.char
    #         return
    #     elif event.keysym == "BackSpace":
    #         self.img_dict_list[self.img_index]['name'] = self.img_dict_list[self.img_index]['name'][:-1]
    #         return
    #     return "break"

    def displayImage(self):
        """Display image on canvas"""
        if not self.img_dict_list:
            self.img_canvas.delete(self.canvas_img_id)
            self.img_canvas.delete(self.canvas_label_id)
            self.canvas_img_id = None
            self.canvas_label_id = None
            self.init_text_id = self.img_canvas.create_text(
                100, 50, text="No Image Selected", fill="black", font=('Helvetica 15 bold')
            )
            self.init_text_id2 = self.img_canvas.create_text(
                100, 50, text="No Image Selected", fill="black", font=('Helvetica 15 bold')
            )
            utils.log_message('debug', "No image selected — showing default text")
            self.fileNameLabel.config(text='no image select')
            return None

        try:
            imgPath = self.img_dict_list[self.img_index]['img_path']
            labelPath = self.img_dict_list[self.img_index]['label_path']
            
            if labelPath == "":
                labelPath = utils.imgPath('300px-Debugempty.png')
            
            # print(imgPath)
            # print(labelPath)
            self.img = Image.open(imgPath)
            self.label = Image.open(labelPath)
            picsize = 500, 500
            sizeImg = self.img.size
            sizeLabel = self.label.size
            self.img = self.img.resize(utils.best_fit(sizeImg, picsize), Image.Resampling.LANCZOS)
            self.label = self.label.resize(utils.best_fit(sizeLabel, picsize), Image.Resampling.LANCZOS)
            self.photoImg = ImageTk.PhotoImage(self.img)
            self.photoLabel = ImageTk.PhotoImage(self.label)
            self.fileNameLabel.config(text=os.path.basename(self.img_dict_list[self.img_index]['img_path']))

            if self.canvas_img_id is None:
                self.img_canvas.delete(self.init_text_id)
                self.canvas_img_id = self.img_canvas.create_image(
                    250, 250, image=self.photoImg, anchor="center"
                )
                self.label_canvas.delete(self.init_text_id2)
                self.label_canvas_id = self.label_canvas.create_image(
                    250, 250, image=self.photoLabel, anchor="center"
                )
            else:
                self.img_canvas.itemconfig(self.canvas_img_id, image=self.photoImg)
                self.label_canvas.itemconfig(self.label_canvas_id, image=self.photoLabel)

            utils.log_message('info', f"Displayed image: {imgPath}")

        except Exception as e:
            utils.errorMsg(title='displayImage', msg=f'error in displayImage {e}')
            utils.log_message('error', f"Error displaying image: {e}")

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
