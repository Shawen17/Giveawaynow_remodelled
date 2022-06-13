from django.core.management.base import BaseCommand
from django.utils import timezone
from givers.models import Give,Vendor
from datetime import datetime,timedelta, tzinfo
from django.db.models import Q



class Command(BaseCommand):
    help = 'Displays current time'

    # def handle(self, *args, **kwargs):
    #     vend=Vendor.objects.filter(payment_status=True,request_date__isnull=False)
        
    #     data = {
    #         'delivered':True
    #         }
    #     for obj in vend:
    #         b=timezone.now()-obj.request_date
    #         diff=int(b.days)
    #         if diff>=10 and obj.gift.payment_status==False:
    #             obj.delivered= data['delivered']
    #             obj.save()
    #     self.stdout.write("It's now done")

    def handle(self, *args, **kwargs):
        processed=['paid','on-delivery']
        gives=Give.objects.filter(gift_status__in=processed)
        
        data = {
            'delivered':True
            }
        for obj in gives:
            b=timezone.now()-obj.request_date
            diff=int(b.days)
            if diff>=10:
                obj.gift.delivered= data['delivered']
                obj.gift_status='received'
                obj.date_received=timezone.now()
                obj.save()
        self.stdout.write("It's now done")