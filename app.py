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
    berikan_kesimpulan_komposisi,
    ekstrak_data_dengan_koordinat,
    get_catatan_gizi,
    tentukan_grade_indonesia
)

print("INFO: Aplikasi NutriSnap sedang memuat...")

def process_image(input_image, jenis_produk):
    """
    Fungsi utama yang akan dijalankan oleh Gradio.
    Menerima gambar input dan mengembalikan seluruh laporan sebagai satu teks.
    """
    # Gradio menyimpan gambar upload sementara, kita butuh path-nya
    path_gambar = input_image

    # --- Analisis 1: Komposisi Bahan (Kualitatif) ---
    laporan1_header = "[ANALISIS 1: Komposisi Bahan (Kualitatif)]\n"
    gambar_komposisi, bahasa_komposisi = temukan_dan_pangkas_komposisi(path_gambar)
    teks_komposisi = pytesseract.image_to_string(gambar_komposisi, lang='ind+eng')
    skor, alasan = analisis_komposisi(teks_komposisi, bahasa_komposisi)
    kesimpulan_kualitatif, _ = berikan_kesimpulan_komposisi(skor)
    
    # --- Analisis 2: Tabel Nilai Gizi (Kuantitatif) ---
    laporan2_header = "\n[ANALISIS 2: Tabel Nilai Gizi (Kuantitatif dengan PSM 6)]\n"
    data_gizi = ekstrak_data_dengan_koordinat(path_gambar) 
    
    info_produk = {'jenis': jenis_produk} 
    grade_final, deskripsi_final = tentukan_grade_indonesia(data_gizi, info_produk)

    # --- Gabungkan Semua Menjadi Satu Laporan Teks ---
    laporan_final = "========================================\n"
    laporan_final += "       LAPORAN GABUNGAN NUTRISNAP       \n"
    laporan_final += "========================================\n"
    laporan_final += f"GRADE KESEHATAN: {grade_final}\n"
    laporan_final += f"DESKRIPSI: {deskripsi_final}\n"
    
    laporan_final += "\n--- Rincian Kuantitatif (per 100g/ml) ---\n"
    if data_gizi:
        for nutrisi, nilai in data_gizi.items():
            satuan = 'g'
            if 'Natrium' in nutrisi or 'Kolesterol' in nutrisi:
                satuan = 'mg'
            laporan_final += f"- {nutrisi}: {nilai}{satuan}\n"
    else:
        laporan_final += "Tidak ada data kuantitatif yang berhasil diekstrak.\n"
    laporan_final += f"\n--- Analisis Komposisi Bahan (Skor: {skor}) ---\n"
    if alasan:
        for detail in alasan: 
            laporan_final += f"- {detail}\n"
    else: 
        laporan_final += "Tidak ada detail spesifik yang ditemukan.\n"
    
    laporan_final += "========================================"
    
    return laporan_final

# Membuat Antarmuka Gradio
demo = gr.Interface(
    fn=process_image,
    inputs=[
        gr.Image(type="filepath", label="Upload Gambar Kemasan"),
        gr.Radio(["padat", "cair"], label="Jenis Produk", value="padat")
    ],
    outputs=gr.Textbox(label="Hasil Analisis NutriSnap", lines=25),
    title="🍓 NutriSnap",
    description="Demo Analisis Gizi Otomatis. Upload gambar kemasan makanan, pilih jenis produknya (padat/cair), lalu lihat hasilnya.",
    allow_flagging="never"
)

# Menjalankan demo
if __name__ == "__main__":
    demo.launch()