import tkinter as tk
from PIL import Image, ImageTk
import sys, os
from tkinter import messagebox
import numpy as np 

# 🔴 EN BAŞA TAŞINDI: Python'a 'cvli' klasörünü ara dememiz gerekiyor.
sys.path.append(os.path.join(os.path.dirname(__file__), 'cvli')) 


from gui_cerceve import dosya_ac, yeni_sayfa, cerceveleri_olustur, resetle
from butonlar import butonlari_bagla
from cvlibutonlar import opencv_paneli_olustur

# 🔴 DÜZELTİLMİŞ IMPORT: cvislem dosyasındaki tüm fonksiyonları esnek olarak import ediyoruz
try:
    from cvislem import (
        cv_gri, cv_negatif, cv_esikleme, cv_logaritmik, cv_kontrast_germe,
        cv_histogram, cv_mean, cv_gaussian, cv_median, cv_laplace,
        cv_sobel_y, cv_sobel_x, cv_prewitt, cv_dondur, cv_ayna,
        cv_ters, cv_otele, cv_boyutlandir,
        cv_parlaklik, cv_kontrast 
    )
except ImportError:
    # Eğer cvislem bulunamazsa, cvli alt klasöründe ara
    from cvli.cvislem import (
        cv_gri, cv_negatif, cv_esikleme, cv_logaritmik, cv_kontrast_germe,
        cv_histogram, cv_mean, cv_gaussian, cv_median, cv_laplace,
        cv_sobel_y, cv_sobel_x, cv_prewitt, cv_dondur, cv_ayna,
        cv_ters, cv_otele, cv_boyutlandir,
        cv_parlaklik, cv_kontrast 
    )

# 🔴 CVSİZ MODÜLLER
import gui_cerceve
# Bu importlar zaten başka bir yerden gelmeli (butonlar.py içinde kullanılıyor),
# Burada sadece çağrılacakları için varlar.
try:
    from cvsiz.perspektif import goster_perspektif
except ImportError:
    goster_perspektif = None
try:
    from cvsiz.kolere import goster_kolere
except ImportError:
    goster_kolere = None


# ======================================================
# ANA PENCERE
# ======================================================
pencere = tk.Tk()
pencere.title("Görüntü İşleme")
pencere.geometry("1520x950+50+0")
pencere.resizable(False, False)


# ======================================================
# YARDIMCI FONKSİYONLAR
# ======================================================
def ayar_panelini_temizle():
    for widget in ayar_paneli.winfo_children():
        widget.destroy()

def buton_sifirla():
    resetle(cerceveler)
    ayar_panelini_temizle()

def menuden_yeni():
    yeni_sayfa(cerceveler)
    ayar_panelini_temizle()


# ======================================================
# AYAR PANELİ AÇMA FONKSİYONLARI (KAYNAK PARAMETRESİ EKLENDİ)
# ======================================================
def parlaklik_ayari_ac(kaynak="CVLI"):
    if gui_cerceve.current_image is None:
        messagebox.showwarning("Hata", "Önce bir görüntü açmalısınız.")
        return
    gui_cerceve.ayarlar_panelini_olustur(
        cerceveler=cerceveler, baslik="Parlaklık Ayarı", islem_adi="parlaklik", kaynak=kaynak
    )

def kontrast_ayari_ac(kaynak="CVLI"):
    if gui_cerceve.current_image is None:
        messagebox.showwarning("Hata", "Önce bir görüntü açmalısınız.")
        return
    gui_cerceve.ayarlar_panelini_olustur(
        cerceveler=cerceveler, baslik="Kontrast Ayarı", islem_adi="kontrast", kaynak=kaynak
    )

def oteleme_ayari_ac(kaynak="CVLI"):
    if gui_cerceve.current_image is None:
        messagebox.showwarning("Hata", "Önce bir görüntü açmalısınız.")
        return
    gui_cerceve.ayarlar_panelini_olustur(
        cerceveler=cerceveler, baslik="Öteleme Ayarı", islem_adi="oteleme", kaynak=kaynak
    )

