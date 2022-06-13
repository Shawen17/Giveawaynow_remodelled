from django.db import models
from django import dispatch
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
import pandas as pd
from Giveaway.settings import STATIC_ROOT
from django.utils import timezone
import secrets
from datetime import datetime,date,time,timedelta
from .paystack import PayStack
from django.contrib.postgres.fields import JSONField 
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
import random
from django.utils.translation import ugettext_lazy as _

def validate_number(value):
    if len(str(value))==10:
        return value
    else:
        raise ValidationError(_('Your phone number is incorrect'))

file_path = os.path.join(STATIC_ROOT,'givers\\state.xlsx')
df = pd.read_excel(file_path)
df1= zip(df.value,df.representation)
states=[]
for i,j in df1:
    states.append((i,j))

file_path = os.path.join(STATIC_ROOT,'givers\\vendor.xlsx')
df = pd.read_excel(file_path)
df1= zip(df.value,df.representation)
vendors=[]
for i,j in df1:
    vendors.append((i,j))



com_list=(
    ('enquiry','Enquiry'),
    ('complaint','Complaint'),
    ('report','Report'),
    ('others','Others')
)

gender =(
    ('M','Male'),
    ('F','Female')
)

categories =(
    ('fur','Furniture'),
    ('clo','Clothes'),
    ('sho','Shoes'),
    ('toy','toys'),
    ('ele','Electronics'),
    ('bag','Bags'),
    ('fon','mobile-phones'),
    ('lap','Laptops'),
    ('buk','Books'),
    ('kit','Kitchen-utensils'),
    ('bic','Bicyle'),
    ('ace','Accessories'),
    ('fud','Food-stuffs'),
    ('gro','Groceries'),
    ('gen','Generator'),
    ('bty','Beauty-product'),
    ('nat','Natives')
)

status=(
    ('unpicked','unpicked'),
    ('requested','requested'),
    ('received','received'),
    ('redeemed','redeemed'),
    ('on-delivery','on-delivery'),
    ('on-pickup','on-pickup'),
    ('paid','paid')
)

pay_status=(
    ('unpaid','unpaid'),
    ('paid','paid'),
    ('on-delivery','on-delivery'),
    ('on-pickup','on-pickup')
)

sub_package=(
    ('basic','basic'),
    ('standard','standard'),
    ('premium','premium')
)

class Profile(models.Model):
    user= models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    state=models.CharField(max_length=50,choices=states)
    phone_number=models.IntegerField(default=int('08000000000'))
    sex=models.CharField(max_length=10,choices=gender,blank=True,default='')
    profile_pic = models.ImageField(upload_to='givers/images',default='default_pic.jpg')
    bio = models.TextField(blank=True,default='')
    package=models.CharField(max_length=20,choices=sub_package,default='basic')
    end_date=models.DateTimeField(null=True,blank=True)
    balance=models.IntegerField(default=0)
    status=models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


