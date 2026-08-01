import os
import numpy as np
from PIL import Image, ImageOps, ImageFilter
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from moviepy.audio.fx import AudioLoop

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
BACKGROUND_COLOR = (0, 0, 0)
FRAME_DURATION = 4
FPS = 30

def create_blurred_background(img):
    bg = ImageOps.fit(
        img,
        (TARGET_WIDTH, TARGET_HEIGHT),
        method=Image.Resampling.LANCZOS,
        bleed=0.0,
        centering=(0.5, 0.5)
    )

    bg = bg.filter(ImageFilter.GaussianBlur(radius=25))
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.6)
    return bg


def prepare_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img_ratio = img.width / img.height
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT

    if img_ratio > target_ratio:
        background = create_blurred_background(img)

        new_height = TARGET_HEIGHT
        new_width = int(TARGET_HEIGHT * img_ratio)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        x_offset = (TARGET_WIDTH - new_width) // 2
        y_offset = 0
        background.paste(img_resized, (x_offset, y_offset))
        return background
    else:
        return ImageOps.fit(
            img,
            (TARGET_WIDTH, TARGET_HEIGHT),
            method=Image.Resampling.LANCZOS,
            bleed=0.0,
            centering=(0.5, 0.5)
        )


def create_video(image_paths, audio_path, output_path, status_callback=None, progress_callback=None):
    def log(msg):
        if status_callback:
            status_callback(msg)
        print(msg)

    def update_progress(percent):
        if progress_callback:
            progress_callback(percent)

    if not image_paths:
        log("❌ Список изображений пуст.")
        return False

    if not os.path.exists(audio_path):
        log("❌ Аудиофайл не найден.")
        return False

    valid_paths = []
    for path in image_paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            log(f"⚠️ Файл не найден: {os.path.basename(path)}")

    if not valid_paths:
        log(" Ни один из файлов не найден.")
        return False

    log(f"🎵 Трек: {os.path.basename(audio_path)}")
    log(f"🖼 Изображений: {len(valid_paths)}")

    clips = []
    total = len(valid_paths)

    for i, path in enumerate(valid_paths):
        log(f"  [{i + 1}/{total}] {os.path.basename(path)}")
        try:
            pil_image = prepare_image(path)
            frame_array = np.array(pil_image)
            clip = ImageClip(frame_array, duration=FRAME_DURATION).with_fps(FPS)
            clips.append(clip)
            update_progress((i + 1) / total * 50)
        except Exception as e:
            log(f" Ошибка: {os.path.basename(path)} — {str(e)}")

    if not clips:
        log("❌ Не удалось создать клипы.")
        return False

    log("⏳ Склейка клипов...")
    final_video = concatenate_videoclips(clips, method="compose")
    video_duration = final_video.duration

    log(" Подключение аудио...")
    try:
        audio = AudioFileClip(audio_path)
        if audio.duration < video_duration:
            audio = audio.with_effects([AudioLoop(duration=video_duration)])
        else:
            audio = audio.subclipped(0, video_duration)
        final_video = final_video.with_audio(audio)
    except Exception as e:
        log(f"❌ Ошибка аудио: {str(e)}")
        return False

    log(" Рендеринг...")
    update_progress(60)

    try:
        final_video.write_videofile(
            output_path,
            fps=FPS, codec="libx264", audio_codec="aac",
            preset="medium", ffmpeg_params=["-movflags", "+faststart"],
            logger=None
        )
        update_progress(100)
        log(f"✅ Готово: {output_path}")
        return True
    except Exception as e:
        log(f"❌ Ошибка рендера: {str(e)}")
        return False
    finally:
        for clip in clips:
            try:
                clip.close()
            except:
                pass
        try:
            audio.close()
            final_video.close()
        except:
            pass