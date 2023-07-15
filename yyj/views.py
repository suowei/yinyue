from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Count, Q
import datetime
from .models import Role, Tour, Schedule, Musical, Produce, Artist, Show, City, Theatre, Stage
from .models import MusicalProduces, MusicalStaff, MusicalCast
from .forms import ShowForm


def index(request):
    now = datetime.datetime.now()
    today = now.date()
    begin = today
    month_list = []
    for i in range(12):
        if begin.month != 12:
            end = datetime.date(begin.year, begin.month + 1, 1)
        else:
            end = datetime.date(begin.year + 1, 1, 1)
        schedule_list = Schedule.objects.filter(
            is_long_term=False, begin_date__lt=end, end_date__gte=begin
        ).select_related(
            'tour', 'tour__musical', 'stage', 'stage__theatre', 'stage__theatre__city'
        ).order_by('stage__theatre__city__seq', 'end_date')
        if schedule_list:
            month_list.append({'month': begin, 'schedule_list': schedule_list})
        begin = end
    long_term_schedule_list = Schedule.objects.filter(
        is_long_term=True, begin_date__lte=today
    ).select_related(
        'tour', 'tour__musical', 'stage', 'stage__theatre', 'stage__theatre__city'
    ).order_by('stage__theatre__city__seq', 'begin_date')
    end = today + datetime.timedelta(7)
    show_list = Show.objects.filter(time__range=(now, end)).select_related(
        'schedule', 'schedule__tour', 'schedule__tour__musical',
        'schedule__stage', 'schedule__stage__theatre', 'schedule__stage__theatre__city'
    ).order_by('schedule__stage__theatre__city__seq', 'time')
    day_list = []
    for show in show_list:
        for day in day_list:
            if day[0].time.date() == show.time.date():
                break
        else:
            day = []
            i = len(day_list)
            while i > 0:
                i -= 1
                if show.time.date() > day_list[i][0].time.date():
                    i += 1
                    break
            day_list.insert(i, day)
        day.append(show)
        show.cast_list = show.cast.select_related('role', 'artist').order_by('role__seq')
    musical_list_dd = Musical.objects.filter(progress=Musical.PROMOTE).order_by('premiere_date')
    schedule_list_new = Schedule.objects.filter(begin_date__gt=today).select_related(
        'tour', 'tour__musical', 'stage', 'stage__theatre', 'stage__theatre__city'
    ).order_by('-id')[:20]
    context = {
        'long_term_schedule_list': long_term_schedule_list,
        'day_list': day_list,
        'month_list': month_list,
        'musical_list_dd': musical_list_dd,
        'schedule_list_new': schedule_list_new,
    }
    return render(request, 'yyj/index.html', context)


def musical_index(request):
    musical_list_zz = Musical.objects.filter(progress=Musical.SETUP).order_by('premiere_date')
    musical_list_dd = Musical.objects.filter(progress=Musical.PROMOTE).order_by('premiere_date')
    musical_list_ss = Musical.objects.filter(progress=Musical.PRESENT).order_by('-premiere_date')
    context = {
        'musical_list_zz': musical_list_zz,
        'musical_list_dd': musical_list_dd,
        'musical_list_ss': musical_list_ss
    }
    return render(request, 'yyj/musical_index.html', context)


def musical_detail(request, pk):
    musical = Musical.objects.get(pk=pk)
    produces = MusicalProduces.objects.filter(musical=musical).select_related('produce').order_by('seq')
    staff_list = MusicalStaff.objects.filter(musical=musical).select_related('artist').order_by('seq')
    today = datetime.datetime.now().date()
    tour_list = Tour.objects.filter(musical=musical, end_date__gte=today).order_by('-end_date')
    tour_list_history = Tour.objects.filter(musical=musical, end_date__lt=today).order_by('-end_date')
    context = {
        'musical': musical,
        'produces': produces,
        'staff_list': staff_list,
        'tour_list': tour_list,
        'tour_list_history': tour_list_history,
    }
    return render(request, 'yyj/musical_detail.html', context)


