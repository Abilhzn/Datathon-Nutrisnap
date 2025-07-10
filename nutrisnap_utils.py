# Library
import pytesseract
from PIL import Image
import re
from pathlib import Path
import cv2
import pandas as pd
import google.generativeai as genai
import json
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# komposisi
KAMUS_BAHAN_MERAH_ID = {
    'GULA_DAN_PEMANIS': ['gula', 'sirup fruktosa', 'sirup jagung', 'dekstrosa', 'maltodekstrin', 'pemanis buatan', 'aspartam', 'sakarin', 'sukralosa', 'asesulfam-k'],
    'LEMAK_JAHAT': ['lemak trans', 'minyak terhidrogenasi', 'lemak terhidrogenasi', 'shortening', 'minyak nabati terhidrogenasi'],
    'GARAM_TINGGI': ['garam', 'natrium', 'sodium'],
    'ADITIF_KONTROVERSIAL': ['mononatrium glutamat', 'msg', 'penguat rasa', 'perisa sintetik', 'pewarna buatan', 'tartrazin', 'kuning fcf', 'ponceau', 'karmoisin', 'pengawet', 'natrium benzoat', 'kalium sorbat', 'bht', 'bha']
}
KAMUS_BAHAN_HIJAU_ID = {
    'SERAT_DAN_GANDUM_UTUH': ['gandum utuh', 'whole wheat', 'serat pangan', 'oat', 'bekatul', 'serat larut'],
    'SUMBER_BAIK': ['protein', 'kalsium', 'vitamin', 'mineral', 'ekstrak buah', 'sayuran kering'],
    'KLAIM_POSITIF': ['tanpa tambahan gula', 'tanpa pengawet', 'tanpa pewarna', 'sumber serat']
}
KAMUS_BAHAN_MERAH_EN = {
    'SUGAR_AND_SWEETENERS': ['sugar', 'fructose syrup', 'corn syrup', 'dextrose', 'maltodextrin', 'artificial sweetener', 'aspartame', 'saccharin', 'sucralose', 'acesulfame-k'],
    'BAD_FATS': ['trans fat', 'hydrogenated oil', 'partially hydrogenated oil', 'shortening'],
    'HIGH_SALT': ['salt', 'sodium'],
    'CONTROVERSIAL_ADDITIVES': ['monosodium glutamate', 'msg', 'flavor enhancer', 'artificial flavor', 'artificial color', 'tartrazine', 'sunset yellow', 'carmine', 'preservative', 'sodium benzoate', 'potassium sorbate', 'bht', 'bha']
}
KAMUS_BAHAN_HIJAU_EN = {
    'FIBER_AND_WHOLE_GRAINS': ['whole wheat', 'whole grain', 'dietary fiber', 'oat', 'bran', 'soluble fiber'],
    'GOOD_SOURCES': ['protein', 'calcium', 'vitamin', 'mineral', 'fruit extract', 'dried vegetables'],
    'POSITIVE_CLAIMS': ['no added sugar', 'no preservatives', 'no artificial colors', 'source of fiber']
}

# def ekstrak_teks_dari_gambar_komposisi(path_gambar):
#     """
#     Fungsi 'Mata AI' versi UPGRADE:
#     Melakukan pre-processing gambar untuk meningkatkan akurasi OCR.
#     """
#     try:
#         # 1. Baca gambar menggunakan OpenCV
#         gambar = cv2.imread(path_gambar)
        
#         # 2. Ubah ke Grayscale (skala abu-abu)
#         gray = cv2.cvtColor(gambar, cv2.COLOR_BGR2GRAY)
        
#         # 3. Terapkan Thresholding untuk membuat gambar menjadi hitam-putih
#         # Ini membantu mempertajam teks dan menghilangkan noise latar belakang.
#         _, processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
#         # 4. Kirim gambar yang sudah diproses ke Tesseract
#         teks = pytesseract.image_to_string(processed_img, lang='ind')
#         return teks
        
#     except FileNotFoundError:
#         return "ERROR: File gambar tidak ditemukan."
#     except Exception as e:
#         return f"ERROR: Terjadi kesalahan saat memproses gambar: {e}"
    
