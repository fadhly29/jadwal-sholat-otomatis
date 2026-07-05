"""
Konversi .docx -> .jpg (satu gambar utuh) pakai LibreOffice (soffice) + poppler (pdftoppm).
Keduanya perlu terinstall di runner (sudah ditangani di workflow GitHub Actions
lewat `apt-get install libreoffice poppler-utils`).

Karena tinggi halaman docx dibuat dinamis di generate_docx.py (1 halaman panjang,
bukan multi-halaman), hasil PDF-nya selalu 1 halaman -> hasil JPG-nya juga 1 file.
"""

import subprocess
import os
import glob
from PIL import Image, ImageChops


def _autocrop_whitespace(jpg_path: str, padding: int = 20):
    """
    Potong area putih kosong di bawah/kanan tabel (sisa dari halaman besar
    yang sengaja dibuat lebih panjang dari kontennya). Padding kecil disisakan
    di semua sisi biar tidak terlalu mepet.
    """
    img = Image.open(jpg_path)
    bg = Image.new(img.mode, img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox is None:
        return  # gambar kosong semua, jangan diapa-apakan
    left, top, right, bottom = bbox
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(img.width, right + padding)
    bottom = min(img.height, bottom + padding)
    img.crop((left, top, right, bottom)).save(jpg_path, quality=92)


def convert_docx_to_jpg(docx_path: str, out_dir: str, dpi: int = 150) -> str:
    """
    Return path ke file .jpg hasil konversi.
    """
    os.makedirs(out_dir, exist_ok=True)

    # 1. docx -> pdf
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", out_dir, docx_path],
        check=True,
        capture_output=True,
    )
    pdf_path = os.path.join(out_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")

    # 2. pdf -> jpg
    jpg_prefix = os.path.join(out_dir, os.path.splitext(os.path.basename(docx_path))[0])
    subprocess.run(
        ["pdftoppm", "-jpeg", "-r", str(dpi), pdf_path, jpg_prefix],
        check=True,
        capture_output=True,
    )

    # pdftoppm menghasilkan nama dengan suffix "-1", "-01", dst tergantung jumlah halaman.
    hasil = sorted(glob.glob(jpg_prefix + "*.jpg"))
    if not hasil:
        raise RuntimeError(f"Konversi ke JPG gagal, tidak ada file dihasilkan untuk {docx_path}")
    if len(hasil) > 1:
        print(
            f"PERINGATAN: hasil konversi jadi {len(hasil)} halaman/file, "
            "seharusnya cuma 1. Cek apakah tabel masih terlalu panjang untuk 1 halaman."
        )

    # Rapikan nama file jadi persis <namafile>.jpg (tanpa suffix halaman)
    final_path = os.path.join(out_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".jpg")
    if hasil[0] != final_path:
        os.replace(hasil[0], final_path)

    _autocrop_whitespace(final_path)

    return final_path
