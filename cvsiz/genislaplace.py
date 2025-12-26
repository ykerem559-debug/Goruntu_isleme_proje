import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox

# ================= MANUEL LAPLACIAN ================= #

def laplacian_keskinlestir(gorsel):
    if gorsel.mode != 'L':
        gorsel = gorsel.convert('L')
    
    pixels = gorsel.load()
    w, h = gorsel.size
    
    img_lap = Image.new("L", (w, h))
    img_k4 = Image.new("L", (w, h))
    img_k8 = Image.new("L", (w, h))
    
    pix_lap = img_lap.load()
    pix_k4 = img_k4.load()
    pix_k8 = img_k8.load()
    
    # Laplacian Kernel
    # [[0, -1, 0], 
    #  [-1, 4, -1], 
    #  [0, -1, 0]]
    
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            merkez = pixels[x, y]
            ust    = pixels[x, y-1]
            alt    = pixels[x, y+1]
            sol    = pixels[x-1, y]
            sag    = pixels[x+1, y]
            
            # Konvolüsyon
            val = (merkez * 4) - (ust + alt + sol + sag)
            
            # Sadece Laplacian haritası için sınırla
            lap_val = val
            if lap_val > 255: lap_val = 255
            elif lap_val < 0: lap_val = 0
            pix_lap[x, y] = lap_val
            
            # Keskinleştirme (Orijinal + 4*Lap)
            k4 = merkez + 4 * val
            if k4 > 255: k4 = 255
            elif k4 < 0: k4 = 0
            pix_k4[x, y] = k4
            
            # Keskinleştirme (Orijinal + 8*Lap)
            k8 = merkez + 8 * val
            if k8 > 255: k8 = 255
            elif k8 < 0: k8 = 0
            pix_k8[x, y] = k8
            
    return gorsel, img_lap, img_k4, img_k8

def histogram_ciz(canvas, gorsel):
    if gorsel.mode != 'L': gorsel = gorsel.convert('L')
    pixels = gorsel.load()
    w, h = gorsel.size
    hist = [0]*256
    for y in range(h):
        for x in range(w):
            hist[pixels[x, y]] += 1

    canvas.delete("all")
    canvas.update_idletasks() 
    genislik = canvas.winfo_width()
    yukseklik = canvas.winfo_height()
    
    if genislik < 10: return

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