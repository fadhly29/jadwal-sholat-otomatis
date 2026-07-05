# Jadwal Sholat Otomatis — Kota Tangerang Selatan

Generate gambar `.jpg` jadwal sholat bulanan secara otomatis, meniru format
`jadwal-sholat-juni.docx` (tabel dengan kolom M/H/Hari/Imsak.../Isya, header ungu,
highlight biru untuk Senin-Kamis, highlight hijau untuk Jumat, dan highlight Ayyamul Bidh),
lalu otomatis dikirim ke Telegram dan/atau WhatsApp.

Sumber data: [EQuran.id API](https://equran.id/apidev/shalat), yang datanya berasal
dari Bimas Islam Kementerian Agama RI.

**Alur:** ambil data → generate `.docx` (dipakai sebagai "master" tata letak,
supaya warna/border/highlight persis) → konversi ke `.jpg` lewat LibreOffice
→ kirim ke Telegram/WhatsApp. File `.docx`-nya tetap disimpan juga di `output/`
sebagai cadangan, tapi yang dikirim ke chat adalah `.jpg`-nya.

> **Soal Hermes Agent / OpenClaw:** kedua tools itu framework AI agent
> serba-bisa yang perlu jalan 24 jam di server sendiri plus API key LLM —
> dibuat untuk chatbot yang membalas pesan, bukan untuk kirim 1 gambar
> sebulan sekali. Untuk kebutuhan kamu, itu jauh lebih rumit dan lebih mahal
> dari yang perlu. Cukup pakai GitHub Actions (gratis, tidak perlu server
> nyala) + Telegram Bot API (gratis, resmi) seperti di bawah ini.

## Coba dulu di komputer sendiri

```bash
pip install -r requirements.txt

# perlu juga LibreOffice + poppler-utils untuk konversi ke jpg (Ubuntu/Debian):
sudo apt install libreoffice poppler-utils
# (di Mac: brew install libreoffice poppler)

# opsional tapi disarankan: install font Selawik biar tampilan lokal sama
# persis dengan hasil GitHub Actions (lihat catatan soal font di bawah)
mkdir -p ~/.fonts
curl -sL -o ~/.fonts/Selawik-Bold.ttf \
  "https://raw.githubusercontent.com/fontfen/selawik/master/Selawik-Bold.ttf"
fc-cache -f ~/.fonts

# opsional, sekali saja: pastikan nama kabkota di config.py cocok dengan API
python check_kabkota.py

# generate untuk bulan depan
python main.py

# atau generate untuk bulan/tahun tertentu, misal Agustus 2026
python main.py 8 2026
```

File hasil (`.jpg` dan `.docx`) ada di folder `output/`.

## Setup otomatisasi bulanan (gratis, pakai GitHub Actions)

1. Buat repository baru di GitHub (boleh **private**), lalu upload semua file di folder ini.
2. Repo privat dapat 2.000 menit runner gratis/bulan — job ini makan waktu lebih lama dari sebelumnya
   (karena install LibreOffice), sekitar 2-3 menit/bulan, masih jauh dari batas.
3. Buka tab **Actions** di repo kamu → workflow **"Generate Jadwal Sholat Bulanan"** akan otomatis terdaftar
   (sudah ada di `.github/workflows/generate-jadwal.yml`).
4. Klik **Run workflow** sekali secara manual untuk memastikan semuanya jalan.
5. Setelah itu, workflow akan jalan sendiri **tiap tanggal 25** tiap bulan, generate jadwal untuk bulan berikutnya,
   lalu:
   - commit file `.jpg`+`.docx` baru ke folder `output/` di repo kamu, dan
   - upload juga sebagai "artifact" yang bisa didownload dari tab Actions, dan
   - kirim ke Telegram/WhatsApp kalau secretnya sudah diisi (lihat di bawah).

### Kirim otomatis ke Telegram (gratis, resmi, direkomendasikan)

1. Di Telegram, chat bot **@BotFather** → kirim `/newbot` → ikuti instruksinya
   (kasih nama & username bot). Di akhir kamu dapat **token** seperti
   `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`.
2. Mulai chat dengan bot barumu (klik link yang diberikan BotFather, kirim `/start`),
   atau invite bot itu ke grup keluarga/jamaah kalau mau kirim ke grup.
3. Ambil **chat_id** tujuan:
   - Kirim 1 pesan apa saja ke bot/grup tersebut dulu.
   - Buka `https://api.telegram.org/bot<TOKEN>/getUpdates` di browser
     (ganti `<TOKEN>` dengan token dari langkah 1).
   - Cari angka `"chat":{"id": ...}` di response JSON-nya — itu chat_id-nya
     (untuk grup biasanya angkanya negatif, itu normal).
4. Di repo GitHub, buka **Settings → Secrets and variables → Actions**, tambahkan:
   - `TELEGRAM_BOT_TOKEN` — token dari langkah 1
   - `TELEGRAM_CHAT_ID` — chat_id dari langkah 3
5. Selesai — jalankan workflow, gambar jadwal sholat akan otomatis terkirim ke Telegram.

Telegram Bot API 100% gratis selamanya, resmi dari Telegram (bukan tools tidak
resmi), dan tidak ada risiko akun kena banned — jauh lebih simpel dibanding WhatsApp
untuk kasus seperti ini.

### Kirim otomatis ke WhatsApp juga (opsional, pakai Fonnte)

1. Daftar di [fonnte.com](https://fonnte.com), lalu buat device baru dan scan QR
   pakai nomor WhatsApp yang mau dipakai untuk mengirim (disarankan pakai
   nomor sekunder, bukan nomor utama kamu).
2. Salin **token** device dari dashboard Fonnte.
3. Tentukan target: nomor WA tujuan format `628xxxxxxxxxx` (tanpa `+` / `08`),
   atau ID grup WhatsApp kalau mau kirim ke grup jamaah/pengurus
   (cara ambil ID grup ada di [docs.fonnte.com](https://docs.fonnte.com/get-whatsapp-group-id/)).
4. Tambahkan secrets `FONNTE_TOKEN` dan `WA_TARGET` di repo GitHub kamu.

Kalau secret Telegram/Fonnte tidak diisi, langkah kirim itu otomatis dilewati
(tidak error) — jadi aman untuk dicoba bertahap: generate gambar dulu, baru
nyalakan pengiriman belakangan. Kamu bisa aktifkan salah satu saja atau
keduanya sekaligus.

**Soal biaya Fonnte:** paket gratis Fonnte cuma untuk uji coba/pengembangan dan
terbatas; untuk pemakaian rutin bulanan seperti ini paket termurahnya sekitar
Rp25.000/bulan. Fonnte juga layanan tidak resmi (bukan dari Meta), jadi tetap
ada risiko kecil kena banned kalau dipakai berlebihan — untuk kirim 1x/bulan
ke 1 nomor/grup risikonya sangat kecil. Kalau WA tidak wajib, Telegram di atas
sudah cukup dan gratis penuh.

### Kalau mau dikirim otomatis ke email

Buka `.github/workflows/generate-jadwal.yml`, hapus tanda `#` di bagian
"Kirim email" paling bawah, lalu tambahkan 3 secrets di
**Settings → Secrets and variables → Actions**:
- `EMAIL_USERNAME` — alamat Gmail kamu
- `EMAIL_PASSWORD` — [App Password Gmail](https://myaccount.google.com/apppasswords) (bukan password biasa)
- `EMAIL_TO` — alamat tujuan

## Kalau mau pindah kota/provinsi

Edit `config.py`:

```python
PROVINSI = "Banten"
KABKOTA = "Kota Tangerang Selatan"
```

Jalankan `python check_kabkota.py` setelah ganti nilai `PROVINSI` untuk memastikan
penulisan `KABKOTA` persis sama dengan yang dikenali API.

## Catatan

- **Soal font:** kamu minta "Segoe UI Black"/"Segoe UI Bold", tapi Segoe UI
  itu font proprietary bawaan Windows yang tidak ada di server Linux (GitHub
  Actions jalan di Ubuntu). Sebagai gantinya dipakai **Selawik** — font
  pengganti Segoe UI yang dibuat resmi oleh Microsoft sendiri (open source,
  lisensi OFL, metric-compatible dengan Segoe UI, jadi proporsinya memang
  didesain semirip mungkin). Selawik cuma tersedia 5 ketebalan (Light,
  Semilight, Regular, Semibold, Bold) — **tidak ada varian "Black"** — jadi
  **Bold** yang dipakai di sini adalah yang paling tebal yang ada. Font-nya
  diinstall otomatis lewat workflow. Nama family font-nya di dalam file cuma
  "Selawik" (bukan "Selawik Bold"); ketebalan Bold-nya otomatis kepakai
  karena semua teks di kode ini sudah diset `bold=True`.
- **Tanggal Hijriah** dihitung otomatis pakai library `hijridate` (metode hisab
  Umm al-Qura), sudah dites cocok dengan tanggal Kemenag untuk contoh
  1 Juni 2026 = 15 Dzulhijjah 1447H dan 30 Juni 2026 = 15 Muharram 1448H.
  Karena ini hasil hitungan (bukan hasil sidang isbat resmi), ada kemungkinan kecil
  selisih 1 hari di sekitar pergantian bulan Hijriah — cek manual kalau kebetulan
  pas di tanggal krusial (misal awal Ramadhan/Syawal).
- Kalau endpoint `equran.id` di kemudian hari berubah/down, dua alternatif:
  1. Minta akses API resmi ke Bimas Islam Kemenag: `humasbimasislam@kemenag.go.id`
  2. Ganti `fetch_jadwal.py` untuk pakai package `pip install jadwal-shalat-kemenag`
     (scraping langsung ke situs Kemenag — perlu diingat situs itu punya `robots.txt`
     yang melarang akses otomatis, jadi ini bukan opsi pertama yang disarankan).
