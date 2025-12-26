from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import messagebox
import inspect
# Matplotlib importları (Eğer Matplotlib kullanıyorsanız)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

# ====================== KOD PANELİ ======================

kod_text = None

def kod_paneli_olustur(parent, width, height):
    """Kod görüntüleme paneli"""
    global kod_text
    frame = tk.LabelFrame(parent, text="İşlem Kodu", width=width, height=height, bg="white")
    frame.pack(side="left", padx=5, pady=10)
    frame.pack_propagate(False)

    kod_text = tk.Text(frame, bg="white", fg="black", font=("Consolas", 9))
    kod_text.pack(fill="both", expand=True)

    return kod_text


def kod_yaz(metin):
    """Kod paneline yaz"""
    if kod_text is None:
        return
    kod_text.delete("1.0", "end")
    kod_text.insert("1.0", metin)

def get_cvsiz_source(fonksiyon_adi):
    """Verilen fonksiyon adının islemler modülündeki kaynak kodunu döner."""
    try:
        modul = __import__('islemler')
        fonksiyon = getattr(modul, fonksiyon_adi)
        kod = inspect.getsource(fonksiyon)
        return f"--- {fonksiyon_adi.upper()} KODU (Python Döngüleri) ---\n\n{kod}"
    except Exception as e:
        return f"--- KOD OKUMA HATASI ({fonksiyon_adi}) ---\nKaynak kod okunamadı (islemler.py'yi kontrol edin): {e}"


# ====================== ANA ÇERÇEVELER ======================

def cerceveleri_olustur(pencere):

    # --- ANA CANVAS + HORIZONTAL SCROLL ---
    canvas = tk.Canvas(pencere, bg="white")
    canvas.pack(fill="both", expand=True)

    # İçerik çerçevesi
    ana = tk.Frame(canvas, bg="white")
    canvas.create_window((0, 0), window=ana, anchor="nw")

    # Scroll bölgesini güncelle
    def update_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    ana.bind("<Configure>", update_scroll)

    # --- PANEL GENİŞLİK / YÜKSEKLİK ---
    G_BOYUT = 320    # Genişlik
    LOG_G_BOYUT = 250
    Y_BOYUT = 400    # Yükseklik

    # --- SOL – Orijinal Resim ---
    sol_cerceve = tk.LabelFrame(ana, text="Orijinal Resim",
                                 width=G_BOYUT, height=Y_BOYUT,
                                 bg="white")
    sol_cerceve.pack(side="left", padx=5, pady=10)
    sol_cerceve.pack_propagate(False)

    sol_label = tk.Label(sol_cerceve, bg="#eeeeee") 
    sol_label.pack(fill="both", expand=True)

    # --- ORTA – Log Alanı ---
    orta_cerceve = tk.LabelFrame(ana, text="İşlem Gidişatı",
                                  width=LOG_G_BOYUT, height=Y_BOYUT,
                                  bg="white")
    orta_cerceve.pack(side="left", padx=5, pady=10)
    orta_cerceve.pack_propagate(False)

    log_alani = tk.Text(orta_cerceve, width=30)
    log_alani.pack(fill="both", expand=True)
    log_alani.config(state=tk.DISABLED) # Başlangıçta log alanı Disabled
    
    # --- KOD PANELİ ---
    kod_paneli_olustur(ana, LOG_G_BOYUT, Y_BOYUT)

    # --- SAĞ – İşlenmiş Resim ---
    sag_cerceve = tk.LabelFrame(ana, text="İşlenmiş Resim",
                                 width=G_BOYUT, height=Y_BOYUT,
                                 bg="white")
    sag_cerceve.pack(side="left", padx=5, pady=10)
    sag_cerceve.pack_propagate(False)

    sag_label = tk.Label(sag_cerceve, bg="#eeeeee")
    sag_label.pack(fill="both", expand=True)

    # --- HISTOGRAM ---
    hist_cerceve = tk.LabelFrame(ana, text="Histogram",
                                  width=G_BOYUT, height=Y_BOYUT,
                                  bg="white")
    hist_cerceve.pack(side="left", padx=5, pady=10)
    hist_cerceve.pack_propagate(False)

    hist_canvas = tk.Canvas(hist_cerceve, bg="white")
    hist_canvas.pack(fill="both", expand=True)

    return {
        "sol": sol_label,
        "log": log_alani,
        "kod": kod_text,
        "sag": sag_label,
        "hist": hist_canvas,
        "canvas": canvas
    }


