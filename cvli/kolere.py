# cvli/kolere.py
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageTk
import threading
import inspect
import cv2


# =====================================================
# ROI TABANLI KORELASYON (OPENCV + NUMPY)
# =====================================================
class KolereUygulama:
    def __init__(self, root, img_pil):
        self.root = root
        self.root.title("ROI Tabanlı Korelasyon (OpenCV)")
        self.root.resizable(False, False)

        # ---------------- Görüntüler ----------------
        self.img_color = img_pil.copy()
        # Gri tonlu resim (OpenCV formatı)
        self.I_cv = cv2.cvtColor(np.array(img_pil.convert("RGB")), cv2.COLOR_RGB2GRAY)
        self.I = self.I_cv.astype(float)

        self.start = None
        self.rect = None
        self.roi = None
        self.roi_coords = None

        # ---------------- Ana Yerleşim ----------------
        ana = tk.Frame(root)
        ana.pack(padx=10, pady=10)

        frame_sol_orta = tk.Frame(ana)
        frame_sol_orta.grid(row=0, column=0, columnspan=2)

        # -------- SOL --------
        sol = tk.LabelFrame(frame_sol_orta, text="Orijinal (ROI Seç)", width=330, height=330)
        sol.pack(side="left", padx=5)
        sol.pack_propagate(False)

        self.canvas = tk.Canvas(sol, width=300, height=300, bg="#ddd")
        self.canvas.pack(padx=5, pady=5)

        self.canvas.bind("<ButtonPress-1>", self.roi_basla)
        self.canvas.bind("<B1-Motion>", self.roi_ciz)
        self.canvas.bind("<ButtonRelease-1>", self.roi_bitir)

        # -------- ORTA --------
        orta = tk.LabelFrame(frame_sol_orta, text="İşlem Kodu", width=330, height=330)
        orta.pack(side="left", padx=5)
        orta.pack_propagate(False)

        self.code_text = tk.Text(orta, width=40, font=("Consolas", 9))
        self.code_text.pack(fill="both", expand=True)

        # -------- SAĞ --------
        sag = tk.LabelFrame(ana, text="Korelasyon Sonucu", width=330, height=330)
        sag.grid(row=0, column=2, padx=5)
        sag.pack_propagate(False)

        self.out = tk.Canvas(sag, width=300, height=300, bg="#ddd")
        self.out.pack(padx=5, pady=5)

        self.loading_text = self.out.create_text(
            150, 150, text="Hesaplanıyor...", fill="gray", font=("Arial", 14), state="hidden"
        )

        # -------- BUTONLAR --------
        alt = tk.Frame(ana)
        alt.grid(row=1, column=0, columnspan=3, pady=10)

        tk.Button(alt, text="Ortalama", width=12,
                  command=lambda: self.islem_baslat(self.ortalama_harita, "Ortalama")).pack(side="left", padx=3)

        tk.Button(alt, text="Varyans", width=12,
                  command=lambda: self.islem_baslat(self.varyans_harita, "Varyans")).pack(side="left", padx=3)

        tk.Button(alt, text="Çapraz Korelasyon", width=15,
                  command=lambda: self.islem_baslat(self.cc_hesapla, "Çapraz Korelasyon")).pack(side="left", padx=3)

        tk.Button(alt, text="Korelasyon", width=12,
                  command=lambda: self.islem_baslat(self.korelasyon_hesapla, "Korelasyon")).pack(side="left", padx=3)

        tk.Button(alt, text="Konvolüsyon", width=12,
                  command=lambda: self.islem_baslat(self.konvolusyon, "Konvolüsyon")).pack(side="left", padx=3)

        tk.Button(alt, text="Sıfırla", width=12, command=self.reset).pack(side="left", padx=3)

        self.goster_sol()
        self.kod_yaz_baslangic()

    # ==================================================
    # KOD PANELİ
    # ==================================================
    def kod_yaz_baslangic(self):
        self.code_text.delete("1.0", "end")
        self.code_text.insert("end", "# ROI seçin ve bir işlem butonuna basın.\n")

    def kod_yaz(self, func):
        try:
            # Async fonksiyonların içindeki hesaplama kodunu göstermek için
            f = func
            if func.__name__.endswith(("_async", "_hesapla")):
                if func.__name__ == "cc_hesapla":
                    f = self.cc_kod
                elif func.__name__ == "korelasyon_hesapla":
                    f = self.korelasyon_kod
                elif func.__name__ == "varyans_harita":
                    f = self.varyans_harita_kod
            
            self.code_text.delete("1.0", "end")
            self.code_text.insert("end", inspect.getsource(f))
        except Exception as e:
            self.code_text.insert("end", str(e))

    def islem_baslat(self, func, isim):
        self.kod_yaz(func)
        if self.roi is None and isim not in ["Ortalama", "Konvolüsyon"]: 
            messagebox.showwarning("Hata", f"{isim} için önce ROI seçin.")
            return
        
        # Ortalama ve Konvolüsyon yeterince hızlı, diğerlerini Threading ile başlatıyoruz
        if func.__name__ in ["varyans_harita", "cc_hesapla", "korelasyon_hesapla"]:
            self.islem_async(func)
        else:
            func()
    
    def islem_async(self, func):
        self.out.itemconfig(self.loading_text, state="normal")
        
        def worker():
            out = None
            if func.__name__ == "cc_hesapla":
                out = self.cc_hesapla_internal()
            elif func.__name__ == "korelasyon_hesapla":
                out = self.korelasyon_hesapla_internal()
            elif func.__name__ == "varyans_harita": 
                # Varyans işlemi yavaş olduğu için burada hesaplıyoruz
                out = self.varyans_hesapla_internal()

            self.root.after(0, lambda: self.islem_bitti(out))
            
        threading.Thread(target=worker, daemon=True).start()

    def islem_bitti(self, mat):
        self.out.itemconfig(self.loading_text, state="hidden")
        self.goster_sag(mat)


    # ==================================================
    # GÖSTERİM
    # ==================================================
    def goster_sol(self):
        im = Image.fromarray(self.I_cv).convert("RGB").resize((300, 300))
        self.tkimg = ImageTk.PhotoImage(im)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tkimg)

    def goster_sag(self, mat):
        mn, mx = mat.min(), mat.max()
        if (mx - mn) < 1e-6:
            norm = np.zeros_like(mat)
        else:
            norm = (mat - mn) / (mx - mn)

        gamma = 0.5
        img_array = np.clip(np.power(norm, gamma) * 255, 0, 255).astype(np.uint8)

        img = Image.fromarray(img_array).resize((300, 300), Image.NEAREST)
        self.tkout = ImageTk.PhotoImage(img)

        self.out.delete("all")
        self.out.create_image(0, 0, anchor="nw", image=self.tkout)

    # ==================================================
    # ROI
    # ==================================================
    def roi_basla(self, e):
        self.start = (e.x, e.y)
        self.canvas.delete("roi")
        self.canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="red", width=2, tags="roi")

    def roi_ciz(self, e):
        if not self.start:
            return
        x0, y0 = self.start
        self.canvas.coords("roi", x0, y0, e.x, e.y)

    def roi_bitir(self, e):
        if not self.start:
            return
        x0, y0 = self.start
        x1, y1 = e.x, e.y
        self.start = None

        w, h = self.img_color.size
        sx, sy = w / 300, h / 300

        x_min, x_max = int(min(x0, x1) * sx), int(max(x0, x1) * sx)
        y_min, y_max = int(min(y0, y1) * sy), int(max(y0, y1) * sy)

        if (x_max - x_min) < 2 or (y_max - y_min) < 2:
            messagebox.showwarning("ROI", "ROI çok küçük.")
            return

        self.roi = self.I_cv[y_min:y_max, x_min:x_max] # ROI'yi uint8 (I_cv) olarak alıyoruz

    # ==================================================
    # İŞLEMLER (OpenCV ve NumPy ile)
    # ==================================================

    def ortalama_harita(self):
        """Ortalama Filtresi (cv2.blur)"""
        kernel_size = 5 
        out = cv2.blur(self.I_cv, (kernel_size, kernel_size), borderType=cv2.BORDER_CONSTANT)
        self.goster_sag(out.astype(float))
        return out.astype(float) 

    def ortalama_harita_kod(self):
        """Kod Gösterimi: Ortalama Harita"""
        kernel_size = 5
        return f"""
# 🔴 OpenCV Ortalama Filtresi (Konvolüsyon)
# ===================================================
# cv2.blur, 5x5 çekirdek ile ortalama (kutu) filtresi uygular.
# Bu, basit yumuşatma için optimize edilmiş Konvolüsyon'dur.
kernel_size = {kernel_size}
out = cv2.blur(self.I_cv, (kernel_size, kernel_size), 
               borderType=cv2.BORDER_CONSTANT)
"""
    
    def varyans_hesapla_internal(self):
        """Varyans Haritası (NumPy ile, yavaş çalışır)"""
        if self.roi is not None:
            T = self.roi
        else:
            T = np.ones((5, 5), np.uint8) # Varsayılan 5x5

        h, w = T.shape
        H, W = self.I.shape
        out = np.zeros((H - h + 1, W - w + 1))
        
        # Varyans için optimize edilmiş CV fonksiyonu olmadığından NumPy döngüsü kullanılır
        for y in range(H - h + 1):
            for x in range(W - w + 1):
                out[y, x] = self.I[y:y+h, x:x+w].var()
        return out

    def varyans_harita(self):
        """Varyans Haritası (Threading ile çağrılır)"""
        # islem_async'e yönlendirilir
        return self.varyans_hesapla_internal()

    def varyans_harita_kod(self):
        """Kod Gösterimi: Varyans Haritası"""
        return """
# 🔴 OpenCV UYGULAMA (NumPy Yerel İstatistik)
# ===================================================
# OpenCV'de doğrudan Varyans Haritası fonksiyonu yoktur.
# Doku ve Kenar analizi için Yerel İstatistik (Varyans) hesaplanır.
# İşlem performansı için NumPy tabanlı, kayan pencere (For-loop) kullanılır.

h, w = ROI.shape # Ya da sabit bir çekirdek boyutu
out = np.zeros(...)
for y, x:
    # ROI bölgesindeki varyansı hesapla
    out[y, x] = I[y:y+h, x:x+w].var()
"""

    def konvolusyon(self):
        """Basit 3x3 Konvolüsyon (Kutu Filtresi)"""
        kernel = np.ones((3, 3), np.float32) / 9
        # cv2.filter2D, çekirdek döndürmeyi yaparak Konvolüsyon uygular.
        out = cv2.filter2D(self.I_cv, cv2.CV_64F, kernel)
        self.goster_sag(out)
        return out

    def konvolusyon_kod(self):
        """Kod Gösterimi: Konvolüsyon"""
        return """
# 🔴 OpenCV Konvolüsyon İşlemi
# ===================================================
# Görüntü filtrelemede temel işlemdir (180 derece çekirdek döndürme yapılır).
kernel = np.ones((3, 3), np.float32) / 9 
# cv2.CV_64F, çift duyarlıklı çıktı (hassas hesaplama) sağlar.
out = cv2.filter2D(self.I_cv, cv2.CV_64F, kernel)
"""


    # --- Çapraz Korelasyon (cv2.matchTemplate ile Optimize) ---
    def cc_hesapla_internal(self):
        T = self.roi
        # cv2.matchTemplate, T'yi I'da kaydırır. TM_CCORR, Çapraz Korelasyondur.
        out = cv2.matchTemplate(self.I_cv, T, cv2.TM_CCORR) 
        return out
        
    def cc_hesapla(self):
        """Çapraz Korelasyon (Threading ile çağrılır)"""
        return self.cc_hesapla_internal()

    def cc_kod(self):
        """Kod Gösterimi: Çapraz Korelasyon"""
        return """
# 🔴 OpenCV Çapraz Korelasyon İşlemi
# ===================================================
# ROI Tabanlı Şablon Eşleştirme (Template Matching) olarak uygulanır.
# cv2.TM_CCORR: Çekirdek döndürülmez (Çapraz Korelasyon).
T = self.roi # Seçilen şablon (ROI)
out = cv2.matchTemplate(self.I_cv, T, cv2.TM_CCORR)
"""

    # --- Korelasyon (cv2.matchTemplate ile Optimize) ---
    def korelasyon_hesapla_internal(self):
        T = self.roi
        # cv2.TM_CCOEFF_NORMED, normalize edilmiş korelasyondur (std sapma bazlı).
        out = cv2.matchTemplate(self.I_cv, T, cv2.TM_CCOEFF_NORMED)
        return out
        
    def korelasyon_hesapla(self):
        """Korelasyon (Threading ile çağrılır)"""
        return self.korelasyon_hesapla_internal()

    def korelasyon_kod(self):
        """Kod Gösterimi: Korelasyon"""
        return """
# 🔴 OpenCV Korelasyon İşlemi (cv2.matchTemplate)
# ===================================================
# Normalizasyonlu Şablon Eşleştirme (Korelasyon)
# TM_CCOEFF_NORMED: Normalizasyonlu Korelasyon hesaplar (Çıktı [-1.0, 1.0]).
T = self.roi
out = cv2.matchTemplate(self.I_cv, T, cv2.TM_CCOEFF_NORMED)

# +1.0 : Mükemmel Eşleşme (Tam Korelasyon)
# -1.0 : Tam Tersi Eşleşme 
"""
    # ==================================================
    def reset(self):
        self.roi = None
        self.out.delete("all")
        self.I_cv = cv2.cvtColor(np.array(self.img_color.convert("RGB")), cv2.COLOR_RGB2GRAY)
        self.I = self.I_cv.astype(float)
        self.goster_sol()
        self.kod_yaz_baslangic()


# =====================================================
def goster_kolere(img_pil):
    pencere = tk.Toplevel()
    KolereUygulama(pencere, img_pil)