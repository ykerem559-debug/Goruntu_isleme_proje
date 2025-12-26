# -*- coding: utf-8 -*-
import tkinter as tk
from PIL import Image, ImageTk
import inspect
import numpy as np # Histogram için gerekli import

# =========================================================
#                GÖRÜNTÜ BOYUTLANDIRMA (AUTO-FIT)
# =========================================================
def resize_to_fit(img, max_w, max_h):
    w, h = img.size
    oran = min(max_w / w, max_h / h)
    if oran >= 1:
        return img.copy()  # zaten sığıyor
    nw, nh = int(w * oran), int(h * oran)
    return img.resize((nw, nh))


# =========================================================
#                  GRİYE DÖNÜŞTÜRME
# =========================================================
def to_grayscale(img):
    if img.mode == "L":
        return img.copy()
    w, h = img.size
    gri = Image.new("L", (w, h))
    px = img.convert("RGB").load()
    pg = gri.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            pg[x, y] = int(r * 0.299 + g * 0.587 + b * 0.114)
    return gri


# =========================================================
#                 HİSTOGRAM ÇİZİMİ
# =========================================================
def ciz_histogram_morf(img, canvas):
    try:
        arr = np.array(img.convert("L"))
        hist = np.bincount(arr.flatten(), minlength=256)

        canvas.delete("all")
        canvas.update_idletasks()
        
        gen = canvas.winfo_width()
        yuk = canvas.winfo_height()

        ust = 15
        alt = 5

        yuk_cizim = yuk - ust - alt
        m = max(hist) if hist.max() > 0 else 1
        
        if m == 0: m = 1

        ox = gen / 256
        oy = yuk_cizim / m

        zemin = yuk - alt
        canvas.create_line(0, zemin, gen, zemin, fill="gray")

        for i in range(256):
            x0 = i * ox
            y1 = zemin - hist[i] * oy
            y1 = max(y1, ust)
            canvas.create_line(x0, zemin, x0, y1, fill="black")

    except Exception as e:
        print("Morfoloji Histogram hatası:", e)


# =========================================================
#        EROSION — TAMAMEN BAĞIMSIZ AKADEMİK KOD
# =========================================================
def erosion(img):
    g = to_grayscale(img)
    w, h = g.size
    p  = g.load()

    out = Image.new("L", (w, h))
    po  = out.load()

    for y in range(1, h-1):
        for x in range(1, w-1):
            mn = p[x-1, y-1]
            for j in (-1, 0, 1):
                for i in (-1, 0, 1):
                    val = p[x+i, y+j]
                    if val < mn:
                        mn = val
            po[x, y] = mn

    return out


# =========================================================
#        DILATION — TAMAMEN BAĞIMSIZ AKADEMİK KOD
# =========================================================
def dilation(img):
    g = to_grayscale(img)
    w, h = g.size
    p = g.load()

    out = Image.new("L", (w, h))
    po  = out.load()

    for y in range(1, h-1):
        for x in range(1, w-1):
            mx = p[x-1, y-1]
            for j in (-1, 0, 1):
                for i in (-1, 0, 1):
                    val = p[x+i, y+j]
                    if val > mx:
                        mx = val
            po[x, y] = mx

    return out


# =========================================================
#                OPENING — GÖMÜLÜ HESAP
# =========================================================
def opening(img):
    g = to_grayscale(img)
    w, h = g.size
    p = g.load()

    # --- erosion ---
    er = Image.new("L", (w, h))
    per = er.load()
    for y in range(1, h-1):
        for x in range(1, w-1):
            mn = p[x-1, y-1]
            for j in (-1,0,1):
                for i in (-1,0,1):
                    v = p[x+i, y+j]
                    if v < mn: mn = v
            per[x, y] = mn

    # --- dilation ---
    out = Image.new("L", (w, h))
    po = out.load()
    p2 = er.load()

    for y in range(1, h-1):
        for x in range(1, w-1):
            mx = p2[x-1, y-1]
            for j in (-1,0,1):
                for i in (-1,0,1):
                    v = p2[x+i, y+j]
                    if v > mx: mx = v
            po[x, y] = mx

    return out


