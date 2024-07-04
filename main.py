import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageEnhance, ImageDraw
import cv2

class ImageApp:
    """
    Класс для представления приложения обработки изображений.

    Атрибуты:
    root : tk.Tk
        Главное окно приложения Tkinter.
    image : PIL.Image
        Текущее загруженное изображение.
    canvas_frame : tk.Frame
        Фрейм, содержащий холст и полосы прокрутки.
    canvas : tk.Canvas
        Виджет холста для отображения изображений.
    v_scrollbar : tk.Scrollbar
        Вертикальная полоса прокрутки для холста.
    h_scrollbar : tk.Scrollbar
        Горизонтальная полоса прокрутки для холста.
    image_container : int
        Идентификатор контейнера изображения на холсте.
    channel_var : tk.StringVar
        Переменная для хранения выбранного цветового канала.
    """

    def __init__(self, root):
        """
        Конструктор для создания всех необходимых атрибутов объекта ImageApp.

        Параметры:
        root : tk.Tk
            Главное окно приложения Tkinter.
        """
        self.root = root
        self.root.title("Упрощенный графический редактор")
        self.root.geometry("1050x650")

        self.image = None

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg='light blue')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=self.v_scrollbar.set)

        self.h_scrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.config(xscrollcommand=self.h_scrollbar.set)

        self.image_container = self.canvas.create_image(0, 0, anchor=tk.NW)

        self.create_widgets()

    def create_widgets(self):
        """
        Создает основное окно
        """
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        button_width = 20  # Increase the button width to fit "Capture from Webcam"

        tk.Button(control_frame, text="Загрузить изображение", command=self.upload_image, width=button_width).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(control_frame, text="Снимок с камеры", command=self.capture_image, width=button_width).pack(side=tk.LEFT, padx=5, pady=5)

        self.channel_var = tk.StringVar(value="Цвет")
        tk.OptionMenu(control_frame, self.channel_var, "Красный", "Зеленый", "Синий").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(control_frame, text="Показать канал", command=self.show_channel, width=button_width).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(control_frame, text="Изменить размер", command=self.crop_image, width=button_width).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(control_frame, text="Уменьшить яркость", command=self.enhance_brightness, width=button_width).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(control_frame, text="Нарисовать круг", command=self.draw_line, width=button_width).pack(side=tk.LEFT, padx=5, pady=5)

    def upload_image(self):
        """
        Загружает фотографию из файловой системы
        """
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg")])
        if file_path:
            self.image = Image.open(file_path)
            self.display_image(self.image)

    def capture_image(self):
        """
        Получает фотографию с камеры
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", "Не удалось открыть веб-камеру. Попробуйте сделать фото вручную и загрузить его с помощью проводника.")
            return

        ret, frame = cap.read()
        cap.release()
        if ret:
            self.image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.display_image(self.image)
        else:
            messagebox.showerror("Ошибка", "Не удалось получить изображение с камеры.")

    def display_image(self, image):
        """
        Показвает выбранную фотографию
        """
        self.img_tk = ImageTk.PhotoImage(image)
        self.canvas.itemconfig(self.image_container, image=self.img_tk)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def show_channel(self):
        """
        Показывает выбранный канал
        """
        if self.image is None:
            messagebox.showerror("Ошибка", "Изображение не загружено.")
            return

        channel = self.channel_var.get()
        channels = self.image.split()
        if channel == "Красный":
            self.display_image(channels[0])
        elif channel == "Зеленый":
            self.display_image(channels[1])
        elif channel == "Синий":
            self.display_image(channels[2])
        else:
            messagebox.showerror("Ошибка", "Канал не выбран.")

    def crop_image(self):
        """
        Изменяет размер изображения
        """
        if self.image is None:
            messagebox.showerror("Ошибка", "Фотография не загружена.")
            return

        dimensions = simpledialog.askstring("Ввод", "Введите новый размер(ширина, высота):")
        if dimensions:
            try:
                width, height = map(int, dimensions.split(','))
                if width <= 0 or height <= 0:
                    messagebox.showerror("Ошибка", "Ширина и высота должны быть больше нуля.")
                    return
                self.image = self.image.resize((width, height), Image.ANTIALIAS)
                self.display_image(self.image)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверные значения.")

    def enhance_brightness(self):
        """
        Уменьшает яркость изображения
        """
        if self.image is None:
            messagebox.showerror("Ошибка", "Изображение не загружена.")
            return

        value = simpledialog.askfloat("Ввод", "Введите значение(яркость уменьшится в n раз):")
        if value is not None:
            if value <= 0:
                messagebox.showerror("Ошибка", "Яркость должна быть больше нуля.")
                return
            enhancer = ImageEnhance.Brightness(self.image)
            self.image = enhancer.enhance(1 / value)  # Reduce brightness
            self.display_image(self.image)

    def draw_line(self):
        """
        Рисует круг с координатами и радиусом введенными пользователем
        """
        if self.image is None:
            messagebox.showerror("Ошибка", "Изображение не загружено.")
            return

        circle_params = simpledialog.askstring("Ввод", "Введите параметры круга(x_center, y_center, радиус):")
        if circle_params:
            try:
                x_center, y_center, radius = map(int, circle_params.split(','))
                if radius <= 0:
                    messagebox.showerror("Ошибка", "Радиус должен быть больше нуля.")
                    return
                draw = ImageDraw.Draw(self.image)
                left_up_point = (x_center - radius, y_center - radius)
                right_down_point = (x_center + radius, y_center + radius)
                draw.ellipse([left_up_point, right_down_point], fill="red")
                self.display_image(self.image)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверные параметры круга.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()