def tour_detail(request, pk):
    tour = Tour.objects.get(pk=pk)
    role_list = Role.objects.filter(musical=tour.musical).order_by('seq')
    now = datetime.datetime.now()
    today = now.date()
    schedule_list_coming = Schedule.objects.filter(tour=tour, end_date__gte=today).select_related(
        'stage', 'stage__theatre', 'stage__theatre__city').order_by('begin_date')
    for schedule in schedule_list_coming:
        if schedule.is_long_term:
            schedule.show_list_done = Show.objects.filter(schedule=schedule, time__lt=now)[:1]
        schedule.shows = schedule.show_set.filter(time__gte=now).order_by('time')
        for show in schedule.shows:
            show_cast_list = show.cast.select_related('role', 'artist').order_by('seq')
            if not show_cast_list:
                continue
            schedule.has_cast_table = True
            show.cast_table = [None] * len(role_list)
            for show_cast in show_cast_list:
                if show.cast_table[show_cast.role.seq - 1]:
                    show.cast_table[show_cast.role.seq - 1].append(show_cast)
                else:
                    show.cast_table[show_cast.role.seq - 1] = [show_cast]
    schedule_list_done = Schedule.objects.filter(is_long_term=False, tour=tour, begin_date__lte=today).select_related(
        'stage', 'stage__theatre', 'stage__theatre__city').order_by('begin_date')
    for schedule in schedule_list_done:
        schedule.shows = schedule.show_set.filter(time__lt=now).order_by('time')[:30]
        if schedule.show_set.filter(time__lt=now).count() > 30:
            schedule.show_list_more = True
        for show in schedule.shows:
            show_cast_list = show.cast.select_related('role', 'artist').order_by('seq')
            if not show_cast_list:
                continue
            schedule.has_cast_table = True
            show.cast_table = [None] * len(role_list)
            for show_cast in show_cast_list:
                if show.cast_table[show_cast.role.seq - 1]:
                    show.cast_table[show_cast.role.seq - 1].append(show_cast)
                else:
                    show.cast_table[show_cast.role.seq - 1] = [show_cast]
    context = {
        'tour': tour,
        'role_list': role_list,
        'schedule_list_coming': schedule_list_coming,
        'schedule_list_done': schedule_list_done,
    }
    return render(request, 'yyj/tour_detail.html', context)


def schedule_detail(request, pk):
    schedule = Schedule.objects.get(pk=pk)
    tour = schedule.tour
    role_list = Role.objects.filter(musical=tour.musical).order_by('seq')
    now = datetime.datetime.now()
    schedule.shows = schedule.show_set.filter(time__gte=now).order_by('time')
    schedule.show_list_done = Show.objects.filter(schedule=schedule, time__lt=now)[:1]
    for show in schedule.shows:
        show_cast_list = show.cast.select_related('role', 'artist').order_by('seq')
        if not show_cast_list:
            continue
        schedule.has_cast_table = True
        show.cast_table = [None] * len(role_list)
        for show_cast in show_cast_list:
            if show.cast_table[show_cast.role.seq - 1]:
                show.cast_table[show_cast.role.seq - 1].append(show_cast)
            else:
                show.cast_table[show_cast.role.seq - 1] = [show_cast]
    other_schedule_list = Schedule.objects.filter(tour=tour, end_date__gte=now.date()).exclude(pk=pk).select_related(
        'stage', 'stage__theatre', 'stage__theatre__city').order_by('begin_date')
    # today = datetime.datetime.now().date()
    # schedule_list_coming = Schedule.objects.filter(tour=tour, end_date__gte=today) \
    #     .select_related('stage', 'stage__theatre', 'stage__theatre__city').order_by('begin_date')
    # for schedule in schedule_list_coming:
    #     schedule.shows = schedule.show_set.order_by('time')
    #     for show in schedule.shows:
    #         show_cast_list = show.cast.select_related('role', 'artist').order_by('role__seq')
    #         if not show_cast_list:
    #             continue
    #         schedule.has_cast_table = True
    #         show.cast_table = [None] * len(role_list)
    #         for show_cast in show_cast_list:
    #             show.cast_table[show_cast.role.seq - 1] = show_cast
    # schedule_list_done = Schedule.objects.filter(tour=tour, end_date__lt=today) \
    #     .select_related('stage', 'stage__theatre', 'stage__theatre__city').order_by('begin_date')
    # for schedule in schedule_list_done:
    #     schedule.shows = schedule.show_set.order_by('time')
    #     for show in schedule.shows:
    #         show_cast_list = show.cast.select_related('role', 'artist').order_by('role__seq')
    #         if not show_cast_list:
    #             continue
    #         schedule.has_cast_table = True
    #         show.cast_table = [None] * len(role_list)
    #         for show_cast in show_cast_list:
    #             show.cast_table[show_cast.role.seq - 1] = show_cast
    context = {
        'schedule': schedule,
        'role_list': role_list,
        'other_schedule_list': other_schedule_list,
    }
    return render(request, 'yyj/schedule_detail.html', context)


