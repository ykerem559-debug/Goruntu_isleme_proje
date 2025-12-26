# -*- coding: utf-8 -*-
# coklu/kolere.py

import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import threading
import inspect


# =====================================================
# ROI TABANLI KORELASYON (AKADEMİK – cv2 YOK)
# =====================================================
class KolereUygulama:
    def __init__(self, root, img_pil):
        self.root = root
        self.root.title("ROI Tabanlı Korelasyon (Akademik)")
        self.root.resizable(False, False)

        # -------------------------------------------------
        # GÖRÜNTÜLER ve DURUM
        # -------------------------------------------------
        self.img_color = img_pil.copy()          # solda RENKLİ
        self.img_gray  = img_pil.convert("L")   # hesaplama için
        self.I = np.array(self.img_gray, dtype=float)

        # ROI
        self.start = None
        self.rect = None
        self.roi = None
        self.roi_coords = None

        # -------------------------------------------------
        # ANA YERLEŞİM
        # -------------------------------------------------
        ana = tk.Frame(root)
        ana.pack(padx=10, pady=10)
        
        # --- Sol ve Orta Frame (3 Sütunlu Yapı) ---
        frame_sol_orta = tk.Frame(ana)
        frame_sol_orta.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        # ---------------- SOL (ROI) ----------------
        sol = tk.LabelFrame(frame_sol_orta, text="Orijinal (ROI Seç)", width=330, height=330)
        sol.pack(side="left", padx=5)
        sol.pack_propagate(False)

        self.canvas = tk.Canvas(sol, width=300, height=300, bg="#ddd")
        self.canvas.pack(padx=5, pady=5)

        self.canvas.bind("<ButtonPress-1>", self.roi_basla)
        self.canvas.bind("<B1-Motion>", self.roi_ciz)
        self.canvas.bind("<ButtonRelease-1>", self.roi_bitir)

        # ---------------- ORTA (Kod) ----------------
        orta = tk.LabelFrame(frame_sol_orta, text="İşlem Kodu", width=330, height=330)
        orta.pack(side="left", padx=5)
        orta.pack_propagate(False)

        self.code_text = tk.Text(orta, width=40, font=("Consolas", 9))
        self.code_text.pack(fill="both", expand=True)

        # ---------------- SAĞ (Sonuç) ----------------
        sag = tk.LabelFrame(ana, text="Korelasyon Sonucu", width=330, height=330)
        sag.grid(row=0, column=2, padx=5)
        sag.pack_propagate(False)

        self.out = tk.Canvas(sag, width=300, height=300, bg="#ddd")
        self.out.pack(padx=5, pady=5)

        # yükleniyor yazısı
        self.loading_text = self.out.create_text(
            150, 150,
            text="Hesaplanıyor...",
            fill="gray",
            font=("Arial", 14),
            state="hidden"
        )

        # ---------------- ALT (Butonlar) ----------------
        alt = tk.Frame(ana)
        alt.grid(row=1, column=0, columnspan=3, pady=10)

        tk.Button(alt, text="Ortalama", width=12,
                  command=lambda: self.islem_baslat(self.ortalama_harita, "Ortalama")).pack(side="left", padx=3)

        tk.Button(alt, text="Varyans", width=12,
                  command=lambda: self.islem_baslat(self.varyans_harita, "Varyans")).pack(side="left", padx=3)

        tk.Button(alt, text="Çapraz Kolerasyon", width=15,
                  command=lambda: self.islem_baslat(self.cc_async, "Çapraz Kolerasyon")).pack(side="left", padx=3)

        tk.Button(alt, text="Korelasyon", width=12,
                  command=lambda: self.islem_baslat(self.korelasyon_async, "Korelasyon")).pack(side="left", padx=3)

        tk.Button(alt, text="Konvolüsyon", width=12,
                  command=lambda: self.islem_baslat(self.konvolusyon, "Konvolüsyon")).pack(side="left", padx=3)

        tk.Button(alt, text="Sıfırla", width=12,
                  command=self.reset).pack(side="left", padx=3)


        self.goster_sol()
        self.kod_yaz_baslangic()

    # ==================================================
    # KOD GÖSTERİMİ VE İŞLEM BAŞLATMA
    # ==================================================
    def kod_yaz_baslangic(self):
        self.code_text.delete("1.0", "end")
        self.code_text.insert("end",
            "# KOD PANELİ\n"
            "# Soldan bir ROI (Alan) seçin,\n"
            "# ardından aşağıdaki işlemlerden birine basın.\n"
        )

    def kod_yaz(self, func):
        try:
            # Asenkron wrapper ise, asıl iş yapan metodu bul.
            func_to_inspect = func
            if func.__name__.endswith("_async"):
                hesapla_adi = func.__name__.replace("_async", "_hesapla")
                if hasattr(self, hesapla_adi):
                    func_to_inspect = getattr(self, hesapla_adi)
                
            kod = inspect.getsource(func_to_inspect)
            self.code_text.delete("1.0", "end")
            self.code_text.insert("end", f"--- {func_to_inspect.__name__.upper()} KODU ---\n\n{kod}")
        except Exception as e:
            self.code_text.delete("1.0", "end")
            self.code_text.insert("end", f"--- KOD OKUMA HATASI ---\n{e}")

    def islem_baslat(self, func, isim):
        # Kod gösterme artık asıl hesaplama fonksiyonunu bulacaktır.
        self.kod_yaz(func) 
        
        if self.roi is None:
            tk.messagebox.showwarning("Hata", f"'{isim}' işlemini başlatmak için önce bir ROI (Alan) seçin.")
            return

        func()

    # ==================================================
    # GÖSTERİM (NORMALİZASYON BURADA YAPILDI)
    # ==================================================
    def goster_sol(self):
        im = self.img_color.resize((300, 300))
        self.tkimg = ImageTk.PhotoImage(im)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tkimg)
        if self.roi_coords:
             self.rect = self.canvas.create_rectangle(
                *self.roi_coords, outline="red", width=2
            )
        

