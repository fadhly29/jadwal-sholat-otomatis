"""
Kirim file JPG jadwal sholat otomatis ke Telegram, pakai Telegram Bot API resmi.
100% gratis, tidak ada risiko banned (beda dengan WhatsApp tidak resmi),
dan tidak butuh server yang nyala 24 jam - cukup 1 HTTP request biasa,
cocok banget dipanggil dari GitHub Actions.

Setup sekali di awal (lihat README.md):
1. Chat @BotFather di Telegram, kirim /newbot, ikuti instruksinya
   -> dapat TELEGRAM_BOT_TOKEN
2. Mulai chat dengan bot yang baru dibuat (klik link dari BotFather, kirim /start)
   -> atau invite bot itu ke grup keluarga/jamaah
3. Ambil chat_id:
   - Untuk chat pribadi: buka https://api.telegram.org/bot<TOKEN>/getUpdates
     setelah kirim pesan apa saja ke bot, chat_id ada di response JSON-nya
   - Untuk grup: invite bot ke grup, kirim pesan di grup, lalu cek getUpdates juga
4. Simpan TELEGRAM_BOT_TOKEN & TELEGRAM_CHAT_ID sebagai GitHub secrets
"""

import os
import requests


class TelegramSendError(Exception):
    pass


def kirim_gambar_telegram(bot_token: str, chat_id: str, filepath: str, caption: str) -> dict:
    """
    Kirim 1 file gambar ke Telegram sebagai dokumen (bukan "photo") supaya
    resolusinya tidak dikompres ulang oleh Telegram - penting karena ini
    tabel dengan teks kecil, gampang buram kalau dikompres.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(filepath, "rb") as f:
        files = {"document": (os.path.basename(filepath), f, "image/jpeg")}
        data = {"chat_id": chat_id, "caption": caption}
        resp = requests.post(url, data=data, files=files, timeout=60)

    body = resp.json()
    if not body.get("ok"):
        raise TelegramSendError(f"Telegram menolak permintaan: {body}")
    return body


def kirim_dari_env(filepath: str, caption: str) -> dict | None:
    """
    Dipanggil dari main.py: kirim otomatis kalau TELEGRAM_BOT_TOKEN dan
    TELEGRAM_CHAT_ID tersedia di environment (GitHub Actions secrets).
    Kalau tidak ada, dilewati saja tanpa error.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID tidak diset, lewati pengiriman Telegram.")
        return None

    print(f"Mengirim {filepath} ke Telegram (chat_id={chat_id})...")
    result = kirim_gambar_telegram(token, chat_id, filepath, caption)
    print("Berhasil dikirim ke Telegram.")
    return result
