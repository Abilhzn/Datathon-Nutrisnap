import gradio as gr
import cv2
import pytesseract
import pandas as pd
import re
import os

# Mengimpor semua fungsi dari "library" yang kita buat
from nutrisnap_utils import (
    temukan_dan_pangkas_komposisi,
    analisis_komposisi,
    berikan_kesimpulan,
    ekstrak_data_dengan_koordinat,
    get_catatan_gizi
)

print("INFO: Aplikasi NutriSnap sedang memuat...")

def process_image(input_image):
    """
    Fungsi utama yang akan dijalankan oleh Gradio.
    Menerima gambar input dan mengembalikan seluruh laporan sebagai satu teks.
    """
    # Gradio menyimpan gambar upload sementara, kita butuh path-nya
    path_gambar = input_image.name

    # --- Analisis 1: Komposisi Bahan (Kualitatif) ---
    laporan1_header = "[ANALISIS 1: Komposisi Bahan (Kualitatif)]\n"
    gambar_komposisi, bahasa_komposisi = temukan_dan_pangkas_komposisi(path_gambar)
    teks_komposisi = pytesseract.image_to_string(gambar_komposisi, lang='ind+eng')
    skor, alasan = analisis_komposisi(teks_komposisi, bahasa_komposisi)
    kesimpulan, deskripsi = berikan_kesimpulan(skor)
    
    # --- Analisis 2: Tabel Nilai Gizi (Kuantitatif) ---
    laporan2_header = "\n[ANALISIS 2: Tabel Nilai Gizi (Kuantitatif dengan PSM 6)]\n"
    data_gizi = ekstrak_data_dengan_koordinat(path_gambar) 
    
    # --- Gabungkan Semua Menjadi Satu Laporan Teks ---
    laporan_final = "========================================\n"
    laporan_final += "       LAPORAN GABUNGAN NUTRISNAP       \n"
    laporan_final += "========================================\n"
    laporan_final += f"KESIMPULAN UMUM: {kesimpulan} ({deskripsi})\n"
    laporan_final += f"SKOR KUALITATIF (dari bahan): {skor}\n"
    
    laporan_final += "\n--- Rincian Kualitatif (dari Komposisi) ---\n"
    if alasan:
        for detail in alasan: laporan_final += f"- {detail}\n"
    else: laporan_final += "Tidak ada detail spesifik yang ditemukan.\n"
            
    laporan_final += "\n--- Rincian Kuantitatif (dari Tabel Gizi) ---\n"
    if data_gizi:
        for nutrisi, nilai in data_gizi.items():
            # Kita panggil fungsi get_catatan_gizi di sini
            catatan = get_catatan_gizi(nutrisi, nilai)
            satuan = 'g' if 'Natrium' not in nutrisi else 'mg'
            laporan_final += f"- {nutrisi}: {nilai}{satuan} per saji {catatan}\n"
    else:
        laporan_final += "Tidak ada data kuantitatif yang berhasil diekstrak.\n"
    laporan_final += "========================================"
    
    return laporan_final

# Membuat Antarmuka Gradio
demo = gr.Interface(
    fn=process_image,
    inputs=gr.Image(type="file", label="Upload Gambar Kemasan"),
    outputs=gr.Textbox(label="Hasil Analisis NutriSnap", lines=25),
    title="🍓 NutriSnap",
    description="Demo Analisis Gizi Otomatis. Upload gambar kemasan makanan untuk melihat analisis kualitatif dari komposisi dan analisis kuantitatif dari tabel nilai gizi.",
    allow_flagging="never"
)

# Menjalankan demo
if __name__ == "__main__":
    demo.launch()