def analisis_komposisi(teks_komposisi, bahasa='ID'):
    """
    Fungsi 'Otak AI': Menganalisis teks komposisi dan memberikan skor serta alasan.
    """
    # Pilih kamus berdasarkan bahasa yang terdeteksi
    if bahasa == 'EN':
        kamus_merah_aktif = KAMUS_BAHAN_MERAH_EN
        kamus_hijau_aktif = KAMUS_BAHAN_HIJAU_EN
        kata_kunci_penalti = ['sugar', 'salt', 'sodium']
    else: # Default ke ID
        kamus_merah_aktif = KAMUS_BAHAN_MERAH_ID
        kamus_hijau_aktif = KAMUS_BAHAN_HIJAU_ID
        kata_kunci_penalti = ['gula', 'garam', 'natrium']

    skor_kesehatan, alasan = (0, [])
    teks_bersih = teks_komposisi.lower()
    daftar_bahan = [bahan.strip() for bahan in re.split(r'[,\.]', teks_bersih) if bahan.strip()]

    if not daftar_bahan: return 0, ["Tidak dapat mendeteksi daftar bahan."]

    # Aturan Penalti berdasarkan bahasa
    for bahan in daftar_bahan[:3]:
        for kata_kunci in kata_kunci_penalti:
            if kata_kunci in bahan:
                skor_kesehatan -= 5
                alasan.append(f"PENALTI: '{bahan.capitalize()}' ada di 3 bahan teratas.")
                break
        else: continue
        break

    # Looping kamus aktif (merah dan hijau)
    for kategori, daftar_merah in kamus_merah_aktif.items():
        for bahan_merah in daftar_merah:
            if bahan_merah in teks_bersih:
                skor_kesehatan -= 1
                alasan.append(f"TERDETEKSI BAHAN 'MERAH': {bahan_merah.capitalize()}.")
    for kategori, daftar_hijau in kamus_hijau_aktif.items():
        for bahan_hijau in daftar_hijau:
            if bahan_hijau in teks_bersih:
                skor_kesehatan += 1
                alasan.append(f"TERDETEKSI BAHAN 'HIJAU': {bahan_hijau.capitalize()}.")
    return skor_kesehatan, alasan

def berikan_kesimpulan_komposisi(skor):
    """Memberikan vonis akhir berdasarkan skor kesehatan."""
    if skor >= 2:
        return "SEHAT 👍", "Pilihan yang baik. Mengandung lebih banyak bahan positif."
    elif skor > -3 and skor < 2:
        return "CUKUP SEHAT 🤔", "Tidak buruk, tapi perhatikan konsumsinya. Cek komposisi lebih detail."
    else:
        return "TIDAK SEHAT 👎", "Sebaiknya dihindari. Terdeteksi banyak bahan 'merah' atau tinggi gula/garam."

def temukan_dan_pangkas_komposisi(path_gambar):
    """
    Mencari kata 'komposisi' (ID) atau 'ingredients' (EN) di gambar, 
    lalu memangkas gambar secara otomatis untuk hanya menyisakan area di bawah kata tersebut.
    Prioritas pada Bahasa Indonesia.
    """
    try:
        gambar = cv2.imread(path_gambar)
        # Gunakan image_to_data untuk mendapatkan lokasi dan confidence score setiap kata
        data = pytesseract.image_to_data(gambar, lang='ind+eng', output_type=pytesseract.Output.DATAFRAME)
        
        # Hapus data yang tidak terdeteksi dengan baik (confidence score rendah)
        data = data[data.conf > 0]
        data['text'] = data['text'].str.lower()

        baris_komposisi = data[data['text'].str.contains('komposisi')]
        baris_ingredients = data[data['text'].str.contains('ingredients')]
        baris_terpilih, kata_ditemukan, bahasa = (None, "", 'ID') # Default bahasa ke ID

        # baris_terpilih = None
        # kata_ditemukan = ""

        # Aturan Prioritas dan Fallback
        if not baris_komposisi.empty and not baris_ingredients.empty:
            conf_id, conf_en = baris_komposisi.iloc[0]['conf'], baris_ingredients.iloc[0]['conf']
            if conf_id > 70 or conf_id >= conf_en:
                baris_terpilih, kata_ditemukan, bahasa = (baris_komposisi, "Komposisi", 'ID')
            else:
                baris_terpilih, kata_ditemukan, bahasa = (baris_ingredients, "Ingredients", 'EN')
        elif not baris_komposisi.empty:
            baris_terpilih, kata_ditemukan, bahasa = (baris_komposisi, "Komposisi", 'ID')
        elif not baris_ingredients.empty:
            baris_terpilih, kata_ditemukan, bahasa = (baris_ingredients, "Ingredients", 'EN')

        if baris_terpilih is not None:
            print(f"INFO: Kata '{kata_ditemukan}' ditemukan! Melakukan pangkas otomatis...")
            y_pos = baris_terpilih.iloc[0]['top']
            x_pos = baris_terpilih.iloc[0]['left']
            height =  baris_terpilih.iloc[0]['height']
            posisi_awal_crop = y_pos  # Tambahkan sedikit margin di atas
            # posisi_awal_crop = y_pos
            gambar_terpangkas = gambar[posisi_awal_crop : gambar.shape[0], 0 : gambar.shape[1]]
            return gambar_terpangkas, bahasa
        else:
            print("INFO: Kata kunci tidak ditemukan. Menganalisis seluruh gambar dalam Bahasa Indonesia.")
            return gambar, 'ID'
    except Exception as e:
        print(f"ERROR saat auto-crop: {e}")
        return cv2.imread(path_gambar), 'ID'
    