def dondurme_ayari_ac(kaynak="CVLI"):
    if gui_cerceve.current_image is None:
        messagebox.showwarning("Hata", "Önce bir görüntü açmalısınız.")
        return
    gui_cerceve.ayarlar_panelini_olustur(
        cerceveler=cerceveler, baslik="Açı Döndürme Ayarı", islem_adi="dondurme", kaynak=kaynak
    )

def boyutlandirma_ayari_ac(kaynak="CVLI"):
    if gui_cerceve.current_image is None:
        messagebox.showwarning("Hata", "Önce bir görüntü açmalısınız.")
        return
    gui_cerceve.ayarlar_panelini_olustur(
        cerceveler=cerceveler, baslik="Boyutlandırma Ayarı", islem_adi="boyutlandirma", kaynak=kaynak
    )


# ======================================================
# OPENCV KOD GÖSTERME FONKSİYONU (TEMEL TUŞLAR İÇİN)
# ======================================================

def kod_oku(isim):
    """Verilen isme karşılık gelen temel OpenCV kodunu döndürür."""
    # Not: pil_to_cv ve cv_to_pil dönüşümleri varsayılır. cv2 ve np importları koda eklenmiştir.
    
    if isim == "Gri":
        return "cv = pil_to_cv(img)\ngray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)\n# Sonuç Image.fromarray(gray) ile PIL'e dönüştürülür."
    elif isim == "Negatif":
        return "cv = pil_to_cv(img)\nneg = cv2.bitwise_not(cv)"
    elif isim == "Eşikleme":
        return "cv = pil_to_cv(img)\ngray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)\n_, th = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)"
    elif isim == "Logaritmik":
        return "cv = pil_to_cv(img).astype(np.float32)\nc = 255 / np.log(1 + np.max(cv))\nlog_img = c * np.log(1 + cv)"
    elif isim == "Kontrast Germe":
        return "cv = pil_to_cv(img)\nmin_val, max_val = np.min(cv), np.max(cv)\nstretched = (cv - min_val) * (255 / (max_val - min_val))"
    elif isim == "Histogram Eşitleme":
        return "cv = pil_to_cv(img)\nycrcb = cv2.cvtColor(cv, cv2.COLOR_BGR2YCrCb)\nycrcb[:,:,0] = cv2.equalizeHist(ycrcb[:,:,0])"
    elif isim == "Mean Filter":
        return "cv = pil_to_cv(img)\nblurred = cv2.blur(cv, (5,5))"
    elif isim == "Gaussian Filter":
        return "cv = pil_to_cv(img)\nblurred = cv2.GaussianBlur(cv, (5,5), 0)"
    elif isim == "Median Filter":
        return "cv = pil_to_cv(img)\nblurred = cv2.medianBlur(cv, 5)"
    elif isim == "Laplacian":
        return "cv = pil_to_cv(img)\ngray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)\nlap = cv2.Laplacian(gray, cv2.CV_64F)"
    elif isim == "Sobel Yatay":
        return "cv = pil_to_cv(img)\ngray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)\nsob = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)"
    elif isim == "Sobel Dikey":
        return "cv = pil_to_cv(img)\ngray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)\nsob = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)"
    elif isim == "Prewitt":
        return "cv = pil_to_cv(img)\ngray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)\nkernelx = np.array([[1,0,-1],[1,0,-1],[1,0,-1]])\npre = cv2.filter2D(gray, -1, kernelx)"
    elif isim == "Aynalama":
        return "cv = pil_to_cv(img)\nreflected = cv2.flip(cv, 1)"
    elif isim == "Ters Çevirme":
        return "cv = pil_to_cv(img)\nreflected = cv2.flip(cv, 0)"
    
    return f"--- {isim.upper()} İŞLEMİ ---\nKod bulunamadı."


