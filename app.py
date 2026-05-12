import streamlit as st
import re
import json
import base64
import io
from datetime import datetime, date
from PIL import Image
import pytesseract
import gspread
from google.oauth2.service_account import Credentials

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="INTIF — Perpanjangan Izin Tinggal",
    page_icon="🛂",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS KUSTOM — tampilan elegan & mobile-friendly
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --navy:   #0B1F3A;
    --gold:   #C9A84C;
    --gold2:  #E8C97A;
    --cream:  #F7F4EE;
    --white:  #FFFFFF;
    --red:    #C0392B;
    --green:  #1A7A4A;
    --border: #D6CEBD;
    --shadow: 0 4px 24px rgba(11,31,58,0.10);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--cream);
    color: var(--navy);
}

/* Header instansi */
.intif-header {
    background: linear-gradient(135deg, var(--navy) 0%, #163660 100%);
    color: var(--white);
    border-radius: 16px;
    padding: 28px 32px 24px 32px;
    margin-bottom: 28px;
    border-left: 5px solid var(--gold);
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
}
.intif-header::after {
    content: '';
    position: absolute;
    right: -30px; top: -30px;
    width: 130px; height: 130px;
    border-radius: 50%;
    border: 30px solid rgba(201,168,76,0.10);
}
.intif-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 1.55rem;
    margin: 0 0 4px 0;
    letter-spacing: 0.5px;
    color: var(--gold2);
}
.intif-header p {
    margin: 0;
    font-size: 0.85rem;
    opacity: 0.80;
    letter-spacing: 0.3px;
}
.badge {
    display: inline-block;
    background: var(--gold);
    color: var(--navy);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
}

