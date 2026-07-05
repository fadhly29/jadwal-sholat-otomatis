"""
Jalankan sekali secara manual untuk memastikan penulisan nama kabupaten/kota
di config.py PERSIS sama dengan yang dikenali API (huruf besar/kecil dan
"Kota "/"Kab." harus cocok).

    python check_kabkota.py
"""

from fetch_jadwal import list_kabkota
from config import PROVINSI, KABKOTA

daftar = list_kabkota(PROVINSI)
print(f"Daftar kabupaten/kota di provinsi '{PROVINSI}':")
for nama in daftar:
    tanda = " <-- dipakai di config.py" if nama == KABKOTA else ""
    print(f"  - {nama}{tanda}")

if KABKOTA not in daftar:
    print(f"\n⚠️  '{KABKOTA}' TIDAK ditemukan persis di daftar di atas.")
    print("   Salin nama yang benar dari daftar dan tempel ke config.py (KABKOTA = ...)")
else:
    print(f"\n✅ '{KABKOTA}' cocok dengan data API.")