# ======================================================
# OPENCV BUTONLARINI BAĞLAMA FONKSİYONU
# ======================================================
def opencv_butonlarini_bagla(opencv_butonlar, cerceveler):
    """OpenCV'li butonlara karşılık gelen cvislem fonksiyonlarını atar."""
    
    buton_fonksiyonlari = {
        "Gri": cv_gri, "Negatif": cv_negatif, "Eşikleme": cv_esikleme, 
        "Logaritmik": cv_logaritmik, "Kontrast Germe": cv_kontrast_germe,
        "Histogram Eşitleme": cv_histogram, "Mean Filter": cv_mean, 
        "Gaussian Filter": cv_gaussian, "Median Filter": cv_median, 
        "Laplacian": cv_laplace, "Sobel Yatay": cv_sobel_x, 
        "Sobel Dikey": cv_sobel_y, "Prewitt": cv_prewitt,
        "Aynalama": cv_ayna, "Ters Çevirme": cv_ters,
        
        # Ayar Paneline yönlendirilmesi gerekenler için varsayılan komutlar
        "Açı Döndürme": lambda img: cv_dondur(img, aci=0), 
        "Öteleme": lambda img: cv_otele(img, dx=0, dy=0),
        "Yeniden Boyutlandırma": lambda img: cv_boyutlandir(img, oran=1.0),
    }
    
    # 🔴 KRİTİK DÜZELTME 1: Komut fonksiyonu artık log açıklaması alıyor
    def komut_calistir_ve_kod_yaz(f, c, kod, aciklama):
        """İşlemi yapar ve sonra kodu kod paneline yazar."""
        
        # 🔴 Fonksiyona description atama (Bunu gui_cerceve.islem_yap kullanacak)
        f.description = aciklama 
        
        gui_cerceve.kod_yaz(f"--- {aciklama.upper()} KODU (OpenCV) ---\n\nimport cv2, numpy as np\n\n{kod}")
        gui_cerceve.islem_yap(f, c)


    # ÖZEL AYAR KOMUTLARINI ATA (CV'li)
    if "Parlaklık" in opencv_butonlar: opencv_butonlar["Parlaklık"].config(command=parlaklik_ayari_ac)
    if "Kontrast" in opencv_butonlar: opencv_butonlar["Kontrast"].config(command=kontrast_ayari_ac)
    if "Öteleme" in opencv_butonlar: opencv_butonlar["Öteleme"].config(command=oteleme_ayari_ac)
    if "Açı Döndürme" in opencv_butonlar: opencv_butonlar["Açı Döndürme"].config(command=dondurme_ayari_ac)
    if "Yeniden Boyutlandırma" in opencv_butonlar: opencv_butonlar["Yeniden Boyutlandırma"].config(command=boyutlandirma_ayari_ac)


    # Ana işlemleri bağla (Tek tıklamayla çalışanlar)
    for isim, fonksiyon in buton_fonksiyonlari.items():
        if isim in opencv_butonlar and isim not in ["Parlaklık", "Kontrast", "Öteleme", "Açı Döndürme", "Yeniden Boyutlandırma"]:
            
            opencv_kod = kod_oku(isim)
            
            # 🔴 KRİTİK DÜZELTME 2: LOGA YAZILACAK ÖZEL AÇIKLAMAYI BURADA BELİRLİYORUZ:
            if isim == "Gri":
                log_aciklama = "Gri Tonlama Uygulandı"
            elif isim == "Negatif":
                log_aciklama = "Negatif Görüntüleme Uygulandı"
            elif isim == "Eşikleme":
                log_aciklama = "İkili (Binary) Eşikleme Uygulandı"
            elif isim == "Logaritmik":
                log_aciklama = "Logaritmik Dönüşüm Uygulandı"
            elif isim == "Kontrast Germe":
                log_aciklama = "Kontrast Germe (Streching) Uygulandı"
            elif isim == "Histogram Eşitleme":
                log_aciklama = "Histogram Eşitleme Uygulandı"
            elif isim == "Mean Filter":
                log_aciklama = "Mean (Ortalama) Filtre Uygulandı"
            elif isim == "Gaussian Filter":
                log_aciklama = "Gaussian Filtre Uygulandı"
            elif isim == "Median Filter":
                log_aciklama = "Median Filtre Uygulandı"
            elif isim == "Laplacian":
                log_aciklama = "Laplacian Kenar Algılama Uygulandı"
            elif isim == "Sobel Yatay":
                log_aciklama = "Sobel Yatay Gradyent (Gx) Uygulandı"
            elif isim == "Sobel Dikey":
                log_aciklama = "Sobel Dikey Gradyent (Gy) Uygulandı"
            elif isim == "Prewitt":
                log_aciklama = "Prewitt Kenar Algılama Uygulandı"
            elif isim == "Aynalama":
                log_aciklama = "Aynalama (Yatay Yansıtma) Uygulandı"
            elif isim == "Ters Çevirme":
                log_aciklama = "Ters Çevirme (Dikey Yansıtma) Uygulandı"
            else:
                log_aciklama = f"'{isim}' İşlemi Başarıyla Uygulandı" # Varsayılan fallback
            
            
            opencv_butonlar[isim].config(
                # 🔴 LOG AÇIKLAMASINI KOMUT FONKSİYONUNA GÖNDERİYORUZ
                command=lambda f=fonksiyon, c=cerceveler, k=opencv_kod, ac=log_aciklama: 
                        komut_calistir_ve_kod_yaz(f, c, k, ac)
            )


