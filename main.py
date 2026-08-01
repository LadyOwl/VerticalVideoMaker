import os
import numpy as np
from PIL import Image, ImageOps
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from moviepy.audio.fx import AudioLoop

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
BACKGROUND_COLOR = (0, 0, 0)
FRAME_DURATION = 4
FPS = 30
FIT_MODE = 'cover'


def prepare_image(image_path):
    img = Image.open(image_path).convert("RGB")
    if FIT_MODE == 'cover':
        return ImageOps.fit(img, (TARGET_WIDTH, TARGET_HEIGHT), method=Image.Resampling.LANCZOS, bleed=0.0,
                            centering=(0.5, 0.5))
    else:
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

def create_video(image_dir, audio_path, output_path, status_callback=None, progress_callback=None):
    def log(msg):
        if status_callback:
            status_callback(msg)
        print(msg)

    def update_progress(percent):
        if progress_callback:
            progress_callback(percent)

    image_paths = get_supported_files(image_dir, (".jpg", ".jpeg", ".png"))

    if not image_paths:
        log("❌ В папке не найдено картинок.")
        return False
    if not os.path.exists(audio_path):
        log("❌ Аудиофайл не найден.")
        return False

    log(f"🎵 Используем трек: {os.path.basename(audio_path)}")
    log(f" Найдено картинок: {len(image_paths)}")

    clips = []
    total_images = len(image_paths)

    for i, path in enumerate(image_paths):
        log(f"  → Обрабатываю: {os.path.basename(path)}")
        pil_image = prepare_image(path)
        frame_array = np.array(pil_image)
        clip = ImageClip(frame_array, duration=FRAME_DURATION).with_fps(FPS)
        clips.append(clip)

        update_progress((i + 1) / total_images * 50)

    log("⏳ Склеиваю клипы...")
    final_video = concatenate_videoclips(clips, method="compose")
    video_duration = final_video.duration

    log("🎵 Подключаю аудио...")
    audio = AudioFileClip(audio_path)
    if audio.duration < video_duration:
        audio = audio.with_effects([AudioLoop(duration=video_duration)])
    else:
        audio = audio.subclipped(0, video_duration)
    final_video = final_video.with_audio(audio)

    log(" Рендеринг видео (самый долгий этап)...")
    update_progress(60)

    try:
        final_video.write_videofile(
            output_path,
            fps=FPS, codec="libx264", audio_codec="aac",
            preset="medium", ffmpeg_params=["-movflags", "+faststart"],
            logger=None
        )
        update_progress(100)
        log("✅ Готово! Видео сохранено.")
        return True
    except Exception as e:
        log(f"❌ Ошибка при рендере: {str(e)}")
        return False
    finally:
        for clip in clips: clip.close()
        audio.close()
        final_video.close()