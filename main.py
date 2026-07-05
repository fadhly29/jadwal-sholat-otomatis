"""
Jalankan bulanan (lewat GitHub Actions) untuk generate jadwal sholat bulan DEPAN,
otomatis dari data Bimas Islam Kemenag, lalu dikirim sebagai gambar JPG ke
Telegram (dan/atau WhatsApp kalau diaktifkan).

Alur: ambil data -> generate .docx (dipakai sebagai "master" tata letak) ->
konversi ke .jpg -> kirim ke Telegram / WhatsApp.

Jalan manual:
    python main.py                # generate untuk bulan depan (default)
    python main.py 8 2026         # generate untuk bulan & tahun tertentu
"""

import sys
import os
from datetime import date

from config import PROVINSI, KABKOTA, NAMA_TAMPILAN, OUTPUT_DIR
from fetch_jadwal import get_jadwal_bulanan
from hijriah_helper import ke_hijriah, rentang_hijriah_bulan_ini
from generate_docx import build_document
from convert_to_image import convert_docx_to_jpg
from send_telegram import kirim_dari_env as kirim_telegram
from send_whatsapp import kirim_dari_env as kirim_whatsapp

BULAN_NAMA_ID = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


def next_month(today: date) -> tuple[int, int]:
    if today.month == 12:
        return 1, today.year + 1
    return today.month + 1, today.year


def main():
    if len(sys.argv) >= 3:
        bulan, tahun = int(sys.argv[1]), int(sys.argv[2])
    else:
        bulan, tahun = next_month(date.today())

    print(f"Mengambil jadwal sholat {KABKOTA}, {PROVINSI} untuk {BULAN_NAMA_ID[bulan]} {tahun}...")
    data = get_jadwal_bulanan(PROVINSI, KABKOTA, bulan, tahun)
    data["kabkota"] = NAMA_TAMPILAN
    data["bulan_nama"] = BULAN_NAMA_ID[bulan]

    # Tambahkan tanggal Hijriah per hari + siapkan label rentang Hijriah untuk judul
    tanggal_masehi_list = []
    for item in data["jadwal"]:
        d = date.fromisoformat(item["tanggal_lengkap"])
        tanggal_masehi_list.append(d)
        h_hari, _, _ = ke_hijriah(d)
        item["h_tanggal"] = h_hari

    hijriah_label = rentang_hijriah_bulan_ini(tanggal_masehi_list)

    doc = build_document(data, hijriah_label)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"jadwal-sholat-{data['bulan_nama'].lower()}-{tahun}.docx"
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc.save(filepath)

    print(f"Berhasil disimpan: {filepath}")

    jpg_path = convert_docx_to_jpg(filepath, OUTPUT_DIR)
    print(f"Berhasil dikonversi ke JPG: {jpg_path}")

    caption = (
        f"Jadwal Sholat {NAMA_TAMPILAN} - {data['bulan_nama']} {tahun} sudah terbit. "
        f"({hijriah_label})"
    )
    kirim_telegram(jpg_path, caption)
    kirim_whatsapp(jpg_path, caption)

    return jpg_path


if __name__ == "__main__":
    main()
