from django.urls import path

from . import views

app_name = 'szzj'
urlpatterns = [
    path('', views.AlbumIndexView.as_view(), name='index'),
    path('<int:year>/', views.year_index, name='year_index'),
    path('artist/', views.artist_index, name='artist_index'),
    path('artist/<int:pk>/', views.ArtistDetailView.as_view(), name='artist_detail'),
]
