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
# Целевое разрешение для вертикальных видео (Stories, Reels, Shorts)
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

# Длительность показа одного кадра (в секундах)
FRAME_DURATION = 4

# Частота кадров в секунду (стандарт для соцсетей)
# 24 FPS достаточно для слайд-шоу и экономит время рендеринга
FPS = 24


# =========================================================


def prepare_image(image_path: str) -> Image.Image:
    """
    Адаптирует изображение под вертикальный формат 1080x1920 БЕЗ обрезки.

    Логика:
    1. Создает красивый размытый фон из самого изображения (заполняет весь экран).
    2. Вписывает оригинальное изображение целиком по центру.
    Это гарантирует, что ни одна часть фото не будет потеряна,
    а видео будет выглядеть профессионально (эффект как в Instagram/TikTok).

    Args:
        image_path: Путь к исходному изображению.

    Returns:
        Объект PIL.Image размером 1080x1920.
    """
    # Открываем изображение и приводим к RGB (на случай PNG с прозрачностью)
    img = Image.open(image_path).convert("RGB")

    img_ratio = img.width / img.height
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT

    # --- Шаг 1: Создание размытого фона ---
    # Масштабируем картинку так, чтобы она заполнила весь холст 1080x1920
    if img_ratio > target_ratio:
        bg_width = TARGET_WIDTH
        bg_height = int(TARGET_WIDTH / img_ratio)
    else:
        bg_height = TARGET_HEIGHT
        bg_width = int(TARGET_HEIGHT * img_ratio)

    bg_resized = img.resize((bg_width, bg_height), Image.Resampling.LANCZOS)

    # Вставляем на черный холст
    bg_canvas = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0))
    bg_x = (TARGET_WIDTH - bg_width) // 2
    bg_y = (TARGET_HEIGHT - bg_height) // 2
    bg_canvas.paste(bg_resized, (bg_x, bg_y))

    # Применяем сильное размытие и затемнение для фона
    bg_blurred = bg_canvas.filter(ImageFilter.GaussianBlur(radius=30))
    enhancer = ImageEnhance.Brightness(bg_blurred)
    bg_final = enhancer.enhance(0.5)  # Затемняем фон на 50%

    # --- Шаг 2: Вставка оригинала без обрезки ---
    # Масштабируем оригинал так, чтобы он целиком поместился в 1080x1920
    if img_ratio > target_ratio:
        new_width = TARGET_WIDTH
        new_height = int(TARGET_WIDTH / img_ratio)
    else:
        new_height = TARGET_HEIGHT
        new_width = int(TARGET_HEIGHT * img_ratio)

    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Центрируем оригинал на размытом фоне
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
    """
    Главная функция создания видео. Принимает список путей и собирает ролик.

    Args:
        image_paths: Список путей к изображениям (в порядке добавления).
        audio_path: Путь к аудиофайлу (MP3/WAV).
        output_path: Путь для сохранения готового .mp4 файла.
        status_callback: Функция для отправки текстовых статусов в GUI.
        progress_callback: Функция для обновления прогресс-бара (0-100).

    Returns:
        True, если видео успешно создано, иначе False.
    """

    # Вспомогательные функции для безопасной связи с GUI
    def log(msg: str):
        if status_callback:
            status_callback(msg)
        print(msg)

    def update_progress(percent: float):
        if progress_callback:
            progress_callback(percent)

    # 1. Валидация входных данных
    if not image_paths:
        log("❌ Список изображений пуст.")
        return False

    if not os.path.exists(audio_path):
        log("❌ Аудиофайл не найден.")
        return False

    # Фильтруем только существующие файлы
    valid_paths = []
    for path in image_paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            log(f"️ Файл не найден и будет пропущен: {os.path.basename(path)}")

    if not valid_paths:
        log("❌ Ни один из файлов не найден.")
        return False

    log(f"🎵 Трек: {os.path.basename(audio_path)}")
    log(f"🖼 Изображений: {len(valid_paths)}")

    # 2. Создание видеоклипов из изображений
    clips = []
    total = len(valid_paths)

    for i, path in enumerate(valid_paths):
        log(f"  [{i + 1}/{total}] {os.path.basename(path)}")
        try:
            pil_image = prepare_image(path)
            frame_array = np.array(pil_image)

            # Создаем клип. Размер 1080x1920 определяется автоматически из массива
            clip = ImageClip(
                frame_array,
                duration=FRAME_DURATION
            ).with_fps(FPS)

            clips.append(clip)
            # Обновляем прогресс (первые 50% работы)
            update_progress((i + 1) / total * 50)
        except Exception as e:
            log(f"❌ Ошибка обработки {os.path.basename(path)}: {str(e)}")

    if not clips:
        log("❌ Не удалось создать ни один клип.")
        return False

    # 3. Склейка клипов в единый видеоряд
    log(" Склейка клипов...")
    final_video = concatenate_videoclips(clips, method="compose")
    video_duration = final_video.duration

    # 4. Обработка и наложение аудио
    log(" Подключение аудио...")
    try:
        audio = AudioFileClip(audio_path)

        # Если трек короче видео — зацикливаем его
        if audio.duration < video_duration:
            audio = audio.with_effects([AudioLoop(duration=video_duration)])
        # Если трек длиннее — обрезаем под длительность видео
        else:
            audio = audio.subclipped(0, video_duration)

        final_video = final_video.with_audio(audio)
    except Exception as e:
        log(f"❌ Ошибка работы с аудио: {str(e)}")
        return False

    # 5. Финальный рендеринг и экспорт
    log("🎬 Рендеринг видео (это может занять несколько минут)...")
    update_progress(60)

    try:
        # 🔥 ОПТИМИЗАЦИЯ ДЛЯ УСКОРЕНИЯ РЕНДЕРИНГА:
        # preset="ultrafast" - самый быстрый пресет (в 5-10 раз быстрее medium)
        # crf="28" - качество (28 = чуть ниже стандартного, но для соцсетей незаметно)
        # threads="0" - использовать все ядра процессора

        final_video.write_videofile(
            output_path,
            fps=FPS,
            codec="libx264",  # Стандартный видеокодек H.264
            audio_codec="aac",  # Стандартный аудиокодек для MP4
            preset="superfast",  
            ffmpeg_params=[
                "-movflags", "+faststart",  # Оптимизация для стриминга/соцсетей
                "-crf", "30",
                "-threads", "0"  # Использовать все ядра CPU
            ],
            logger=None  # Отключаем вывод ffmpeg в консоль
        )
        update_progress(100)
        log(f"✅ Готово! Видео сохранено: {output_path}")
        return True

    except Exception as e:
        log(f"❌ Ошибка при рендере: {str(e)}")
        return False

    finally:
        # 6. Очистка ресурсов (Критически важно для безопасности и памяти!)
        # Закрываем все клипы, аудио и финальное видео, чтобы освободить файлы
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