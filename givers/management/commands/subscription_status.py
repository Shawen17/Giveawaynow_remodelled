from django.core.management.base import BaseCommand
from django.utils import timezone
from givers.models import Profile
from datetime import datetime,timedelta, tzinfo
from django.db.models import Q



class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        prof=Profile.objects.filter(status=True)
        for obj in prof:
            if obj.balance==0:
                obj.status=False
                obj.save()
        self.stdout.write("It's now done")