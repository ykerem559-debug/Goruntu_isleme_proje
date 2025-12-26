# -*- coding: utf-8 -*-
import tkinter as tk
import gui_cerceve
import tkinter.messagebox

# --- 🔴 GÜNCELLENMİŞ IMPORTLAR (Tüm analiz pencereleri dahil) ---

try:
    from cvli.perspektif import goster_perspektif
except ImportError:
    goster_perspektif = None

try:
    from cvli.kolere import goster_kolere
except ImportError:
    goster_kolere = None
    
try:
    # Yüksek Geçiren Analiz Penceresi
    from cvli.yuksek_geciren_pencere import goster_yuksek_geciren 
except ImportError:
    goster_yuksek_geciren = None

try:
    # Gradyent Analiz Penceresi
    from cvli.gradyent import goster_gradyent 
except ImportError:
    goster_gradyent = None
    
try:
    # Prewitt Analiz Penceresi (Geniş Prewitt tuşu için kullanılır)
    from cvli.prewitt import goster_prewitt_analiz
except ImportError:
    goster_prewitt_analiz = None
    
try:
    # Geniş Laplace Analiz Penceresi
    from cvli.genislaplace import goster_laplace_analiz
except ImportError:
    goster_laplace_analiz = None

try:
    from cvli.morfolojipencere import goster_morfoloji
except ImportError:
    goster_morfoloji = None

# 🔴 YENİ: CVLİ TUZ BİBER ANALİZ MODÜLÜNÜ İMPORT ET
try:
    from cvli.tuzbiber import goster_tuzbiber_analiz_cv
except ImportError:
    goster_tuzbiber_analiz_cv = None
# --- DÜZELTME SONU ---