# ======================================================
# MENÜ 
# ======================================================
menu_cubugu = tk.Menu(pencere)

dosya_menusu = tk.Menu(menu_cubugu, tearoff=0)
dosya_menusu.add_command(label="Yeni", command=menuden_yeni)
dosya_menusu.add_command(label="Aç", command=lambda: dosya_ac(cerceveler))
dosya_menusu.add_separator()
dosya_menusu.add_command(label="Çıkış", command=pencere.quit)
menu_cubugu.add_cascade(label="Dosya", menu=dosya_menusu)

duzen_menusu = tk.Menu(menu_cubugu, tearoff=0)
duzen_menusu.add_command(label="Tam Ekran Yap", command=lambda: pencere.attributes("-fullscreen", True))
duzen_menusu.add_command(label="Normal Ekran Yap", command=lambda: pencere.attributes("-fullscreen", False))
menu_cubugu.add_cascade(label="Düzen", menu=duzen_menusu)

pencere.config(menu=menu_cubugu)


# ======================================================
# YERLEŞİM 
# ======================================================
ust_ana_panel = tk.Frame(pencere, bg="#d9d9d9")
ust_ana_panel.place(relx=0, rely=0, relwidth=1, relheight=0.57)

alt_ana_panel = tk.Frame(pencere, bg="#d9d9d9")
alt_ana_panel.place(relx=0, rely=0.57, relwidth=1, relheight=0.43)

cerceveler = cerceveleri_olustur(ust_ana_panel)

alt_ana_panel.columnconfigure(0, weight=4)
alt_ana_panel.columnconfigure(1, weight=4)
alt_ana_panel.columnconfigure(2, weight=2)
alt_ana_panel.rowconfigure(0, weight=1)


# ======================================================
# SOL PANEL — OPENCV'SİZ
# ======================================================
container_sol = tk.Frame(alt_ana_panel, bg="#d9d9d9")
container_sol.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

frame_cv_siz_ust = tk.LabelFrame(
    container_sol, text="Görüntü İşleme Araçları (OpenCV'siz)",
    font=("Arial", 9, "bold"), bg="#BBCDEE", bd=2
)
frame_cv_siz_ust.pack(side="top", fill="both", expand=True, pady=(0, 2))

# 🔴 DÜZELTME: ANALİZ BUTONLARI VE GÜRÜLTÜ AYRI BİR FRAME'E ALINDI
frame_analiz = tk.LabelFrame(
    container_sol, text="Analiz ve Gürültü İşlemleri (CVSİZ)",
    font=("Arial", 9, "bold"), bg="#C6A7DF", bd=2
)
frame_analiz.pack(side="top", fill="x", pady=(2, 0))


