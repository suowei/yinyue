from django.contrib import admin

from .models import City, Theatre, Stage, Produce, Musical, MusicalProduces, MusicalStaff, MusicalCast, Tour, Schedule, Role, Artist, Show, Chupiao


class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']


class TheatreAdmin(admin.ModelAdmin):
    search_fields = ['name']
    autocomplete_fields = ['city']


class StageAdmin(admin.ModelAdmin):
    search_fields = ['theatre__name']
    autocomplete_fields = ['theatre']


class ProduceAdmin(admin.ModelAdmin):
    search_fields = ['name']


class ArtistAdmin(admin.ModelAdmin):
    search_fields = ['name']


class MusicalStaffAdmin(admin.ModelAdmin):
    search_fields = ['musical__name', 'artist__name']
    autocomplete_fields = ['musical', 'artist']


class MusicalCastAdmin(admin.ModelAdmin):
    save_as = True
    search_fields = ['role__musical__name', 'role__name', 'artist__name']
    autocomplete_fields = ['role', 'artist']


class MusicalProducesInline(admin.TabularInline):
    model = MusicalProduces
    autocomplete_fields = ['produce']


class MusicalStaffInline(admin.TabularInline):
    model = MusicalStaff
    autocomplete_fields = ['artist']


class RoleInline(admin.TabularInline):
    model = Role


class MusicalAdmin(admin.ModelAdmin):
    save_as = True
    search_fields = ['name']
    inlines = [
        MusicalStaffInline,
        MusicalProducesInline,
        RoleInline,
    ]


class ScheduleInline(admin.TabularInline):
    model = Schedule
    autocomplete_fields = ['stage']


class TourAdmin(admin.ModelAdmin):
    save_as = True
    search_fields = ['musical__name']
    autocomplete_fields = ['musical']
    inlines = [
        ScheduleInline,
    ]


class ShowInline(admin.TabularInline):
    model = Show
    autocomplete_fields = ['cast']


class ScheduleAdmin(admin.ModelAdmin):
    save_as = True
    ordering = ['-id']
    search_fields = ['tour__musical__name']
    autocomplete_fields = ['tour', 'stage']
    inlines = [
        ShowInline,
    ]

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if not isinstance(inline, ShowInline) or obj is not None:
                yield inline.get_formset(request, obj), inline


class MusicalCastInline(admin.TabularInline):
    model = MusicalCast
    autocomplete_fields = ['artist']


class RoleAdmin(admin.ModelAdmin):
    save_as = True
    list_select_related = ('musical',)
    search_fields = ['musical__name']
    autocomplete_fields = ['musical']
    inlines = [
        MusicalCastInline,
    ]


class ShowCastInline(admin.TabularInline):
    model = Show.cast.through
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        args = request.resolver_match.kwargs
        if "object_id" in args:
            show_id = args["object_id"]
            show = Show.objects.get(pk=show_id)
            if db_field.name == "musicalcast":
                kwargs["queryset"] = MusicalCast.objects.filter(role__musical=show.schedule.tour.musical_id)\
                    .select_related('role', 'artist').order_by('role__seq', 'seq')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_min_num(self, request, obj=None, **kwargs):
        if obj:
            min_num = Role.objects.filter(musical=obj.schedule.tour.musical_id).count()
        else:
            min_num = 0
        return min_num


class ShowAdmin(admin.ModelAdmin):
    save_as = True
    search_fields = ['schedule__tour__musical__name', 'cast__artist__name']
    autocomplete_fields = ['schedule']
    exclude = ('cast',)
    inlines = [
        ShowCastInline,
    ]


class ChupiaoAdmin(admin.ModelAdmin):
    model = Chupiao
    autocomplete_fields = ['show', 'user']


admin.site.register(City, CityAdmin)
admin.site.register(Theatre, TheatreAdmin)
admin.site.register(Stage, StageAdmin)
admin.site.register(Produce, ProduceAdmin)
admin.site.register(Musical, MusicalAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Show, ShowAdmin)
admin.site.register(MusicalStaff, MusicalStaffAdmin)
admin.site.register(MusicalCast, MusicalCastAdmin)
admin.site.register(Chupiao, ChupiaoAdmin)