/* Card utama */
.card {
    background: var(--white);
    border-radius: 14px;
    padding: 28px 28px 24px 28px;
    margin-bottom: 20px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.10rem;
    font-weight: 600;
    color: var(--navy);
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.card-sub {
    font-size: 0.80rem;
    color: #6b7588;
    margin-bottom: 18px;
}

/* Step indicator */
.steps {
    display: flex;
    gap: 0;
    margin-bottom: 28px;
    position: relative;
}
.step {
    flex: 1;
    text-align: center;
    font-size: 0.72rem;
    font-weight: 600;
    color: #a0a8b8;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding-top: 8px;
}
.step.active { color: var(--navy); }
.step.done   { color: var(--green); }
.step-dot {
    width: 28px; height: 28px;
    border-radius: 50%;
    background: #e3e7ef;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 6px auto;
    font-size: 0.78rem;
    font-weight: 700;
    color: #a0a8b8;
    border: 2px solid #e3e7ef;
    transition: all 0.3s;
}
.step.active .step-dot {
    background: var(--navy);
    color: var(--white);
    border-color: var(--navy);
    box-shadow: 0 0 0 4px rgba(11,31,58,0.12);
}
.step.done .step-dot {
    background: var(--green);
    color: var(--white);
    border-color: var(--green);
}

/* Alert */
.alert-danger {
    background: #FFF0EE;
    border-left: 4px solid var(--red);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 14px;
    color: var(--red);
    font-size: 0.87rem;
    font-weight: 500;
    line-height: 1.55;
}
.alert-success {
    background: #EAF7EF;
    border-left: 4px solid var(--green);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 14px;
    color: var(--green);
    font-size: 0.87rem;
    font-weight: 500;
}

/* Tombol */
.stButton > button {
    background: linear-gradient(135deg, var(--navy) 0%, #163660 100%) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 12px 28px !important;
    letter-spacing: 0.4px !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
    box-shadow: 0 3px 12px rgba(11,31,58,0.18) !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Upload zone */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    background: #FAFAF8 !important;
    padding: 12px !important;
}

/* Input fields */
.stTextInput > div > div > input,
.stDateInput > div > div > input {
    border-radius: 8px !important;
    border: 1.5px solid var(--border) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.90rem !important;
    color: var(--navy) !important;
    background: #FAFAF8 !important;
    padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus,
.stDateInput > div > div > input:focus {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 3px rgba(11,31,58,0.09) !important;
}
label[data-testid="stWidgetLabel"] {
    font-size: 0.80rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    color: #4a5568 !important;
    text-transform: uppercase !important;
}

/* Divider */
hr { border-color: var(--border) !important; margin: 20px 0 !important; }

/* Footer */
.footer {
    text-align: center;
    font-size: 0.74rem;
    color: #9aa3b2;
    margin-top: 32px;
    padding-bottom: 20px;
    line-height: 1.7;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--cream); }
::-webkit-scrollbar-thumb { background: #c5cad4; border-radius: 3px; }

/* Success animation */
@keyframes fadeIn { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
.fade-in { animation: fadeIn 0.5s ease; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# GOOGLE SHEETS SETUP
# ============================================================
SHEET_NAME = "INTIF - Data Perpanjangan Izin Tinggal"   # ganti sesuai nama sheet Anda
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_gsheet_client():
    """
    Membaca credentials dari file JSON yang diupload user,
    atau dari st.secrets jika di-deploy ke Streamlit Cloud.
    """
    try:
        # Coba dari st.secrets (untuk deployment)
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    except Exception:
        # Fallback: baca dari file lokal credentials.json
        try:
            creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        except FileNotFoundError:
            return None
    client = gspread.authorize(creds)
    return client

def append_to_sheet(data: dict):
    """Menambahkan satu baris data ke Google Sheets."""
    client = get_gsheet_client()
    if client is None:
        return False, "File credentials.json tidak ditemukan. Ikuti panduan setup Google Sheets."
    try:
        sheet = client.open(SHEET_NAME).sheet1
        # Pastikan header ada
        headers = sheet.row_values(1)
        if not headers:
            sheet.append_row([
                "Timestamp", "Nama Lengkap", "Nomor Paspor",
                "Tanggal Lahir", "Kewarganegaraan", "Masa Berlaku Paspor",
                "Nomor HP", "Email", "Keperluan"
            ])
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("nama", ""),
            data.get("nomor_paspor", ""),
            data.get("tanggal_lahir", ""),
            data.get("kewarganegaraan", ""),
            data.get("masa_berlaku", ""),
            data.get("nomor_hp", ""),
            data.get("email", ""),
            data.get("keperluan", ""),
        ]
        sheet.append_row(row)
        return True, "Data berhasil disimpan ke Google Sheets ✓"
    except Exception as e:
        return False, f"Gagal menyimpan ke Sheets: {str(e)}"


# ============================================================
# OCR — EKSTRAKSI DATA PASPOR
# ============================================================
def preprocess_image(img: Image.Image) -> Image.Image:
    """Pra-pemrosesan ringan agar OCR cepat."""
    # Batasi ukuran maksimal agar tidak berat
    max_size = 1500
    w, h = img.size
    if w > max_size or h > max_size:
        ratio = min(max_size/w, max_size/h)
        img = img.resize((int(w*ratio), int(h*ratio)), Image.LANCZOS)
    # Grayscale saja — cukup untuk paspor
    return img.convert("L")

def parse_mrz(mrz_lines: list) -> dict:
    """Parse MRZ paspor — menerima list of strings."""
    result = {}
    try:
        # Bersihkan dan ambil 2 baris
        baris = [l.replace(' ', '').strip() for l in mrz_lines if l.strip()]
        if len(baris) < 2:
            return result

        line1 = baris[0].ljust(44, '<')[:44]
        line2 = baris[1].ljust(44, '<')[:44]

        # Nama dari baris 1 (posisi 5-44)
        name_raw = line1[5:44]
        parts    = name_raw.split('<<')
        surname  = parts[0].replace('<', ' ').strip()
        given    = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ''
        nama     = f"{surname} {given}".strip()
        if nama:
            result['nama'] = nama

        # Nomor paspor (baris 2, posisi 0-8)
        nomor = line2[0:9].replace('<', '').strip()
        if nomor:
            result['nomor_paspor'] = nomor

        # Kewarganegaraan (baris 2, posisi 10-12)
        neg = line2[10:13].replace('<', '').strip()
        if neg:
            result['kewarganegaraan'] = neg

        # Tanggal lahir YYMMDD (posisi 13-18)
        dob = line2[13:19]
        if re.match(r'\d{6}', dob):
            yy   = int(dob[:2])
            year = 1900 + yy if yy > 30 else 2000 + yy
            result['tanggal_lahir'] = f"{dob[4:6]}/{dob[2:4]}/{year}"

        # Masa berlaku YYMMDD (posisi 19-24)
        exp = line2[19:25]
        if re.match(r'\d{6}', exp):
            year_exp = 2000 + int(exp[:2])
            result['masa_berlaku'] = f"{exp[4:6]}/{exp[2:4]}/{year_exp}"

    except Exception:
        pass

    return result

def extract_from_text(text: str) -> dict:
    """Ekstrak data dari teks hasil OCR secara lebih agresif."""
    result = {}
    lines  = [l.strip() for l in text.split('\n') if l.strip()]
    full   = ' '.join(lines)

    # ── 1. COBA MRZ DULU ──────────────────────────────────────
    # MRZ paspor: baris yang mengandung banyak huruf kapital dan 
    mrz_lines = [l for l in lines if len(l) >= 30 and
                 sum(c.isalpha() or c.isdigit() or c == '<' for c in l) / len(l) > 0.85]

    if len(mrz_lines) >= 2:
        mrz_result = parse_mrz(mrz_lines[-2:])  # ambil 2 baris terakhir
        if mrz_result.get('nama'):
            result.update(mrz_result)

    # ── 2. NOMOR PASPOR ───────────────────────────────────────
    # Format: huruf kapital diikuti 6-8 angka, contoh: A1234567 atau B12345678
    if not result.get("nomor_paspor"):
        patterns = [
            r'\b([A-Z]{1,2}[0-9]{6,8})\b',        # standar
            r'(?:No\.?|Number|Passport)[:\s]*([A-Z]{1,2}[0-9]{6,8})',  # setelah label
        ]
        for pat in patterns:
            m = re.search(pat, full, re.IGNORECASE)
            if m:
                result['nomor_paspor'] = m.group(1).upper()
                break

    # ── 3. NAMA ───────────────────────────────────────────────
    if not result.get("nama"):
        # Cari setelah label "Surname" / "Given name" / "Name"
        patterns_nama = [
            r'(?:Surname|Family name)[:\s/]+([A-Z][A-Z\s]+)',
            r'(?:Given name[s]?|First name)[:\s/]+([A-Z][A-Z\s]+)',
            r'(?:Name|Nama)[:\s]+([A-Z][A-Z\s]{3,})',
        ]
        for pat in patterns_nama:
            m = re.search(pat, full, re.IGNORECASE)
            if m:
                nama_raw = m.group(1).strip()
                # Bersihkan karakter aneh
                nama_bersih = re.sub(r'[^A-Za-z\s]', '', nama_raw).strip()
                if len(nama_bersih) > 2:
                    result['nama'] = nama_bersih.upper()
                    break

        # Fallback: cari baris yang semua huruf kapital dan panjang (kemungkinan nama)
        if not result.get("nama"):
            for line in lines:
                line_clean = re.sub(r'[^A-Za-z\s]', '', line).strip()
                words = line_clean.split()
                if (len(words) >= 2 and
                    line_clean == line_clean.upper() and
                    all(len(w) >= 2 for w in words) and
                    len(line_clean) >= 5 and
                    not any(kw in line_clean for kw in [
                        'PASSPORT', 'REPUBLIC', 'INDONESIA', 'SURNAME',
                        'GIVEN', 'NATIONALITY', 'DATE', 'BIRTH', 'EXPIRY',
                        'PLACE', 'SEX', 'MALE', 'FEMALE', 'TYPE', 'CODE'
                    ])):
                    result['nama'] = line_clean.strip()
                    break

    # ── 4. KEWARGANEGARAAN ────────────────────────────────────
    if not result.get("kewarganegaraan"):
        m = re.search(
            r'\b(IDN|MYS|SGP|PHL|THA|VNM|CHN|IND|PAK|BGD|LKA|NPL|MMR|KHM|'
            r'USA|GBR|AUS|NZL|CAN|DEU|FRA|NLD|JPN|KOR|SAU|ARE|QAT|EGY|TUR|'
            r'NGA|GHA|KEN|ETH|ZAF|SDN|SOM|BNG|AFG|IRN|IRQ|SYR|JOR|LBN)\b',
            full
        )
        if m:
            result['kewarganegaraan'] = m.group(1)

    # ── 5. TANGGAL (sudah biasanya terdeteksi, ini backup) ────
    date_patterns = [
        r'\b(\d{2}/\d{2}/\d{4})\b',
        r'\b(\d{2}-\d{2}-\d{4})\b',
        r'\b(\d{1,2}\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+\d{4})\b',
    ]
    dates_found = []
    for pat in date_patterns:
        dates_found += re.findall(pat, full, re.IGNORECASE)

    if len(dates_found) >= 1 and not result.get('tanggal_lahir'):
        result['tanggal_lahir'] = dates_found[0]
    if len(dates_found) >= 2 and not result.get('masa_berlaku'):
        result['masa_berlaku'] = dates_found[-1]

    return result

def run_ocr(image: Image.Image) -> dict:
    """Jalankan OCR dan kembalikan data terstruktur."""
    try:
        processed = preprocess_image(image)
    except Exception:
        processed = image.convert("L")  # Grayscale saja jika OpenCV tidak ada

    # OCR dengan berbagai konfigurasi
    configs = ['--oem 3 --psm 6']
    all_text = ""
    for cfg in configs:
        try:
            all_text += pytesseract.image_to_string(processed, config=cfg) + "\n"
        except Exception:
            pass

    # Coba MRZ dulu, lalu fallback ke teks bebas
    data = parse_mrz(all_text)
    if not data:
        data = extract_from_text(all_text)

    return data, all_text


# ============================================================
# VALIDASI DATA
# ============================================================
def validasi_nama(nama: str) -> tuple[bool, str]:
    """
    Validasi nama berdasarkan aturan INTIF.
    Returns: (valid: bool, pesan: str)
    """
    nama = nama.strip()
    if not nama:
        return False, "Nama tidak boleh kosong."

    # Pisahkan nama menjadi kata-kata
    kata = nama.split()
    n = len(kata)

    # 1 kata saja → invalid
    if n == 1:
        return False, (
            "⚠️ Peringatan: Nama hanya terdiri dari 1 suku kata. "
            "Mohon lakukan amandemen penambahan nama pada paspor Anda terlebih dahulu."
        )

    # Cek apakah ada singkatan/inisial (1-2 huruf diikuti titik ATAU 1 huruf saja)
    def is_inisial(kata_: str) -> bool:
        # Inisial: 1 huruf saja, ATAU 1-2 huruf diikuti titik
        if re.match(r'^[A-Za-z]\.$', kata_):  # misal "A." atau "B."
            return True
        if re.match(r'^[A-Za-z]{2}\.$', kata_):  # misal "MD."
            return True
        if re.match(r'^[A-Za-z]$', kata_):  # misal "A" (tanpa titik)
            return True
        return False

    def is_pengecualian_muh(kata_: str) -> bool:
        return kata_.rstrip('.').upper() in ('MUH', 'MUHAMAD', 'MUHAMMAD')

    # Cek kata depan dan kata belakang
    depan = kata[0]
    belakang = kata[-1]

    if n == 2:
        # Jika 2 kata: cek apakah salah satunya adalah inisial (bukan pengecualian Muh)
        if is_inisial(depan) and not is_pengecualian_muh(depan):
            return False, (
                "⚠️ Peringatan: Nama terdiri dari 2 suku kata dengan inisial/singkatan di depan. "
                "Mohon lakukan amandemen penambahan nama pada paspor Anda terlebih dahulu."
            )
        if is_inisial(belakang) and not is_pengecualian_muh(belakang):
            return False, (
                "⚠️ Peringatan: Nama terdiri dari 2 suku kata dengan inisial/singkatan di belakang. "
                "Mohon lakukan amandemen penambahan nama pada paspor Anda terlebih dahulu."
            )

    # 3+ kata: nama dianggap valid (kecuali inisial di depan/belakang jika perlu)
    return True, "✓ Nama valid."


def validasi_masa_berlaku(masa_berlaku_str: str) -> tuple[bool, str]:
    """
    Validasi masa berlaku paspor.
    Returns: (valid: bool, pesan: str)
    """
    if not masa_berlaku_str:
        return False, "Masa berlaku paspor tidak boleh kosong."

    # Ekstrak tahun dari berbagai format tanggal
    tahun_match = re.search(r'\b(20\d{2}|19\d{2})\b', masa_berlaku_str)
    if not tahun_match:
        return False, "Format tanggal masa berlaku tidak dikenali."

    tahun = int(tahun_match.group(1))

    if tahun < 2027:
        return False, (
            f"⚠️ Peringatan: Masa berlaku paspor berakhir tahun {tahun} (kurang dari 2027). "
            "Mohon lakukan perpanjangan (renewal) paspor Anda terlebih dahulu."
        )

    return True, f"✓ Masa berlaku valid hingga tahun {tahun}."


# ============================================================
# SESSION STATE INIT
# ============================================================
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'ocr_data' not in st.session_state:
    st.session_state.ocr_data = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False


# ============================================================
# UI HEADER
# ============================================================
st.markdown("""
<div class="intif-header">
    <div class="badge">🛂 INTIF Official</div>
    <h1>Perpanjangan Izin Tinggal</h1>
    <p>Immigration Tracking &amp; Information Facility &nbsp;|&nbsp; Formulir Digital Resmi</p>
</div>
""", unsafe_allow_html=True)

# Step Indicator
steps_html = '<div class="steps">'
step_labels = ["Upload Paspor", "Verifikasi Data", "Konfirmasi"]
for i, label in enumerate(step_labels, start=1):
    cls = "done" if st.session_state.step > i else ("active" if st.session_state.step == i else "")
    icon = "✓" if st.session_state.step > i else str(i)
    steps_html += f'<div class="step {cls}"><div class="step-dot">{icon}</div>{label}</div>'
steps_html += '</div>'
st.markdown(steps_html, unsafe_allow_html=True)


# ============================================================
# STEP 1 — UPLOAD PASPOR
# ============================================================
if st.session_state.step == 1:
    st.markdown("""
    <div class="card">
        <div class="card-title">📷 Upload Foto Halaman Biodata Paspor</div>
        <div class="card-sub">Pastikan foto jelas, tidak blur, dan seluruh halaman biodata terlihat lengkap.</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Pilih foto dari galeri, atau ambil foto langsung (HP)",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        help="Ukuran maksimum: 20MB. Format: JPG, PNG, WEBP."
    )

    if uploaded:
        img = Image.open(uploaded)
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image(img, caption="Pratinjau foto paspor Anda", width=400)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Proses & Ekstrak Data Otomatis", key="btn_ocr"):
            with st.spinner("Membaca data paspor... Mohon tunggu (5-10 detik)"):
                data, raw_text = run_ocr(img)
                # DEBUG — tampilkan hasil mentah
                st.write("**Data OCR:**", data)
                st.write("**Teks mentah:**", raw_text)
                st.session_state.ocr_data = data
                st.session_state.step     = 2
                st.rerun()
    else:
        st.info("💡 **Tips:** Gunakan browser HP Anda untuk langsung mengambil foto kamera, atau pilih foto dari galeri.")


# ============================================================
# STEP 2 — REVIEW & VALIDASI
# ============================================================
elif st.session_state.step == 2:
    ocr = st.session_state.ocr_data

    st.markdown("""
    <div class="card">
        <div class="card-title">📋 Review & Lengkapi Data</div>
        <div class="card-sub">Periksa data berikut. Koreksi jika ada yang salah, lalu isi kolom tambahan.</div>
    </div>
    """, unsafe_allow_html=True)

    # Simpan nilai form ke session state agar tidak konflik
    if 'nama' not in st.session_state:
        st.session_state.nama = ocr.get("nama", "")
    if 'nomor_paspor' not in st.session_state:
        st.session_state.nomor_paspor = ocr.get("nomor_paspor", "")
    if 'tanggal_lahir' not in st.session_state:
        st.session_state.tanggal_lahir = ocr.get("tanggal_lahir", "")
    if 'kewarganegaraan' not in st.session_state:
        st.session_state.kewarganegaraan = ocr.get("kewarganegaraan", "")
    if 'masa_berlaku' not in st.session_state:
        st.session_state.masa_berlaku = ocr.get("masa_berlaku", "")
    if 'nomor_hp' not in st.session_state:
        st.session_state.nomor_hp = ""
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'keperluan' not in st.session_state:
        st.session_state.keperluan = ""

    st.markdown("**— Data Paspor (dari OCR) —**")

    nama         = st.text_input("Nama Lengkap (sesuai paspor)", key="nama")
    nomor_paspor = st.text_input("Nomor Paspor", key="nomor_paspor")
    tanggal_lahir= st.text_input("Tanggal Lahir (DD/MM/YYYY)", key="tanggal_lahir")
    kewarganegaraan = st.text_input("Kewarganegaraan", key="kewarganegaraan")
    masa_berlaku = st.text_input("Masa Berlaku Paspor (DD/MM/YYYY)", key="masa_berlaku")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**— Data Tambahan —**")

    nomor_hp = st.text_input("Nomor HP / WhatsApp (aktif)", key="nomor_hp")
    email    = st.text_input("Alamat Email", key="email")
    keperluan= st.text_input("Keperluan / Tujuan Tinggal", key="keperluan")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✅ Validasi & Lanjutkan", key="btn_validasi"):
        valid_nama, msg_nama   = validasi_nama(nama)
        valid_exp,  msg_exp    = validasi_masa_berlaku(masa_berlaku)

        errors = []
        if not valid_nama:
            errors.append(msg_nama)
        if not valid_exp:
            errors.append(msg_exp)
        if not nomor_paspor.strip():
            errors.append("⚠️ Nomor paspor tidak boleh kosong.")
        if not tanggal_lahir.strip():
            errors.append("⚠️ Tanggal lahir tidak boleh kosong.")
        if not nomor_hp.strip():
            errors.append("⚠️ Nomor HP tidak boleh kosong.")

        if errors:
            for err in errors:
                st.markdown(f'<div class="alert-danger">{err}</div>', unsafe_allow_html=True)
        else:
            # Gunakan key berbeda agar tidak konflik dengan widget
            st.session_state['fd_nama']            = nama
            st.session_state['fd_nomor_paspor']    = nomor_paspor
            st.session_state['fd_tanggal_lahir']   = tanggal_lahir
            st.session_state['fd_kewarganegaraan'] = kewarganegaraan
            st.session_state['fd_masa_berlaku']    = masa_berlaku
            st.session_state['fd_nomor_hp']        = nomor_hp
            st.session_state['fd_email']           = email
            st.session_state['fd_keperluan']       = keperluan
            st.session_state.step = 3
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Kembali & Upload Ulang", key="btn_kembali2"):
        # Bersihkan session agar form reset
        for k in ['nama','nomor_paspor','tanggal_lahir','kewarganegaraan',
                  'masa_berlaku','nomor_hp','email','keperluan']:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state.step = 1
        st.rerun()

# ============================================================
# STEP 3 — KONFIRMASI & SUBMIT
# ============================================================
elif st.session_state.step == 3:
    if not st.session_state.submitted:
        fd = {
            "nama":            st.session_state.get('fd_nama', ''),
            "nomor_paspor":    st.session_state.get('fd_nomor_paspor', ''),
            "tanggal_lahir":   st.session_state.get('fd_tanggal_lahir', ''),
            "kewarganegaraan": st.session_state.get('fd_kewarganegaraan', ''),
            "masa_berlaku":    st.session_state.get('fd_masa_berlaku', ''),
            "nomor_hp":        st.session_state.get('fd_nomor_hp', ''),
            "email":           st.session_state.get('fd_email', ''),
            "keperluan":       st.session_state.get('fd_keperluan', ''),
        }

        st.markdown("""
        <div class="card fade-in">
            <div class="card-title">✅ Konfirmasi Data</div>
            <div class="card-sub">Pastikan semua data sudah benar sebelum mengirim.</div>
        </div>
        """, unsafe_allow_html=True)

        # Ringkasan data
        def row(label, val):
            return f"<tr><td style='padding:8px 12px;font-size:0.82rem;color:#6b7588;font-weight:600;width:45%;'>{label}</td><td style='padding:8px 12px;font-size:0.88rem;color:#0B1F3A;font-weight:500;'>{val or '—'}</td></tr>"

        table = f"""
        <div class="card" style="padding:8px 0;">
        <table style="width:100%;border-collapse:collapse;">
            {row("Nama Lengkap", fd['nama'])}
            {row("Nomor Paspor", fd['nomor_paspor'])}
            {row("Tanggal Lahir", fd['tanggal_lahir'])}
            {row("Kewarganegaraan", fd['kewarganegaraan'])}
            {row("Masa Berlaku", fd['masa_berlaku'])}
            {row("Nomor HP", fd['nomor_hp'])}
            {row("Email", fd['email'])}
            {row("Keperluan", fd['keperluan'])}
        </table>
        </div>
        """
        st.markdown(table, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Edit Data"):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button("📤 KIRIM PERMOHONAN"):
                with st.spinner("Mengirim data ke sistem..."):
                    ok, msg = append_to_sheet(fd)
                    if ok:
                        st.session_state.submitted = True
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                        st.info("💡 Jika belum setup Google Sheets, ikuti panduan di README.md")
    else:
        # Halaman sukses
        st.markdown("""
        <div class="card fade-in" style="text-align:center;padding:40px 28px;">
            <div style="font-size:3rem;margin-bottom:16px;">🎉</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.4rem;color:#0B1F3A;font-weight:700;margin-bottom:10px;">
                Permohonan Berhasil Dikirim!
            </div>
            <div style="font-size:0.88rem;color:#6b7588;line-height:1.7;margin-bottom:24px;">
                Data Anda telah tercatat dalam sistem INTIF.<br>
                Tim kami akan menghubungi Anda melalui nomor HP yang terdaftar.
            </div>
            <div class="alert-success">✓ Data tersimpan otomatis ke Google Sheets INTIF</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Buat Permohonan Baru"):
            for key in ['step', 'ocr_data', 'form_data', 'submitted']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.step = 1
            st.rerun()

# Footer
st.markdown("""
<div class="footer">
    © 2025 INTIF — Immigration Tracking & Information Facility<br>
    Sistem Digital Resmi Perpanjangan Izin Tinggal &nbsp;|&nbsp; Kerahasiaan data terjamin
</div>
""", unsafe_allow_html=True)