def schedule_show_index(request, pk):
    schedule = Schedule.objects.get(pk=pk)
    role_list = Role.objects.filter(musical=schedule.tour.musical).order_by('seq')
    now = datetime.datetime.now()
    order = request.GET.get('order')
    if order == 'asc':
        show_list_done = Show.objects.filter(schedule=schedule, time__lt=now).order_by('time')
    else:
        show_list_done = Show.objects.filter(schedule=schedule, time__lt=now).order_by('-time')
    paginator = Paginator(show_list_done, 30)
    page = request.GET.get('page')
    show_list = paginator.get_page(page)
    for show in show_list:
        show_cast_list = show.cast.select_related('role', 'artist').order_by('seq')
        if not show_cast_list:
            continue
        schedule.has_cast_table = True
        show.cast_table = [None] * len(role_list)
        for show_cast in show_cast_list:
            if show.cast_table[show_cast.role.seq - 1]:
                show.cast_table[show_cast.role.seq - 1].append(show_cast)
            else:
                show.cast_table[show_cast.role.seq - 1] = [show_cast]
    context = {
        'order': order,
        'schedule': schedule,
        'show_list': show_list,
        'role_list': role_list,
    }
    return render(request, 'yyj/schedule_show_index.html', context)


def produce_detail(request, pk):
    produce = Produce.objects.get(pk=pk)
    musical_produce_list = MusicalProduces.objects.filter(produce=produce).select_related('musical').order_by('-musical__premiere_date')
    context = {'produce': produce, 'musical_produce_list': musical_produce_list}
    return render(request, 'yyj/produce_detail.html', context)


def artist_detail(request, pk):
    artist = Artist.objects.get(pk=pk)
    musical_staff_list = artist.musicalstaff_set.select_related('musical').order_by('-musical__premiere_date')
    musical_cast_list = artist.musicalcast_set.select_related('role', 'role__musical').order_by('role__musical')
    now = datetime.datetime.now()
    show_list_coming = Show.objects.filter(cast__artist=artist, time__gte=now).select_related(
        'schedule', 'schedule__stage', 'schedule__stage__theatre', 'schedule__stage__theatre__city'
    ).extra(
        select={"cast_id": "`yyj_musicalcast`.`id`"}
    ).order_by('time')
    for show in show_list_coming:
        for musical_cast in musical_cast_list:
            if musical_cast.id == show.cast_id:
                show.role = musical_cast.role
                break
    show_list_done = Show.objects.filter(cast__artist=artist, time__lt=now)[:1]
    context = {
        'artist': artist,
        'musical_staff_list': musical_staff_list,
        # 'musical_cast_list': musical_cast_list,
        'show_list_coming': show_list_coming,
        'show_list_done': show_list_done,
    }
    return render(request, 'yyj/artist_detail.html', context)


def artist_show_index(request, pk):
    artist = Artist.objects.get(pk=pk)
    now = datetime.datetime.now()
    show_list_done = Show.objects.filter(cast__artist=artist, time__lt=now).select_related(
        'schedule', 'schedule__stage', 'schedule__stage__theatre', 'schedule__stage__theatre__city'
    ).extra(
        select={"cast_id": "`yyj_musicalcast`.`id`"}
    ).order_by('-time')
    paginator = Paginator(show_list_done, 50)
    page = request.GET.get('page')
    show_list = paginator.get_page(page)
    musical_cast_list = artist.musicalcast_set.select_related('role', 'role__musical')
    for show in show_list:
        for musical_cast in musical_cast_list:
            if musical_cast.id == show.cast_id:
                show.role = musical_cast.role
                break
    context = {'artist': artist, 'show_list': show_list}
    return render(request, 'yyj/artist_show_index.html', context)


