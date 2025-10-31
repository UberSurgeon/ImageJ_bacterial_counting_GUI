import tkinter as tk
from tkinterweb import HtmlFrame
import markdown
import include.utils as utils
import customtkinter as ctk
from include.DirectoryCard import DirectoryCard


APP_BG= "#f1f8ff"

TEXT_COLOR = "#003366"



class Tab4(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.configure(fg_color=APP_BG)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)


        self.main_container = ctk.CTkFrame(self, fg_color=APP_BG)
        self.main_container.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.columnconfigure(1, weight=1)
        DirectoryCard(self.main_container,"How to use", "Click the button to open the help guide.", "Guide" ,self.createWindowHelp).grid(row=0, column=0, pady=10,padx=10,sticky="nsew")
        DirectoryCard(self.main_container,"Contact", "Click the button to open the contact/support window.", "Help", self.createWindowContact).grid(row=0, column=1, pady=10,padx=10,sticky="nsew")

        utils.log_message('info', "Tab4 initialized successfully")

    def createWindowHelp(self):
        """Create and display a help/contact window using markdown and HTML."""
        try:
            # Create a new popup window
            new_window = tk.Toplevel()
            new_window.geometry('800x600')
            new_window.rowconfigure(0, weight=1)
            new_window.columnconfigure(0, weight=1)
            utils.log_message('info', "Opened new Tab4 help window")

            # Markdown help content
            md_text = md_text = """
# How to Use

This guide explains the basic workflow and features of the App.

---

## 1. Uploading Images

1. Go to **Tab 1 — Upload Image**.  
2. Click **Upload** and select one or more image files (supported formats: `.png`, `.jpg`, `.tif`).  
3. After uploading:
   - Uploaded images will appear in the main display area.  
   - Use **<<** and **>>** to navigate between multiple images.  
   - Click directly on an image to open a popup window showing it at full resolution, with zoom and pan support.  
4. To delete an image:
   - Click **Remove Image** and confirm when prompted.  
   - The selected image will be removed from your working directory.  
5. To rotate an image:
   - Click **Rotate** to rotate the image by **90° clockwise**.
6. Toggle image labeling:
   - Click the **predict labeling?** checkbox if you want to crop and predict the detected label
   - If the box is not checked, it will just crop the image reduce the processing time

**Note:** Uploaded images are stored temporarily in the `raw/` folder within your project directory.

---

## 2. Cropping

1. Click **Crop** to automatically detect and crop the dish in the image.  
2. The app will also attempt to detect and label the dish automatically.  
3. If no label is detected, a placeholder image will be used instead.

---

## 3. Renaming

1. You can manually rename each file by typing in the text box below the image.  
2. Each filename must be **unique** — duplicate names are not allowed.  
3. When done, click **Done** to rename all files.  
4. If a text box is left blank, the **default name** shown will be used.

---

## 4. Counting and Image Processing

1. Go to **Tab 2 — Count**.  
2. Click **Count** to process your images.  
   - The app uses **ImageJ** to analyze the images.  
   - Processed images showing detection points will appear in the display area.  
   - Data files will be saved in the `/data` folder.  
3. You can switch between:
   - **Raw view** — displays original images.  
   - **Count view** — displays processed images with detection overlays.  
4. The text box in the top-right corner shows image metadata (size, format, mode, etc.).  
5. To adjust detection settings:
   - Click the **“:”** button to open the **Preset Configuration** window.  
   - Select a built-in preset or choose **Custom** to define your own values for `addlightness` and `prominence`.

**Note:** The currently active preset and its parameters are displayed on-screen.

---

## 5. Arranging Tables

In **Tab 3 — Table Manager**, you can organize and export your data into a structured CSV file.

**Note:** MAKE SURE TO SAVE FIRST.

### Steps:
1. Click **Select File** and choose the CSV file generated during the counting step.  
2. Click **Select Output Dir** to choose the output directory.  
3. Click **Arrange Table** to process and save the results.  
4. The output file will be named  
   `Taulukko_Kuvista_Lasketuista_pesakeluvuista.csv`  
   and stored in the selected directory.

**Note:** The app automatically organizes data by sample type, extracted from filenames.

---

## 6. Tips and Notes

- Ensure **JAVA_HOME** and **Fiji/ImageJ** directories are correctly set before launching the main window.  
- Temporary files are stored in automatically created folders (e.g., `temp_...`) and will be removed when the program closes.  
- Always **save your project** before exiting to prevent data loss.  
- If an operation fails, check the **log file** for detailed error information.

---

## 7. Support and Feedback

If you encounter bugs or have suggestions:
1. Go to **Tab 4 — Info/Misc**.  
2. Click **Contact for Support** for instructions on reporting issues.  
3. You can also reach out directly through the provided contact information or the official **GitHub repository**.

"""


            # Convert markdown to HTML
            html = markdown.markdown(md_text, extensions=['extra', 'sane_lists', 'nl2br'])

            # Create an HTML frame for display
            frame = HtmlFrame(new_window,
                              horizontal_scrollbar="auto",
                              vertical_scrollbar="auto",
                              messages_enabled=False
                              )
            frame.load_html(html)
            frame.pack(fill="both", expand=True)

            utils.log_message('debug', "Markdown help content loaded into HTML frame successfully")

        except Exception as e:
            utils.log_message('error', f"Error creating help window: {e}")
            utils.errorMsg(title='Help Window Error', msg=f'Unable to open help window: {e}')
            

    def createWindowContact(self):
        """Create and display a contact window for bug reports or support"""
        try:
            # Create a new popup window
            new_window = tk.Toplevel()
            new_window.geometry('600x400')
            new_window.title("Contact & Support")
            new_window.rowconfigure(0, weight=1)
            new_window.columnconfigure(0, weight=1)

            # Log that the contact window opened successfully
            utils.log_message('info', "Opened Tab4 contact window")

            # Contact info (replace with your actual details)
            contact_email = "sb15290@student.samk.fi"
            github_link = "https://github.com/UberSurgeon"
            github_repo = "https://github.com/UberSurgeon/ImageJ_bacterial_counting_GUI"

            # Markdown text for the contact page
            md_text = f"""
# Contact & Support

If you encounter a **bug**, have a **feature request**, or need **technical support**, please reach out using one of the following methods.

---

## Email Support

You can contact the developer directly via email:

**Email:** [{contact_email}](mailto:{contact_email})

Please include:
- A short description of the issue  
- Steps to reproduce it  
- Your operating system and Python version (if applicable)

---

## GitHub

For bug reports or feature requests, you can also open an issue on GitHub:

[Visit GitHub Profile]({github_link})

If this project helped you, consider leaving a star on the repository!

[Visit GitHub Repo]({github_repo})

---

Thank you for using this application.
"""

            # Render markdown into HTML

            html = markdown.markdown(md_text, extensions=['extra', 'sane_lists', 'nl2br'])
            frame = HtmlFrame(
                new_window,
                horizontal_scrollbar="auto",
                vertical_scrollbar="auto",
                messages_enabled=False  # disable tkinterweb debug logs
            )
            frame.load_html(html)
            frame.pack(fill="both", expand=True)

        except Exception as e:
            utils.log_message('error', f"Error creating contact window: {e}")
            utils.errorMsg(
                title='Contact Window Error',
                msg=f'Unable to open contact window: {e}'
            )
