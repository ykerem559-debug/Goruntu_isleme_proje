import math
from PIL import Image
import random # Gürültü eklemek için gerekli

# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================

def sinir_koy(deger):
    if deger > 255: return 255
    if deger < 0: return 0
    return int(deger)

def gri_yap_dondur(img):
    """Filtreler için hızlı griye çevirme."""
    if img.mode == 'L':
        return img.copy()
    
    genislik, yukseklik = img.size
    yeni = Image.new("L", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    # Eğer resim RGB değilse convert et (Hata önleyici)
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    pix_eski = img.load()
    
    for y in range(yukseklik):
        for x in range(genislik):
            r, g, b = pix_eski[x, y]
            val = int(r * 0.299 + g * 0.587 + b * 0.114)
            pix_yeni[x, y] = val
    return yeni

def konvolusyon_uygula(img, kernel):
    """
    Optimize edilmiş manuel konvolüsyon.
    Fonksiyon çağrıları azaltıldı.
    """
    gri_img = gri_yap_dondur(img)
    genislik, yukseklik = gri_img.size
    pixels = gri_img.load()
    
    k_boyut = len(kernel)
    pad = k_boyut // 2
    
    yeni = Image.new("L", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    range_y = range(pad, yukseklik - pad)
    range_x = range(pad, genislik - pad)
    range_k = range(k_boyut)
    
    for y in range_y:
        for x in range_x:
            
            toplam = 0.0 # Float olarak başlat
            
            # Kernel Döngüsü
            for ky in range_k:
                for kx in range_k:
                    piksel = pixels[x + kx - pad, y + ky - pad]
                    k_val = kernel[ky][kx]
                    
                    if k_val != 0:
                        toplam += piksel * k_val
            
            # INLINE CLIPPING (Fonksiyon çağırmadan sınır koyma)
            if toplam > 255:
                pix_yeni[x, y] = 255
            elif toplam < 0:
                pix_yeni[x, y] = 0
            else:
                pix_yeni[x, y] = int(toplam)
            
    return yeni

# =========================================================
# TEMEL İŞLEMLER
# =========================================================

def gri(img):
    genislik, yukseklik = img.size
    yeni = Image.new("L", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    if img.mode != 'RGB': img = img.convert('RGB')
    pix_eski = img.load()

    for y in range(yukseklik):
        for x in range(genislik):
            r, g, b = pix_eski[x, y]
            pix_yeni[x, y] = int(r * 0.299 + g * 0.587 + b * 0.114)
    return yeni

def negatif(img):
    genislik, yukseklik = img.size
    yeni = Image.new(img.mode, (genislik, yukseklik))
    pix_yeni = yeni.load()
    pix_eski = img.load()
    
    is_rgb = (img.mode == 'RGB')

    for y in range(yukseklik):
        for x in range(genislik):
            piksel = pix_eski[x, y]
            if is_rgb:
                r, g, b = piksel
                pix_yeni[x, y] = (255 - r, 255 - g, 255 - b)
            else:
                pix_yeni[x, y] = 255 - piksel
    return yeni

def parlaklik_ayarla(img, deger):
    genislik, yukseklik = img.size
    yeni = Image.new("RGB", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    if img.mode != 'RGB': img = img.convert('RGB')
    pix_eski = img.load()

    for y in range(yukseklik):
        for x in range(genislik):
            r, g, b = pix_eski[x, y]
            
            nr = r + deger
            ng = g + deger
            nb = b + deger
            
            if nr > 255: nr = 255
            elif nr < 0: nr = 0
            
            if ng > 255: ng = 255
            elif ng < 0: ng = 0
            
            if nb > 255: nb = 255
            elif nb < 0: nb = 0
            
            pix_yeni[x, y] = (nr, ng, nb)
    return yeni

def kontrast_ayarla(img, faktor):
    genislik, yukseklik = img.size
    yeni = Image.new("RGB", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    if img.mode != 'RGB': img = img.convert('RGB')
    pix_eski = img.load()

    for y in range(yukseklik):
        for x in range(genislik):
            r, g, b = pix_eski[x, y]
            
            nr = int((r - 128) * faktor + 128)
            ng = int((g - 128) * faktor + 128)
            nb = int((b - 128) * faktor + 128)
            
            if nr > 255: nr = 255
            elif nr < 0: nr = 0
            
            if ng > 255: ng = 255
            elif ng < 0: ng = 0
            
            if nb > 255: nb = 255
            elif nb < 0: nb = 0
            
            pix_yeni[x, y] = (nr, ng, nb)
    return yeni

def esikleme(img, esik=128):
    genislik, yukseklik = img.size
    yeni = Image.new("L", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    if img.mode != 'RGB': img = img.convert('RGB')
    pix_eski = img.load()

    for y in range(yukseklik):
        for x in range(genislik):
            r, g, b = pix_eski[x, y]
            gri_val = int(r * 0.299 + g * 0.587 + b * 0.114)
            
            if gri_val > esik:
                pix_yeni[x, y] = 255
            else:
                pix_yeni[x, y] = 0
    return yeni

def logaritmik(img):
    gri_img = gri_yap_dondur(img)
    genislik, yukseklik = gri_img.size
    pixels = gri_img.load()
    yeni = Image.new("L", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    c = 255 / math.log(1 + 255)
    
    for y in range(yukseklik):
        for x in range(genislik):
            val = pixels[x, y]
            log_val = int(c * math.log(1 + val))
            
            if log_val > 255: log_val = 255
            elif log_val < 0: log_val = 0
            pix_yeni[x, y] = log_val
    return yeni

def kontrast_germe(img):
    gri_img = gri_yap_dondur(img)
    genislik, yukseklik = gri_img.size
    pixels = gri_img.load()
    yeni = Image.new("L", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    min_val = 255
    max_val = 0
    
    # Min-Max bulma döngüsü
    for y in range(yukseklik):
        for x in range(genislik):
            val = pixels[x, y]
            if val < min_val: min_val = val
            if val > max_val: max_val = val
            
    if max_val == min_val:
        return gri_img
        
    diff = max_val - min_val
    
    for y in range(yukseklik):
        for x in range(genislik):
            val = pixels[x, y]
            norm = int((val - min_val) / diff * 255)
            pix_yeni[x, y] = norm
            
    return yeni

def histogram_esitleme(img):
    gri_img = gri_yap_dondur(img)
    genislik, yukseklik = gri_img.size
    pixels = gri_img.load()
    
    hist = [0] * 256
    for y in range(yukseklik):
        for x in range(genislik):
            hist[pixels[x, y]] += 1
            
    cdf = [0] * 256
    cdf[0] = hist[0]
    for i in range(1, 256):
        cdf[i] = cdf[i-1] + hist[i]
        
    cdf_min = 0
    for c in cdf:
        if c > 0:
            cdf_min = c
            break
            
    toplam = genislik * yukseklik
    yeni_degerler = [0] * 256
    
    payda = toplam - cdf_min
    if payda == 0: payda = 1
    
    for i in range(256):
        val = int(round((cdf[i] - cdf_min) / payda * 255))
        if val > 255: val = 255
        elif val < 0: val = 0
        yeni_degerler[i] = val
        
    yeni = Image.new("L", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    for y in range(yukseklik):
        for x in range(genislik):
            pix_yeni[x, y] = yeni_degerler[pixels[x, y]]
            
    return yeni

# =========================================================
# FİLTRELER
# =========================================================

def mean_filter(img):
    gri_img = gri_yap_dondur(img)
    genislik, yukseklik = gri_img.size
    pixels = gri_img.load()
    
    yeni = Image.new("L", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    for y in range(1, yukseklik - 1):
        for x in range(1, genislik - 1):
            
            toplam = (
                pixels[x-1, y-1] + pixels[x, y-1] + pixels[x+1, y-1] +
                pixels[x-1, y]   + pixels[x, y]   + pixels[x+1, y]   +
                pixels[x-1, y+1] + pixels[x, y+1] + pixels[x+1, y+1]
            )
            
            pix_yeni[x, y] = toplam // 9
            
    return yeni


def laplacian(img):
    gri_img = gri_yap_dondur(img)
    genislik, yukseklik = gri_img.size
    pixels = gri_img.load()
    
    yeni = Image.new("L", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    for y in range(1, yukseklik - 1):
        for x in range(1, genislik - 1):
            
            merkez = pixels[x, y]
            ust    = pixels[x, y-1]
            alt    = pixels[x, y+1]
            sol    = pixels[x-1, y]
            sag    = pixels[x+1, y]
            
            val = (merkez * 4) - (ust + alt + sol + sag)
            
            if val > 255: val = 255
            elif val < 0: val = 0
            
            pix_yeni[x, y] = val
            
    return yeni


def gaussian_kernel_uret(sigma=1.0):
    kernel = [[0.0 for _ in range(3)] for _ in range(3)]
    toplam = 0.0

    for y in range(3):
        for x in range(3):
            dx = x - 1
            dy = y - 1
            deger = math.exp(-(dx*dx + dy*dy) / (2 * sigma * sigma))
            kernel[y][x] = deger
            toplam += deger

    for y in range(3):
        for x in range(3):
            kernel[y][x] /= toplam

    return kernel


def gaussian_filter(img):
    kernel = gaussian_kernel_uret(1.0)
    return konvolusyon_uygula(img, kernel)


def sobel_yatay_kernel_uret():
    kernel = [[0 for _ in range(3)] for _ in range(3)]
    for y in range(3):
        for x in range(3):
            dx = x - 1
            dy = y - 1
            if dy == 0:
                kernel[y][x] = dx * 2
            else:
                kernel[y][x] = dx
    return kernel


def sobel_dikey_kernel_uret():
    kernel = [[0 for _ in range(3)] for _ in range(3)]
    for y in range(3):
        for x in range(3):
            dx = x - 1
            dy = y - 1
            if dx == 0:
                kernel[y][x] = dy * 2
            else:
                kernel[y][x] = dy
    return kernel


def sobel_yatay(img):
    return konvolusyon_uygula(img, sobel_yatay_kernel_uret())


def sobel_dikey(img):
    return konvolusyon_uygula(img, sobel_dikey_kernel_uret())

def prewitt_kernel_uret():
    kernel = [[0 for _ in range(3)] for _ in range(3)]
    for y in range(3):
        for x in range(3):
            dy = y - 1
            kernel[y][x] = dy
    return kernel


def prewitt(img):
    return konvolusyon_uygula(img, prewitt_kernel_uret())


def median_filter(img):
    gri_img = gri_yap_dondur(img)
    genislik, yukseklik = gri_img.size
    pixels = gri_img.load()
    yeni = Image.new("L", (genislik, yukseklik))
    pix_yeni = yeni.load()
    
    for y in range(1, yukseklik - 1):
        for x in range(1, genislik - 1):
            komsular = [
                pixels[x-1, y-1], pixels[x, y-1], pixels[x+1, y-1],
                pixels[x-1, y],   pixels[x, y],   pixels[x+1, y],
                pixels[x-1, y+1], pixels[x, y+1], pixels[x+1, y+1]
            ]
            komsular.sort()
            pix_yeni[x, y] = komsular[4]
            
    return yeni

# =========================================================
# GÜRÜLTÜ İŞLEMLERİ (Yeni Eklendi)
# =========================================================

def tuz_biber_gurultusu_ekle(img, oran=0.1):
    """
    Görüntüye 'tuz ve biber' (salt and pepper) gürültüsü ekler.
    Oran, gürültülenecek piksel yüzdesidir (0.0 ile 1.0 arası).
    """
    
    if img.mode != 'RGB': 
        img = img.convert('RGB')
        
    genislik, yukseklik = img.size
    yeni = img.copy()
    pix_yeni = yeni.load()
    
    toplam_piksel = genislik * yukseklik
    gurultu_sayisi = int(toplam_piksel * oran)
    
    for _ in range(gurultu_sayisi):
        x = random.randint(0, genislik - 1)
        y = random.randint(0, yukseklik - 1)
        
        if random.random() < 0.5:
            # Tuz (Beyaz)
            pix_yeni[x, y] = (255, 255, 255)
        else:
            # Biber (Siyah)
            pix_yeni[x, y] = (0, 0, 0)
            
    return yeni

# =========================================================
# GEOMETRİK İŞLEMLER
# =========================================================

def ayna(img):
    genislik, yukseklik = img.size
    yeni = Image.new("RGB", (genislik, yukseklik))
    if img.mode != 'RGB': img = img.convert('RGB')
    pix_eski = img.load()
    pix_yeni = yeni.load()
    
    for y in range(yukseklik):
        for x in range(genislik):
            pix_yeni[x, y] = pix_eski[genislik - 1 - x, y]
    return yeni

def ters_cevir(img):
    genislik, yukseklik = img.size
    yeni = Image.new("RGB", (genislik, yukseklik))
    if img.mode != 'RGB': img = img.convert('RGB')
    pix_eski = img.load()
    pix_yeni = yeni.load()
    
    for y in range(yukseklik):
        for x in range(genislik):
            pix_yeni[x, y] = pix_eski[x, yukseklik - 1 - y]
    return yeni

def ote(img, dx, dy):
    genislik, yukseklik = img.size
    yeni = Image.new("RGB", (genislik, yukseklik))
    if img.mode != 'RGB': img = img.convert('RGB')
    pix_eski = img.load()
    pix_yeni = yeni.load()
    
    bas_y = max(0, dy)
    bit_y = min(yukseklik, yukseklik + dy)
    bas_x = max(0, dx)
    bit_x = min(genislik, genislik + dx)
    
    for y in range(bas_y, bit_y):
        src_y = y - dy
        for x in range(bas_x, bit_x):
            src_x = x - dx
            if 0 <= src_x < genislik and 0 <= src_y < yukseklik:
                pix_yeni[x, y] = pix_eski[src_x, src_y]
                
    return yeni

def aci_degistir(img, derece):
    if img.mode != 'RGB': img = img.convert('RGB')
    w, h = img.size
    rad = math.radians(derece)
    cos_v = math.cos(rad)
    sin_v = math.sin(rad)
    
    yeni_w = int(abs(w * cos_v) + abs(h * sin_v))
    yeni_h = int(abs(w * sin_v) + abs(h * cos_v))
    
    yeni = Image.new("RGB", (yeni_w, yeni_h))
    pix_yeni = yeni.load()
    pix_eski = img.load()
    
    cx, cy = w // 2, h // 2
    ncx, ncy = yeni_w // 2, yeni_h // 2
    
    for y in range(yeni_h):
        ty_part_cos = (y - ncy) * cos_v
        ty_part_sin = (y - ncy) * sin_v
        
        for x in range(yeni_w):
            tx = x - ncx
            
            ox = int(tx * cos_v + ty_part_sin + cx)
            oy = int(-tx * sin_v + ty_part_cos + cy)
            
            if 0 <= ox < w and 0 <= oy < h:
                pix_yeni[x, y] = pix_eski[ox, oy]
    return yeni

def yeniden_boyutlandir(img, boyut):
    w, h = img.size
    hedef_w, hedef_h = boyut
    
    if img.mode != 'RGB': 
        img = img.convert('RGB')
        
    yeni = Image.new("RGB", (hedef_w, hedef_h))
    pix_yeni = yeni.load()
    pix_eski = img.load()
    
    x_oran = w / hedef_w
    y_oran = h / hedef_h
    
    for y in range(hedef_h):
        src_y = int(y * y_oran)
        src_y = min(src_y, h - 1) 
        
        for x in range(hedef_w):
            src_x = int(x * x_oran)
            src_x = min(src_x, w - 1) 
            
            pix_yeni[x, y] = pix_eski[src_x, src_y]
            
    return yeni

# =========================================================
# ÖZEL ANALİZ İŞLEMİ (Yeni Eklendi)
# =========================================================

def tum_filtreleri_uygula_gosterim(img):
    """
    Belirli temel filtre ve işlemleri uygulayarak sonuçları listeler.
    Bu, GUI'de Matplotlib ile yan yana gösterim için kullanılacaktır.
    """
    
    sonuclar = []

    # Orijinal resim (Gösterim için RGB, ama gri yapıp kullanmak daha tutarlı)
    img_orjinal = img.copy() 
    img_gri = gri(img_orjinal) # Griye çevir (Çoğu filtre için başlangıç)

    sonuclar.append({"img": img_orjinal, "title": "0. Orijinal Görüntü"})
    sonuclar.append({"img": img_gri, "title": "1. Gri Tonlama"})
    
    # 1. Temel İşlemler
    sonuclar.append({"img": negatif(img_gri), "title": "2. Negatif"})
    sonuclar.append({"img": esikleme(img_gri, esik=128), "title": "3. İkili Eşikleme (128)"})

    # 2. Yoğunluk Dönüşümleri
    sonuclar.append({"img": logaritmik(img_gri), "title": "4. Logaritmik"})
    sonuclar.append({"img": kontrast_germe(img_gri), "title": "5. Kontrast Germe"})
    sonuclar.append({"img": histogram_esitleme(img_gri), "title": "6. Histogram Eşitleme"})

    # 3. Düzeltme/Gürültü Filtreleri
    img_gurultulu = tuz_biber_gurultusu_ekle(img_orjinal, oran=0.1) # Gürültü ekle
    sonuclar.append({"img": img_gurultulu, "title": "7. Tuz Biber Gürültü (%10)"})
    sonuclar.append({"img": mean_filter(img_gurultulu), "title": "8. Mean (Ortalama) Filtre"})
    sonuclar.append({"img": median_filter(img_gurultulu), "title": "9. Median Filtre"})
    sonuclar.append({"img": gaussian_filter(img_gri), "title": "10. Gaussian Filtre (Yumuşatma)"})


    # 4. Kenar Algılama Filtreleri
    sonuclar.append({"img": laplacian(img_gri), "title": "11. Laplacian (Kenar)"})
    sonuclar.append({"img": sobel_yatay(img_gri), "title": "12. Sobel Yatay (Kenar)"})
    sonuclar.append({"img": prewitt(img_gri), "title": "13. Prewitt (Kenar)"})
        
    return sonuclar