def city_detail(request, pk):
    city = City.objects.get(pk=pk)
    now = datetime.datetime.now()
    today = now.date()
    long_term_schedule_list = Schedule.objects.filter(
        is_long_term=True, begin_date__lte=today, end_date__gte=today, stage__theatre__city=city).select_related(
        'tour', 'tour__musical', 'stage', 'stage__theatre').order_by('begin_date')
    schedule_list = Schedule.objects.filter(
        is_long_term=False, begin_date__lte=today, end_date__gte=today, stage__theatre__city=city).select_related(
        'tour', 'tour__musical', 'stage', 'stage__theatre').order_by('end_date')
    schedule_list_coming = Schedule.objects.filter(
        begin_date__gt=today, stage__theatre__city=city).select_related(
        'tour', 'tour__musical', 'stage', 'stage__theatre').order_by('begin_date', 'end_date')
    end = today + datetime.timedelta(7)
    show_list = Show.objects.filter(schedule__stage__theatre__city=city, time__range=(now, end)).select_related(
        'schedule', 'schedule__tour', 'schedule__tour__musical', 'schedule__stage', 'schedule__stage__theatre'
    ).order_by('time')
    day_list = []
    for show in show_list:
        for day in day_list:
            if day[0].time.date() == show.time.date():
                break
        else:
            day = []
            day_list.append(day)
        day.append(show)
        show.cast_list = show.cast.select_related('role', 'artist').order_by('role__seq')
    context = {
        'city': city,
        'long_term_schedule_list': long_term_schedule_list,
        'schedule_list': schedule_list,
        'schedule_list_coming': schedule_list_coming,
        'day_list': day_list,
    }
    return render(request, 'yyj/city_detail.html', context)


def theatre_detail(request, pk):
    theatre = Theatre.objects.get(pk=pk)
    stage_list = theatre.stage_set.all()
    if len(stage_list) > 1:
        theatre.has_multiple_stages = True
    else:
        theatre.has_multiple_stages = False
    now = datetime.datetime.now()
    today = now.date()
    schedule_list = Schedule.objects.filter(end_date__gte=today, stage__theatre=theatre).select_related(
        'tour', 'tour__musical', 'stage').order_by('begin_date')
    for schedule in schedule_list:
        if schedule.begin_date <= today:
            schedule.on_show = True
    show_list = Show.objects.filter(schedule__stage__theatre=theatre, time__gte=now).select_related(
        'schedule', 'schedule__tour', 'schedule__tour__musical', 'schedule__stage',
    ).order_by('time')
    for show in show_list:
        show.cast_list = show.cast.select_related('role', 'artist').order_by('role__seq')
    schedule_list_done = Schedule.objects.filter(stage__theatre=theatre, end_date__lt=today).select_related(
        'tour', 'tour__musical', 'stage').order_by('-end_date')
    context = {
        'theatre': theatre,
        'stage_list': stage_list,
        'schedule_list': schedule_list,
        'show_list': show_list,
        'schedule_list_done': schedule_list_done,
    }
    return render(request, 'yyj/theatre_detail.html', context)


def theatre_show_index(request, pk):
    theatre = Theatre.objects.get(pk=pk)
    stage_list = theatre.stage_set.all()
    if len(stage_list) > 1:
        theatre.has_multiple_stages = True
    else:
        theatre.has_multiple_stages = False
    now = datetime.datetime.now()
    show_list_done = Show.objects.filter(schedule__stage__theatre=theatre, time__lt=now).select_related(
        'schedule', 'schedule__stage', 'schedule__tour', 'schedule__tour__musical'
    ).order_by('-time')
    paginator = Paginator(show_list_done, 50)
    page = request.GET.get('page')
    show_list = paginator.get_page(page)
    for show in show_list:
        show.cast_list = show.cast.select_related('role', 'artist').order_by('role__seq')
    context = {'theatre': theatre, 'show_list': show_list}
    return render(request, 'yyj/theatre_show_index.html', context)


def stage_index(request):
    stage_list = Stage.objects.select_related('theatre', 'theatre__city').order_by('theatre__city__seq', '-seats')
    context = {
        'stage_list': stage_list,
    }
    return render(request, 'yyj/stage_index.html', context)


