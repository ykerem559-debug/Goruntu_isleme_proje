# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import Toplevel, messagebox
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================

def sinirla(v):
    if v < 0: return 0
    if v > 255: return 255
    return int(v)

def gri_yap(img):
    if img.mode == "L":
        return img.copy()
    return img.convert("L")

# =========================================================
# LAPLCIAN (MERKEZ = 5) – SAF DÖNGÜ
# =========================================================
def laplacian_merkez5(img):
    w, h = img.size
    src = img.load()

    out = Image.new("L", (w, h))
    dst = out.load()

    for y in range(1, h-1):
        for x in range(1, w-1):
            val = (
                src[x, y-1] +
                src[x-1, y] -
                4 * src[x, y] +
                src[x+1, y] +
                src[x, y+1]
            )
            dst[x, y] = sinirla(val)

    return out

# =========================================================
# ORİJİNAL + LAPLCIAN (MERKEZ 5)
# =========================================================
def original_plus_laplacian_5(img):
    w, h = img.size
    src = img.load()

    out = Image.new("L", (w, h))
    dst = out.load()

    for y in range(1, h-1):
        for x in range(1, w-1):
            lap = (
                src[x, y-1] +
                src[x-1, y] -
                4 * src[x, y] +
                src[x+1, y] +
                src[x, y+1]
            )
            dst[x, y] = sinirla(src[x, y] + lap)

    return out

# =========================================================
# ORİJİNAL + LAPLCIAN (MERKEZ 8)
# =========================================================
def original_plus_laplacian_8(img):
    w, h = img.size
    src = img.load()

    out = Image.new("L", (w, h))
    dst = out.load()

    for y in range(1, h-1):
        for x in range(1, w-1):
            lap = (
                src[x-1, y-1] + src[x, y-1] + src[x+1, y-1] +
                src[x-1, y]   - 8 * src[x, y] + src[x+1, y] +
                src[x-1, y+1] + src[x, y+1] + src[x+1, y+1]
            )
            dst[x, y] = sinirla(src[x, y] + lap)

    return out

# =========================================================
# HISTOGRAM (SAF DÖNGÜ)
# =========================================================
def histogram_hesapla(img):
    hist = [0] * 256
    w, h = img.size
    px = img.load()

    for y in range(h):
        for x in range(w):
            hist[px[x, y]] += 1

    return hist

# =========================================================
# ANA GÖSTERİM PENCERESİ
# =========================================================
def goster_yuksek_geciren(orjinal_img):

    if orjinal_img is None:
        messagebox.showwarning("Hata", "Görüntü yok")
        return

    img_gri = gri_yap(orjinal_img)

    img_lap = laplacian_merkez5(img_gri)
    img_c5  = original_plus_laplacian_5(img_gri)
    img_c8  = original_plus_laplacian_8(img_gri)

    pencere = Toplevel()
    pencere.title("Laplacian Keskinleştirme Analizi (Saf Döngü)")

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle("Laplacian – Akademik Saf Döngü Analizi", fontsize=14)

    imgs = [
        ("Orijinal (Gri)", img_gri),
        ("Laplacian Çıktısı", img_lap),
        ("Orijinal + Laplacian (Merkez 5)", img_c5),
        ("Orijinal + Laplacian (Merkez 8)", img_c8)
    ]

    for i, (title, img) in enumerate(imgs):
        axes[0, i].imshow(img, cmap="gray")
        axes[0, i].set_title(title)
        axes[0, i].axis("off")

        hist = histogram_hesapla(img)
        axes[1, i].bar(range(256), hist, width=1)
        axes[1, i].set_xlim(0, 255)
        axes[1, i].set_yticks([])
        axes[1, i].set_title("Histogram")

    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=pencere)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()
