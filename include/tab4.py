import tkinter as tk
from tkinterweb import HtmlFrame
import markdown
import include.utils as utils


class Tab4(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Button to open how-to-use guide
        tk.Button(self, text='How to use', command=self.createWindowHelp).pack()

        # Button for contact/help
        tk.Button(self, text='Contact',
                  command=self.createWindowContact).pack()

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

This guide explains the basic workflow and features of the Image Analysis App.

---

## 1. Uploading Images

1. Go to **Tab 1 — Upload Image**.  
2. Click **Upload** and select one or more image files (supported formats: `.png`, `.jpg`, `.tif`).  
3. After uploading:
   - Images will appear in the main display area.  
   - Use **<<** and **>>** to navigate between multiple images.  
   - Click directly on an image to open a popup window showing it at full resolution, with zoom and pan support.
4. To delete an image:
   - Click **Remove Image** and confirm when prompted.  
   - The selected image will be removed from your working directory.

**Note:** Uploaded images are stored temporarily in the `raw/` folder within your project directory.

---

## 2. Cropping

If cropping functionality is available:
1. Open the image you wish to crop.  
2. Use the selection tool to define the area you want to keep.  
3. Confirm to save the cropped version.

This feature may be added or expanded in future updates.

---

## 3. Counting and Image Processing

1. Go to **Tab 2 — Count**.  
2. Click **Count** to process your images.  
   - The app uses **ImageJ** to analyze the images.  
   - Processed images showing detection points will appear in the display area.  
   - Data files will be saved in the `/data` folder.
3. You can switch between:
   - **Raw** view — original images.  
   - **Count** view — processed images with overlays.
4. The top-right text box displays metadata for the current image, such as size, format, and mode.
5. To adjust detection settings:
   - Click the **“:”** button to open the preset configuration window.  
   - Select a built-in preset or choose **custom** to define your own values for `addlightness` and `prominence`.

**Tip:** The currently active preset and its parameters are shown on-screen.

---

## 4. Arranging Tables

In **Tab 3 — Table Manager**, you can organize and export data into a structured CSV file.

### Steps:
1. Click **Select File** and choose the CSV file generated during the counting step.  
2. Click **Select Output Dir** to choose where to save the arranged file.  
3. Click **Arrange Table** to process and save the results.  
4. The output file will be named `dataTable.csv` and stored in the selected directory.

**Note:** The app automatically organizes data by sample type, extracted from filenames.

---

## 5. Tips and Notes

- Make sure **JAVA_HOME** and **Fiji/ImageJ** directories are correctly set before launching the main window.  
- Temporary files are stored in automatically created folders (for example, `temp_...`) and will be removed when the program closes.  
- Always **save your project** before exiting to prevent data loss.  
- If an operation fails, check the log file for detailed error information.

---

## 6. Support and Feedback

If you encounter bugs or have suggestions:
- Go to **Tab 4 — Info/Misc**.  
- Click **Contact for support** for details or instructions on reporting issues.  
- You can also reach out directly via the provided contact information or GitHub repository.

"""


            # Convert markdown to HTML
            html = markdown.markdown(md_text)

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

            html = markdown.markdown(md_text)
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