@receiver(post_save,sender=User,dispatch_uid='user.created')   
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Give(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    state=models.CharField(max_length=40,choices=states)
    category=models.CharField(max_length=50,blank=True,default='',choices=categories)
    description = models.CharField(max_length=50)
    image= models.ImageField(blank=True)
    gender=models.CharField(max_length=10,choices=gender,blank=True,default='')
    quantity=models.IntegerField()
    giver_number=models.IntegerField(default='')
    address=models.TextField(default='Head office')
    date_posted=models.DateTimeField(auto_now_add=True)
    date_requested = models.DateTimeField(null=True,blank=True)
    date_received = models.DateTimeField(null=True,blank=True)
    gift_recipient = models.CharField(max_length=100,default='',blank=True)
    gift_status = models.CharField(max_length=30,default='unpicked',blank=True,choices=status)

    def __str__(self):
        return self.description

    

class GiveImage(models.Model):
    give= models.ForeignKey(Give,default=None,on_delete=models.CASCADE,related_name='giveimage')
    images= models.ImageField(upload_to='givers/images/')

    def __str__(self):
        return self.giveimage.give


class ContactUs(models.Model):
    ticket=models.CharField(max_length=15,blank=True,default='')
    email= models.EmailField(max_length=150)
    subject= models.CharField(max_length=20,choices=com_list)
    body=models.TextField()
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class Received(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='person')
    gift_requested = models.OneToOneField(Give,on_delete=models.CASCADE,related_name='commodity')
    date_requested = models.DateTimeField(auto_now_add=True)
    date_received = models.DateTimeField(auto_now_add=True)


class Vendor(models.Model):
    give = models.OneToOneField(Give,on_delete=models.CASCADE,related_name='gift')
    ticket = models.CharField(max_length=10,blank=True,default='')
    image=models.ImageField(upload_to='givers/images/')
    state = models.CharField(max_length=50,choices=states,default='')
    description=models.CharField(max_length=100)
    request_date=models.DateTimeField(blank=True,null=True)
    category = models.CharField(max_length=100,choices=categories)
    giver_number=models.IntegerField(blank=True,null=True)  
    address=models.TextField(default='Head Office')
    receiver_number=models.IntegerField(blank=True,null=True,validators=[validate_number])
    delivery_address =models.TextField(max_length=200,blank=True,null=True)
    amount = models.IntegerField(blank=True,null=True)
    payment_status = models.CharField(max_length=30,choices=pay_status,default='unpaid')
    pickup_location=models.CharField(max_length=50,default='',blank=True,null=True)
    treated=models.BooleanField(default=False)

    def __str__(self):
        return self.give.description

    

@receiver(post_save,sender=Give,dispatch_uid='give.created')   
def create_vendor_profile(sender,instance,created,**kwargs):
    if created:
        Vendor.objects.create(give=instance)
    instance.gift.save()


class Transaction(models.Model):
    made_by = models.CharField( max_length=50,blank=True,null=True)
    made_on = models.DateTimeField(auto_now_add=True)
    items_id=models.JSONField(default=list,null=True)
    pickup_location=models.CharField(max_length=500,default='')
    delivery_address=models.CharField(max_length=500,default='')
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    ref = models.CharField( max_length=200,blank=True,null=True)
    email=models.EmailField(default='')
    verified=models.BooleanField(default=False)
    delivered=models.BooleanField(default=False)

    def __str__(self):
        return self.ref

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(16)
            object_with_similar_ref = OnDeliveryTransaction.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref=ref
        super().save(*args, **kwargs)

    def amount_value(self):
        return self.amount * 100

    def verify_payment(self):
        paystack =PayStack()
        status,result = paystack.verify_payment(self.ref,self.amount)
        if status:
            self.verified =True
            self.save()
        if self.verified:
            return True
        return False

class Charge(models.Model):
    name= models.CharField(max_length=50)
    charge= models.IntegerField()


class OnDeliveryTransaction(models.Model):
    made_by = models.CharField( max_length=50,blank=True,null=True)
    made_on = models.DateTimeField(auto_now_add=True)
    items_id=models.JSONField(default=list,null=True)
    amount = models.BigIntegerField()
    pickup_location=models.CharField(max_length=500,blank=True,null=True)
    delivery_address=models.CharField(max_length=500,blank=True,null=True)
    ref = models.CharField( max_length=200,blank=True,null=True)
    email=models.EmailField(default='')
    delivered=models.BooleanField(default=False)
    

    def __str__(self):
        return self.ref

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(16)
            object_with_similar_ref = OnDeliveryTransaction.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref=ref
        super().save(*args, **kwargs)

class Subscription(models.Model):
    ref = models.CharField( max_length=200,blank=True,null=True)
    made_by= models.CharField(max_length=50,blank=True,null=True)
    amount=models.IntegerField()
    start_date=models.DateTimeField(auto_now_add=True)
    end_date=models.DateTimeField()
    balance=models.IntegerField(default=0)
    email=models.EmailField(default='')
    verified=models.BooleanField(default=False)

    def __str__(self):
        return self.ref
    
    def save(self, *args, **kwargs):
        while not self.ref:
            
            ref = secrets.token_urlsafe(16)
            object_with_similar_ref = Subscription.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref=ref
        super().save(*args, **kwargs)
    
    def amount_value(self):
        return self.amount * 100

    def verify_payment(self):
        paystack =PayStack()
        status,result = paystack.verify_payment(self.ref,self.amount)
        if status:
            #if result['amount']/ 100 == self.amount:
            self.verified =True
            self.save()
        if self.verified:
            return True
        return False

class State(models.Model):
    name = models.CharField(max_length=25,default='lagos',choices=states)

    def __str__(self):
        return self.name

class PickupCentre(models.Model):
    state=models.ForeignKey(State,on_delete=models.CASCADE,related_name='city')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Location(models.Model):
    state=models.ForeignKey(State,on_delete=models.SET_NULL, null=True)
    pickup_centre=models.ForeignKey(PickupCentre,on_delete=models.SET_NULL, null=True,related_name='centre')
    address=models.TextField()
    phone_number=models.IntegerField()
    
    def __str__(self):
        return self.address

class OnPickup(models.Model):
    ref = models.CharField( max_length=200,blank=True,null=True)
    made_by = models.CharField( max_length=50,blank=True,null=True)
    made_on = models.DateTimeField(auto_now_add=True)
    items_id=models.JSONField(default=list,null=True)
    item=models.CharField(max_length=500,blank=True,null=True)
    state=models.CharField(max_length=30,choices=states)
    pickup_centre=models.CharField(max_length=30,blank=True,null=True)
    email=models.EmailField(default='')
    collection_status=models.BooleanField(default=False)
    

    def __str__(self):
        return self.ref

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(16)
            object_with_similar_ref = OnPickup.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref=ref
        super().save(*args, **kwargs)


class GiveawayCap(models.Model):
    name=models.CharField(max_length=50)
    number=models.IntegerField()

    def __str__(self):
        return self.name



class DestinationCharge(models.Model):
    state=models.ForeignKey(State,on_delete=models.SET_NULL, null=True,default=1)
    city=models.CharField(max_length=100)
    charge=models.IntegerField()

    def __str__(self):
        return self.city

