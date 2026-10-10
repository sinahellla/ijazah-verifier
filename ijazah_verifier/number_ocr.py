"""Area nomor ijazah: enhancement -> OCR (Tesseract) -> ekstraksi nomor."""
import os
import re
from dataclasses import dataclass

import cv2
import numpy as np
import pytesseract

from . import preprocessing as P

if os.environ.get("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]

# Whitelist: digit + huruf label "Nomor ijazah:" agar baris utuh tetap terbaca
# (label tidak ikut ke hasil karena diambil hanya runtun digit terpanjang).
_TESS_CONFIG = "--psm 7 -c tessedit_char_whitelist=0123456789Nomorijazah:"
MIN_DIGITS = 6


@dataclass
class NumberResult:
    number: str          # "" bila tidak terbaca
    raw: str             # keluaran mentah Tesseract
    error: bool = False  # True bila Tesseract gagal/crash


def prepare_for_ocr(g: np.ndarray, scale: int = 2, pad: int = 20) -> np.ndarray:
    """Upscale (membantu glyph kecil) + padding tepi (Tesseract butuh margin)."""
    g = cv2.resize(g, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    return cv2.copyMakeBorder(g, pad, pad, pad, pad, cv2.BORDER_REPLICATE)


def read_number(roi_gray: np.ndarray, enhancement: str = P.DEFAULT_NUMBER_ENHANCEMENT) -> NumberResult:
    """ROI nomor (grayscale) -> enhancement -> OCR -> nomor ijazah."""
    enhanced = P.ENHANCEMENTS[enhancement](roi_gray)
    img = prepare_for_ocr(enhanced)
    try:
        raw = pytesseract.image_to_string(img, config=_TESS_CONFIG)
    except Exception:  # pytesseract.TesseractError / RuntimeError
        return NumberResult("", "", error=True)
    runs = re.findall(r"\d+", raw)
    best = max(runs, key=len) if runs else ""
    return NumberResult(best if len(best) >= MIN_DIGITS else "", raw.strip())
