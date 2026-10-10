"""Visualisasi pipeline per ijazah (panel gambar + nomor + status tanda tangan).

Jalankan:  python visualize.py          -> results/visualisasi/visualisasi_01.png ... _09.png
"""
import glob
import os

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ijazah_verifier import preprocessing as P
from ijazah_verifier.number_ocr import read_number
from ijazah_verifier.signature import clean_morphology, detect_signature, threshold_ink

NUM_DIR, SIG_DIR, OUT = "data/Nomor_Ijazah", "data/Tanda_Tangan", "results/visualisasi"


def main(enhancement=P.DEFAULT_NUMBER_ENHANCEMENT):
    os.makedirs(OUT, exist_ok=True)
    for i, nf in enumerate(sorted(glob.glob(f"{NUM_DIR}/*.jpg")), 1):
        sf = os.path.join(SIG_DIR, os.path.basename(nf))
        num_img, sig_img = cv2.imread(nf), cv2.imread(sf)
        g_num = P.global_enhancement(P.to_gray(num_img))
        g_sig = P.global_enhancement(P.to_gray(sig_img))

        enhanced = P.ENHANCEMENTS[enhancement](g_num)
        num = read_number(g_num, enhancement)
        sig = detect_signature(g_sig)
        thr, _, _ = threshold_ink(g_sig)

        panels = [("Citra area nomor", cv2.cvtColor(num_img, cv2.COLOR_BGR2RGB)),
                  ("Grayscale + enhancement global", g_num),
                  (f"Enhancement nomor:\n{enhancement}", enhanced),
                  ("Citra area tanda tangan", cv2.cvtColor(sig_img, cv2.COLOR_BGR2RGB)),
                  ("Thresholding", thr),
                  ("Morphology (open + close)", clean_morphology(thr))]
        fig, axes = plt.subplots(2, 3, figsize=(15, 8), dpi=160)
        fig.suptitle(f"Verifikasi Ijazah {i} - {os.path.basename(nf)}", fontsize=14, fontweight="bold")
        for ax, (title, im) in zip(axes.flat, panels):
            ax.imshow(im, cmap="gray" if im.ndim == 2 else None)
            ax.set_title(title, fontsize=10)
            ax.axis("off")
        fig.text(0.03, 0.015,
                 f"Nomor Ijazah : {num.number or 'TIDAK TERBACA'}\n"
                 f"Tanda Tangan : {sig.label}  (tinta {sig.ink_ratio}% | komponen terbesar {sig.largest_ratio}%)",
                 fontsize=12, va="bottom", family="monospace")
        fig.tight_layout(rect=[0, 0.08, 1, 0.94])
        fig.savefig(f"{OUT}/visualisasi_{i:02d}.png")
        plt.close(fig)
        print(f"[{i}] {os.path.basename(nf)} -> {num.number or 'TIDAK TERBACA'} | {sig.label}")


if __name__ == "__main__":
    main()
