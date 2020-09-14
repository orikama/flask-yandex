import textwrap

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


PATH_TO_FONT = './static/fonts/Montserrat-Bold.ttf'
FONT_SIZE = 40


class TextOnImage():

    def __init__(self, width):
        self.font = ImageFont.truetype(PATH_TO_FONT, size=FONT_SIZE)
        self.text_pos = (50, 50)
        self.text_wrapper = textwrap.TextWrapper(self.__get_wrap_width(width))

    def draw_text(self, text, img):
        wrapped_text = ""
        for line in self.text_wrapper.wrap(text=text):
            wrapped_text += line + '\n'

        image = Image.open(BytesIO(img))
        draw = ImageDraw.Draw(image)

        text_size = draw.textsize(wrapped_text, font=self.font)
        text_color = self.__get_inversed_area_color(text_size, image.convert('RGB'))
        draw.multiline_text(self.text_pos, wrapped_text, fill=f'rgb{text_color}', font=self.font)

        return image

    def __get_inversed_area_color(self, text_size, image):
        r, g, b = 0, 0, 0
        ox, oy = text_size
        x, y = self.text_pos

        count = 0
        for s in range(x, x + ox + 1):
            for t in range(y, y + oy + 1):
                pixlr, pixlg, pixlb = image.getpixel((s,t))
                r += pixlr
                g += pixlg
                b += pixlb
                count += 1

        avg = ((r // count), (g // count), (b // count))
        result = ((avg[0] + 127) % 255,(avg[1] + 127) % 255,(avg[2] + 127) % 255)

        return result

    @staticmethod
    def __get_wrap_width(width):
        return int(width * 2 * 0.7 / FONT_SIZE)
