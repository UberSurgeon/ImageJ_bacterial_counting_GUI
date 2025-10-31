import customtkinter as ctk
import customtkinter as ctk
import tkinter as tk
class LogDropdown(ctk.CTkFrame):
    def __init__(self, parent, get_logs_func,max_height=200):
        super().__init__(parent)
        self.get_logs_func = get_logs_func
        self.expanded = False  # Is the dropdown open?
        self.max_height = max_height

        self.configure(fg_color="#f1f8ff")

        # Button to toggle dropdown
        self.toggle_btn = ctk.CTkButton(self, text="Show Log ▼", command=self.toggle,fg_color="white",text_color="#003366")
        self.toggle_btn.pack(fill="x", padx=10, pady=5)

        # Frame to hold the log (hidden initially)
        self.log_frame = ctk.CTkScrollableFrame(self,height=self.max_height,fg_color="white")
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_frame.pack_forget()  # Hide initially

    def toggle(self):
        if self.expanded:
            self.log_frame.pack_forget()
            self.toggle_btn.configure(text="Show Log ▼")
            self.expanded = False
        else:
            # Clear previous logs
            for widget in self.log_frame.winfo_children():
                widget.destroy()

            # Get new logs dynamically
            raw_logs = self.get_logs_func()
            if isinstance(raw_logs, str):
                logs = raw_logs.splitlines()  # split string into lines
            else:
                logs = raw_logs

            # Add labels to scrollable frame
            for log in logs:
                label = ctk.CTkLabel(self.log_frame, text=log, anchor="w")
                label.pack(fill="x", padx=5, pady=2)

            self.log_frame.pack(fill="both", expand=True, padx=10, pady=5)
            self.toggle_btn.configure(text="Hide Log ▲")
            self.expanded = True
