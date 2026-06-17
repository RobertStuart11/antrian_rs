from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Q

from .models import Antrian, Poliklinik, Pasien
from .forms import AmbilAntrianForm, UpdateStatusForm, PoliklinikForm


# ───────────────────────────── AUTH ─────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Selamat datang, {user.get_full_name() or user.username}!')
        return redirect('dashboard')
    return render(request, 'antrian/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Anda telah keluar dari sistem.')
    return redirect('login')


# ───────────────────────────── DASHBOARD ─────────────────────────────

@login_required
def dashboard(request):
    hari_ini = timezone.localdate()
    antrian_hari_ini = Antrian.objects.filter(tanggal=hari_ini)

    context = {
        'total_pasien': antrian_hari_ini.count(),
        'menunggu': antrian_hari_ini.filter(status='menunggu').count(),
        'dilayani': antrian_hari_ini.filter(status='dilayani').count(),
        'selesai': antrian_hari_ini.filter(status='selesai').count(),
        'antrian_terbaru': antrian_hari_ini.order_by('-waktu_daftar')[:10],
        'antrian_aktif': antrian_hari_ini.filter(
            status__in=['menunggu', 'dipanggil', 'dilayani']
        ).order_by('poliklinik', 'nomor_urut')[:8],
        'poliklinik_list': Poliklinik.objects.filter(aktif=True),
        'tanggal': hari_ini,
    }
    return render(request, 'antrian/dashboard.html', context)


# ───────────────────────────── AMBIL ANTRIAN ─────────────────────────────

def ambil_antrian(request):
    """Halaman publik untuk mengambil nomor antrian."""
    form = AmbilAntrianForm(request.POST or None)
    tiket = None

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        poli = data['poliklinik']
        nomor = poli.nomor_antrian_berikutnya()

        antrian = Antrian.objects.create(
            poliklinik=poli,
            nama_pasien=data['nama_pasien'],
            nik=data.get('nik', ''),
            jenis_pasien=data['jenis_pasien'],
            keluhan=data.get('keluhan', ''),
            nomor_urut=nomor,
        )
        tiket = antrian
        messages.success(request, f'Nomor antrian Anda: {antrian.kode_antrian}')

    return render(request, 'antrian/ambil_antrian.html', {'form': form, 'tiket': tiket})


# ───────────────────────────── DAFTAR ANTRIAN ─────────────────────────────

@login_required
def daftar_antrian(request):
    hari_ini = timezone.localdate()
    tanggal = request.GET.get('tanggal', str(hari_ini))
    poli_id = request.GET.get('poli', '')
    status_filter = request.GET.get('status', '')

    antrian_qs = Antrian.objects.filter(tanggal=tanggal).select_related('poliklinik')

    if poli_id:
        antrian_qs = antrian_qs.filter(poliklinik_id=poli_id)
    if status_filter:
        antrian_qs = antrian_qs.filter(status=status_filter)

    context = {
        'antrian_list': antrian_qs.order_by('poliklinik__kode', 'nomor_urut'),
        'poliklinik_list': Poliklinik.objects.filter(aktif=True),
        'tanggal': tanggal,
        'poli_id': poli_id,
        'status_filter': status_filter,
        'status_choices': Antrian.STATUS_CHOICES,
    }
    return render(request, 'antrian/daftar_antrian.html', context)


# ───────────────────────────── DETAIL & UPDATE ANTRIAN ─────────────────────────────

@login_required
def detail_antrian(request, pk):
    antrian = get_object_or_404(Antrian, pk=pk)
    form = UpdateStatusForm(request.POST or None, instance=antrian)

    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        if obj.status == 'dipanggil' and not obj.waktu_panggil:
            obj.waktu_panggil = timezone.now()
        if obj.status == 'selesai' and not obj.waktu_selesai:
            obj.waktu_selesai = timezone.now()
        obj.save()
        messages.success(request, 'Status antrian berhasil diperbarui.')
        return redirect('daftar_antrian')

    return render(request, 'antrian/detail_antrian.html', {'antrian': antrian, 'form': form})


@login_required
def panggil_antrian(request, pk):
    """Panggil pasien berikutnya via AJAX atau form POST."""
    antrian = get_object_or_404(Antrian, pk=pk)
    antrian.status = 'dipanggil'
    antrian.waktu_panggil = timezone.now()
    antrian.save()
    messages.success(request, f'{antrian.kode_antrian} – {antrian.nama_pasien} dipanggil.')
    return redirect(request.META.get('HTTP_REFERER', 'daftar_antrian'))


