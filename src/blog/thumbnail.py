import logging
from unicodedata import category

from PIL import Image, ImageDraw, ImageFont


def generate_thumbnail(category_="", title_="", output_path_=None, font_=None):
    width, height = 1280, 720
    background_color = (255, 255, 255)
    category_color =(46,140,255)
    title_color = (0, 0, 0)
    spacing = 80
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)
    font_category = ImageFont.truetype(font_, 70)
    font_title = ImageFont.truetype(font_, 95)  # bold
    category_size = draw.textbbox((0, 0), category_, font=font_category)
    title_size = draw.textbbox((0, 0), title_, font=font_title)
    total_height = (category_size[3] - category_size[1]) + spacing + (title_size[3] - title_size[1])
    start_y = (height - total_height) // 2
    category_x = (width - (category_size[2] - category_size[0])) // 2
    title_x = (width - (title_size[2] - title_size[0])) // 2
    draw.text((category_x, start_y), category_, fill=category_color, font=font_category)
    draw.text((title_x, start_y + (category_size[3] - category_size[1]) + spacing), title, fill=title_color, font=font_title, align="center")
    image.save(output_path_)
    logging.info(f"이미지 저장 완료: {output_path_}")


if __name__ == '__main__':
    category = "Python"
    title = "파이썬 왈러스 연산자(:=)"
    output = "../../thumbnails/designPattern_template_method_pattern.png"
    font = "/Users/genius/Library/Fonts/NanumGothicExtraBold.ttf"
    generate_thumbnail(category, title, output, font)
