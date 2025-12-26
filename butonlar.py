# -*- coding: utf-8 -*-
import tkinter as tk
import threading
import inspect
import gui_cerceve
# DÜZELTME: SyntaxError giderildi, importlar ayrıldı
from islemler import *
from gui_cerceve import log_yaz, resetle, gui_sonuc_goster, ciz_histogram, kod_yaz
import tkinter.messagebox # Hata mesajları için gerekli
try:
    # 🔴 YENİ EKLENDİ
    from cvsiz.tuzbiber import goster_tuzbiber_analiz as goster_tuzbiber 
except:
    goster_tuzbiber = None
# ======================================================
# ANALİZ PENCERELERİ İMPORT KISMI
# ======================================================
try:
    from cvsiz.yuksek_geciren_pencere import goster_yuksek_geciren as goster_yuksek
except:
    goster_yuksek = None

try:
    from cvsiz.gradyent import goster_gradyent as goster_grad
except:
    goster_grad = None

try:
    from cvsiz.genislaplace import goster_laplace_analiz as goster_lap
except:
    goster_lap = None

try:
    from cvsiz.prewitt import goster_prewitt_analiz as goster_pre
except:
    goster_pre = None

try:
    from cvsiz.morfolojipencere import goster_morfoloji
except:
    goster_morfoloji = None


# ======================================================
# KOD GÖSTERME (INSPECT KULLANILARAK)
# ======================================================
def kod_goster(*args):
    txt = ""
    for f in args:
        if f is None:
            continue
        try:
            txt += inspect.getsource(f) + "\n" + "-" * 40 + "\n"
        except:
            pass
    kod_yaz(txt)

# 🔴 KRİTİK DÜZELTME: KOD OKUMA FONKSİYONU (ZİNCİRLEME SÜRÜM)
def kod_oku_cvsiz(fonksiyon):
    """Verilen CVSİZ (islemler.py'den gelen) fonksiyonunun kaynak kodunu döndürür."""
    
    fonk_adi = fonksiyon.__name__ if hasattr(fonksiyon, '__name__') else "Bilinmeyen İşlem"
    asıl_fonksiyon_adı = fonk_adi
    
    try:
        # Wrapper'dan Asıl Fonksiyon Adını Çıkarma
        if fonk_adi == "esikleme_varsayilan":
            asıl_fonksiyon_adı = "esikleme"
        elif fonk_adi == "kontrast_varsayilan":
             asıl_fonksiyon_adı = "kontrast_ayarla"
        elif "sobel_yatay_wrapper" in fonk_adi:
            asıl_fonksiyon_adı = "sobel_yatay"
        elif "sobel_dikey_wrapper" in fonk_adi:
            asıl_fonksiyon_adı = "sobel_dikey"
        elif "prewitt_wrapper" in fonk_adi:
            asıl_fonksiyon_adı = "prewitt"
        elif fonk_adi == "tuzbiber_varsayilan": # 🔴 YENİ EKLENDİ
             asıl_fonksiyon_adı = "tuz_biber_gurultusu_ekle"
        
        # Asıl Fonksiyonun Kaynağını Çekme
        modul = __import__('islemler')
        
        # Konvolüsyon işlemleri için zincir çekme
        if asıl_fonksiyon_adı in ["sobel_yatay", "sobel_dikey", "prewitt", "gaussian_filter", "laplacian", "mean_filter", "median_filter"]:
            
            fonksiyon_ana = getattr(modul, asıl_fonksiyon_adı)
            kod_ana = inspect.getsource(fonksiyon_ana)
            
            # Kernel/Yardımcı Fonksiyonları Zincirleme
            kod_kernel = ""
            if "sobel" in asıl_fonksiyon_adı:
                kod_kernel = inspect.getsource(getattr(modul, f"{asıl_fonksiyon_adı}_kernel_uret"))
            elif "prewitt" in asıl_fonksiyon_adı:
                kod_kernel = inspect.getsource(getattr(modul, "prewitt_kernel_uret"))
            elif "gaussian" in asıl_fonksiyon_adı:
                kod_kernel = inspect.getsource(getattr(modul, "gaussian_kernel_uret"))
            
            # Eğer bir kernel kodu varsa, bunu ana koda ekle
            if kod_kernel:
                kod_ana += f"\n\n--- KERNEL ÜRETİM KODU ---\n\n{kod_kernel}"
            
            # Konvolüsyon İşleyicisini (Filtreler için kritik) ekle
            if asıl_fonksiyon_adı not in ["mean_filter", "median_filter", "laplacian"]: 
                 fonksiyon_konvolusyon = getattr(modul, "konvolusyon_uygula")
                 kod_konvolusyon = inspect.getsource(fonksiyon_konvolusyon)
                 kod_ana += f"\n\n--- KONVOLUSYON_UYGULA KODU (Ana İşleyici) ---\n\n{kod_konvolusyon}"

            return f"--- {asıl_fonksiyon_adı.upper()} KODU ---\n\n{kod_ana}"
        
        # Diğer Tek Başına Çalışanlar (Gri, Negatif, Eşikleme vb.)
        fonksiyon_asıl = getattr(modul, asıl_fonksiyon_adı)
        kod = inspect.getsource(fonksiyon_asıl)
        return f"--- {asıl_fonksiyon_adı.upper()} KODU (Python Döngüleri) ---\n\n{kod}"
        
    except Exception as e:
        return f"--- KOD OKUMA HATASI ({asıl_fonksiyon_adı}) ---\nKaynak kod okunamadı: {e}\n(Lütfen 'islemler.py' dosyasında {asıl_fonksiyon_adı} ve yardımcı fonksiyonlarının varlığını kontrol edin.)"


