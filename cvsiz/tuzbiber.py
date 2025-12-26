# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import Toplevel, messagebox
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import random

# =========================================================
# YARDIMCI
# =========================================================
def sinirla(v):
    if v < 0: return 0
    if v > 255: return 255
    return int(v)

# =========================================================
# TUZ BİBER GÜRÜLTÜSÜ (SAF)
# =========================================================
def tuz_biber_gurultusu_ekle(img, oran=0.1):
    w, h = img.size
    src = img.load()

    out = img.copy()
    dst = out.load()

    toplam = w * h
    gurultu_sayisi = int(toplam * oran)

    for _ in range(gurultu_sayisi):
        x = random.randint(0, w-1)
        y = random.randint(0, h-1)
        dst[x, y] = 255 if random.random() < 0.5 else 0

    return out

# =========================================================
# MEAN FILTER (3x3 – SAF)
# =========================================================
def mean_filter(img):
    w, h = img.size
    src = img.load()

    out = Image.new("L", (w, h))
    dst = out.load()

    for y in range(1, h-1):
        for x in range(1, w-1):
            toplam = 0
            for j in range(-1, 2):
                for i in range(-1, 2):
                    toplam += src[x+i, y+j]
            dst[x, y] = toplam // 9

    return out

# =========================================================
# MEDIAN FILTER (3x3 – SAF)
# =========================================================
def median_filter(img):
    w, h = img.size
    src = img.load()

    out = Image.new("L", (w, h))
    dst = out.load()

    for y in range(1, h-1):
        for x in range(1, w-1):
            pencere = []
            for j in range(-1, 2):
                for i in range(-1, 2):
                    pencere.append(src[x+i, y+j])
            pencere.sort()
            dst[x, y] = pencere[4]  # median

    return out

# =========================================================
# HISTOGRAM (SAF)
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
# ANA ANALİZ PENCERESİ
# =========================================================
def goster_tuzbiber_analiz(orjinal_img):

    if orjinal_img is None:
        messagebox.showwarning("Hata", "Görüntü yok")
        return

    # RGB kopya (gösterim için)
    img_orjinal_rgb = orjinal_img.copy().convert("RGB")

    # Gri (filtreler için)
    img_gri = orjinal_img.convert("L")

    # Tuz-biber (RGB üstünden)
    img_gurultulu_rgb = tuz_biber_gurultusu_ekle(img_orjinal_rgb.copy(), oran=0.1)

    # Gürültülü gri
    img_gurultulu_gri = img_gurultulu_rgb.convert("L")

    # Filtreler
    img_median = median_filter(img_gurultulu_gri)
    img_mean   = mean_filter(img_gurultulu_gri)

    pencere = Toplevel()
    pencere.title("Tuz Biber Gürültüsü ve Filtre Analizi (Saf Döngü)")

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle("Tuz-Biber Gürültüsü – Mean / Median Karşılaştırması", fontsize=14)

    imgs = [
        ("Orijinal (RGB)", img_orjinal_rgb, "RGB"),
        ("Tuz-Biber (RGB)", img_gurultulu_rgb, "RGB"),
        ("Median Filtre (Gri)", img_median, "L"),
        ("Mean Filtre (Gri)", img_mean, "L"),
    ]

    for i, (title, img, mode) in enumerate(imgs):
        # Görüntü
        axes[0, i].imshow(img if mode=="RGB" else img, cmap=None if mode=="RGB" else "gray")
        axes[0, i].set_title(title)
        axes[0, i].axis("off")

        # Histogram
        hist_img = img.convert("L")
        hist = histogram_hesapla(hist_img)
        axes[1, i].bar(range(256), hist, width=1)
        axes[1, i].set_xlim(0, 255)
        axes[1, i].set_yticks([])
        axes[1, i].set_title("Histogram")

    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=pencere)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()
