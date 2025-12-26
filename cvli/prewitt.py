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

# ================= OPENCV PREWITT GRADYENT ================= #

def prewitt_hesapla_cv(gorsel):
    """Prewitt Gradyent hesaplamalarını OpenCV ve filter2D ile uygular."""
    
    img_cv = pil_to_cv(gorsel)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Prewitt Kernelleri (numpy formatında)
    Kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    Ky = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
    
    # 1. Adım: Konvolüsyon (Derinlik olarak CV_64F kullanıldı)
    Gx = cv2.filter2D(gray, cv2.CV_64F, Kx)
    Gy = cv2.filter2D(gray, cv2.CV_64F, Ky)
    
    # 2. Adım: Yatay ve Dikey Kenar Haritaları (Mutlak değer ve 8-bit'e çevirme)
    abs_Gx = cv2.convertScaleAbs(Gx)
    abs_Gy = cv2.convertScaleAbs(Gy)
    
    # 3. Adım: Orijinal + Kenarlar (Orijinal + |Gx| + |Gy|)
    # Mutlak değerleri toplayıp orijinal gri resme eklemek için
    kenar_toplami = cv2.add(abs_Gx, abs_Gy)
    comb = cv2.add(gray, kenar_toplami)
    
    # Sonuçları PIL formatına çevir
    pil_x = Image.fromarray(abs_Gx)
    pil_y = Image.fromarray(abs_Gy)
    pil_sonuc = Image.fromarray(comb)
    
    return gorsel, pil_x, pil_y, pil_sonuc

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

def goster_prewitt_analiz(gorsel):
    if gorsel is None:
        messagebox.showwarning("Uyarı", "Lütfen önce bir görüntü yükleyin.")
        return

    try:
        # 🔴 OpenCV fonksiyonunu çağır
        orjinal, prewitt_yatay, prewitt_dikey, orjinal_arti_prewitt = prewitt_hesapla_cv(gorsel)
    except Exception as e:
        messagebox.showerror("Hata", f"Prewitt işlemi sırasında hata oluştu: {e}")
        return

    pencere = tk.Toplevel()
    pencere.title("Prewitt Kenar Analiz Penceresi (OpenCV)")
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

    resim_ekle(frame_resimler, orjinal, "Orijinal Görüntü")
    resim_ekle(frame_resimler, prewitt_yatay, "Prewitt Yatay")
    resim_ekle(frame_resimler, prewitt_dikey, "Prewitt Dikey")
    resim_ekle(frame_resimler, orjinal_arti_prewitt, "Orijinal + Prewitt")

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
    hist_ekle(frame_histogramlar, prewitt_yatay, "Yatay Prewitt Histogram")
    hist_ekle(frame_histogramlar, prewitt_dikey, "Dikey Prewitt Histogram")
    hist_ekle(frame_histogramlar, orjinal_arti_prewitt, "Sonuç Histogram")
    return pencere