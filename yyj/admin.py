from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
import datetime
import re

from .models import City, Theatre, Stage, Produce, Musical, MusicalProduces, MusicalStaff, MusicalCast, Tour, Schedule, Role, Artist, Show, Conflict, Chupiao, Location


class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']


class LocationAdmin(admin.ModelAdmin):
    search_fields = ['name']


class TheatreAdmin(admin.ModelAdmin):
    search_fields = ['name']
    autocomplete_fields = ['city', 'location']


class StageAdmin(admin.ModelAdmin):
    search_fields = ['theatre__name']
    autocomplete_fields = ['theatre']


class ProduceAdmin(admin.ModelAdmin):
    search_fields = ['name']


class ArtistAdmin(admin.ModelAdmin):
    search_fields = ['name']


class MusicalProducesAdmin(admin.ModelAdmin):
    search_fields = ['musical__name', 'produce__name']
    autocomplete_fields = ['musical', 'produce']


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
    ordering = ['-id']
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
    ordering = ['-id']
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
    search_fields = ['schedule__tour__musical__name', 'schedule__tour__name']
    autocomplete_fields = ['schedule']
    exclude = ('cast',)
    inlines = [
        ShowCastInline,
    ]


class ConflictAdmin(admin.ModelAdmin):
    autocomplete_fields = ['artist']


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
admin.site.register(MusicalProduces, MusicalProducesAdmin)
admin.site.register(MusicalStaff, MusicalStaffAdmin)
admin.site.register(MusicalCast, MusicalCastAdmin)
admin.site.register(Conflict, ConflictAdmin)
admin.site.register(Chupiao, ChupiaoAdmin)
admin.site.register(Location, LocationAdmin)


