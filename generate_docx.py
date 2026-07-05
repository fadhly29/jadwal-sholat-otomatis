"""
Generate file .docx jadwal sholat, meniru persis struktur file template
"jadwal-sholat-juni.docx" yang sudah dibedah XML-nya:

- Header tabel: latar ungu (5F497A), teks putih, bold, font Segoe UI Black
- Baris data: latar biru muda (B6DDE8) merata di semua sel
- Border tabel: garis tunggal hitam 0.75pt di semua sisi
- Highlight khusus (di atas latar biru muda):
    * Baris Senin & Kamis  -> sel HARI + sel MAGRIB di-highlight DARK_BLUE
      (mengikuti sunnah puasa Senin-Kamis, highlight waktu berbuka)
    * Baris Jumat          -> sel HARI + sel ZUHUR di-highlight GREEN
      (mengingatkan waktu shalat Jumat)
    * Tanggal Hijriah 13/14/15 -> sel H di-highlight DARK_BLUE
      (Ayyamul Bidh, puasa sunnah pertengahan bulan Hijriah)
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HEADER_FILL = "5F497A"
DATA_FILL = "B6DDE8"
FONT_NAME = "Segoe UI Black"

# Lebar kolom persis seperti template (dalam satuan DXA, 1440 dxa = 1 inch)
COLUMN_WIDTHS_DXA = [475, 577, 1073, 981, 1096, 1015, 923, 1039, 784, 969, 1085]
HEADERS = ["M", "H", "HARI", "IMSAK", "SUBUH", "SYURUQ", "DUHA", "ZUHUR", "ASAR", "MAGRIB", "ISYA"]

COL_IDX = {name: i for i, name in enumerate(HEADERS)}


def _set_cell_shading(cell, fill_hex: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)
    tcPr.append(shd)


def _set_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tblPr.append(borders)


def _set_column_widths(table):
    table.autofit = False
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            cell.width = Cm(COLUMN_WIDTHS_DXA[idx] / 566.9)  # dxa -> cm (1 cm = 566.9 dxa)


def _write_cell(cell, text, *, bold=False, color=None, highlight=None, size=11):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(str(text))
    run.font.name = FONT_NAME
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if highlight:
        run.font.highlight_color = highlight


def build_document(data: dict, hijriah_range_label: str) -> Document:
    """
    data: hasil dari fetch_jadwal.get_jadwal_bulanan(), sudah ditambah key
          "h_tanggal" (int hari Hijriah) di tiap item jadwal (lihat main.py).
    hijriah_range_label: contoh "Dzulhijjah 1447 - Muharram 1448"
    """
    doc = Document()

    section = doc.sections[0]
    section.orientation = 0  # portrait
    section.left_margin = Cm(1.5)
    section.right_margin = Cm(1.5)
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(0.5)

    # Halaman dibuat 1 halaman besar (bukan A4 biasa) supaya tabel 28-31 baris
    # tidak pernah kepotong ke halaman 2. Kelebihan area putih di bawah akan
    # dipotong otomatis nanti di convert_to_image.py (auto-crop), jadi tidak
    # perlu kalkulasi tinggi per baris yang rapuh (rentan meleset kalau font
    # fallback bikin teks wrap 2 baris di sel HARI).
    section.page_width = Cm(21)  # lebar A4
    section.page_height = Cm(50)  # cukup untuk 31 baris + judul, masih di bawah batas docx (~55.8cm)

    # --- Judul ---
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(f"Jadwal Sholat {data['kabkota']}")
    run.font.size = Pt(18)
    run.font.bold = True

    # --- Sub judul: bulan/tahun + rentang hijriah + sumber ---
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = sub.add_run(f"{data['bulan_nama'].upper()} {data['tahun']} (")
    r1.font.size = Pt(13)
    r2 = sub.add_run(hijriah_range_label)
    r2.font.size = Pt(10)
    r2.font.underline = True
    r3 = sub.add_run(")   ")
    r3.font.size = Pt(13)
    r4 = sub.add_run("Sumber: bimasislam.kemenag.go.id")
    r4.font.size = Pt(9)
    r4.italic = True

    doc.add_paragraph()

    # --- Tabel ---
    n_rows = len(data["jadwal"]) + 1
    table = doc.add_table(rows=n_rows, cols=len(HEADERS))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_table_borders(table)

    # Header
    for c, label in enumerate(HEADERS):
        cell = table.rows[0].cells[c]
        _set_cell_shading(cell, HEADER_FILL)
        _write_cell(cell, label, bold=True, color="FFFFFF", size=11)

    # Data
    for r, item in enumerate(data["jadwal"], start=1):
        hari = item["hari"]
        if hari in ("Minggu",):
            hari = "Ahad"  # ikut gaya penamaan Kemenag

        h_tanggal = item["h_tanggal"]

        row_values = {
            "M": item["tanggal"],
            "H": h_tanggal,
            "HARI": hari,
            "IMSAK": item["imsak"],
            "SUBUH": item["subuh"],
            "SYURUQ": item["terbit"],
            "DUHA": item["dhuha"],
            "ZUHUR": item["dzuhur"],
            "ASAR": item["ashar"],
            "MAGRIB": item["maghrib"],
            "ISYA": item["isya"],
        }

        is_senin_kamis = hari in ("Senin", "Kamis")
        is_jumat = hari == "Jumat"
        is_ayyamul_bidh = h_tanggal in (13, 14, 15)

        for col_name, col_idx in COL_IDX.items():
            cell = table.rows[r].cells[col_idx]
            _set_cell_shading(cell, DATA_FILL)

            highlight = None
            if is_senin_kamis and col_name in ("HARI", "MAGRIB"):
                highlight = WD_COLOR_INDEX.DARK_BLUE
            if is_jumat and col_name in ("HARI", "ZUHUR"):
                highlight = WD_COLOR_INDEX.GREEN
            if is_ayyamul_bidh and col_name == "H":
                highlight = WD_COLOR_INDEX.DARK_BLUE

            _write_cell(cell, row_values[col_name], bold=(col_name in ("M", "HARI")), highlight=highlight)

    _set_column_widths(table)
    return doc
