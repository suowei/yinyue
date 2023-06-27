from django.urls import path

from . import views

app_name = 'yyj'
urlpatterns = [
    path('', views.index, name='yyj.index'),
    path('musical/', views.musical_index, name='yyj.musical_index'),
    path('artist/<int:pk>/', views.artist_detail, name='yyj.artist_detail'),
    path('artist/<int:pk>/show', views.artist_show_index, name='yyj.artist_show_index'),
    path('musical/<int:pk>/', views.musical_detail, name='yyj.musical_detail'),
    path('produce/<int:pk>/', views.produce_detail, name='yyj.produce_detail'),
    path('tour/<int:pk>/', views.tour_detail, name='yyj.tour_detail'),
    path('schedule/<int:pk>/', views.schedule_detail, name='yyj.schedule_detail'),
    path('schedule/<int:pk>/show', views.schedule_show_index, name='yyj.schedule_show_index'),
    path('city/<int:pk>/', views.city_detail, name='yyj.city_detail'),
    path('theatre/<int:pk>/', views.theatre_detail, name='yyj.theatre_detail'),
    path('theatre/<int:pk>/show', views.theatre_show_index, name='yyj.theatre_show_index'),
    path('stage/', views.stage_index, name='yyj.stage_index'),
    path('stage/<int:pk>/', views.stage_detail, name='yyj.stage_detail'),
    path('stage/<int:pk>/show', views.stage_show_index, name='yyj.stage_show_index'),
    path('year/<int:year>/', views.show_year_index, name='yyj.show_year_index'),
    path('search/', views.search, name='yyj.search'),
    path('search_day/', views.show_day_index, name='yyj.show_day_index'),
]
