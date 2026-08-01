import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from main import create_video

# ================= НЕОНОВАЯ ПАЛИТРА =================
BG_COLOR = "#0a0e1a"
FRAME_COLOR = "#151a2e"
NEON_CYAN = "#00f5ff"
NEON_BLUE = "#0066ff"
NEON_PURPLE = "#b000ff"
NEON_PINK = "#ff006e"
NEON_GREEN = "#00ff88"
TEXT_COLOR = "#e0e0e0"
# =====================================================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class VerticalVideoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Vertical Video Maker | SocialLift")
        self.geometry("700x720")
        self.resizable(True, True)
        self.configure(fg_color=BG_COLOR)

        self.selected_images = []  # Список путей в порядке добавления
        self.audio_file_path = ctk.StringVar()
        self.is_generating = False

        self.setup_ui()

    def setup_ui(self):
        # Заголовок
        self.title_label = ctk.CTkLabel(
            self, text="⚡ Vertical Video Maker ⚡",
            font=ctk.CTkFont(size=30, weight="bold"), text_color=NEON_CYAN
        )
        self.title_label.pack(pady=15)

        # ================= БЛОК ИЗОБРАЖЕНИЙ =================
        self.image_frame = ctk.CTkFrame(
            self, corner_radius=20, fg_color=FRAME_COLOR,
            border_width=2, border_color=NEON_BLUE
        )
        self.image_frame.pack(pady=12, padx=25, fill="x")

        ctk.CTkLabel(
            self.image_frame, text="📁 Изображения",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=NEON_CYAN
        ).pack(pady=(12, 8))

        # Кнопки управления
        btn_frame = ctk.CTkFrame(self.image_frame, fg_color="transparent")
        btn_frame.pack(pady=5, padx=15, fill="x")

        self.add_btn = ctk.CTkButton(
            btn_frame, text="➕ Добавить", command=self.add_images,
            fg_color=NEON_BLUE, hover_color="#0088ff",
            border_width=2, border_color=NEON_CYAN, text_color=TEXT_COLOR,
            corner_radius=12, width=170, height=38,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.add_btn.pack(side="left", padx=10, pady=5)

        self.clear_btn = ctk.CTkButton(
            btn_frame, text="🗑 Очистить всё", command=self.clear_images,
            fg_color=NEON_PINK, hover_color="#ff3388",
            border_width=2, border_color="#ff66aa", text_color=TEXT_COLOR,
            corner_radius=12, width=170, height=38,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.clear_btn.pack(side="right", padx=10, pady=5)

        # Список файлов (скроллируемый)
        self.list_frame = ctk.CTkScrollableFrame(
            self.image_frame, corner_radius=12, fg_color="#0d1120",
            border_width=1, border_color=NEON_BLUE, height=160
        )
        self.list_frame.pack(pady=8, padx=15, fill="both", expand=True)

        self.empty_label = ctk.CTkLabel(
            self.list_frame, text="Файлы не выбраны",
            text_color="#666666", font=ctk.CTkFont(size=13)
        )
        self.empty_label.pack(pady=15)

        self.image_count_label = ctk.CTkLabel(
            self.image_frame, text="Выбрано: 0 изображений",
            text_color=NEON_CYAN, font=ctk.CTkFont(size=12, weight="bold")
        )
        self.image_count_label.pack(pady=5)

        # ================= БЛОК АУДИО =================
        self.audio_frame = ctk.CTkFrame(
            self, corner_radius=20, fg_color=FRAME_COLOR,
            border_width=2, border_color=NEON_PURPLE
        )
        self.audio_frame.pack(pady=12, padx=25, fill="x")

        ctk.CTkLabel(
            self.audio_frame, text="🎵 Аудиофайл",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=NEON_CYAN
        ).pack(pady=(12, 8))

        self.audio_entry = ctk.CTkEntry(
            self.audio_frame, textvariable=self.audio_file_path,
            placeholder_text="Файл не выбран...", state="readonly",
            corner_radius=12, border_width=2, border_color=NEON_PURPLE,
            fg_color="#0d1120", text_color=TEXT_COLOR,
            font=ctk.CTkFont(size=12)
        )
        self.audio_entry.pack(pady=5, padx=15, fill="x")

        audio_btn_frame = ctk.CTkFrame(self.audio_frame, fg_color="transparent")
        audio_btn_frame.pack(pady=8, padx=15, fill="x")

        self.audio_btn = ctk.CTkButton(
            audio_btn_frame, text="🎧 Выбрать аудио",
            command=self.select_audio_file,
            fg_color=NEON_PURPLE, hover_color="#cc33ff",
            border_width=2, border_color=NEON_CYAN, text_color=TEXT_COLOR,
            corner_radius=12, width=180, height=38,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.audio_btn.pack(side="left", padx=10, pady=5)

        self.remove_audio_btn = ctk.CTkButton(
            audio_btn_frame, text="✕ Удалить",
            command=self.remove_audio,
            fg_color=NEON_PINK, hover_color="#ff3388",
            border_width=2, border_color="#ff66aa", text_color=TEXT_COLOR,
            corner_radius=12, width=180, height=38,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.remove_audio_btn.pack(side="right", padx=10, pady=5)

        # ================= КНОПКА ГЕНЕРАЦИИ =================
        self.generate_btn = ctk.CTkButton(
            self, text="🎬 СОЗДАТЬ ВИДЕО",
            font=ctk.CTkFont(size=20, weight="bold"),
            command=self.start_generation,
            fg_color=NEON_GREEN, hover_color="#33ffaa",
            border_width=3, border_color=NEON_CYAN, text_color="#000000",
            corner_radius=18, height=60, width=330
        )
        self.generate_btn.pack(pady=20)

        # ================= ПРОГРЕСС И СТАТУС =================
        self.progress_frame = ctk.CTkFrame(
            self, corner_radius=15, fg_color=FRAME_COLOR,
            border_width=1, border_color=NEON_BLUE
        )
        self.progress_frame.pack(pady=8, padx=25, fill="x")

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame, orientation="horizontal", mode="determinate",
            fg_color="#1a2e1a", progress_color=NEON_CYAN,
            height=18, corner_radius=10
        )
        self.progress_bar.pack(pady=12, padx=15, fill="x")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self, text="Готов к работе. Добавьте изображения и аудио.",
            text_color=TEXT_COLOR, font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=8)

    def add_images(self):
        """Добавляет файлы В ТОМ ПОРЯДКЕ, в котором их выбрал пользователь"""
        files = filedialog.askopenfilenames(
            title="Выберите изображения",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if files:
            # 🔥 БЕЗ сортировки — сохраняем порядок выбора
            self.selected_images.extend(files)
            self.update_files_list()
            self.update_status(f"✓ Добавлено: {len(files)} изобр.")

    def clear_images(self):
        self.selected_images = []
        self.update_files_list()
        self.update_status("Список изображений очищен")

    def remove_image(self, index):
        """Удаляет конкретный файл из списка по индексу"""
        if 0 <= index < len(self.selected_images):
            self.selected_images.pop(index)
            self.update_files_list()
            self.update_status(f"Удалено изображение #{index + 1}")

    def move_image_up(self, index):
        """Перемещает файл вверх в списке"""
        if index > 0:
            self.selected_images[index], self.selected_images[index - 1] = \
                self.selected_images[index - 1], self.selected_images[index]
            self.update_files_list()

    def move_image_down(self, index):
        """Перемещает файл вниз в списке"""
        if index < len(self.selected_images) - 1:
            self.selected_images[index], self.selected_images[index + 1] = \
                self.selected_images[index + 1], self.selected_images[index]
            self.update_files_list()

    def remove_audio(self):
        self.audio_file_path.set("")
        self.update_status("Аудио удалено")

    def update_files_list(self):
        """Перерисовывает список файлов с кнопками управления"""
        # Очищаем текущий список
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.selected_images:
            self.empty_label = ctk.CTkLabel(
                self.list_frame, text="Файлы не выбраны",
                text_color="#666666", font=ctk.CTkFont(size=13)
            )
            self.empty_label.pack(pady=15)
        else:
            for i, file_path in enumerate(self.selected_images):
                file_name = os.path.basename(file_path)

                # Создаем строку для каждого файла
                row_frame = ctk.CTkFrame(
                    self.list_frame, fg_color="transparent",
                    corner_radius=8
                )
                row_frame.pack(pady=2, padx=5, fill="x")

                # Номер и имя файла
                name_label = ctk.CTkLabel(
                    row_frame, text=f"{i + 1}. {file_name}",
                    text_color=TEXT_COLOR, justify="left", anchor="w",
                    font=ctk.CTkFont(size=12)
                )
                name_label.pack(side="left", padx=5, fill="x", expand=True)

                # Кнопка "Вверх"
                up_btn = ctk.CTkButton(
                    row_frame, text="↑", width=35, height=28,
                    fg_color=NEON_BLUE, hover_color="#0088ff",
                    text_color=TEXT_COLOR, corner_radius=8,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=lambda idx=i: self.move_image_up(idx)
                )
                up_btn.pack(side="left", padx=2)

                # Кнопка "Вниз"
                down_btn = ctk.CTkButton(
                    row_frame, text="↓", width=35, height=28,
                    fg_color=NEON_BLUE, hover_color="#0088ff",
                    text_color=TEXT_COLOR, corner_radius=8,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=lambda idx=i: self.move_image_down(idx)
                )
                down_btn.pack(side="left", padx=2)

                # Кнопка "Удалить"
                del_btn = ctk.CTkButton(
                    row_frame, text="", width=35, height=28,
                    fg_color=NEON_PINK, hover_color="#ff3388",
                    text_color=TEXT_COLOR, corner_radius=8,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=lambda idx=i: self.remove_image(idx)
                )
                del_btn.pack(side="left", padx=2)

        # Обновляем счетчик
        count = len(self.selected_images)
        if count > 0:
            self.image_count_label.configure(
                text=f"Выбрано: {count} изобр. (~{count * 4} сек.)"
            )
        else:
            self.image_count_label.configure(text="Выбрано: 0 изображений")

    def select_audio_file(self):
        file = filedialog.askopenfilename(
            title="Выберите аудиофайл",
            filetypes=[("Audio files", "*.mp3 *.wav")]
        )
        if file:
            self.audio_file_path.set(file)
            self.update_status(f"✓ Аудио: {os.path.basename(file)}")

    def update_status(self, text):
        self.status_label.configure(text=text)

    def update_progress(self, value):
        self.after(0, self.progress_bar.set, value / 100.0)

    def start_generation(self):
        if self.is_generating:
            return
        if not self.selected_images:
            messagebox.showwarning("Внимание", "Добавьте изображения!")
            return
        audio_path = self.audio_file_path.get()
        if not audio_path:
            messagebox.showwarning("Внимание", "Выберите аудиофайл!")
            return

        self.is_generating = True
        self.generate_btn.configure(state="disabled", text="⏳ Генерация...")
        self.add_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")
        self.audio_btn.configure(state="disabled")
        self.remove_audio_btn.configure(state="disabled")
        self.progress_bar.set(0)

        output_path = os.path.join("output", "final_video.mp4")
        os.makedirs("output", exist_ok=True)

        thread = threading.Thread(
            target=self.run_engine,
            args=(self.selected_images.copy(), audio_path, output_path)
        )
        thread.start()

    def run_engine(self, image_list, audio_path, output_path):
        try:
            success = create_video(
                image_list, audio_path, output_path,
                status_callback=self.update_status,
                progress_callback=self.update_progress
            )
            if success:
                self.after(0, lambda: messagebox.showinfo(
                    "✓ Успех!",
                    f"Видео создано!\n\n{os.path.abspath(output_path)}"
                ))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Ошибка", str(e)))
        finally:
            self.after(0, self.finish_generation)

    def finish_generation(self):
        self.is_generating = False
        self.generate_btn.configure(state="normal", text="🎬 СОЗДАТЬ ВИДЕО")
        self.add_btn.configure(state="normal")
        self.clear_btn.configure(state="normal")
        self.audio_btn.configure(state="normal")
        self.remove_audio_btn.configure(state="normal")


if __name__ == "__main__":
    app = VerticalVideoApp()
    app.mainloop()