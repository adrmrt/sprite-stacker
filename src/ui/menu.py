import tkinter as tk
from tkinter import Menu
from typing import Callable


class AppMenu:
    def __init__(
        self, root: tk.Tk, on_open: Callable[[], None], on_save: Callable[[], None]
    ):
        self.menu_bar = Menu(root)

        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Add images", command=on_open)
        file_menu.add_command(label="Save", command=on_save)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        root.config(menu=self.menu_bar)
