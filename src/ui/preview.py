import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class PreviewPanel:
    def __init__(self, container: ttk.PanedWindow):
        self.frame = tk.Frame(container)
        container.add(self.frame)

        self._label = tk.Label(self.frame)
        self._label.pack(expand=True, anchor="center")

        self._photo = None  # keep reference alive

    def update(self, image: Image.Image):
        self._photo = ImageTk.PhotoImage(image)
        self._label.configure(image=self._photo)

    @property
    def width(self) -> int:
        return self.frame.winfo_width()

    @property
    def height(self) -> int:
        return self.frame.winfo_height()
