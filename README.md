# Verifikasi Ijazah: OCR Nomor Ijazah + Deteksi Tanda Tangan

Prototipe miniproject Pengolahan Citra Digital.

```
Input : ijazah_001.jpg
Output: Nomor Ijazah : 571012022000056
        Tanda Tangan : PRESENT
```

## Pipeline

```
Citra Ijazah -> Grayscale -> Image Enhancement (global: median 3x3)
   -> Area Nomor : Enhancement -> OCR (Tesseract) -> Nomor Ijazah
   -> Area TTD   : Thresholding -> Morphology -> Signature Detection
   -> Hasil Verifikasi
```

## Cara menjalankan

1. Instal Tesseract OCR
   - Ubuntu/Debian: `sudo apt install tesseract-ocr`
   - macOS: `brew install tesseract`
   - Windows: unduh installer UB Mannheim; bila perlu set `TESSERACT_CMD`, mis. `set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`
2. Instal dependensi Python (disarankan di virtualenv):
   ```
   pip install -r requirements.txt
   ```
3. Jalankan (dari root repo):
   ```bash
   # satu pasang crop (area nomor + area tanda tangan)
   python main.py --number data/Nomor_Ijazah/01_HighQuality_Enhanced.jpg \
                  --signature data/Tanda_Tangan/01_HighQuality_Enhanced.jpg

   # semua pasangan di folder data/
   python main.py --batch data

   # citra ijazah utuh; ROI = pecahan x,y,w,h (0-1) dari citra
   python main.py --image ijazah_001.jpg --number-roi 0.15,0.20,0.55,0.08 --signature-roi 0.60,0.75,0.30,0.15
   ```
   Opsi: `--enhancement "<nama metode>"` (default `Gaussian + Stretching`), `--debug-dir` (simpan citra biner tanda tangan).
4. Visualisasi panel per ijazah (hasil di `results/visualisasi/`):
   ```bash
   python visualize.py
   ```
5. Evaluasi CER dan deteksi tanda tangan (sekitar 8 menit di 1 CPU):
   ```bash
   python evaluate.py
   ```
   Hasil: `results/hasil_evaluasi.md`, `results/cer_per_image.csv`, `results/cer_comparison.png`.

## Metode

**Grayscale**: konversi BGR ke satu kanal intensitas (`cv2.cvtColor`).

**Enhancement global**: median filter 3x3 untuk meredam noise impulsif sebelum ROI dipisah.

**Area nomor**
- Enhancement ROI (11 metode dibandingkan, lihat `preprocessing.py`): Histogram Equalization, CLAHE, Contrast Stretching (persentil 1-99), Brightness Adjustment, Gamma, Gaussian/Median + Stretching, Median + CLAHE, + Unsharp, Background Normalization.
- OCR: citra di-upscale 2x, diberi padding, lalu Tesseract (`--psm 7`, whitelist digit dan huruf label). Nomor diambil dari runtun digit terpanjang.

**Area tanda tangan**
- Thresholding: kegelapan relatif terhadap latar (selisih dengan estimasi latar), Otsu dengan lantai kontras mutlak (45). Lantai ini perlu karena Otsu murni pada area kosong tetap memisahkan derau watermark sebagai foreground.
- Morphology: opening 3x3 (buang bintik) lalu closing 7x7 (sambung goresan).
- Deteksi: PRESENT bila piksel tinta >= 0,5% luas ROI dan komponen terhubung terbesar >= 0,3%.

**CER** = (S + D + I) / N, dengan jarak Levenshtein terhadap ground truth `571012022000056`. Hasil OCR kosong dihitung CER 1.

## Hasil dan analisis CER

| Metode | CER data asli (9 citra) | CER stress test (63 citra) |
|---|---|---|
| Gaussian + Stretching | 0,0000 | **0,2783** |
| Background Normalization | 0,0000 | 0,2984 |
| Median + Stretching | 0,0000 | 0,3407 |
| Gamma Correction | 0,0000 | 0,3704 |
| Brightness Adjustment | 0,0000 | 0,3905 |
| Grayscale saja | 0,0000 | 0,4180 |
| Contrast Stretching | 0,0000 | 0,4212 |
| Median + CLAHE | 0,0000 | 0,4307 |
| CLAHE | 0,2222 | 0,4328 |
| Median + Stretch + Unsharp | 0,0000 | 0,4339 |
| Histogram Equalization | 1,0000 | 1,0000 |

**Kesimpulan:** metode paling efektif adalah **Gaussian blur 3x3 + Contrast Stretching**, dengan CER stress test terendah (0,2783) dan 38/63 nomor terbaca tepat. Alasannya:
- Stretching memperlebar jarak intensitas teks terhadap latar tanpa mengubah bentuk histogram, jadi pola watermark tidak ikut menguat.
- Gaussian blur meredam noise sebelum diregangkan, sehingga noise tidak ikut diperkuat. Ini terlihat dari Contrast Stretching saja (0,4212), yang lebih buruk dari kombinasi dengan Gaussian.
- Histogram Equalization gagal total (CER 1,0): ia meratakan histogram sehingga pola watermark kuning menjadi sekuat tinta dan OCR kosong. CLAHE gagal pada 2 citra asli (01 dan 07) karena Tesseract mengembalikan error pada citra hasil CLAHE tersebut (bukan salah baca); penyebab pastinya belum saya selidiki.
- Brightness Adjustment (+25) memberi CER 0 pada data asli tetapi hanya peringkat 5 pada stress test (0,3905), karena hanya menggeser intensitas tanpa melebarkan kontras atau meredam noise.
- Unsharp mask memberi CER stress test terburuk di antara metode yang berfungsi (0,4339); dugaan saya karena mempertajam noise, tetapi ini belum diuji.

**Batasan yang perlu dicatat:**
- Pada 9 citra asli, 8 metode seri (CER 0), jadi data asli tidak bisa membedakan mereka. Peringkat ditentukan oleh stress test dengan degradasi **sintetis** (noise, blur, kontras rendah).
- Selisih antar peringkat teratas kecil (38, 34, 35 dari 63) dan dihitung dari satu ground truth tunggal pada satu jenis font, jadi jangan dibaca sebagai selisih yang pasti signifikan.
- Deteksi tanda tangan 18/18 benar, tetapi 9 sampel "ABSENT" dibuat sintetis (tinta dihapus lalu di-inpaint) karena dataset tidak punya contoh tanpa tanda tangan. Pada scan nyata (noda, stempel, garis) hasilnya bisa berbeda.
- Mode citra utuh (`--image`) belum divalidasi pada scan ijazah utuh; ROI harus diatur sesuai layout ijazah.

## Struktur

```
main.py                  CLI
evaluate.py              evaluasi CER + tanda tangan
visualize.py             panel visualisasi per ijazah
ijazah_verifier/         preprocessing, number_ocr, signature, metrics, pipeline
data/                    dataset (Nomor_Ijazah, Tanda_Tangan)
results/                 keluaran evaluasi
```
