import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uuid
import asyncio

# Импортируем наш движок
from main import create_video

app = FastAPI(title="Vertical Video Maker API")

# Папка для временных файлов и готовых видео
TEMP_DIR = "temp_uploads"
OUTPUT_DIR = "output"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Подключаем папку со статикой (HTML, CSS)
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
    """
    Принимает картинки и аудио, создает видео и возвращает файл.
    """
    # 1. Генерируем уникальное имя для временной папки, чтобы не было конфликтов
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(TEMP_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    image_paths = []
    audio_path = None

    try:
        # 2. Сохраняем загруженные картинки
        for img in images:
            # Проверяем расширение
            if img.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(session_dir, img.filename)
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(img.file, f)
                image_paths.append(file_path)
            else:
                raise HTTPException(status_code=400, detail=f"Неподдерживаемый формат картинки: {img.filename}")

        if not image_paths:
            raise HTTPException(status_code=400, detail="Не загружено ни одного изображения")

        # 3. Сохраняем аудио
        if audio.filename.lower().endswith(('.mp3', '.wav')):
            audio_path = os.path.join(session_dir, audio.filename)
            with open(audio_path, "wb") as f:
                shutil.copyfileobj(audio.file, f)
        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат аудио")

        # 4. Формируем путь для готового видео
        output_filename = f"video_{session_id}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # 5. Запускаем генерацию в отдельном потоке, чтобы не блокировать сервер
        # (create_video - синхронная функция)
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            None,
            create_video,
            image_paths,
            audio_path,
            output_path
        )

        if not success:
            raise HTTPException(status_code=500, detail="Ошибка при создании видео. Проверьте логи.")

        # 6. Возвращаем готовый видеофайл пользователю
        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename="vertical_video.mp4"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

    finally:
        # 7. Очистка временных файлов (безопасность и экономия места)
        shutil.rmtree(session_dir, ignore_errors=True)