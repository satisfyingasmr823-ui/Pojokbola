"""
Pemeriksaan otomatis untuk index.html.
- Script harus ada dan berisi JavaScript yang valid (dicek dengan Node).
- Setiap elemen yang dipanggil script (lewat $('id')) harus ada di HTML.
- Tidak boleh ada sisa penanda diff (@@) yang tertempel ke dalam kode.
Jalankan: python3 tools/check_app.py
"""
import pathlib, re, subprocess, sys, tempfile

root = pathlib.Path(__file__).resolve().parent.parent
html = (root / 'index.html').read_text(encoding='utf-8')
errors = []

m = re.search(r'<script>(.*)</script>', html, re.S)
if not m:
    errors.append('tag <script> tidak ditemukan')
    js = ''
else:
    js = m.group(1)

used = set(re.findall(r"\$\('([^']+)'\)", js))
declared = set(re.findall(r'id="([^"]+)"', html))
missing = sorted(used - declared)
if missing:
    errors.append('elemen tidak ada di HTML: ' + ', '.join(missing))

if re.search(r'^@@', html, re.M):
    errors.append('ada sisa penanda diff (@@) di index.html')

if js:
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(js)
        path = f.name
    r = subprocess.run(['node', '--check', path], capture_output=True, text=True)
    if r.returncode != 0:
        errors.append('sintaks JavaScript salah:\n' + r.stderr.strip())

if not (root / '.nojekyll').exists():
    errors.append('berkas .nojekyll tidak ada')

if errors:
    print('GAGAL:')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print(f'OK: {len(used)} elemen dipakai, semua tersedia; sintaks JavaScript valid.')
