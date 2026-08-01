import os
import numpy as np
from PIL import Image
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from moviepy.audio.fx import AudioLoop

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
BACKGROUND_COLOR = (0, 0, 0)
FRAME_DURATION = 4
FPS = 30

INPUT_IMAGES_DIR = "input_images"
INPUT_AUDIO_DIR = "input_audio"
OUTPUT_DIR = "output"

def prepare_image(image_path):

    img = Image.open(image_path).convert("RGB")

    img_ratio = img.width / img.height
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT

    if img_ratio > target_ratio:
        new_width = TARGET_WIDTH
        new_height = int(TARGET_WIDTH / img_ratio)
    else:
        new_height = TARGET_HEIGHT
        new_width = int(TARGET_HEIGHT * img_ratio)

    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    background = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), BACKGROUND_COLOR)
    x_offset = (TARGET_WIDTH - new_width) // 2
    y_offset = (TARGET_HEIGHT - new_height) // 2
    background.paste(img_resized, (x_offset, y_offset))

    return background


def get_supported_files(directory, extensions):

    files = []
    for filename in sorted(os.listdir(directory)):
        if filename.lower().endswith(tuple(extensions)):
            files.append(os.path.join(directory, filename))
    return files


def create_video(output_filename="final_video.mp4"):

    image_paths = get_supported_files(INPUT_IMAGES_DIR, (".jpg", ".jpeg", ".png"))
    audio_paths = get_supported_files(INPUT_AUDIO_DIR, (".mp3", ".wav"))

    if not image_paths:
        print(f"❌ В папке '{INPUT_IMAGES_DIR}' не найдено картинок.")
        return
    if not audio_paths:
        print(f"❌ В папке '{INPUT_AUDIO_DIR}' не найдено аудио.")
        return

    audio_path = audio_paths[0]
    print(f"🎵 Используем трек: {os.path.basename(audio_path)}")
    print(f"🖼 Найдено картинок: {len(image_paths)}")

    clips = []
    for path in image_paths:
        print(f"  → Обрабатываю: {os.path.basename(path)}")
        pil_image = prepare_image(path)
        frame_array = np.array(pil_image)
        clip = ImageClip(frame_array, duration=FRAME_DURATION).with_fps(FPS)
        clips.append(clip)
    final_video = concatenate_videoclips(clips, method="compose")
    video_duration = final_video.duration
    print(f"⏱ Длительность видео: {video_duration:.1f} сек.")

    audio = AudioFileClip(audio_path)
    if audio.duration < video_duration:
        print("🔁 Трек короче видео — зацикливаем его.")
        audio = audio.with_effects([AudioLoop(duration=video_duration)])
    else:
        print("✂️ Трек длиннее видео — обрезаем под длину ролика.")
        audio = audio.subclip(0, video_duration)

    final_video = final_video.with_audio(audio)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    print(f"💾 Сохраняю видео в: {output_path}")

    try:
        final_video.write_videofile(
            output_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            logger="bar"
        )
        print(f"✅ Готово! Видео сохранено: {output_path}")
    finally:
        for clip in clips:
            clip.close()
        audio.close()
        final_video.close()


if __name__ == "__main__":
    create_video()