# ======================= MENÜ ÇUBUĞU + DÖKÜMAN FONKS =======================

current_image = None
orjinal_image = None
current_photo = None 

# Görüntü İşleme Parametreleri
parlaklik_beta = 0   
kontrast_alpha = 1.0 
otele_dx = 0     
otele_dy = 0     
dondur_aci = 0     
boyut_oran = 1.0    


def yeni_sayfa(cerceveler):
    global current_image, orjinal_image, parlaklik_beta, kontrast_alpha, otele_dx, otele_dy, dondur_aci, boyut_oran
    current_image = None
    orjinal_image = None
    parlaklik_beta = 0   
    kontrast_alpha = 1.0 
    otele_dx = 0     
    otele_dy = 0     
    dondur_aci = 0     
    boyut_oran = 1.0    

    bos_resim = ImageTk.PhotoImage(Image.new('RGB', (1, 1), color='#eeeeee'))

    cerceveler["sol"].config(image=bos_resim, bg="#eeeeee")
    cerceveler["sol"].image = bos_resim

    cerceveler["sag"].config(image=bos_resim, bg="#eeeeee")
    cerceveler["sag"].image = bos_resim

    cerceveler["hist"].delete("all")

    log_alani = cerceveler["log"]
    log_alani.config(state=tk.NORMAL)
    log_alani.delete('1.0', tk.END)
    log_alani.config(state=tk.DISABLED)
    
    kod_yaz("")
    
    if "alt" in cerceveler:
        for widget in cerceveler["alt"].winfo_children():
            widget.destroy()


def dosya_ac(cerceveler):
    global current_image, orjinal_image, parlaklik_beta, kontrast_alpha, otele_dx, otele_dy, dondur_aci, boyut_oran

    yol = filedialog.askopenfilename(
        filetypes=[("Resim Dosyası", "*.png;*.jpg;*.jpeg;*.bmp")]
    )
    if not yol:
        return

    img = Image.open(yol)
    current_image = img
    orjinal_image = img.copy()
    parlaklik_beta = 0   
    kontrast_alpha = 1.0 
    otele_dx = 0     
    otele_dy = 0     
    dondur_aci = 0     
    boyut_oran = 1.0    

    goster_sol(img, cerceveler)
    goster_sag(img, cerceveler)
    ciz_histogram(img, cerceveler)
    log_yaz(cerceveler, f"Dosya açıldı: {yol}")


def resetle(cerceveler):
    global current_image, orjinal_image, parlaklik_beta, kontrast_alpha, otele_dx, otele_dy, dondur_aci, boyut_oran
    if orjinal_image is None:
        return

    current_image = orjinal_image.copy()
    parlaklik_beta = 0   
    kontrast_alpha = 1.0 
    otele_dx = 0     
    otele_dy = 0     
    dondur_aci = 0     
    boyut_oran = 1.0    
    
    goster_sol(current_image, cerceveler)
    goster_sag(current_image, cerceveler)
    ciz_histogram(current_image, cerceveler)
    
    kod_yaz("") # Kodu temizle
    log_alani = cerceveler["log"]
    log_alani.config(state=tk.NORMAL)
    log_alani.delete('1.0', tk.END)
    log_alani.config(state=tk.DISABLED)
    
    log_yaz(cerceveler, "Resim varsayılan haline döndürüldü.")
    
    if "alt" in cerceveler:
        for widget in cerceveler["alt"].winfo_children():
            widget.destroy()


def log_yaz(cerceveler, yazi):
    try:
        cerceveler["log"].config(state=tk.NORMAL)
        cerceveler["log"].insert("end", yazi + "\n")
        cerceveler["log"].see("end")
        cerceveler["log"].config(state=tk.DISABLED)
    except:
        pass


