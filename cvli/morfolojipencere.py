# -*- coding: utf-8 -*-
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import inspect
from tkinter import messagebox
import gui_cerceve 
import numpy as np

# 🔴 DÜZELTME: cvislem dosyasını import etmeye çalış
# Bu blok, cv_morfoloji fonksiyonunu bulmaya çalışır.
try:
    from cvislem import cv_morfoloji, pil_to_cv, cv_to_pil 
    # cv_to_pil'i de dahil ettik, çünkü Morfoloji kodu cv_to_pil kullanıyordu.
except ImportError:
    try:
        from cvli.cvislem import cv_morfoloji, pil_to_cv, cv_to_pil
    except Exception:
        cv_morfoloji = None
        # Fonksiyonlar bulunamazsa güvenli varsayılanlar
        cv_to_pil = lambda x: Image.new("L", (1, 1))
        pil_to_cv = lambda x: np.zeros((1, 1, 3), dtype=np.uint8) 


def uygula_morfoloji(img_orjinal, islem_tipi):
    """cv_morfoloji fonksiyonunu sabit çekirdek boyutuyla (3x3) çağırır."""
    if cv_morfoloji is None:
        messagebox.showerror("Hata", "OpenCV Morfoloji fonksiyonu bulunamadı. (cvislem.py)")
        return img_orjinal 

    CEKIRDEK_BOYUTU = 3 
    
    try:
        # Morfolojik işlemleri gerçekleştir
        img_sonuc = cv_morfoloji(img_orjinal, islem_tipi, CEKIRDEK_BOYUTU)
        return img_sonuc
    except Exception as e:
        messagebox.showerror("İşlem Hatası", f"{islem_tipi} uygulanırken hata: {e}")
        return img_orjinal


# =========================================================
# Görüntüyü sığdırma için temel yardımcı fonksiyon
# =========================================================
def resize_to_fit(img, max_w, max_h):
    w, h = img.size
    oran = min(max_w / w, max_h / h)
    if oran >= 1: return img.copy()
    nw, nh = int(w * oran), int(h * oran)
    # Image.LANCZOS kullanmak için PIL/Pillow'u doğru import ettiğinizden emin olun
    return img.resize((nw, nh), Image.LANCZOS)


