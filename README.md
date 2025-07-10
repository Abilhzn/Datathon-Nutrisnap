# NutriSnap: Analisis Gizi Instan dari Kemasan Makanan

<p align="center">
  <a href="https://huggingface.co/spaces/abilhzn/NutriSnap-Demo">
    <img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-yellow" alt="Hugging Face Spaces">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-BSD_3--Clause-blue.svg" alt="License">
  </a>
  <img src="https://img.shields.io/badge/python-3.10-blue.svg" alt="Python">
</p>

**NutriSnap** adalah sebuah prototipe aplikasi cerdas yang dirancang untuk memecahkan masalah informasi gizi yang rumit pada kemasan makanan. Hanya dengan satu foto, NutriSnap dapat secara otomatis "membaca" dan menganalisis label produk untuk memberikan laporan kesehatan yang mudah dipahami.

## Fitur Utama

- **Deteksi & Pangkas Otomatis**: Secara cerdas menemukan dan mengisolasi area "Komposisi" dan "Tabel Nilai Gizi" dari gambar kemasan yang ramai.
- **Analisis Ganda**: Memberikan dua lapis analisis:
  1.  **Kualitatif**: Menghitung skor kesehatan berdasarkan baik/buruknya bahan-bahan dalam daftar komposisi.
  2.  **Kuantitatif**: Mengekstrak nilai gram/mg nutrisi penting (Gula, Garam, Lemak) dan membandingkannya dengan standar Angka Kecukupan Gizi (AKG) harian.
- **Dukungan Bilingual**: Mampu memahami label dalam Bahasa Indonesia ("Komposisi", "Gula") dan Bahasa Inggris ("Ingredients", "Sugar").
- **Antarmuka Interaktif**: Dibangun dengan Gradio dan di-hosting di Hugging Face Spaces untuk demo yang mudah diakses siapa saja.

## Demo Live

Coba langsung aplikasi NutriSnap di Hugging Face Spaces!

**[➡️ Klik di sini untuk mencoba NutriSnap](https://huggingface.co/spaces/abilhzn/NutriSnap-Demo)**

## Teknologi yang Digunakan

Proyek ini dibangun menggunakan serangkaian teknologi modern di bidang AI dan pengembangan perangkat lunak:

- **Python 3.13**
- **OpenCV**: Untuk semua tugas pemrosesan gambar, seperti deteksi kontur dan pangkas otomatis.
- **Tesseract (via `pytesseract`)**: Sebagai mesin Optical Character Recognition (OCR) untuk mengubah gambar teks menjadi data string.
- **Pandas**: Untuk memanipulasi data hasil OCR yang berbentuk tabel.
- **Gradio**: Untuk membangun antarmuka web yang cepat dan interaktif.
- **Hugging Face Spaces**: Sebagai platform untuk hosting dan deployment aplikasi.

## ⚙️ Instalasi & Penggunaan Lokal

Jika kamu ingin menjalankan proyek ini di komputermu sendiri:

1.  **Clone repositori ini:**
    ```bash
    git clone [https://github.com/NAMA_USER_GITHUB_KAMU/NAMA_REPO_KAMU.git](https://github.com/NAMA_USER_GITHUB_KAMU/NAMA_REPO_KAMU.git)
    cd NAMA_REPO_KAMU
    ```

2.  **Install dependensi sistem (Tesseract):**
    * Untuk Debian/Ubuntu:
        ```bash
        sudo apt-get install tesseract-ocr tesseract-ocr-ind tesseract-ocr-eng
        ```

3.  **Install dependensi Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Jalankan aplikasi:**
    ```bash
    python app.py
    ```
    Buka URL yang muncul di terminal (biasanya `http://127.0.0.1:7860`).

## 🗺️ Roadmap & Pengembangan di Masa Depan

NutriSnap saat ini adalah prototipe yang kuat. Rencana pengembangan selanjutnya meliputi:
- [ ] **Implementasi Model End-to-End**: Mengganti pipeline saat ini dengan model Document Understanding (seperti Donut atau LayoutLM) untuk akurasi yang lebih tinggi.
- [ ] **Analisis Berbasis LLM**: Menggunakan Large Language Models untuk pemahaman konteks bahan yang lebih mendalam dan pembersihan data OCR yang lebih cerdas.
- [ ] **Fitur Scan Barcode**: Mendapatkan informasi produk langsung dari database barcode.
- [ ] **Rekomendasi Personalisasi**: Memberikan saran produk alternatif yang lebih sehat berdasarkan profil pengguna (misal: alergi, preferensi diet).

## Kontribusi

Kontribusi, isu, dan permintaan fitur sangat diterima! Jangan ragu untuk membuka *issue* baru atau mengajukan *pull request*.

##  Lisensi

Proyek ini dilisensikan di bawah **Lisensi BSD 3-Clause**. Lihat file `LICENSE` untuk detail lengkap.
