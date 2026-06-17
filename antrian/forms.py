from django import forms
from .models import Antrian, Poliklinik, Pasien


class AmbilAntrianForm(forms.Form):
    nama_pasien = forms.CharField(
        max_length=150,
        label='Nama Pasien',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan nama lengkap'
        })
    )
    nik = forms.CharField(
        max_length=16,
        required=False,
        label='NIK / No. KTP',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '16 digit NIK (opsional)'
        })
    )
    jenis_kelamin = forms.ChoiceField(
        choices=[('L', 'Laki-laki'), ('P', 'Perempuan')],
        label='Jenis Kelamin',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    jenis_pasien = forms.ChoiceField(
        choices=Pasien.JENIS_CHOICES,
        label='Jenis Pasien',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    poliklinik = forms.ModelChoiceField(
        queryset=Poliklinik.objects.filter(aktif=True),
        label='Poliklinik Tujuan',
        empty_label='-- Pilih Poliklinik --',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    keluhan = forms.CharField(
        required=False,
        label='Keluhan Utama',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ceritakan keluhan Anda secara singkat...'
        })
    )


class UpdateStatusForm(forms.ModelForm):
    class Meta:
        model = Antrian
        fields = ['status', 'catatan_dokter']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'catatan_dokter': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'status': 'Status Antrian',
            'catatan_dokter': 'Catatan Dokter',
        }


class PoliklinikForm(forms.ModelForm):
    class Meta:
        model = Poliklinik
        fields = ['kode', 'nama', 'ruangan', 'dokter', 'aktif']
        widgets = {
            'kode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: A'}),
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Poli Umum'}),
            'ruangan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Ruang 1'}),
            'dokter': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama dokter'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
