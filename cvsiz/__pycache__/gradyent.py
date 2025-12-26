import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

# ================= SOBEL GRADYENT HESAPLAMA ================= #

def sobel_gradyent(img):
    arr = np.array(img.convert("L"), dtype=np.float32)

    Kx = np.array([[-1,0,1],
                   [-2,0,2],
                   [-1,0,1]], dtype=np.float32)

    Ky = np.array([[-1,-2,-1],
                   [ 0, 0, 0],
                   [ 1, 2, 1]], dtype=np.float32)

    p = np.pad(arr, 1, mode="edge")

    sx = (
        p[:-2,:-2]*Kx[0,0] + p[:-2,1:-1]*Kx[0,1] + p[:-2,2:]*Kx[0,2] +
        p[1:-1,:-2]*Kx[1,0] + p[1:-1,1:-1]*Kx[1,1] + p[1:-1,2:]*Kx[1,2] +
        p[2:,:-2]*Kx[2,0] + p[2:,1:-1]*Kx[2,1] + p[2:,2:]*Kx[2,2]
    )

    sy = (
        p[:-2,:-2]*Ky[0,0] + p[:-2,1:-1]*Ky[0,1] + p[:-2,2:]*Ky[0,2] +
        p[1:-1,:-2]*Ky[1,0] + p[1:-1,1:-1]*Ky[1,1] + p[1:-1,2:]*Ky[1,2] +
        p[2:,:-2]*Ky[2,0] + p[2:,1:-1]*Ky[2,1] + p[2:,2:]*Ky[2,2]
    )

    sobel_xy = np.clip(np.abs(sx) + np.abs(sy), 0, 255).astype(np.uint8)
    grad_mag = np.sqrt(sx**2 + sy**2)
    grad_mag = np.clip(grad_mag, 0, 255).astype(np.uint8)
    comb = np.clip(arr + grad_mag, 0, 255).astype(np.uint8)

    return (
        Image.fromarray(arr.astype(np.uint8)),     # Orijinal (gri)
        Image.fromarray(sobel_xy),                 # |Sx| + |Sy|
        Image.fromarray(grad_mag),                 # Gradient Magnitude
        Image.fromarray(comb)                      # Orijinal + Gradient
    )


# ================= HISTOGRAM ÇİZİM ================= #

def histogram_ciz(canvas, img):
    arr = np.array(img.convert("L"))
    hist = np.bincount(arr.flatten(), minlength=256)

    canvas.delete("all")

    canvas.update_idletasks()
    w = canvas.winfo_width()
    h = canvas.winfo_height()

    if w < 5 or h < 5:
        return

    max_val = hist.max() if hist.max() > 0 else 1
    scale_x = w / 256
    scale_y = (h - 20) / max_val

    for x in range(256):
        x0 = int(x * scale_x)
        y0 = h
        y1 = h - int(hist[x] * scale_y)
        canvas.create_line(x0, y0, x0, y1, fill="black")


# ================= ANALİZ PENCERESİ ================= #

def goster_gradyent(base_img):
    if base_img is None:
        return

    img_orj, img_sobel_xy, img_grad, img_comb = sobel_gradyent(base_img)

    win = tk.Toplevel()
    win.title("Sobel Gradyent – Analiz Penceresi")
    win.geometry("1800x800")
    win.resizable(False, False)
    win.configure(bg="white")

    main = tk.Frame(win, bg="white")
    main.pack(fill="both", expand=True, padx=10, pady=10)

    imgs = [
        ("Orijinal", img_orj),
        ("Sobel X+Y", img_sobel_xy),
        ("Gradient Magnitude", img_grad),
        ("Orijinal + Gradient", img_comb),
    ]

    for title, img in imgs:
        frame = tk.Frame(main, bg="white")
        frame.pack(side="left", padx=10)

        lbl_title = tk.Label(frame, text=title, bg="white", font=("Arial", 14, "bold"))
        lbl_title.pack(pady=5)

        # Görüntü Label
        lbl_img = tk.Label(frame, bg="white")
        lbl_img.pack()

        tkimg = ImageTk.PhotoImage(img.resize((350, 350)))
        lbl_img.config(image=tkimg)
        lbl_img.image = tkimg

        # Histogram Canvas
        canvas_hist = tk.Canvas(frame, bg="white", height=230, width=350, highlightthickness=1)
        canvas_hist.pack(pady=5, fill="both", expand=True)

        # histogramı doğru zamanda çiz
        canvas_hist.bind("<Configure>", lambda e, c=canvas_hist, i=img: histogram_ciz(c, i))

    return win
