"""Evaluasi: (1) CER tiap metode enhancement pada OCR nomor, (2) akurasi deteksi tanda tangan.

Dua skenario CER:
  A. data asli  : 9 citra bawaan dataset (sudah terdegradasi: low contrast, blur, noise, dst.)
  B. stress test: degradasi SINTETIS tambahan di atas 9 citra tsb (noise, blur, kontras rendah, kombinasi)
     agar perbedaan antar metode terlihat saat data asli sudah 'mudah' bagi semua metode.
Jalankan:  python evaluate.py
"""
import csv
import glob
from concurrent.futures import ProcessPoolExecutor
import os
import sys

os.environ.setdefault("OMP_THREAD_LIMIT", "1")  # 1 thread Tesseract per proses

import cv2
import numpy as np

from ijazah_verifier import preprocessing as P
from ijazah_verifier.metrics import cer
from ijazah_verifier.number_ocr import read_number
from ijazah_verifier.signature import detect_signature

GROUND_TRUTH = "571012022000056"   # nomor yang tercetak pada seluruh citra dataset
NUM_DIR, SIG_DIR, OUT = "data/Nomor_Ijazah", "data/Tanda_Tangan", "results"


# ------------------------------------------------------------ degradasi sintetis
def add_noise(g, sigma, rng):
    return np.clip(g.astype(np.float32) + rng.normal(0, sigma, g.shape), 0, 255).astype(np.uint8)


def add_blur(g, sigma):
    return cv2.GaussianBlur(g, (0, 0), sigma)


def low_contrast(g, alpha=0.35):
    return np.clip((g.astype(np.float32) - 128) * alpha + 128, 0, 255).astype(np.uint8)


STRESS = {
    "noise sigma=25": lambda g, r: add_noise(g, 25, r),
    "noise sigma=45": lambda g, r: add_noise(g, 45, r),
    "blur sigma=2.5": lambda g, r: add_blur(g, 2.5),
    "blur sigma=4": lambda g, r: add_blur(g, 4),
    "kontras 35%": lambda g, r: low_contrast(g, 0.35),
    "kontras 20%": lambda g, r: low_contrast(g, 0.20),
    "kombinasi (kontras 35% + blur 2 + noise 20)": lambda g, r: add_noise(add_blur(low_contrast(g, 0.35), 2), 20, r),
}


def load_gray(path):
    return P.global_enhancement(P.to_gray(cv2.imread(path)))


def _job(args):
    method, name, g = args
    res = read_number(g, method)
    return method, name, res.number, cer(GROUND_TRUTH, res.number), res.error  # "" -> CER 1.0


def eval_cer(samples):
    """samples: list[(nama, gray)] -> ({metode: (mean_cer, exact_match, n, n_error)}, baris per citra)"""
    jobs = [(m, n, g) for m in P.ENHANCEMENTS for n, g in samples]
    workers = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else (os.cpu_count() or 1)
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            results = list(ex.map(_job, jobs, chunksize=4))
    else:
        results = []
        for i, j in enumerate(jobs, 1):
            results.append(_job(j))
            if i % 50 == 0:
                print(f"  ... {i}/{len(jobs)} OCR selesai", file=sys.stderr, flush=True)
    stats, per_image = {}, []
    for method in P.ENHANCEMENTS:
        rs = [r for r in results if r[0] == method]
        stats[method] = (float(np.mean([r[3] for r in rs])),
                         sum(r[2] == GROUND_TRUTH for r in rs), len(rs), sum(r[4] for r in rs))
        per_image += [(r[1], r[0], r[2], round(r[3], 4), r[4]) for r in rs]
    return stats, per_image


def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(f"{NUM_DIR}/*.jpg"))
    if not files:
        sys.exit("Dataset tidak ditemukan. Jalankan dari root repo.")
    real = [(os.path.basename(f), load_gray(f)) for f in files]

    # ---- A. data asli
    stats_a, rows_a = eval_cer(real)
    # ---- B. stress test (seed tetap -> reproducible)
    rng = np.random.default_rng(42)
    stress = [(f"{n} | {k}", fn(g, rng)) for n, g in real for k, fn in STRESS.items()]
    stats_b, rows_b = eval_cer(stress)

    with open(f"{OUT}/cer_per_image.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["skenario", "citra", "metode", "hasil_ocr", "cer", "tesseract_error"])
        for r in rows_a:
            w.writerow(["A_data_asli", *r])
        for r in rows_b:
            w.writerow(["B_stress_test", *r])

    def table(stats):
        order = sorted(stats.items(), key=lambda kv: (kv[1][0], -kv[1][1]))
        lines = ["| Peringkat | Metode enhancement | Mean CER | Exact match | Tesseract error |",
                 "|---|---|---|---|---|"]
        for i, (m, (c, e, n, err)) in enumerate(order, 1):
            lines.append(f"| {i} | {m} | {c:.4f} | {e}/{n} | {err} |")
        return "\n".join(lines)

    md = ["# Hasil evaluasi CER", "",
          f"Ground truth: `{GROUND_TRUTH}`", "",
          f"## A. Data asli ({len(real)} citra)", "", table(stats_a), "",
          f"## B. Stress test sintetis ({len(stress)} citra = {len(real)} x {len(STRESS)} degradasi)", "",
          table(stats_b), ""]

    # ---- Tanda tangan
    sig_files = sorted(glob.glob(f"{SIG_DIR}/*.jpg"))
    ok = tot = 0
    sig_rows = ["| Citra | Jenis | Prediksi | Ink % | Komponen terbesar % |", "|---|---|---|---|---|"]
    for f in sig_files:
        g = load_gray(f)
        # sampel ABSENT sintetis: tinta dihapus lalu di-inpaint -> hanya latar/watermark
        bg = cv2.medianBlur(cv2.dilate(g, np.ones((25, 25), np.uint8)), 51)
        mask = cv2.dilate((cv2.subtract(bg, g) > 25).astype(np.uint8) * 255, np.ones((7, 7), np.uint8))
        absent = cv2.inpaint(g, mask, 5, cv2.INPAINT_TELEA)
        for kind, img, truth in (("asli (ada TTD)", g, True), ("sintetis (TTD dihapus)", absent, False)):
            r = detect_signature(img)
            ok += r.present == truth
            tot += 1
            sig_rows.append(f"| {os.path.basename(f)} | {kind} | {r.label} | {r.ink_ratio} | {r.largest_ratio} |")
    md += ["## C. Deteksi tanda tangan", "", f"Akurasi: **{ok}/{tot}**", "", *sig_rows, ""]

    with open(f"{OUT}/hasil_evaluasi.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    print("\n".join(md))

    # ---- grafik
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        names = list(P.ENHANCEMENTS)
        fig, ax = plt.subplots(figsize=(11, 5.5), dpi=200)
        x = np.arange(len(names)); wd = 0.4
        ax.bar(x - wd / 2, [stats_a[n][0] for n in names], wd, label="A. data asli")
        ax.bar(x + wd / 2, [stats_b[n][0] for n in names], wd, label="B. stress test")
        ax.set_xticks(x); ax.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
        ax.set_ylabel("Mean CER (lebih kecil = lebih baik)"); ax.legend()
        ax.set_title("Perbandingan metode enhancement berdasarkan CER")
        fig.tight_layout(); fig.savefig(f"{OUT}/cer_comparison.png"); plt.close(fig)
    except ImportError:
        pass


if __name__ == "__main__":
    main()
