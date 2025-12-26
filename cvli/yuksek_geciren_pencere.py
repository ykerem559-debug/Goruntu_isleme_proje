# yuksek_geciren_pencere.py

import tkinter as tk
from tkinter import Toplevel
from PIL import Image
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

# 🔴 cvislem.py dosyasından gerekli fonksiyonları içe aktar
try:
    from cvislem import laplacian_kenar_haritasi_cv, laplacian_keskinlestir_cv, gri_yap_dondur
except ImportError:
    tk.messagebox.showerror("Hata", "OpenCV işlemleri için gerekli fonksiyonlar (laplacian_kenar_haritasi_cv vb.) 'cvislem.py' dosyasında bulunamadı.")
    laplacian_kenar_haritasi_cv = None
    laplacian_keskinlestir_cv = None
    gri_yap_dondur = lambda img: img.convert('L') 


def goster_yuksek_geciren(orjinal_img): # 🔴 AD DÜZELTİLDİ: Artık goster_yuksek_geciren_cv değil!
    """
    OpenCV kullanarak Laplacian Keskinleştirme Analizini (4 sonuçlu) gösterir.
    """
    if orjinal_img is None:
        tk.messagebox.showwarning("Hata", "Görüntü yüklenmedi.")
        return

    # 1. İşlemleri Yap
    try:
        # Renkli göstermek için RGB kopyası
        img_orjinal_rgb = orjinal_img.copy().convert("RGB")
        
        # Analiz için Griye Çevir
        img_gri = gri_yap_dondur(img_orjinal_rgb)
        
        if laplacian_kenar_haritasi_cv and laplacian_keskinlestir_cv:
            # 2. Laplacian Çıktısı (Kenar resmi)
            img_laplacian = laplacian_kenar_haritasi_cv(img_gri) 

            # 3. Keskinleştirme İşlemlerini Uygula (Merkez 5 ve Merkez 9/8)
            img_merkez_5 = laplacian_keskinlestir_cv(img_gri, C=5) 
            img_merkez_8 = laplacian_keskinlestir_cv(img_gri, C=9)
        else:
            # Hata durumunda boş gri resimler göster
            img_laplacian = img_gri.copy()
            img_merkez_5 = img_gri.copy()
            img_merkez_8 = img_gri.copy()
        
    except Exception as e:
        tk.messagebox.showerror("Hata", f"OpenCV Laplacian işlemleri sırasında hata oluştu: {e}")
        return

    # 4. Yeni Pencereyi Oluştur
    pencere = Toplevel()
    pencere.title("OpenCV Laplacian Keskinleştirme Analizi (Yüksek Geçiren)")
    
    # 5. Matplotlib Figürünü Oluştur (2 Satır, 4 Sütun)
    fig, axes = plt.subplots(2, 4, figsize=(16, 8)) 
    fig.suptitle("Laplacian Keskinleştirme Karşılaştırması ve Histogram Analizi (OpenCV)", fontsize=14)
    
    # Görüntü Listesi
    gosterilecekler = [
        {"img": img_orjinal_rgb, "title": "1. Orijinal Görüntü (RGB)", "mode": "RGB"},
        {"img": img_laplacian, "title": "2. Laplacian Çıktısı (Gri)", "mode": "L"},
        {"img": img_merkez_5, "title": "3. Orijinal+Laplasyen (Merkez 5)", "mode": "L"},
        {"img": img_merkez_8, "title": "4. Orijinal+Laplasyen (Merkez 8)", "mode": "L"}
    ]

    # 6. Figüre Resimleri ve Histogramları Ekle
    for i, item in enumerate(gosterilecekler):
        img_data = item["img"]
        
        # --- Üst Satır: Görüntü ---
        ax_img = axes[0, i]
        
        if item["mode"] == "L":
            img_array = np.array(img_data)
            ax_img.imshow(img_array, cmap='gray')
        else:
            img_array = np.array(img_data)
            ax_img.imshow(img_array)
            
        ax_img.set_title(item["title"], fontsize=10)
        ax_img.axis('off')

        # --- Alt Satır: Histogram (Doldurulmuş Çubuklar) ---
        ax_hist = axes[1, i]
        
        # Histogram hesapla (RGB ise griye çevir)
        if item["mode"] == "RGB":
            hist_array = np.array(img_data.convert("L"))
        else:
            hist_array = np.array(img_data)
            
        hist, bins = np.histogram(hist_array.flatten(), 256, [0, 256])
        
        # ÇUBUK GRAFİK İLE DOLDUR
        ax_hist.bar(bins[:-1], hist, width=1, color='black', align='edge')
        
        ax_hist.set_title("Histogram", fontsize=8)
        ax_hist.set_xlim([0, 256])
        ax_hist.set_yticks([]) 

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # 7. Tkinter Canvas'a Göm
    canvas = FigureCanvasTkAgg(fig, master=pencere)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    canvas.draw()