# ======================================================
# KRİTİK WRAPPER FONKSİYONLARI (TÜM PROBLEMLİLER İÇİN)
# ======================================================

def esikleme_varsayilan(img):
    """Eşikleme işlemini sabit 128 değeriyle uygular."""
    from islemler import esikleme
    return esikleme(img, esik=128)

def esikleme_wrapper_and_apply():
    """Eşikleme işlemini uygula_thread ile başlatır."""
    uygula_thread(esikleme_varsayilan, "İkili Eşikleme Uygulandı")

def sobel_yatay_wrapper_and_apply():
    """Sobel Yatay işlemini uygula_thread ile başlatır."""
    from islemler import sobel_yatay
    uygula_thread(sobel_yatay, "Sobel Yatay Gradyent Uygulandı")

def sobel_dikey_wrapper_and_apply():
    """Sobel Dikey işlemini uygula_thread ile başlatır."""
    from islemler import sobel_dikey
    uygula_thread(sobel_dikey, "Sobel Dikey Gradyent Uygulandı")

def prewitt_wrapper_and_apply():
    """Prewitt işlemini uygula_thread ile başlatır."""
    from islemler import prewitt
    uygula_thread(prewitt, "Prewitt Kenar Algılama Uygulandı")
    
def kontrast_varsayilan(img):
    """Kontrast işlemini sabit 1.0 değeriyle uygular."""
    from islemler import kontrast_ayarla
    return kontrast_ayarla(img, faktor=1.0)

def kontrast_wrapper_and_apply():
    """Kontrast işlemini uygula_thread ile başlatır."""
    uygula_thread(kontrast_varsayilan, "Kontrast Varsayılan Değere Ayarlandı")
    
def tuzbiber_varsayilan(img): # 🔴 YENİ EKLENDİ
    """Tuz biber gürültüsünü sabit %10 değeriyle uygular."""
    from islemler import tuz_biber_gurultusu_ekle
    return tuz_biber_gurultusu_ekle(img, oran=0.1) 

def tuzbiber_wrapper_and_apply(): # 🔴 YENİ EKLENDİ
    """Tuz Biber Gürültüsü ekleme işlemini uygula_thread ile başlatır."""
    uygula_thread(tuzbiber_varsayilan, "Tuz Biber Gürültüsü (%10) Eklendi")
    
def full_analiz_wrapper(): # 🔴 YENİ EKLENDİ
    """Tüm temel filtreleri ve işlemleri uygulayıp 4xN figürde gösterir."""
    
    if gui_cerceve.current_image is None:
        log_yaz(cerceveler_global, "Resim yok!")
        return
        
    def islem():
        try:
            # İşlemleri Çalıştır ve Sonuçları Al
            from islemler import tum_filtreleri_uygula_gosterim
            sonuclar = tum_filtreleri_uygula_gosterim(gui_cerceve.current_image)
            
            # Figürü Göster
            from gui_cerceve import show_multiple_images
            show_multiple_images(sonuclar, baslik="CVSİZ Temel Görüntü İşleme Analizi")

            log_yaz(cerceveler_global, f"{len(sonuclar)} Farklı İşlem Sonucu Analiz Figüründe Gösterildi.")
             
        except Exception as e:
             log_yaz(cerceveler_global, f"HATA (Full Analiz): {e}")

    # Uzun sürebileceği için Thread içinde çalıştır
    threading.Thread(target=islem, daemon=True).start()


