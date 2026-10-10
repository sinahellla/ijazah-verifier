"""Pipeline utama:
Citra -> Grayscale -> Enhancement -> [Area Nomor | Area Tanda Tangan] -> Hasil Verifikasi
"""
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np

from . import preprocessing as P
from .number_ocr import NumberResult, read_number
from .signature import SignatureResult, detect_signature

Box = Tuple[float, float, float, float]  # (x, y, w, h) sebagai pecahan 0-1 dari citra


@dataclass
class Verification:
    number: NumberResult
    signature: SignatureResult

    def report(self) -> str:
        nomor = self.number.number or "TIDAK TERBACA"
        return f"Nomor Ijazah : {nomor}\nTanda Tangan : {self.signature.label}"


def crop_fraction(img: np.ndarray, box: Optional[Box]) -> np.ndarray:
    """Potong ROI dari koordinat pecahan; box=None -> seluruh citra."""
    if box is None:
        return img
    h, w = img.shape[:2]
    x, y, bw, bh = box
    return img[int(y * h):int((y + bh) * h), int(x * w):int((x + bw) * w)]


def verify_gray(gray_number: np.ndarray, gray_sig: np.ndarray,
                enhancement: str = P.DEFAULT_NUMBER_ENHANCEMENT) -> Verification:
    return Verification(read_number(gray_number, enhancement), detect_signature(gray_sig))


def verify_ijazah(path: str, number_box: Optional[Box], sig_box: Optional[Box],
                  enhancement: str = P.DEFAULT_NUMBER_ENHANCEMENT) -> Verification:
    """Mode citra ijazah utuh: ROI diambil dari koordinat pecahan."""
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(path)
    g = P.global_enhancement(P.to_gray(img))          # grayscale + enhancement global
    return verify_gray(crop_fraction(g, number_box), crop_fraction(g, sig_box), enhancement)


def verify_crops(number_path: str, sig_path: str,
                 enhancement: str = P.DEFAULT_NUMBER_ENHANCEMENT) -> Verification:
    """Mode crop: dataset sudah berisi potongan area nomor & area tanda tangan."""
    out = []
    for p in (number_path, sig_path):
        img = cv2.imread(p)
        if img is None:
            raise FileNotFoundError(p)
        out.append(P.global_enhancement(P.to_gray(img)))
    return verify_gray(out[0], out[1], enhancement)
