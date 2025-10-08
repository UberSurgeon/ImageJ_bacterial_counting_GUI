import io
import imagej.doctor
from contextlib import redirect_stdout
import tkinter as tk
import include.utils as utils
import json
from tkinter import filedialog

def capture_checkup_output():
    # Create a string buffer to capture the output
    buffer = io.StringIO()

    # Redirect stdout to the buffer
    with redirect_stdout(buffer):
        imagej.doctor.checkup()

    # Get the captured output as a string
    output = buffer.getvalue()

    # Close the buffer
    buffer.close()

    return output


def main():
    pre = tk.Tk()
    utils.set_icon(pre)
    with open(utils.settingPath(), 'r') as file:
        setting = json.load(file)

    JHLb = tk.Label(pre, text=f'JAVA_HOME={setting["JAVA_HOME"]}')
    FJLb = tk.Label(pre, text=f'fiji_dir={setting["fiji_dir"]}')

    def update_JAVA_HOME():
        path = filedialog.askdirectory(title='Select the JAVA_HOME Directory')
        if path != '':
            setting["JAVA_HOME"] = path
            JHLb.config(text=f'JAVA_HOME={setting["JAVA_HOME"]}')
            update_setting()

    def update_fijiDir():
        path = filedialog.askdirectory(
            title='Select the fiji installation Directory'
            )
        if path != '':
            setting["fiji_dir"] = path
            FJLb.config(text=f'JAVA_HOME={setting["fiji_dir"]}')
            update_setting()

    def update_setting():
        with open(utils.settingPath(), 'w') as file:
            json.dump(setting, file, indent=4)

    JHLb.pack()
    tk.Button(pre, text='Change JAVA_HOME', command=update_JAVA_HOME).pack()
    FJLb.pack()
    tk.Button(pre, text='Change fiji_dir', command=update_fijiDir).pack()

    text_box = tk.Text(pre,)
    text_box.pack()
    text_box.insert(tk.END, capture_checkup_output())
    text_box.config(state='disabled')

    pre.mainloop()
    
if __name__ == '__main__':
    main()
