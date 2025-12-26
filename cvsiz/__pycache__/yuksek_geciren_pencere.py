import tkinter as tk
from PIL import Image, ImageTk
import numpy as np

def laplacian_keskinlestir(gorsel):
    dizi = np.array(gorsel.convert("L"), dtype=np.float32)
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
    lap_min = np.min(lap)
    lap_max = np.max(lap)
    
    if lap_max != lap_min:
        lap_n = ((lap - lap_min) / (lap_max - lap_min) * 255).astype(np.uint8)
    else:
        lap_n = np.full(lap.shape, 128, dtype=np.uint8)
    keskin = np.clip(dizi + lap, 0, 255).astype(np.uint8)
    return (
        Image.fromarray(dizi.astype(np.uint8)),
        Image.fromarray(lap_n),
        Image.fromarray(keskin)
    )

def histogram_ciz(canvas, gorsel):
    dizi = np.array(gorsel.convert("L"))
    hist = np.bincount(dizi.flatten(), minlength=256)

    canvas.delete("all")
    canvas.update_idletasks() 
    genislik = canvas.winfo_width()
    yukseklik = canvas.winfo_height()
    
    m = hist.max() if hist.max() > 0 else 1
    ust_bosluk = 0 
    alt_bosluk = 20 
    cizim_yukseklik = yukseklik - ust_bosluk - alt_bosluk 

    olcek_x = genislik / 256
    olcek_y = cizim_yukseklik / m 
    canvas.create_line(0, yukseklik - alt_bosluk, genislik, yukseklik - alt_bosluk, fill="gray")
    
    for x in range(256):
        x0 = x * olcek_x
        y0 = yukseklik - alt_bosluk
        y1 = y0 - hist[x] * olcek_y 
        y1 = max(y1, ust_bosluk) 
        canvas.create_line(x0, y0, x0, y1, fill="black")
        
def goster_yuksek_geciren(gorsel):
    if gorsel is None:
        return

    orjinal, laplacian, keskin = laplacian_keskinlestir(gorsel)

    pencere = tk.Toplevel()
    pencere.title("Yüksek Geçiren Filtresi - Analiz Penceresi")
    pencere.geometry("1600x900") 
    pencere.resizable(False, False)
    pencere.configure(bg="white")

    ana_frame = tk.Frame(pencere, bg="white")
    ana_frame.pack(padx=10, pady=10, fill="both", expand=True) 

    frame_resimler = tk.Frame(ana_frame, bg="white")
    frame_resimler.pack(pady=10) 

    def resim_ekle(parent, gorsel, baslik):
        cerceve = tk.Frame(parent, bg="white")
        cerceve.pack(side="left", padx=20)

        lbl_baslik = tk.Label(cerceve, text=baslik, bg="white", font=("Arial", 16, "bold"))
        lbl_baslik.pack(pady=10)

        lbl_gorsel = tk.Label(cerceve, bg="white")
        lbl_gorsel.pack()

        tkimg = ImageTk.PhotoImage(gorsel.resize((400, 400))) 
        lbl_gorsel.config(image=tkimg)
        lbl_gorsel.image = tkimg

    resim_ekle(frame_resimler, orjinal, "Orijinal")
    resim_ekle(frame_resimler, laplacian, "Laplacian (Kenar Haritası)")
    resim_ekle(frame_resimler, keskin, "Keskinleştirilmiş")

    frame_histogramlar = tk.Frame(ana_frame, bg="white")
    frame_histogramlar.pack(pady=20, fill="both", expand=True) 

    def hist_ekle(parent, gorsel, baslik):
        cerceve = tk.Frame(parent, bg="white")
        cerceve.pack(side="left", padx=30, fill="both", expand=True) 
        lbl = tk.Label(cerceve, text=baslik, bg="white", font=("Arial", 14))
        lbl.pack(pady=5)
        canvas = tk.Canvas(cerceve, bg="white", highlightthickness=1) 
        canvas.pack(fill="both", expand=True)
        canvas.bind('<Configure>', lambda event, c=canvas, i=gorsel: histogram_ciz(c, i))
    hist_ekle(frame_histogramlar, orjinal, "Orijinal Histogram")
    hist_ekle(frame_histogramlar, laplacian, "Laplacian Histogram")
    hist_ekle(frame_histogramlar, keskin, "Keskinleştirilmiş Histogram")

    return pencere

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    from tkinter import filedialog
    from tkinter import messagebox
    yol = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.bmp")]) 
    if yol:
        try:
            img = Image.open(yol)
            goster_yuksek_geciren(img)
            root.mainloop()
        except Exception as e:
            messagebox.showerror("Hata", f"Görüntü işlenirken bir hata oluştu: {e}")
    else:
        print("Dosya seçilmedi, program sonlanıyor.")