# ======================================================
# THREAD / GEOMETRİ UYGULAMA MANTIĞI (LOG MESAJLARI DÜZELTİLDİ)
# ======================================================
cerceveler_global = None

def uygula_thread(fonk, mesaj=None): # mesaj parametresi eklendi
    if gui_cerceve.current_image is None:
        log_yaz(cerceveler_global, "Resim yok!")
        return
    
    # Kodu yazdır
    kod = kod_oku_cvsiz(fonk)
    gui_cerceve.kod_yaz(kod)

    def islem():
        try:
             yeni = fonk(gui_cerceve.current_image)
             gui_cerceve.gui_sonuc_goster(yeni, cerceveler_global)
             
             log_mesaj = mesaj if mesaj else f"İşlem uygulandı: {fonk.__name__}"
             gui_cerceve.log_yaz(cerceveler_global, log_mesaj)
             
        except Exception as e:
             gui_cerceve.log_yaz(cerceveler_global, f"HATA (CVSİZ): {e}")

    threading.Thread(target=islem, daemon=True).start()

def uygula_geometri(fonk, mesaj): # mesaj parametresi var
    if gui_cerceve.current_image is None: 
        log_yaz(cerceveler_global, "Resim yok!")
        return
        
    # Kodu yazdır
    kod = kod_oku_cvsiz(fonk)
    gui_cerceve.kod_yaz(kod)
    
    try:
        yeni = fonk(gui_cerceve.current_image)
        gui_cerceve.gui_sonuc_goster(yeni, cerceveler_global)
        gui_cerceve.ciz_histogram(yeni, cerceveler_global)
        
        gui_cerceve.log_yaz(cerceveler_global, f"İşlem uygulandı: {mesaj}")
        
    except Exception as e:
        gui_cerceve.log_yaz(cerceveler_global, f"HATA (CVSİZ): {e}")


