import secrets
from PIL import Image, ImageDraw, ImageFont


class DrawText:
    DEFAULT_FONT_SIZE = 16
    DEFAULT_FONT_NAME = "courierprime-mono"

    text_offset = (1, 0)

    def __init__(self, text, font_name=DEFAULT_FONT_NAME, font_size=DEFAULT_FONT_SIZE):
        font = self._get_font(font_name, font_size)
        self.image = Image.new("RGB", self._get_image_size(font, text), (255, 255, 255))
        drawing_content = ImageDraw.Draw(self.image)
        drawing_content.text(self.text_offset, text, font=font, fill=(0, 0, 0))

    def save_image(self, filepath=None):
        if filepath is None:
            filepath = f"tmp/str_{secrets.token_urlsafe(8)}.png"
        self.image.save(filepath)
        return filepath

    def show(self):
        self.image.show()

    def get_image(self):
        return self.image

    def _get_image_size(self, font, text):
        text_size = font.getsize(text)
        image_width = text_size[0] + self.text_offset[0] + 2
        image_height = text_size[1] + self.text_offset[1] + 2
        return image_width, image_height

    @staticmethod
    def _get_font(font_name, font_size):
        return ImageFont.truetype(f"resources/{font_name}.ttf", font_size)


if __name__ == "__main__":
    DrawText(
        "2.12.9-rc.1"
    ).show()