# ======================= İŞLEM YAP (Tüm işlemler için genel fonksiyon) =======================

def islem_yap(fonksiyon, cerceveler):
    """
    Verilen fonksiyonu mevcut görüntüye uygular ve sonucu arayüzde gösterir.
    Log mesajı, fonksiyona atanmış özel 'description' özelliğinden alınır.
    """
    global current_image

    if current_image is None:
        messagebox.showwarning("Hata", "Önce bir görüntü açmalısınız.")
        return

    try:
        sonuc_image = fonksiyon(current_image)
        current_image = sonuc_image
        
        gui_sonuc_goster(sonuc_image, cerceveler)
        
        aciklama = getattr(fonksiyon, 'description', f"Bilinmeyen İşlem ({fonksiyon.__name__})")
        log_yaz(cerceveler, f"CV2: {aciklama}")

    except Exception as e:
        messagebox.showerror("İşlem Hatası", f"Görüntü işlenirken hata oluştu: {e}")
        log_yaz(cerceveler, f"HATA: {e}")


# ======================= AYAR PANELİ MANTIĞI =======================

def ayarlar_panelini_olustur(cerceveler, baslik, islem_adi, kaynak="CVLI"):
    """Sağdaki ayar panelini temizler ve kontrol düğmelerini ekler."""
    global parlaklik_beta, kontrast_alpha, otele_dx, otele_dy, dondur_aci, boyut_oran
    
    panel = cerceveler["alt"]
    for widget in panel.winfo_children():
        widget.destroy()

    panel.config(text=baslik)
    
    if islem_adi in ["parlaklik", "kontrast", "dondurme"]:
        
        if islem_adi == "parlaklik":
            current_val, miktar, baslik_yazi = parlaklik_beta, 10, "Parlaklık"
        elif islem_adi == "kontrast":
            current_val, miktar, baslik_yazi = kontrast_alpha, 0.2, "Kontrast"
        elif islem_adi == "dondurme":
            current_val, miktar, baslik_yazi = dondur_aci, 10, "Açı Döndürme"

        etiket_text = f"{baslik_yazi}: {current_val}"
        etiket = tk.Label(panel, text=etiket_text, bg="#eeeeee")
        etiket.pack(pady=5)
        
        buton_frame = tk.Frame(panel, bg="#eeeeee")
        buton_frame.pack(pady=5)

        btn_azalt = tk.Button(
            buton_frame, text=" - ", 
            command=lambda: ayar_guncelle(cerceveler, islem_adi, -miktar, etiket, kaynak)
        )
        btn_azalt.pack(side="left", padx=5)

        btn_yukselt = tk.Button(
            buton_frame, text=" + ", 
            command=lambda: ayar_guncelle(cerceveler, islem_adi, miktar, etiket, kaynak)
        )
        btn_yukselt.pack(side="left", padx=5)

    elif islem_adi == "oteleme":
        
        miktar = 10 
        
        etiket_xy = tk.Label(panel, text=f"X: {otele_dx}, Y: {otele_dy}", bg="#eeeeee")
        etiket_xy.pack(side="top", pady=(5, 10))

        frame_butonlar = tk.Frame(panel, bg="#eeeeee")
        frame_butonlar.pack(pady=5, padx=5)

        tk.Label(frame_butonlar, text="Yön:", bg="#eeeeee").pack(side="left", padx=10)

        tk.Button(frame_butonlar, text="←", command=lambda: ayar_guncelle(cerceveler, "oteleme_x", -miktar, etiket_xy, kaynak)).pack(side="left", padx=2)
        tk.Button(frame_butonlar, text="→", command=lambda: ayar_guncelle(cerceveler, "oteleme_x", miktar, etiket_xy, kaynak)).pack(side="left", padx=2)
        tk.Button(frame_butonlar, text="↑", command=lambda: ayar_guncelle(cerceveler, "oteleme_y", -miktar, etiket_xy, kaynak)).pack(side="left", padx=2)
        tk.Button(frame_butonlar, text="↓", command=lambda: ayar_guncelle(cerceveler, "oteleme_y", miktar, etiket_xy, kaynak)).pack(side="left", padx=2)

    elif islem_adi == "boyutlandirma":
        
        w, h = orjinal_image.size if orjinal_image else (0, 0)
        
        frame_w = tk.Frame(panel, bg="#eeeeee"); frame_w.pack(pady=(10, 5), fill="x")
        tk.Label(frame_w, text="Genişlik (W):", bg="#eeeeee").pack(side="left", padx=5)
        entry_w = tk.Entry(frame_w, width=8); entry_w.insert(0, str(w)); entry_w.pack(side="right", padx=5) 

        frame_h = tk.Frame(panel, bg="#eeeeee"); frame_h.pack(pady=(5, 10), fill="x")
        tk.Label(frame_h, text="Yükseklik (H):", bg="#eeeeee").pack(side="left", padx=5)
        entry_h = tk.Entry(frame_h, width=8); entry_h.insert(0, str(h)); entry_h.pack(side="right", padx=5) 

        tk.Button(
            panel, 
            text="✓ Onayla", 
            font=('Arial', 10, 'bold'),
            bg='#d4edda', 
            fg='#155724', 
            command=lambda: ayar_guncelle_boyut(
                cerceveler, entry_w.get(), entry_h.get(), kaynak
            )
        ).pack(pady=10)

