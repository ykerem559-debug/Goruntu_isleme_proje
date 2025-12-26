# perspektif.py (CVLİ klasörü için OpenCV Sürümü)
# -*- coding: utf-8 -*-

import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import cv2 # 🔴 OpenCV Eklendi
import sys, os

# 🔴 KRİTİK: cvislem'den dönüşüm fonksiyonlarını alıyoruz
# (Bu dosya cvislem ile aynı klasördeyse direkt import edilir)
try:
    from cvislem import pil_to_cv, cv_to_pil
except ImportError:
    # Eğer cvislem alt klasörde değilse, bu import'un ana ekrandan gelmesi gerekir.
    # Geçici olarak numpy kullanırız. Ancak gerçek projede cvislem'den gelmeli.
    pass 


# ======================================================
# ANA SINIF
# ======================================================
class PerspektifUygulama:
    def __init__(self, root, img_pil):
        self.root = root
        self.root.title("Perspektif Düzeltme (OpenCV)")
        self.root.resizable(False, False)

        # ----------------------------
        self.original_img_pil = img_pil.copy()
        self.img_cv = pil_to_cv(img_pil) # 🔴 Görüntüyü OpenCV formatına çevir
        self.points = []
        self.preview_cv = None # OpenCV sonuç görüntüsü
        self.M = None          # Dönüşüm Matrisi (OpenCV)

        # ======================================================
        # ANA YERLEŞİM (Aynı kalır)
        # ======================================================
        ana = tk.Frame(root, bg="#f2f2f2")
        ana.pack(padx=10, pady=10)

        # ... (SOL, ORTA, SAĞ frame'lerinin oluşturulması aynı kalır) ...
        # (Yerleşim kodunu kısaltıyorum)

        sol = tk.LabelFrame(ana, text="Kaynak Resim", width=320, height=320)
        sol.grid(row=0, column=0, padx=5, pady=5)
        sol.pack_propagate(False)

        self.canvas = tk.Canvas(sol, width=300, height=300, bg="#dddddd")
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.select_point)

        orta = tk.LabelFrame(ana, text="İşlem Kodu", width=320, height=320)
        orta.grid(row=0, column=1, padx=5, pady=5)
        orta.pack_propagate(False)

        self.code = tk.Text(orta, font=("Consolas", 9))
        self.code.pack(fill="both", expand=True)

        sag = tk.LabelFrame(ana, text="Çıktı", width=320, height=320)
        sag.grid(row=0, column=2, padx=5, pady=5)
        sag.pack_propagate(False)

        self.out_canvas = tk.Canvas(sag, width=300, height=300, bg="#dddddd")
        self.out_canvas.pack(padx=10, pady=10)
        
        alt = tk.Frame(ana)
        alt.grid(row=1, column=0, columnspan=3, pady=10)

        tk.Button(alt, text="Uygula", width=12, command=self.apply).pack(side="left", padx=5)
        tk.Button(alt, text="Sıfırla", width=12, command=self.reset).pack(side="left", padx=5)
        tk.Button(alt, text="Kapat", width=12, command=self.root.destroy).pack(side="left", padx=5)


        self.goster_sol(self.original_img_pil)
        self.kod_yaz_baslangic()

    # ======================================================
    # GÖSTERİM FONKSİYONLARI (PIL Kullanarak)
    # ======================================================
    def goster_sol(self, img_pil):
        # PIL kullanarak göster
        img = img_pil.resize((300, 300))
        self.tkimg = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tkimg)

    def goster_sag(self, img_cv):
        # 🔴 OpenCV'den PIL'e çevirip göster
        img_pil = cv_to_pil(img_cv)
        img = img_pil.resize((300, 300))
        self.tkout = ImageTk.PhotoImage(img)
        self.out_canvas.delete("all")
        self.out_canvas.create_image(0, 0, anchor="nw", image=self.tkout)

    # ======================================================
    def select_point(self, event):
        if len(self.points) >= 4:
            return

        self.points.append((event.x, event.y))
        self.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, fill="red")

        self.code.delete("1.0", "end")
        self.code.insert("end", "# Seçilen Noktalar (Canvas)\n")
        for i, p in enumerate(self.points):
            self.code.insert("end", f"P{i+1}: {p}\n")

        if len(self.points) < 4:
            self.code.insert("end", "\n# 4 nokta seçildiğinde OpenCV hesaplaması başlayacak.")

    # ======================================================
    def apply(self):
        if len(self.points) != 4:
            return

        h, w = self.img_cv.shape[:2]
        
        # Canvas boyutunu gerçek resim boyutuna ölçekle
        sx, sy = w / 300, h / 300

        # Gözlenen orijinal noktalar (Gerçek piksel koordinatları)
        src_points = np.float32([(x*sx, y*sy) for x, y in self.points])

        # Hedef noktalar (Yeni 300x300 kare)
        dst_points = np.float32([[0, 0], [w, 0], [w, h], [0, h]]) # 🔴 Hedef boyutu orijinal resmin boyutu yapıyoruz

        # 🔴 KRİTİK DEĞİŞİKLİK: OpenCV Matris Hesaplaması
        self.M = cv2.getPerspectiveTransform(src_points, dst_points)

        # 🔴 Dönüşüm Uygulama
        self.preview_cv = cv2.warpPerspective(
            self.img_cv, 
            self.M, 
            (w, h), # Orijinal boyutta sonuç döndür
            flags=cv2.INTER_LINEAR
        )

        self.goster_sag(self.preview_cv)
        self.kod_yaz_debug(src_points, dst_points)

    # ======================================================
    def reset(self):
        self.points.clear()
        self.M = None
        self.img_cv = pil_to_cv(self.original_img_pil.copy()) # 🔴 OpenCV'ye çevir
        self.preview_cv = None
        self.canvas.delete("all")
        self.out_canvas.delete("all")
        self.goster_sol(self.original_img_pil)
        self.kod_yaz_baslangic()

    # ======================================================
    def kod_yaz_baslangic(self):
        self.code.delete("1.0", "end")
        self.code.insert("end",
            "# 4 nokta seç (Sol Üst -> Sağ Üst -> Sağ Alt -> Sol Alt)\n"
            "# ardından Uygula'ya bas\n"
            "# OpenCV'nin matematiksel çözümü burada görünecek\n"
        )

    def kod_yaz_debug(self, src_points, dst_points):
        self.code.delete("1.0", "end")

        self.code.insert("end", "# === SRC (Gözlenen Orijinal Noktalar) ===\n")
        self.code.insert("end", f"{src_points}\n")

        self.code.insert("end", "\n# === DST (Hedef Noktalar - Tam Kare) ===\n")
        self.code.insert("end", f"{dst_points}\n")

        self.code.insert("end", "\n# === DÖNÜŞÜM MATRİSİ (M) ===\n")
        self.code.insert("end", f"{self.M.tolist()}\n")

        self.code.insert("end", """
# 🔴 OpenCV Kodu:
# M'i hesapla:
M = cv2.getPerspectiveTransform(src_points, dst_points)

# Görüntüyü dönüştür:
height, width = img_cv.shape[:2]
result = cv2.warpPerspective(
    img_cv, M, (width, height), 
    flags=cv2.INTER_LINEAR
)
"""
)

# ======================================================
# DIŞARDAN ÇAĞRILAN
# ======================================================
def goster_perspektif(img_pil):
    # DÖNÜŞÜM FONKSİYONLARI OLMAK ZORUNDA
    # Eğer cvislem import edilemediyse hata ver
    try:
        from cvislem import pil_to_cv, cv_to_pil
    except ImportError:
        tk.messagebox.showerror("Hata", "OpenCV perspektif işlemleri için 'cvislem.py' dosyasında pil_to_cv ve cv_to_pil dönüşüm fonksiyonları gereklidir.")
        return

    pencere = tk.Toplevel()
    PerspektifUygulama(pencere, img_pil)