def opencv_paneli_olustur(container):
    butonlar = {}

    frame_ust = tk.LabelFrame(
        container, text="Görüntü İşleme Araçları (OpenCV'li)",
        font=("Arial", 9, "bold"), bg="#b7f1ed", bd=2
    )
    frame_ust.pack(side="top", fill="both", expand=True, pady=(0, 2))

    frame_alt = tk.LabelFrame(
        container, text="Toplu İşlemler (OpenCV'li)",
        font=("Arial", 9, "bold"), bg="#e5b1f0", bd=2
    )
    frame_alt.pack(side="bottom", fill="x", pady=(2, 0))

    for i in range(4):
        frame_ust.grid_columnconfigure(i, weight=1)
        frame_alt.grid_columnconfigure(i, weight=1, uniform="alt")
    frame_alt.grid_rowconfigure(0, weight=1)

    ana_butonlar = [
        "Gri", "Negatif", "Parlaklık", "Kontrast",
        "Eşikleme", "Logaritmik", "Kontrast Germe", "Histogram Eşitleme",
        "Mean Filter", "Gaussian Filter", "Median Filter", "Laplacian",
        "Sobel Yatay", "Sobel Dikey", "Prewitt", "Açı Döndürme",
        "Aynalama", "Ters Çevirme", "Öteleme", "Yeniden Boyutlandırma"
    ]

    for idx, isim in enumerate(ana_butonlar):
        r, c = idx // 4, idx % 4
        btn = tk.Button(frame_ust, text=isim, height=2, font=("Arial", 8))
        btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
        butonlar[isim] = btn

    # -----------------------------
    # Morfoloji
    # -----------------------------
    def morfoloji_ac():
        if gui_cerceve.current_image is None:
            return
        if goster_morfoloji:
            goster_morfoloji(gui_cerceve.current_image)
        else:
            tk.messagebox.showerror("Hata", "Morfoloji modülü (cvli/morfolojipencere.py) bulunamadı.")

    btn_morf = tk.Button(
        frame_ust, text="Morfoloji", height=2,
        font=("Arial", 10, "bold"), bg="#d0d0d0", command=morfoloji_ac
    )
    btn_morf.grid(row=5, column=0, columnspan=4, padx=2, pady=(6, 2), sticky="nsew")
    butonlar["Morfoloji"] = btn_morf

    # -----------------------------
    # Perspektif (OpenCV'li)
    # -----------------------------
    def perspektif_ac():
        if gui_cerceve.current_image is None:
            return
        if goster_perspektif:
            goster_perspektif(gui_cerceve.current_image) 
        else:
            tk.messagebox.showerror("Hata", "Perspektif modülü (cvli/perspektif.py) bulunamadı.")

    btn_persp = tk.Button(
        frame_ust, text="Perspektif", height=2,
        font=("Arial", 10, "bold"), bg="#cfd8ff", command=perspektif_ac
    )
    btn_persp.grid(row=6, column=0, columnspan=2, padx=2, pady=(2, 6), sticky="nsew")
    butonlar["Perspektif"] = btn_persp

    # -----------------------------
    # Korelasyon (OpenCV'li)
    # -----------------------------
    def kolere_ac():
        if gui_cerceve.current_image is None:
            return
        if goster_kolere:
            goster_kolere(gui_cerceve.current_image)
        else:
            tk.messagebox.showerror("Hata", "Korelasyon modülü (cvli/kolere.py) bulunamadı.")

    btn_kolere = tk.Button(
        frame_ust, text="Korelasyon", height=2,
        font=("Arial", 10, "bold"), bg="#cfd8ff", command=kolere_ac
    )
    btn_kolere.grid(row=6, column=2, columnspan=2, padx=2, pady=(2, 6), sticky="nsew")
    butonlar["Korelasyon"] = btn_kolere

    # -----------------------------
    # Alt analiz (Toplu İşlemler)
    # -----------------------------
    
    # YÜKSEK GEÇİREN KOMUTU TANIMLANIYOR
    def yuksek_geciren_ac():
        if gui_cerceve.current_image is None:
            return
        if goster_yuksek_geciren:
            goster_yuksek_geciren(gui_cerceve.current_image) 
        else:
            tk.messagebox.showerror("Hata", "Yüksek Geçiren Analiz modülü bulunamadı.")
            
    # GRADYENT KOMUTU TANIMLANIYOR
    def gradyent_ac():
        if gui_cerceve.current_image is None:
            return
        if goster_gradyent:
            goster_gradyent(gui_cerceve.current_image) 
        else:
            tk.messagebox.showerror("Hata", "Gradyent Analiz modülü bulunamadı.")
            
    # PREWITT ANALİZ KOMUTU (Geniş Prewitt tuşu için)
    def prewitt_analiz_ac():
        if gui_cerceve.current_image is None:
            return
        if goster_prewitt_analiz:
            goster_prewitt_analiz(gui_cerceve.current_image) 
        else:
            tk.messagebox.showerror("Hata", "Prewitt Analiz modülü bulunamadı.")
            
    # GENİŞ LAPLACE KOMUTU
    def genis_laplace_ac():
        if gui_cerceve.current_image is None:
            return
        if goster_laplace_analiz:
            goster_laplace_analiz(gui_cerceve.current_image) 
        else:
            tk.messagebox.showerror("Hata", "Geniş Laplace Analiz modülü bulunamadı.")

    # 🔴 YENİ: TUZ BİBER ANALİZ KOMUTU (CVLİ)
    def tuzbiber_analiz_ac_cv():
        if gui_cerceve.current_image is None:
            return
        if goster_tuzbiber_analiz_cv: 
            goster_tuzbiber_analiz_cv(gui_cerceve.current_image)
        else:
            tk.messagebox.showerror("Hata", "Tuz Biber Analiz modülü bulunamadı (cvli/tuzbiber_cv.py).")

            
    analizler = ["Yüksek Geçiren", "Gradyent", "Geniş Laplace", "Geniş Prewitt", "Tuz Biber Analiz"] # 🔴 Yeni buton eklendi
    
    for i, isim in enumerate(analizler):
        btn = tk.Button(frame_alt, text=isim, height=2,
                        font=("Arial", 8, "bold"), bg="#999689")
        btn.grid(row=0, column=i, padx=2, pady=2, sticky="nsew")
        butonlar[isim] = btn
        
        # 🔴 KRİTİK BAĞLANTI ATAMALARI
        if isim == "Yüksek Geçiren":
            btn.config(command=yuksek_geciren_ac)
        
        if isim == "Gradyent":
            btn.config(command=gradyent_ac)
            
        if isim == "Geniş Laplace":
            btn.config(command=genis_laplace_ac)
            
        if isim == "Geniş Prewitt":
            btn.config(command=prewitt_analiz_ac) # Analiz penceresi Prewitt'e atanmıştır.
            
        if isim == "Tuz Biber Analiz":
            btn.config(command=tuzbiber_analiz_ac_cv) # 🔴 Yeni komut ataması

    return butonlar