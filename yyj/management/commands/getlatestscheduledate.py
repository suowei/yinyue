from django.core.management.base import BaseCommand
from yyj.models import Schedule


class Command(BaseCommand):
    help = 'Get schedule latest date.'

    def add_arguments(self, parser):
        parser.add_argument('schedule_id', nargs='?')

    def handle(self, *args, **options):
        pk = int(options['schedule_id'])
        schedule = Schedule.objects.get(pk=pk)
        latest_show = schedule.show_set.latest('time')
        schedule.end_date = latest_show.time.date()
        schedule.save()
