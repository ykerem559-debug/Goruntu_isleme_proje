# cvli/tuzbiber_cv.py (TUZ BİBER GÜRÜLTÜSÜ VE FİLTRE ANALİZİ - OPENCV)

import tkinter as tk
from tkinter import Toplevel, messagebox
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import numpy as np
import cv2

# 🔴 cvislem.py dosyasından gerekli dönüşüm fonksiyonlarını içe aktar
try:
    from cvislem import cv_to_pil, pil_to_cv
except ImportError:
    tk.messagebox.showerror("Hata", "Gerekli dönüşüm fonksiyonları (cv_to_pil, pil_to_cv) 'cvislem.py' dosyasında bulunamadı.")
    # Hata durumunda temel dönüşümleri tanımla (geçici çözüm)
    def pil_to_cv(img_pil):
        return cv2.cvtColor(np.array(img_pil.convert('RGB')), cv2.COLOR_RGB2BGR)
    def cv_to_pil(img_cv):
        return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    
# =========================================================
# TUZ BİBER GÜRÜLTÜSÜ (CVLİ)
# =========================================================
def tuz_biber_gurultusu_ekle_cv(img_pil, oran=0.01):
    """
    OpenCV (NumPy) kullanarak Tuz Biber gürültüsü ekler.
    Oran: Gürültü yoğunluğu (Örn: 0.01 = %1)
    """
    img_cv = pil_to_cv(img_pil)
    img_np = np.copy(img_cv)
    
    gurultu_sayisi = int(np.prod(img_np.shape[:2]) * oran)

    # Tuz (Salt): Beyaz nokta ekleme (255)
    coords = [np.random.randint(0, i - 1, gurultu_sayisi) for i in img_np.shape[:2]]
    img_np[coords[0], coords[1], :] = 255

    # Biber (Pepper): Siyah nokta ekleme (0)
    coords = [np.random.randint(0, i - 1, gurultu_sayisi) for i in img_np.shape[:2]]
    img_np[coords[0], coords[1], :] = 0
    
    return cv_to_pil(img_np)

# =========================================================
# MEAN FILTER (CVLİ)
# =========================================================
def mean_filter_cv(img_pil):
    """OpenCV cv2.blur kullanarak Ortalama (Mean) filtresi uygular."""
    img_cv = pil_to_cv(img_pil)
    # 3x3 pencere ile ortalama filtresi
    mean_sonuc = cv2.blur(img_cv, (3, 3)) 
    return cv_to_pil(mean_sonuc)

# =========================================================
# MEDIAN FILTER (CVLİ)
# =========================================================
def median_filter_cv(img_pil):
    """OpenCV cv2.medianBlur kullanarak Medyan filtresi uygular."""
    img_cv = pil_to_cv(img_pil)
    # 5x5 pencere ile medyan filtresi uygular (medianBlur tek boyutlu ksize alır)
    median_sonuc = cv2.medianBlur(img_cv, 5) 
    return cv_to_pil(median_sonuc)

# =========================================================
# ANA ANALİZ PENCERESİ
# =========================================================
def goster_tuzbiber_analiz_cv(orjinal_img):

    if orjinal_img is None:
        messagebox.showwarning("Hata", "Görüntü yok")
        return

    # RGB kopya (gösterim ve gürültü için)
    img_orjinal_rgb = orjinal_img.copy().convert("RGB")
    
    # 1. Tuz Biber Gürültüsü Ekle
    # Gürültü oranı 0.01 (%1) olarak ayarlandı
    img_gurultulu_rgb = tuz_biber_gurultusu_ekle_cv(img_orjinal_rgb, oran=0.01)

    # 2. Filtreleri Uygula
    # Not: Medyan ve Mean filtreleri genellikle gürültülü (RGB) görüntüye uygulanır.
    img_median = median_filter_cv(img_gurultulu_rgb.copy())
    img_mean = mean_filter_cv(img_gurultulu_rgb.copy())
    
    # 3. Yeni Pencere Oluştur
    pencere = Toplevel()
    pencere.title("Tuz Biber Gürültüsü ve Filtre Analizi (OpenCV)")

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle("Tuz-Biber Gürültüsü – Mean / Median Karşılaştırması (OpenCV)", fontsize=14)

    imgs = [
        ("Orijinal (RGB)", img_orjinal_rgb, "RGB"),
        ("Tuz-Biber (RGB)", img_gurultulu_rgb, "RGB"),
        ("Median Filtre (RGB)", img_median, "RGB"),
        ("Mean Filtre (RGB)", img_mean, "RGB"),
    ]

    for i, (title, img, mode) in enumerate(imgs):
        # Görüntü (Üst Satır)
        img_array = np.array(img)
        axes[0, i].imshow(img_array)
        axes[0, i].set_title(title)
        axes[0, i].axis("off")

        # Histogram (Alt Satır) - Griye çevirerek hesapla
        hist_img = img.convert("L")
        hist = cv2.calcHist([np.array(hist_img)], [0], None, [256], [0, 256])

        axes[1, i].bar(range(256), hist.flatten(), width=1, color='black')
        axes[1, i].set_xlim(0, 255)
        axes[1, i].set_yticks([])
        axes[1, i].set_title("Histogram")

    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=pencere)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()