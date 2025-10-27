import tkinter as tk
import threading

class LoadingWindow:
    def __init__(self, text, spinner=True, delay=150):
        self.text = f"loading >> {text}"
        self.spinner = spinner
        self.delay = delay
        self.running = False
        self.thread = None
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
        
    def stop(self):
        self.running = False

    def _run(self):
        self.root = tk.Tk()
        self.root.title(self.text)
        self.root.geometry("250x100")
        self.root.resizable(False, False)

        self.label = tk.Label(self.root, text=self.text, font=("Arial", 5))
        self.label.pack(expand=True, pady=20)

        if self.spinner:
            self.spinner_index = 0
            self.spinner_chars = ["|", "/", "-", "\\"]
            self._animate()

        self._check_stop()
        self.root.mainloop()

    def _animate(self):
        spinner_char = self.spinner_chars[self.spinner_index]
        self.label.config(text=f"{self.text} {spinner_char}")
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
        if self.running:
            self.root.after(self.delay, self._animate)

    def _check_stop(self):
        if not self.running:
            self.root.destroy()
        else:
            self.root.after(100, self._check_stop)
