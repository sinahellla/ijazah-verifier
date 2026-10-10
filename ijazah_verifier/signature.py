"""Area tanda tangan: thresholding -> morphology -> signature detection."""
from dataclasses import dataclass

import cv2
import numpy as np

# Kontras minimum (selisih gelap terhadap latar, skala 0-255) agar suatu piksel
# dianggap tinta. Tanpa lantai ini, Otsu pada area KOSONG akan tetap memisahkan
# derau watermark menjadi "foreground" dan menghasilkan false positive.
MIN_CONTRAST = 45
# Ambang keputusan (persen luas ROI)
MIN_INK_RATIO = 0.5       # total piksel tinta
MIN_COMPONENT_RATIO = 0.3  # komponen terhubung terbesar


@dataclass
class SignatureResult:
    present: bool
    ink_ratio: float          # % piksel tinta setelah morphology
    largest_ratio: float      # % luas komponen terbesar
    otsu: float
    threshold: float
    binary: np.ndarray        # citra biner akhir (untuk debug/visualisasi)

    @property
    def label(self) -> str:
        return "PRESENT" if self.present else "ABSENT"


def threshold_ink(g: np.ndarray):
    """Thresholding: 'kegelapan relatif terhadap latar' + Otsu dengan lantai kontras."""
    g = cv2.medianBlur(g, 3)
    bg = cv2.medianBlur(cv2.dilate(g, np.ones((25, 25), np.uint8)), 51)  # estimasi latar
    diff = cv2.subtract(bg, g)
    otsu, _ = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thr = max(otsu, MIN_CONTRAST)
    return (diff > thr).astype(np.uint8) * 255, float(otsu), float(thr)


def clean_morphology(bw: np.ndarray) -> np.ndarray:
    """Opening (buang bintik derau) lalu Closing (sambung goresan putus)."""
    bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    return cv2.morphologyEx(bw, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))


def detect_signature(roi_gray: np.ndarray) -> SignatureResult:
    bw, otsu, thr = threshold_ink(roi_gray)
    bw = clean_morphology(bw)
    h, w = bw.shape
    n, _, stats, _ = cv2.connectedComponentsWithStats(bw)
    largest = int(stats[1:, cv2.CC_STAT_AREA].max()) if n > 1 else 0
    ink_ratio = float((bw > 0).mean() * 100)
    largest_ratio = largest / (h * w) * 100
    present = ink_ratio >= MIN_INK_RATIO and largest_ratio >= MIN_COMPONENT_RATIO
    return SignatureResult(present, round(ink_ratio, 3), round(largest_ratio, 3), otsu, thr, bw)
