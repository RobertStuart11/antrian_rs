from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Halaman Utama
    path('', views.dashboard, name='dashboard'),
    path('ambil-antrian/', views.ambil_antrian, name='ambil_antrian'),
    path('daftar-antrian/', views.daftar_antrian, name='daftar_antrian'),
    path('display/', views.display_board, name='display_board'),
    path('laporan/', views.laporan, name='laporan'),

    # Detail & Aksi Antrian
    path('antrian/<int:pk>/', views.detail_antrian, name='detail_antrian'),
    path('antrian/<int:pk>/panggil/', views.panggil_antrian, name='panggil_antrian'),
    path('antrian/<int:pk>/selesai/', views.selesai_antrian, name='selesai_antrian'),

    # Kelola Poliklinik
    path('poliklinik/', views.kelola_poliklinik, name='kelola_poliklinik'),
    path('poliklinik/tambah/', views.tambah_poliklinik, name='tambah_poliklinik'),
    path('poliklinik/<int:pk>/edit/', views.edit_poliklinik, name='edit_poliklinik'),
    path('poliklinik/<int:pk>/hapus/', views.hapus_poliklinik, name='hapus_poliklinik'),

    # API
    path('api/status/', views.api_status_antrian, name='api_status'),
]
