"""CLI verifikasi ijazah.

Contoh:
  # 1) Mode crop (sesuai dataset): potongan area nomor + area tanda tangan
  python main.py --number data/Nomor_Ijazah/01_HighQuality_Enhanced.jpg \\
                 --signature data/Tanda_Tangan/01_HighQuality_Enhanced.jpg

  # 2) Mode batch: semua pasangan file bernama sama di dua folder
  python main.py --batch data

  # 3) Mode citra ijazah utuh: ROI diberikan sebagai pecahan x,y,w,h (0-1)
  python main.py --image ijazah_001.jpg --number-roi 0.15,0.20,0.55,0.08 --signature-roi 0.60,0.75,0.30,0.15
"""
import argparse
import glob
import os
import sys

from ijazah_verifier import preprocessing as P
from ijazah_verifier.pipeline import verify_crops, verify_ijazah


def parse_box(s):
    if s is None:
        return None
    x, y, w, h = (float(v) for v in s.split(","))
    return x, y, w, h


def save_debug(sig, path):
    import cv2
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    cv2.imwrite(path, sig.binary)


def main():
    ap = argparse.ArgumentParser(description="Verifikasi ijazah: OCR nomor + deteksi tanda tangan")
    ap.add_argument("--number", help="citra area nomor ijazah (mode crop)")
    ap.add_argument("--signature", help="citra area tanda tangan (mode crop)")
    ap.add_argument("--image", help="citra ijazah utuh (mode full)")
    ap.add_argument("--number-roi", help="x,y,w,h pecahan untuk area nomor (mode full)")
    ap.add_argument("--signature-roi", help="x,y,w,h pecahan untuk area tanda tangan (mode full)")
    ap.add_argument("--batch", help="folder berisi Nomor_Ijazah/ dan Tanda_Tangan/")
    ap.add_argument("--enhancement", default=P.DEFAULT_NUMBER_ENHANCEMENT, choices=list(P.ENHANCEMENTS),
                    help="metode enhancement area nomor (default: %(default)s)")
    ap.add_argument("--debug-dir", help="simpan citra biner tanda tangan ke folder ini")
    a = ap.parse_args()

    if a.batch:
        for n in sorted(glob.glob(os.path.join(a.batch, "Nomor_Ijazah", "*.jpg"))):
            s = os.path.join(a.batch, "Tanda_Tangan", os.path.basename(n))
            if not os.path.exists(s):
                print(f"[lewati] pasangan tanda tangan tidak ada: {s}", file=sys.stderr)
                continue
            v = verify_crops(n, s, a.enhancement)
            print(f"== {os.path.basename(n)}\n{v.report()}\n")
            if a.debug_dir:
                save_debug(v.signature, os.path.join(a.debug_dir, "sig_" + os.path.basename(n)))
    elif a.image:
        v = verify_ijazah(a.image, parse_box(a.number_roi), parse_box(a.signature_roi), a.enhancement)
        print(v.report())
        if a.debug_dir:
            save_debug(v.signature, os.path.join(a.debug_dir, "sig_" + os.path.basename(a.image)))
    elif a.number and a.signature:
        v = verify_crops(a.number, a.signature, a.enhancement)
        print(v.report())
        if a.debug_dir:
            save_debug(v.signature, os.path.join(a.debug_dir, "sig_" + os.path.basename(a.signature)))
    else:
        ap.error("pilih salah satu: --number & --signature, --image, atau --batch")


if __name__ == "__main__":
    main()
