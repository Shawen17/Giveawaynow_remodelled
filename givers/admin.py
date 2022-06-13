from django.contrib import admin
from .models import Profile,Give,GiveImage,ContactUs,Received,Vendor,Transaction,Charge,OnDeliveryTransaction,Subscription,Location,OnPickup,State,PickupCentre,GiveawayCap,DestinationCharge
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
import csv
from django.http import HttpResponse
from rest_framework.authtoken.admin import TokenAdmin


TokenAdmin.raw_id_fields=['user']

@admin.register(Charge)
class ChargeAdmin(ModelAdmin):
    list_display=('name','charge')

@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display=('ref','email','made_by','made_on','items_id','pickup_location','delivery_address','amount','verified','delivered')
    ordering =('-made_on',)
    search_fields =('ref','email')
    actions=['mark_delivered']

    def mark_delivered(self,request,queryset):
        queryset.update(delivered=True)
        for i in queryset:
            gives=Give.objects.filter(id__in=i.items_id).update(gift_status='received',date_received=timezone.now())
            
    mark_delivered.short_description = 'Mark as Delivered'

@admin.register(OnDeliveryTransaction)
class OnDeliveryTransactionAdmin(ModelAdmin):
    list_display=('ref','email','made_by','made_on','items_id','pickup_location','delivery_address','amount','delivered')
    ordering =('-made_on',)
    search_fields =('ref','made_by','email')
    actions=['mark_delivered']

    def mark_delivered(self,request,queryset):
        queryset.update(delivered=True)
        for i in queryset:
            gives=Give.objects.filter(id__in=i.items_id).update(gift_status='received',date_received=timezone.now())
            vends=Vendor.objects.filter(give__in=i.items_id).update(payment_status='paid')

    mark_delivered.short_description = 'Mark as Delivered'

@admin.register(Received)
class ReceivedAdmin(ModelAdmin):
    list_display =('gift_requested','date_requested','date_received')
    ordering = ('-date_requested','-date_received')
    search_fields = ('gift_requested',)

@admin.register(ContactUs)
class ContactUsAdmin(ModelAdmin):
    list_display =('ticket','email','subject','body','date')
    ordering =('-date','subject',)
    search_fields = ('email','ticket')

@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display=('state','phone_number','sex','profile_pic','package','end_date','balance','status')
    search_fields=('state',)
    ordering = ('package','status',)

class ProfileInline(admin.StackedInline):
    model=Profile
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = 'profile'



class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    

class GiveImageInline(admin.StackedInline):
    model=GiveImage
    fk_name= 'give'
    can_delete= False
    verbose_name_plural = 'giveimage'

class VendorInline(admin.StackedInline):
    model= Vendor
    fk_name= 'give'
    can_delete = False
    verbose_name_plural= 'gift'

@admin.register(Give)
class GiveAdmin(ModelAdmin):
    inlines=(GiveImageInline,VendorInline)
    list_display= ('description','category','gift_recipient','state','address','gender','quantity','giver_number','date_posted','date_requested','date_received','gift_status')
    search_fields=('category','description','gift_recipient',)
    ordering=('-date_posted','category',)
    actions = ['mark_unpicked']

    def mark_unpicked(self,request,queryset):
        queryset.update(gift_status='unpicked')

    mark_unpicked.short_description='Mark as Unpicked'
    
  

@admin.register(GiveImage)
class GiveImageAdmin(ModelAdmin):
    pass


@admin.register(Vendor)
class VendorAdmin(ModelAdmin):
    list_display=('ticket','give','description','image','category','request_date','giver_number','address','receiver_number','delivery_address','amount','payment_status','pickup_location','treated')
    ordering=('-request_date','treated')
    search_fields=('ticket',)
    actions=['mark_treated','mark_return']

    def mark_return(self,request,queryset):
        queryset.update(payment_status='unpaid',amount=None,delivery_address=None,receiver_number=None,request_date=None,ticket='')
        data = {
                'date_requested':None,
                'gift_recipient': '',
                'gift_status':'unpicked'}
        give_ids=[i.id for i in queryset]
        give=Give.objects.filter(id__in=give_ids).update(**data)
        # for i in queryset:

        #     give=Give.objects.get(description=i.description)
        #     give.date_requested=data['date_requested']
        #     give.gift_recipient=data['gift_recipient']
        #     give.gift_status=data['gift_status']
        #     give.save(update_fields=['date_requested','gift_recipient','gift_status'])


    def mark_treated(self,request,queryset):
        queryset.update(treated=True)

    mark_return.short_description='Return Item(s)'
    mark_treated.short_description = 'Mark as Treated'
    

@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display=('ref','email','made_by','start_date','end_date','amount','balance','verified')
    ordering=('-end_date','verified')
    search_fields=('ref','email',)

@admin.register(State)
class StateAdmin(ModelAdmin):
    list_display=('name',)

@admin.register(PickupCentre)
class PickupCentreAdmin(ModelAdmin):
    list_display=('name',)


@admin.register(Location)
class LocationAdmin(ModelAdmin):
    list_display=('address','phone_number')
    search_fields=('phone_number',)
    

@admin.register(OnPickup)
class OnPickupAdmin(ModelAdmin):
    list_display=('ref','made_on','made_by','items_id','email','item','state','pickup_centre','collection_status')
    ordering=('-made_on','state','collection_status')
    search_fields=('pickup_centre','email')
    actions=['mark_delivered']

    def mark_delivered(self,request,queryset):
        queryset.update(collection_status=True)
        data={
            'gift_status':'received',
            'date_received':timezone.now()
        }
        for i in queryset:
            gives=Give.objects.filter(id__in=i.items_id).update(**data)
            # for give in gives:
            #     give.gift_status='received'
            #     give.date_received=timezone.now()
            #     give.save(update_fields=['gift_status','date_received'])

    mark_delivered.short_description = 'Mark as Collected'

@admin.register(GiveawayCap)
class GiveawayCapAdmin(ModelAdmin):
    list_display=('name','number')

@admin.register(DestinationCharge)
class DestinationChargeAdmin(ModelAdmin):
    list_display=('state','city','charge')
    actions=['export_rate']

    def export_rate(self,request,queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        writer = csv.writer(response)
        writer.writerow(['Destination','Charge'])
        orders = queryset.values_list('city','charge')
        for order in orders:
            writer.writerow(order)
        return response
    export_rate.short_description = 'Export to csv'

admin.site.unregister(User)
admin.site.register(User,UserAdmin)

