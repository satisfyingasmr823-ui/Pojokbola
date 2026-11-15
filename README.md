# Pojokbola Video Maker

Ubah berita bola dari Pojokbola.web.id (atau sumber lain) menjadi video vertikal 9:16 untuk Facebook Reels dan YouTube Shorts.
Teks dan gambar diambil dari artikel, naskah dibacakan dengan suara bahasa Indonesia,
dan musik latar dibuat langsung oleh browser sehingga bebas hak cipta.

## Fitur

- Ambil judul, paragraf, dan gambar dari link berita (tombol **Ambil Isi dari Link**)
- Kotak teks terisi otomatis dan bisa diedit sebelum video dibuat
- Satu gambar thumbnail artikel dipakai sebagai latar seluruh video (jika tidak ada, dicari di Wikimedia Commons)
- Ganti atau hapus gambar tiap slide jika ingin memakai gambar lain (dari file atau link)
- Format **Bola** (Hook, Inti, Fakta, Dampak, Penutup) tanpa batas durasi, atau **Bebas**
- Subtitle (.srt) dan naskah (.txt) untuk caption atau voice-over
- Narasi dengan teks yang menyorot kata yang sedang dibacakan
- Musik latar: Bola (stadion, default), Energik, Berita (serius), Santai, file musik sendiri, atau tanpa musik
- Rekam dan unduh video 1080×1920 (MP4 jika didukung, jika tidak WebM)

## Pemasangan di GitHub (otomatis)

1. Buat repository baru di GitHub, misalnya `pojokbola-video`.
2. Unggah semua berkas di folder ini, termasuk folder `.github` dan `tools`.
3. Buka **Settings → Pages**, lalu pilih **Source: GitHub Actions**.
4. Setiap kali ada perubahan di branch `main`, workflow **Deploy ke GitHub Pages** berjalan otomatis
   dan memperbarui situs. Lihat hasilnya di tab **Actions**.
5. Setiap perubahan juga diperiksa oleh workflow **Pemeriksaan aplikasi**: sintaks JavaScript, elemen HTML,
   dan `server.py`. Jika gagal, perbaiki sebelum digabungkan.

Pemeriksaan bisa dijalankan manual di komputer: `python3 tools/check_app.py`

Catatan: GitHub Pages hanya menjalankan halaman statis. Karena itu pengambilan isi link di situs online
memakai layanan proxy publik. Untuk hasil paling andal, jalankan `server.py` di komputer sendiri.

## Cara pakai

### Mode 1: Buka langsung (GitHub Pages)

Halaman bisa dibuka dari `https://USERNAME.github.io/NAMA-REPO/`.
Pengambilan isi link memakai layanan proxy publik, yang kadang gagal.
Jika gagal, tempel teks berita secara manual di kotak "Teks berita".

### Mode 2: Jalankan lokal (disarankan)

Mode ini paling andal karena pengambilan link berjalan dari komputermu sendiri.

1. Pastikan Python 3 terpasang.
2. Di folder ini, jalankan `python server.py` (Windows: `py server.py`).
3. Buka http://127.0.0.1:8000 di Chrome atau Edge.

## Narasi suara masuk ke video (disarankan)

Narasi dibuat oleh `server.py` sebagai file audio, lalu dicampur langsung ke video.
Dengan cara ini suara pasti ikut terunduh, dan kamu tidak perlu berbagi tab.

1. Pasang Python 3 dan mesin suara, pilih salah satu:
   - Offline (suara sistem): `pip install pyttsx3`
     Di Windows, pastikan suara bahasa Indonesia terpasang (Settings → Time & language → Speech).
   - Online (suara Google): `pip install gTTS` (membutuhkan internet)
2. Jalankan `python server.py`, lalu buka http://127.0.0.1:8000
3. Jika halaman menampilkan "Narasi server aktif", klik **⬇ Buat & Unduh Otomatis**.
   Tidak ada jendela berbagi layar yang muncul.

Jika server tidak berjalan, aplikasi memakai suara browser dan kamu perlu memilih
**Bagikan audio tab** saat merekam.

## Merekam video

1. Pilih format dan gaya musik, lalu klik **Buat Video Otomatis**.
2. Klik **Rekam & Unduh**.
3. Pada jendela berbagi, pilih tab ini dan centang **Bagikan audio tab**.
   Suara narasi dan musik ikut terekam.
4. Jangan pindah tab selama rekaman berlangsung.

Rekaman hanya bisa dibuat di Chrome atau Edge.

## Mengunggah ke Facebook dan YouTube

Facebook paling andal dengan MP4 (video H.264, audio AAC). Jika browser merekam WebM,
suara bisa hilang setelah diunggah. Aplikasi akan memberi tahu jika formatnya WebM.

Konversi dengan FFmpeg (satu perintah):

    ffmpeg -i video-berita.webm -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart video-berita.mp4

Tanpa FFmpeg, buka file WebM di HandBrake lalu pilih preset **Fast 1080p30**, dan pastikan
audio di-encode sebagai AAC.

Setelah konversi, putar MP4 di pemutar video untuk memastikan suara narasi terdengar sebelum
diunggah.

## Catatan hak cipta

- Musik latar dibuat oleh kode di halaman ini, tidak memakai file audio pihak lain.
- Gambar dari Wikimedia Commons punya lisensi masing-masing. Cek syaratnya, terutama atribusi.
- Teks berita tetap milik sumbernya. Tulis ulang dengan kata-katamu sendiri dan cantumkan sumber.

## Struktur

- `index.html`: aplikasi lengkap (satu file, tanpa instalasi)
- `server.py`: server lokal opsional untuk mengambil isi link tanpa batasan CORS
- `.nojekyll`: memberi tahu GitHub Pages agar file dibaca apa adanya