# Gizi
TARGET_NUTRIENTS = {
    'ID': ['gula', 'natrium', 'lemak total', 'serat pangan', 'protein'],
    'EN': ['sugar', 'sodium', 'total fat', 'dietary fiber', 'protein']
}

def pangkas_tabel_gizi_otomatis(path_gambar):
    """
    Mendeteksi bingkai kotak pada gambar dan memangkas area di dalamnya.
    """
    try:
        gambar_asli = cv2.imread(path_gambar)

        # Mengubah ke grayscale dan berikan sedikit blur untuk mengurangi noise
        gray = cv2.cvtColor(gambar_asli, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Deteksi garis tepi menggunakan Canny
        edges = cv2.Canny(blur, 50, 150)

        # Temukan semua kontur (bentuk outline)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        kandidat_kotak = []

        for c in contours:
            # Aproksimasi kontur menjadi bentuk yang lebih sederhana
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)

            if len(approx) == 4: # Jika bentuknya punya 4 sudut, kita anggap itu kandidat
                kandidat_kotak.append(c)

        if kandidat_kotak:
            # Jika ada kandidat, urutkan berdasarkan area dari terbesar ke terkecil dan ambil yang paling besar
            kotak_terbesar = max(kandidat_kotak, key=cv2.contourArea)
            
            # Ambil koordinat bounding box dari kotak terbesar itu
            x, y, w, h = cv2.boundingRect(kotak_terbesar)
            
            # Pangkas gambar asli menggunakan koordinat tersebut dan beri sedikit margin agar tidak terlalu mepet
            margin = 5
            gambar_terpangkas = gambar_asli[y-margin:y+h+margin, x-margin:x+w+margin]
            
            print("INFO: Bingkai tabel gizi terdeteksi! Memangkas otomatis...")
            cv2.imwrite("hasil_terpangkas.jpg", gambar_terpangkas)
            return gambar_terpangkas
        else:
            print("INFO: Tidak ada bingkai kotak yang terdeteksi, menggunakan gambar penuh.")
            return gambar_asli

    except Exception as e:
        print(f"ERROR saat pangkas tabel gizi: {e}")
        return cv2.imread(path_gambar)
    
def bersihkan_nilai_gizi(teks_nilai):
    """Fungsi kecil untuk membersihkan teks nilai (misal: '13g' -> 13.0)"""
    if not isinstance(teks_nilai, str):
        return 0.0
    angka_saja = re.sub(r'[^0-9.]', '', teks_nilai)
    try:
        return float(angka_saja)
    except (ValueError, TypeError):
        return 0.0

