import tkinter as tk
import math
from PIL import Image, ImageTk

# ================= MANUEL SOBEL GRADYENT ================= #

def sobel_gradyent(img):
    if img.mode != 'L':
        img = img.convert('L')
    
    pixels = img.load()
    w, h = img.size
    
    img_sobel_xy = Image.new("L", (w, h))
    img_grad = Image.new("L", (w, h))
    img_comb = Image.new("L", (w, h))
    
    pix_xy = img_sobel_xy.load()
    pix_grad = img_grad.load()
    pix_comb = img_comb.load()
    
    # Sobel Kernelleri
    # Kx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    # Ky = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            tl = pixels[x-1, y-1]; tm = pixels[x, y-1]; tr = pixels[x+1, y-1]
            ml = pixels[x-1, y];   mm = pixels[x, y];   mr = pixels[x+1, y]
            bl = pixels[x-1, y+1]; bm = pixels[x, y+1]; br = pixels[x+1, y+1]
            
            # Sobel X
            sx = (tr + 2*mr + br) - (tl + 2*ml + bl)
            
            # Sobel Y
            sy = (bl + 2*bm + br) - (tl + 2*tm + tr)
            
            # |Sx| + |Sy|
            val_xy = abs(sx) + abs(sy)
            if val_xy > 255: val_xy = 255
            pix_xy[x, y] = val_xy
            
            # Magnitude (Karekök)
            mag = int(math.sqrt(sx*sx + sy*sy))
            if mag > 255: mag = 255
            pix_grad[x, y] = mag
            
            # Combo
            comb = mm + mag
            if comb > 255: comb = 255
            pix_comb[x, y] = comb

    return img, img_sobel_xy, img_grad, img_comb


# ================= MANUEL HISTOGRAM ================= #

def histogram_ciz(canvas, img):
    if img.mode != 'L': img = img.convert('L')
    pixels = img.load()
    w, h = img.size
    
    # Histogram listesi
    hist = [0] * 256
    for y in range(h):
        for x in range(w):
            hist[pixels[x, y]] += 1

    canvas.delete("all")
    canvas.update_idletasks()
    cw = canvas.winfo_width()
    ch = canvas.winfo_height()

    if cw < 5 or ch < 5: return

    max_val = max(hist) if max(hist) > 0 else 1
    scale_x = cw / 256
    scale_y = (ch - 20) / max_val

    for x in range(256):
        x0 = int(x * scale_x)
        y0 = ch
        y1 = ch - int(hist[x] * scale_y)
        canvas.create_line(x0, y0, x0, y1, fill="black")


# ================= ANALİZ PENCERESİ ================= #

def goster_gradyent(base_img):
    if base_img is None: return

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

        lbl_img = tk.Label(frame, bg="white")
        lbl_img.pack()

        tkimg = ImageTk.PhotoImage(img.resize((350, 350)))
        lbl_img.config(image=tkimg)
        lbl_img.image = tkimg

        canvas_hist = tk.Canvas(frame, bg="white", height=230, width=350, highlightthickness=1)
        canvas_hist.pack(pady=5, fill="both", expand=True)
        canvas_hist.bind("<Configure>", lambda e, c=canvas_hist, i=img: histogram_ciz(c, i))

    return win