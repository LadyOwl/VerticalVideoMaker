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

# Папки для временных файлов и готовых видео
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
    # Генерируем уникальное имя сессии
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(TEMP_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    image_paths = []
    audio_path = None

    try:
        # 1. Сохраняем картинки
        for img in images:
            if img.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Очищаем имя файла от спецсимволов, чтобы не было ошибок пути
                safe_filename = "".join(c for c in img.filename if c.isalnum() or c in "._- ")
                file_path = os.path.join(session_dir, safe_filename)

                with open(file_path, "wb") as f:
                    shutil.copyfileobj(img.file, f)
                image_paths.append(file_path)
            else:
                raise HTTPException(status_code=400, detail=f"Неподдерживаемый формат: {img.filename}")

        if not image_paths:
            raise HTTPException(status_code=400, detail="Не загружено ни одного изображения")

        # 2. Сохраняем аудио
        if audio.filename.lower().endswith(('.mp3', '.wav')):
            safe_audio_name = "".join(c for c in audio.filename if c.isalnum() or c in "._- ")
            audio_path = os.path.join(session_dir, safe_audio_name)
            with open(audio_path, "wb") as f:
                shutil.copyfileobj(audio.file, f)
        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат аудио")

        # 3. Путь для готового видео
        output_filename = f"video_{session_id}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # 4. Запуск генерации в отдельном потоке
        try:
            # ИСПРАВЛЕНИЕ: используем get_running_loop() для стабильности
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
            raise HTTPException(status_code=500, detail="Ошибка при создании видео.")

        # 5. Возвращаем файл пользователю
        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename="vertical_video.mp4"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"ОБЩАЯ ОШИБКА СЕРВЕРА: {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")

    finally:
        # Очистка временных файлов (безопасность)
        shutil.rmtree(session_dir, ignore_errors=True)