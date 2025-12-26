# cvislem.py

# -*- coding: utf-8 -*-
import cv2
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import messagebox

# ======================================================
# YARDIMCI DÖNÜŞÜMLER
# ======================================================
def pil_to_cv(img_pil):
    """PIL RGB/BGR görüntüyü OpenCV BGR formatına çevirir."""
    if img_pil.mode == 'RGB':
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    elif img_pil.mode == 'L':
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_GRAY2BGR)
    else:
        return cv2.cvtColor(np.array(img_pil.convert('RGB')), cv2.COLOR_RGB2BGR)

def cv_to_pil(img_cv):
    """OpenCV BGR görüntüyü PIL RGB formatına çevirir."""
    return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

# ... (Mevcut diğer cv_gri, cv_negatif, cv_esikleme vb. fonksiyonlar buraya gelir) ...

# ======================================================
# BASİT GÖRÜNTÜ İŞLEMLERİ
# ======================================================
def cv_gri(img):
    cv = pil_to_cv(img)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    return Image.fromarray(gray)

def cv_negatif(img):
    cv = pil_to_cv(img)
    neg = cv2.bitwise_not(cv)
    return cv_to_pil(neg)

def cv_esikleme(img):
    cv = pil_to_cv(img) 
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return Image.fromarray(th)

def cv_logaritmik(img):
    cv = pil_to_cv(img).astype(np.float32)
    c = 255 / np.log(1 + np.max(cv))
    log_img = c * np.log(1 + cv)
    log_img = np.array(log_img, dtype=np.uint8)
    return cv_to_pil(log_img)

def cv_kontrast_germe(img):
    cv = pil_to_cv(img)
    min_val, max_val = np.min(cv), np.max(cv)
    stretched = (cv - min_val) * (255 / (max_val - min_val))
    return cv_to_pil(stretched.astype(np.uint8))

def cv_histogram(img):
    cv = pil_to_cv(img)
    ycrcb = cv2.cvtColor(cv, cv2.COLOR_BGR2YCrCb)
    ycrcb[:,:,0] = cv2.equalizeHist(ycrcb[:,:,0])
    eq = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
    return cv_to_pil(eq)

def cv_parlaklik(img, beta=0):
    cv = pil_to_cv(img)
    sonuc = cv2.convertScaleAbs(cv, alpha=1.0, beta=beta)
    return cv_to_pil(sonuc)

def cv_kontrast(img, alpha=1.0):
    cv = pil_to_cv(img)
    sonuc = cv2.convertScaleAbs(cv, alpha=alpha, beta=0.0)
    return cv_to_pil(sonuc)

# ======================================================
# FİLTRELER
# ======================================================
def cv_mean(img):
    cv = pil_to_cv(img)
    return cv_to_pil(cv2.blur(cv, (5,5)))

def cv_gaussian(img):
    cv = pil_to_cv(img)
    return cv_to_pil(cv2.GaussianBlur(cv, (5,5), 0))

def cv_median(img):
    cv = pil_to_cv(img)
    return cv_to_pil(cv2.medianBlur(cv, 5))

def cv_laplace(img):
    cv = pil_to_cv(img)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    lap = np.uint8(np.absolute(lap))
    return Image.fromarray(lap)

def cv_sobel_y(img):
    cv = pil_to_cv(img)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    sob = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    return Image.fromarray(np.uint8(np.absolute(sob)))

def cv_sobel_x(img):
    cv = pil_to_cv(img)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    sob = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    return Image.fromarray(np.uint8(np.absolute(sob)))

def cv_prewitt(img):
    cv = pil_to_cv(img)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    kernelx = np.array([[1,0,-1],[1,0,-1],[1,0,-1]])
    pre = cv2.filter2D(gray, -1, kernelx)
    return Image.fromarray(np.uint8(np.absolute(pre)))

