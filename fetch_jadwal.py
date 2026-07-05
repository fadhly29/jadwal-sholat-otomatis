"""
Ambil data jadwal sholat bulanan dari API publik EQuran.id.

API ini mengambil datanya dari Bimas Islam Kemenag (bimasislam.kemenag.go.id),
tapi disajikan lewat endpoint REST yang bersih dan tidak butuh API key:
https://equran.id/apidev/shalat

Kalau di kemudian hari endpoint ini berubah atau tidak bisa diakses, alternatif:
1. Minta akses API resmi ke humasbimasislam@kemenag.go.id
2. Pakai package pip "jadwal-shalat-kemenag" (scraping langsung ke situs Kemenag)
"""

import requests

BASE_URL = "https://equran.id/api/v2/shalat"


class JadwalFetchError(Exception):
    pass


def get_jadwal_bulanan(provinsi: str, kabkota: str, bulan: int, tahun: int) -> dict:
    """
    Ambil jadwal sholat 1 bulan penuh untuk provinsi & kabupaten/kota tertentu.

    Return: dict dengan struktur:
        {
            "provinsi": "Banten",
            "kabkota": "Kota Tangerang Selatan",
            "bulan": 7,
            "tahun": 2026,
            "bulan_nama": "Juli",
            "jadwal": [
                {
                    "tanggal": 1,
                    "tanggal_lengkap": "2026-07-01",
                    "hari": "Rabu",
                    "imsak": "04:28",
                    "subuh": "04:38",
                    "terbit": "05:55",
                    "dhuha": "06:24",
                    "dzuhur": "11:55",
                    "ashar": "15:16",
                    "maghrib": "17:48",
                    "isya": "19:02"
                },
                ...
            ]
        }
    """
    payload = {
        "provinsi": provinsi,
        "kabkota": kabkota,
        "bulan": bulan,
        "tahun": tahun,
    }
    resp = requests.post(BASE_URL, json=payload, timeout=30)
    resp.raise_for_status()
    body = resp.json()

    if body.get("code") != 200:
        raise JadwalFetchError(f"API mengembalikan error: {body}")

    data = body.get("data")
    if not data or not data.get("jadwal"):
        raise JadwalFetchError(
            f"Data jadwal kosong untuk {kabkota}, {provinsi} ({bulan}/{tahun}). "
            "Cek kembali penulisan nama provinsi/kabkota."
        )
    return data


def list_kabkota(provinsi: str) -> list:
    """Utilitas buat mengecek daftar nama kabupaten/kota persis sesuai API (opsional, untuk debug)."""
    resp = requests.post(
        "https://equran.id/api/v2/shalat/kabkota", json={"provinsi": provinsi}, timeout=30
    )
    resp.raise_for_status()
    return resp.json().get("data", [])
