from django.contrib import admin

from .models import Artist
from .models import Company
from .models import Album
from .models import AlbumData
from .models import AlbumDataDaily
from .models import AlbumInfo
from .models import Tour
from .models import City
from .models import Site
from .models import Concert


class ArtistAdmin(admin.ModelAdmin):
    search_fields = ['name']


class CompanyAdmin(admin.ModelAdmin):
    search_fields = ['name']


class AlbumDataInline(admin.TabularInline):
    model = AlbumData
    fields = ('time',)
    extra = 1


class AlbumAdmin(admin.ModelAdmin):
    search_fields = ['title']
    autocomplete_fields = ['artist', 'company']
    inlines = [
        AlbumDataInline,
    ]

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if isinstance(inline, AlbumDataInline) and obj is None:
                yield inline.get_formset(request, obj), inline


class AlbumInfoAdmin(admin.ModelAdmin):
    autocomplete_fields = ['artist']


class AlbumDataAdmin(admin.ModelAdmin):
    autocomplete_fields = ['album']


class TourAdmin(admin.ModelAdmin):
    search_fields = ['title']
    autocomplete_fields = ['artist']


class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']


class SiteAdmin(admin.ModelAdmin):
    search_fields = ['name']
    autocomplete_fields = ['city']


class ConcertAdmin(admin.ModelAdmin):
    save_as = True
    autocomplete_fields = ['tour', 'site']


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(AlbumData, AlbumDataAdmin)
admin.site.register(AlbumDataDaily)
admin.site.register(AlbumInfo, AlbumInfoAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Concert, ConcertAdmin)