def ayar_guncelle(cerceveler, islem_adi, miktar, etiket, kaynak="CVLI"):
    """Parametre değerini günceller, işlemi uygular ve kodu yazar."""
    
    global parlaklik_beta, kontrast_alpha, otele_dx, otele_dy, dondur_aci, current_image, orjinal_image
    
    if current_image is None:
        messagebox.showwarning("Hata", "Önce bir görüntü açmalısınız.")
        return
        
    yeni_deger = None 
    fonksiyon_adi = None
    modul_adlari = ['islemler'] if kaynak == "CVSİZ" else ['cvislem', 'cvli.cvislem']
    base_kod = f"\n# Kaynak: {kaynak} İşlemi\n\n"
    
    try:
        # 1. Değer Hesaplama ve Fonksiyon Atama
        if islem_adi == "parlaklik":
            parlaklik_beta = int(max(-255, min(255, parlaklik_beta + miktar)))
            yeni_deger = parlaklik_beta
            fonksiyon_adi = "cv_parlaklik" if kaynak == "CVLI" else "parlaklik_ayarla"
            parametre = {'beta': yeni_deger} if kaynak == "CVLI" else {'deger': yeni_deger}
            log_aciklama = f"Parlaklık {yeni_deger} değeriyle uygulandı"
            
        elif islem_adi == "kontrast":
            kontrast_alpha = round(max(0.0, min(3.0, kontrast_alpha + miktar)), 1)
            yeni_deger = kontrast_alpha
            fonksiyon_adi = "cv_kontrast" if kaynak == "CVLI" else "kontrast_ayarla"
            parametre = {'alpha': yeni_deger} if kaynak == "CVLI" else {'faktor': yeni_deger}
            log_aciklama = f"Kontrast {yeni_deger:.2f} katsayısıyla uygulandı"
            
        elif islem_adi == "dondurme":
            dondur_aci = (dondur_aci + miktar) % 360 
            yeni_deger = dondur_aci
            fonksiyon_adi = "cv_dondur" if kaynak == "CVLI" else "aci_degistir"
            parametre = {'aci': yeni_deger} if kaynak == "CVLI" else {'derece': yeni_deger}
            log_aciklama = f"Görüntü {yeni_deger}° döndürüldü"
            
        elif islem_adi in ["oteleme_x", "oteleme_y"]: 
            if islem_adi == "oteleme_x": otele_dx += miktar
            elif islem_adi == "oteleme_y": otele_dy += miktar
            yeni_deger = f"X:{otele_dx}, Y:{otele_dy}" 
            
            fonksiyon_adi = "cv_otele" if kaynak == "CVLI" else "ote"
            parametre = {'dx': otele_dx, 'dy': otele_dy}
            log_aciklama = f"Öteleme ayarlandı: X={otele_dx}, Y={otele_dy}"
        
        else:
            return

        # 2. İşlemi Çalıştırma (Dinamik import ile)
        islem_fonk = None
        for modul_ad in modul_adlari:
            try:
                if modul_ad == 'islemler': modul = __import__(modul_ad)
                else: modul = __import__(modul_ad, fromlist=[fonksiyon_adi])

                islem_fonk = getattr(modul, fonksiyon_adi)
                break
            except Exception:
                continue

        if islem_fonk is None:
            messagebox.showerror("Modül Hatası", f"Gerekli '{fonksiyon_adi}' modülü bulunamadı.")
            return

        sonuc = islem_fonk(orjinal_image.copy(), **parametre)

        # 3. Sonucu Gösterme ve Loglama
        current_image = sonuc
        gui_sonuc_goster(sonuc, cerceveler) 
        
        if kaynak == "CVLI":
            kod_satirlari = [
                "# Kullanılan Fonksiyon:",
                f"result = {fonksiyon_adi}(orjinal_image, **{parametre})"
            ]
            kod_yaz(f"--- {fonksiyon_adi.upper()} KODU (AYARLI CVLİ) ---{base_kod}\n" + "\n".join(kod_satirlari))
        elif kaynak == "CVSİZ":
            kaynak_kod_tamami = get_cvsiz_source(fonksiyon_adi)
            kod_yaz(kaynak_kod_tamami)
            
        etiket.config(text=f"{etiket.cget('text').split(':')[0]}: {yeni_deger}")
        log_yaz(cerceveler, f"{log_aciklama} ({kaynak})")
        
    except Exception as e:
        messagebox.showerror("İşlem Hatası", f"Ayar uygulanırken hata oluştu: {e}")
        log_yaz(cerceveler, f"HATA: {e}")


