import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox

# ================= MANUEL İŞLEMLER ================= #

def prewitt_hesapla(gorsel):
    if gorsel.mode != 'L':
        gorsel = gorsel.convert('L')
    
    pixels = gorsel.load()
    w, h = gorsel.size
    
    # Çıktı resimleri
    img_x = Image.new("L", (w, h))
    img_y = Image.new("L", (w, h))
    img_sonuc = Image.new("L", (w, h))
    
    pix_x = img_x.load()
    pix_y = img_y.load()
    pix_sonuc = img_sonuc.load()
    
    # Prewitt Kernelleri
    # Kx = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
    # Ky = [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
    
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            # Komşular
            tl = pixels[x-1, y-1]; tm = pixels[x, y-1]; tr = pixels[x+1, y-1]
            ml = pixels[x-1, y];   mm = pixels[x, y];   mr = pixels[x+1, y]
            bl = pixels[x-1, y+1]; bm = pixels[x, y+1]; br = pixels[x+1, y+1]
            
            # X Gradyan (Dikey çizgileri bulur)
            # (-1*tl + 0*tm + 1*tr) + ...
            gx = (tr + mr + br) - (tl + ml + bl)
            
            # Y Gradyan (Yatay çizgileri bulur)
            # (-1*tl + -1*tm + -1*tr) + ...
            gy = (bl + bm + br) - (tl + tm + tr)
            
            # Mutlak değer ve sınırlama
            val_x = abs(gx)
            val_y = abs(gy)
            
            if val_x > 255: val_x = 255
            if val_y > 255: val_y = 255
            
            pix_x[x, y] = val_x
            pix_y[x, y] = val_y
            
            # Orijinal + Kenarlar
            comb = pixels[x, y] + val_x + val_y
            if comb > 255: comb = 255
            
            pix_sonuc[x, y] = comb
            
    return gorsel, img_x, img_y, img_sonuc

def histogram_ciz(canvas, gorsel):
    # Manuel Histogram
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
        canvas.bind('<Configure>', lambda event, c=canvas, i=gorsel: histogram_ciz(c, i))

    hist_ekle(frame_histogramlar, orjinal, "Orijinal Histogram")
    hist_ekle(frame_histogramlar, prewitt_yatay, "Yatay Prewitt Histogram")
    hist_ekle(frame_histogramlar, prewitt_dikey, "Dikey Prewitt Histogram")
    hist_ekle(frame_histogramlar, orjinal_arti_prewitt, "Sonuç Histogram")
    return pencere