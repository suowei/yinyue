from django.contrib import admin
from django.urls import path, include

from yyj.admin import admin_site

urlpatterns = [
    path('', include('szzj.urls')),
    path("admin/tools/", admin_site.urls),
    path('admin/', admin.site.urls),
    path('yyj/', include('yyj.urls')),
]
