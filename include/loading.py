from multiprocessing import Process, Value, freeze_support, set_start_method
import tkinter as tk
import time
import include.utils as utils 

class LoadingWindow:
    def __init__(self, text="Loading...", spinner=True, delay=150):
        freeze_support()  # required for pyinstaller on Windows
        try:
            set_start_method('spawn')
        except RuntimeError:
            pass

        self.text = text
        self.spinner = spinner
        self.delay = delay
        self._run_flag = Value('i', 1)
        self.process = None

    @staticmethod
    def _run_window(text, spinner, delay, run_flag):
        """Executed in a separate process: creates its own Tkinter loop."""
        root = tk.Tk()
        utils.set_icon(root)
        root.title("Loading...")
        root.geometry("250x100")
        root.resizable(False, False)
        root.attributes("-topmost", True)
        label = tk.Label(root, text=text, font=("Arial", 8))
        label.pack(expand=True, pady=20)

        spinner_chars = ["|", "/", "-", "\\"]
        idx = 0

        def animate():
            nonlocal idx
            if run_flag.value == 0:
                root.destroy()
                return
            if spinner:
                label.config(text=f"{text} {spinner_chars[idx]}")
                idx = (idx + 1) % len(spinner_chars)
            root.after(delay, animate)

        animate()
        root.mainloop()

    def start(self):
        self._run_flag.value = 1
        self.process = Process(
            target=self._run_window,
            args=(self.text, self.spinner, self.delay, self._run_flag),
            name='loading-window',
        )
        self.process.start()

    def stop(self):
        # if self.process and self.process.is_alive():
        #     self._run_flag.value = 0
        #     self.process.join(timeout=2)
        #     self.process.close()
        #     self.process = None
        if self.process is not None:
            if self.process.is_alive():
                self.process.terminate()
                self.process.join()
            self.process.close()
            self.process = None

    def run_with_loading(self, func, *args, **kwargs):
        self.start()
        try:
            result = func(*args, **kwargs)
        finally:
            self.stop()
        return result


if __name__ == "__main__":
    # Test run
    def demo_task():
        for i in range(5):
            print(f"Working... {i+1}/5")
            time.sleep(1)

    loader = LoadingWindow("Initializing...", spinner=True)
    loader.run_with_loading(demo_task)
    print("Done!")
