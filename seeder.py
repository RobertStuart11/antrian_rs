"""
Script untuk mengisi data awal (demo) aplikasi Antrian Poliklinik.
Jalankan: python seeder.py
(Pastikan sudah ada di folder antrian_rs dan sudah migrasi)
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antrian_rs.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from antrian.models import Poliklinik, Antrian
from django.utils import timezone
import random

print("=== SEEDER ANTRIAN POLIKLINIK ===")

# 1. Superuser admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@rs.com', 'admin123')
    print("✓ Superuser: admin / admin123")

# 2. User petugas
if not User.objects.filter(username='petugas').exists():
    petugas = User.objects.create_user('petugas', 'petugas@rs.com', 'petugas123')
    petugas.first_name = 'Budi'
    petugas.last_name = 'Santoso'
    petugas.save()
    print("✓ User petugas: petugas / petugas123")

# 3. Poliklinik
poli_data = [
    ('A', 'Poli Umum',      'Ruang 1', 'dr. Andi Prasetyo, Sp.PD'),
    ('B', 'Poli Anak',      'Ruang 3', 'dr. Rina Wahyuni, Sp.A'),
    ('C', 'Poli Gigi',      'Ruang 5', 'drg. Sari Dewi'),
    ('D', 'Poli Kandungan', 'Ruang 7', 'dr. Maya Kusuma, Sp.OG'),
    ('E', 'Poli Jantung',   'Ruang 9', 'dr. Hendra Gunawan, Sp.JP'),
]
poli_objs = {}
for kode, nama, ruangan, dokter in poli_data:
    poli, created = Poliklinik.objects.get_or_create(
        kode=kode,
        defaults={'nama': nama, 'ruangan': ruangan, 'dokter': dokter}
    )
    poli_objs[kode] = poli
    if created:
        print(f"✓ Poliklinik: {nama}")

# 4. Data antrian hari ini (demo)
hari_ini = timezone.localdate()
nama_pasien = [
    "Ahmad Fauzi", "Siti Rahayu", "Budi Santoso", "Dewi Lestari",
    "Hendra Gunawan", "Rina Wati", "Agus Salim", "Nur Hidayah",
    "Wahyu Pratama", "Fitri Handayani", "Dani Saputra", "Lia Anggraini",
    "Rizky Maulana", "Ayu Kartika", "Fajar Nugroho",
]
status_pool = ['selesai', 'selesai', 'selesai', 'dilayani', 'menunggu', 'menunggu', 'menunggu']

antrian_count = 0
for kode, poli in poli_objs.items():
    if Antrian.objects.filter(tanggal=hari_ini, poliklinik=poli).exists():
        continue
    jumlah = random.randint(5, 10)
    for i in range(1, jumlah + 1):
        nama = random.choice(nama_pasien)
        status = random.choice(status_pool)
        a = Antrian(
            poliklinik=poli,
            nama_pasien=nama,
            jenis_pasien=random.choice(['umum', 'bpjs']),
            nomor_urut=i,
            tanggal=hari_ini,
            status=status,
        )
        if status in ('dilayani', 'selesai'):
            a.waktu_panggil = timezone.now()
        if status == 'selesai':
            a.waktu_selesai = timezone.now()
        a.save()
        antrian_count += 1

print(f"✓ Data antrian hari ini: {antrian_count} antrian dibuat")
print("\n=== SELESAI ===")
print("Jalankan: python manage.py runserver")
print("Akses   : http://127.0.0.1:8000/")
print("Admin   : http://127.0.0.1:8000/admin/")
print("Login   : admin / admin123  atau  petugas / petugas123")
print("Pasien  : http://127.0.0.1:8000/ambil-antrian/  (tanpa login)")
