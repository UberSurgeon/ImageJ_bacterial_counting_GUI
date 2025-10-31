import customtkinter as ctk

class SecondaryButton(ctk.CTkButton):
    def __init__(self, master, button_text, command=None, fg_color=None, **kwargs):
        super().__init__(
            master,
            text=button_text,
            command=command,
            fg_color=fg_color or "white",
            hover_color="#f1f8ff",         
            text_color="#003366",          
            font=ctk.CTkFont("Roboto",size=16, weight="bold"),
            corner_radius=10,
            width=100,
            border_width=0.3,
            height=40,
            border_color="#BEDEFE",
            **kwargs
        )

        # Add hover effects for text color
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self,event=None):
        self.configure(text_color="white",fg_color="#36719f")

    def _on_leave(self,event=None):
        self.configure(text_color="#003366",fg_color="white")
    
    def change_text(self, new_text):
        self.configure(text=new_text)