class CustomAdminSite(admin.AdminSite):
    site_header = "管理后台"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.admin_view(self.tools_view)),
            path("loadshow/", self.admin_view(self.loadshow_view)),
            path("replacecast/", self.admin_view(self.replace_cast_view)),
            path("cancelshow/", self.admin_view(self.cancel_show_view)),
        ]
        return custom_urls + urls

    def tools_view(self, request):
        context = dict(
            self.each_context(request),
            title="后台工具"
        )
        return TemplateResponse(request, "admin/tools.html", context)

    def loadshow_view(self, request):
        result = []
        if request.method == "POST":
            schedule_id = request.POST.get("schedule_id")
            showcast_text = request.POST.get("showcast")
            keependdate = bool(request.POST.get("keependdate"))
            schedule = Schedule.objects.get(pk=int(schedule_id))
            role_list = Role.objects.filter(musical=schedule.tour.musical).order_by('seq')
            musical_cast_list = MusicalCast.objects.filter(
                role__musical=schedule.tour.musical).select_related('role', 'artist')
            lines = showcast_text.strip().split("\n")
            # 读取角色列表
            header = lines[0].split('\t')
            role_id_list = []
            for s_role in header:
                for role in role_list:
                    if s_role.strip() == role.name:
                        role_id_list.append(role)
                        result.append("OK -> " + s_role)
                        break
            # 读取每一场演出的卡司排期并检查演员行程是否冲突
            today = datetime.date.today()
            for line in lines[1:]:
                try:
                    row = line.split('\t')
                    # 去除空格和空字段
                    row = [s.strip() for s in row]
                    row = [s for s in row if s]
                    # 读取日期和时间并添加演出信息
                    for i, s in enumerate(row):
                        numbers = [int(num) for num in re.findall(r'\d+', row[i])]
                        l_numbers = len(numbers)
                        # 如果有冒号代表读取结束
                        if ':' in row[i]:
                            if l_numbers == 2:
                                hour = numbers[0]
                                minute = numbers[1]
                            elif l_numbers == 4:
                                month = numbers[0]
                                if month < today.month:
                                    year = today.year + 1
                                else:
                                    year = today.year
                                day = numbers[1]
                                hour = numbers[2]
                                minute = numbers[3]
                            elif l_numbers == 5:
                                year = numbers[0]
                                month = numbers[1]
                                day = numbers[2]
                                hour = numbers[3]
                                minute = numbers[4]
                            break
                        # 如果没有冒号只读取日期
                        if l_numbers == 2:
                            month = numbers[0]
                            if month < today.month:
                                year = today.year + 1
                            else:
                                year = today.year
                            day = numbers[1]
                        elif l_numbers == 3:
                            year = numbers[0]
                            month = numbers[1]
                            day = numbers[2]
                    time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(hour) + ':' + str(minute)
                    show, created = Show.objects.get_or_create(schedule=schedule, time=time)
                    # 读取并添加卡司信息
                    index = i + 1
                    for i, s_artist in enumerate(row[index:]):
                        for musical_cast in musical_cast_list:
                            if musical_cast.role == role_id_list[i] and musical_cast.artist.name == s_artist:
                                show.cast.add(musical_cast)
                                show_count = Show.objects.filter(cast__artist=musical_cast.artist_id,
                                                                 time=show.time).distinct().count()
                                if show_count > 1:
                                    Conflict.objects.get_or_create(artist=musical_cast.artist, time=show.time)
                                break
                    result.append("OK -> " + line)
                except Exception as e:
                    result.append("ERROR " + line)
            if not keependdate and year and month and day:
                end_date = str(year) + '-' + str(month) + '-' + str(day)
                schedule.end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                schedule.save()
        context = dict(
            self.each_context(request),
            title="导入演出信息",
            result="\n".join(result)
        )

        return TemplateResponse(request, "admin/loadshow.html", context)

    def replace_cast_view(self, request):
        result = []
        if request.method == "POST":
            schedule_id = request.POST.get("schedule_id")
            replace_lines = request.POST.get("replace_lines", "").strip()
            # 获取Schedule
            try:
                schedule = Schedule.objects.get(pk=schedule_id)
            except Schedule.DoesNotExist:
                result.append("Schedule does not exist.")
                return TemplateResponse(
                    request,
                    "admin/replace_cast.html",
                    dict(self.each_context(request), result=result),
                )
            today = datetime.date.today()
            for i, line in enumerate(replace_lines.splitlines(), 1):
                line = line.strip()
                if not line:
                    continue
                # 解析格式：日期时间 + 制表符分隔的卡司名单
                m = re.match(
                    r"(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日\s.*?(\d{2}:\d{2})\t(.+)",
                    line,
                )
                if not m:
                    result.append("格式错误：" + line)
                    continue
                year = int(m.group(1)) if m.group(1) else None
                month = int(m.group(2))
                day = int(m.group(3))
                if year is None:
                    if month < today.month:
                        year = today.year + 1
                    else:
                        year = today.year
                hour, minute = map(int, m.group(4).split(":"))
                new_names = [name.strip() for name in m.group(5).split("\t") if name.strip()]
                try:
                    show_time = datetime.datetime(year, month, day, hour, minute)
                except ValueError:
                    result.append("日期无效：" + line)
                    continue
                # 获取 Show
                try:
                    show = Show.objects.get(schedule=schedule, time=show_time)
                except Show.DoesNotExist:
                    result.append("演出不存在：" + line)
                    continue
                # 获取当前卡司，按角色建立映射
                current_casts = show.cast.select_related('role', 'artist').order_by('role__seq')
                print(current_casts)
                if len(new_names) != len(current_casts):
                    result.append("卡司数量不匹配：" + line)
                    continue
                # 逐位对比，不同的就替换
                replaced = []
                for cast, new_name in zip(current_casts, new_names):
                    if cast.artist.name != new_name:
                        try:
                            new_cast = MusicalCast.objects.get(
                                role=cast.role, artist__name=new_name
                            )
                        except MusicalCast.DoesNotExist:
                            result.append("新卡司不存在：" + new_name)
                            break
                        show.cast.remove(cast)
                        show.cast.add(new_cast)
                        replaced.append(cast.artist.name + " → " + new_name)
                else:
                    if replaced:
                        result.append(line + "替换了：" + '，'.join(replaced))
                    else:
                        result.append(line + " 无变化")
        context = dict(
            self.each_context(request),
            title="更换卡司",
            result="\n".join(result),
        )
        return TemplateResponse(request, "admin/replace_cast.html", context)

    def cancel_show_view(self, request):
        result = ""
        if request.method == "POST":
            schedule_id = request.POST.get("schedule_id")
            show_time_str = request.POST.get("show_time_str")
            # 解析时间
            today = datetime.date.today()
            try:
                m = re.search(r"(\d+)月(\d+)日.*?(\d{2}:\d{2})", show_time_str)
                if not m:
                    raise ValueError()
                month = int(m.group(1))
                day = int(m.group(2))
                hour, minute = map(int, m.group(3).split(":"))
                if month < today.month:
                    year = today.year + 1
                else:
                    year = today.year
                show_time = datetime.datetime(year, month, day, hour, minute)
            except Exception:
                result = "Invalid show time format. Example: 4月15日 星期三 19:30"
                return TemplateResponse(
                    request,
                    "admin/cancel_show.html",
                    dict(self.each_context(request), result=result),
                )
            # 获取Schedule
            try:
                schedule = Schedule.objects.get(pk=schedule_id)
            except Schedule.DoesNotExist:
                result = "Schedule does not exist."
                return TemplateResponse(
                    request,
                    "admin/cancel_show.html",
                    dict(self.each_context(request), result=result),
                )
            # 获取Show
            try:
                show = Show.objects.get(schedule=schedule, time=show_time)
            except Show.DoesNotExist:
                result = "Show does not exist."
                return TemplateResponse(
                    request,
                    "admin/cancel_show.html",
                    dict(self.each_context(request), result=result),
                )
            # 删除show
            show.delete()
            result = "Show cancelled successfully."
        context = dict(
            self.each_context(request),
            title="演出取消",
            result=result,
        )
        return TemplateResponse(request, "admin/cancel_show.html", context)


admin_site = CustomAdminSite(name="custom_admin")
