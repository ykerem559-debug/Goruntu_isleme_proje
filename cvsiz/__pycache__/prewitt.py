# prewitt_pencere.py
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from tkinter import messagebox

def prewitt_hesapla(gorsel):

    if gorsel.mode != 'L':
        dizi = np.array(gorsel.convert("L"), dtype=np.float32)
    else:
        dizi = np.array(gorsel, dtype=np.float32)

    K_yatay = np.array([
        [-1, 0, 1],
        [-1, 0, 1],
        [-1, 0, 1]
    ], dtype=np.float32)
    
    K_dikey = np.array([
        [-1, -1, -1],
        [ 0,  0,  0],
        [ 1,  1,  1]
    ], dtype=np.float32)

    padli = np.pad(dizi, 1, mode="edge")
    prewitt_x = (
        padli[:-2, :-2] * K_yatay[0, 0] + padli[:-2, 1:-1] * K_yatay[0, 1] + padli[:-2, 2:] * K_yatay[0, 2] +
        padli[1:-1, :-2] * K_yatay[1, 0] + padli[1:-1, 1:-1] * K_yatay[1, 1] + padli[1:-1, 2:] * K_yatay[1, 2] +
        padli[2:, :-2] * K_yatay[2, 0] + padli[2:, 1:-1] * K_yatay[2, 1] + padli[2:, 2:] * K_yatay[2, 2]
    )
    prewitt_y = (
        padli[:-2, :-2] * K_dikey[0, 0] + padli[:-2, 1:-1] * K_dikey[0, 1] + padli[:-2, 2:] * K_dikey[0, 2] +
        padli[1:-1, :-2] * K_dikey[1, 0] + padli[1:-1, 1:-1] * K_dikey[1, 1] + padli[1:-1, 2:] * K_dikey[1, 2] +
        padli[2:, :-2] * K_dikey[2, 0] + padli[2:, 1:-1] * K_dikey[2, 1] + padli[2:, 2:] * K_dikey[2, 2]
    )

    gx_gorsel = np.clip(np.absolute(prewitt_x), 0, 255).astype(np.uint8)
    gy_gorsel = np.clip(np.absolute(prewitt_y), 0, 255).astype(np.uint8)
    
    prewitt_buyukluk = np.absolute(prewitt_x) + np.absolute(prewitt_y)
    orjinal_arti_prewitt = dizi + prewitt_buyukluk

    sonuc = np.clip(orjinal_arti_prewitt, 0, 255).astype(np.uint8)
    return (
        Image.fromarray(dizi.astype(np.uint8)),    
        Image.fromarray(gx_gorsel),                
        Image.fromarray(gy_gorsel),               
        Image.fromarray(sonuc)                   
    )
def histogram_ciz(canvas, gorsel):
    dizi = np.array(gorsel.convert("L"))
    hist = np.bincount(dizi.flatten(), minlength=256)

    canvas.delete("all")
    canvas.update_idletasks() 
    genislik = canvas.winfo_width()
    yukseklik = canvas.winfo_height()
    
    if genislik <= 0 or yukseklik <= 0:
        return

    max_deger = hist.max() if hist.max() > 0 else 1
    ust_bosluk = 0 
    alt_bosluk = 20 
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
        
def goster_prewitt_analiz(gorsel):
    if gorsel is None:
        messagebox.showwarning("Uyarı", "Lütfen önce bir görüntü yükleyin.")
        return

    try:
        orjinal, prewitt_yatay, prewitt_dikey, orjinal_arti_prewitt = prewitt_hesapla(gorsel)
    except Exception as e:
        messagebox.showerror("Hata", f"Prewitt işlemi sırasında hata oluştu: {e}")
        return

    pencere = tk.Toplevel()
    pencere.title("Prewitt Kenar Analiz Penceresi")
    pencere.geometry("1600x900")
    pencere.resizable(False, False)
    pencere.configure(bg="white")

    ana_frame = tk.Frame(pencere, bg="white")
    ana_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # 1️⃣ RESİMLER ÜSTTE
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

    # 2️⃣ HİSTOGRAMLAR ALTA
    frame_histogramlar = tk.Frame(ana_frame, bg="white")
    frame_histogramlar.pack(pady=20, fill="both", expand=True)

    def hist_ekle(parent, gorsel, baslik):
        cerceve = tk.Frame(parent, bg="white")
        cerceve.pack(side="left", padx=15, fill="both", expand=True)
        lbl = tk.Label(cerceve, text=baslik, bg="white", font=("Arial", 12))
        lbl.pack(pady=5)
        canvas = tk.Canvas(cerceve, bg="white", highlightthickness=1)
        canvas.pack(fill="both", expand=True)
        canvas.bind('<Configure>', lambda event, c=canvas, i=gorsel: histogram_ciz(c, i))

    hist_ekle(frame_histogramlar, orjinal, "Orijinal Histogram")
    hist_ekle(frame_histogramlar, prewitt_yatay, "Yatay Prewitt Histogram")
    hist_ekle(frame_histogramlar, prewitt_dikey, "Dikey Prewitt Histogram")
    hist_ekle(frame_histogramlar, orjinal_arti_prewitt, "Sonuç Histogram")
    return pencere