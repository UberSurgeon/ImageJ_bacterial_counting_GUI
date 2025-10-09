import tkinter as tk
from tkinter import filedialog
import os
import pandas as pd
import include.utils as utils


class Tab3(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.inputFile = None
        self.outputPath = None

        # UI labels and buttons
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

        utils.log_message('info', "Tab3 initialized successfully")

    def inputDir(self):
        """Prompt user to select input CSV file."""
        try:
            self.inputFile = filedialog.askopenfilename(
                initialdir='gui',
                title='Select input CSV file',
                filetypes=(('CSV files', '*.csv'), ("All files", "*.*"))
            )
            if self.inputFile == '':
                self.inputFile = None
                utils.log_message('warning', "No input file selected")
            else:
                self.inFile.config(text=self.inputFile)
                utils.log_message('info', f"Selected input CSV file: {self.inputFile}")
        except Exception as e:
            utils.errorMsg(title='Input Error', msg=f'Error selecting input file: {e}')
            utils.log_message('error', f"Exception during input file selection: {e}")

    def outputDir(self):
        """Prompt user to select output directory."""
        try:
            self.outputPath = filedialog.askdirectory(
                initialdir='gui',
                title='Select output directory'
            )
            if self.outputPath == '':
                self.outputPath = None
                utils.log_message('warning', "No output directory selected")
            else:
                self.outDir.config(text=self.outputPath)
                utils.log_message('info', f"Selected output directory: {self.outputPath}")
        except Exception as e:
            utils.errorMsg(title='Output Error', msg=f'Error selecting output directory: {e}')
            utils.log_message('error', f"Exception during output directory selection: {e}")

    def arrange_table(self):
        """Read input CSV, transform it into a pivoted table, and save to output directory."""
        try:
            # Validate that both paths are set
            if not self.inputFile:
                utils.warningMsg("Missing input", "Please select an input CSV file first.")
                utils.log_message('warning', "ArrangeTable aborted — no input file selected")
                return
            if not self.outputPath:
                utils.warningMsg("Missing output", "Please select an output directory first.")
                utils.log_message('warning', "ArrangeTable aborted — no output directory selected")
                return

            utils.log_message('info', f"Processing input CSV: {self.inputFile}")

            df = pd.read_csv(self.inputFile)
            utils.log_message('debug', f"Read CSV with {len(df)} rows")

            # Extract sample type from filenames
            df["SampleType"] = (
                df["Filename"].str.split("_").str[0].str.split("-").str[1]
            )

            # Extract base name BEFORE the sample type (for grouping)
            df["BaseName"] = df["Filename"].str.split("-").str[0]

            # Pivot so each sample type becomes a column within each BaseName
            pivot = df.pivot(index="BaseName", columns="SampleType", values=["Filename", "Count"])

            # Flatten columns
            pivot.columns = [f"{a} ({b})" for a, b in pivot.columns]
            pivot.reset_index(drop=True, inplace=True)

            # Save results
            output_file = os.path.join(self.outputPath, 'Taulukko_Kuvista_Lasketuista_pesakeluvuista.csv')
            pivot.to_csv(output_file, index=False)

            utils.infoMsg(title='csv table saved', msg=f'csv table saved at {output_file}')
            utils.log_message('info', f"CSV table successfully saved at {output_file}")
            self.check.config(text='success*')

        except Exception as e:
            utils.errorMsg(title='Processing Error', msg=f'Error during arrange_table: {e}')
            utils.log_message('error', f"Error while arranging table: {e}")