# ======================================================
# ORTA PANEL — OPENCV
# ======================================================
container_orta = tk.Frame(alt_ana_panel, bg="#d9d9d9")
container_orta.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
opencv_butonlar_listesi = opencv_paneli_olustur(container_orta) 


# ======================================================
# SAĞ PANEL — AYAR
# ======================================================
frame_sag = tk.Frame(alt_ana_panel, bg="#d9d9d9")
frame_sag.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)


# ======================================================
# BUTONLAR (OpenCV'siz paneldeki butonlar)
# ======================================================
butonlar = {}

liste_ana = [
    "Gri", "Negatif", "Parlaklık", "Kontrast",
    "Eşikleme", "Logaritmik", "Kontrast Germe", "Histogram Eşitleme",
    "Mean Filter", "Gaussian Filter", "Median Filter", "Laplacian",
    "Sobel Yatay", "Sobel Dikey", "Prewitt", "Açı Döndürme",
    "Aynalama", "Ters Çevirme", "Öteleme", "Yeniden Boyutlandırma"
]

# 🔴 YENİ VE MEVCUT ANALİZ BUTONLARI
liste_analiz = [
    "Yüksek Geçiren", "Gradyent", "Geniş Laplace", "Geniş Prewitt",
    "Tuz Biber Analiz", # 🔴 Yeni Eklendi
]

# --- frame_cv_siz_ust kolon ayarı ---
for i in range(4):
    frame_cv_siz_ust.grid_columnconfigure(i, weight=1)

# --- frame_analiz kolon ayarı ---
for i in range(len(liste_analiz)): # Analiz butonları sayısı kadar
    frame_analiz.grid_columnconfigure(i, weight=1)


# --- ANA BUTONLAR ---
for idx, isim in enumerate(liste_ana):
    r, c = idx // 4, idx % 4
    btn = tk.Button(frame_cv_siz_ust, text=isim, height=2, font=("Arial", 8))
    btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
    butonlar[isim] = btn

# --- MEVCUT ANALİZ BUTONLARI VE YENİ GÜRÜLTÜ BUTONU ---
for idx, isim in enumerate(liste_analiz):
    btn = tk.Button(frame_analiz, text=isim, height=2,
                    font=("Arial", 8, "bold"), bg="#999689")
    btn.grid(row=0, column=idx, padx=2, pady=2, sticky="nsew")
    butonlar[isim] = btn
for idx, isim in enumerate(liste_analiz):
    btn = tk.Button(frame_analiz, text=isim, height=2,
                    font=("Arial", 8, "bold"), bg="#999689")
    btn.grid(row=0, column=idx, padx=2, pady=2, sticky="nsew")
    butonlar[isim] = btn
# --- MORFOLOJİ ---
btn_morfoloji = tk.Button(
    frame_cv_siz_ust, text="Morfoloji",
    height=2, font=("Arial", 9, "bold"), bg="#d0d0d0"
)
btn_morfoloji.grid(row=5, column=0, columnspan=4, padx=2, pady=4, sticky="nsew")
butonlar["Morfoloji"] = btn_morfoloji

# --- PERSPEKTİF ---
btn_perspektif = tk.Button(
    frame_cv_siz_ust, text="Perspektif",
    height=2, font=("Arial", 9, "bold"), bg="#d0d0d0"
)
btn_perspektif.grid(row=6, column=0, columnspan=2, padx=2, pady=4, sticky="nsew")
butonlar["Perspektif"] = btn_perspektif

# --- KORELASYON ---
btn_kolerasyon = tk.Button(
    frame_cv_siz_ust, text="Korelasyon",
    height=2, font=("Arial", 9, "bold"), bg="#d0d0d0"
)
btn_kolerasyon.grid(row=6, column=2, columnspan=2, padx=2, pady=4, sticky="nsew")
butonlar["Korelasyon"] = btn_kolerasyon