@login_required
def selesai_antrian(request, pk):
    antrian = get_object_or_404(Antrian, pk=pk)
    antrian.status = 'selesai'
    antrian.waktu_selesai = timezone.now()
    antrian.save()
    messages.success(request, f'Antrian {antrian.kode_antrian} selesai.')
    return redirect(request.META.get('HTTP_REFERER', 'daftar_antrian'))


# ───────────────────────────── DISPLAY BOARD ─────────────────────────────

def display_board(request):
    """Halaman display antrian publik (tampil di TV/monitor ruang tunggu)."""
    hari_ini = timezone.localdate()
    poli_list = Poliklinik.objects.filter(aktif=True)
    board_data = []

    for poli in poli_list:
        sedang = poli.antrian_set.filter(
            tanggal=hari_ini,
            status__in=['dipanggil', 'dilayani']
        ).order_by('nomor_urut').first()

        berikutnya = poli.antrian_set.filter(
            tanggal=hari_ini,
            status='menunggu'
        ).order_by('nomor_urut').first()

        board_data.append({
            'poli': poli,
            'sedang': sedang,
            'berikutnya': berikutnya,
        })

    return render(request, 'antrian/display_board.html', {
        'board_data': board_data,
        'tanggal': hari_ini,
    })


# ───────────────────────────── POLIKLINIK CRUD ─────────────────────────────

@login_required
def kelola_poliklinik(request):
    poli_list = Poliklinik.objects.all()
    return render(request, 'antrian/kelola_poliklinik.html', {'poli_list': poli_list})


@login_required
def tambah_poliklinik(request):
    form = PoliklinikForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Poliklinik berhasil ditambahkan.')
        return redirect('kelola_poliklinik')
    return render(request, 'antrian/form_poliklinik.html', {'form': form, 'judul': 'Tambah Poliklinik'})


@login_required
def edit_poliklinik(request, pk):
    poli = get_object_or_404(Poliklinik, pk=pk)
    form = PoliklinikForm(request.POST or None, instance=poli)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Poliklinik berhasil diperbarui.')
        return redirect('kelola_poliklinik')
    return render(request, 'antrian/form_poliklinik.html', {'form': form, 'judul': 'Edit Poliklinik'})


@login_required
def hapus_poliklinik(request, pk):
    poli = get_object_or_404(Poliklinik, pk=pk)
    if request.method == 'POST':
        poli.delete()
        messages.success(request, 'Poliklinik berhasil dihapus.')
        return redirect('kelola_poliklinik')
    return render(request, 'antrian/hapus_konfirmasi.html', {'obj': poli, 'nama': poli.nama})


# ───────────────────────────── LAPORAN ─────────────────────────────

@login_required
def laporan(request):
    hari_ini = timezone.localdate()
    tanggal = request.GET.get('tanggal', str(hari_ini))

    antrian_qs = Antrian.objects.filter(tanggal=tanggal)
    per_poli = antrian_qs.values(
        'poliklinik__kode', 'poliklinik__nama'
    ).annotate(
        total=Count('id'),
        selesai=Count('id', filter=Q(status='selesai')),
        menunggu=Count('id', filter=Q(status='menunggu')),
        batal=Count('id', filter=Q(status='batal')),
    ).order_by('poliklinik__kode')

    context = {
        'tanggal': tanggal,
        'total_pasien': antrian_qs.count(),
        'total_selesai': antrian_qs.filter(status='selesai').count(),
        'total_menunggu': antrian_qs.filter(status='menunggu').count(),
        'total_batal': antrian_qs.filter(status='batal').count(),
        'per_poli': per_poli,
    }
    return render(request, 'antrian/laporan.html', context)


# ───────────────────────────── API JSON ─────────────────────────────

def api_status_antrian(request):
    """API endpoint untuk auto-refresh display board."""
    hari_ini = timezone.localdate()
    poli_list = Poliklinik.objects.filter(aktif=True)
    data = []
    for poli in poli_list:
        sedang = poli.antrian_set.filter(
            tanggal=hari_ini,
            status__in=['dipanggil', 'dilayani']
        ).order_by('nomor_urut').values('kode_antrian', 'nama_pasien').first()

        berikut = poli.antrian_set.filter(
            tanggal=hari_ini, status='menunggu'
        ).order_by('nomor_urut').values('kode_antrian', 'nama_pasien').first()

        data.append({
            'poli': poli.nama,
            'ruangan': poli.ruangan,
            'dokter': poli.dokter,
            'sedang': sedang,
            'berikutnya': berikut,
        })
    return JsonResponse({'data': data, 'waktu': timezone.now().strftime('%H:%M:%S')})
