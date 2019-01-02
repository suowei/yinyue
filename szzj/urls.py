from django.urls import path

from . import views

app_name = 'szzj'
urlpatterns = [
    path('', views.index, name='index'),
    path('artist/<int:pk>/', views.ArtistDetailView.as_view(), name='artist_detail'),
]