def ayar_guncelle_boyut(cerceveler, w_str, h_str, kaynak):
    """Manuel girilen genişlik ve yükseklik değerlerini işler ve yeniden boyutlandırmayı uygular."""
    global boyut_oran, orjinal_image, current_image

    if orjinal_image is None:
        messagebox.showwarning("Hata", "Önce bir görüntü açmalısınız.")
        return

    try:
        hedef_w = max(1, int(w_str))
        hedef_h = max(1, int(h_str))
        orj_w, orj_h = orjinal_image.size
        yeni_oran = round(hedef_w / orj_w, 2) if orj_w > 0 else 1.0
        
        boyut_oran = yeni_oran

        fonksiyon_adi = "cv_boyutlandir" if kaynak == "CVLI" else "yeniden_boyutlandir"
        parametre = {'boyut': (hedef_w, hedef_h)}

        islem_fonk = None
        modul_adlari = ['islemler'] if kaynak == "CVSİZ" else ['cvislem', 'cvli.cvislem']
        
        for modul_ad in modul_adlari:
            try:
                if modul_ad == 'islemler': modul = __import__(modul_ad)
                else: modul = __import__(modul_ad, fromlist=[fonksiyon_adi])

                islem_fonk = getattr(modul, fonksiyon_adi)
                break
            except Exception:
                continue

        if islem_fonk is None:
            messagebox.showerror("Modül Hatası", f"Gerekli '{fonksiyon_adi}' modülü bulunamadı.")
            return

        sonuc = islem_fonk(orjinal_image.copy(), **parametre)

        current_image = sonuc
        gui_sonuc_goster(sonuc, cerceveler) 
        
        kaynak_kod_aciklama = f"yeniden_boyutlandir(img, boyut=({hedef_w}, {hedef_h}))"
        if kaynak == "CVSİZ":
             kaynak_kod_tamami = get_cvsiz_source(fonksiyon_adi)
             kod_yaz(kaynak_kod_tamami + f"\n\n# Çağrı: {kaynak_kod_aciklama}")
        else:
             kod_yaz(f"--- CV_BOYUTLANDIR KODU (AYARLI CVLİ) ---\n# Çağrı: {kaynak_kod_aciklama}")
        
        log_yaz(cerceveler, f"Boyutlandırma ({hedef_w}x{hedef_h}) uygulandı (Oran: {yeni_oran}) ({kaynak})")
        
    except ValueError:
        messagebox.showerror("Hata", "Genişlik ve Yükseklik tam sayı olmalıdır.")
    except Exception as e:
        messagebox.showerror("İşlem Hatası", f"Boyutlandırma uygulanırken hata oluştu: {e}")
        log_yaz(cerceveler, f"HATA: {e}")