def stage_detail(request, pk):
    stage = Stage.objects.get(pk=pk)
    if Stage.objects.filter(theatre=stage.theatre).count() > 1:
        stage.is_single = False
    else:
        stage.is_single = True
    now = datetime.datetime.now()
    today = now.date()
    schedule_list = Schedule.objects.filter(end_date__gte=today, stage=stage).select_related(
        'tour', 'tour__musical').order_by('begin_date')
    for schedule in schedule_list:
        if schedule.begin_date <= today:
            schedule.on_show = True
    show_list = Show.objects.filter(schedule__stage=stage, time__gte=now).select_related(
        'schedule', 'schedule__tour', 'schedule__tour__musical',
    ).order_by('time')
    for show in show_list:
        show.cast_list = show.cast.select_related('role', 'artist').order_by('role__seq')
    schedule_list_done = Schedule.objects.filter(stage=stage, end_date__lt=today).select_related(
        'tour', 'tour__musical').order_by('-end_date')
    context = {
        'stage': stage,
        'schedule_list': schedule_list,
        'show_list': show_list,
        'schedule_list_done': schedule_list_done,
    }
    return render(request, 'yyj/stage_detail.html', context)


def stage_show_index(request, pk):
    stage = Stage.objects.get(pk=pk)
    now = datetime.datetime.now()
    show_list_done = Show.objects.filter(schedule__stage=stage, time__lt=now).select_related(
        'schedule', 'schedule__tour', 'schedule__tour__musical'
    ).order_by('-time')
    paginator = Paginator(show_list_done, 50)
    page = request.GET.get('page')
    show_list = paginator.get_page(page)
    for show in show_list:
        show.cast_list = show.cast.select_related('role', 'artist').order_by('role__seq')
    context = {'stage': stage, 'show_list': show_list}
    return render(request, 'yyj/stage_show_index.html', context)


def show_year_index(request, year):
    now = datetime.datetime.now()
    if year == now.year:
        begin_time = datetime.datetime(year, 1, 1, 0, 0, 0)
        num_show = Count('schedule__show', filter=Q(schedule__show__time__gte=begin_time) & Q(schedule__show__time__lte=now))
        tour_list = Tour.objects.filter(begin_date__year__lte=year, end_date__year__gte=year).annotate(
            num_show=num_show).select_related('musical').order_by('begin_date')
    else:
        num_show = Count('schedule__show', filter=Q(schedule__show__time__year=year))
        tour_list = Tour.objects.filter(begin_date__year__lte=year, end_date__year__gte=year).annotate(
            num_show=num_show).select_related('musical').order_by('begin_date')
    musical_list = []
    count = 0
    for tour in tour_list:
        if tour.num_show == 0:
            continue
        for musical in musical_list:
            if musical.id == tour.musical_id:
                break
        else:
            musical = tour.musical
            musical.num_show = 0
            musical.tour_list = []
            musical_list.append(musical)
        musical.num_show += tour.num_show
        musical.tour_list.append(tour)
        count += tour.num_show
    musical_list.sort(key=lambda x: x.num_show, reverse=True)
    context = {'year': year, 'count': count, 'musical_list': musical_list}
    return render(request, 'yyj/show_year_index.html', context)


def show_year_index_city(request, year):
    now = datetime.datetime.now()
    if year == now.year:
        begin_time = datetime.datetime(year, 1, 1, 0, 0, 0)
        num_show = Count('show', filter=Q(show__time__gte=begin_time) & Q(show__time__lte=now))
        schedule_list = Schedule.objects.filter(
            begin_date__year__lte=year, end_date__year__gte=year
        ).annotate(num_show=num_show).select_related(
            'tour', 'tour__musical', 'stage', 'stage__theatre', 'stage__theatre__city'
        ).order_by('begin_date')
    else:
        num_show = Count('show', filter=Q(show__time__year=year))
        schedule_list = Schedule.objects.filter(
            begin_date__year__lte=year, end_date__year__gte=year
        ).annotate(num_show=num_show).select_related(
            'tour', 'tour__musical', 'stage', 'stage__theatre', 'stage__theatre__city'
        ).order_by('begin_date')
    city_list = []
    count = 0
    for schedule in schedule_list:
        if schedule.num_show == 0:
            continue
        for city in city_list:
            if city.id == schedule.stage.theatre.city_id:
                break
        else:
            city = schedule.stage.theatre.city
            city.num_show = 0
            city.musical_list = []
            city_list.append(city)
        for musical in city.musical_list:
            if musical.id == schedule.tour.musical_id:
                break
        else:
            musical = schedule.tour.musical
            musical.num_show = 0
            musical.schedule_list = []
            city.musical_list.append(musical)
        city.num_show += schedule.num_show
        musical.num_show += schedule.num_show
        musical.schedule_list.append(schedule)
        count += schedule.num_show
    city_list.sort(key=lambda x: x.num_show, reverse=True)
    for city in city_list:
        city.musical_list.sort(key=lambda  x: x.num_show, reverse=True)
    context = {'year': year, 'count': count, 'city_list': city_list}
    return render(request, 'yyj/show_year_index_city.html', context)


