"""
Vertical Video Maker - Движок генерации видео (Backend)
------------------------------------------------------
Этот модуль отвечает за обработку изображений, склейку видеоряда,
наложение аудио и финальный экспорт видеофайла.
Разработан для SocialLift Studio.
"""

import os
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from moviepy.audio.fx import AudioLoop

# ================= КОНСТАНТЫ И НАСТРОЙКИ =================
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
FRAME_DURATION = 4
FPS = 24  # 24 FPS достаточно для слайд-шоу и ускоряет рендер
# =========================================================

def prepare_image(image_path: str) -> Image.Image:
    """Адаптирует изображение под 1080x1920 с размытым фоном без обрезки."""
    img = Image.open(image_path).convert("RGB")
    img_ratio = img.width / img.height
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT

    if img_ratio > target_ratio:
        bg_width = TARGET_WIDTH
        bg_height = int(TARGET_WIDTH / img_ratio)
    else:
        bg_height = TARGET_HEIGHT
        bg_width = int(TARGET_HEIGHT * img_ratio)

    bg_resized = img.resize((bg_width, bg_height), Image.Resampling.LANCZOS)
    bg_canvas = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0))
    bg_x = (TARGET_WIDTH - bg_width) // 2
    bg_y = (TARGET_HEIGHT - bg_height) // 2
    bg_canvas.paste(bg_resized, (bg_x, bg_y))

    bg_blurred = bg_canvas.filter(ImageFilter.GaussianBlur(radius=30))
    enhancer = ImageEnhance.Brightness(bg_blurred)
    bg_final = enhancer.enhance(0.5)

    if img_ratio > target_ratio:
        new_width = TARGET_WIDTH
        new_height = int(TARGET_WIDTH / img_ratio)
    else:
        new_height = TARGET_HEIGHT
        new_width = int(TARGET_HEIGHT * img_ratio)

    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    x_offset = (TARGET_WIDTH - new_width) // 2
    y_offset = (TARGET_HEIGHT - new_height) // 2
    bg_final.paste(img_resized, (x_offset, y_offset))

    return bg_final

def create_video(
    image_paths: list[str],
    audio_path: str,
    output_path: str,
    status_callback: callable = None,
    progress_callback: callable = None
) -> bool:
    """Главная функция создания видео."""

    def log(msg: str):
        if status_callback:
            status_callback(msg)
        print(msg)

    def update_progress(percent: float):
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
        log("❌ Ни один из файлов не найден.")
        return False

    log(f"🎵 Трек: {os.path.basename(audio_path)}")
    log(f"🖼 Изображений: {len(valid_paths)}")

    clips = []
    total = len(valid_paths)

    for i, path in enumerate(valid_paths):
        log(f"  [{i+1}/{total}] {os.path.basename(path)}")
        try:
            pil_image = prepare_image(path)
            frame_array = np.array(pil_image)

            clip = ImageClip(
                frame_array,
                duration=FRAME_DURATION
            ).with_fps(FPS)

            clips.append(clip)
            update_progress((i + 1) / total * 50)
        except Exception as e:
            log(f"❌ Ошибка обработки {os.path.basename(path)}: {str(e)}")

    if not clips:
        log("❌ Не удалось создать ни один клип.")
        return False

    log("⏳ Склейка клипов...")
    final_video = concatenate_videoclips(clips, method="compose")
    video_duration = final_video.duration

    log("🎵 Подключение аудио...")
    try:
        audio = AudioFileClip(audio_path)
        if audio.duration < video_duration:
            audio = audio.with_effects([AudioLoop(duration=video_duration)])
        else:
            audio = audio.subclipped(0, video_duration)
        final_video = final_video.with_audio(audio)
    except Exception as e:
        log(f"❌ Ошибка работы с аудио: {str(e)}")
        return False

    log("🎬 Рендеринг видео (ускоренный режим)...")
    update_progress(60)

    try:
        # 🔥 ОПТИМИЗИРОВАННЫЙ БЛОК (все запятые на месте!)
        final_video.write_videofile(
            output_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            ffmpeg_params=[
                "-movflags", "+faststart",
                "-crf", "28",
                "-threads", "0"
            ],
            logger=None
        )
        update_progress(100)
        log(f"✅ Готово! Видео сохранено: {output_path}")
        return True

    except Exception as e:
        log(f"❌ Ошибка при рендере: {str(e)}")
        return False

    finally:
        for clip in clips:
            try:
                clip.close()
            except Exception:
                pass
        try:
            audio.close()
            final_video.close()
        except Exception:
            pass