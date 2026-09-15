from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
import datetime
import re
from django.db.models import Q

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
            path("importstaff/", self.admin_view(self.import_staff_view)),
            path("addrolelist/", self.admin_view(self.addrolelist_view)),
            path("stoplongterm/", self.admin_view(self.stop_longterm_view)),
            path("editshowtime/", self.admin_view(self.edit_showtime_view)),
            path("removecast/", self.admin_view(self.remove_cast_view)),
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
        step = "input"
        schedule_id = ""
        showcast_text = ""
        keependdate = False
        pending_roles = []
        pending_casts = []
        musical = None
        schedule = None

        if request.method == "POST":
            schedule_id = request.POST.get("schedule_id", "")
            showcast_text = request.POST.get("showcast", "")
            keependdate = bool(request.POST.get("keependdate"))
            # 获取 Schedule
            try:
                schedule = Schedule.objects.get(pk=int(schedule_id))
            except (Schedule.DoesNotExist, ValueError):
                return TemplateResponse(
                    request,
                    "admin/loadshow.html",
                    dict(self.each_context(request), step="input", result="Schedule does not exist.",
                         schedule_id=schedule_id, showcast_text=showcast_text, keependdate=keependdate),
                )
            musical = schedule.tour.musical
            role_list = list(Role.objects.filter(musical=musical).order_by('seq'))
            musical_cast_list = list(MusicalCast.objects.filter(
                role__musical=musical).select_related('role', 'artist'))

            # === Step 3: 执行（用户已确认）===
            if "confirm" in request.POST:
                pending_roles_count = int(request.POST.get("pending_roles_count", 0))
                pending_casts_count = int(request.POST.get("pending_casts_count", 0))

                lines = showcast_text.strip().split("\n") if showcast_text.strip() else []
                if not lines:
                    return TemplateResponse(
                        request,
                        "admin/loadshow.html",
                        dict(self.each_context(request), step="input", result="请输入卡司排期文本。",
                             schedule_id=schedule_id, showcast_text=showcast_text, keependdate=keependdate),
                    )
                header = [s.strip() for s in lines[0].split('\t')]

                # 1. 创建 Role（按 pending_roles 顺序）
                max_role_seq = Role.objects.filter(musical=musical).order_by("-seq").values_list("seq", flat=True).first() or 0
                new_role_by_col = {}
                for k in range(pending_roles_count):
                    try:
                        col_index = int(request.POST.get("pending_role_col_" + str(k)))
                    except (TypeError, ValueError):
                        continue
                    role_name = request.POST.get("pending_role_name_" + str(k))
                    action = request.POST.get("pending_role_action_" + str(k))
                    if action == "new" and role_name:
                        role, created = Role.objects.get_or_create(
                            musical=musical, name=role_name,
                            defaults={'seq': max_role_seq + 1}
                        )
                        if created:
                            max_role_seq += 1
                        new_role_by_col[col_index] = role

                # 2. 构建 role_id_list（一一对应 header，None 表示该列未匹配且未新增）
                all_roles = list(Role.objects.filter(musical=musical).order_by('seq'))
                role_id_list = []
                for i, s_role in enumerate(header):
                    role = None
                    if i in new_role_by_col:
                        role = new_role_by_col[i]
                    else:
                        for r in all_roles:
                            if s_role == r.name:
                                role = r
                                break
                    role_id_list.append(role)

                # 3. 创建 Artist + MusicalCast
                created_artists_count = 0
                created_casts_count = 0
                for k in range(pending_casts_count):
                    try:
                        col_index = int(request.POST.get("pending_cast_col_" + str(k)))
                    except (TypeError, ValueError):
                        continue
                    name = request.POST.get("pending_cast_name_" + str(k))
                    action = request.POST.get("pending_cast_action_" + str(k))

                    if not action or action == "skip" or not name:
                        continue
                    if col_index >= len(role_id_list) or role_id_list[col_index] is None:
                        continue
                    role = role_id_list[col_index]

                    if action.startswith("match_"):
                        try:
                            artist = Artist.objects.get(pk=int(action.replace("match_", "")))
                        except (Artist.DoesNotExist, ValueError):
                            continue
                    elif action == "new":
                        artist = Artist.objects.create(name=name)
                        created_artists_count += 1
                    else:
                        continue

                    # 创建 MusicalCast（如果不存在）
                    if not MusicalCast.objects.filter(role=role, artist=artist).exists():
                        actor_seq = MusicalCast.objects.filter(role=role).order_by("-seq").values_list("seq", flat=True).first() or 0
                        MusicalCast.objects.create(role=role, artist=artist, seq=actor_seq + 1)
                        created_casts_count += 1

                # 4. 重新查 musical_cast_list（含新建的）
                musical_cast_list = list(MusicalCast.objects.filter(
                    role__musical=musical).select_related('role', 'artist'))

                # 5. 走原 loadshow 后半段逻辑：解析日期 + 创建 Show + add cast + 冲突检查
                today = datetime.date.today()
                year = month = day = hour = minute = None
                for line in lines[1:]:
                    try:
                        row = line.split('\t')
                        row = [s.strip() for s in row]
                        row = [s for s in row if s]
                        for i, s in enumerate(row):
                            numbers = [int(num) for num in re.findall(r'\d+', row[i])]
                            l_numbers = len(numbers)
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
                                    if year < 100:
                                        year += 2000
                                    month = numbers[1]
                                    day = numbers[2]
                                    hour = numbers[3]
                                    minute = numbers[4]
                                break
                            if l_numbers == 2:
                                month = numbers[0]
                                if month < today.month:
                                    year = today.year + 1
                                else:
                                    year = today.year
                                day = numbers[1]
                            elif l_numbers == 3:
                                year = numbers[0]
                                if year < 100:
                                    year += 2000
                                month = numbers[1]
                                day = numbers[2]
                        time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(hour) + ':' + str(minute)
                        show, created = Show.objects.get_or_create(schedule=schedule, time=time)
                        index = i + 1
                        for ci, s_artist in enumerate(row[index:]):
                            if s_artist == "敬请期待":
                                continue
                            found = False
                            if ci < len(role_id_list) and role_id_list[ci] is not None:
                                for musical_cast in musical_cast_list:
                                    if (musical_cast.role == role_id_list[ci]
                                            and musical_cast.artist.name == s_artist):
                                        show.cast.add(musical_cast)
                                        show_count = Show.objects.filter(
                                            cast__artist=musical_cast.artist_id,
                                            time=show.time
                                        ).distinct().count()
                                        if show_count > 1:
                                            Conflict.objects.get_or_create(artist=musical_cast.artist, time=show.time)
                                        found = True
                                        break
                            if not found:
                                role_name = role_id_list[ci].name if ci < len(role_id_list) and role_id_list[ci] else "未知角色"
                                result.append("  ⚠ 未找到卡司：" + role_name + " = " + s_artist)
                        result.append("OK -> " + line)
                    except Exception:
                        result.append("ERROR " + line)

                if not keependdate and year and month and day:
                    end_date = str(year) + '-' + str(month) + '-' + str(day)
                    schedule.end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                    schedule.save()

                stats = "✅ 新增 {} 角色 / {} 演员 / {} 卡司".format(
                    len(new_role_by_col), created_artists_count, created_casts_count)
                result.insert(0, stats)

                context = dict(
                    self.each_context(request),
                    title="导入演出信息",
                    step="input",
                    result="\n".join(result),
                    schedule_id=schedule_id,
                    showcast_text=showcast_text,
                    keependdate=keependdate,
                )
                return TemplateResponse(request, "admin/loadshow.html", context)

            # === Step 2: 解析（产出 pending_roles / pending_casts）===
            lines = showcast_text.strip().split("\n") if showcast_text.strip() else []
            if not lines:
                return TemplateResponse(
                    request,
                    "admin/loadshow.html",
                    dict(self.each_context(request), step="input", result="请输入卡司排期文本。",
                         schedule_id=schedule_id, showcast_text=showcast_text, keependdate=keependdate),
                )
            header = [s.strip() for s in lines[0].split('\t')]

            # 解析 header 角色，一一对应 role_id_list
            role_id_list = []
            for s_role in header:
                found = None
                for role in role_list:
                    if s_role == role.name:
                        found = role
                        break
                role_id_list.append(found)
                if found is None and s_role:
                    # 去重：同一角色名只入一次 pending_roles
                    if not any(pr['role_name'] == s_role for pr in pending_roles):
                        pending_roles.append({
                            'index': len(pending_roles),
                            'col_index': len(role_id_list) - 1,
                            'role_name': s_role,
                        })

            # 解析后续每行：定位时间列，扫描演员列，收集未匹配的 MusicalCast
            for line in lines[1:]:
                try:
                    row = line.split('\t')
                    row = [s.strip() for s in row]
                    row = [s for s in row if s]
                    # 找时间列（含 ':'）
                    time_col = None
                    for i, s in enumerate(row):
                        if ':' in s:
                            time_col = i
                            break
                    if time_col is None:
                        continue
                    # 演员从 time_col + 1 开始，索引 ci 对应 role_id_list[ci]
                    for ci, s_artist in enumerate(row[time_col + 1:]):
                        if s_artist == "敬请期待":
                            continue
                        # 去重：同一 (col_index, artist_name) 只入一次
                        if any(pc['col_index'] == ci and pc['name'] == s_artist for pc in pending_casts):
                            continue
                        role = role_id_list[ci] if ci < len(role_id_list) else None
                        # 检查是否已有 MusicalCast（仅当 role 已存在时）
                        exists = False
                        if role is not None:
                            for mc in musical_cast_list:
                                if mc.role == role and mc.artist.name == s_artist:
                                    exists = True
                                    break
                        if exists:
                            continue
                        # Artist 模糊匹配
                        exact_matches = list(Artist.objects.filter(name=s_artist))
                        if len(exact_matches) == 1:
                            status, artist, candidates = "matched", exact_matches[0], []
                        elif len(exact_matches) > 1:
                            status, artist, candidates = "similar", None, exact_matches
                        else:
                            similar = list(Artist.objects.filter(
                                Q(name__icontains=s_artist) | Q(name__icontains=s_artist[:2])
                            ).distinct()[:10])
                            if similar:
                                status, artist, candidates = "similar", None, similar
                            else:
                                status, artist, candidates = "new", None, []
                        # 显示用的角色名
                        if role is not None:
                            role_name = role.name
                        elif ci < len(header) and header[ci]:
                            role_name = "(待新增: " + header[ci] + ")"
                        else:
                            role_name = "(未知角色)"
                        pending_casts.append({
                            'index': len(pending_casts),
                            'col_index': ci,
                            'role_name': role_name,
                            'name': s_artist,
                            'status': status,
                            'artist': artist,
                            'candidates': candidates,
                        })
                except Exception:
                    continue

            step = "confirm"

        context = dict(
            self.each_context(request),
            title="导入演出信息",
            step=step,
            result="\n".join(result) if result else "",
            schedule_id=schedule_id,
            showcast_text=showcast_text,
            keependdate=keependdate,
            musical=musical,
            schedule=schedule,
            pending_roles=pending_roles,
            pending_casts=pending_casts,
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
                # 解析格式：日期时间 + 制表符、顿号或空格分隔的卡司名单
                m = re.match(
                    r"(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日.*?(\d{1,2}):(\d{2})[\t、 ](.+)",
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
                hour = int(m.group(4))
                minute = int(m.group(5))
                new_names = [name.strip() for name in re.split(r"[\t、 ]", m.group(6)) if name.strip()]
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
        result = []
        if request.method == "POST":
            schedule_id = request.POST.get("schedule_id")
            show_time_text = request.POST.get("show_time_text", "")
            # 获取Schedule
            try:
                schedule = Schedule.objects.get(pk=schedule_id)
            except Schedule.DoesNotExist:
                result.append("Schedule does not exist.")
                return TemplateResponse(
                    request,
                    "admin/cancel_show.html",
                    dict(self.each_context(request), result="\n".join(result)),
                )
            today = datetime.date.today()
            for line in show_time_text.splitlines():
                line = line.strip()
                if not line:
                    continue
                # 解析时间
                try:
                    m = re.search(r"(?:(\d{4})[年./-])?(\d{1,2})[月./-](\d{1,2})日?.*?(\d{1,2}):(\d{2})", line)
                    if not m:
                        raise ValueError()
                    year = int(m.group(1)) if m.group(1) else None
                    month = int(m.group(2))
                    day = int(m.group(3))
                    hour = int(m.group(4))
                    minute = int(m.group(5))
                    if year is None:
                        if month < today.month:
                            year = today.year + 1
                        else:
                            year = today.year
                    show_time = datetime.datetime(year, month, day, hour, minute)
                except Exception:
                    result.append("格式错误：" + line)
                    continue
                # 获取Show
                try:
                    show = Show.objects.get(schedule=schedule, time=show_time)
                except Show.DoesNotExist:
                    result.append("演出不存在：" + line)
                    continue
                # 删除show
                show.delete()
                result.append("已取消：" + line)
        context = dict(
            self.each_context(request),
            title="演出取消",
            result="\n".join(result),
        )
        return TemplateResponse(request, "admin/cancel_show.html", context)

    def remove_cast_view(self, request):
        result = []
        if request.method == "POST":
            schedule_id = request.POST.get("schedule_id")
            show_cast_text = request.POST.get("show_cast_text", "")
            try:
                schedule = Schedule.objects.get(pk=schedule_id)
            except Schedule.DoesNotExist:
                result.append("Schedule does not exist.")
                context = dict(
                    self.each_context(request),
                    title="去除多余卡司",
                    result="\n".join(result),
                )
                return TemplateResponse(request, "admin/remove_cast.html", context)
            today = datetime.date.today()
            for line in show_cast_text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    m = re.search(r"(?:(\d{4})[年./-])?(\d{1,2})[月./-](\d{1,2})日?.*?(\d{1,2}):(\d{2})", line)
                    if not m:
                        raise ValueError("时间格式无法解析")
                    year = int(m.group(1)) if m.group(1) else None
                    month = int(m.group(2))
                    day = int(m.group(3))
                    hour = int(m.group(4))
                    minute = int(m.group(5))
                    if year is None:
                        if month < today.month:
                            year = today.year + 1
                        else:
                            year = today.year
                    show_time = datetime.datetime(year, month, day, hour, minute)
                    artist_name = line[m.end():].strip().lstrip('\t').lstrip('、').strip()
                    if not artist_name:
                        raise ValueError("缺少演员名")
                except Exception as e:
                    result.append(line + " → " + str(e))
                    continue
                try:
                    show = Show.objects.get(schedule=schedule, time=show_time)
                except Show.DoesNotExist:
                    result.append(line + " → 演出不存在")
                    continue
                try:
                    artist = Artist.objects.get(name=artist_name)
                except Artist.DoesNotExist:
                    result.append(line + " → 演员不存在：" + artist_name)
                    continue
                removed = []
                for musical_cast in show.cast.select_related('artist', 'role').all():
                    if musical_cast.artist == artist:
                        show.cast.remove(musical_cast)
                        removed.append(musical_cast.role.name + "/" + musical_cast.artist.name)
                if removed:
                    result.append("已移除：" + line + " → " + '，'.join(removed))
                else:
                    result.append(line + " → 该演员不在该场卡司中")
        context = dict(
            self.each_context(request),
            title="去除多余卡司",
            result="\n".join(result),
        )
        return TemplateResponse(request, "admin/remove_cast.html", context)

    def edit_showtime_view(self, request):
        result = ""
        if request.method == "POST":
            schedule_id = request.POST.get("schedule_id")
            old_time_str = request.POST.get("old_time_str")
            new_time_str = request.POST.get("new_time_str")
            today = datetime.date.today()

            def _parse_time(s):
                m = re.search(r"(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日.*?(\d{1,2}):(\d{2})", s)
                if not m:
                    raise ValueError("时间格式无法解析")
                year = int(m.group(1)) if m.group(1) else None
                month = int(m.group(2))
                day = int(m.group(3))
                hour = int(m.group(4))
                minute = int(m.group(5))
                if year is None:
                    if month < today.month:
                        year = today.year + 1
                    else:
                        year = today.year
                return datetime.datetime(year, month, day, hour, minute)

            try:
                old_show_time = _parse_time(old_time_str)
            except Exception:
                result = "原时间格式错误。示例：4月15日 19:30 或 2026年4月15日 周四 19:30"
                return TemplateResponse(
                    request,
                    "admin/edit_showtime.html",
                    dict(self.each_context(request), result=result),
                )
            try:
                new_show_time = _parse_time(new_time_str)
            except Exception:
                result = "新时间格式错误。示例：4月15日 19:30 或 2026年4月15日 周四 19:30"
                return TemplateResponse(
                    request,
                    "admin/edit_showtime.html",
                    dict(self.each_context(request), result=result),
                )
            # 获取Schedule
            try:
                schedule = Schedule.objects.get(pk=schedule_id)
            except Schedule.DoesNotExist:
                result = "Schedule does not exist."
                return TemplateResponse(
                    request,
                    "admin/edit_showtime.html",
                    dict(self.each_context(request), result=result),
                )
            # 获取原时间对应的Show
            try:
                show = Show.objects.get(schedule=schedule, time=old_show_time)
            except Show.DoesNotExist:
                result = "原时间的演出不存在。"
                return TemplateResponse(
                    request,
                    "admin/edit_showtime.html",
                    dict(self.each_context(request), result=result),
                )
            # 检查新时间是否冲突
            if Show.objects.filter(schedule=schedule, time=new_show_time).exclude(pk=show.pk).exists():
                result = "新时间下该 Schedule 已有演出，无法修改（会重复）。"
                return TemplateResponse(
                    request,
                    "admin/edit_showtime.html",
                    dict(self.each_context(request), result=result),
                )
            # 更新时间
            show.time = new_show_time
            show.save()
            result = "✅ 修改成功：{} → {}".format(old_show_time, new_show_time)
        context = dict(
            self.each_context(request),
            title="修改演出时间",
            result=result,
        )
        return TemplateResponse(request, "admin/edit_showtime.html", context)

    def import_staff_view(self, request):
        import re
        from django.db.models import Q

        result = ""
        step = "input"
        musical = None
        items = []
        created = 0

        if request.method == "POST":
            musical_id = request.POST.get("musical_id")

            # 获取 Musical
            try:
                musical = Musical.objects.get(pk=musical_id)
            except Musical.DoesNotExist:
                result = "Musical does not exist."
                return TemplateResponse(
                    request,
                    "admin/import_staff.html",
                    dict(self.each_context(request), step="input", result=result),
                )

            if "confirm" in request.POST:
                count = int(request.POST.get("item_count", 0))
                max_seq = MusicalStaff.objects.filter(
                    musical=musical
                ).order_by("-seq").values_list("seq", flat=True).first() or 0

                for i in range(count):
                    job = request.POST.get("job_" + str(i))
                    action = request.POST.get("action_" + str(i))
                    name = request.POST.get("name_" + str(i))

                    if not action or action == "skip":
                        continue

                    if action.startswith("match_"):
                        artist = Artist.objects.get(pk=int(action.replace("match_", "")))
                    elif action == "new":
                        artist = Artist.objects.create(name=name)
                    else:
                        continue

                    max_seq += 1
                    MusicalStaff.objects.create(
                        musical=musical, job=job, artist=artist, seq=max_seq,
                    )
                    created += 1

                result = "✅ 成功导入 " + str(created) + " 条 staff 到「" + str(musical) + "」"
                return TemplateResponse(
                    request,
                    "admin/import_staff.html",
                    dict(self.each_context(request), step="done", result=result),
                )

            # Step 1: 解析文本
            raw_text = request.POST.get("raw_text", "")
            if not raw_text.strip():
                result = "请输入 staff 文本。"
                return TemplateResponse(
                    request,
                    "admin/import_staff.html",
                    dict(self.each_context(request), step="input", result=result),
                )

            for line in raw_text.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                # 优先冒号分隔，否则第一个空白符分隔
                m = re.match(r"^(.+?)[：:]\s*(.+)$", line)
                if not m:
                    m = re.match(r"^(\S+)\s+(.+)$", line)
                if not m:
                    continue
                job = m.group(1).strip()
                names = re.split(r"[、，,/\s]+", m.group(2).strip())
                for name in names:
                    name = name.strip()
                    if not name:
                        continue

                    exact_matches = list(Artist.objects.filter(name=name))
                    if len(exact_matches) == 1:
                        status, artist, candidates = "matched", exact_matches[0], []
                    elif len(exact_matches) > 1:
                        # 同名 artist 多个，全部放入下拉列表供选择
                        status, artist, candidates = "similar", None, exact_matches
                    else:
                        similar = list(Artist.objects.filter(
                            Q(name__icontains=name) | Q(name__icontains=name[:2])
                        ).distinct()[:10])
                        if similar:
                            status, artist, candidates = "similar", None, similar
                        else:
                            status, artist, candidates = "new", None, []

                    items.append({
                        "index": len(items),
                        "job": job,
                        "name": name,
                        "status": status,
                        "artist": artist,
                        "candidates": candidates,
                    })

            step = "confirm"

        context = dict(
            self.each_context(request),
            title="导入 Staff",
            step=step,
            musical=musical,
            items=items,
            result=result,
        )
        return TemplateResponse(request, "admin/import_staff.html", context)

    def addrolelist_view(self, request):
        result = ""
        step = "input"
        musical = None
        items = []
        created_roles = 0
        created_casts = 0
        if request.method == "POST":
            musical_id = request.POST.get("musical_id")
            try:
                musical = Musical.objects.get(pk=musical_id)
            except Musical.DoesNotExist:
                result = "Musical does not exist."
                return TemplateResponse(
                    request,
                    "admin/addrolelist.html",
                    dict(self.each_context(request), step="input", result=result),
                )
            if "confirm" in request.POST:
                count = int(request.POST.get("item_count", 0))
                max_role_seq = Role.objects.filter(
                    musical=musical
                ).order_by("-seq").values_list("seq", flat=True).first() or 0
                current_role = None
                current_role_name = None
                actor_seq = 0
                for i in range(count):
                    role_name = request.POST.get("role_name_" + str(i))
                    action = request.POST.get("action_" + str(i))
                    name = request.POST.get("name_" + str(i))
                    if not action or action == "skip":
                        continue
                    if role_name != current_role_name:
                        current_role_name = role_name
                        current_role = Role.objects.filter(
                            musical=musical, name=role_name
                        ).first()
                        if not current_role:
                            max_role_seq += 1
                            current_role = Role.objects.create(
                                musical=musical, name=role_name, seq=max_role_seq
                            )
                            created_roles += 1
                        actor_seq = MusicalCast.objects.filter(
                            role=current_role
                        ).order_by("-seq").values_list("seq", flat=True).first() or 0
                    if action.startswith("match_"):
                        artist = Artist.objects.get(pk=int(action.replace("match_", "")))
                    elif action == "new":
                        artist = Artist.objects.create(name=name)
                    else:
                        continue
                    if MusicalCast.objects.filter(role=current_role, artist=artist).exists():
                        continue
                    actor_seq += 1
                    MusicalCast.objects.create(
                        role=current_role, artist=artist, seq=actor_seq
                    )
                    created_casts += 1
                result = (
                        "✅ 成功为「" + str(musical) + "」添加了 "
                        + str(created_roles) + " 个角色、"
                        + str(created_casts) + " 位演员"
                )
                return TemplateResponse(
                    request,
                    "admin/addrolelist.html",
                    dict(self.each_context(request), step="done", result=result),
                )
            raw_text = request.POST.get("raw_text", "")
            if not raw_text.strip():
                result = "请输入角色列表文本。"
                return TemplateResponse(
                    request,
                    "admin/addrolelist.html",
                    dict(self.each_context(request), step="input", result=result),
                )
            blocks = []
            current_block = []
            for line in raw_text.strip().split("\n"):
                line = line.strip()
                if not line:
                    if current_block:
                        blocks.append(current_block)
                        current_block = []
                else:
                    current_block.append(line)
            if current_block:
                blocks.append(current_block)
            for block in blocks:
                role_name = block[0]
                actors = block[1:] if len(block) > 1 else []
                for name in actors:
                    name = name.strip()
                    if not name:
                        continue
                    exact_matches = list(Artist.objects.filter(name=name))
                    if len(exact_matches) == 1:
                        status, artist, candidates = "matched", exact_matches[0], []
                    elif len(exact_matches) > 1:
                        # 同名 artist 多个，全部放入下拉列表供选择
                        status, artist, candidates = "similar", None, exact_matches
                    else:
                        similar = list(Artist.objects.filter(
                            Q(name__icontains=name) | Q(name__icontains=name[1:])
                        ).distinct()[:10])
                        if similar:
                            status, artist, candidates = "similar", None, similar
                        else:
                            status, artist, candidates = "new", None, []
                    items.append({
                        "index": len(items),
                        "role_name": role_name,
                        "name": name,
                        "status": status,
                        "artist": artist,
                        "candidates": candidates,
                    })
            step = "confirm"
        context = dict(
            self.each_context(request),
            title="添加角色列表",
            step=step,
            musical=musical,
            items=items,
            result=result,
        )
        return TemplateResponse(request, "admin/addrolelist.html", context)

    def stop_longterm_view(self, request):
        result = ""
        if request.method == "POST":
            schedule_id = request.POST.get("schedule_id")
            # 获取 Schedule
            try:
                schedule = Schedule.objects.get(pk=schedule_id)
            except Schedule.DoesNotExist:
                result = "Schedule does not exist."
                return TemplateResponse(
                    request,
                    "admin/stoplongterm.html",
                    dict(self.each_context(request), result=result),
                )
            # 获取该 Schedule 最后一场 Show 的日期
            last_show = Show.objects.filter(schedule=schedule).order_by("-time").first()
            if not last_show:
                result = "该 Schedule 没有任何 Show，无法确定 end_date。"
                return TemplateResponse(
                    request,
                    "admin/stoplongterm.html",
                    dict(self.each_context(request), result=result),
                )
            last_date = last_show.time.date()
            # 更新 Schedule
            schedule.end_date = last_date
            schedule.is_long_term = False
            schedule.save()
            # 更新对应的 Tour
            tour = schedule.tour
            tour.end_date = last_date
            tour.is_long_term = False
            tour.save()
            result = (
                "✅ 已停止驻演。\n"
                "Schedule #{pk}：end_date = {date}，is_long_term = False\n"
                "Tour #{tour_pk}：end_date = {date}，is_long_term = False"
            ).format(pk=schedule.pk, tour_pk=tour.pk, date=last_date)
        context = dict(
            self.each_context(request),
            title="停止驻演",
            result=result,
        )
        return TemplateResponse(request, "admin/stoplongterm.html", context)


admin_site = CustomAdminSite(name="custom_admin")