# 🔴 YENİ: FULL ANALİZ BUTONU (Tüm alanın altına)
# Bu butonu frame_analiz altına yeni bir satıra ekleyelim
btn_full_analiz = tk.Button(
    frame_analiz, 
    text="FULL ANALİZ (Yan Yana Göster)",
    height=2,
    bg='#a3e7ff', 
    fg='#084298',
    font=('Arial', 10, 'bold')
)
# Tüm kolonları kaplaması için columnspan kullanıyoruz
btn_full_analiz.grid(row=1, column=0, columnspan=len(liste_analiz), padx=2, pady=5, sticky="nsew") 
butonlar["Full Analiz"] = btn_full_analiz # butonlar.py'deki bağlama için kritik


# ======================================================
# SAĞ PANEL (Devamı aynı)
# ======================================================
btn_reset = tk.Button(
    frame_sag, text="⟲ Varsayılan (Sıfırla)",
    bg="#ffcccc", font=("Arial", 10, "bold"), height=2,
    command=buton_sifirla
)
btn_reset.pack(fill="x", padx=5, pady=(2, 5), side="top")

ayar_paneli = tk.LabelFrame(frame_sag, text="Ayar Paneli", bg="#eeeeee", height=150)
ayar_paneli.pack_propagate(False)
ayar_paneli.pack(fill="x", padx=5, pady=0, side="top")

cerceveler["alt"] = ayar_paneli
butonlar["Varsayılan"] = btn_reset


# ======================================================
# BUTON BAĞLAMA (Düzeltilen komut atamaları)
# ======================================================
butonlari_bagla(butonlar, cerceveler)
opencv_butonlarini_bagla(opencv_butonlar_listesi, cerceveler)

# 🔴 CVSİZ AYAR PANELİ BUTON ATAMALARI (kaynak="CVSİZ" parametresi eklendi)
if "Parlaklık" in butonlar: butonlar["Parlaklık"].config(command=lambda: parlaklik_ayari_ac(kaynak="CVSİZ"))
if "Kontrast" in butonlar: butonlar["Kontrast"].config(command=lambda: kontrast_ayari_ac(kaynak="CVSİZ"))
if "Öteleme" in butonlar: butonlar["Öteleme"].config(command=lambda: oteleme_ayari_ac(kaynak="CVSİZ"))
if "Açı Döndürme" in butonlar: butonlar["Açı Döndürme"].config(command=lambda: dondurme_ayari_ac(kaynak="CVSİZ"))
if "Yeniden Boyutlandırma" in butonlar: butonlar["Yeniden Boyutlandırma"].config(command=lambda: boyutlandirma_ayari_ac(kaynak="CVSİZ"))


def perspektif_ac():
    if gui_cerceve.current_image is None:
        messagebox.showwarning("Uyarı", "Lütfen önce bir görüntü açın.")
        return
    if goster_perspektif:
        gui_cerceve.log_yaz(cerceveler, "Perspektif Dönüşüm Penceresi Açıldı (Manuel)")
        goster_perspektif(gui_cerceve.current_image)
    else:
        messagebox.showerror("Hata", "Perspektif modülü bulunamadı (cvsiz/perspektif.py).")

def kolere_ac():
    if gui_cerceve.current_image is None:
        messagebox.showwarning("Uyarı", "Lütfen önce bir görüntü açın.")
        return
    if goster_kolere:
        gui_cerceve.log_yaz(cerceveler, "Korelasyon (Şablon Eşleştirme) Penceresi Açıldı (Manuel)")
        goster_kolere(gui_cerceve.current_image)
    else:
        messagebox.showerror("Hata", "Korelasyon modülü bulunamadı (cvsiz/kolere.py).")

butonlar["Perspektif"].config(command=perspektif_ac)
butonlar["Korelasyon"].config(command=kolere_ac)

# ======================================================
# ÇALIŞTIR
# ======================================================
pencere.mainloop()