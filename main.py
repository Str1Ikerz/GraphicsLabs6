from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import math
import os

root = Tk()
root.title("Form1")
root.geometry("650x400")

img_orig = None
img_affine = None
img_inverse = None
img_nonlinear = None


def show_image(img, lbl, max_w=200, max_h=150):
    if img is None:
        lbl.config(image='', bg='white')
        lbl.image = None
        return
    w, h = img.size
    scale = min(max_w / w, max_h / h, 1.0)
    im_r = img.resize((int(w * scale), int(h * scale)))
    tk_img = ImageTk.PhotoImage(im_r)
    lbl.config(image=tk_img)
    lbl.image = tk_img


def open_image():
    global img_orig
    path = filedialog.askopenfilename(filetypes=[("Изображения", "*.bmp;*.jpg;*.png;*.jpeg;*.ppm")])
    if not path:
        return
    try:
        img_orig = Image.open(path).convert("RGB")
        show_image(img_orig, lbl_orig)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")


def save_image(img):
    if img is None:
        messagebox.showwarning("Ошибка", "Нет изображения для сохранения")
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".ppm",
        filetypes=[("PPM", "*.ppm"), ("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("BMP", "*.bmp")],
        title="Сохранить изображение"
    )
    if not path:
        return
    try:
        # Сохраняем в формате PPM
        img.save(path, "PPM")
        messagebox.showinfo("Сохранено", f"Изображение сохранено:\n{os.path.basename(path)}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


def affine_transform():
    global img_affine
    if img_orig is None:
        messagebox.showwarning("Ошибка", "Сначала загрузите изображение")
        return
    try:
        # Параметры переноса
        tx = float(translation_x_entry.get())
        ty = float(translation_y_entry.get())
        # Параметр скоса
        shear = float(shear_entry.get())
    except:
        messagebox.showwarning("Ошибка", "Введите корректные параметры преобразования")
        return

    w, h = img_orig.size
    src = img_orig.load()
    result = Image.new("RGB", (w, h), (255, 255, 255))
    dst = result.load()

    for i in range(w):
        for j in range(h):
            # Обратное преобразование для нахождения исходной точки
            # Прямое преобразование: x' = x + tx + shear * y, y' = y + ty
            # Обратное: x = x' - tx - shear * (y' - ty), y = y' - ty
            x_src = i - tx - shear * (j - ty)
            y_src = j - ty

            xi = int(round(x_src))
            yi = int(round(y_src))

            if 0 <= xi < w and 0 <= yi < h:
                dst[i, j] = src[xi, yi]

    img_affine = result
    show_image(img_affine, lbl_affine)


def inverse_button_action():
    global img_inverse
    if img_orig is None:
        messagebox.showwarning("Ошибка", "Сначала загрузите изображение")
        return
    img_inverse = img_orig.copy()
    show_image(img_inverse, lbl_inverse)


def nonlinear_transform():
    global img_nonlinear
    if img_orig is None:
        messagebox.showwarning("Ошибка", "Сначала загрузите изображение")
        return

    w, h = img_orig.size
    cx, cy = w / 2, h / 2
    src = img_orig.load()
    result = Image.new("RGB", (w, h), (255, 255, 255))
    dst = result.load()

    for i in range(w):
        for j in range(h):
            # Обратное преобразование: находим исходные координаты
            # Прямое преобразование: i = cosh(x') - 1, j = y'
            # где i, j - координаты в результирующем изображении
            # x', y' - координаты в исходном изображении относительно центра

            # Сначала преобразуем координаты результата относительно центра
            x_prime = i - cx
            y_prime = j - cy

            # Обратное преобразование для i = cosh(x') - 1
            # => cosh(x') = i + 1
            # => x' = acosh(i + 1)
            try:
                if (x_prime + 1) >= 1:  # cosh(x) >= 1 для всех x
                    x_src = math.acosh(x_prime + 1)
                else:
                    # Если значение вне области определения, пропускаем пиксель
                    continue
            except (ValueError, OverflowError):
                # Если значение вне области определения, пропускаем пиксель
                continue

            # Для j = y' преобразование простое
            y_src = y_prime

            # Преобразуем обратно в координаты изображения
            xi = int(round(x_src + cx))
            yi = int(round(y_src + cy))

            if 0 <= xi < w and 0 <= yi < h:
                dst[i, j] = src[xi, yi]

    img_nonlinear = result
    show_image(img_nonlinear, lbl_nonlinear, max_w=400, max_h=120)


# Создание элементов интерфейса
btn_open = Button(root, text="Открыть", command=open_image)
btn_open.place(x=10, y=10, width=80)

# Параметры для аффинного преобразования (перенос и скос)
Label(root, text="Перенос X:").place(x=100, y=13)
translation_x_entry = Entry(root, width=5)
translation_x_entry.insert(0, "10")
translation_x_entry.place(x=160, y=13, width=40)

Label(root, text="Y:").place(x=205, y=13)
translation_y_entry = Entry(root, width=5)
translation_y_entry.insert(0, "5")
translation_y_entry.place(x=225, y=13, width=40)

Label(root, text="Скос:").place(x=270, y=13)
shear_entry = Entry(root, width=5)
shear_entry.insert(0, "0.3")
shear_entry.place(x=310, y=13, width=40)

btn_aff = Button(root, text="аффинное", command=affine_transform)
btn_aff.place(x=360, y=10, width=80)

btn_save_aff = Button(root, text="Сохранить", command=lambda: save_image(img_affine))
btn_save_aff.place(x=450, y=10, width=80)

btn_inv = Button(root, text="обратно", command=inverse_button_action)
btn_inv.place(x=540, y=10, width=80)

lbl_orig = Label(root, bg="white", relief="solid")
lbl_orig.place(x=10, y=50, width=200, height=150)

lbl_affine = Label(root, bg="white", relief="solid")
lbl_affine.place(x=220, y=50, width=200, height=150)

lbl_inverse = Label(root, bg="white", relief="solid")
lbl_inverse.place(x=430, y=50, width=200, height=150)

btn_nl = Button(root, text="нелинейное", command=nonlinear_transform)
btn_nl.place(x=10, y=230, width=80)

btn_save_nl = Button(root, text="Сохранить", command=lambda: save_image(img_nonlinear))
btn_save_nl.place(x=100, y=230, width=80)

lbl_nonlinear = Label(root, bg="white", relief="solid")
lbl_nonlinear.place(x=10, y=260, width=400, height=120)

root.mainloop()