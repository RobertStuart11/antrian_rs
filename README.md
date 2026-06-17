# 🏥 Sistem Antrian Poliklinik Rumah Sakit
**Framework:** Django (Python) | **Database:** SQLite | **UI:** Bootstrap 5

---

## 📋 Fitur Aplikasi

| Fitur | Keterangan |
|-------|-----------|
| 🎫 Ambil Nomor Antrian | Pasien bisa daftar tanpa login |
| 📋 Daftar Antrian | Lihat & kelola semua antrian harian |
| 📺 Display Board | Layar antrian real-time (cocok di TV) |
| 🏥 Kelola Poliklinik | CRUD poli beserta dokter & ruangan |
| 📊 Laporan | Rekap antrian per poli per hari |
| 🔐 Login Petugas | Sistem autentikasi bawaan Django |
| 🔄 Auto-refresh | Display board update otomatis 15 detik |

---

## ⚡ Cara Instalasi & Menjalankan

### 1. Persiapan (jika belum ada)
```bash
pip install django
```

### 2. Masuk ke folder proyek
```bash
cd antrian_rs
```

### 3. Migrasi database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Isi data awal (demo)
```bash
python seeder.py
```

### 5. Jalankan server
```bash
python manage.py runserver
```

### 6. Buka di browser
```
http://127.0.0.1:8000/
```

---

## 🔑 Akun Login

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Petugas | `petugas` | `petugas123` |

**Admin Django:** http://127.0.0.1:8000/admin/

---

## 🗂️ Struktur Proyek

```
antrian_rs/
├── manage.py
├── seeder.py                  ← Data demo
├── antrian_rs/
│   ├── settings.py            ← Konfigurasi Django
│   └── urls.py                ← URL utama
└── antrian/
    ├── models.py              ← Model Poliklinik, Pasien, Antrian
    ├── views.py               ← Semua logika halaman
    ├── forms.py               ← Form pendaftaran & update
    ├── urls.py                ← URL routing app
    ├── admin.py               ← Tampilan Django Admin
    └── templates/antrian/
        ├── base.html          ← Template induk (navbar, footer)
        ├── login.html         ← Halaman login
        ├── dashboard.html     ← Dashboard utama
        ├── ambil_antrian.html ← Form + tiket antrian
        ├── daftar_antrian.html← Tabel antrian + filter
        ├── detail_antrian.html← Detail & update status
        ├── display_board.html ← Layar antrian (TV/monitor)
        ├── laporan.html       ← Laporan harian
        ├── kelola_poliklinik.html
        ├── form_poliklinik.html
        └── hapus_konfirmasi.html
```

---

## 🗄️ Diagram Database

```
Poliklinik          Antrian              Pasien
──────────          ──────────           ──────────
kode (PK)  ◄──┐    id (PK)              id (PK)
nama            └── poliklinik (FK) ──► nama
ruangan         ┌── pasien (FK)         nik
dokter          │   nama_pasien         jenis_pasien
aktif           │   nik                 no_hp
                │   jenis_pasien
                │   keluhan
                │   nomor_urut
                │   kode_antrian
                │   tanggal
                │   status
                │   waktu_daftar
                │   waktu_panggil
                └── waktu_selesai
```

---

## 🌐 URL & Halaman

| URL | Halaman | Login? |
|-----|---------|--------|
| `/` | Dashboard | ✅ |
| `/login/` | Halaman Login | ❌ |
| `/ambil-antrian/` | Ambil Nomor (Pasien) | ❌ |
| `/display/` | Display Board | ❌ |
| `/daftar-antrian/` | Daftar Antrian | ✅ |
| `/antrian/<id>/` | Detail Antrian | ✅ |
| `/poliklinik/` | Kelola Poliklinik | ✅ |
| `/laporan/` | Laporan Harian | ✅ |
| `/api/status/` | API JSON Antrian | ❌ |
| `/admin/` | Admin Django | ✅ (superuser) |

---

## 🎓 Poin Presentasi

1. **Arsitektur MVT** – Django menggunakan pola Model-View-Template
2. **Model relasi** – ForeignKey antara Antrian dan Poliklinik
3. **CRUD lengkap** – Create, Read, Update, Delete di Poliklinik
4. **Authentication** – Sistem login bawaan Django dengan dekorator `@login_required`
5. **API JSON** – Endpoint `/api/status/` mengembalikan data real-time
6. **Display Board** – Auto-refresh setiap 15 detik untuk monitor ruang tunggu
7. **Halaman Publik** – Pasien bisa ambil nomor tanpa login

---

*Dibuat untuk tugas Pemrograman Web – Sistem Antrian Poliklinik RS*
