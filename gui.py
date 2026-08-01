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
        self.geometry("600x550")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)

        self.image_folder_path = ctk.StringVar()
        self.audio_file_path = ctk.StringVar()
        self.is_generating = False

        self.setup_ui()

    def setup_ui(self):
        self.title_label = ctk.CTkLabel(self, text="Vertical Video Maker", font=ctk.CTkFont(size=28, weight="bold"),
                                        text_color=NEON_CYAN)
        self.title_label.pack(pady=20)

        self.image_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=FRAME_COLOR)
        self.image_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.image_frame, text="📁 Папка с изображениями", font=ctk.CTkFont(size=14, weight="bold")).pack(
            pady=(15, 5))
        self.image_entry = ctk.CTkEntry(self.image_frame, textvariable=self.image_folder_path,
                                        placeholder_text="Путь к папке не выбран...", state="readonly",
                                        corner_radius=10)
        self.image_entry.pack(pady=5, padx=15, fill="x")
        self.image_btn = ctk.CTkButton(self.image_frame, text="Выбрать папку", command=self.select_image_folder,
                                       fg_color=NEON_BLUE, hover_color="#00a3ff", corner_radius=10)
        self.image_btn.pack(pady=10)

        # Блок аудио
        self.audio_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=FRAME_COLOR)
        self.audio_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.audio_frame, text=" Аудиофайл (MP3/WAV)", font=ctk.CTkFont(size=14, weight="bold")).pack(
            pady=(15, 5))
        self.audio_entry = ctk.CTkEntry(self.audio_frame, textvariable=self.audio_file_path,
                                        placeholder_text="Файл не выбран...", state="readonly", corner_radius=10)
        self.audio_entry.pack(pady=5, padx=15, fill="x")
        self.audio_btn = ctk.CTkButton(self.audio_frame, text="Выбрать файл", command=self.select_audio_file,
                                       fg_color=NEON_BLUE, hover_color="#00a3ff", corner_radius=10)
        self.audio_btn.pack(pady=10)

        self.generate_btn = ctk.CTkButton(self, text="🎬 Создать видео", font=ctk.CTkFont(size=20, weight="bold"),
                                          command=self.start_generation, fg_color=NEON_CYAN, hover_color="#00c8d4",
                                          text_color="#000000", corner_radius=15, height=55, width=300)
        self.generate_btn.pack(pady=30)

        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate")
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, text="Готов к работе. Выберите файлы.", text_color="#aaaaaa")
        self.status_label.pack(pady=5)

    def select_image_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку с картинками")
        if folder:
            self.image_folder_path.set(folder)
            self.update_status(f"Папка выбрана: {os.path.basename(folder)}")

    def select_audio_file(self):
        file = filedialog.askopenfilename(title="Выберите аудиофайл", filetypes=[("Audio files", "*.mp3 *.wav")])
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

        image_dir = self.image_folder_path.get()
        audio_path = self.audio_file_path.get()

        if not image_dir or not audio_path:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите папку с картинками и аудиофайл!")
            return

        self.is_generating = True
        self.generate_btn.configure(state="disabled", text="⏳ Генерация...")
        self.progress_bar.set(0)

        output_path = os.path.join("output", "final_video.mp4")
        os.makedirs("output", exist_ok=True)

        thread = threading.Thread(target=self.run_engine, args=(image_dir, audio_path, output_path))
        thread.start()

    def run_engine(self, image_dir, audio_path, output_path):
        try:
            success = create_video(
                image_dir,
                audio_path,
                output_path,
                status_callback=self.update_status,
                progress_callback=self.update_progress
            )

            if success:
                self.after(0, lambda: messagebox.showinfo("Успех!",
                                                          f"Видео успешно создано!\nПуть: {os.path.abspath(output_path)}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}"))
        finally:
            self.after(0, self.finish_generation)

    def finish_generation(self):
        self.is_generating = False
        self.generate_btn.configure(state="normal", text="🎬 Создать видео")


if __name__ == "__main__":
    app = VerticalVideoApp()
    app.mainloop()