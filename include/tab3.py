import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import pandas as pd


class Tab3(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.inputFile = None
        self.outputPath = None
        
        tk.Label(self, text='Input file path:').pack()
        self.inFile = tk.Label(self, text='Non Selected')
        self.inFile.pack()
        tk.Button(self, text='Select file', command=self.inputDir).pack()
        tk.Label(self, text='Output directory path:').pack()
        self.outDir = tk.Label(self, text='Non Selected')
        self.outDir.pack()
        tk.Button(self, text='Select output dir', command=self.outputDir).pack()
        
        tk.Button(self, text='ArrangeTable', command=self.arrange_table).pack()
        self.check = tk.Label(self, text='')
        self.check.pack()

    def inputDir(self):
        try:
            self.inputFile = filedialog.askopenfilename(
                initialdir='gui',
                title='Select input CSV file',
                filetypes=(('CSV files', '*.csv'),
                           ("All files", "*.*"))
            )
            if self.inputFile == '':
                self.inputFile = None
            else:
                self.inFile.config(text=self.inputFile)
        except Exception as e:
            self.error_msg(title='Input Error', msg=f'Error selecting input file: {e}')

    def outputDir(self):
        try:
            self.outputPath = filedialog.askdirectory(
                initialdir='gui',
                title='Select output directory'
            )
            if self.outputPath == '':
                self.outputPath = None
            else:
                self.outDir.config(text=self.outputDir)
        except Exception as e:
            self.error_msg(title='Output Error', msg=f'Error selecting output directory: {e}')

    def arrange_table(self):
        try:
            if self.inputFile and self.outDir:
                df = pd.read_csv(self.inputFile)

                # Extract sample type from filenames
                df["SampleType"] = df["Filename"].str.split("_").str[0].str.split("-").str[1]

                # Pivot so each sample type becomes a column
                pivot = df.pivot(columns="SampleType", values=["Filename", "Count"])

                # Flatten column names
                pivot.columns = [f"{a} ({b})" for a, b in pivot.columns]

                # Save results
                output_file = os.path.join(self.outputPath, 'dataTable.csv')
                pivot.to_csv(output_file, index=False)
                self.info_msg(title='csv table saved', msg=f'csv table saved at {output_file}')
                self.check.config(text='success*')
        except Exception as e:
            self.error_msg(title='Processing Error', msg=f'Error during arrange_table: {e}')

    def error_msg(self, title, msg):
        messagebox.showerror(title=title, message=msg)

    def warning_msg(self, title, msg):
        messagebox.showwarning(title=title, message=msg)

    def info_msg(self, title, msg):
        messagebox.showinfo(title=title, message=msg)
