## Panduan Penggunaan Aplikasi Notis Berbasis Web

### Akun Pemilik
# username : isman
# password : isman1234

### Akun Karyawan
# username : dzull
# password : dzull123

### 1. Pendahuluan
Aplikasi Notis adalah aplikasi berbasis web yang dibangun menggunakan framework Flask dengan database MySQL. Aplikasi ini memungkinkan pengguna untuk melakukan manajemen produk, transaksi, dan pengguna. Panduan ini akan memberikan langkah-langkah untuk menginstalasi dan menjalankan aplikasi ini di localhost.

### 2. Prasyarat
Sebelum memulai instalasi, pastikan Anda telah menginstal:
- Python 3.7 atau lebih baru
- MySQL
- Pip (Python package installer)

### 3. Langkah-langkah Instalasi

#### 3.1. Clone Repository
Clone repository aplikasi dari sumber yang diberikan:
```bash
git clone <URL_REPOSITORY>
cd <NAMA_FOLDER_REPOSITORY>
```

#### 3.2. Membuat Virtual Environment
Buat dan aktifkan virtual environment untuk mengelola dependensi:
```bash
python -m venv venv
source venv/bin/activate  # Untuk pengguna macOS/Linux
venv\Scripts\activate  # Untuk pengguna Windows
```

#### 3.3. Instalasi Dependensi
Instalasi semua dependensi yang dibutuhkan menggunakan `pip`:
```bash
pip install -r requirements.txt
```

#### 3.4. Konfigurasi Database
Buat database MySQL untuk aplikasi ini dan konfigurasi file `config.py` sesuai dengan kredensial database Anda:
```python
class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/database_name'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    # Konfigurasi lainnya
```

#### 3.5. Inisialisasi Database
Inisialisasi database dengan menjalankan perintah berikut:
```bash
flask db init
flask db migrate
flask db upgrade
```

#### 3.6. Menjalankan Aplikasi
Jalankan aplikasi menggunakan perintah berikut:
```bash
flask run
```
Aplikasi akan berjalan di `http://127.0.0.1:5000`.

### 4. Panduan Instalasi wkhtmltopdf
Aplikasi ini menggunakan `wkhtmltopdf` untuk menghasilkan PDF. Berikut langkah-langkah untuk menginstal `wkhtmltopdf`:

#### 4.1. Instalasi di macOS/Linux
Unduh dan instal `wkhtmltopdf` menggunakan perintah berikut:
```bash
# Untuk macOS menggunakan Homebrew
brew install Caskroom/cask/wkhtmltopdf

# Untuk Linux (contoh pada Ubuntu)
sudo apt-get install wkhtmltopdf
```

#### 4.2. Instalasi di Windows
1. Unduh installer dari [tautan ini](https://wkhtmltopdf.org/downloads.html).
2. Jalankan installer dan ikuti instruksi instalasi.

#### 4.3. Konfigurasi Path wkhtmltopdf di app.py
Setelah instalasi, temukan path lengkap dari executable `wkhtmltopdf`. Ubah path pada baris ke-789 di `app.py` sesuai dengan path instalasi di perangkat Anda:
```python
# Misalnya, jika pathnya adalah '/usr/local/bin/wkhtmltopdf' di macOS/Linux
config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

# Misalnya, jika pathnya adalah 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe' di Windows
config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
```

### 5. Struktur Proyek
Berikut adalah struktur direktori dari proyek:
```
.
├── app.py
├── config.py
├── models.py
├── requirements.txt
├── templates
│   ├── layout.html
│   ├── index.html
│   └── ...
├── static
│   ├── css
│   ├── js
│   └── ...
└── ...
```

### 6. Penggunaan
- **Menambahkan Pengguna:** Navigasi ke `/register` untuk menambahkan pengguna baru.
- **Manajemen Produk:** Navigasi ke `/products` untuk melihat, menambah, mengedit, dan menghapus produk.
- **Transaksi:** Navigasi ke `/transactions` untuk melihat dan mengelola transaksi.

### 7. Troubleshooting
- **Masalah Koneksi Database:** Pastikan kredensial database di `config.py` benar dan server MySQL berjalan.
- **Dependensi Tidak Terpasang:** Pastikan virtual environment aktif dan jalankan `pip install -r requirements.txt` lagi.

### 8. Mengimpor Database menggunakan phpMyAdmin

Untuk mengimpor database `not_is.sql` menggunakan phpMyAdmin, ikuti langkah-langkah berikut:

#### 8.1. Akses phpMyAdmin
1. Buka browser web Anda.
2. Akses phpMyAdmin melalui URL `http://localhost/phpmyadmin`.

#### 8.2. Buat Database Baru
1. Setelah masuk ke phpMyAdmin, klik pada tab **"Databases"**.
2. Di bawah **"Create database"**, masukkan nama database sebagai `not_is`.
3. Klik tombol **"Create"**.

#### 8.3. Impor File SQL
1. Pilih database `not_is` yang baru saja dibuat dari daftar di sebelah kiri.
2. Klik pada tab **"Import"** di bagian atas.
3. Di bagian **"File to import"**, klik tombol **"Browse"** dan pilih file `not_is.sql` dari sistem Anda.
4. Pastikan format file adalah SQL.
5. Klik tombol **"Go"** untuk memulai proses impor.

#### 8.4. Konfirmasi Impor
1. Setelah impor selesai, Anda akan melihat pesan sukses.
2. Klik pada tab **"Structure"** untuk melihat daftar tabel yang diimpor ke dalam database `not_is`.

---

Dengan mengikuti langkah-langkah ini, Anda dapat mengimpor database `not_is.sql` ke MySQL menggunakan phpMyAdmin dengan mudah.

Dengan mengikuti panduan ini, Anda seharusnya bisa menginstal dan menjalankan aplikasi Notis di localhost dengan lancar. Selamat menggunakan aplikasi!