# kolere.py (goster_sag metodu)

# kolere.py (goster_sag metodu)

# kolere.py (goster_sag metodu)

# kolere.py (goster_sag metodu)

    def goster_sag(self, mat):
        """
        Matrisi normalleştirir ve Logaritmik + Güç Fonksiyonu ile küçük farkları vurgular.
        """
        
        # 1. Mutlak Değer Al ve Normalize Et (Değerler [-1, 1] aralığında olduğundan)
        # Mutlak değer alırsak, zıt korelasyonlar da vurgulanır.
        # Ancak Korelasyon (ZNCC) haritası genellikle -1'den +1'e normalize edilmiş haldedir.
        # Sadece pozitif korelasyonu (eşleşmeyi) vurgulamak için mat'ı kullanmaya devam edelim.
        
        min_val = mat.min()
        max_val = mat.max()
        
        if (max_val - min_val) < 1e-8: # ÇOK küçük bir fark varsa
             mat_norm = np.full(mat.shape, 0.7) 
        else:
            # Min-Max Normalizasyonu: N = [0, 1]
            mat_norm = (mat - min_val) / (max_val - min_val)
        
        # -----------------------------------------------------
        # 🔴 GÜÇLENDİRİLMİŞ LOGARİTMİK VURGULAMA
        # -----------------------------------------------------
        
        # Korelasyon haritasının doğası gereği yüksek kontrast gereklidir.
        
        # Adım 1: Logaritmik Sıkıştırma (Düşük sinyalleri korumak için)
        # c * log(1 + N)
        c_log = 1.0 / np.log(1 + 1.0) 
        mat_log = c_log * np.log(1 + mat_norm)

        # Adım 2: Güçlü Vurgulama (Yüksek katsayıları beyaza çekmek için)
        # Logaritmik çıktı da [0, 1] aralığındadır. Üstel fonksiyon uygulayalım.
        
        # Eğer sonuç hala karanlıksa, power_factor > 1 olmalıdır.
        # Ancak önce 1.0 deneyelim (sadece Logaritmik)
        
        power_factor = 1.0 
        mat_final = np.power(mat_log, power_factor)
        
        # Eğer karanlık çıkarsa, 2.0 veya 3.0 deneyebiliriz.
        
        # -----------------------------------------------------
        
        # 2. Görselleştirme için 0-255 aralığına çevirme
        img_array = (mat_final * 255).astype(np.uint8) 
        
        img = Image.fromarray(img_array)
        img = img.resize((300, 300))
        self.tkout = ImageTk.PhotoImage(img)

        self.out.delete("all")
        self.out.create_image(0, 0, anchor="nw", image=self.tkout)    # ROI SEÇİMİ (Aynı kaldı)
    # ==================================================
    def roi_basla(self, e):
        self.start = (e.x, e.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            e.x, e.y, e.x, e.y,
            outline="red", width=2
        )
        self.roi = None

    def roi_ciz(self, e):
        if not self.start:
            return
        x0, y0 = self.start
        self.canvas.coords(self.rect, x0, y0, e.x, e.y)

    def roi_bitir(self, e):
        if not self.start:
            return

        x0, y0 = self.start
        x1, y1 = e.x, e.y
        self.start = None

        w, h = self.img_gray.size
        sx, sy = w / 300, h / 300

        y_min = int(min(y0, y1) * sy)
        y_max = int(max(y0, y1) * sy)
        x_min = int(min(x0, x1) * sx)
        x_max = int(max(x0, x1) * sx)

        if (y_max - y_min) < 2 or (x_max - x_min) < 2:
            self.roi = None
            self.roi_coords = None
            tk.messagebox.showwarning("ROI Hatası", "Lütfen en az 2x2 boyutunda bir alan seçin.")
            self.canvas.delete(self.rect)
            self.rect = None
            return

        self.roi = self.I[
            y_min:y_max,
            x_min:x_max
        ]
        self.roi_coords = (x0, y0, x1, y1)

        print(f"ROI seçimi tamamlandı. Boyut: {self.roi.shape}. Lütfen bir işlem butonu seçin.")


    # ==================================================
    # İŞLEMLER (Aynı kaldı)
    # ==================================================
    def ortalama_harita(self):
        T = self.roi
        h, w = T.shape
        H, W = self.I.shape
        out = np.zeros((H - h + 1, W - w + 1))
        for y in range(H - h + 1):
            for x in range(W - w + 1):
                P = self.I[y:y+h, x:x+w]
                out[y, x] = P.mean()
        self.goster_sag(out)
        
    def cc_async(self):
        self.out.itemconfig(self.loading_text, state="normal")
        def worker():
            try:
                T = self.roi
                h, w = T.shape
                H, W = self.I.shape
                out = np.zeros((H - h + 1, W - w + 1))
                for y in range(H - h + 1):
                    for x in range(W - w + 1):
                        P = self.I[y:y+h, x:x+w]
                        out[y, x] = np.sum(P * T)
                self.root.after(0, lambda: self.korelasyon_bitti(out))
            except Exception as e:
                print(f"Çapraz Korelasyon sırasında hata oluştu: {e}")
                self.root.after(0, self.hata)
        threading.Thread(target=worker, daemon=True).start()
           
        
    def varyans_harita(self):
        T = self.roi
        h, w = T.shape
        H, W = self.I.shape
        out = np.zeros((H - h + 1, W - w + 1))
        for y in range(H - h + 1):
            for x in range(W - w + 1):
                P = self.I[y:y+h, x:x+w]
                out[y, x] = P.var()
        self.goster_sag(out)
        
    def konvolusyon(self):
        kernel = np.ones((3, 3)) / 9
        I = self.I
        H, W = I.shape
        out = np.zeros_like(I)
        for y in range(1, H-1):
            for x in range(1, W-1):
                region = I[y-1:y+2, x-1:x+2]
                out[y, x] = np.sum(region * kernel)
        self.goster_sag(out)

    def korelasyon_async(self):
        self.out.itemconfig(self.loading_text, state="normal")
        def worker():
            try:
                sonuc = self.korelasyon_hesapla()
                self.root.after(0, lambda: self.korelasyon_bitti(sonuc))
            except Exception as e:
                print(f"Korelasyon sırasında hata oluştu: {e}")
                self.root.after(0, self.hata)
        threading.Thread(target=worker, daemon=True).start()

    def korelasyon_hesapla(self):
        T = self.roi
        I = self.I
        Tn = T - T.mean()
        Ts = T.std() + 1e-6
        h, w = T.shape
        H, W = I.shape
        out = np.zeros((H - h + 1, W - w + 1))
        step = 2
        for y in range(0, H - h + 1, step):
            for x in range(0, W - w + 1, step):
                P = I[y:y+h, x:x+w]
                Pn = P - P.mean()
                P_std = P.std()
                if P_std * Ts < 1e-6:
                     out[y, x] = 0
                else:
                     out[y, x] = np.sum(Pn * Tn) / (P_std * Ts)
        return out

    # ==================================================
    def korelasyon_bitti(self, mat):
        self.out.itemconfig(self.loading_text, state="hidden")
        self.goster_sag(mat)

    def hata(self):
        self.out.itemconfig(self.loading_text, state="hidden")
        self.out.delete("all")
        self.out.create_text(150, 150, text="Hata", fill="red")

    # ==================================================
    def reset(self):
        self.roi = None
        self.roi_coords = None
        self.out.delete("all")
        self.goster_sol()
        self.kod_yaz_baslangic()


# =====================================================
# ANA PROJE İÇİN GİRİŞ NOKTASI
# =====================================================
def goster_kolere(img_pil):
    pencere = tk.Toplevel()
    KolereUygulama(pencere, img_pil)