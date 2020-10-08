from django.urls import path

from . import views

app_name = 'szzj'
urlpatterns = [
    path('', views.index, name='index'),
    path('szzj/', views.album_index, name='szzj.index'),
    path('szzj/<int:year>/', views.album_year_index, name='szzj.album_year_index'),
    path('szzj/sales/', views.album_sales_index, name='szzj.album_sales_index'),
    path('szzj/<int:year>/sales/', views.album_sales_year_index, name='szzj.album_sales_year_index'),
    path('szzj/artist/', views.artist_index, name='szzj.artist_index'),
    path('szzj/artist/<int:pk>/', views.ArtistDetailView.as_view(), name='szzj.artist_detail'),
    path('szzj/new/', views.new_album_index, name='szzj.new_album_index'),
    path('szzj/today', views.today_album_index, name='szzj.today_album_index'),
    path('szzj/album/<int:pk>/', views.album_detail, name='szzj.album_detail'),
    path('szzj/album/<int:album>/daily', views.album_data_daily, name='szzj.album_data_daily'),
    path('szzj/album/<int:album>/<int:year>/<int:month>/<int:day>/', views.album_data_daily_detail, name='szzj.album_data_daily_detail'),
    path('szzj/album/download/', views.album_download, name='szzj.album_download'),
    path('yanchanghui/', views.ConcertIndexView.as_view(), name='yanchanghui.index'),
    path('yanchanghui/<int:year>/', views.concert_year_index, name='yanchanghui.concert_year_index'),
    path('yanchanghui/site/', views.SiteIndexView.as_view(), name='yanchanghui.site_index'),
    path('yanchanghui/site/<int:pk>/', views.SiteDetailView.as_view(), name='yanchanghui.site_detail'),
    path('search/', views.search),
]
