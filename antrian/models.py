from django.db import models
from django.utils import timezone


class Poliklinik(models.Model):
    KODE_CHOICES = [
        ('A', 'Poli Umum'),
        ('B', 'Poli Anak'),
        ('C', 'Poli Gigi'),
        ('D', 'Poli Kandungan'),
        ('E', 'Poli Jantung'),
        ('F', 'Poli Mata'),
    ]
    kode = models.CharField(max_length=2, unique=True)
    nama = models.CharField(max_length=100)
    ruangan = models.CharField(max_length=20, default='Ruang 1')
    dokter = models.CharField(max_length=100, blank=True)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Poliklinik'
        verbose_name_plural = 'Poliklinik'
        ordering = ['kode']

    def __str__(self):
        return f"{self.kode} - {self.nama}"

    def antrian_hari_ini(self):
        hari_ini = timezone.localdate()
        return self.antrian_set.filter(tanggal=hari_ini)

    def nomor_antrian_berikutnya(self):
        hari_ini = timezone.localdate()
        terakhir = self.antrian_set.filter(tanggal=hari_ini).order_by('-nomor_urut').first()
        return (terakhir.nomor_urut + 1) if terakhir else 1


class Pasien(models.Model):
    JENIS_CHOICES = [
        ('umum', 'Umum'),
        ('bpjs', 'BPJS'),
    ]
    nama = models.CharField(max_length=150)
    nik = models.CharField(max_length=16, blank=True)
    jenis_kelamin = models.CharField(max_length=1, choices=[('L', 'Laki-laki'), ('P', 'Perempuan')], default='L')
    tanggal_lahir = models.DateField(null=True, blank=True)
    no_hp = models.CharField(max_length=15, blank=True)
    alamat = models.TextField(blank=True)
    jenis_pasien = models.CharField(max_length=10, choices=JENIS_CHOICES, default='umum')

    class Meta:
        verbose_name = 'Pasien'
        verbose_name_plural = 'Pasien'
        ordering = ['nama']

    def __str__(self):
        return self.nama


class Antrian(models.Model):
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu'),
        ('dipanggil', 'Dipanggil'),
        ('dilayani', 'Sedang Dilayani'),
        ('selesai', 'Selesai'),
        ('batal', 'Batal / Tidak Hadir'),
    ]

    poliklinik = models.ForeignKey(Poliklinik, on_delete=models.CASCADE)
    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE, null=True, blank=True)
    nama_pasien = models.CharField(max_length=150)
    nik = models.CharField(max_length=16, blank=True)
    jenis_pasien = models.CharField(max_length=10, choices=Pasien.JENIS_CHOICES, default='umum')
    keluhan = models.TextField(blank=True)
    nomor_urut = models.PositiveIntegerField()
    kode_antrian = models.CharField(max_length=10)
    tanggal = models.DateField(default=timezone.localdate)
    waktu_daftar = models.DateTimeField(auto_now_add=True)
    waktu_panggil = models.DateTimeField(null=True, blank=True)
    waktu_selesai = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='menunggu')
    catatan_dokter = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Antrian'
        verbose_name_plural = 'Antrian'
        ordering = ['tanggal', 'poliklinik', 'nomor_urut']
        unique_together = ['poliklinik', 'tanggal', 'nomor_urut']

    def __str__(self):
        return f"{self.kode_antrian} - {self.nama_pasien}"

    def save(self, *args, **kwargs):
        if not self.kode_antrian:
            self.kode_antrian = f"{self.poliklinik.kode}{self.nomor_urut:03d}"
        super().save(*args, **kwargs)

    def posisi_antrian(self):
        """Berapa orang di depan pasien ini yang masih menunggu."""
        return Antrian.objects.filter(
            poliklinik=self.poliklinik,
            tanggal=self.tanggal,
            status='menunggu',
            nomor_urut__lt=self.nomor_urut
        ).count()

    def estimasi_menit(self):
        """Estimasi waktu tunggu dalam menit (asumsi 10 menit/pasien)."""
        return self.posisi_antrian() * 10
