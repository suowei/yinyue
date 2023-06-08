from django.core.management.base import BaseCommand
from yyj.models import Role, TourCast, MusicalCast


class Command(BaseCommand):

    def handle(self, *args, **options):
        role_list = Role.objects.all()
        for role in role_list:
            tour_cast_list = TourCast.objects.filter(role=role).select_related(
                'tour').order_by('tour__begin_date', 'seq')
            musical_cast_list = []
            for tour_cast in tour_cast_list:
                musical_cast, created = MusicalCast.objects.get_or_create(role=role, artist=tour_cast.artist)
                tour_cast.musical_cast = musical_cast
                tour_cast.save()
                if created:
                    musical_cast_list.append(musical_cast)
            seq = 1
            for musical_cast in musical_cast_list:
                musical_cast.seq = seq
                musical_cast.save()
                seq += 1
