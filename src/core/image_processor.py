from PIL import Image


class ImageProcessor:
    def __init__(self):
        self.cache: dict[str, Image.Image] = {}

    def load(self, path: str) -> Image.Image:
        if path not in self.cache:
            with Image.open(path) as img:
                self.cache[path] = img.copy()
        return self.cache[path]

    def evict(self, path: str) -> None:
        self.cache.pop(path, None)

    def composite(
        self,
        paths: list[str],
        enabled: dict[str, bool],
        max_width: int,
        max_height: int,
    ) -> Image.Image:
        """
        Composite all enabled images into a single RGBA image.
        If the result exceeds max_width/max_height it is thumbnailed to fit.
        Returns a transparent placeholder if no images are enabled.
        """
        active = [p for p in paths if enabled.get(self._filename(p), True)]

        if not active:
            return Image.new("RGBA", (max_width, max_height), (255, 255, 255, 0))

        images = [self.load(p) for p in reversed(active)]
        canvas_w = max(img.width for img in images)
        canvas_h = max(img.height for img in images)

        combined = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        for img in images:
            x = (canvas_w - img.width) // 2
            y = (canvas_h - img.height) // 2
            layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
            layer.paste(img, (x, y), img if img.mode == "RGBA" else None)
            combined.alpha_composite(layer)

        if combined.width > max_width or combined.height > max_height:
            combined.thumbnail((max_width, max_height), Image.LANCZOS)

        return combined

    @staticmethod
    def _filename(path: str) -> str:
        import os

        return os.path.basename(path)
