from functools import partial
from itertools import groupby
from operator import attrgetter
from .models import OnDeliveryTransaction,Transaction,Give,Charge
from django.forms.models import ModelChoiceIterator, ModelChoiceField
from django.utils import timezone

class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __init__(self, field, groupby):
        self.groupby = groupby
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset
        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, objs in groupby(queryset, self.groupby):
            yield (group, [self.choice(obj) for obj in objs])


class GroupedModelChoiceField(ModelChoiceField):
    def __init__(self, *args, choices_groupby, **kwargs):
        if isinstance(choices_groupby, str):
            choices_groupby = attrgetter(choices_groupby)
        elif not callable(choices_groupby):
            raise TypeError('choices_groupby must either be a str or a callable accepting a single argument')
        self.iterator = partial(GroupedModelChoiceIterator, groupby=choices_groupby)
        super().__init__(*args, **kwargs)


def show_up(*item):
    pass



def final_checkout(Model,account_owner,cost):
    
    service_charge=Charge.objects.get(name='standard').charge
    #change gift_recipient=user.email
    give=Give.objects.select_related('gift').filter(gift_recipient=account_owner,gift_status='redeemed')
    ondelivery_total=cost+service_charge
    if ondelivery_total>=2500:
        paystack_charge=100 + (0.015*ondelivery_total)
    else:
        paystack_charge=(0.015*ondelivery_total)
        
    paystack_charge=round(paystack_charge,2)
    paid_delivery_total=cost+service_charge+paystack_charge
    ids=[]
    item=[]
    a=[]
    address=[]
    for i in give:
        b=i.gift.address
        c=i.description
        ids.append(i.id)
        e=str(0)+str(i.giver_number)
        d=f'{b} ({e})---{c}'
        item.append(c)
        a.append(d)
        address.append(i.gift.delivery_address)
        print(address)
        phone=str(0)+str(i.gift.receiver_number)
    ordered_giveaway=[]
    for count,ele in enumerate(item,1):
        t= f'{count}.{ele}'
        ordered_giveaway.append(t)
    ordered_giveaway=('\n'.join(ordered_giveaway))
    letter=[]
    for count,ele in enumerate(a,1):
        t= f'{count}.{ele}   '
        letter.append(t)
    letter=('\n'.join(letter))
    address=address[0] + f'({phone})'
    if isinstance(Model,Transaction):
        data={
        'made_by':account_owner,
        'email':account_owner.email,   
        'items_id':ids,
        'amount':paid_delivery_total,
        'pickup_location':letter,
        'delivery_address':address
        }
        return data,paystack_charge
    elif isinstance(Model,OnDeliveryTransaction):
        for i in give:
            i.gift.payment_status='on-delivery'
            i.gift_status='on-delivery'
            i.save()
        data={
        'made_by':account_owner,
        'email':account_owner.email,
        'made_on':timezone.now(),
        'items_id':ids,
        'amount':ondelivery_total,
        'pickup_location':letter,
        'delivery_address':address,
        'delivered':False
        }
        return data,ordered_giveaway



        
