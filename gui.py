import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from main import create_video

BG_COLOR = "#0f111a"
FRAME_COLOR = "#1a1d2e"
NEON_BLUE = "#0077ff"
NEON_CYAN = "#00f0ff"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class VerticalVideoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Vertical Video Maker | SocialLift")
        self.geometry("650x650")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)

        self.selected_images = []
        self.audio_file_path = ctk.StringVar()
        self.is_generating = False

        self.setup_ui()

    def setup_ui(self):
        self.title_label = ctk.CTkLabel(self, text="Vertical Video Maker", font=ctk.CTkFont(size=28, weight="bold"),
                                        text_color=NEON_CYAN)
        self.title_label.pack(pady=15)

        self.image_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=FRAME_COLOR)
        self.image_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.image_frame, text="📁 Изображения для видео", font=ctk.CTkFont(size=14, weight="bold")).pack(
            pady=(15, 5))

        btn_frame = ctk.CTkFrame(self.image_frame, fg_color="transparent")
        btn_frame.pack(pady=5, padx=15, fill="x")

        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Добавить изображения",
            command=self.add_images,
            fg_color=NEON_BLUE,
            hover_color="#00a3ff",
            corner_radius=10,
            width=200
        )
        self.add_btn.pack(pady=5)

        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑 Очистить список",
            command=self.clear_images,
            fg_color="#ff4444",
            hover_color="#ff6666",
            corner_radius=10,
            width=200
        )
        self.clear_btn.pack(pady=5)

        self.list_frame = ctk.CTkScrollableFrame(self.image_frame, corner_radius=10, fg_color="#0d0f16")
        self.list_frame.pack(pady=10, padx=15, fill="both", expand=True)

        self.files_label = ctk.CTkLabel(self.list_frame, text="Файлы не выбраны", text_color="#666666", justify="left")
        self.files_label.pack(pady=10)

        self.image_count_label = ctk.CTkLabel(self.image_frame, text="Выбрано: 0 изображений", text_color=NEON_CYAN)
        self.image_count_label.pack(pady=5)

        self.audio_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=FRAME_COLOR)
        self.audio_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.audio_frame, text="🎵 Аудиофайл (MP3/WAV)", font=ctk.CTkFont(size=14, weight="bold")).pack(
            pady=(15, 5))

        self.audio_entry = ctk.CTkEntry(self.audio_frame, textvariable=self.audio_file_path,
                                        placeholder_text="Файл не выбран...", state="readonly", corner_radius=10)
        self.audio_entry.pack(pady=5, padx=15, fill="x")

        self.audio_btn = ctk.CTkButton(
            self.audio_frame,
            text="Выбрать аудио",
            command=self.select_audio_file,
            fg_color=NEON_BLUE,
            hover_color="#00a3ff",
            corner_radius=10
        )
        self.audio_btn.pack(pady=10)

        self.generate_btn = ctk.CTkButton(
            self,
            text="🎬 Создать видео",
            font=ctk.CTkFont(size=20, weight="bold"),
            command=self.start_generation,
            fg_color=NEON_CYAN,
            hover_color="#00c8d4",
            text_color="#000000",
            corner_radius=15,
            height=55,
            width=300
        )
        self.generate_btn.pack(pady=25)

        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate")
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, text="Готов к работе. Добавьте изображения и аудио.",
                                         text_color="#aaaaaa")
        self.status_label.pack(pady=5)

    def add_images(self):
        files = filedialog.askopenfilenames(
            title="Выберите изображения",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )

        if files:
            self.selected_images.extend(files)
            self.update_files_list()
            self.update_status(f"Добавлено изображений: {len(files)}")

    def clear_images(self):
        self.selected_images = []
        self.update_files_list()
        self.update_status("Список изображений очищен")

    def update_files_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.selected_images:
            ctk.CTkLabel(self.list_frame, text="Файлы не выбраны", text_color="#666666", justify="left").pack(pady=10)
        else:
            for i, file_path in enumerate(self.selected_images, 1):
                file_name = os.path.basename(file_path)
                file_label = ctk.CTkLabel(
                    self.list_frame,
                    text=f"{i}. {file_name}",
                    text_color="#cccccc",
                    justify="left",
                    anchor="w"
                )
                file_label.pack(pady=2, padx=10, fill="x")

        count = len(self.selected_images)
        self.image_count_label.configure(text=f"Выбрано: {count} изображений")

        if count > 0:
            total_duration = count * 4
            self.image_count_label.configure(
                text=f"Выбрано: {count} изобр. (~{total_duration} сек.)"
            )

    def select_audio_file(self):
        file = filedialog.askopenfilename(
            title="Выберите аудиофайл",
            filetypes=[("Audio files", "*.mp3 *.wav")]
        )
        if file:
            self.audio_file_path.set(file)
            self.update_status(f"Аудио выбрано: {os.path.basename(file)}")

    def update_status(self, text):
        self.status_label.configure(text=text)

    def update_progress(self, value):
        self.after(0, self.progress_bar.set, value / 100.0)

    def start_generation(self):
        if self.is_generating:
            return

        if not self.selected_images:
            messagebox.showwarning("Внимание", "Пожалуйста, добавьте хотя бы одно изображение!")
            return

        audio_path = self.audio_file_path.get()
        if not audio_path:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите аудиофайл!")
            return

        self.is_generating = True
        self.generate_btn.configure(state="disabled", text=" Генерация...")
        self.add_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")
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
                image_list,
                audio_path,
                output_path,
                status_callback=self.update_status,
                progress_callback=self.update_progress
            )

            if success:
                self.after(0, lambda: messagebox.showinfo(
                    "Успех!",
                    f"Видео успешно создано!\n\nПуть: {os.path.abspath(output_path)}\nИзображений: {len(image_list)}"
                ))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}"))
        finally:
            self.after(0, self.finish_generation)

    def finish_generation(self):
        self.is_generating = False
        self.generate_btn.configure(state="normal", text="🎬 Создать видео")
        self.add_btn.configure(state="normal")
        self.clear_btn.configure(state="normal")


if __name__ == "__main__":
    app = VerticalVideoApp()
    app.mainloop()