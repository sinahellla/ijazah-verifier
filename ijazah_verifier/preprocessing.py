"""Grayscale + metode image enhancement.

Semua fungsi menerima & mengembalikan citra grayscale uint8.
"""
import cv2
import numpy as np


def to_gray(img: np.ndarray) -> np.ndarray:
    """Konversi BGR -> grayscale (sudah grayscale dibiarkan)."""
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# ---------------------------------------------------------------- enhancement
def none(g):
    return g


def hist_eq(g):
    """Histogram Equalization global."""
    return cv2.equalizeHist(g)


def clahe(g, clip=2.0, tile=8):
    """Contrast Limited Adaptive Histogram Equalization."""
    return cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile)).apply(g)


def contrast_stretch(g, lo_pct=1, hi_pct=99):
    """Peregangan kontras berbasis persentil (robust terhadap outlier)."""
    lo, hi = np.percentile(g, (lo_pct, hi_pct))
    out = (g.astype(np.float32) - lo) * 255.0 / max(hi - lo, 1.0)
    return np.clip(out, 0, 255).astype(np.uint8)


def brightness_adjustment(g, beta=25):
    """Brightness Adjustment: tambah konstanta beta ke setiap piksel."""
    return cv2.convertScaleAbs(g, alpha=1.0, beta=beta)


def gamma_correction(g, gamma=0.6):
    lut = np.array([(i / 255.0) ** gamma * 255 for i in range(256)], np.uint8)
    return cv2.LUT(g, lut)


def median_denoise(g, k=3):
    return cv2.medianBlur(g, k)


def gaussian_denoise(g, k=3):
    return cv2.GaussianBlur(g, (k, k), 0)


def unsharp(g, amount=1.5, sigma=2.0):
    blur = cv2.GaussianBlur(g, (0, 0), sigma)
    return cv2.addWeighted(g, 1 + amount, blur, -amount, 0)


def background_normalize(g, dil=9, blur=31):
    """Hilangkan latar/watermark: |g - estimasi latar|, lalu invert + normalisasi."""
    bg = cv2.medianBlur(cv2.dilate(g, np.ones((dil, dil), np.uint8)), blur)
    out = 255 - cv2.absdiff(g, bg)
    return cv2.normalize(out, None, 0, 255, cv2.NORM_MINMAX)


# Registry metode enhancement yang dibandingkan pada evaluasi CER.
ENHANCEMENTS = {
    "none (grayscale saja)": none,
    "Histogram Equalization": hist_eq,
    "CLAHE": clahe,
    "Contrast Stretching": contrast_stretch,
    "Brightness Adjustment": brightness_adjustment,
    "Gamma Correction": gamma_correction,
    "Median + Stretching": lambda g: contrast_stretch(median_denoise(g)),
    "Gaussian + Stretching": lambda g: contrast_stretch(gaussian_denoise(g)),
    "Median + CLAHE": lambda g: clahe(median_denoise(g)),
    "Median + Stretch + Unsharp": lambda g: unsharp(contrast_stretch(median_denoise(g))),
    "Background Normalization": lambda g: background_normalize(median_denoise(g)),
}

DEFAULT_NUMBER_ENHANCEMENT = "Gaussian + Stretching"  # terbaik pada stress test CER (lihat results/hasil_evaluasi.md)


def global_enhancement(g):
    """Tahap 'Image Enhancement' global (sebelum ROI dipisah): denoise ringan."""
    return median_denoise(g, 3)
