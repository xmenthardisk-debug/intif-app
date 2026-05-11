import streamlit as st
import re
import json
import base64
import io
from datetime import datetime
from PIL import Image
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
}
.card-sub {
    font-size: 0.80rem;
    color: #6b7588;
    margin-bottom: 18px;
}

.steps {
    display: flex;
    gap: 0;
    margin-bottom: 28px;
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

[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    background: #FAFAF8 !important;
    padding: 12px !important;
}

.stTextInput > div > div > input {
    border-radius: 8px !important;
    border: 1.5px solid var(--border) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.90rem !important;
    color: var(--navy) !important;
    background: #FAFAF8 !important;
    padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus {
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

hr { border-color: var(--border) !important; margin: 20px 0 !important; }

.footer {
    text-align: center;
    font-size: 0.74rem;
    color: #9aa3b2;
    margin-top: 32px;
    padding-bottom: 20px;
    line-height: 1.7;
}

@keyframes fadeIn {
    from { opacity:0; transform:translateY(12px); }
    to   { opacity:1; transform:translateY(0); }
}
.fade-in { animation: fadeIn 0.5s ease; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# GOOGLE SHEETS — KONEKSI & SIMPAN DATA
# ============================================================
SHEET_NAME = "INTIF - Data Perpanjangan Izin Tinggal"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_gsheet_client():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    except Exception:
        try:
            creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        except FileNotFoundError:
            return None
    return gspread.authorize(creds)

def append_to_sheet(data: dict):
    client = get_gsheet_client()
    if client is None:
        return False, "File credentials.json tidak ditemukan."
    try:
        sheet = client.open(SHEET_NAME).sheet1
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
        return True, "Data berhasil disimpan ✓"
    except Exception as e:
        return False, f"Gagal menyimpan ke Sheets: {str(e)}"


# ============================================================
# OCR — GOOGLE CLOUD VISION API
# ============================================================
def parse_mrz(mrz_lines: list) -> dict:
    """Parse MRZ paspor standar ICAO (2 baris x 44 karakter)."""
    result = {}
    try:
        line1 = mrz_lines[0].ljust(44, '<')[:44]
        line2 = mrz_lines[1].ljust(44, '<')[:44]

        # Nama (baris 1, posisi 5-44)
        name_raw = line1[5:44]
        parts    = name_raw.split('<<')
        surname  = parts[0].replace('<', ' ').strip()
        given    = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ''
        result['nama'] = f"{surname} {given}".strip()

        # Nomor paspor & kewarganegaraan (baris 2)
        result['nomor_paspor']    = line2[0:9].replace('<', '').strip()
        result['kewarganegaraan'] = line2[10:13].replace('<', '').strip()

        # Tanggal lahir YYMMDD
        dob = line2[13:19]
        if re.match(r'\d{6}', dob):
            yy   = int(dob[:2])
            year = 1900 + yy if yy > 30 else 2000 + yy
            result['tanggal_lahir'] = f"{dob[4:6]}/{dob[2:4]}/{year}"

        # Masa berlaku YYMMDD
        exp = line2[19:25]
        if re.match(r'\d{6}', exp):
            year_exp = 2000 + int(exp[:2])
            result['masa_berlaku'] = f"{exp[4:6]}/{exp[2:4]}/{year_exp}"

    except Exception:
        pass
    return result


def extract_from_text(text: str) -> dict:
    """Ekstrak data dari teks bebas hasil OCR (fallback dari MRZ)."""
    result = {}
    lines  = [l.strip() for l in text.split('\n') if l.strip()]
    full   = ' '.join(lines)

    # Coba MRZ dulu
    mrz_lines = [l for l in lines if re.match(r'^[A-Z0-9<]{30,}$', l)]
    if len(mrz_lines) >= 2:
        result = parse_mrz(mrz_lines)

    # Fallback — nomor paspor
    if not result.get("nomor_paspor"):
        m = re.search(r'\b([A-Z]{1,2}\d{6,8})\b', full)
        if m:
            result['nomor_paspor'] = m.group(1)

    # Fallback — nama
    if not result.get("nama"):
        m = re.search(r'(?:Name|Nama)[:\s]+([A-Z][A-Z\s]+)', full, re.IGNORECASE)
        if m:
            result['nama'] = m.group(1).strip()

    # Fallback — kewarganegaraan
    if not result.get("kewarganegaraan"):
        m = re.search(
            r'\b(IDN|MYS|SGP|PHL|THA|VNM|CHN|IND|PAK|BGD|LKA|NPL|MMR|'
            r'USA|GBR|AUS|NZL|CAN|DEU|FRA|NLD|JPN|KOR|SAU|ARE|QAT|EGY)\b',
            full
        )
        if m:
            result['kewarganegaraan'] = m.group(1)

    # Fallback — tanggal
    dates = re.findall(
        r'\b(\d{2}[\s/-]\w{3}[\s/-]\d{4}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})\b',
        full
    )
    if len(dates) >= 1:
        result.setdefault('tanggal_lahir', dates[0])
    if len(dates) >= 2:
        result.setdefault('masa_berlaku', dates[-1])

    return result


def run_ocr(image: Image.Image) -> tuple:
    """Ekstrak data paspor menggunakan Google Cloud Vision API."""
    from google.cloud import vision

    # Load credentials
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict)
    except Exception:
        try:
            creds = Credentials.from_service_account_file("credentials.json")
        except Exception as e:
            return {}, f"Credentials error: {str(e)}"

    try:
        client = vision.ImageAnnotatorClient(credentials=creds)

        # Resize jika terlalu besar
        w, h = image.size
        if w > 2000 or h > 2000:
            ratio = min(2000/w, 2000/h)
            image = image.resize((int(w*ratio), int(h*ratio)), Image.LANCZOS)

        # Konversi ke bytes
        buffer  = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        content = buffer.getvalue()

        vision_image = vision.Image(content=content)
        response     = client.text_detection(image=vision_image)

        if response.error.message:
            return {}, f"Vision API error: {response.error.message}"

        full_text = response.full_text_annotation.text
        data      = extract_from_text(full_text)
        return data, full_text

    except Exception as e:
        return {}, f"OCR error: {str(e)}"


# ============================================================
# VALIDASI
# ============================================================
def validasi_nama(nama: str) -> tuple:
    nama = nama.strip()
    if not nama:
        return False, "Nama tidak boleh kosong."

    kata = nama.split()
    n    = len(kata)

    if n == 1:
        return False, (
            "⚠️ Peringatan: Nama hanya terdiri dari 1 suku kata. "
            "Mohon lakukan amandemen penambahan nama pada paspor Anda terlebih dahulu."
        )

    def is_inisial(k):
        return bool(
            re.match(r'^[A-Za-z]\.$', k) or
            re.match(r'^[A-Za-z]{2}\.$', k) or
            re.match(r'^[A-Za-z]$', k)
        )

    def is_muh(k):
        return k.rstrip('.').upper() in ('MUH', 'MUHAMAD', 'MUHAMMAD')

    if n == 2:
        if is_inisial(kata[0]) and not is_muh(kata[0]):
            return False, (
                "⚠️ Peringatan: Nama terdiri dari 2 suku kata dengan inisial di depan. "
                "Mohon lakukan amandemen penambahan nama pada paspor Anda terlebih dahulu."
            )
        if is_inisial(kata[-1]) and not is_muh(kata[-1]):
            return False, (
                "⚠️ Peringatan: Nama terdiri dari 2 suku kata dengan inisial di belakang. "
                "Mohon lakukan amandemen penambahan nama pada paspor Anda terlebih dahulu."
            )

    return True, "✓ Nama valid."


def validasi_masa_berlaku(masa_berlaku_str: str) -> tuple:
    if not masa_berlaku_str:
        return False, "Masa berlaku paspor tidak boleh kosong."

    m = re.search(r'\b(20\d{2}|19\d{2})\b', masa_berlaku_str)
    if not m:
        return False, "Format tanggal masa berlaku tidak dikenali."

    tahun = int(m.group(1))
    if tahun < 2027:
        return False, (
            f"⚠️ Peringatan: Masa berlaku paspor berakhir tahun {tahun} (kurang dari 2027). "
            "Mohon lakukan perpanjangan (renewal) paspor Anda terlebih dahulu."
        )

    return True, f"✓ Masa berlaku valid hingga tahun {tahun}."


# ============================================================
# SESSION STATE
# ============================================================
if 'step'      not in st.session_state: st.session_state.step      = 1
if 'ocr_data'  not in st.session_state: st.session_state.ocr_data  = {}
if 'submitted' not in st.session_state: st.session_state.submitted = False


# ============================================================
# HEADER & STEP INDICATOR
# ============================================================
st.markdown("""
<div class="intif-header">
    <div class="badge">🛂 INTIF Official</div>
    <h1>Perpanjangan Izin Tinggal</h1>
    <p>Immigration Tracking &amp; Information Facility &nbsp;|&nbsp; Formulir Digital Resmi</p>
</div>
""", unsafe_allow_html=True)

steps_html  = '<div class="steps">'
step_labels = ["Upload Paspor", "Verifikasi Data", "Konfirmasi"]
for i, label in enumerate(step_labels, start=1):
    cls  = "done"   if st.session_state.step > i else ("active" if st.session_state.step == i else "")
    icon = "✓"      if st.session_state.step > i else str(i)
    steps_html += f'<div class="step {cls}"><div class="step-dot">{icon}</div>{label}</div>'
steps_html += '</div>'
st.markdown(steps_html, unsafe_allow_html=True)


# ============================================================
# STEP 1 — UPLOAD FOTO
# ============================================================
if st.session_state.step == 1:
    st.markdown("""
    <div class="card">
        <div class="card-title">📷 Upload Foto Halaman Biodata Paspor</div>
        <div class="card-sub">Pastikan foto jelas, tidak blur, dan seluruh halaman biodata terlihat — termasuk 2 baris kode MRZ di bagian bawah halaman paspor.</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Pilih foto dari galeri atau ambil foto langsung (HP)",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        help="Format: JPG, PNG, WEBP. Pastikan pencahayaan cukup terang."
    )

    if uploaded:
        img = Image.open(uploaded)
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image(img, caption="Pratinjau foto paspor", width=400)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Proses & Ekstrak Data Otomatis", key="btn_ocr"):
            with st.spinner("Membaca data paspor... Mohon tunggu (5-10 detik)"):
                data, raw_text = run_ocr(img)
                st.session_state.ocr_data = data
                st.session_state.step     = 2
                st.rerun()
    else:
        st.info("💡 **Tips:** Di HP, klik tombol upload lalu pilih **'Camera'** untuk langsung foto paspor Anda.")


# ============================================================
# STEP 2 — REVIEW & VALIDASI
# ============================================================
elif st.session_state.step == 2:
    ocr = st.session_state.ocr_data

    st.markdown("""
    <div class="card">
        <div class="card-title">📋 Review & Lengkapi Data</div>
        <div class="card-sub">Periksa data hasil scan. Koreksi jika ada yang salah atau kosong, lalu isi data tambahan di bawah.</div>
    </div>
    """, unsafe_allow_html=True)

    # Isi nilai awal dari OCR ke session state (hanya jika belum ada)
    defaults = {
        'nama':            ocr.get("nama", ""),
        'nomor_paspor':    ocr.get("nomor_paspor", ""),
        'tanggal_lahir':   ocr.get("tanggal_lahir", ""),
        'kewarganegaraan': ocr.get("kewarganegaraan", ""),
        'masa_berlaku':    ocr.get("masa_berlaku", ""),
        'nomor_hp':        "",
        'email':           "",
        'keperluan':       "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    st.markdown("**— Data Paspor (hasil scan, periksa & koreksi jika perlu) —**")
    nama            = st.text_input("Nama Lengkap (sesuai paspor)",     key="nama")
    nomor_paspor    = st.text_input("Nomor Paspor",                     key="nomor_paspor")
    tanggal_lahir   = st.text_input("Tanggal Lahir (DD/MM/YYYY)",       key="tanggal_lahir")
    kewarganegaraan = st.text_input("Kewarganegaraan (contoh: IDN)",    key="kewarganegaraan")
    masa_berlaku    = st.text_input("Masa Berlaku Paspor (DD/MM/YYYY)", key="masa_berlaku")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**— Data Tambahan —**")
    nomor_hp  = st.text_input("Nomor HP / WhatsApp (aktif)", key="nomor_hp")
    email     = st.text_input("Alamat Email",                key="email")
    keperluan = st.text_input("Keperluan / Tujuan Tinggal",  key="keperluan")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✅ Validasi & Lanjutkan", key="btn_validasi"):
        valid_nama, msg_nama = validasi_nama(nama)
        valid_exp,  msg_exp  = validasi_masa_berlaku(masa_berlaku)

        errors = []
        if not valid_nama:               errors.append(msg_nama)
        if not valid_exp:                errors.append(msg_exp)
        if not nomor_paspor.strip():     errors.append("⚠️ Nomor paspor tidak boleh kosong.")
        if not tanggal_lahir.strip():    errors.append("⚠️ Tanggal lahir tidak boleh kosong.")
        if not nomor_hp.strip():         errors.append("⚠️ Nomor HP tidak boleh kosong.")

        if errors:
            for err in errors:
                st.markdown(f'<div class="alert-danger">{err}</div>', unsafe_allow_html=True)
        else:
            # Simpan dengan prefix fd_ agar tidak konflik dengan key widget
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
            <div class="card-sub">Pastikan semua data sudah benar sebelum mengirim permohonan.</div>
        </div>
        """, unsafe_allow_html=True)

        def row(label, val):
            return (
                f"<tr>"
                f"<td style='padding:10px 14px;font-size:0.82rem;color:#6b7588;"
                f"font-weight:600;width:45%;border-bottom:1px solid #f0ece4;'>{label}</td>"
                f"<td style='padding:10px 14px;font-size:0.88rem;color:#0B1F3A;"
                f"font-weight:500;border-bottom:1px solid #f0ece4;'>{val or '—'}</td>"
                f"</tr>"
            )

        st.markdown(f"""
        <div class="card" style="padding:8px 0;">
        <table style="width:100%;border-collapse:collapse;">
            {row("Nama Lengkap",    fd['nama'])}
            {row("Nomor Paspor",    fd['nomor_paspor'])}
            {row("Tanggal Lahir",   fd['tanggal_lahir'])}
            {row("Kewarganegaraan", fd['kewarganegaraan'])}
            {row("Masa Berlaku",    fd['masa_berlaku'])}
            {row("Nomor HP",        fd['nomor_hp'])}
            {row("Email",           fd['email'])}
            {row("Keperluan",       fd['keperluan'])}
        </table>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Edit Data", key="btn_edit"):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button("📤 KIRIM PERMOHONAN", key="btn_submit"):
                with st.spinner("Mengirim data ke sistem INTIF..."):
                    ok, msg = append_to_sheet(fd)
                    if ok:
                        st.session_state.submitted = True
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    else:
        st.markdown("""
        <div class="card fade-in" style="text-align:center;padding:48px 28px;">
            <div style="font-size:3.5rem;margin-bottom:16px;">🎉</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.5rem;
                        color:#0B1F3A;font-weight:700;margin-bottom:12px;">
                Permohonan Berhasil Dikirim!
            </div>
            <div style="font-size:0.88rem;color:#6b7588;line-height:1.8;margin-bottom:28px;">
                Data Anda telah tercatat dalam sistem INTIF.<br>
                Tim kami akan menghubungi Anda melalui nomor HP yang terdaftar<br>
                dalam waktu 1x24 jam kerja.
            </div>
            <div class="alert-success">✓ Data tersimpan otomatis ke Google Sheets INTIF</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Buat Permohonan Baru", key="btn_reset"):
            keys_to_clear = [
                'step', 'ocr_data', 'submitted',
                'nama', 'nomor_paspor', 'tanggal_lahir', 'kewarganegaraan',
                'masa_berlaku', 'nomor_hp', 'email', 'keperluan',
                'fd_nama', 'fd_nomor_paspor', 'fd_tanggal_lahir',
                'fd_kewarganegaraan', 'fd_masa_berlaku',
                'fd_nomor_hp', 'fd_email', 'fd_keperluan',
            ]
            for k in keys_to_clear:
                if k in st.session_state:
                    del st.session_state[k]
            st.session_state.step = 1
            st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="footer">
    © 2025 INTIF — Immigration Tracking & Information Facility<br>
    Sistem Digital Resmi Perpanjangan Izin Tinggal &nbsp;|&nbsp; Kerahasiaan data terjamin
</div>
""", unsafe_allow_html=True)