# =========================================================
#                CLOSING — GÖMÜLÜ HESAP
# =========================================================
def closing(img):
    g = to_grayscale(img)
    w, h = g.size
    p = g.load()

    # --- dilation ---
    dl = Image.new("L", (w, h))
    pdl = dl.load()
    for y in range(1, h-1):
        for x in range(1, w-1):
            mx = p[x-1, y-1]
            for j in (-1,0,1):
                for i in (-1,0,1):
                    v = p[x+i, y+j]
                    if v > mx: mx = v
            pdl[x, y] = mx

    # --- erosion ---
    out = Image.new("L", (w, h))
    po = out.load()
    p2 = dl.load()

    for y in range(1, h-1):
        for x in range(1, w-1):
            mn = p2[x-1, y-1]
            for j in (-1,0,1):
                for i in (-1,0,1):
                    v = p2[x+i, y+j]
                    if v < mn: mn = v
            po[x, y] = mn

    return out


# =========================================================
#                GRADIENT — di - er
# =========================================================
def gradient(img):
    g = to_grayscale(img)
    w, h = g.size
    p = g.load()

    # erosion
    er = Image.new("L", (w, h))
    per = er.load()
    for y in range(1, h-1):
        for x in range(1, w-1):
            mn = p[x-1, y-1]
            for j in (-1,0,1):
                for i in (-1,0,1):
                    v = p[x+i, y+j]
                    if v < mn: mn = v
            per[x, y] = mn

    # dilation
    di = Image.new("L", (w, h))
    pdi = di.load()
    for y in range(1, h-1):
        for x in range(1, w-1):
            mx = p[x-1, y-1]
            for j in (-1,0,1):
                for i in (-1,0,1):
                    v = p[x+i, y+j]
                    if v > mx: mx = v
            pdi[x, y] = mx

    # fark
    out = Image.new("L", (w, h))
    po = out.load()
    for y in range(h):
        for x in range(w):
            v = pdi[x, y] - per[x, y]
            if v < 0: v = 0
            if v > 255: v = 255
            po[x, y] = v

    return out


# =========================================================
#          TOP-HAT — original - opening
# =========================================================
def top_hat(img):
    op = opening(img)
    g = to_grayscale(img)

    w, h = g.size
    pg = g.load()
    po = op.load()

    out = Image.new("L", (w, h))
    pr = out.load()

    for y in range(h):
        for x in range(w):
            v = pg[x, y] - po[x, y]
            if v < 0: v = 0
            pr[x, y] = v

    return out


# =========================================================
#      BLACK-HAT — closing - original
# =========================================================
def black_hat(img):
    cl = closing(img)
    g = to_grayscale(img)

    w, h = g.size
    pg = g.load()
    pc = cl.load()

    out = Image.new("L", (w, h))
    pr = out.load()

    for y in range(h):
        for x in range(w):
            v = pc[x, y] - pg[x, y]
            if v < 0:
                v = 0
            pr[x, y] = v

    return out


