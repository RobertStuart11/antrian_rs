from django.contrib import admin
from .models import Antrian, Poliklinik, Pasien


@admin.register(Poliklinik)
class PoliklinikAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama', 'ruangan', 'dokter', 'aktif']
    list_editable = ['aktif']
    search_fields = ['kode', 'nama', 'dokter']


@admin.register(Pasien)
class PasienAdmin(admin.ModelAdmin):
    list_display = ['nama', 'nik', 'jenis_kelamin', 'jenis_pasien', 'no_hp']
    search_fields = ['nama', 'nik']
    list_filter = ['jenis_pasien', 'jenis_kelamin']


@admin.register(Antrian)
class AntrianAdmin(admin.ModelAdmin):
    list_display = ['kode_antrian', 'nama_pasien', 'poliklinik', 'tanggal', 'status', 'waktu_daftar']
    list_filter = ['status', 'poliklinik', 'tanggal', 'jenis_pasien']
    search_fields = ['kode_antrian', 'nama_pasien', 'nik']
    date_hierarchy = 'tanggal'
    readonly_fields = ['waktu_daftar', 'waktu_panggil', 'waktu_selesai']
    ordering = ['-tanggal', 'poliklinik', 'nomor_urut']