# =========================================================
#                 HİSTOGRAM ÇİZİMİ (Sizin kodunuzdan alındı)
# =========================================================
def ciz_histogram_morf(img, canvas):
    try:
        # Renkli resmi griye çevirip NumPy dizisine al
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
# MORFOLOJİ PENCERESİ (OpenCV - Yeniden Düzenlenmiş Konumlar)
# =========================================================
def goster_morfoloji(orjinal_resim):

    penc = tk.Toplevel()
    penc.title("Morfolojik İşlemler (OpenCV)")
    penc.geometry("1300x750")
    penc.resizable(False, False)

    # ============================================
    # SOL PANEL — ORİJİNAL (Sizin Genişlik/Yükseklik Ayarınız)
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
    # ORTA PANEL — KOD (Küçültülmüş Genişlik + Yükseklik Korundu)
    # ============================================
    orta = tk.Frame(penc, bg="#eeeeee")
    # Genişlik: 0.20 (Sizin Ayarınız), Yükseklik: 0.80 (Korundu)
    orta.place(relx=0.27, rely=0.05, relwidth=0.20, relheight=0.80) 

    tk.Label(orta, text="İşlem Kodu (OpenCV)", bg="#eeeeee",
             font=("Arial", 12, "bold")).pack()

    kod_text = tk.Text(orta, font=("Consolas", 9))
    kod_text.pack(fill="both", expand=True)


    # ============================================
    # YENİ PANEL — HİSTOGRAM (Büyütülmüş Genişlik + Yükseklik Korundu)
    # ============================================
    hist_panel = tk.Frame(penc, bg="#ffffff")
    # relx: 0.48 (Sizin Ayarınız), Genişlik: 0.26 (Sizin Ayarınız), Yükseklik: 0.80 (Korundu)
    hist_panel.place(relx=0.48, rely=0.05, relwidth=0.26, relheight=0.80)
    
    tk.Label(hist_panel, text="Sonuç Histogramı", bg="#ffffff",
             font=("Arial", 12, "bold")).pack()
             
    hist_canvas = tk.Canvas(hist_panel, bg="white", width=200, height=450)
    hist_canvas.pack(fill="both", expand=True, padx=5, pady=5)


    # ============================================
    # SAĞ PANEL — SONUÇ (Sizin Genişlik/Yükseklik Ayarınız)
    # ============================================
    sag = tk.Frame(penc, bg="#dddddd")
    # relx: 0.74, Genişlik: 0.25, Yükseklik: 0.80 (Korundu)
    sag.place(relx=0.74, rely=0.05, relwidth=0.25, relheight=0.80)

    tk.Label(sag, text="İşlenmiş Resim",
             bg="#dddddd", font=("Arial", 12, "bold")).pack()

    sonuc_lbl = tk.Label(sag, bg="#dddddd")
    sonuc_lbl.pack(pady=10)

    # 🔴 GÜNCELLEME FONKSİYONU (OpenCV'li mantık)
    def guncelle_opencv(islem_tipi):
        # İşlemi yap
        img_sonuc = uygula_morfoloji(orjinal_resim, islem_tipi)

        # Görüntüyü sığdırma ve gösterme
        fit = resize_to_fit(img_sonuc, 360, 500)
        tkimg = ImageTk.PhotoImage(fit)
        sonuc_lbl.config(image=tkimg)
        sonuc_lbl.image = tkimg
        
        # Histogramı çiz
        ciz_histogram_morf(img_sonuc, hist_canvas)
        
        # Kodu gösterme
        CEKIRDEK_BOYUTU = 3
        
        if islem_tipi == "orjinal":
            kod_aciklama = "--- MORFOLOJİ HAZIR ---\nLütfen bir işlem seçin (Erozyon, Genişleme, vb.).\n"
        elif islem_tipi in ["erozyon", "genisleme"]:
            cv_fonk = "cv2.erode" if islem_tipi == "erozyon" else "cv2.dilate"
            kod_aciklama = f"""--- {islem_tipi.upper()} (OpenCV) ---

import cv2, numpy as np
# Resim önce BGR'ye (OpenCV formatı) çevrilir.
cv_img = pil_to_cv(img) 

kernel = np.ones(({CEKIRDEK_BOYUTU}, {CEKIRDEK_BOYUTU}), np.uint8)

# Tekrarlama sayısı (Iterations) varsayılan 1
sonuc = {cv_fonk}(cv_img, kernel, iterations=1)
"""
        else:
            cv_morph_tipi = f"cv2.MORPH_{islem_tipi.upper()}"
            kod_aciklama = f"""--- {islem_tipi.upper()} (OpenCV) ---

import cv2, numpy as np
# Resim önce BGR'ye (OpenCV formatı) çevrilir.
cv_img = pil_to_cv(img)

kernel = np.ones(({CEKIRDEK_BOYUTU}, {CEKIRDEK_BOYUTU}), np.uint8)

# İşlem Tipi: {cv_morph_tipi}
sonuc = cv2.morphologyEx(cv_img, {cv_morph_tipi}, kernel)
"""
            
        kod_text.delete("1.0", tk.END)
        kod_text.insert("1.0", kod_aciklama)

        # Ana ekranı güncelle (Opsiyonel)
        if hasattr(gui_cerceve, 'gui_sonuc_goster') and hasattr(gui_cerceve, 'cerceveler'):
            gui_cerceve.gui_sonuc_goster(img_sonuc, gui_cerceve.cerceveler)


    # ============================================
    # ALT BUTONLAR (OpenCV işlem tiplerine göre düzenlendi)
    # ============================================
    alt = tk.Frame(penc, bg="#cccccc")
    alt.place(relx=0.01, rely=0.86,
              relwidth=0.98, relheight=0.12)

    for i in range(8):
        alt.grid_columnconfigure(i, weight=1)

    # OpenCV'de karşılığı olan işlemler (uygula_morfoloji'ye gönderilen tipler)
    islemler = [
        ("Erozyon", "erozyon"),
        ("Genişleme", "genisleme"),
        ("Açma", "acma"),
        ("Kapama", "kapama"),
        ("Gradyent", "gradient"), 
        ("Top-Hat", "tophat"),     
        ("Black-Hat", "blackhat"), 
    ]

    for i, (isim, islem_tipi) in enumerate(islemler):
        tk.Button(
            alt, text=isim, height=2,
            font=("Arial", 10, "bold"),
            command=lambda tip=islem_tipi: guncelle_opencv(tip)
        ).grid(row=0, column=i, sticky="nsew",
               padx=3, pady=5)

    # Varsayılan sıfırlama
    tk.Button(
        alt, text="Varsayılan (Sıfırla)", height=2,
        font=("Arial", 10, "bold"), bg="#ffbbbb",
        command=lambda: guncelle_opencv("orjinal") 
    ).grid(row=0, column=7, sticky="nsew",
           padx=3, pady=5)
            
    # Pencere açıldığında ilk işlemi yap
    penc.after(100, lambda: guncelle_opencv("orjinal"))