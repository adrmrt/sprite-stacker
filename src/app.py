import os
import tkinter as tk
from tkinter import filedialog, ttk
import windnd

from src.core import ImageProcessor
from src.ui import AppMenu, PreviewPanel, FileTreeView


class SpriteStacker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sprite Stacker")
        self.geometry("900x700")

        self.image_paths: list[str] = []
        self.image_enabled: dict[str, bool] = {}
        self.current_image = None
        self.processor = ImageProcessor()

        self._build_ui()
        windnd.hook_dropfiles(self, func=self._on_drop)
        self.bind("<Configure>", lambda e: self._refresh())

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------

    def _build_ui(self):
        container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        container.pack(fill=tk.BOTH, expand=True)

        self._tree = FileTreeView(
            container,
            on_order_change=self._on_order_change,
            on_toggle=self._on_toggle,
            on_remove=self._on_remove,
        )
        self._preview = PreviewPanel(container)
        AppMenu(self, on_open=self._open_images, on_save=self._save_image)

    # ------------------------------------------------------------------
    # Callbacks passed to child components
    # ------------------------------------------------------------------

    def _on_order_change(self, filenames: list[str]):
        self.image_paths = [
            path
            for name in filenames
            for path in self.image_paths
            if os.path.basename(path) == name
        ]
        self._refresh()

    def _on_toggle(self, filename: str) -> bool:
        """Flip enabled state and return the new value."""
        enabled = not self.image_enabled.get(filename, True)
        self.image_enabled[filename] = enabled
        self._refresh()
        return enabled

    def _on_remove(self, filenames: list[str]):
        for name in filenames:
            path = next(
                (p for p in self.image_paths if os.path.basename(p) == name), None
            )
            if path:
                self.image_paths.remove(path)
                self.processor.evict(path)
                self.image_enabled.pop(name, None)
        self._refresh()

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    def _open_images(self):
        selected = filedialog.askopenfilenames(
            title="Select images",
            filetypes=[("Images", ".png;*.jpg")],
        )
        for path in reversed(selected):
            self._insert(path)
        self._refresh()

    def _save_image(self):
        if self.current_image is None:
            return
        path = filedialog.asksaveasfilename(
            title="Save image as",
            filetypes=[("PNG files", "*.png")],
            defaultextension=".png",
        )
        if path:
            self.current_image.save(path, format="PNG")

    def _on_drop(self, filenames):
        for file in filenames:
            file = file.decode("utf-8")
            if os.path.isfile(file) and file.lower().endswith((".png", ".jpg")):
                self._insert(file)
        self._refresh()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _insert(self, path: str):
        self.image_paths.insert(0, path)
        filename = os.path.basename(path)
        self.image_enabled[filename] = True
        self._tree.insert(filename)

    def _refresh(self):
        image = self.processor.composite(
            self.image_paths,
            self.image_enabled,
            self._preview.width,
            self._preview.height,
        )
        self.current_image = image
        self._preview.update(image)
