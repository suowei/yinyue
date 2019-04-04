from django.urls import path

from . import views

app_name = 'szzj'
urlpatterns = [
    path('', views.index, name='index'),
    path('szzj/', views.AlbumIndexView.as_view(), name='szzj.index'),
    path('szzj/<int:year>/', views.album_year_index, name='szzj.album_year_index'),
    path('szzj/artist/', views.artist_index, name='szzj.artist_index'),
    path('szzj/artist/<int:pk>/', views.ArtistDetailView.as_view(), name='szzj.artist_detail'),
    path('szzj/new/', views.new_album_index, name='szzj.new_album_index'),
    path('yanchanghui/', views.ConcertIndexView.as_view(), name='yanchanghui.index'),
    path('yanchanghui/<int:year>/', views.concert_year_index, name='yanchanghui.concert_year_index'),
    path('yanchanghui/site/', views.SiteIndexView.as_view(), name='yanchanghui.site_index'),
]
