"""Character Error Rate (CER) berbasis Levenshtein distance."""


def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j] + 1,                      # deletion
                         cur[j - 1] + 1,                   # insertion
                         prev[j - 1] + (a[i - 1] != b[j - 1]))  # substitution
        prev = cur
    return prev[-1]


def cer(reference: str, hypothesis: str) -> float:
    """CER = (S + D + I) / N, N = panjang referensi.  Bisa > 1 bila banyak insertion."""
    if not reference:
        raise ValueError("reference kosong")
    return levenshtein(reference, hypothesis) / len(reference)