def ekstrak_data_dengan_koordinat(path_gambar):
    """
    Alternatif non-LLM untuk membersihkan dan menstrukturkan data OCR
    menggunakan logika spasial dan regex.
    """
    gambar_asli = cv2.imread(path_gambar)
    if gambar_asli is None: return {}

    # Tahap 1: Pangkas Otomatis Berdasarkan Border
    gambar_untuk_dianalisis = pangkas_tabel_gizi_otomatis(path_gambar)
    
    # Tahap 2: Baca gambar (yang sudah dipangkas) dengan PSM 6
    print("INFO: Membaca tabel dengan mode PSM 6 untuk akurasi tinggi...")
    config = '--psm 6'
    ocr_dataframe = pytesseract.image_to_data(gambar_untuk_dianalisis, lang='ind+eng', output_type=pytesseract.Output.DATAFRAME, config=config)
    ocr_dataframe = ocr_dataframe[ocr_dataframe.conf > 40]

    # Tahap 3: Rekonstruksi Baris dan Ekstraksi (kode ini sama seperti sebelumnya)
    if ocr_dataframe.empty: return {}

    lines = {}
    for _, row in ocr_dataframe.iterrows():
        line_num = row['line_num']
        if line_num not in lines: lines[line_num] = []
        lines[line_num].append(row)

    reconstructed_lines = []
    for line_num in sorted(lines.keys()):
        lines[line_num].sort(key=lambda x: x['left'])
        reconstructed_lines.append(" ".join([str(word['text']) for word in lines[line_num]]))

    hasil_nutrisi = {}
    pola_nutrisi = {
        # Kunci: Nama standar, Value: Pola Regex untuk dicari
        'Lemak Total (Total Fat)': r'(lemak\s*total|total\s*fat)\s*(\d+\.?\d*\s*g)',
        'Lemak Jenuh (Saturated Fat)': r'(lemak\s*jenuh|saturated\s*fat)\s*(\d+\.?\d*\s*g)',
        'Lemak Trans (Trans Fat)': r'(lemak\s*trans|trans\s*fat)\s*(\d+\.?\d*\s*g)',
        'Kolesterol (Cholesterol)': r'(kolesterol|cholesterol)\s*(\d+\.?\d*\s*mg)',
        'Protein': r'(protein)\s*(\d+\.?\d*\s*g)',
        'Karbohidrat Total (Total Carbohydrate)': r'(karbohidrat\s*total|total\s*carbohydrate)\s*(\d+\.?\d*\s*g)',
        'Serat (Fiber)': r'(serat\s*pangan|dietary\s*fiber)\s*(\d+\.?\d*\s*g)',
        'Gula (Sugar)': r'(gula|sugars|sugar)\s*(\d+\.?\d*\s*g)',
        'Natrium (Sodium)': r'(natrium|sodium)\s*(\d+\.?\d*\s*mg)'
    }
    for line in reconstructed_lines:
        for nama_nutrisi, pola in pola_nutrisi.items():
            match = re.search(pola, line, re.IGNORECASE)
            if match:
                nilai_kotor = match.group(2)
                nilai_bersih = bersihkan_nilai_gizi(nilai_kotor)
                hasil_nutrisi[nama_nutrisi] = nilai_bersih
                break
    
    return hasil_nutrisi

def get_catatan_gizi(nutrisi, nilai):
    """
    Memberikan catatan gizi (Rendah, Sedang, Tinggi) berdasarkan
    standar Kemenkes RI & WHO.
    """
    catatan = ""
    # Acuan batas harian (100%)
    batas_gula_harian = 50  # gram
    batas_natrium_harian = 2000  # mg
    batas_lemak_jenuh_harian = 20  # gram
    batas_lemak_total_harian = 67 # gram

    # Hitung persentase dari batas harian
    persentase = 0
    if 'Gula' in nutrisi:
        persentase = (nilai / batas_gula_harian) * 100
    elif 'Natrium' in nutrisi:
        persentase = (nilai / batas_natrium_harian) * 100
    elif 'Lemak Jenuh' in nutrisi:
        persentase = (nilai / batas_lemak_jenuh_harian) * 100
    elif 'Lemak Total' in nutrisi:
        persentase = (nilai / batas_lemak_total_harian) * 100
    
    # Berikan label berdasarkan persentase
    if persentase > 0:
        if persentase >= 20:
            catatan = f"🔴 TINGGI ({persentase:.0f}% dari harian)"
        elif persentase >= 6:
            catatan = f"🟡 SEDANG ({persentase:.0f}% dari harian)"
        else:
            catatan = f"🟢 RENDAH ({persentase:.0f}% dari harian)"
            
    return catatan