# ======================= GÖSTERME FONKSİYONLARI =======================

def resmi_sigdir(img, hedef_label):
    lw = hedef_label.winfo_width()
    lh = hedef_label.winfo_height()

    if lw < 5 or lh < 5:
        return img

    iw, ih = img.size
    oran = min(lw / iw, lh / ih)
    if oran > 1:
        oran = 1
        
    # Anti-aliasing için Image.Resampling.LANCZOS kullan
    yeni = img.resize((int(iw * oran), int(ih * oran)), Image.Resampling.LANCZOS)
    return yeni


def goster_sol(img, cerceveler):
    img2 = resmi_sigdir(img, cerceveler["sol"])
    tkimg = ImageTk.PhotoImage(img2)
    cerceveler["sol"].config(image=tkimg, bg="white")
    cerceveler["sol"].image = tkimg


def goster_sag(img, cerceveler):
    img2 = resmi_sigdir(img, cerceveler["sag"])
    tkimg = ImageTk.PhotoImage(img2)
    cerceveler["sag"].config(image=tkimg, bg="white")
    cerceveler["sag"].image = tkimg


def gui_sonuc_goster(img, cerceveler):
    global current_image
    current_image = img
    goster_sag(img, cerceveler)
    ciz_histogram(img, cerceveler)


# ======================= HISTOGRAM =======================

def ciz_histogram(img, cerceveler):
    try:
        arr = np.array(img.convert("L"))
        hist = np.bincount(arr.flatten(), minlength=256)

        can = cerceveler["hist"]
        can.delete("all")

        can.update_idletasks()
        gen = can.winfo_width()
        yuk = can.winfo_height()

        ust = 15
        alt = 5

        yuk_cizim = yuk - ust - alt
        m = max(hist) if hist.max() > 0 else 1

        ox = gen / 256
        oy = yuk_cizim / m

        zemin = yuk - alt
        can.create_line(0, zemin, gen, zemin, fill="gray")

        for i in range(256):
            x0 = i * ox
            y1 = zemin - hist[i] * oy
            y1 = max(y1, ust)
            can.create_line(x0, zemin, x0, y1, fill="black")

        can.create_text(5, 5, anchor="nw", text="")
    except Exception as e:
        print("Histogram hatası:", e)


# ======================= ÇOKLU GÖSTERİM (Yeni Eklendi) =======================

def show_multiple_images(results, baslik="Tüm Filtre Uygulamaları"):
    """
    Sonuçları (img ve title içeren dict listesi) 4'lü satırlar halinde gösterir.
    Matplotlib penceresi açar.
    """
    if not results:
        return

    num_images = len(results)
    num_rows = (num_images + 3) // 4  # Her satırda max 4 resim
    
    # Figürü aç
    fig, axes = plt.subplots(num_rows, 4, figsize=(16, 4 * num_rows))
    fig.suptitle(baslik, fontsize=16)
    
    # 2D/1D axes array'ini düzleştirme (Tek satırsa 1D, çok satırsa 2D gelir)
    axes_flat = axes.flatten() if num_rows > 1 else axes

    for i in range(num_rows * 4):
        
        # Axes'i al
        ax = axes_flat[i] if num_rows > 1 else axes[i]
        
        if i < num_images:
            res = results[i]
            img_data = res["img"]
            title = res["title"]
            
            # Görüntü moduna göre renk haritasını ayarla
            if img_data.mode == 'L':
                ax.imshow(np.array(img_data), cmap='gray')
            else:
                ax.imshow(np.array(img_data))
                
            ax.set_title(title, fontsize=10)
            ax.axis('off')

        else:
            ax.axis('off') # Boş kalan yerleri gizle

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show() # Yeni bir pencerede göster