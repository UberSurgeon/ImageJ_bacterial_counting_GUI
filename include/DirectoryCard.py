import customtkinter as ctk
from include.Secondary_Button import SecondaryButton

class DirectoryCard(ctk.CTkFrame):
    def __init__(self,master,heading,directory,button_text,command,**kwargs):
        super().__init__(master,**kwargs)
        self.heading = heading
        self.directory=directory
        self.button_text = button_text
        self.button_command = command
        self.configure(fg_color="white")
        heading_font = ("Roboto",18,"bold")
        directory_font = ("roboto",16)
        #creating elements
        self.heading_element = ctk.CTkLabel(self,text=self.heading,font=heading_font)
        self.directory_element = ctk.CTkLabel(self,text=self.directory,font=directory_font)
        self.button_element= SecondaryButton(self,self.button_text,self.button_command)
        
        #positioning of elements
        self.heading_element.pack(padx=20,pady=10)
        self.directory_element.pack(padx=20,pady=10)
        self.button_element.pack(padx=20,pady=10)


