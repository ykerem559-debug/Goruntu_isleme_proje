# genislaplace_tr.py
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from tkinter import messagebox


def laplacian_keskinlestir(gorsel):

    if gorsel.mode != 'L':
        dizi = np.array(gorsel.convert("L"), dtype=np.float32)
    else:
        dizi = np.array(gorsel, dtype=np.float32)

    cekirdek = np.array([
        [0, -1,  0],
        [-1, 4, -1],
        [0, -1,  0]
    ], dtype=np.float32)
    padli = np.pad(dizi, 1, mode="edge")
    lap = (
        padli[:-2, :-2] * cekirdek[0, 0] + padli[:-2, 1:-1] * cekirdek[0, 1] + padli[:-2, 2:] * cekirdek[0, 2] +
        padli[1:-1, :-2] * cekirdek[1, 0] + padli[1:-1, 1:-1] * cekirdek[1, 1] + padli[1:-1, 2:] * cekirdek[1, 2] +
        padli[2:, :-2] * cekirdek[2, 0] + padli[2:, 1:-1] * cekirdek[2, 1] + padli[2:, 2:] * cekirdek[2, 2]
    )
    lap_haritasi = np.clip(lap, 0, 255).astype(np.uint8)
    keskin_4 = np.clip(dizi + 4 * lap, 0, 255).astype(np.uint8)
    keskin_8 = np.clip(dizi + 8 * lap, 0, 255).astype(np.uint8)
    return (
        Image.fromarray(dizi.astype(np.uint8)), 
        Image.fromarray(lap_haritasi),          
        Image.fromarray(keskin_4),            
        Image.fromarray(keskin_8)             
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

def goster_laplace_analiz(gorsel):
    if gorsel is None:
        messagebox.showwarning("Uyarı", "Lütfen önce bir görüntü yükleyin.")
        return
    try:
        orjinal, lap_harita, keskin_4, keskin_8 = laplacian_keskinlestir(gorsel)
    except Exception as e:
        messagebox.showerror("Hata", f"Laplacian işlemi sırasında hata oluştu: {e}")
        return

    pencere = tk.Toplevel()
    pencere.title("Laplacian Analiz Penceresi")
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
        canvas.bind('<Configure>', lambda event, c=canvas, i=gorsel: histogram_ciz(c, i))

    hist_ekle(frame_histogramlar, orjinal, "Orijinal Histogram")
    hist_ekle(frame_histogramlar, lap_harita, "Laplacian Histogram")
    hist_ekle(frame_histogramlar, keskin_4, "Keskin A=4 Histogram")
    hist_ekle(frame_histogramlar, keskin_8, "Keskin A=8 Histogram")
    return pencere
