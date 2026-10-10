# Hasil evaluasi CER

Ground truth: `571012022000056`

## A. Data asli (9 citra)

| Peringkat | Metode enhancement | Mean CER | Exact match | Tesseract error |
|---|---|---|---|---|
| 1 | none (grayscale saja) | 0.0000 | 9/9 | 0 |
| 2 | Contrast Stretching | 0.0000 | 9/9 | 0 |
| 3 | Brightness Adjustment | 0.0000 | 9/9 | 0 |
| 4 | Gamma Correction | 0.0000 | 9/9 | 0 |
| 5 | Median + Stretching | 0.0000 | 9/9 | 0 |
| 6 | Gaussian + Stretching | 0.0000 | 9/9 | 0 |
| 7 | Median + CLAHE | 0.0000 | 9/9 | 0 |
| 8 | Median + Stretch + Unsharp | 0.0000 | 9/9 | 0 |
| 9 | Background Normalization | 0.0000 | 9/9 | 0 |
| 10 | CLAHE | 0.2222 | 7/9 | 2 |
| 11 | Histogram Equalization | 1.0000 | 0/9 | 0 |

## B. Stress test sintetis (63 citra = 9 x 7 degradasi)

| Peringkat | Metode enhancement | Mean CER | Exact match | Tesseract error |
|---|---|---|---|---|
| 1 | Gaussian + Stretching | 0.2783 | 38/63 | 0 |
| 2 | Background Normalization | 0.2984 | 34/63 | 0 |
| 3 | Median + Stretching | 0.3407 | 35/63 | 0 |
| 4 | Gamma Correction | 0.3704 | 35/63 | 0 |
| 5 | Brightness Adjustment | 0.3905 | 30/63 | 0 |
| 6 | none (grayscale saja) | 0.4180 | 32/63 | 0 |
| 7 | Contrast Stretching | 0.4212 | 29/63 | 0 |
| 8 | Median + CLAHE | 0.4307 | 34/63 | 0 |
| 9 | CLAHE | 0.4328 | 32/63 | 0 |
| 10 | Median + Stretch + Unsharp | 0.4339 | 31/63 | 0 |
| 11 | Histogram Equalization | 1.0000 | 0/63 | 0 |

## C. Deteksi tanda tangan

Akurasi: **18/18**

| Citra | Jenis | Prediksi | Ink % | Komponen terbesar % |
|---|---|---|---|---|
| 01_HighQuality_Enhanced.jpg | asli (ada TTD) | PRESENT | 2.546 | 1.834 |
| 01_HighQuality_Enhanced.jpg | sintetis (TTD dihapus) | ABSENT | 0.0 | 0.0 |
| 02_LowContrast.jpg | asli (ada TTD) | PRESENT | 2.811 | 2.029 |
| 02_LowContrast.jpg | sintetis (TTD dihapus) | ABSENT | 0.0 | 0.0 |
| 03_Blurred.jpg | asli (ada TTD) | PRESENT | 3.301 | 2.329 |
| 03_Blurred.jpg | sintetis (TTD dihapus) | ABSENT | 0.0 | 0.0 |
| 04_HighNoise.jpg | asli (ada TTD) | PRESENT | 2.456 | 1.77 |
| 04_HighNoise.jpg | sintetis (TTD dihapus) | ABSENT | 0.0 | 0.0 |
| 05_LowResolution_Upsampled.jpg | asli (ada TTD) | PRESENT | 2.719 | 1.954 |
| 05_LowResolution_Upsampled.jpg | sintetis (TTD dihapus) | ABSENT | 0.0 | 0.0 |
| 06_Faded_Underexposed.jpg | asli (ada TTD) | PRESENT | 2.382 | 1.723 |
| 06_Faded_Underexposed.jpg | sintetis (TTD dihapus) | ABSENT | 0.0 | 0.0 |
| 07_ColorShift_WarmTint.jpg | asli (ada TTD) | PRESENT | 2.404 | 1.731 |
| 07_ColorShift_WarmTint.jpg | sintetis (TTD dihapus) | ABSENT | 0.0 | 0.0 |
| 08_JPEGCompression_Artifacts.jpg | asli (ada TTD) | PRESENT | 2.573 | 1.853 |
| 08_JPEGCompression_Artifacts.jpg | sintetis (TTD dihapus) | ABSENT | 0.0 | 0.0 |
| 09_CombinedDegradation.jpg | asli (ada TTD) | PRESENT | 2.741 | 1.969 |
| 09_CombinedDegradation.jpg | sintetis (TTD dihapus) | ABSENT | 0.0 | 0.0 |
