from givers.models import Give,Vendor
from datetime import datetime,timedelta, tzinfo
from django.utils import timezone
from django.db.models import Q

#update update_picked from views
def update_picked():
    selected=['requested','redeemed']
    give=Give.objects.filter(gift_status__in=selected)
    a=timezone.now()
    current_time=a.replace(tzinfo=None)
    data = {
                'date_requested':None,
                'gift_recipient': '',
                'gift_status':'unpicked'}
    if give:
        for obj in give:
            w=obj.date_requested
            date_requested=w.replace(tzinfo=None)
            if current_time-timedelta(hours=2)<=date_requested<=current_time+timedelta(hours=2):
                obj.date_requested= data['date_requested']
                obj.gift_recipient= data['gift_recipient']
                obj.gift_status=data['gift_status']
                obj.gift.ticket=''
                obj.gift.amount=None
                obj.gift.receiver_number=None
                obj.gift.delivery_address=None
                obj.save()

