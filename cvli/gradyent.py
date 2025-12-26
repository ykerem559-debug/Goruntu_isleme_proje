import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
import math

# 🔴 GEREKLİ YARDIMCI DÖNÜŞÜM FONKSİYONLARI (Varsayılan olarak main dosyasından alınır)
# NOT: Bu fonksiyonların sizin ana kodunuzda tanımlı olduğunu varsayıyorum.
def pil_to_cv(img_pil):
    """PIL Image objesini OpenCV (BGR) formatına çevirir."""
    img_np = np.array(img_pil.convert('RGB'))
    return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

def cv_to_pil(img_cv):
    """OpenCV (BGR) formatındaki resmi PIL Image objesine çevirir."""
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img_rgb)


# ================= OPENCV SOBEL GRADYENT ================= #

def sobel_gradyent_cv(gorsel):
    """Sobel Gradyent ve Magnitüd hesaplamalarını OpenCV ile uygular."""
    
    # PIL'den OpenCV'ye çevir ve Griye dönüştür
    img_cv = pil_to_cv(gorsel)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # 1. Adım: Sobel Yatay (Gx) ve Dikey (Gy) hesaplamaları
    # Derinlik: cv2.CV_64F (negatif değerler için)
    
    # Gx (Yatay Kenarlar)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    # Gy (Dikey Kenarlar)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    
    # 2. Adım: Mutlak Değerler ve Normalizasyon (Kenar Haritaları için)
    
    # |Gx| ve |Gy|'nin 8-bit tam sayı versiyonları
    abs_sobelx = cv2.convertScaleAbs(sobelx)
    abs_sobely = cv2.convertScaleAbs(sobely)
    
    # Sobel X+Y: İki mutlak değeri topla
    sobel_xy = cv2.addWeighted(abs_sobelx, 0.5, abs_sobely, 0.5, 0)
    
    # 3. Adım: Gradyent Magnitüd (Büyüklük)
    # Magnitüd: sqrt(Gx² + Gy²)
    # OpenCV'de bu genellikle cv2.magnitude ile yapılır, ancak biz numpy'ı kullanabiliriz
    mag_64f = np.sqrt(sobelx**2 + sobely**2)
    
    # Magnitüdü 0-255 aralığına sıkıştır ve 8-bit'e çevir
    mag = np.clip(mag_64f, 0, 255).astype(np.uint8)
    
    # 4. Adım: Orijinal + Gradient (Keskinleştirme/Kabartma etkisi)
    # Gri resmi float'a çevir
    gray_float = gray.astype(np.float32)
    
    # Magnitüdü 0-255 aralığına sıkıştırıp float'a çevir
    mag_float = mag.astype(np.float32)
    
    # Magnitüdü orijinal gri resme ekle
    comb_float = gray_float + mag_float
    
    # Sonucu 0-255 aralığına sıkıştır
    comb = np.clip(comb_float, 0, 255).astype(np.uint8)


    # 5. Adım: Sonuçları PIL formatına çevir
    pil_sobel_xy = Image.fromarray(sobel_xy)
    pil_grad = Image.fromarray(mag)
    pil_comb = Image.fromarray(comb)
    
    # Not: img_orj orijinal PIL resmidir.
    return gorsel, pil_sobel_xy, pil_grad, pil_comb


# ================= OPENCV HISTOGRAM ================= #

def histogram_hesapla_cv(img_pil):
    """OpenCV calcHist kullanarak histogram hesaplama"""
    # Görüntüyü Griye çevir (PIL'den NumPy'a)
    img_np = np.array(img_pil.convert('L'))
    hist = cv2.calcHist([img_np], [0], None, [256], [0, 256])
    return hist.flatten().tolist()


def histogram_ciz(canvas, img):
    hist = histogram_hesapla_cv(img) # 🔴 Yeni OpenCV fonksiyonu çağrıldı

    canvas.delete("all")
    canvas.update_idletasks()
    cw = canvas.winfo_width()
    ch = canvas.winfo_height()

    if cw < 5 or ch < 5: return

    max_val = max(hist) if max(hist) > 0 else 1
    scale_x = cw / 256
    scale_y = (ch - 20) / max_val
    
    # Çizim için zemin çizgisi
    canvas.create_line(0, ch - 20, cw, ch - 20, fill="gray")

    for x in range(256):
        x0 = int(x * scale_x)
        y0 = ch - 20
        y1 = y0 - int(hist[x] * scale_y)
        canvas.create_line(x0, y0, x0, y1, fill="black")


# ================= ANALİZ PENCERESİ ================= #

def goster_gradyent(base_img):
    if base_img is None: return

    # 🔴 Yeni OpenCV fonksiyonunu çağır
    img_orj, img_sobel_xy, img_grad, img_comb = sobel_gradyent_cv(base_img)

    win = tk.Toplevel()
    win.title("Sobel Gradyent – Analiz Penceresi (OpenCV)")
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
        # 🔴 Yeni histogram çizme fonksiyonu çağrılır
        canvas_hist.bind("<Configure>", lambda e, c=canvas_hist, i=img: histogram_ciz(c, i))

    return win