# ======================================================
# MORFOLOJİ İŞLEMLERİ
# ======================================================
def cv_morfoloji(img, islem_tipi, cekirdek_boyutu=3): 
    """Genel Morfoloji İşlevi"""
    cv = pil_to_cv(img)
    
    if cekirdek_boyutu % 2 == 0:
        cekirdek_boyutu += 1
        
    kernel = np.ones((cekirdek_boyutu, cekirdek_boyutu), np.uint8)

    if islem_tipi == "erozyon":
        sonuc = cv2.erode(cv, kernel, iterations=1)
    elif islem_tipi == "genisleme":
        sonuc = cv2.dilate(cv, kernel, iterations=1)
    elif islem_tipi == "acma":
        sonuc = cv2.morphologyEx(cv, cv2.MORPH_OPEN, kernel)
    elif islem_tipi == "kapama":
        sonuc = cv2.morphologyEx(cv, cv2.MORPH_CLOSE, kernel)
    elif islem_tipi == "gradient":
        sonuc = cv2.morphologyEx(cv, cv2.MORPH_GRADIENT, kernel)
    elif islem_tipi == "tophat":
        sonuc = cv2.morphologyEx(cv, cv2.MORPH_TOPHAT, kernel)
    elif islem_tipi == "blackhat":
        sonuc = cv2.morphologyEx(cv, cv2.MORPH_BLACKHAT, kernel)
    elif islem_tipi == "orjinal": 
        return img 
    else:
        return img 

    return cv_to_pil(sonuc)


# ======================================================
# GEOMETRİ
# ======================================================
def cv_dondur(img, aci=10):
    cv = pil_to_cv(img)
    h, w = cv.shape[:2]
    m = cv2.getRotationMatrix2D((w//2,h//2), aci, 1)
    rot = cv2.warpAffine(cv, m, (w,h))
    return cv_to_pil(rot)

def cv_ayna(img):
    cv = pil_to_cv(img)
    return cv_to_pil(cv2.flip(cv, 1))

def cv_ters(img):
    cv = pil_to_cv(img)
    return cv_to_pil(cv2.flip(cv, 0))

def cv_otele(img, dx=50, dy=50):
    cv = pil_to_cv(img)
    m = np.float32([[1,0,dx],[0,1,dy]])
    sh = cv2.warpAffine(cv, m, (cv.shape[1], cv.shape[0]))
    return cv_to_pil(sh)
    
def cv_boyutlandir(img, boyut=(0, 0)): 
    cv = pil_to_cv(img)
    
    new_w, new_h = boyut 

    if new_w == 0 or new_h == 0:
        h, w = cv.shape[:2]
        new_w, new_h = w, h
        
    return cv_to_pil(cv2.resize(cv, (new_w, new_h)))


# ======================================================
# YÜKSEK GEÇİREN ANALİZ İŞLEMLERİ (ANALİZ PENCERESİ İÇİN EKLENEN KISIM)
# ======================================================

def laplacian_kenar_haritasi_cv(img_pil):
    """
    OpenCV kullanarak Laplasyen çıktısını (Laplacian Çıktısı) üretir.
    """
    img_cv_rgb = np.array(img_pil.convert('RGB'))
    img_cv = cv2.cvtColor(img_cv_rgb, cv2.COLOR_RGB2GRAY)
    
    laplacian_cv = cv2.Laplacian(img_cv, cv2.CV_64F, ksize=3)
    laplacian_normalized = cv2.convertScaleAbs(laplacian_cv)
    
    return Image.fromarray(laplacian_normalized)

def laplacian_keskinlestir_cv(img_pil, C):
    """
    OpenCV filter2D kullanarak Laplasyen tabanlı keskinleştirmeyi yapar (3. ve 4. Sütun).
    C=5: Merkez 5 Çekirdeği; C=9: Merkez 9/8 Çekirdeği.
    """
    img_cv_rgb = np.array(img_pil.convert('RGB'))
    img_cv = cv2.cvtColor(img_cv_rgb, cv2.COLOR_RGB2GRAY)
    
    img_float = img_cv.astype(np.float32)

    if C == 5:
        # Merkez 5 Çekirdeği: [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    elif C == 9:
        # Merkez 9 Çekirdeği: [[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]] (Merkez 8 etkisi)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32)
    else:
        raise ValueError("C değeri sadece 5 veya 9 olmalıdır.")

    sharpened_output = cv2.filter2D(img_float, ddepth=-1, kernel=kernel)

    sharpened_output = np.clip(sharpened_output, 0, 255).astype(np.uint8)

    return Image.fromarray(sharpened_output)

def gri_yap_dondur(img):
    """PIL Image objesini gri tonlamada döndürür (Analiz penceresi için)."""
    return img.convert('L')