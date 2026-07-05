"""
Kirim file jadwal sholat (.docx) otomatis ke WhatsApp lewat Fonnte
(https://fonnte.com) - WA gateway tidak resmi yang paling gampang untuk
kasus seperti ini karena tinggal scan QR sekali, tanpa perlu verifikasi
bisnis/dokumen seperti WhatsApp API resmi dari Meta.

Setup sekali di awal (lihat README.md untuk detail):
1. Daftar & buat device di https://fonnte.com (scan QR pakai nomor WA kamu)
2. Salin "token" device dari dashboard
3. Simpan sebagai secret FONNTE_TOKEN & WA_TARGET di GitHub repo

CATATAN:
- Fonnte adalah layanan tidak resmi (jalan lewat WhatsApp Web yang diotomasi),
  jadi tetap ada risiko kecil nomor kena banned oleh WhatsApp kalau dipakai
  untuk broadcast/spam. Untuk kirim ke 1 nomor/1 grup jamaah tiap bulan,
  risikonya sangat rendah.
- WA_TARGET bisa berupa nomor (format 628xxxxxxxxxx, tanpa "+") atau ID grup
  WhatsApp (lihat cara ambil ID grup di docs.fonnte.com/get-whatsapp-group-id).
"""

import os
import requests

FONNTE_URL = "https://api.fonnte.com/send"


class WhatsAppSendError(Exception):
    pass


def kirim_dokumen_whatsapp(token: str, target: str, filepath: str, pesan: str) -> dict:
    """
    Kirim satu file (docx/pdf/dll) + pesan pendamping ke satu nomor/grup WA.
    """
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f)}
        data = {"target": target, "message": pesan}
        headers = {"Authorization": token}
        resp = requests.post(FONNTE_URL, headers=headers, data=data, files=files, timeout=60)

    resp.raise_for_status()
    body = resp.json()

    if body.get("status") is False:
        raise WhatsAppSendError(f"Fonnte menolak permintaan: {body}")

    return body


def kirim_dari_env(filepath: str, pesan: str) -> dict | None:
    """
    Helper dipanggil dari main.py: kirim otomatis kalau env var FONNTE_TOKEN
    dan WA_TARGET tersedia (diisi lewat GitHub Actions secrets). Kalau tidak
    ada, dilewati saja (tidak error) supaya script tetap jalan tanpa WA.
    """
    token = os.environ.get("FONNTE_TOKEN")
    target = os.environ.get("WA_TARGET")

    if not token or not target:
        print("FONNTE_TOKEN / WA_TARGET tidak diset, lewati pengiriman WhatsApp.")
        return None

    print(f"Mengirim {filepath} ke WhatsApp ({target})...")
    result = kirim_dokumen_whatsapp(token, target, filepath, pesan)
    print("Berhasil dikirim ke WhatsApp:", result)
    return result
