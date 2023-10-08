from django.urls import path, include, reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordChangeView

from . import views

app_name = 'yyj'
urlpatterns = [
    path('', views.index, name='yyj.index'),
    path('musical/', views.musical_index, name='yyj.musical_index'),
    path('artist/<int:pk>/', views.artist_detail, name='yyj.artist_detail'),
    path('artist/<int:pk>/show', views.artist_show_index, name='yyj.artist_show_index'),
    path('artist/<int:pk>/download', views.artist_show_download, name='yyj.artist_show_download'),
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
    path('year/<int:year>/city', views.show_year_index_city, name='yyj.show_year_index_city'),
    path('year/<int:year>/artist', views.show_year_index_artist, name='yyj.show_year_index_artist'),
    path('search/', views.search, name='yyj.search'),
    path('search_day/', views.show_day_index, name='yyj.show_day_index'),
    path('download/', views.download, name='yyj.download'),
    path('download/<str:file>', views.download_file, name='yyj.download_file'),
    path('data/', TemplateView.as_view(template_name="yyj/data.html"), name='yyj.data'),
    path('api/', TemplateView.as_view(template_name="yyj/api.html"), name='yyj.api'),
    path('api/search_day/', views.api_show_day_index, name='yyj.api_show_day_index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('password_change/', PasswordChangeView.as_view(success_url=reverse_lazy('yyj:password_change_done')), name='password_change'),
    path('accounts/register', views.register, name='register'),
    path('chupiao/', views.chupiao_index, name='yyj.chupiao_index'),
    path('chupiao/<int:pk>/', views.chupiao_detail, name='yyj.chupiao_detail'),
    path('chupiao/search', views.chupiao_search, name='yyj.chupiao_search'),
    path('chupiao/add/', views.chupiao_create, name='yyj.chupiao_add'),
    path('chupiao/<int:pk>/edit/', views.chupiao_edit, name='yyj.chupiao_edit'),
    path('chupiao/<int:pk>/delete/', views.chupiao_delete, name='yyj.chupiao_delete'),
]
