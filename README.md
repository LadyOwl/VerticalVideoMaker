# ⚡ Vertical Video Maker

> Автоматизированный генератор вертикальных видеороликов (1080×1920) из изображений и аудио.

Идеально подходит для создания контента для **Instagram Reels**, **YouTube Shorts**, **TikTok** и **Stories**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![MoviePy](https://img.shields.io/badge/MoviePy-2.x-orange)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

---

# 📑 Содержание

- [О проекте](#-о-проекте)
- [Возможности](#-возможности)
- [Стек технологий](#-стек-технологий)
- [Структура проекта](#-структура-проекта)
- [Установка](#-установка-и-запуск)
- [Создание EXE](#-создание-exe-файла)
- [Решение проблем](#-решение-проблем)
- [Соответствие ТЗ](#-соответствие-тз)
- [Автор](#-автор)
- [Лицензия](#-лицензия)

---

# 🎯 О проекте

**Vertical Video Maker** — инструмент для автоматической сборки вертикальных видеороликов из изображений и музыкального сопровождения.

Проект разработан для **SocialLift Studio** и позволяет создавать промо-видео всего за несколько кликов.

---

# ✨ Возможности

- 📷 Автоматическая адаптация изображений под формат **9:16**
- 🎵 Автоматическая обрезка или зацикливание аудио
- ⚡ Быстрый рендеринг благодаря оптимизированным настройкам FFmpeg
- 🌐 Современный веб-интерфейс
- 📱 Поддержка мобильных устройств
- 📂 Изменение порядка изображений
- 🧹 Автоматическая очистка временных файлов
- 💻 Поддержка Windows, Linux и macOS

---

# 🛠 Стек технологий

| Компонент | Технологии |
|-----------|------------|
| Backend | FastAPI, Uvicorn |
| Видео | MoviePy 2.x |
| Изображения | Pillow |
| Численные вычисления | NumPy |
| FFmpeg | imageio-ffmpeg |
| Frontend | HTML5, CSS3, JavaScript |
| Язык | Python 3.10+ |

---

# 📂 Структура проекта

```text
VerticalVideoMaker/
│
├── main.py
├── server.py
├── gui.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   └── index.html
│
├── temp_uploads/
│
└── output/
```

---

# 🚀 Установка и запуск

## 1. Клонирование проекта

```bash
git clone https://github.com/LadyOwl/VerticalVideoMaker.git
cd VerticalVideoMaker
```

---

## 2. Создание виртуального окружения

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## 4. Запуск веб-версии

```bash
uvicorn server:app --reload
```

После запуска откройте браузер:

```
http://127.0.0.1:8000
```

---

## Альтернатива — Desktop GUI

```bash
python gui.py
```

---

# 📦 Создание EXE файла

Установите PyInstaller:

```bash
pip install pyinstaller
```

Соберите приложение:

```bash
pyinstaller ^
    --onefile ^
    --windowed ^
    --name VerticalVideoMaker ^
    gui.py
```

Для Linux/macOS:

```bash
pyinstaller --onefile --windowed --name VerticalVideoMaker gui.py
```

---

# ⚠️ Решение проблем

## Антивирус блокирует программу

Добавьте папку проекта в список исключений.

---

## FFmpeg не найден

```bash
pip install imageio-ffmpeg
```

---

## Медленный рендеринг

Рекомендуется закрыть ресурсоёмкие приложения.

В проекте уже используются:

- `preset="ultrafast"`
- многопоточность
- оптимизированное кодирование

---

# ✅ Соответствие техническому заданию

- ✅ Поддержка JPG и PNG
- ✅ Поддержка MP3 и WAV
- ✅ Видео 1080×1920
- ✅ Длительность кадра — 4 секунды
- ✅ Автоматическая подгонка аудио
- ✅ Экспорт MP4 (24 FPS)
- ✅ Веб-интерфейс
- ✅ Progress Bar
- ✅ Комментарии по PEP 8
- ✅ Модульная структура проекта
- ✅ README
- ✅ requirements.txt
- ✅ .gitignore

---

# 👨‍💻 Автор

Разработано для **SocialLift Studio**.

---

# 📄 Лицензия

Проект разработан по индивидуальному заказу.

Все права принадлежат заказчику.
=======


