import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import cv2
import numpy as np
import math

# 🔴 GEREKLİ YARDIMCI DÖNÜŞÜM FONKSİYONLARI (Ana kodunuzdan alınmalıdır)
def pil_to_cv(img_pil):
    """PIL Image objesini OpenCV (BGR) formatına çevirir."""
    img_np = np.array(img_pil.convert('RGB'))
    return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

def cv_to_pil(img_cv):
    """OpenCV (BGR) formatındaki resmi PIL Image objesine çevirir."""
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img_rgb)

# ================= OPENCV LAPLACIAN ================= #

def laplacian_hesapla_cv(gorsel):
    """Laplacian ve Keskinleştirme işlemlerini OpenCV ile uygular."""
    
    img_cv = pil_to_cv(gorsel)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # 1. Adım: Laplacian Filtresi Uygulama
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    
    # Laplasyen sonucunu (lap) 0-255 aralığına normalize et (Görselleştirme için)
    lap_normalized = cv2.normalize(lap, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    
    # 2. Adım: Keskinleştirme (Orijinal + A * Laplacian)
    gray_64f = gray.astype(np.float64)
    
    # Keskinlik Faktörü A=4
    keskin_4_f = gray_64f + 4 * lap
    keskin_4 = np.clip(keskin_4_f, 0, 255).astype(np.uint8)
    
    # Keskinlik Faktörü A=8
    keskin_8_f = gray_64f + 8 * lap
    keskin_8 = np.clip(keskin_8_f, 0, 255).astype(np.uint8)
    
    # 3. Adım: Sonuçları PIL formatına çevir
    pil_lap = Image.fromarray(lap_normalized)
    pil_k4 = Image.fromarray(keskin_4)
    pil_k8 = Image.fromarray(keskin_8)
    
    return gorsel, pil_lap, pil_k4, pil_k8

# ================= OPENCV HISTOGRAM ================= #

def histogram_hesapla_cv(img_pil):
    """OpenCV calcHist kullanarak histogram hesaplama"""
    img_np = np.array(img_pil.convert('L'))
    hist = cv2.calcHist([img_np], [0], None, [256], [0, 256])
    return hist.flatten().tolist()

def histogram_ciz(canvas, gorsel):
    hist = histogram_hesapla_cv(gorsel)

    canvas.delete("all")
    canvas.update_idletasks() 
    genislik = canvas.winfo_width()
    yukseklik = canvas.winfo_height()
    
    if genislik <= 0 or yukseklik <= 0: return

    max_deger = max(hist) if max(hist) > 0 else 1
    ust_bosluk, alt_bosluk = 0, 20 
    cizim_yuksekligi = yukseklik - ust_bosluk - alt_bosluk
    olcek_x = genislik / 256
    olcek_y = cizim_yuksekligi / max_deger
    
    canvas.create_line(0, yukseklik - alt_bosluk, genislik, yukseklik - alt_bosluk, fill="gray")
    
    for x in range(256):
        x0 = x * olcek_x
        y0 = yukseklik - alt_bosluk
        y1 = y0 - hist[x] * olcek_y
        y1 = max(y1, ust_bosluk)
        canvas.create_line(x0, y0, x0, y1, fill="black")


# ================= ANALİZ PENCERESİ ================= #

def goster_laplace_analiz(gorsel):
    if gorsel is None:
        messagebox.showwarning("Uyarı", "Lütfen önce bir görüntü yükleyin.")
        return
    try:
        # 🔴 OpenCV fonksiyonunu çağır
        orjinal, lap_harita, keskin_4, keskin_8 = laplacian_hesapla_cv(gorsel)
    except Exception as e:
        messagebox.showerror("Hata", f"Laplacian işlemi sırasında hata oluştu: {e}")
        return

    pencere = tk.Toplevel()
    pencere.title("Laplacian Analiz Penceresi (OpenCV)")
    pencere.geometry("1600x900")
    pencere.resizable(False, False)
    pencere.configure(bg="white")
    ana_frame = tk.Frame(pencere, bg="white")
    ana_frame.pack(padx=10, pady=10, fill="both", expand=True)
    
    frame_resimler = tk.Frame(ana_frame, bg="white")
    frame_resimler.pack(pady=10)

    def resim_ekle(parent, gorsel, baslik):
        cerceve = tk.Frame(parent, bg="white")
        cerceve.pack(side="left", padx=15)
        lbl_baslik = tk.Label(cerceve, text=baslik, bg="white", font=("Arial", 14, "bold"))
        lbl_baslik.pack(pady=5)
        lbl_gorsel = tk.Label(cerceve, bg="lightgray")
        lbl_gorsel.pack()
        res_img = gorsel.resize((350, 350))
        tkimg = ImageTk.PhotoImage(res_img)
        lbl_gorsel.config(image=tkimg)
        lbl_gorsel.image = tkimg

    resim_ekle(frame_resimler, orjinal, "Orijinal")
    resim_ekle(frame_resimler, lap_harita, "Laplacian")
    resim_ekle(frame_resimler, keskin_4, "Orijinal + Laplacian * 4")
    resim_ekle(frame_resimler, keskin_8, "Orijinal + Laplacian * 8")

    frame_histogramlar = tk.Frame(ana_frame, bg="white")
    frame_histogramlar.pack(pady=20, fill="both", expand=True)

    def hist_ekle(parent, gorsel, baslik):
        cerceve = tk.Frame(parent, bg="white")
        cerceve.pack(side="left", padx=15, fill="both", expand=True)
        lbl = tk.Label(cerceve, text=baslik, bg="white", font=("Arial", 12))
        lbl.pack(pady=5)
        canvas = tk.Canvas(cerceve, bg="white", highlightthickness=1)
        canvas.pack(fill="both", expand=True)
        # 🔴 Yeni histogram çizme fonksiyonu çağrılır
        canvas.bind('<Configure>', lambda event, c=canvas, i=gorsel: histogram_ciz(c, i))

    hist_ekle(frame_histogramlar, orjinal, "Orijinal Histogram")
    hist_ekle(frame_histogramlar, lap_harita, "Laplacian Histogram")
    hist_ekle(frame_histogramlar, keskin_4, "Keskin A=4 Histogram")
    hist_ekle(frame_histogramlar, keskin_8, "Keskin A=8 Histogram")
    return pencere