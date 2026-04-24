import tkinter as tk
from tkinter import ttk
from typing import Callable


class FileTreeView:
    def __init__(
        self,
        container: ttk.PanedWindow,
        on_order_change: Callable[[list[str]], None],
        on_toggle: Callable[[str], bool],
        on_remove: Callable[[list[str]], None],
    ):
        self._on_order_change = on_order_change
        self._on_toggle = on_toggle
        self._on_remove = on_remove

        self._tree = ttk.Treeview(container, show="tree")
        self._tree.tag_configure("disabled", foreground="gray")
        container.add(self._tree)

        self._dragged_item = None
        self._bind_events()
        self._create_context_menu(container)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, filename: str):
        self._tree.insert("", 0, text=filename)

    def remove(self, item):
        self._tree.delete(item)

    def get_filenames(self) -> list[str]:
        return [self._tree.item(i, "text") for i in self._tree.get_children()]

    def set_enabled(self, item, enabled: bool):
        self._tree.item(item, tags=(() if enabled else ("disabled",)))

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _bind_events(self):
        self._tree.bind("<Button-1>", self._on_drag_start)
        self._tree.bind("<B1-Motion>", self._on_drag_motion)
        self._tree.bind("<ButtonRelease-1>", self._on_drag_release)
        self._tree.bind("<Delete>", lambda e: self._remove_selected())
        self._tree.bind("<Double-1>", self._on_double_click)
        self._tree.bind("<Button-3>", self._show_context_menu)

    def _create_context_menu(self, root):
        self._context_menu = tk.Menu(root, tearoff=0)
        self._context_menu.add_command(label="Remove", command=self._remove_selected)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_drag_start(self, event):
        self._dragged_item = self._tree.identify_row(event.y)

    def _on_drag_motion(self, event):
        if not self._dragged_item:
            return
        target = self._tree.identify_row(event.y)
        if target and target != self._dragged_item:
            self._tree.move(
                self._dragged_item,
                self._tree.parent(target),
                self._tree.index(target),
            )

    def _on_drag_release(self, event):
        self._dragged_item = None
        self._on_order_change(self.get_filenames())

    def _on_double_click(self, event):
        item = self._tree.identify_row(event.y)
        if not item:
            return
        filename = self._tree.item(item, "text")
        enabled = self._on_toggle(filename)
        self.set_enabled(item, enabled)

    def _show_context_menu(self, event):
        item = self._tree.identify_row(event.y)
        if item:
            if len(self._tree.selection()) <= 1:
                self._tree.selection_set(item)
            self._context_menu.post(event.x_root, event.y_root)

    def _remove_selected(self):
        selected = self._tree.selection()
        if not selected:
            return
        filenames = [self._tree.item(i, "text") for i in selected]
        for item in selected:
            self._tree.delete(item)
        self._on_remove(filenames)
