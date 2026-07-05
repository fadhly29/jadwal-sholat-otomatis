"""
Konversi tanggal Masehi -> Hijriah pakai library `hijridate` (perhitungan algoritmik,
metode Umm al-Qura). Dites cocok dengan kalender Kemenag untuk kasus contoh
(1 Juni 2026 = 15 Dzulhijjah 1447H, 30 Juni 2026 = 15 Muharram 1448H).

CATATAN: karena ini hasil hisab/algoritma (bukan hasil sidang isbat Kemenag),
ada kemungkinan kecil selisih 1 hari di sekitar pergantian bulan Hijriah
(terutama bulan Ramadhan & Syawal). Kalau butuh presisi 100% sesuai isbat,
cek ulang manual di sekitar tanggal 1 bulan Hijriah baru.
"""

from datetime import date
from hijridate import Gregorian

NAMA_BULAN_HIJRIAH_ID = {
    1: "Muharram",
    2: "Safar",
    3: "Rabiul Awal",
    4: "Rabiul Akhir",
    5: "Jumadil Awal",
    6: "Jumadil Akhir",
    7: "Rajab",
    8: "Syaban",
    9: "Ramadhan",
    10: "Syawal",
    11: "Dzulkaidah",
    12: "Dzulhijjah",
}


def ke_hijriah(tanggal_masehi: date) -> tuple[int, int, int]:
    """Return (hari, bulan, tahun) Hijriah untuk satu tanggal Masehi."""
    h = Gregorian(tanggal_masehi.year, tanggal_masehi.month, tanggal_masehi.day).to_hijri()
    return h.day, h.month, h.year


def nama_bulan_hijriah(bulan: int) -> str:
    return NAMA_BULAN_HIJRIAH_ID[bulan]


def is_ayyamul_bidh(hari_hijriah: int) -> bool:
    """Ayyamul Bidh = puasa sunnah tanggal 13, 14, 15 tiap bulan Hijriah."""
    return hari_hijriah in (13, 14, 15)


def rentang_hijriah_bulan_ini(list_tanggal_masehi: list[date]) -> str:
    """
    Bikin teks rentang Hijriah untuk judul dokumen, misal:
    "Dzulhijjah 1447 - Muharram 1448" (kalau bulan Masehi ini mencakup
    pergantian bulan Hijriah), atau cukup "Ramadhan 1447" kalau tidak lintas bulan.
    """
    awal_hari, awal_bulan, awal_tahun = ke_hijriah(list_tanggal_masehi[0])
    akhir_hari, akhir_bulan, akhir_tahun = ke_hijriah(list_tanggal_masehi[-1])

    awal_label = f"{nama_bulan_hijriah(awal_bulan)} {awal_tahun}"
    if (awal_bulan, awal_tahun) == (akhir_bulan, akhir_tahun):
        return awal_label
    akhir_label = f"{nama_bulan_hijriah(akhir_bulan)} {akhir_tahun}"
    return f"{awal_label} - {akhir_label}"
