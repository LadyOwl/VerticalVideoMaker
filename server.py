import os
import shutil
import uuid
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Импортируем наш движок
from main import create_video

app = FastAPI(title="Vertical Video Maker API")

# ================= НАСТРОЙКИ БЕЗОПАСНОСТИ И ЛИМИТЫ =================
MAX_IMAGES_COUNT = 50  # Максимальное количество изображений за один запрос
MAX_FILE_SIZE_MB = 50  # Максимальный размер одного файла в МБ
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Разрешенные MIME-типы (строгая проверка содержимого, а не только расширения)
ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/jpg"}
ALLOWED_AUDIO_MIMES = {"audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp3"}
# ===================================================================

TEMP_DIR = "temp_uploads"
OUTPUT_DIR = "output"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Отдает главную HTML-страницу"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/generate")
async def generate_video(
        images: list[UploadFile] = File(...),
        audio: UploadFile = File(...)
):
    # 1. Проверка лимита количества файлов
    if len(images) > MAX_IMAGES_COUNT:
        raise HTTPException(
            status_code=400,
            detail=f"Слишком много изображений. Максимум: {MAX_IMAGES_COUNT}"
        )

    if not images:
        raise HTTPException(status_code=400, detail="Не загружено ни одного изображения")

    session_id = str(uuid.uuid4())
    session_dir = os.path.join(TEMP_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    image_paths = []
    audio_path = None

    try:
        # 2. Обработка и проверка изображений
        for img in images:
            # Проверка MIME-типа
            if img.content_type not in ALLOWED_IMAGE_MIMES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Недопустимый формат файла '{img.filename}'. Разрешены только изображения (JPEG, PNG)."
                )

            # Проверка размера файла
            content = await img.read()
            if len(content) > MAX_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"Файл '{img.filename}' слишком большой. Максимальный размер: {MAX_FILE_SIZE_MB} МБ."
                )

            # Возвращаем указатель файла в начало, чтобы его можно было сохранить
            img.file.seek(0)

            # Очистка имени файла от опасных символов
            safe_filename = "".join(c for c in (img.filename or "image") if c.isalnum() or c in "._- ")
            file_path = os.path.join(session_dir, safe_filename)

            with open(file_path, "wb") as f:
                f.write(content)

            image_paths.append(file_path)

        # 3. Обработка и проверка аудио
        if audio.content_type not in ALLOWED_AUDIO_MIMES:
            raise HTTPException(
                status_code=400,
                detail=f"Недопустимый формат аудио '{audio.filename}'. Разрешены только MP3 или WAV."
            )

        audio_content = await audio.read()
        if len(audio_content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Аудиофайл слишком большой. Максимальный размер: {MAX_FILE_SIZE_MB} МБ."
            )

        audio.file.seek(0)
        safe_audio_name = "".join(c for c in (audio.filename or "audio") if c.isalnum() or c in "._- ")
        audio_path = os.path.join(session_dir, safe_audio_name)

        with open(audio_path, "wb") as f:
            f.write(audio_content)

        # 4. Формирование пути для готового видео
        output_filename = f"video_{session_id}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # 5. Запуск генерации в отдельном потоке
        try:
            loop = asyncio.get_running_loop()
            success = await loop.run_in_executor(
                None,
                create_video,
                image_paths,
                audio_path,
                output_path
            )
        except Exception as e:
            print(f"ОШИБКА В ПОТОКЕ ГЕНЕРАЦИИ: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка движка MoviePy: {str(e)}")

        if not success:
            raise HTTPException(status_code=500, detail="Ошибка при создании видео. Проверьте логи.")

        # 6. Возврат готового файла пользователю
        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename="vertical_video.mp4"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА СЕРВЕРА: {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

    finally:
        # 7. Очистка временных файлов (безопасность и экономия места)
        shutil.rmtree(session_dir, ignore_errors=True)