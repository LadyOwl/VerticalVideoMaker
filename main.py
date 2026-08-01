import os
from PIL import Image

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
BACKGROUND_COLOR = (0, 0, 0)


def prepare_image(image_path):

    img = Image.open(image_path)

    img_ratio = img.width / img.height
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT

    if img_ratio > target_ratio:
        new_width = TARGET_WIDTH
        new_height = int(TARGET_WIDTH / img_ratio)
    else:
        new_height = TARGET_HEIGHT
        new_width = int(TARGET_HEIGHT * img_ratio)

    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    background = Image.new('RGB', (TARGET_WIDTH, TARGET_HEIGHT), BACKGROUND_COLOR)

    x_offset = (TARGET_WIDTH - new_width) // 2
    y_offset = (TARGET_HEIGHT - new_height) // 2

    background.paste(img_resized, (x_offset, y_offset))

    return background

if __name__ == "__main__":
    os.makedirs("input_images", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    test_img = Image.new('RGB', (800, 600), color='red')
    test_img.save("input_images/test_poster.jpg")

    print("Тестовая картинка создана. Начинаю адаптацию...")

    final_image = prepare_image("input_images/test_poster.jpg")

    final_image.save("output/test_vertical_frame.jpg")
    print("Готово! Проверь папку output.")