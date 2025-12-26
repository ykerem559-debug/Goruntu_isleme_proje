# perspektif.py
# -*- coding: utf-8 -*-

import tkinter as tk
import numpy as np
from PIL import Image, ImageTk


# ======================================================
# ANA SINIF
# ======================================================
class PerspektifUygulama:
    def __init__(self, root, img_pil):
        self.root = root
        self.root.title("Perspektif Düzeltme")
        self.root.resizable(False, False)

        # ----------------------------
        self.original_img = img_pil.copy()
        self.img_pil = img_pil.copy()
        self.points = []
        self.preview = None

        # debug alanları
        self.src = None
        self.dst = None
        self.A = None
        self.B = None
        self.coeffs = None

        # ======================================================
        # ANA YERLEŞİM
        # ======================================================
        ana = tk.Frame(root, bg="#f2f2f2")
        ana.pack(padx=10, pady=10)

        # ---------- SOL ----------
        sol = tk.LabelFrame(ana, text="Kaynak Resim", width=320, height=320)
        sol.grid(row=0, column=0, padx=5, pady=5)
        sol.pack_propagate(False)

        self.canvas = tk.Canvas(sol, width=300, height=300, bg="#dddddd")
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.select_point)

        # ---------- ORTA ----------
        orta = tk.LabelFrame(ana, text="İşlem Kodu", width=320, height=320)
        orta.grid(row=0, column=1, padx=5, pady=5)
        orta.pack_propagate(False)

        self.code = tk.Text(orta, font=("Consolas", 9))
        self.code.pack(fill="both", expand=True)

        # ---------- SAĞ ----------
        sag = tk.LabelFrame(ana, text="Çıktı", width=320, height=320)
        sag.grid(row=0, column=2, padx=5, pady=5)
        sag.pack_propagate(False)

        self.out_canvas = tk.Canvas(sag, width=300, height=300, bg="#dddddd")
        self.out_canvas.pack(padx=10, pady=10)

        # ---------- ALT ----------
        alt = tk.Frame(ana)
        alt.grid(row=1, column=0, columnspan=3, pady=10)

        tk.Button(alt, text="Uygula", width=12, command=self.apply).pack(side="left", padx=5)
        tk.Button(alt, text="Sıfırla", width=12, command=self.reset).pack(side="left", padx=5)
        tk.Button(alt, text="Kapat", width=12, command=self.root.destroy).pack(side="left", padx=5)

        self.goster_sol(self.img_pil)
        self.kod_yaz_baslangic()

    # ======================================================
    def goster_sol(self, img):
        img = img.resize((300, 300))
        self.tkimg = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tkimg)

    def goster_sag(self, img):
        img = img.resize((300, 300))
        self.tkout = ImageTk.PhotoImage(img)
        self.out_canvas.delete("all")
        self.out_canvas.create_image(0, 0, anchor="nw", image=self.tkout)

    # ======================================================
    def select_point(self, event):
        if len(self.points) >= 4:
            return

        self.points.append((event.x, event.y))
        self.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, fill="red")

        # nokta seçimi canlı yazılsın
        self.code.delete("1.0", "end")
        self.code.insert("end", "# Seçilen Noktalar (Canvas)\n")
        for i, p in enumerate(self.points):
            self.code.insert("end", f"P{i+1}: {p}\n")

        if len(self.points) < 4:
            self.code.insert("end", "\n# 4 nokta seçildiğinde matematik hesaplanacak")

    # ======================================================
    def apply(self):
        if len(self.points) != 4:
            return

        w, h = self.img_pil.size
        sx, sy = w / 300, h / 300

        # gözlenenler
        self.src = [(x*sx, y*sy) for x, y in self.points]
        self.dst = [(0, 0), (300, 0), (300, 300), (0, 300)]

        self.coeffs, self.A, self.B = find_perspective_coeffs_debug(self.dst, self.src)

        self.preview = self.img_pil.transform(
            (300, 300),
            Image.PERSPECTIVE,
            self.coeffs,
            Image.BICUBIC
        )

        self.goster_sag(self.preview)
        self.kod_yaz_debug()

    # ======================================================
    def reset(self):
        self.points.clear()
        self.src = self.dst = self.A = self.B = self.coeffs = None
        self.img_pil = self.original_img.copy()
        self.preview = None
        self.canvas.delete("all")
        self.out_canvas.delete("all")
        self.goster_sol(self.img_pil)
        self.kod_yaz_baslangic()

    # ======================================================
    def kod_yaz_baslangic(self):
        self.code.delete("1.0", "end")
        self.code.insert("end",
            "# 4 nokta seç\n"
            "# ardından Uygula'ya bas\n"
            "# gözlenen matematik burada görünecek\n"
        )

    def kod_yaz_debug(self):
        self.code.delete("1.0", "end")

        self.code.insert("end", "# === SRC (Orijinal Noktalar) ===\n")
        for i, p in enumerate(self.src):
            self.code.insert("end", f"P{i+1}: {p}\n")

        self.code.insert("end", "\n# === DST (Hedef Noktalar) ===\n")
        for i, p in enumerate(self.dst):
            self.code.insert("end", f"D{i+1}: {p}\n")

        self.code.insert("end", "\n# === A MATRİSİ ===\n")
        for row in self.A:
            self.code.insert("end", f"{row.tolist()}\n")

        self.code.insert("end", "\n# === B VEKTÖRÜ ===\n")
        for v in self.B:
            self.code.insert("end", f"{v}\n")

        self.code.insert("end", "\n# === ÇÖZÜM (PERSPEKTİF KATSAYILARI) ===\n")
        for i, c in enumerate(self.coeffs):
            self.code.insert("end", f"h{i}: {c}\n")

        self.code.insert("end", """
# Dönüşüm:
img.transform(
    (300, 300),
    Image.PERSPECTIVE,
    coeffs,
    Image.BICUBIC
)
def find_perspective_coeffs_debug(dst, src):
    matrix = []
    for (x2, y2), (x1, y1) in zip(dst, src):
        matrix.append([x2, y2, 1, 0, 0, 0, -x1*x2, -x1*y2])
        matrix.append([0, 0, 0, x2, y2, 1, -y1*x2, -y1*y2])

    A = np.array(matrix, dtype=float)
    B = np.array(src, dtype=float).reshape(8)

    coeffs = np.linalg.solve(A, B)
    return coeffs.tolist(), A, B


""")

# ======================================================
# MATEMATİK (DEBUG'LU)
# ======================================================
def find_perspective_coeffs_debug(dst, src):
    matrix = []
    for (x2, y2), (x1, y1) in zip(dst, src):
        matrix.append([x2, y2, 1, 0, 0, 0, -x1*x2, -x1*y2])
        matrix.append([0, 0, 0, x2, y2, 1, -y1*x2, -y1*y2])

    A = np.array(matrix, dtype=float)
    B = np.array(src, dtype=float).reshape(8)

    coeffs = np.linalg.solve(A, B)
    return coeffs.tolist(), A, B


# ======================================================
# DIŞARDAN ÇAĞRILAN
# ======================================================
def goster_perspektif(img_pil):
    pencere = tk.Toplevel()
    PerspektifUygulama(pencere, img_pil)