# =========================================================
#         MORFOLOJİ PENCERESİ (AUTO-FIT'li)
# =========================================================
def goster_morfoloji(orjinal_resim):

    penc = tk.Toplevel()
    penc.title("Morfolojik İşlemler (Akademik Manuel)")
    penc.geometry("1300x750")
    penc.resizable(False, False)

    # ============================================
    # SOL PANEL — ORİJİNAL
    # ============================================
    sol = tk.Frame(penc, bg="#dddddd")
    sol.place(relx=0.01, rely=0.05, relwidth=0.25, relheight=0.80) 

    tk.Label(sol, text="Orijinal", bg="#dddddd",
             font=("Arial", 12, "bold")).pack()

    fit_org = resize_to_fit(orjinal_resim, 360, 500)
    tk_img_org = ImageTk.PhotoImage(fit_org)

    lbl_org = tk.Label(sol, image=tk_img_org, bg="#dddddd")
    lbl_org.image = tk_img_org
    lbl_org.pack(pady=10)


    # ============================================
    # ORTA PANEL — KOD (Küçültülmüş Genişlik)
    # ============================================
    orta = tk.Frame(penc, bg="#eeeeee")
    # Genişlik: 0.20
    orta.place(relx=0.27, rely=0.05, relwidth=0.20, relheight=0.80) 

    tk.Label(orta, text="İşlem Kodu", bg="#eeeeee",
             font=("Arial", 12, "bold")).pack()

    kod_text = tk.Text(orta, font=("Consolas", 9))
    kod_text.pack(fill="both", expand=True)


    # ============================================
    # YENİ PANEL — HİSTOGRAM (Büyütülmüş Genişlik)
    # ============================================
    hist_panel = tk.Frame(penc, bg="#ffffff")
    # relx: 0.48, Genişlik: 0.26
    hist_panel.place(relx=0.48, rely=0.05, relwidth=0.26, relheight=0.80) 
    
    tk.Label(hist_panel, text="Sonuç Histogramı", bg="#ffffff",
             font=("Arial", 12, "bold")).pack()
             
    hist_canvas = tk.Canvas(hist_panel, bg="white", width=200, height=450)
    hist_canvas.pack(fill="both", expand=True, padx=5, pady=5)


    # ============================================
    # SAĞ PANEL — SONUÇ
    # ============================================
    sag = tk.Frame(penc, bg="#dddddd")
    # relx: 0.74, Genişlik: 0.25
    sag.place(relx=0.74, rely=0.05, relwidth=0.25, relheight=0.80) 

    tk.Label(sag, text="İşlenmiş Resim",
             bg="#dddddd", font=("Arial", 12, "bold")).pack()

    sonuc_lbl = tk.Label(sag, bg="#dddddd")
    sonuc_lbl.pack(pady=10)


    def guncelle(img, fonk):
        fit = resize_to_fit(img, 360, 500)
        tkimg = ImageTk.PhotoImage(fit)
        sonuc_lbl.config(image=tkimg)
        sonuc_lbl.image = tkimg

        # Histogram çizimi güncelleniyor
        ciz_histogram_morf(img, hist_canvas)

        kod_text.delete("1.0", tk.END)
        kod_text.insert("1.0",
            f"--- {fonk.__name__.upper()} ---\n\n" +
            inspect.getsource(fonk)
        )


    # ============================================
    # ALT BUTONLAR
    # ============================================
    alt = tk.Frame(penc, bg="#cccccc")
    alt.place(relx=0.01, rely=0.86,
              relwidth=0.98, relheight=0.12)

    for i in range(8):
        alt.grid_columnconfigure(i, weight=1)

    islemler = [
        ("Erosion", erosion),
        ("Dilation", dilation),
        ("Opening", opening),
        ("Closing", closing),
        ("Gradient", gradient),
        ("Top-Hat", top_hat),
        ("Black-Hat", black_hat),
    ]

    for i, (isim, fonk) in enumerate(islemler):
        tk.Button(
            alt, text=isim, height=2,
            font=("Arial", 10, "bold"),
            command=lambda f=fonk: guncelle(f(orjinal_resim), f)
        ).grid(row=0, column=i, sticky="nsew",
               padx=3, pady=5)

    tk.Button(
        alt, text="Varsayılan (Sıfırla)", height=2,
        font=("Arial", 10, "bold"), bg="#ffbbbb",
        command=lambda: guncelle(orjinal_resim, lambda x: x)
    ).grid(row=0, column=7, sticky="nsew",
           padx=3, pady=5)
    
    # 🔴 YENİ EKLENEN SATIR: Pencere açılır açılmaz orijinal resmi göster ve histogramını çiz
    penc.after(100, lambda: guncelle(orjinal_resim, lambda x: x))