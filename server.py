"""
Server lokal untuk Berita ke Video.
Menjalankan halaman aplikasi dan mengambil isi link berita langsung dari komputer kamu
(tanpa proxy pihak ketiga, jadi tidak diblokir oleh CORS).

Cara pakai:
  1. Pastikan Python 3 sudah terpasang.
  2. Simpan server.py dan index.html (atau berita-ke-video.html) di folder yang sama.
  3. Jalankan:  python server.py
  4. Buka di browser: http://127.0.0.1:8000
"""
import http.server
import os
import socketserver
import urllib.parse
import urllib.request

PORT = 8000
HERE = os.path.dirname(os.path.abspath(__file__))
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')


def tts_engine():
    """Mesin suara yang tersedia di komputer ini: pyttsx3 (offline, suara sistem) atau gTTS (online)."""
    try:
        import pyttsx3  # noqa: F401
        return 'pyttsx3'
    except Exception:
        pass
    try:
        import gtts  # noqa: F401
        return 'gtts'
    except Exception:
        return None


def synthesize(text, voice):
    """Mengembalikan (bytes audio, content-type). voice: 'male' atau 'female'."""
    import io, os, re, tempfile
    engine = tts_engine()
    if engine == 'pyttsx3':
        import pyttsx3
        e = pyttsx3.init()
        e.setProperty('rate', 165)
        voices = e.getProperty('voices') or []
        want_male = voice == 'male'
        def is_id(v):
            langs = ' '.join(str(x) for x in (v.languages or []))
            return 'id' in langs.lower() or bool(re.search(r'indones|andika|ardi|gadis|damayanti', v.name or '', re.I))
        def is_male(v):
            return bool(re.search(r'andika|ardi|male|pria', v.name or '', re.I))
        cands = [v for v in voices if is_id(v)]
        pick = next((v for v in cands if is_male(v) == want_male), cands[0] if cands else None)
        if pick is not None:
            e.setProperty('voice', pick.id)
        fd, path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        try:
            e.save_to_file(text, path)
            e.runAndWait()
            with open(path, 'rb') as f:
                data = f.read()
        finally:
            os.remove(path)
        return data, 'audio/wav'
    if engine == 'gtts':
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text, lang='id').write_to_fp(buf)
        return buf.getvalue(), 'audio/mpeg'
    raise RuntimeError('mesin suara tidak terpasang (pasang pyttsx3 atau gTTS)')


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == '/fetch':
            target = urllib.parse.parse_qs(p.query).get('url', [''])[0]
            if not target.startswith(('http://', 'https://')):
                return self._send(400, b'url tidak valid', 'text/plain; charset=utf-8')
            try:
                req = urllib.request.Request(target, headers={
                    'User-Agent': UA,
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'id,en;q=0.8',
                })
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = r.read()
                    ctype = r.headers.get('Content-Type', 'text/html; charset=utf-8')
                self._send(200, data, ctype)
            except Exception as e:
                self._send(502, ('gagal mengambil: ' + str(e)).encode('utf-8'),
                           'text/plain; charset=utf-8')
        elif p.path == '/tts-status':
            import json
            body = json.dumps({'engine': tts_engine()}).encode('utf-8')
            self._send(200, body, 'application/json; charset=utf-8')
        elif p.path == '/tts':
            qs = urllib.parse.parse_qs(p.query)
            text = qs.get('text', [''])[0].strip()[:1000]
            voice = qs.get('voice', ['female'])[0]
            if not text:
                return self._send(400, b'teks kosong', 'text/plain; charset=utf-8')
            try:
                data, ctype = synthesize(text, voice)
                self._send(200, data, ctype)
            except Exception as e:
                self._send(503, str(e).encode('utf-8'), 'text/plain; charset=utf-8')
        elif p.path == '/image':
            target = urllib.parse.parse_qs(p.query).get('url', [''])[0]
            if not target.startswith(('http://', 'https://')):
                return self._send(400, b'url tidak valid', 'text/plain; charset=utf-8')
            try:
                origin = urllib.parse.urlparse(target)
                req = urllib.request.Request(target, headers={
                    'User-Agent': UA,
                    'Accept': 'image/*',
                    'Referer': f'{origin.scheme}://{origin.netloc}/',
                })
                with urllib.request.urlopen(req, timeout=20) as r:
                    ctype = r.headers.get('Content-Type', '')
                    data = r.read(12 * 1024 * 1024)
                if not ctype.startswith('image/'):
                    return self._send(415, b'bukan gambar', 'text/plain; charset=utf-8')
                self._send(200, data, ctype)
            except Exception as e:
                self._send(502, ('gagal mengambil gambar: ' + str(e)).encode('utf-8'),
                           'text/plain; charset=utf-8')
        elif p.path in ('/', '/index.html', '/berita-ke-video.html'):
            page = next((os.path.join(HERE, n) for n in ('index.html', 'berita-ke-video.html')
                         if os.path.exists(os.path.join(HERE, n))), None)
            if page is None:
                return self._send(404, b'berkas aplikasi tidak ditemukan', 'text/plain; charset=utf-8')
            with open(page, 'rb') as f:
                self._send(200, f.read(), 'text/html; charset=utf-8')
        else:
            self._send(404, b'tidak ditemukan', 'text/plain; charset=utf-8')

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(('127.0.0.1', PORT), Handler) as srv:
        print(f'Berita ke Video berjalan di http://127.0.0.1:{PORT}  (Ctrl+C untuk berhenti)')
        srv.serve_forever()