# ======================================================
# ANA BAĞLAMA FONKSİYONU (LOG MESAJLARI DÜZELTİLDİ)
# ======================================================
def butonlari_bagla(butonlar, cerceveler):
    global cerceveler_global
    cerceveler_global = cerceveler
    alt = cerceveler["alt"]

    # -----------------------------
    # ANALİZ AÇICI (4 BUTON + YENİ FULL ANALİZ)
    # -----------------------------
    def analiz_ac(fonk, isim):
        if fonk is None:
            tk.messagebox.showerror("Hata", f"{isim} modülü bulunamadı (cvsiz klasörünü kontrol edin).")
            return
        if gui_cerceve.current_image is None:
            log_yaz(cerceveler, "Resim yok!")
            return
        log_yaz(cerceveler, f"{isim} Analiz Penceresi Açıldı")
        fonk(gui_cerceve.current_image)

    # 🔥 ANALİZ BUTONLARI
    butonlar["Yüksek Geçiren"].config(
        command=lambda: analiz_ac(goster_yuksek, "Yüksek Geçiren")
    )
    butonlar["Gradyent"].config(
        command=lambda: analiz_ac(goster_grad, "Gradyent")
    )
    butonlar["Geniş Laplace"].config(
        command=lambda: analiz_ac(goster_lap, "Geniş Laplace")
    )
    butonlar["Geniş Prewitt"].config(
        command=lambda: analiz_ac(goster_pre, "Geniş Prewitt")
    )
    
    # 🔴 YENİ BUTON BAĞLANTISI
    if "Full Analiz" in butonlar:
         butonlar["Full Analiz"].config(command=full_analiz_wrapper)


    # -----------------------------
    # MORFOLOJİ - Düzeltilmiş Atama
    # -----------------------------
    if "Morfoloji" in butonlar:
        def morfoloji_ac():
            if gui_cerceve.current_image is None:
                log_yaz(cerceveler, "Resim yok!")
                return
            if goster_morfoloji:
                log_yaz(cerceveler, "Morfoloji Analiz Penceresi Açıldı") 
                goster_morfoloji(gui_cerceve.current_image)
            else:
                 tk.messagebox.showerror("Hata", "Morfoloji modülü bulunamadı (cvsiz/morfolojipencere.py).")

        butonlar["Morfoloji"].config(command=morfoloji_ac)

    # -----------------------------
    # TEK TIKLA İŞLEMLERİ (ÖZEL MESAJLARLA BAĞLANIYOR)
    # -----------------------------
    
    butonlar["Gri"].config(command=lambda: uygula_thread(gri, "Gri Tonlama Uygulandı"))
    butonlar["Negatif"].config(command=lambda: uygula_thread(negatif, "Negatif Görüntüleme Uygulandı"))
    
    # KRİTİK DÜZELTME: Eşikleme butonunu wrapper'a atadık.
    butonlar["Eşikleme"].config(command=esikleme_wrapper_and_apply) 
    
    butonlar["Logaritmik"].config(command=lambda: uygula_thread(logaritmik, "Logaritmik Dönüşüm Uygulandı"))
    butonlar["Kontrast Germe"].config(command=lambda: uygula_thread(kontrast_germe, "Kontrast Germe Uygulandı"))
    butonlar["Histogram Eşitleme"].config(command=lambda: uygula_thread(histogram_esitleme, "Histogram Eşitleme Uygulandı"))
    
    # FİLTRELER:
    butonlar["Mean Filter"].config(command=lambda: uygula_thread(mean_filter, "Mean (Ortalama) Filtre Uygulandı"))
    butonlar["Gaussian Filter"].config(command=lambda: uygula_thread(gaussian_filter, "Gaussian Filtre Uygulandı"))
    butonlar["Median Filter"].config(command=lambda: uygula_thread(median_filter, "Median Filtre Uygulandı"))
    butonlar["Laplacian"].config(command=lambda: uygula_thread(laplacian, "Laplacian Kenar Algılama Uygulandı"))
    
    # GÜRÜLTÜ EKLEME (YENİ)
    if "Tuz Biber Gürültü" in butonlar:
        butonlar["Tuz Biber Gürültü"].config(command=tuzbiber_wrapper_and_apply)
    
    # KRİTİK DÜZELTME: Sobel/Prewitt butonlarını wrapper'a atadık.
    butonlar["Sobel Yatay"].config(command=sobel_yatay_wrapper_and_apply) 
    butonlar["Sobel Dikey"].config(command=sobel_dikey_wrapper_and_apply)
    butonlar["Prewitt"].config(command=prewitt_wrapper_and_apply)
    
    # GEOMETRİK İŞLEMLER:
    butonlar["Aynalama"].config(command=lambda: uygula_geometri(ayna, "Aynalama (Yatay Yansıtma) Uygulandı"))
    butonlar["Ters Çevirme"].config(command=lambda: uygula_geometri(ters_cevir, "Ters Çevirme (Dikey Yansıtma) Uygulandı"))

    # AYAR PANELLİLER (Wrapper'lar kullanıldı):
    
    # Parlaklık için özel bir wrapper olmadığından direkt lambda kullanıldı.
    butonlar["Parlaklık"].config(
        command=lambda: uygula_geometri(lambda img: parlaklik_ayarla(img, 0), "Parlaklık (Sıfırlandı) Uygulandı")
    )

    # KRİTİK DÜZELTME: Kontrast butonu wrapper'a atandı
    butonlar["Kontrast"].config(
        command=kontrast_wrapper_and_apply 
    )
    
    # Öteleme ayarı yoksa sıfır değerini uygula
    butonlar["Öteleme"].config(
        command=lambda: uygula_geometri(lambda img: ote(img, 0, 0), "Öteleme (Sıfırlandı) Uygulandı")
    )
    
    # Açı Döndürme ayarı yoksa sıfır açıyı uygula
    butonlar["Açı Döndürme"].config(
        command=lambda: uygula_geometri(lambda img: aci_degistir(img, 0), "Açı Döndürme (Sıfırlandı) Uygulandı")
    )
    if "Tuz Biber Analiz" in butonlar:
        butonlar["Tuz Biber Analiz"].config(
            command=lambda: analiz_ac(goster_tuzbiber, "Tuz Biber Analiz")
        )
    # Yeniden Boyutlandırma (islemler.py'de yeniden_boyutlandir olduğu varsayılır)
    try: 
        from islemler import yeniden_boyutlandir
        def boyut_sifirla(img):
            w, h = img.size
            return yeniden_boyutlandir(img, (w, h))
        butonlar["Yeniden Boyutlandırma"].config(
            command=lambda: uygula_geometri(boyut_sifirla, "Boyutlandırma (Sıfırlandı) Uygulandı")
        )
    except ImportError:
         log_yaz(cerceveler, "HATA: yeniden_boyutlandir fonksiyonu bulunamadı.")