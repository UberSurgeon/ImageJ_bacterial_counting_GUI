import tkinter as tk
from tkinter import messagebox
from tkinterweb import HtmlFrame
import markdown




class Tab4(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Button(self, text='How to use', command=self.create_window).pack()
        
        # add credits and contact if encounter anybugs
        tk.Button(self, text='Contact for support', command=self.create_window).pack()

    def create_window(self):        
        new_window = tk.Toplevel()
        new_window.geometry('800x600')
        new_window.rowconfigure(0, weight=1)  # make the CanvasImage widget expandable
        new_window.columnconfigure(0, weight=1)
        md_text = """
        How to use:

        1. Upload image:
        To upload image click Tab 1 and select the file you want to upload, it should display the images in the app, use << and >> to navigate between multiple image.
        {delete image section}.
        To view the full image click on the image itself, it will open a pop up screen with the original resolution where you can zoom and pan through the image.

        2. Crop:
        ...

        3. Manipulating the image:
        To count just click the count button, it will count and display the point selection image in the small window, click to view full. The data table will be put in the /data folder, and will be display in the small table to the right.
        You can change between the preset available, or set your custom value using the ":" button
        To view raw, click raw
        The top right text box is the image meta data.

        4. ArrangeTable
        Click select file -> Click select dir -> click arrange you can find the output file in the selected output dir
        """
        html = markdown.markdown(md_text)
        frame = HtmlFrame(new_window, horizontal_scrollbar="auto", vertical_scrollbar="auto")
        frame.load_html(html)
        frame.pack()



    def error_msg(self, title, msg):
        messagebox.showerror(title=title, message=msg)

    def warning_msg(self, title, msg):
        messagebox.showwarning(title=title, message=msg)

    def info_msg(self, title, msg):
        messagebox.showinfo(title=title, message=msg)