def show_year_index_artist(request, year):
    now = datetime.datetime.now()
    if year == now.year:
        begin_time = datetime.datetime(year, 1, 1, 0, 0, 0)
        show_count = Count(
            'musicalcast__show', distinct=True,
            filter=Q(musicalcast__show__time__gte=begin_time) & Q(musicalcast__show__time__lte=now)
        )
        artists = Artist.objects.annotate(show_count=show_count).filter(show_count__gt=0).order_by('-show_count')
        paginator = Paginator(artists, 100)
        page = request.GET.get('page')
        artist_list = paginator.get_page(page)
        num_show = Count('show', filter=Q(show__time__gte=begin_time) & Q(show__time__lte=now))
        cast_list = MusicalCast.objects.filter(artist__in=artist_list).annotate(
            num_show=num_show).select_related('role', 'role__musical', 'artist').order_by('-num_show')
    else:
        show_count = Count('musicalcast__show', distinct=True, filter=Q(musicalcast__show__time__year=year))
        artists = Artist.objects.annotate(show_count=show_count).filter(show_count__gt=0).order_by('-show_count')
        paginator = Paginator(artists, 100)
        page = request.GET.get('page')
        artist_list = paginator.get_page(page)
        num_show = Count('show', filter=Q(show__time__year=year))
        cast_list = MusicalCast.objects.filter(artist__in=artist_list).annotate(
            num_show=num_show).select_related('role', 'role__musical', 'artist').order_by('-num_show')
    for artist in artist_list:
        artist.cast_list = []
    for cast in cast_list:
        if cast.num_show == 0:
            continue
        for artist in artist_list:
            if artist.id == cast.artist_id:
                artist.cast_list.append(cast)
                break
    context = {'year': year, 'artist_list': artist_list}
    return render(request, 'yyj/show_year_index_artist.html', context)


def search(request):
    q = request.GET['q']
    artist_list = Artist.objects.filter(name__icontains=q)
    musical_list = Musical.objects.filter(name__icontains=q)
    context = {'artist_list': artist_list, 'musical_list': musical_list}
    return render(request, 'yyj/search.html', context)


def show_day_index(request):
    form = ShowForm(request.GET)
    if form.is_valid():
        date = form.cleaned_data['date']
        city = form.cleaned_data['city']
        if city:
            show_list = Show.objects.filter(
                schedule__stage__theatre__city=city, time__range=(date, date + datetime.timedelta(1))
            ).select_related(
                'schedule', 'schedule__tour', 'schedule__tour__musical', 'schedule__stage',
                'schedule__stage__theatre'
            ).order_by('time')
        else:
            show_list = Show.objects.filter(
                time__range=(date, date + datetime.timedelta(1))
            ).select_related(
                'schedule', 'schedule__tour', 'schedule__tour__musical', 'schedule__stage',
                'schedule__stage__theatre', 'schedule__stage__theatre__city'
            ).order_by('schedule__stage__theatre__city__seq', 'time')
        for show in show_list:
            show.cast_list = show.cast.select_related('role', 'artist').order_by('role__seq')
        context = {
            'form': form,
            'city': city,
            'show_list': show_list,
        }
        return render(request, 'yyj/show_day_index.html', context)
    else:
        city = request.GET.get('city', None)
        if city:
            form = ShowForm(initial={'city': city})
        else:
            form = ShowForm()
        return render(request, 'yyj/show_day_index.html', {'form': form})

